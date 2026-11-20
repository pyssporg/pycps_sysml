# Example 06: Limiting the design space

The design space is the product of the variation points, so two points with two variants each give four complete assignments. One constraint definition carries typed parameters and a combined cross-point restriction: `sine implies single` and `step implies two`, so only the two diagonal pairs survive. The driver enumerates the product in declaration order, resolves each complete assignment, and lets `evaluate` report per-assignment status as `legal` or the failed constraint. A pure selection pins a point structurally: `StepTwoSystem :> System` redefines `source` and `gain` with `:>>`, and the inherited constraint evaluates legal on that configuration. A constraint cannot stand in for a binding: with only `source` bound, `evaluate` marks it `invalid` (`no selection for 'gain' bound to 'chosenGain'`) instead of inferring the variant the implication allows, which is why the configuration binds both points. Pin points on a derived definition, not in a body on a plain part usage, and note that deriving a selection map from a configuration needs an `Analysis` (example 05). A selection must be complete, so leaving a point open is refused instead of exported with an unresolved type.

## Run

```bash
python examples/06-design-space-limits/run.py
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
pinned: StepTwoSystem source=SourceChoice::step gain=GainChoice::two
pinned evaluation: legal
unbound: sourceDeterminesGain invalid no selection for 'gain' bound to 'chosenGain'
partial: ValueError: Variation point 'GainChoice' at 'gain' in composition 'System' is not selected; pass gain=<variant>.
```
