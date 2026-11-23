# Case: `build-metadata`

Input for the composition classifier: every build-metadata family in one place,
so the recognition order is pinned. `FmuMetadata`, `SspMetadata`, and the
generic family base `SourcedMetadata` all reach the base; a plain typed
attribute does not.

## Artifacts

| Path | Kind |
| --- | --- |
| `precedence.sysml` | Input, one part declaring the two reserved metadata slots and a plain typed attribute |

The model copies no vocabulary: it imports the shipped `PysspCore` root and
derives `CompFmu`/`CompSsp` from the shipped containers.

## What this case proves

An attribute is classified by the type of its container, in this order: FMU
metadata, SSP metadata, another `SourcedMetadata` family container, then any
other resolved type. `fmu_meta` stays FMU metadata and `ssp_meta` stays SSP
metadata even though both also reach the family base; `note` stays a plain
typed attribute. Only the generic container is build metadata with no reserved
slot.

## Update history

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-23 | Case record and `precedence.sysml` added | The classifier gained the generic `SourcedMetadata` family case and needs its precedence pinned |

## Provenance

Authored here for `tests/test_interop_definitions.py`.
