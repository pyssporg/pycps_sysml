# Case: `design-space`

Input document for inferring unbound variation points from asserted constraints.

## Artifacts

| Path | Kind |
| --- | --- |
| `design-space.sysml` | Input |

No expected artifact: the tests assert the completed selections and the
ambiguous/contradictory rejections.

## What this case proves

`System` owns `source` and `gain` and asserts `SourceDeterminesGain`: `sine`
requires `single`, `step` requires `two`, and `blocked` is forbidden.

- `StepSystem` pins only `source=step`, so exactly one completion is valid and
  `gain=two` is derived;
- `SineSystem` pins only `source=sine`, so `gain=single` is derived;
- `UnconstrainedSystem` has both points open and no asserted constraint, so
  every completion stays valid and the refusal names the ambiguity;
- `ContradictorySystem` pins the forbidden `blocked` source, so no completion
  is valid and the refusal names that too;
- `PinnedIllegalSystem` binds the illegal `sine+two` pair explicitly, so
  derivation returns the selection without evaluating constraints; the analysis
  plan is the layer that reports it `violated`.

## Update history

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-20 | Created | Cover constraint-aware inference and its two failure shapes. |
