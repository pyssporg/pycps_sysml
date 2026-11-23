"""A nested part that specializes ``FmuModel`` keeps its own subparts.

``FmuModel`` declares ``attribute fmu_meta : FmuMetadata;`` as an inherited
schema slot. A definition that inherits the marker without filling the slot
authors no metadata, so it is a nested system rather than an FMU component.
"""

from __future__ import annotations

from pathlib import Path

from pycps_sysml2 import core_definitions, load, validate
from pycps_sysml2.metadata import fmu_metadata
from pycps_sysml2.model import Architecture
from tests.fixture_files import fixture_text
from tests.testhelpers import write_model


def _load(tmp_path: Path) -> Architecture:
    model_dir = tmp_path / "nested-fmu-model"
    write_model(
        model_dir / "model.sysml",
        fixture_text("nested-fmu-model/model.sysml"),
    )
    return load(model_dir, core_definitions())


def test_a_nested_fmu_model_validates_and_keeps_its_subparts(
    tmp_path: Path,
) -> None:
    architecture = _load(tmp_path)
    subsystem = architecture.get_part_def("Subsystem")

    report = validate(architecture, "System")

    assert report.ok, report.format()
    assert set(subsystem.parts) == {"leaf"}
    assert fmu_metadata(architecture, subsystem) is None


def test_an_authored_fmu_meta_without_the_marker_is_still_rejected(
    tmp_path: Path,
) -> None:
    model_dir = tmp_path / "unmarked"
    write_model(
        model_dir / "model.sysml",
        fixture_text("validation/fmu-marker.sysml"),
    )
    architecture = load(model_dir, core_definitions())

    report = validate(architecture)

    assert [issue.code for issue in report.issues] == ["fmu-marker"]
    assert "does not specialize FmuModel" in report.issues[0].message
