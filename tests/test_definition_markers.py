"""The shipped vocabulary and the code constants must stay in sync.

Marker names, metadata slot names, and member names live twice by design: once
in Python as constants the dialect reads, and once in ``core.sysml`` as the
definitions a model includes. A rename or field change in either place that
misses the other would split the vocabulary across releases, so this guard
parses the shipped file through the dialect, derives the expected shapes from
the code constants, and fails with the definition name and the difference.
"""

from __future__ import annotations

import importlib

from pycps_sysml2 import core_definitions, load
from pycps_sysml2.metadata import (
    DEFAULT_EXPERIMENT_MARKER,
    EXPERIMENT_MARKER,
    FMU_METADATA_MARKER,
    SOURCED_METADATA_MARKER,
    SSP_METADATA_MARKER,
    is_default_experiment_definition,
)
from pycps_sysml2.metadata.helpers import specializes_marker_deep
from pycps_sysml2.model import Architecture, Definition, effective_members
from pyssp_sysml_definitions import interop_definitions

#: Modules whose module-level constants are part of the vocabulary contract.
_MODULE_NAMES = (
    "pycps_sysml2.metadata.roles",
    "pycps_sysml2.metadata.fmu_metadata",
    "pycps_sysml2.metadata.sourced_metadata",
    "pycps_sysml2.metadata.ssp_metadata",
    "pycps_sysml2.parameters.dialect.markers",
)

#: Constant suffixes that name a term ``core.sysml`` must declare. A port name
#: (``PARAMETERS_PORT_NAME``) and the SSD implementation enumeration
#: (``FMU_IMPLEMENTATION_VALUES``) are authoring/deployment vocabulary, not
#: definitions the core library declares, so they are deliberately out of scope.
_TERM_SUFFIXES = ("_MARKER", "_ATTR", "_FIELDS")


def _vocabulary_terms() -> set[str]:
    """Read the constants from the owning modules; never restate their values."""

    terms: set[str] = set()
    for module_name in _MODULE_NAMES:
        module = importlib.import_module(module_name)
        for name, value in vars(module).items():
            if not name.endswith(_TERM_SUFFIXES):
                continue
            if isinstance(value, str):
                terms.add(value)
            elif isinstance(value, tuple):
                terms.update(item for item in value if isinstance(item, str))
    return terms


def _constant(module_name: str, name: str) -> tuple[str, ...]:
    """Read one vocabulary constant from its owning module."""

    return getattr(importlib.import_module(module_name), name)


def _attribute_members(
    architecture: Architecture, definition: Definition
) -> set[str]:
    return set(effective_members(architecture, definition).attributes)


def _assert_attribute_members(
    architecture: Architecture,
    definition: Definition,
    expected: tuple[str, ...] | set[str],
    *,
    source: str,
) -> None:
    actual = _attribute_members(architecture, definition)
    expected = set(expected)
    assert actual == expected, (
        f"{definition.name} members drifted from {source}: core.sysml declares "
        f"{sorted(actual)}, code expects {sorted(expected)}; "
        f"missing from core.sysml: {sorted(expected - actual)}; "
        f"missing from code: {sorted(actual - expected)}"
    )


def _assert_no_members(
    architecture: Architecture, definition: Definition
) -> None:
    view = effective_members(architecture, definition)
    found = {
        "attributes": sorted(view.attributes),
        "ports": sorted(view.ports),
        "parts": sorted(view.parts),
        "connections": sorted(view.connections),
        "bindings": len(view.bindings),
        "constraints": len(view.constraints),
    }
    assert not any(found.values()), (
        f"{definition.name} must stay an empty marker; found {found}"
    )


def test_core_definitions_carry_every_vocabulary_constant() -> None:
    text = core_definitions().read_text(encoding="utf-8")

    missing = sorted(term for term in _vocabulary_terms() if term not in text)

    assert not missing, (
        "core.sysml no longer carries these constants from code: "
        + ", ".join(missing)
    )


def test_core_definitions_state_the_reserved_parameter_port_name() -> None:
    """The reserved usage name is canonical in ``core.sysml``, not only code."""

    markers = importlib.import_module("pycps_sysml2.parameters.dialect.markers")
    text = core_definitions().read_text(encoding="utf-8")

    assert f"in port {markers.PARAMETERS_PORT_NAME}" in text


def test_shipped_metadata_definitions_match_the_code_fields() -> None:
    architecture = load(core_definitions())
    fmu_fields = _constant(
        "pycps_sysml2.metadata.fmu_metadata", "FMU_METADATA_FIELDS"
    )
    ssp_fields = _constant(
        "pycps_sysml2.metadata.ssp_metadata", "SSP_METADATA_FIELDS"
    )

    _assert_attribute_members(
        architecture,
        architecture.get_attribute_def(FMU_METADATA_MARKER),
        fmu_fields,
        source="FMU_METADATA_FIELDS",
    )
    _assert_attribute_members(
        architecture,
        architecture.get_attribute_def(SSP_METADATA_MARKER),
        ssp_fields,
        source="SSP_METADATA_FIELDS",
    )


def test_shipped_experiment_definitions_match_the_code_fields() -> None:
    architecture = load(core_definitions())
    experiment_fields = _constant(
        "pycps_sysml2.metadata.roles", "EXPERIMENT_FIELDS"
    )
    experiment = architecture.get_attribute_def(EXPERIMENT_MARKER)
    default = architecture.get_attribute_def(DEFAULT_EXPERIMENT_MARKER)

    _assert_attribute_members(
        architecture,
        experiment,
        experiment_fields,
        source="EXPERIMENT_FIELDS",
    )
    # EXPERIMENT_FIELDS is the FMI superset and Experiment is the container that
    # adds to DefaultExperiment, so the default subset is derived from the
    # superset minus Experiment's own declarations instead of restated.
    expected_default = set(experiment_fields) - set(experiment.attributes)
    _assert_attribute_members(
        architecture,
        default,
        expected_default,
        source="EXPERIMENT_FIELDS minus Experiment's own members",
    )


def test_shipped_definitions_keep_their_supertype_chains() -> None:
    architecture = load(interop_definitions(), core_definitions())

    # Every build-metadata container reaches the family base; InteropMetadata
    # ships beside the core vocabulary and is the one that is not FMU or SSP.
    for name in (FMU_METADATA_MARKER, SSP_METADATA_MARKER, "InteropMetadata"):
        definition = architecture.get_attribute_def(name)
        assert specializes_marker_deep(
            architecture, definition, SOURCED_METADATA_MARKER
        ), f"{name} no longer reaches {SOURCED_METADATA_MARKER}"

    experiment = architecture.get_attribute_def(EXPERIMENT_MARKER)
    assert is_default_experiment_definition(architecture, experiment), (
        f"{EXPERIMENT_MARKER} no longer reaches {DEFAULT_EXPERIMENT_MARKER}"
    )


def test_shipped_parameter_markers_stay_empty() -> None:
    architecture = load(core_definitions())
    markers = importlib.import_module("pycps_sysml2.parameters.dialect.markers")

    _assert_no_members(
        architecture,
        architecture.get_port_def(markers.PARAMETER_INTERFACE_MARKER),
    )
    _assert_no_members(
        architecture,
        architecture.get_attribute_def(markers.PARAMETER_SET_MARKER),
    )


def test_the_export_import_covers_exactly_the_shipped_definitions() -> None:
    """Every name the exporter treats as shipped is declared by ``PysspCore``.

    The exporter emits ``private import PysspCore::*;`` for these names and
    omits a synthesized copy, so a name that is not in ``core.sysml`` would
    silently export an unresolvable reference.
    """

    from pycps_sysml2.model.exporter import SHIPPED_DEFINITIONS

    architecture = load(core_definitions())
    declared = (
        set(architecture.attribute_definitions)
        | set(architecture.part_definitions)
        | set(architecture.port_definitions)
    )
    missing = sorted(SHIPPED_DEFINITIONS - declared)

    assert not missing, (
        "the exporter treats these names as shipped, but core.sysml does not "
        "declare them: " + ", ".join(missing)
    )
