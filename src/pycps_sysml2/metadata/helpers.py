"""Marker and member resolution shared by every metadata dialect.

Two marker questions exist and they are not the same question:

- the parameter dialect asks whether a definition *directly* writes a marker in
  its ``:>`` list, and deliberately does not treat the marker definition itself
  as an instance of the marker (:func:`specializes_marker`);
- the role and typed-metadata dialects ask whether a definition *is* the marker
  or reaches it through any chain of supertypes, including the marker
  definition itself (:func:`specializes_marker_deep`).

Keeping both here means one implementation and one place to reason about the
namespace: a ``PartDefinition`` resolves supertypes through
``architecture.part_definitions``, a ``PortDefinition`` through
``architecture.port_definitions``, and everything else through
``architecture.attribute_definitions``.
"""

from __future__ import annotations

from pycps_sysml2.model import (
    Architecture,
    Attribute,
    AttributeDefinition,
    Definition,
    PartDefinition,
    PortDefinition,
)
from pycps_sysml2.model.effective import effective_members as _effective_view


def short_name(name: str) -> str:
    """Last segment of a possibly qualified SysML name."""
    return name.split("::")[-1]


def specializes_marker(definition: Definition | None, marker: str) -> bool:
    """True when ``definition`` writes ``marker`` in its own ``:>`` list.

    Direct only, and the definition's own name is never inspected, so the
    marker definition is not an instance of itself:
    ``is_parameter_set(ParameterSet_marker_definition)`` stays ``False``.
    """
    if definition is None:
        return False
    return any(short_name(name) == marker for name in definition.specializes)


def specializes_marker_deep(
    architecture: Architecture,
    definition: PartDefinition | PortDefinition | AttributeDefinition | None,
    marker: str,
    *,
    seen: set[str] | None = None,
) -> bool:
    """True when ``definition`` is ``marker`` or specializes it transitively.

    Accepts a ``PartDefinition``, a ``PortDefinition``, or an
    ``AttributeDefinition``; each resolves its supertypes through its own
    namespace. Unlike :func:`specializes_marker` this matches the definition's
    own short name, so ``is_ssp_model(SspModel_marker_definition)`` stays
    ``True``.

    The visited set holds stored keys, not bare names: two packages may define
    the same bare name, and a bare-name guard would prune the second definition
    of that name and miss a real chain through it.
    """
    if definition is None:
        return False
    if short_name(definition.name) == marker:
        return True
    seen = set() if seen is None else seen
    key = architecture.stored_key(definition)
    if key in seen:
        return False
    seen.add(key)
    for supertype in definition.specializes:
        if short_name(supertype) == marker:
            return True
        if isinstance(definition, PartDefinition):
            base = architecture.resolve_part(supertype)
        elif isinstance(definition, PortDefinition):
            base = architecture.resolve_port(supertype)
        else:
            base = architecture.resolve_attribute_def(supertype)
        if specializes_marker_deep(architecture, base, marker, seen=seen):
            return True
    return False


def effective_members(
    architecture: Architecture,
    definition: AttributeDefinition,
    *,
    seen: set[str] | None = None,
) -> dict[str, Attribute]:
    """Direct members plus inherited members; inherited values win by name.

    A derived member with no value of its own keeps the inherited value instead
    of shadowing it with ``None``. This is the attribute half of the generic
    :func:`pycps_sysml2.model.effective.effective_members` view, kept here with
    its historical signature for the metadata dialects.
    """
    seen = set() if seen is None else seen
    if architecture.stored_key(definition) in seen:
        return {}
    return dict(_effective_view(architecture, definition).attributes)


def is_inherited_schema_slot(
    architecture: Architecture,
    part_def: PartDefinition,
    name: str,
    attribute: Attribute,
    *,
    slot_name: str,
    marker: str,
) -> bool:
    """True for the canonical slot inherited unfilled from a role marker.

    A role marker such as ``FmuModel`` declares ``attribute fmu_meta :
    FmuMetadata;`` as a schema slot. A definition that inherits the marker but
    does not author metadata inherits that placeholder usage; it means "no
    metadata authored", not a use of the schema directly. A locally declared
    usage of the same name shadows the placeholder and is not a slot.
    """
    if name != slot_name or name in part_def.attributes:
        return False
    definition = architecture.resolve_attribute_def(attribute)
    return definition is not None and short_name(definition.name) == marker
