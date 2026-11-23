# Case: `nested-fmu-model`

Regression input for the composition classifier: a part definition inherits
the shipped `FmuModel` marker, keeps its own subparts, and never fills the
inherited `fmu_meta` slot. That slot is a schema placeholder, not authored
metadata, so the definition is a nested system rather than an FMU component.

## Artifacts

| Path | Behaviour |
| --- | --- |
| `model.sysml` | A leaf `FmuModel` with typed metadata and a nested `FmuModel` with a subpart, composed by an `SspModel` root |

## What this case proves

The inherited, unfilled slot from `FmuModel` is not classified as authored FMU
metadata. A nested part that specializes `FmuModel` validates and keeps its
subparts. Authored `fmu_meta` on a part without the marker stays rejected by
the `fmu-marker` check.

## Update history

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-23 | Case record and `model.sysml` added | The composition classifier treated the inherited `fmu_meta` slot as authored metadata and rejected a legitimate nested system |
