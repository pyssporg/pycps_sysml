"""Specialization diagnostics from sysmlpy's semantic analyzer.

The analyzer is the oracle for specialization and redefinition facts; this
module only translates its issues into the repo-owned
:class:`~pycps_sysml.model.model.SemanticIssue` shape. It imports no
``sysmlpy``: the one call site lives in
:func:`pycps_sysml.model.parser.analyze_semantics`, per the parser boundary.

Only codes sysmlpy 0.96.4 actually emits for such a fact are mapped. In that
release an undefined supertype and a definition-level kind mismatch (a
``part def`` specializing a ``port def``) are not reported at all, so they
have no mapping here rather than a guessed one; the usage-level kind mismatch
codes are mapped because they are the same fault on a typing.
"""

from __future__ import annotations

from pycps_sysml.model.model import SemanticIssue
from pycps_sysml.model.parser import analyze_semantics

__all__ = ["specialization_issues"]

#: sysmlpy issue code -> repo-owned code string.
_ISSUE_CODES = {
    "CYCLIC_SPECIALIZATION": "cyclic-specialization",
    "INCOMPATIBLE_REDEFINITION": "incompatible-redefinition",
    "INCOMPATIBLE_PART_DEFINITION": "kind-mismatch",
    "INCOMPATIBLE_PORT_DEFINITION": "kind-mismatch",
}


def specialization_issues(model) -> tuple[SemanticIssue, ...]:
    """Repo semantic issues for specialization/redefinition problems in *model*.

    *model* is the parsed sysmlpy model the loader already holds; the function
    runs ``analyze()`` once and drops every unrelated finding (undefined
    symbols, imports, connectors, style). ``resolve_types()`` is not called:
    the analyzer resolves its own references and its result is unchanged by
    type linking.
    """
    issues = []
    for issue in analyze_semantics(model):
        code = _ISSUE_CODES.get(issue.code)
        if code is None:
            continue
        issues.append(
            SemanticIssue(
                code=code,
                message=issue.message,
                subject=_subject(issue),
            )
        )
    return tuple(issues)


def _subject(issue) -> str | None:
    """Best-effort element or reference name for one sysmlpy issue."""
    reference = getattr(issue, "reference", "")
    if reference:
        return reference
    element = getattr(issue, "element", None)
    name = getattr(element, "name", None)
    return name if isinstance(name, str) and name else None
