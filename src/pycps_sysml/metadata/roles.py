"""Role markers for exportable models, analyses, and experiments.

The marker definitions are ordinary SysML definitions in the model package::

    part def SspModel;
    part def Analysis;
    part def FmuModel;

    attribute def DefaultExperiment {
      attribute startTime : Real;
      attribute stopTime : Real;
    }
    attribute def Experiment :> DefaultExperiment {
      attribute stepSize : Real;
      attribute tolerance : Real;
    }

A composition is exportable when its ``part def`` specializes ``SspModel``. An
analysis specializes ``Analysis`` and composes the exported model through a single
part usage, conventionally named ``sut``. Analyses are never exported as SSPs.
An FMU component specializes ``FmuModel``; it is the export unit itself, so its
FMU metadata belongs on that definition.

An experiment is also a typed attribute container: ``attribute defaults : <X>;``
where ``<X>`` specializes ``DefaultExperiment``. ``DefaultExperiment`` mirrors
``ssd:DefaultExperiment`` (SSP 2.0.1) and carries ``startTime`` and
``stopTime``, both required. ``Experiment`` mirrors ``fmi2:DefaultExperiment``
and adds the optional ``stepSize`` and ``tolerance``; all four FMI attributes
are optional in the FMI 2.0.5 XSD, so a missing ``stepSize`` reads as ``None``
exactly like a missing ``tolerance``. The FMI exporter copies every authored
field; the SSD exporter copies only ``startTime`` and ``stopTime``. When
present, ``stepSize`` and ``tolerance`` must be positive.

The functions are usable standalone, and :class:`RolePolicy` bundles them so a
consumer that owns a different role vocabulary can inject a predicate instead of
the marker names. :data:`SSP_ROLES` is this module's vocabulary.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from pycps_sysml.metadata.helpers import (
    short_name,
    specializes_marker_deep,
)
from pycps_sysml.model import (
    Architecture,
    Attribute,
    AttributeDefinition,
    PartDefinition,
    PartUsage,
    effective_members,
)

SSP_MODEL_MARKER = "SspModel"
ANALYSIS_MARKER = "Analysis"
FMU_MODEL_MARKER = "FmuModel"
DEFAULT_EXPERIMENT_MARKER = "DefaultExperiment"
EXPERIMENT_MARKER = "Experiment"

EXPERIMENT_FIELDS = ("startTime", "stopTime", "stepSize", "tolerance")


@dataclass(frozen=True)
class Experiment:
    """One resolved experiment.

    ``DefaultExperiment`` mirrors ``ssd:DefaultExperiment`` (SSP 2.0.1):
    ``start_time`` and ``stop_time``. ``Experiment`` mirrors
    ``fmi2:DefaultExperiment`` and adds ``step_size`` and ``tolerance``; all
    four FMI attributes are optional in the FMI 2.0.5 XSD, so a missing one is
    ``None``. The FMI exporter copies every authored field; the SSD exporter
    copies only ``start_time`` and ``stop_time``.
    """

    name: str
    start_time: float
    stop_time: float
    step_size: float | None
    tolerance: float | None = None


def is_ssp_model(architecture: Architecture, definition: PartDefinition) -> bool:
    return specializes_marker_deep(architecture, definition, SSP_MODEL_MARKER)


def is_analysis(architecture: Architecture, definition: PartDefinition) -> bool:
    return specializes_marker_deep(architecture, definition, ANALYSIS_MARKER)


def is_fmu_model(architecture: Architecture, definition: PartDefinition) -> bool:
    return specializes_marker_deep(architecture, definition, FMU_MODEL_MARKER)


def is_experiment_definition(
    architecture: Architecture, definition: AttributeDefinition | None
) -> bool:
    return specializes_marker_deep(architecture, definition, EXPERIMENT_MARKER)


def is_default_experiment_definition(
    architecture: Architecture, definition: AttributeDefinition | None
) -> bool:
    """True when ``definition`` is ``DefaultExperiment`` or specializes it.

    Transitive, so it also matches ``Experiment`` (which specializes
    ``DefaultExperiment``) and every concrete experiment container.
    """
    return specializes_marker_deep(
        architecture, definition, DEFAULT_EXPERIMENT_MARKER
    )


def _variation_point(
    architecture: Architecture,
    definition: PartDefinition | None,
    seen: set[str] | None = None,
) -> str | None:
    """Name of the first variation point reachable from a composition, or None.

    A point is either a variation definition used by a part, or a part usage
    that is itself a variation point (``variation part source : S;``).
    """
    if definition is None:
        return None
    if definition.is_variation:
        return definition.name
    seen = set() if seen is None else seen
    key = architecture.stored_key(definition)
    if key in seen:
        return None
    seen.add(key)
    for usage in effective_members(architecture, definition).parts.values():
        if usage.is_variation:
            return usage.name
        found = _variation_point(architecture, architecture.resolve_part(usage), seen)
        if found is not None:
            return found
    return None


def require_resolved_variation(
    architecture: Architecture, composition: PartDefinition
) -> None:
    """Reject generation of a composition that still carries a variation point.

    Generation is called without a selection here, so the point cannot be
    resolved and a variant-less artifact would be emitted silently. Reject
    instead and name the point; the caller passes ``--select`` to resolve it
    (IMP-006).
    """
    point = _variation_point(architecture, composition)
    if point is None:
        return
    raise ValueError(
        f"Variation point '{point}' in composition '{composition.name}' is not "
        "selected; pass a selection for it (for example "
        f"--select <usage>=<variant>)."
    )


def validate_role_markers(architecture: Architecture) -> None:
    """Reject marker use when the marker definition is missing."""
    used = {
        short_name(name)
        for definition in architecture.part_definitions.values()
        for name in definition.specializes
        if short_name(name) in {SSP_MODEL_MARKER, ANALYSIS_MARKER, FMU_MODEL_MARKER}
    }
    for marker in sorted(used):
        if not architecture.has_definition(architecture.part_definitions, marker):
            raise ValueError(
                f"Role marker '{marker}' is used but not defined. Add "
                f"'part def {marker};' to the package."
            )


def exportable_part_definitions(architecture: Architecture) -> list[PartDefinition]:
    return [
        definition
        for definition in architecture.part_definitions.values()
        if is_ssp_model(architecture, definition)
    ]


def analysis_part_definitions(architecture: Architecture) -> list[PartDefinition]:
    return [
        definition
        for definition in architecture.part_definitions.values()
        if is_analysis(architecture, definition)
        and short_name(definition.name) != ANALYSIS_MARKER
    ]


def model_usage(
    architecture: Architecture, analysis: PartDefinition
) -> tuple[PartUsage, PartDefinition]:
    """The single exportable model usage composed by an analysis."""
    usages: list[tuple[PartUsage, PartDefinition]] = []
    for usage in effective_members(architecture, analysis).parts.values():
        definition = architecture.resolve_part(usage)
        if definition is None:
            raise ValueError(
                f"Unresolved part definition for {analysis.name}.{usage.name}"
            )
        if is_ssp_model(architecture, definition):
            usages.append((usage, definition))
    if len(usages) != 1:
        names = ", ".join(usage.name for usage, _ in usages) or "none"
        raise ValueError(
            f"Analysis '{analysis.name}' must compose exactly one SspModel part; "
            f"found {names}"
        )
    return usages[0]


def experiment_attribute(
    architecture: Architecture,
    part_def: PartDefinition,
    *,
    required: bool,
) -> tuple[str, Attribute, AttributeDefinition] | None:
    """The single experiment attribute declared by ``part_def``.

    ``required=True`` is the analysis rule: exactly one container. With
    ``required=False`` an exported part may carry none, but more than one is
    always rejected.
    """
    found: list[tuple[str, Attribute, AttributeDefinition]] = []
    for name, attribute in effective_members(architecture, part_def).attributes.items():
        definition = architecture.resolve_attribute_def(attribute)
        if is_experiment_definition(
            architecture, definition
        ) or is_default_experiment_definition(architecture, definition):
            assert definition is not None
            found.append((name, attribute, definition))
    if required:
        if len(found) != 1:
            names = ", ".join(name for name, _, _ in found) or "none"
            raise ValueError(
                f"Analysis '{part_def.name}' must declare exactly one Experiment "
                f"attribute; found {names}"
            )
        return found[0]
    if len(found) > 1:
        names = ", ".join(name for name, _, _ in found)
        raise ValueError(
            f"{part_def.name} must declare at most one Experiment attribute; "
            f"found {names}"
        )
    return found[0] if found else None


def read_experiment(
    architecture: Architecture,
    part_def: PartDefinition,
    *,
    required: bool,
) -> Experiment | None:
    """Read the experiment container on ``part_def``, or ``None`` when absent.

    ``DefaultExperiment`` mirrors ``ssd:DefaultExperiment`` (SSP 2.0.1) and
    ``Experiment`` mirrors ``fmi2:DefaultExperiment``. ``startTime`` and
    ``stopTime`` are mandatory and numeric. ``stepSize`` and ``tolerance`` are
    optional FMI 2.0.5 attributes: a missing one yields ``None``. Extra members
    authored on a ``DefaultExperiment`` container are still read, so a local
    four-field vocabulary keeps working. When present, ``stepSize`` and
    ``tolerance`` must be positive. The FMI exporter copies every authored
    field; the SSD exporter copies only ``startTime`` and ``stopTime``.
    """
    attribute = experiment_attribute(architecture, part_def, required=required)
    if attribute is None:
        return None
    name, _attribute, definition = attribute
    members = effective_members(architecture, definition)
    values: dict[str, float] = {}
    for field in ("startTime", "stopTime"):
        values[field] = _numeric_member(
            definition, members.attributes.get(field), field
        )

    step_size: float | None = None
    step_attribute = members.attributes.get("stepSize")
    if step_attribute is not None and step_attribute.value is not None:
        step_size = _numeric_member(definition, step_attribute, "stepSize")

    tolerance: float | None = None
    tolerance_attribute = members.attributes.get("tolerance")
    if tolerance_attribute is not None and tolerance_attribute.value is not None:
        tolerance = _numeric_member(definition, tolerance_attribute, "tolerance")

    if values["stopTime"] <= values["startTime"]:
        raise ValueError(
            f"Experiment '{definition.name}' stopTime must be greater than startTime"
        )
    if step_size is not None and step_size <= 0:
        raise ValueError(f"Experiment '{definition.name}' stepSize must be positive")
    if tolerance is not None and tolerance <= 0:
        raise ValueError(f"Experiment '{definition.name}' tolerance must be positive")

    return Experiment(
        name=name,
        start_time=values["startTime"],
        stop_time=values["stopTime"],
        step_size=step_size,
        tolerance=tolerance,
    )


def _numeric_member(
    definition: AttributeDefinition, attribute: Attribute | None, field: str
) -> float:
    if attribute is None or attribute.value is None:
        raise ValueError(
            f"Experiment '{definition.name}.{field}' must have a numeric value"
        )
    value = attribute.value
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(
            f"Experiment '{definition.name}.{field}' must be numeric, got "
            f"{attribute.primitive_type_str()}"
        )
    return float(value)


@dataclass(frozen=True)
class RolePolicy:
    """The role vocabulary one consumer recognises.

    ``model_marker`` / ``analysis_marker`` / ``fmu_model_marker`` are the names a
    model comparison may need (``None`` when the consumer has no such marker);
    the predicates are what the traversal layers call. :data:`SSP_ROLES` is the
    SSP vocabulary and the default everywhere a policy is optional.
    """

    model_marker: str | None = SSP_MODEL_MARKER
    analysis_marker: str | None = ANALYSIS_MARKER
    fmu_model_marker: str | None = FMU_MODEL_MARKER
    is_model: Callable[[Architecture, PartDefinition | None], bool] = is_ssp_model
    is_analysis: Callable[[Architecture, PartDefinition | None], bool] = is_analysis
    is_fmu_model: Callable[[Architecture, PartDefinition | None], bool] = is_fmu_model
    model_usage: Callable[
        [Architecture, PartDefinition], tuple[PartUsage, PartDefinition]
    ] = model_usage
    analysis_definitions: Callable[[Architecture], list[PartDefinition]] = (
        analysis_part_definitions
    )


SSP_ROLES = RolePolicy()
