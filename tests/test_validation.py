"""Report-style validation: every check runs, failures are collected by code.

The validators keep their fail-fast contract; this file is evidence for the
other direction. One failing fixture per check makes a wrong code visible, and
the passing fixture pins the order and the ``PASS``/``FAIL`` layout of a report.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pycps_sysml2 import ValidationIssue, ValidationReport, validate
from pycps_sysml2.metadata import require_fmu_metadata
from pycps_sysml2.model import Architecture, load
from tests.fixture_files import fixture_text
from tests.testhelpers import write_model


CHECKS = (
    "role-markers",
    "marker-kinds",
    "retired-control-attributes",
    "parameter-dialect",
    "fmu-metadata",
)


def _load(tmp_path: Path, case: str) -> Architecture:
    architecture_dir = tmp_path / case.removesuffix(".sysml")
    write_model(
        architecture_dir / "model.sysml",
        fixture_text(f"validation/{case}"),
    )
    return load(architecture_dir)


def _codes(report: ValidationReport) -> list[str]:
    return [issue.code for issue in report.issues]


def test_a_clean_model_passes_every_check(tmp_path: Path) -> None:
    architecture = _load(tmp_path, "passing.sysml")
    report = validate(architecture, "System")

    assert report.ok
    assert report.issues == ()
    assert report.checks == CHECKS
    assert report.format().splitlines() == [f"PASS {check}" for check in CHECKS]
    assert validate(architecture, architecture.get_part_def("System")) == report


def test_without_a_composition_the_parameter_check_is_not_run(
    tmp_path: Path,
) -> None:
    report = validate(_load(tmp_path, "passing.sysml"))

    assert report.ok
    assert "parameter-dialect" not in report.checks


def test_a_missing_role_marker_is_reported(tmp_path: Path) -> None:
    report = validate(_load(tmp_path, "role-marker.sysml"))

    assert _codes(report) == ["role-markers"]
    assert "Role marker 'SspModel'" in report.issues[0].message
    assert not report.ok


def test_a_marker_on_the_wrong_kind_is_reported(tmp_path: Path) -> None:
    report = validate(_load(tmp_path, "marker-kind.sysml"))

    assert _codes(report) == ["marker-kinds"]
    assert "must be port defs" in report.issues[0].message


def test_a_retired_control_attribute_is_reported(tmp_path: Path) -> None:
    report = validate(_load(tmp_path, "retired-control.sysml"))

    assert _codes(report) == ["retired-control-attributes"]
    assert "pyssp_implementation" in report.issues[0].message


def test_a_flat_parameter_is_reported_for_a_composition(tmp_path: Path) -> None:
    report = validate(_load(tmp_path, "parameter-dialect.sysml"), "System")

    assert _codes(report) == ["parameter-dialect"]
    assert report.issues[0].subject == "System"
    assert "flat parameter attribute" in report.issues[0].message


def test_missing_fmu_metadata_is_reported(tmp_path: Path) -> None:
    report = validate(_load(tmp_path, "missing-fmu-meta.sysml"))

    assert _codes(report) == ["fmu-metadata"]
    assert "no FMU metadata" in report.issues[0].message


def test_a_wrong_fmu_meta_type_is_reported(tmp_path: Path) -> None:
    report = validate(_load(tmp_path, "wrong-fmu-meta.sysml"))

    assert _codes(report) == ["fmu-metadata"]
    assert "must be typed" in report.issues[0].message


def test_an_implementation_mismatch_is_reported(tmp_path: Path) -> None:
    architecture = _load(tmp_path, "implementation-mismatch.sysml")
    component = architecture.get_part_def("Component")

    assert require_fmu_metadata(architecture, [component]) == ()
    problems = require_fmu_metadata(
        architecture, [component], implementation="CoSimulation"
    )

    assert len(problems) == 1
    assert "expected 'CoSimulation'" in problems[0]


def test_require_fmu_metadata_skips_a_nested_system(tmp_path: Path) -> None:
    architecture = _load(tmp_path, "passing.sysml")
    system = architecture.get_part_def("System")

    assert require_fmu_metadata(architecture, [system]) == ()


def test_format_and_raise_report_every_issue_under_its_check() -> None:
    report = ValidationReport(
        checks=("alpha", "beta"),
        issues=(
            ValidationIssue(code="beta", message="first"),
            ValidationIssue(code="beta", message="second"),
        ),
    )

    assert report.format() == (
        "PASS alpha\nFAIL beta: first\nFAIL beta: second"
    )
    with pytest.raises(ValueError) as excinfo:
        report.raise_for_issues()
    assert str(excinfo.value) == "first\nsecond"


def test_raise_for_issues_is_a_no_op_when_ok() -> None:
    ValidationReport(checks=("alpha",), issues=()).raise_for_issues()
