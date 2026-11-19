# Case: `experiment`

Typed experiment containers: a plain `DefaultExperiment` needs only start and
stop, while an `Experiment` subtype also needs a step size. The multiple case
carries two containers on one exported part, which is always rejected.

## Artifacts

| Path | Case |
| --- | --- |
| `baseline.sysml` | One analysis carrying an `Experiment` subtype with all three values |
| `defaults.sysml` | `DefaultExperiment` and `Experiment` markers; one exported part and two analyses |
| `multiple.sysml` | Two experiment containers on the same exported part |
| `tolerance.sysml` | Optional `tolerance`: one authored, one absent, one non-positive |

## What this case proves

`read_experiment` reads `startTime` and `stopTime` from either container kind,
requires `stepSize` only for a type specializing `Experiment`, and returns
`Experiment.step_size is None` for a plain `DefaultExperiment`.
`experiment_attribute` accepts one container on an exported part with
`required=False`, still insists on exactly one for an analysis with
`required=True`, and rejects more than one container in either mode.
`read_experiment` reads the optional FMI 2.0 `tolerance`: an authored positive
value is kept, an absent one is `None`, and a non-positive one is rejected.

## Update history

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-19 | Created | The experiment containers moved from name-prefixed attributes to typed definitions |
| 2026-11-19 | Added `tolerance.sysml` | `DefaultExperiment.tolerance` is standard-backed and optional |
