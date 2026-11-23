"""The shipped interop vocabulary is consumed as roots, never copied.

`pyssp_sysml_definitions` ships `PyfmiInterop` beside `PysspCore`. A consumer
loads both roots and inherits the deployment parameter port instead of
re-authoring it. `InteropDeployment` must read as initialization configuration
under the reserved usage name `parameters`, never as a runtime signal, and the
interop metadata must stay outside the FMI metadata slot.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pycps_sysml2 import core_definitions, load
from pycps_sysml2.metadata.fmu_metadata import is_fmu_metadata_definition
from pycps_sysml2.parameters.dialect.declarations import (
    parameter_interface,
    validate_parameter_port_names,
)
from pycps_sysml2.parameters.dialect.markers import (
    PARAMETERS_PORT_NAME,
    is_parameter_interface,
)
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
