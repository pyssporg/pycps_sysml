"""The shipped interop vocabulary is consumed as roots, never copied.

`pyssp_sysml_definitions` ships `PyfmiInterop` beside `PysspCore`. A consumer
loads both roots and inherits the deployment parameter port instead of
re-authoring it. `InteropDeployment` must read as initialization configuration
under the reserved usage name `parameters`, never as a runtime signal, and the
interop metadata must stay outside the FMI metadata slot. It is still build
metadata: the family base `SourcedMetadata` classifies it as such, after the
FMU and SSP containers that have reserved slots.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pycps_sysml2 import core_definitions, load
from pycps_sysml2.metadata import (
    SOURCED_METADATA_MARKER,
    fmu_metadata,
    is_sourced_metadata_definition,
    is_ssp_metadata_definition,
    ssp_metadata,
)
from pycps_sysml2.metadata.fmu_metadata import is_fmu_metadata_definition
from pycps_sysml2.metadata.helpers import specializes_marker_deep
from pycps_sysml2.parameters.dialect.composition import (
    AttributeKind,
    classify_attribute,
    validate_parameter_dialect,
)
from pycps_sysml2.parameters.dialect.declarations import (
    parameter_interface,
    validate_parameter_port_names,
)
from pycps_sysml2.parameters.dialect.markers import (
    PARAMETERS_PORT_NAME,
    is_parameter_interface,
)
from pycps_sysml2.parameters.policy import SSP_POLICY
from pyssp_sysml_definitions import include_roots, interop_definitions
from tests.fixture_files import fixture_text
from tests.testhelpers import write_model


def test_include_roots_returns_core_before_interop() -> None:
    roots = include_roots()

    assert roots == (core_definitions(), interop_definitions())
    assert [path.name for path in roots] == ["core.sysml", "interop.sysml"]


def test_interop_definitions_parses_as_the_interop_package() -> None:
    architecture = load(interop_definitions(), core_definitions())

    assert architecture.package_name == "PyfmiInterop"
    deployment = architecture.get_port_def("InteropDeployment")
    assert deployment.specializes == ("ParameterInterface",)
    assert is_parameter_interface(architecture, deployment)


def test_interop_deployment_is_initialization_never_a_runtime_signal() -> None:
    architecture = load(interop_definitions(), core_definitions())
    fmu_interop = architecture.get_part_def("FmuInterop")

    assert list(fmu_interop.ports) == [PARAMETERS_PORT_NAME]
    usage = fmu_interop.ports[PARAMETERS_PORT_NAME]
    assert usage.direction == "in"
    assert usage.type_name == "InteropDeployment"

    metadata = architecture.resolve_attribute_def("InteropMetadata")
    assert metadata is not None
    assert not is_fmu_metadata_definition(architecture, metadata)


def test_interop_metadata_reaches_the_family_base() -> None:
    architecture = load(interop_definitions(), core_definitions())
    metadata = architecture.get_attribute_def("InteropMetadata")

    assert specializes_marker_deep(
        architecture, metadata, SOURCED_METADATA_MARKER
    )
    assert is_sourced_metadata_definition(architecture, metadata)
    assert not is_fmu_metadata_definition(architecture, metadata)
    assert not is_ssp_metadata_definition(architecture, metadata)


def test_interop_meta_is_family_build_metadata_without_a_slot() -> None:
    architecture = load(interop_definitions(), core_definitions())
    fmu_interop = architecture.get_part_def("FmuInterop")
    usage = fmu_interop.attributes["interop_meta"]

    assert (
        classify_attribute(architecture, usage, policy=SSP_POLICY)
        is AttributeKind.SOURCED_METADATA
    )
    # It validates as a component attribute and records into neither slot, so
    # neither exporter sees new metadata for this part.
    validate_parameter_dialect(architecture, fmu_interop, policy=SSP_POLICY)
    assert fmu_metadata(architecture, fmu_interop) is None
    assert ssp_metadata(architecture, fmu_interop) is None


def test_fmu_and_ssp_keep_precedence_over_the_family_base(
    tmp_path: Path,
) -> None:
    model = tmp_path / "model.sysml"
    write_model(model, fixture_text("build-metadata/precedence.sysml"))
    architecture = load(model, core_definitions())
    holder = architecture.get_part_def("Holder")

    kinds = {
        name: classify_attribute(architecture, usage, policy=SSP_POLICY)
        for name, usage in holder.attributes.items()
    }
    assert kinds == {
        "fmu_meta": AttributeKind.FMU_METADATA,
        "ssp_meta": AttributeKind.SSP_METADATA,
        "note": AttributeKind.TYPED,
    }


def test_a_shipped_interop_component_reads_the_inherited_parameters_port(
    tmp_path: Path,
) -> None:
    model = tmp_path / "model.sysml"
    write_model(model, fixture_text("interop-definitions/link.sysml"))
    architecture = load(model, *include_roots())
    link = architecture.get_part_def("Link")

    interface = parameter_interface(architecture, link)
    assert interface is not None
    assert interface.name == "InteropDeployment"
    validate_parameter_port_names(architecture, link)
    assert "parameters" not in link.ports


def test_a_shipped_interface_under_another_name_is_rejected(tmp_path: Path) -> None:
    model = tmp_path / "model.sysml"
    write_model(
        model,
        """package Bad {
  private import PysspCore::*;
  private import PyfmiInterop::*;

  part def BadLink :> FmuInterop {
    in port gains : InteropDeployment;
  }
}""",
    )
    architecture = load(model, *include_roots())

    with pytest.raises(ValueError, match="must be named 'parameters'"):
        validate_parameter_port_names(
            architecture, architecture.get_part_def("BadLink")
        )
