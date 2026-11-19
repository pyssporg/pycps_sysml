"""Retired ``pyssp_*`` attribute names and their migration errors.

The ``pyssp_*`` attribute vocabulary is gone. Every special datum is carried by
a typed attribute container — ``attribute <name> : <Def>;`` where ``<Def>`` is
an ``attribute def`` specializing a marker (``SspMetadata``, ``FmuMetadata``,
``DefaultExperiment``/``Experiment``, ``ParameterSet``) — or by a ``part def``
marker supertype. Recognition is by type, never by name.

This module keeps only the migration rule: a document that still writes one of
the removed names must fail with the replacement, never pass silently. The
residual rule is deliberately a catch-all: any other ``pyssp_`` name is an
error too, because the whole prefix was removed in 0.3.0.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pycps_sysml2.model import Architecture, Definition

#: Removed attribute names and the replacement to write instead.
RETIRED_ATTRIBUTES: dict[str, str] = {
    "pyssp_default_start_time": (
        "declare 'attribute defaults : <X>DefaultExperiment { attribute "
        "startTime = ...; attribute stopTime = ...; }' instead"
    ),
    "pyssp_default_stop_time": (
        "declare 'attribute defaults : <X>DefaultExperiment { attribute "
        "startTime = ...; attribute stopTime = ...; }' instead"
    ),
    "pyssp_flat_connector": (
        "pass --flat-connector at export time; it is not model data"
    ),
    "pyssp_implementation": (
        "use 'attribute fmu_meta : <Part>FmuMetadata { attribute "
        "implementation = \"...\"; }'"
    ),
    "pyssp_parameter_set": (
        "define an 'attribute def <Set> :> ParameterSet' and bind it to the "
        "component with 'bind'"
    ),
}

#: The removed vocabulary's prefix. A private literal: the prefix is history,
#: not a configurable control vocabulary.
_RETIRED_PREFIX = "pyssp_"

#: The migration error for a ``pyssp_`` name absent from the retired map.
_REMOVED_VOCABULARY = (
    "the 'pyssp_*' attribute vocabulary was removed in 0.3.0. Declare a typed "
    "attribute container instead: 'attribute <name> : <Def>;' where '<Def>' "
    "is an attribute def specializing a marker"
)


def _unsupported(definition: Definition, name: str, message: str) -> ValueError:
    location = f" in {definition.source_file}" if definition.source_file else ""
    return ValueError(
        f"{definition.name}.{name}{location} is no longer supported; {message}"
    )


def validate_retired_attributes(architecture: Architecture) -> None:
    """Reject every remaining ``pyssp_*`` attribute, naming its replacement.

    Definitions and their attributes are scanned in declaration order, so the
    first removed name raises. A name in :data:`RETIRED_ATTRIBUTES` gets its
    targeted hint; any other ``pyssp_`` name gets the residual error. Neither
    is ever skipped.
    """
    definitions = list(architecture.part_definitions.values()) + list(
        architecture.port_definitions.values()
    )
    for definition in definitions:
        for name in definition.attributes:
            message = RETIRED_ATTRIBUTES.get(name)
            if message is not None:
                raise _unsupported(definition, name, message)
            if name.startswith(_RETIRED_PREFIX):
                raise _unsupported(definition, name, _REMOVED_VOCABULARY)
