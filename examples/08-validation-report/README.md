# Example 08: The validation report

Runs every dialect check as one validation report instead of failing on the first accessor error.

## Run

From the workspace root (`pyssp_dev/`), with the workspace venv active (see
[`examples/README.md`](../README.md#setup)):

```bash
python repos/pycps_sysml/examples/08-validation-report/run.py
```

## Expected output

```text
model.sysml ok: True
PASS role-markers
PASS marker-kinds
PASS retired-control-attributes
PASS specialization
PASS parameter-dialect
PASS fmu-metadata
PASS fmu-marker
broken.sysml ok: False
FAIL fmu-marker: Pump declares fmu_meta but does not specialize FmuModel
raise_for_issues: ValueError: Pump declares fmu_meta but does not specialize FmuModel; author 'part def Pump :> FmuModel'
```

## What the definition encodes

Accessors such as `fmu_metadata` fail fast: the first dialect mistake raises before later checks run. `validate` calls every dialect validator and returns one `ValidationReport`, so `format()` lists every check with `PASS` or `FAIL`, `ok` is one boolean, and `raise_for_issues()` turns the collected failures back into one `ValueError`. Both models are validated against the `System` composition: that enables the `parameter-dialect` check and narrows `fmu-metadata` to the composition's components, whose `fmu_meta` must reach `FmuMetadata`. `model.sysml` passes all seven checks; `broken.sysml` declares `fmu_meta` on `Pump` without specializing `FmuModel`, and the report names exactly that failure.
