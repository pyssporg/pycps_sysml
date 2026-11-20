# Example 02: Inherit the core definitions

`part def System :> SspModel;` inherits every member of the core definition, so the model author does not redeclare the `ssp_meta` slot. The subclass supplies values for what the core definition only declares: `Ball` fills the inherited `fmu_meta` slot with `BallFmu`, and `BallExperiment` fills three members of `Experiment`. An inherited slot that nobody fills reads as "no metadata" (`ssp_metadata(...) is None`), not as an error. A subclass can also use `:>>` to redefine an inherited member explicitly instead of supplying it by name.

## Run

```bash
python examples/02-inherit-core-definitions/run.py
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
