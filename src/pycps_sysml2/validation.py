"""Report-style validation over the dialect validators.

The validators themselves stay fail-fast: a generator stops at the first bad
marker because there is nothing to emit after it. A model author has the other
question — *what is wrong with this document?* — so this module calls every
validator, records the ``ValueError`` each one raises, and returns one report.

This module sits above both ``metadata`` and ``parameters``: composing the role,
marker, control, parameter, and FMU checks into one pass is precisely what
neither layer may do alone.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from pycps_sysml2.metadata.fmu_metadata import require_fmu_metadata
from pycps_sysml2.metadata.helpers import short_name
from pycps_sysml2.metadata.roles import (
    SSP_ROLES,
    RolePolicy,
    validate_role_markers,
)
from pycps_sysml2.model import Architecture, PartDefinition
from pycps_sysml2.parameters.dialect.composition import (
    component_definitions,
    validate_parameter_dialect,
)
from pycps_sysml2.parameters.dialect.markers import validate_marker_definitions
from pycps_sysml2.parameters.policy import SSP_POLICY, DialectPolicy


@dataclass(frozen=True)
class ValidationIssue:
    """One failed check, named by its stable code."""

    code: str
    message: str
    subject: str | None = None


@dataclass(frozen=True)
class ValidationReport:
    """What ran and what failed, in one object a caller can print."""

    checks: tuple[str, ...]
    issues: tuple[ValidationIssue, ...]

    @property
    def ok(self) -> bool:
        return not self.issues

    def raise_for_issues(self) -> None:
        """Raise every message as one ``ValueError``; no-op when ok."""
        if self.ok:
            return
        raise ValueError("\n".join(issue.message for issue in self.issues))

    def format(self) -> str:
        """One ``PASS`` line per check, one ``FAIL`` line per issue."""
        lines: list[str] = []
        for check in self.checks:
            failures = [issue for issue in self.issues if issue.code == check]
            if not failures:
                lines.append(f"PASS {check}")
            lines.extend(f"FAIL {check}: {issue.message}" for issue in failures)
        return "\n".join(lines)


def _resolve_composition(
    architecture: Architecture, composition: PartDefinition | str | None
) -> PartDefinition | None:
    if composition is None or isinstance(composition, PartDefinition):
        return composition
    definition = architecture.resolve_part(composition)
    if definition is None:
        raise ValueError(f"Unknown composition '{composition}'")
    return definition


def _non_marker_part_definitions(
    architecture: Architecture, roles: RolePolicy
) -> list[PartDefinition]:
    """Every part definition except the role markers themselves."""
    markers = {
        short_name(name)
        for name in (
            roles.model_marker,
            roles.analysis_marker,
            roles.fmu_model_marker,
        )
        if name is not None
    }
    return [
        definition
        for definition in architecture.part_definitions.values()
        if short_name(definition.name) not in markers
    ]


def validate(
    architecture: Architecture,
    composition: PartDefinition | str | None = None,
    *,
    roles: RolePolicy = SSP_ROLES,
    policy: DialectPolicy = SSP_POLICY,
) -> ValidationReport:
    """Run every dialect validator that applies and collect their failures.

    ``parameter-dialect`` needs a composition root. Without one,
    ``fmu-metadata`` covers every leaf part definition except the role markers,
    which are vocabulary, not components.
    """
    system = _resolve_composition(architecture, composition)
    checks: list[str] = []
    issues: list[ValidationIssue] = []

    def run(
        code: str,
        validator: Callable[[], None],
        subject: str | None = None,
    ) -> None:
        checks.append(code)
        try:
            validator()
        except ValueError as error:
            issues.append(
                ValidationIssue(code=code, message=str(error), subject=subject)
            )

    run("role-markers", lambda: validate_role_markers(architecture))
    run("marker-kinds", lambda: validate_marker_definitions(architecture))
    run(
        "retired-control-attributes",
        lambda: policy.control.validate(architecture),
    )
    if system is not None:
        run(
            "parameter-dialect",
            lambda: validate_parameter_dialect(
                architecture, system, policy=policy
            ),
            subject=system.name,
        )

    def check_fmu_metadata() -> None:
        definitions = (
            component_definitions(architecture, system)
            if system is not None
            else _non_marker_part_definitions(architecture, roles)
        )
        for problem in require_fmu_metadata(architecture, definitions):
            issues.append(ValidationIssue(code="fmu-metadata", message=problem))

    run("fmu-metadata", check_fmu_metadata)

    return ValidationReport(checks=tuple(checks), issues=tuple(issues))
