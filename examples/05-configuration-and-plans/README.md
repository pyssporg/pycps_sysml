# Example 05: Configuration and analysis plans

Recovers a selection from a configuration and classifies the analysis plans.

## Run

From the workspace root (`pyssp_dev/`), with the workspace venv active (see
[`examples/README.md`](../README.md#setup)):

```bash
python repos/pycps_sysml2/examples/05-configuration-and-plans/run.py
```

## Expected output

```text
configuration: SineLate
model root: System
derived: {'scenario': 'late', 'source': 'sine'}
parse_selection equal: True
resolved source: Sine
resolved scenario: LateScenario
plan: sine_late legal SineLate
plan: unbound_plan invalid Unbound
canonical sine_late: {'sut.scenario': 'late', 'sut.source': 'sine'}
analysis_selections: ValueError at unbound_plan.scenario: variation point 'ScenarioChoice' at 'scenario' is not selected
invalid detail: variation point 'ScenarioChoice' at 'scenario' is not selected
```

## What the definition encodes

A configuration binds a variant with `:>>`, so the choice is part of the model rather than a call-time argument. `derived_selection` recovers the `{usage: variant}` map from those redefinitions, and `resolve_selected` on the root turns that map back into concrete types. `analysis_plans` classifies each `Analysis` as `legal`, `violated`, or `invalid` instead of raising on the first failure, while `analysis_selections` still stops at that failure. Resolving a configuration itself is guarded: a configuration only redefines the root's usages, so pass the root with the derived selection. The basic selection workflow is example 03, and variant shapes are example 04.
