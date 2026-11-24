"""Typed FMU metadata carried by part definitions.

The dialect is a small value-definition hierarchy::

    attribute def FmuMetadata {
      attribute source : String;
      attribute implementation : String;
    }

    attribute def AutopilotFmu :> FmuMetadata {
      attribute source = "build/fmus/Autopilot.fmu";
      attribute implementation = "CoSimulation";
    }

    part def AutopilotModule {
      attribute fmu_meta : AutopilotFmu;
    }

Metadata is recognized by **type**, not by the usage name: the part attribute
must be typed by an ``attribute def`` that specializes ``FmuMetadata``. At most
one such attribute is allowed per part definition.

``source`` and ``implementation`` are ``ssd:Component/@source`` and
``@implementation`` (SSP 2.0.1), not ``fmiModelDescription`` fields:
``FmuMetadata`` describes an FMI model packaged as an SSP component. ``source``
is the build artifact path (a ``.fmu`` file or an extracted FMU directory). It
is authoring data and is never recovered from an SSD. A part definition without
``source`` has no FMU yet: its SSD component is exported with an empty
``source``. ``implementation`` is one of the
``ssd:Component/@implementation`` enumeration values; the FMU resource name is
always derived from the part definition name.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from pycps_sysml.core.fmi_helpers import fmu_resource_path
from pycps_sysml.metadata.helpers import (
    is_inherited_schema_slot,
    short_name,
    specializes_marker_deep,
)
from pycps_sysml.metadata.roles import FMU_MODEL_MARKER, is_fmu_model
from pycps_sysml.model import (
    Architecture,
    Attribute,
    AttributeDefinition,
    PartDefinition,
    effective_members,
)

FMU_METADATA_ATTR = "fmu_meta"
FMU_METADATA_MARKER = "FmuMetadata"
FMU_METADATA_FIELDS = ("source", "implementation")

#: Allowed ``ssd:Component/@implementation`` values (SSP 2.0.1).
FMU_IMPLEMENTATION_VALUES = (
    "any",
    "ModelExchange",
    "CoSimulation",
    "ScheduledExecution",
)


@dataclass(frozen=True)
class FmuMetadata:
    """Effective metadata values for one FMU-backed part definition."""

    source: str | None = None
    implementation: str | None = None


# -- definition resolution --------------------------------------------------


def is_fmu_metadata_definition(
    architecture: Architecture, definition: AttributeDefinition | None
) -> bool:
    """True when ``definition`` is the marker or specializes it transitively."""
    return specializes_marker_deep(architecture, definition, FMU_METADATA_MARKER)


def _metadata_usage(
    architecture: Architecture, part_def: PartDefinition
) -> tuple[str, Attribute, AttributeDefinition] | None:
    found: list[tuple[str, Attribute, AttributeDefinition]] = []
    members = effective_members(architecture, part_def)
    for name, attribute in members.attributes.items():
        definition = architecture.resolve_attribute_def(attribute)
        if is_fmu_metadata_definition(architecture, definition):
            if is_inherited_schema_slot(
                architecture,
                part_def,
                name,
                attribute,
                slot_name=FMU_METADATA_ATTR,
                marker=FMU_METADATA_MARKER,
            ):
                continue
            assert definition is not None
            found.append((name, attribute, definition))

    if len(found) > 1:
        names = ", ".join(sorted(name for name, _, _ in found))
        raise ValueError(
            f"{part_def.name} declares multiple FMU metadata attributes "
            f"({names}); use one"
        )
    if found:
        name, attribute, definition = found[0]
        if short_name(definition.name) == FMU_METADATA_MARKER:
            raise ValueError(
                f"{part_def.name}.{name} is typed by the '{FMU_METADATA_MARKER}' "
                "schema directly; use a concrete 'attribute def <Part>FmuMetadata "
                f":> {FMU_METADATA_MARKER} {{ ... }}' instead"
            )
        return name, attribute, definition

    slot = members.attributes.get(FMU_METADATA_ATTR)
    if slot is not None and not is_inherited_schema_slot(
        architecture,
        part_def,
        FMU_METADATA_ATTR,
        slot,
        slot_name=FMU_METADATA_ATTR,
        marker=FMU_METADATA_MARKER,
    ):
        raise ValueError(
            f"{part_def.name}.{FMU_METADATA_ATTR} must be typed by an "
            f"attribute def marked ':> {FMU_METADATA_MARKER}'"
        )
    return None


def _string_member(name: str, attribute: Attribute | None) -> str | None:
    if attribute is None or attribute.value is None:
        return None
    value = attribute.value
    if not isinstance(value, str) or attribute.primitive_type_str() != "String":
        actual = attribute.primitive_type_str()
        raise ValueError(
            f"Fmu metadata member '{name}' must be a String, got {actual}"
        )
    return value


def _implementation_member(
    part_def: PartDefinition, attribute: Attribute | None
) -> str | None:
    value = _string_member("implementation", attribute)
    if value is not None and value not in FMU_IMPLEMENTATION_VALUES:
        raise ValueError(
            f"{part_def.name} implementation {value!r} is not an "
            "ssd:Component/@implementation value; allowed values are "
            f"{', '.join(FMU_IMPLEMENTATION_VALUES)}"
        )
    return value


def fmu_metadata(
    architecture: Architecture, part_def: PartDefinition
) -> FmuMetadata | None:
    """Resolve effective FMU metadata for ``part_def``, or ``None``."""
    usage = _metadata_usage(architecture, part_def)
    if usage is None:
        return None

    name, _attribute, definition = usage
    if effective_members(architecture, part_def).parts:
        raise ValueError(
            f"{part_def.name} has both subparts and '{name}' metadata; "
            "a nested system cannot also be an FMU component"
        )

    marker = architecture.resolve_attribute_def(FMU_METADATA_MARKER)
    if marker is None:
        raise ValueError(
            f"FMU metadata uses missing marker definition '{FMU_METADATA_MARKER}'. "
            f"Add 'attribute def {FMU_METADATA_MARKER} {{ ... }}' to the package."
        )

    members = effective_members(architecture, definition)
    unknown = sorted(set(members.attributes) - set(FMU_METADATA_FIELDS))
    if unknown:
        raise ValueError(
            f"FMU metadata definition '{definition.name}' declares unsupported "
            f"member(s): {', '.join(unknown)}; allowed members are "
            f"{', '.join(FMU_METADATA_FIELDS)}"
        )

    return FmuMetadata(
        source=_string_member("source", members.attributes.get("source")),
        implementation=_implementation_member(
            part_def, members.attributes.get("implementation")
        ),
    )


def component_source(part_def: PartDefinition, metadata: FmuMetadata | None) -> str:
    """SSD component source; empty when no FMU is authored for the part."""
    if metadata is None or not metadata.source:
        return ""
    return fmu_resource_path(part_def.name)


def component_implementation(metadata: FmuMetadata | None) -> str | None:
    return None if metadata is None else metadata.implementation


# -- synthesis --------------------------------------------------------------


def ensure_fmu_metadata_definition(
    architecture: Architecture, source_file: str
) -> AttributeDefinition:
    """Create the shared ``FmuMetadata`` schema when it is missing."""
    existing = architecture.resolve_attribute_def(FMU_METADATA_MARKER)
    if existing is not None:
        return existing
    if architecture.has_definition(architecture.port_definitions, FMU_METADATA_MARKER):
        raise ValueError(
            f"'{FMU_METADATA_MARKER}' is defined as a port def, but FMU metadata "
            "is an attribute def"
        )

    definition = AttributeDefinition(
        name=FMU_METADATA_MARKER,
        source_file=source_file,
    )
    for field in FMU_METADATA_FIELDS:
        definition.attributes[field] = Attribute(name=field, type_name="String")
    architecture.add_attribute_def(definition)
    return definition


def ensure_fmu_model_definition(
    architecture: Architecture, source_file: str
) -> PartDefinition:
    """Create the shared ``FmuModel`` role marker when it is missing."""
    existing = architecture.resolve_part(FMU_MODEL_MARKER)
    if existing is not None:
        return existing
    if architecture.has_definition(architecture.port_definitions, FMU_MODEL_MARKER):
        raise ValueError(
            f"'{FMU_MODEL_MARKER}' is defined as a port def, but an FMU model is "
            "marked by a part def"
        )

    definition = PartDefinition(name=FMU_MODEL_MARKER, source_file=source_file)
    architecture.add_part_def(definition)
    return definition


def _unique_definition_name(architecture: Architecture, base: str) -> str:
    candidate = base
    counter = 2
    used = set(architecture.attribute_definitions) | set(architecture.port_definitions)
    while candidate in used:
        candidate = f"{base}_{counter}"
        counter += 1
    return candidate


def _metadata_definition_name(part_def: PartDefinition) -> str:
    return f"{part_def.name}FmuMetadata"


def add_fmu_metadata(
    architecture: Architecture,
    part_def: PartDefinition,
    *,
    implementation: str | None = None,
    source_file: str,
) -> AttributeDefinition:
    """Attach a concrete metadata definition and ``fmu_meta`` usage."""
    ensure_fmu_metadata_definition(architecture, source_file)
    if FMU_METADATA_ATTR in part_def.attributes:
        raise ValueError(
            f"{part_def.name}.{FMU_METADATA_ATTR} already exists; update it "
            "instead of adding a second metadata attribute"
        )

    name = _unique_definition_name(
        architecture, _metadata_definition_name(part_def)
    )
    definition = AttributeDefinition(
        name=name,
        source_file=source_file,
        specializes=(FMU_METADATA_MARKER,),
    )
    if implementation is not None:
        definition.attributes["implementation"] = Attribute(
            name="implementation", type_name="String", value=implementation
        )

    architecture.add_attribute_def(definition)
    part_def.attributes[FMU_METADATA_ATTR] = Attribute(
        name=FMU_METADATA_ATTR,
        type_name=name,
    )
    return definition


def _definition_is_shared(
    architecture: Architecture,
    definition: AttributeDefinition,
    owner: PartDefinition,
) -> bool:
    for part_def in architecture.part_definitions.values():
        if part_def is owner:
            continue
        for usage in part_def.attributes.values():
            if architecture.resolve_attribute_def(usage) is definition:
                return True
    return False


def _clone_metadata_definition(
    architecture: Architecture,
    definition: AttributeDefinition,
    part_def: PartDefinition,
    usage_name: str,
    source_file: str,
) -> AttributeDefinition:
    name = _unique_definition_name(
        architecture, _metadata_definition_name(part_def)
    )
    clone = AttributeDefinition(
        name=name,
        doc=definition.doc,
        source_file=source_file,
        specializes=definition.specializes,
    )
    for field, attribute in definition.attributes.items():
        clone.attributes[field] = Attribute(
            name=attribute.name,
            type_name=attribute.type_name,
            value=attribute.value,
            doc=attribute.doc,
            multiplicity=attribute.multiplicity,
        )
    architecture.add_attribute_def(clone)
    part_def.attributes[usage_name] = Attribute(
        name=usage_name,
        type_name=name,
    )
    return clone


def _mark_fmu_model(part_def: PartDefinition) -> None:
    """Append the role marker, keeping every existing supertype in order."""
    if any(
        short_name(name) == FMU_MODEL_MARKER for name in part_def.specializes
    ):
        return
    part_def.specializes = (*part_def.specializes, FMU_MODEL_MARKER)


def update_fmu_metadata_from_component(
    architecture: Architecture,
    part_def: PartDefinition,
    component,
    *,
    source_file: str,
) -> None:
    """Reconcile ``implementation`` with an SSD component.

    ``source`` is authoring data and is preserved. No metadata is created when
    the component carries no implementation. A definition that ends up with
    ``fmu_meta`` is marked ``FmuModel`` and the marker is declared locally.
    """
    implementation = getattr(component, "implementation", None)

    usage = _metadata_usage(architecture, part_def)
    if usage is None:
        if implementation:
            add_fmu_metadata(
                architecture,
                part_def,
                implementation=implementation,
                source_file=source_file,
            )
            _mark_fmu_model(part_def)
            ensure_fmu_model_definition(architecture, source_file)
        return

    usage_name, _attribute, definition = usage
    if _definition_is_shared(architecture, definition, part_def):
        definition = _clone_metadata_definition(
            architecture, definition, part_def, usage_name, source_file
        )

    if implementation:
        definition.attributes["implementation"] = Attribute(
            name="implementation",
            type_name="String",
            value=implementation,
        )
    else:
        definition.attributes.pop("implementation", None)

    if not definition.attributes:
        part_def.attributes.pop(usage_name, None)
        architecture.attribute_definitions.pop(
            architecture.stored_key(definition), None
        )
        return

    _mark_fmu_model(part_def)
    ensure_fmu_model_definition(architecture, source_file)


def validate_fmu_metadata_marker(
    architecture: Architecture, *, path: str | None = None
) -> None:
    """Reject a locally declared ``fmu_meta`` on a definition without ``FmuModel``.

    A part definition that authors FMU metadata is an export unit, so it must
    explicitly specialize ``FmuModel``. The inherited, unfilled core slot is not
    a local declaration and does not trigger the rule; an unauthored
    ``FmuModel`` stays valid.
    """
    offenders = sorted(
        part_def.name
        for part_def in architecture.part_definitions.values()
        if FMU_METADATA_ATTR in part_def.attributes
        and not is_fmu_model(architecture, part_def)
    )
    if not offenders:
        return
    prefix = f"{path}: " if path is not None else ""
    raise ValueError(
        "\n".join(
            f"{prefix}{name} declares {FMU_METADATA_ATTR} but does not specialize "
            f"{FMU_MODEL_MARKER}; author "
            f"'part def {name} :> {FMU_MODEL_MARKER}'"
            for name in offenders
        )
    )


def require_fmu_metadata(
    architecture: Architecture,
    part_defs: Iterable[PartDefinition],
    *,
    implementation: str | None = None,
) -> tuple[str, ...]:
    """Report FMU metadata problems for leaf part definitions, never raising.

    Generation fails fast, where the first bad component is enough. A model
    author asking what is missing needs every component in one pass, so this
    returns the problems instead. A definition with subparts is a nested system
    and is skipped: it cannot also be an FMU component.
    """
    problems: list[str] = []
    for part_def in part_defs:
        if effective_members(architecture, part_def).parts:
            continue
        try:
            metadata = fmu_metadata(architecture, part_def)
        except ValueError as error:
            problems.append(f"{part_def.name}: {error}")
            continue
        if metadata is None:
            problems.append(
                f"{part_def.name}: no FMU metadata; declare "
                f"'attribute {FMU_METADATA_ATTR} : <Name>FmuMetadata;'"
            )
            continue
        if not metadata.source:
            problems.append(f"{part_def.name}: FMU metadata has no 'source'")
        if implementation is not None and metadata.implementation != implementation:
            problems.append(
                f"{part_def.name}: implementation is "
                f"{metadata.implementation!r}, expected {implementation!r}"
            )
    return tuple(problems)
