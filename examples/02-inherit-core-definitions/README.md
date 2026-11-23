# Example 02: Inherit the core definitions

Shows what specializing `SspModel`, `FmuModel`, and `Analysis` gives a model: inherited slots, filled metadata, and unfilled experiment members.

## Run

From the workspace root (`pyssp_dev/`), with the workspace venv active (see
[`examples/README.md`](../README.md#setup)):

```bash
python repos/pycps_sysml2/examples/02-inherit-core-definitions/run.py
```

## Expected output

```text
System specializes: ('SspModel',)
Ball specializes: ('FmuModel',)
Simulation specializes: ('Analysis',)
System ssp_meta type: SspMetadata
System ssp_metadata: None
System declares ssp_meta locally: False
Ball source: 'build/fmus/Ball.fmu'
Ball implementation: 'CoSimulation'
Experiment name: 'experiment'
Experiment start_time: 0.0
Experiment stop_time: 5.0
Experiment step_size: 0.01
Experiment tolerance: None
```

## What the definition encodes

`part def System :> SspModel;` inherits the `ssp_meta` slot from the core definition rather than declaring it locally. The subclass supplies values for what the core definition only declares: `Ball` fills the inherited `fmu_meta` slot with `BallFmu`, and `BallExperiment` fills three members of `Experiment`. An inherited slot that nobody fills reads as "no metadata" (`ssp_metadata(...) is None`), not as an error. A subclass can also use `:>>` to redefine an inherited member explicitly instead of supplying it by name.
