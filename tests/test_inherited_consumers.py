"""Consumer accessors read the effective member view, inherited members included."""

from __future__ import annotations

from pathlib import Path

import pytest

from pycps_sysml2 import core_definitions
from pycps_sysml2.metadata.fmu_metadata import (
    FmuMetadata,
    fmu_metadata,
    require_fmu_metadata,
)
from pycps_sysml2.metadata.roles import (
    SSP_ROLES,
    Experiment,
    model_usage,
    read_experiment,
    require_resolved_variation,
)
from pycps_sysml2.metadata.ssp_metadata import ssp_metadata
from pycps_sysml2.model import Architecture, load
from pycps_sysml2.parameters.dialect.composition import (
    applied_sets,
    component_refs,
    set_usages,
)
from pycps_sysml2.parameters.dialect.declarations import (
    parameter_declarations,
    parameter_port,
)
from pycps_sysml2.parameters.dialect.mapping import mapping_entries
from pycps_sysml2.parameters.dialect.markers import is_parameter_interface
from pycps_sysml2.parameters.policy import SSP_POLICY
from pycps_sysml2.parameters.variation import resolve
from tests.fixture_files import fixture_text
from tests.testhelpers import write_model


def _load(tmp_path: Path) -> Architecture:
    path = tmp_path / "inheritance-consumers" / "consumers.sysml"
    write_model(path, fixture_text("inheritance-consumers/consumers.sysml"))
    return load(path, core_definitions())


def test_derived_analysis_reads_the_inherited_experiment(tmp_path: Path) -> None:
    architecture = _load(tmp_path)

    experiment = read_experiment(
        architecture,
        architecture.get_part_def("DerivedAnalysis"),
        required=True,
    )

    assert experiment == Experiment(
        name="experiment_baseline",
        start_time=0.0,
        stop_time=2.0,
        step_size=0.01,
    )


def test_derived_ssp_model_reads_the_inherited_ssp_metadata(
    tmp_path: Path,
) -> None:
    architecture = _load(tmp_path)

    metadata = ssp_metadata(architecture, architecture.get_part_def("DerivedSsp"))

    assert metadata is not None
    assert metadata.source == "models/ssp/inherited"


def test_derived_fmu_model_reads_the_inherited_fmu_metadata(
    tmp_path: Path,
) -> None:
    architecture = _load(tmp_path)

    metadata = fmu_metadata(
        architecture, architecture.get_part_def("DerivedFmuPart")
    )

    assert metadata == FmuMetadata(
        source="build/fmus/Inherited.fmu",
        implementation="CoSimulation",
    )


def test_inherited_subpart_makes_a_derived_fmu_part_a_nested_system(
    tmp_path: Path,
) -> None:
    architecture = _load(tmp_path)
    part_def = architecture.get_part_def("DerivedNestedFmu")

    assert part_def.parts == {}
    with pytest.raises(ValueError, match="both subparts"):
        fmu_metadata(architecture, part_def)
    assert require_fmu_metadata(architecture, [part_def]) == ()


def test_analysis_reads_an_inherited_model_usage(tmp_path: Path) -> None:
    architecture = _load(tmp_path)

    usage, definition = model_usage(
        architecture, architecture.get_part_def("DerivedModelUsageAnalysis")
    )

    assert (usage.name, definition.name) == ("sut", "ModelUsageModel")


def test_analysis_finds_an_inherited_variation_point(tmp_path: Path) -> None:
    architecture = _load(tmp_path)

    with pytest.raises(ValueError, match="Variation point 'source'"):
        require_resolved_variation(
            architecture, architecture.get_part_def("DerivedVariationAnalysis")
        )


def test_variant_body_connection_resolves_an_inherited_parameter_port(
    tmp_path: Path,
) -> None:
    architecture = _load(tmp_path)
    component = architecture.get_part_def("InheritedParametersComponent")

    assert "parameters" not in component.ports
    resolved = resolve(
        architecture,
        "InheritedPortSystem",
        {"path": "directPath"},
        roles=SSP_ROLES,
    )
    synthesized = resolved.get_part_def("InheritedPortChoice__directPath")
    assert synthesized.connections == {}


def test_derived_parameter_interface_contributes_inherited_members(
    tmp_path: Path,
) -> None:
    architecture = _load(tmp_path)

    declarations = parameter_declarations(
        architecture, architecture.get_part_def("PortOwner")
    )

    assert [attribute.name for attribute in declarations] == [
        "base_member",
        "derived_member",
    ]


def test_composition_sees_an_inherited_parameter_set_usage(
    tmp_path: Path,
) -> None:
    architecture = _load(tmp_path)

    usages = set_usages(
        architecture,
        architecture.get_part_def("DerivedSetOwner"),
        policy=SSP_POLICY,
    )

    assert list(usages) == ["nominal"]


def test_derived_part_reads_the_inherited_parameters_port(
    tmp_path: Path,
) -> None:
    architecture = _load(tmp_path)

    owner = architecture.get_part_def("InheritedPortOwner")

    assert "parameters" not in owner.ports
    port = parameter_port(architecture, owner)
    assert port is not None
    assert port.type_name == "DerivedParameters"
    assert [
        attribute.name
        for attribute in parameter_declarations(architecture, owner)
    ] == ["base_member", "derived_member"]


def test_port_definition_inherits_the_parameter_interface_marker(
    tmp_path: Path,
) -> None:
    architecture = _load(tmp_path)

    derived = architecture.get_port_def("MarkerDerived")

    assert derived.specializes == ("MarkerBase",)
    assert is_parameter_interface(architecture, derived)


def test_component_walk_sees_an_inherited_subpart(tmp_path: Path) -> None:
    architecture = _load(tmp_path)

    system = architecture.get_part_def("DerivedComposition")
    refs = component_refs(architecture, system)

    assert system.parts == {}
    assert [(ref.path, ref.part_def.name) for ref in refs] == [
        (("inherited_child",), "LeafPart")
    ]
    assert [
        usage.name
        for usage in architecture.iter_effective_part_usages(system)
    ] == ["inherited_child"]


def test_mapping_expands_an_inherited_interface_member(tmp_path: Path) -> None:
    architecture = _load(tmp_path)

    system = architecture.get_part_def("MappingOwner")
    applications = applied_sets(architecture, system, policy=SSP_POLICY)

    assert len(applications) == 1
    assert mapping_entries(
        architecture, system, applications[0], policy=SSP_POLICY
    ) == [
        ("base_member", "component.base_member"),
        ("derived_member", "component.derived_member"),
    ]
