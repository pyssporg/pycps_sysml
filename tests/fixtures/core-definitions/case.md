# Case: `core-definitions`

Input for `tests/test_core_definitions.py`: a model that uses the shared dialect
markers without declaring them, so the test can compare the default load with a
load that merges the bundled core definitions.

## Artifacts

| Path | Behaviour |
| --- | --- |
| `marker-user.sysml` | imports `ScalarValues` and `PysspCore`, then specializes `SspModel`, `FmuModel`, and `Analysis` without declaring them, covering an inherited-unfilled slot, a locally authored concrete metadata subtype, and a parameter interface |

## What this case proves

The fixture has no local marker declarations, so the default load leaves every
marker unresolved and the validation gates fail. Loading it with
`load(model, core_definitions())` must resolve the markers, keep the included
definitions out of `export_declared()`, and succeed for role, parameter, and FMU
metadata lookups.

It also proves definition-level part-def inheritance: `System` and
`UnconfiguredBall` author no local metadata slot, yet their effective members
carry the `ssp_meta`/`fmu_meta` slot typed by the core `SspMetadata`/`FmuMetadata`
definition, while the metadata accessors read an inherited unfilled slot as
"no metadata". `LegacySystem` and `Ball` show the authored counterpart: they
specialize the same core marker and write a concrete metadata subtype with a
`source` value in that inherited slot name.

## Update history

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-05 | Case record and `marker-user.sysml` added | The core-definition library test needs a marker-free model as reviewable SysML, not a Python literal |
| 2026-11-20 | Extended `marker-user.sysml` with inherited-slot, authored-subtype, and `Analysis` definitions | Prove that a marker-specializing part def inherits its metadata slot from `core.sysml`, not from a local declaration |
