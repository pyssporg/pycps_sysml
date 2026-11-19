"""Opt-in specialization diagnostics and their report-style validation check.

The default load stays non-validating; ``analyze_semantics=True`` attaches only
the specialization/redefinition findings sysmlpy actually reports. The fixture
also pins the analyzer's observed gaps so a future pin bump shows what moved.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pycps_sysml2 import validate
from pycps_sysml2.model import Architecture, load
from tests.fixture_files import fixture_text
from tests.testhelpers import write_model


def _load(tmp_path: Path, name: str, *, analyze: bool = False) -> Architecture:
    path = tmp_path / name.removesuffix(".sysml") / name
    write_model(path, fixture_text(f"semantics/{name}"))
    return load(path, analyze_semantics=analyze)


@pytest.mark.parametrize(
    "name",
    [
        "clean.sysml",
        "cycle.sysml",
        "unknown-supertype.sysml",
        "kind-mismatch.sysml",
    ],
)
def test_default_load_attaches_no_semantic_issues(
    tmp_path: Path, name: str
) -> None:
    assert _load(tmp_path, name).semantic_issues == ()


def test_analyze_reports_a_specialization_cycle(tmp_path: Path) -> None:
    architecture = _load(tmp_path, "cycle.sysml", analyze=True)

    assert [issue.code for issue in architecture.semantic_issues] == [
        "cyclic-specialization",
        "cyclic-specialization",
    ]
    assert {issue.subject for issue in architecture.semantic_issues} == {"A", "B"}
    assert all(
        "Cyclic specialization" in issue.message
        for issue in architecture.semantic_issues
    )


def test_analyze_reports_a_usage_kind_mismatch(tmp_path: Path) -> None:
    architecture = _load(tmp_path, "usage-kind-mismatch.sysml", analyze=True)

    assert [issue.code for issue in architecture.semantic_issues] == [
        "kind-mismatch"
    ]
    assert architecture.semantic_issues[0].subject == "SomePortDef"
    assert "not PartDefinition" in architecture.semantic_issues[0].message


@pytest.mark.parametrize(
    "name",
    ["unknown-supertype.sysml", "kind-mismatch.sysml"],
)
def test_analyze_does_not_report_definition_level_gaps(
    tmp_path: Path, name: str
) -> None:
    """sysmlpy 0.96.4 reports neither an undefined supertype nor a def-level kind mismatch."""
    assert _load(tmp_path, name, analyze=True).semantic_issues == ()


def test_validate_reports_every_specialization_issue(tmp_path: Path) -> None:
    architecture = _load(tmp_path, "cycle.sysml", analyze=True)

    report = validate(architecture)
    failures = [issue for issue in report.issues if issue.code == "specialization"]

    assert len(failures) == len(architecture.semantic_issues) == 2
    assert not report.ok
    assert "specialization" in report.checks
    assert "FAIL specialization:" in report.format()


def test_validate_passes_specialization_without_the_flag(tmp_path: Path) -> None:
    architecture = _load(tmp_path, "cycle.sysml")

    report = validate(architecture)

    assert "specialization" in report.checks
    assert all(issue.code != "specialization" for issue in report.issues)


def test_a_clean_model_reports_no_specialization_issue(tmp_path: Path) -> None:
    architecture = _load(tmp_path, "clean.sysml", analyze=True)

    assert architecture.semantic_issues == ()
    report = validate(architecture)

    assert all(issue.code != "specialization" for issue in report.issues)
