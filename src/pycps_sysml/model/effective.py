"""Inherited, read-only member view over one definition.

The IR stays source-faithful: a definition carries only the members it declares,
and ``specializes`` names the definitions whose members it inherits. Consumers
that need the whole member set (an artifact generator, a metadata accessor, a
constraint walk) go through :func:`effective_members` instead of reading the
dataclass fields directly.

The merge is ancestor-first in declaration order, then the definition's own
members. A keyed member of the same name replaces the inherited one and keeps
the inherited position; bindings and constraints keep declaration order, with
the inherited entries first. Nothing is cached or written back to the model.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace

from pycps_sysml.model.model import (
    Architecture,
    Attribute,
    AttributeDefinition,
    Binding,
    Connection,
    ConstraintUsage,
    Definition,
    PartDefinition,
    PartUsage,
    PortDefinition,
    PortUsage,
)

__all__ = ["EffectiveMembers", "effective_members"]


@dataclass(frozen=True)
class EffectiveMembers:
    """Everything a definition exposes, inherited members included."""

    attributes: Mapping[str, Attribute]
    ports: Mapping[str, PortUsage]
    parts: Mapping[str, PartUsage]
    connections: Mapping[str, Connection]
    bindings: tuple[Binding, ...]
    constraints: tuple[ConstraintUsage, ...]


def _empty() -> EffectiveMembers:
    return EffectiveMembers(
        attributes={},
        ports={},
        parts={},
        connections={},
        bindings=(),
        constraints=(),
    )


def effective_members(
    architecture: Architecture, definition: Definition
) -> EffectiveMembers:
    """The effective member view of *definition*.

    ``PartDefinition``, ``PortDefinition``, and ``AttributeDefinition`` are
    supported; any other kind returns an empty view. Supertypes resolve through
    the namespace-aware ``resolve_*`` methods, so package qualification and
    imports keep working. An unknown supertype or one of another kind is
    skipped silently; ``sysmlpy.analyze()`` is where such a mismatch is
    reported.
    """
    return _effective(architecture, definition, frozenset())


def _effective(
    architecture: Architecture, definition: Definition, seen: frozenset[str]
) -> EffectiveMembers:
    if isinstance(definition, PartDefinition):
        resolve = architecture.resolve_part
    elif isinstance(definition, PortDefinition):
        resolve = architecture.resolve_port
    elif isinstance(definition, AttributeDefinition):
        resolve = architecture.resolve_attribute_def
    else:
        return _empty()

    key = architecture.stored_key(definition)
    if key in seen:
        return _empty()
    seen = seen | {key}

    attributes: dict[str, Attribute] = {}
    ports: dict[str, PortUsage] = {}
    parts: dict[str, PartUsage] = {}
    connections: dict[str, Connection] = {}
    bindings: list[Binding] = []
    constraints: list[ConstraintUsage] = []

    for supertype in definition.specializes:
        base = resolve(supertype)
        if base is None or type(base) is not type(definition):
            continue
        inherited = _effective(architecture, base, seen)
        attributes.update(inherited.attributes)
        ports.update(inherited.ports)
        parts.update(inherited.parts)
        connections.update(inherited.connections)
        bindings.extend(inherited.bindings)
        constraints.extend(inherited.constraints)

    for name, attribute in definition.attributes.items():
        inherited_attribute = attributes.get(name)
        if (
            attribute.value is None
            and inherited_attribute is not None
            and inherited_attribute.value is not None
        ):
            attribute = replace(attribute, value=inherited_attribute.value)
        attributes[name] = attribute
    ports.update(getattr(definition, "ports", {}))
    parts.update(getattr(definition, "parts", {}))
    connections.update(getattr(definition, "connections", {}))
    bindings.extend(getattr(definition, "bindings", ()))
    constraints.extend(getattr(definition, "constraints", ()))

    return EffectiveMembers(
        attributes=attributes,
        ports=ports,
        parts=parts,
        connections=connections,
        bindings=tuple(bindings),
        constraints=tuple(constraints),
    )
