"""Derive an analysis selection from a model-level SysML v2 configuration.

SysML v2 has variation points and variants but no selection construct. The
standard idiom is a 100% configuration: a part definition specialises the model
and binds each variation usage with a redefinition and a feature value::

    part def StepSystem :> System {
      part :>> source = SourceChoice::step;
    }

An analysis composes the configuration, not the root composition. This module
walks the configuration chain back to the root, replays each binding onto the
effective members, descends into a selected variant's type for nested points,
and returns the canonical ``{"usage path": "variant"}`` map that
:func:`pycps_sysml2.parameters.variation.resolve_selected` consumes.

A point left unbound is inferred from the family's asserted constraints only
when exactly one completion is valid. Zero or several valid completions is
still an error, never a silently unselected or arbitrary artifact.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from itertools import product

from pycps_sysml2.metadata import RolePolicy
from pycps_sysml2.model import (
    Architecture,
    Attribute,
    Definition,
    PartDefinition,
    PartUsage,
    VariantBody,
    VariantMember,
)
from pycps_sysml2.parameters.constraints import evaluate

__all__ = [
    "configuration_name",
    "derived_selection",
    "model_root",
    "qualified_type",
    "scope_analysis_to_root",
]


def _short(name: str) -> str:
    return name.split("::")[-1].strip()


def qualified_type(
    architecture: Architecture,
    definitions: Mapping[str, Definition],
    value: str,
) -> Definition:
    """The definition a ``[Pkg::]Type::Variant`` configuration value names.

    The last segment is the variant; the type is the longest remaining prefix
    that resolves, dropping leading segments one at a time. Raises
    ``ValueError`` when the value is ambiguous or no prefix resolves, naming
    the value either way.
    """
    segments = value.split("::")
    if len(segments) < 2:
        raise ValueError(
            f"configuration value '{value}' is not '[Pkg::]Type::Variant'"
        )
    prefix = segments[:-1]
    while prefix:
        candidate = "::".join(prefix)
        try:
            definition = architecture.resolve(definitions, candidate)
        except ValueError as error:
            raise ValueError(
                f"configuration value '{value}' is ambiguous: {error}"
            ) from None
        if definition is not None:
            return definition
        prefix = prefix[1:]
    raise ValueError(
        f"configuration value '{value}' names no definition; "
        f"tried {', '.join(segments[:-1])}"
    )


def _definition(
    architecture: Architecture, analysis: PartDefinition | str
) -> PartDefinition:
    if isinstance(analysis, PartDefinition):
        return analysis
    return architecture.get_part_def(analysis)


def _specialization_chain(
    architecture: Architecture, definition: PartDefinition, roles: RolePolicy
) -> list[PartDefinition]:
    """Every definition from the root composition down to *definition*."""
    chain = [definition]
    current = definition
    while True:
        base = _model_supertype(architecture, current, roles)
        if base is None:
            break
        chain.append(base)
        current = base
    chain.reverse()
    return chain


def _model_label(roles: RolePolicy) -> str:
    """The name a diagnostic uses for the root marker the policy recognises."""
    return roles.model_marker if roles.model_marker is not None else "model"


def _model_supertype(
    architecture: Architecture, definition: PartDefinition, roles: RolePolicy
) -> PartDefinition | None:
    """The single model supertype, or ``None`` at the root boundary."""
    marker = roles.model_marker
    if marker is not None and _short(definition.name) == marker:
        return None
    specializations = list(definition.specializes)
    if marker is not None and marker in [_short(name) for name in specializations]:
        return None
    bases = []
    others = []
    for name in specializations:
        base = architecture.resolve_part(name)
        if base is None:
            continue
        if roles.is_model(architecture, base):
            bases.append(base)
        else:
            others.append(base)
    label = _model_label(roles)
    if len(bases) > 1:
        names = ", ".join(base.name for base in bases)
        raise ValueError(
            f"Definition '{definition.name}' specialises more than one {label} "
            f"definition ({names}); a configuration chain must be linear."
        )
    if not bases and others:
        raise ValueError(
            f"Definition '{definition.name}' specialises '{others[0].name}', "
            f"which is not marked {label}; a configuration chain must specialise "
            "the root composition."
        )
    return bases[0] if bases else None


def model_root(
    architecture: Architecture,
    definition: PartDefinition,
    *,
    roles: RolePolicy,
) -> PartDefinition:
    """The outermost composition a configuration specialises, for example ``System``."""
    return _specialization_chain(architecture, definition, roles)[0]


def configuration_name(
    architecture: Architecture,
    analysis: PartDefinition | str,
    *,
    roles: RolePolicy,
) -> str | None:
    """The composed model definition's name unless it is the root composition."""
    definition = _definition(architecture, analysis)
    composed = roles.model_usage(architecture, definition)[1]
    return (
        None
        if model_root(architecture, composed, roles=roles) is composed
        else composed.name
    )


def scope_analysis_to_root(
    architecture: Architecture,
    analysis: PartDefinition | str,
    *,
    roles: RolePolicy,
) -> PartDefinition:
    """Retype the analysis's model usage to the root composition.

    Generation stays on the root (IMP-106 option B1): a configuration only
    redefines the family's usages, so its inherited parts, ports, connections,
    and binds live on the root. Mutates *architecture* in place and returns the
    root definition; callers load a private copy first.
    """
    definition = _definition(architecture, analysis)
    usage, composed = roles.model_usage(architecture, definition)
    root = model_root(architecture, composed, roles=roles)
    usage.type_name = root.name
    return root


@dataclass(frozen=True)
class _Point:
    """One variation point in an effective scope."""

    kind: str  # "part" or "attribute"
    variation: str
    variants: tuple[VariantMember, ...]


@dataclass(frozen=True)
class _Binding:
    """One redefinition that binds a point, with the scope its value reads from."""

    usage: PartUsage | Attribute
    local_parts: Mapping[str, PartUsage]
    where: str


def _points(
    architecture: Architecture, scope: PartDefinition
) -> dict[str, _Point]:
    """The variation points an effective scope declares, in declaration order."""
    points: dict[str, _Point] = {}
    for name, usage in scope.parts.items():
        definition = architecture.resolve_part(usage)
        if usage.is_variation and usage.variants:
            points[name] = _Point("part", name, tuple(usage.variants))
        elif definition is not None and definition.is_variation:
            points[name] = _Point(
                "part", definition.name, tuple(definition.variants)
            )
    for name, attribute in scope.attributes.items():
        definition = architecture.resolve_attribute_def(attribute)
        if definition is not None and definition.is_variation:
            points[name] = _Point(
                "attribute", definition.name, tuple(definition.variants)
            )
    return points


def _bindings(
    members: PartDefinition | VariantBody,
    local_parts: Mapping[str, PartUsage],
    where: str,
) -> dict[str, _Binding]:
    """Every redefinition among *members*, keyed by its target feature."""
    bindings: dict[str, _Binding] = {}
    for name, usage in members.parts.items():
        if usage.redefines:
            _single_target(name, usage.redefines, where)
            bindings[name] = _Binding(usage, local_parts, where)
    for name, attribute in members.attributes.items():
        if attribute.redefines:
            _single_target(name, attribute.redefines, where)
            bindings[name] = _Binding(attribute, local_parts, where)
    return bindings


def _single_target(name: str, targets: tuple[str, ...], where: str) -> None:
    if len(targets) > 1:
        listed = ", ".join(targets)
        raise ValueError(
            f"usage '{name}' in {where} redefines more than one feature "
            f"({listed}); bind exactly one variation point."
        )


def derived_selection(
    architecture: Architecture,
    analysis: PartDefinition | str,
    *,
    roles: RolePolicy,
) -> dict[str, str]:
    """The selection an analysis's configuration derives.

    Keys are relative to the composed model (``path``, ``path.inner_stage``) or
    bare for an analysis-local usage (``scenario``). Raises ``ValueError`` when a
    binding does not name a variation point, or when the unbound points do not
    have exactly one constraint-valid completion.
    """
    definition = _definition(architecture, analysis)
    composed = roles.model_usage(architecture, definition)[1]
    chain = _specialization_chain(architecture, composed, roles)
    where = f"configuration '{composed.name}'"

    bindings: dict[str, _Binding] = {}
    for configuration in chain[1:]:
        label = f"configuration '{configuration.name}'"
        bindings.update(_bindings(configuration, configuration.parts, label))
    solutions, first_unbound = _expand(
        architecture, chain[0], bindings, {}, "", where, infer=True
    )
    if first_unbound is None:
        selection = solutions[0]
    else:
        from pycps_sysml2.parameters.variation import resolve_selected

        valid: list[dict[str, str]] = []
        seen: set[tuple[tuple[str, str], ...]] = set()
        for candidate in solutions:
            try:
                resolved, canonical = resolve_selected(
                    architecture, chain[0], candidate, roles=roles
                )
            except ValueError:
                continue
            report = evaluate(resolved, chain[0].name, canonical)
            if report.failed or report.invalid:
                continue
            marker = tuple(sorted(candidate.items()))
            if marker in seen:
                continue
            seen.add(marker)
            valid.append(candidate)
        if len(valid) == 1:
            selection = valid[0]
        else:
            key, point, at = first_unbound
            base = (
                f"variation point '{point.variation}' at '{key}' is not "
                f"selected; bind it in {at}"
            )
            if valid:
                raise ValueError(
                    f"{base}; {len(valid)} assignments satisfy the asserted "
                    f"constraints in {at}"
                )
            raise ValueError(
                f"{base}; no assignment satisfies the asserted constraints in "
                f"{at}"
            )

    local_where = f"analysis '{definition.name}'"
    local: dict[str, _Binding] = {}
    for name, point in _points(architecture, definition).items():
        usage = definition.parts.get(name) or definition.attributes[name]
        local[name] = _Binding(usage, definition.parts, local_where)
    states, _ = _expand(
        architecture, definition, local, selection, "", local_where, infer=False
    )
    return states[0]


def _expand(
    architecture: Architecture,
    scope: PartDefinition,
    bindings: Mapping[str, _Binding],
    selection: dict[str, str],
    prefix: str,
    where: str,
    *,
    infer: bool,
) -> tuple[list[dict[str, str]], tuple[str, _Point, str] | None]:
    """Bind *scope*'s points, fanning out over inferred completions.

    Returns every resulting selection and the first point left unbound in
    depth-first order, if any, so the caller can name it in an error.
    """
    points = _points(architecture, scope)
    states = [dict(selection)]
    first_unbound: tuple[str, _Point, str] | None = None
    for target, binding in bindings.items():
        point = points.get(target)
        if point is None:
            raise ValueError(
                f"redefinition target '{target}' in {where} is not a variation "
                f"point in '{scope.name}'"
            )
        key = prefix + target
        if not binding.usage.value:
            raise ValueError(
                f"variation point '{point.variation}' at '{key}' is not "
                f"selected; bind it in {binding.where}"
            )
        variant, body = _resolve(architecture, point, binding, key)
        expanded: list[dict[str, str]] = []
        for state in states:
            entered, nested_unbound = _enter(
                architecture,
                point,
                variant,
                body,
                binding.local_parts,
                key,
                state,
                binding.where,
                infer,
            )
            expanded.extend(entered)
            if first_unbound is None:
                first_unbound = nested_unbound
        states = expanded

    unbound = [
        (prefix + name, point)
        for name, point in points.items()
        if prefix + name not in states[0]
    ]
    if not unbound:
        return states, first_unbound
    if not infer:
        key, point = unbound[0]
        raise ValueError(
            f"variation point '{point.variation}' at '{key}' is not selected; "
            f"bind it in {where}"
        )
    if first_unbound is None:
        key, point = unbound[0]
        first_unbound = (key, point, where)

    expanded = []
    for variants in product(*(point.variants for _, point in unbound)):
        branch = states
        for (key, point), variant in zip(unbound, variants):
            next_states: list[dict[str, str]] = []
            for state in branch:
                entered, _ = _enter(
                    architecture,
                    point,
                    variant,
                    None,
                    {},
                    key,
                    state,
                    where,
                    infer,
                )
                next_states.extend(entered)
            branch = next_states
        expanded.extend(branch)
    return expanded, first_unbound


def _enter(
    architecture: Architecture,
    point: _Point,
    variant: VariantMember,
    body: VariantBody | None,
    local_parts: Mapping[str, PartUsage],
    key: str,
    selection: dict[str, str],
    where: str,
    infer: bool,
) -> tuple[list[dict[str, str]], tuple[str, _Point, str] | None]:
    """Record one selected variant and descend into its type."""
    state = dict(selection)
    for existing in [
        item for item in state if item == key or item.startswith(key + ".")
    ]:
        del state[existing]
    state[key] = variant.name

    if point.kind != "part" or variant.type_name is None:
        return [state], None
    nested = architecture.resolve_part(variant.type_name)
    if nested is None:
        return [state], None
    inner: dict[str, _Binding] = {}
    if body is not None:
        inner = _bindings(body, {**local_parts, **body.parts}, where)
    return _expand(architecture, nested, inner, state, key + ".", where, infer=infer)


def _resolve(
    architecture: Architecture,
    point: _Point,
    binding: _Binding,
    key: str,
) -> tuple[VariantMember, VariantBody | None]:
    """The variant a binding value names and the body that configures it.

    A qualified ``Type::variant`` value may carry a body on the same usage. An
    unqualified value names a local usage whose subsetting target is the variant
    and whose body binds the points inside that variant's type.
    """
    value = binding.usage.value
    assert value is not None
    if "::" in value:
        definitions = (
            architecture.part_definitions
            if point.kind == "part"
            else architecture.attribute_definitions
        )
        definition = qualified_type(architecture, definitions, value)
        if definition.name != point.variation:
            raise ValueError(
                f"binding '{value}' for variation point '{point.variation}' at "
                f"'{key}' names type '{definition.name}'; "
                f"expected '{point.variation}'"
            )
        return (
            _variant(point, value.rsplit("::", 1)[1], key, binding.where),
            getattr(binding.usage, "body", None),
        )

    local = binding.local_parts.get(value)
    if local is None:
        raise ValueError(
            f"binding '{value}' for variation point '{point.variation}' at "
            f"'{key}' names no part usage in {binding.where}"
        )
    if len(local.subsets) != 1:
        raise ValueError(
            f"part usage '{value}' in {binding.where} must specialise exactly "
            f"one variant of '{point.variation}'; found {len(local.subsets)}"
        )
    subset = local.subsets[0]
    type_name, variant_name = (_short(part) for part in subset.rsplit("::", 1))
    if type_name != point.variation:
        raise ValueError(
            f"part usage '{value}' in {binding.where} specialises '{subset}', "
            f"which is not a variant of '{point.variation}'"
        )
    return _variant(point, variant_name, key, binding.where), local.body


def _variant(
    point: _Point, name: str, key: str, where: str
) -> VariantMember:
    variant = next(
        (member for member in point.variants if member.name == name), None
    )
    if variant is None:
        expected = ", ".join(member.name for member in point.variants) or "none"
        raise ValueError(
            f"Unknown variant '{name}' for variation point '{point.variation}' "
            f"at '{key}' in {where}; expected one of {expected}."
        )
    return variant
