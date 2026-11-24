# Example 07: Parameter dialect

Shows parameter ports, applied sets, bind orientation, and mapping specs.

## Run

From the workspace root (`pyssp_dev/`), with the workspace venv active (see
[`examples/README.md`](../README.md#setup)):

```bash
python repos/pycps_sysml/examples/07-parameter-dialect/run.py
```

## Expected output

```text
declarations: enable Boolean, ki Real, kp Real
applied sets: controller NominalGains usage=nominal identity=False
bind: parameter=controller.parameters.kp target=nominal.kp_value (parameter port left, set usage right)
mapping: component=controller set=NominalGains member=kp_value target=controller.kp
```

## What the definition encodes

The model carries initialization configuration in the two carriers the shared vocabulary defines (see `pyssp_sysml_definitions` `docs/roles.md`): `ControllerParams` declares the scalars that `Controller` exposes through its reserved `parameters` port, and `NominalGains` is the set applied with `bind` at the composition root. The bind is port-first, with the parameter port on the left and the set usage on the right (`bind controller.parameters.kp = nominal.kp_value;`); the reversed form is rejected. `mapping_specs` turns each applied set into the `(set member, component member)` entries that an implementer consumes.
