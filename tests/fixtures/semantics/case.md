# Case: `semantics`

Opt-in specialization diagnostics: what sysmlpy's `analyze()` reports and what
it does not, so the repo maps only real findings.

## Artifacts

All paths are relative to this directory.

| Path | Case |
| --- | --- |
| `clean.sysml` | A valid supertype chain; no semantic issue |
| `cycle.sysml` | Two part defs specialize each other; `CYCLIC_SPECIALIZATION` |
| `unknown-supertype.sysml` | A part def specializes `Missing`, which is never declared |
| `kind-mismatch.sysml` | A part def specializes a port def |
| `usage-kind-mismatch.sysml` | A part usage is typed by a port def; `INCOMPATIBLE_PART_DEFINITION` |

## What this case proves

`load()` is non-validating by default: every document loads with an empty
`semantic_issues` tuple. With `analyze_semantics=True`, the cycle document
attaches `cyclic-specialization` issues, and the usage document attaches a
`kind-mismatch` issue.

The two definition-level shapes are also evidence of the pin's limits:
sysmlpy 0.96.4 reports neither an undefined supertype nor a definition-level
kind mismatch, so those documents stay empty under `analyze()`. The test
asserts that gap instead of inventing a mapping.

## Update history

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-19 | Created | Evidence for opt-in specialization diagnostics and the analyzer's observed coverage |

## Provenance

Authored here for `tests/test_semantics.py`; no document was copied from
another tree.
