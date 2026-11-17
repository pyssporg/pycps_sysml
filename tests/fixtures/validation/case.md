# Case: `validation`

One passing architecture and one failing document per validation check, so a
report names the check that failed and nothing else. Each document is small on
purpose: the failing shape is the evidence, and the test asserts the stable code
rather than restating the SysML.

## Artifacts

All paths are relative to this directory.

| Path | Case |
| --- | --- |
| `passing.sysml` | An FMU composition whose components carry typed metadata; every check passes |
| `role-marker.sysml` | `SspModel` is used as a supertype but never defined |
| `marker-kind.sysml` | `ParameterInterface` is specialized by an attribute def, not a port def |
| `retired-control.sysml` | A part attribute uses the retired `pyssp_implementation` |
| `missing-fmu-meta.sysml` | A leaf part definition has no FMU metadata |
| `wrong-fmu-meta.sysml` | `fmu_meta` is typed by a definition that is not marked `FmuMetadata` |
| `implementation-mismatch.sysml` | Metadata says `ModelExchange` where `CoSimulation` is required |
| `parameter-dialect.sysml` | A component has a flat parameter attribute |

## What this case proves

`validate()` runs every applicable validator, records each `ValueError` under its
stable check code, and leaves the validators fail-fast. A clean document reports
one `PASS` per check; each failing document reports exactly its own code, so a
new check cannot be satisfied by another check's error. The implementation
mismatch is asserted through `require_fmu_metadata`, which returns problems
instead of raising.

## Update history

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-17 | Case record and eight documents added | The report entry point needs one reviewable failing shape per check |

## Provenance

Authored for this repository; no document was copied from another tree.
