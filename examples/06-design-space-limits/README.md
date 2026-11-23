# Example 06: Limiting the design space

Enumerates the design space of two variation points and derives the completions a partial configuration allows.

## Run

From the workspace root (`pyssp_dev/`), with the workspace venv active (see
[`examples/README.md`](../README.md#setup)):

```bash
python repos/pycps_sysml2/examples/06-design-space-limits/run.py
```

## Expected output

```text
space: source 2 x gain 2 = 4 assignments
source=step gain=single: violated sourceDeterminesGain
source=step gain=two: legal -
source=sine gain=single: legal -
source=sine gain=two: violated sourceDeterminesGain
legal: 2 of 4
allowed: step+two, sine+single
derived: StepSystem source=step gain=two (legal)
derived: SineSystem source=sine gain=single (legal)
ambiguous: ValueError: variation point 'SourceChoice' at 'source' is not selected; bind it in configuration 'System'; 2 assignments satisfy the asserted constraints in configuration 'System'
```

## What the definition encodes

The design space is the product of the variation points, so two points with two variants each give four complete assignments. One constraint definition carries typed parameters and a combined cross-point restriction: `sine implies single` and `step implies two`, so only the two diagonal pairs survive. The driver enumerates the product in declaration order, resolves each complete assignment, and lets `evaluate` report per-assignment status as `legal` or the failed constraint. A configuration need not pin every point: `StepSystem :> System` redefines only `source`, and derivation infers `gain` from the family's asserted constraint when exactly one completion is valid; `SineSystem` does the same for the other diagonal. A configuration that leaves several completions valid, such as composing the root `System` itself, is refused as ambiguous rather than choosing arbitrarily. Pin points on a derived definition, not in a body on a plain part usage, and note that deriving a selection map from a configuration needs an `Analysis` (example 05). A fully pinned illegal pair is still returned by derivation and reported `violated` by the analysis plan.
