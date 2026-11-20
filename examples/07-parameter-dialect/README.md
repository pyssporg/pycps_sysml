# Example 07: Parameter dialect

A parameter port is a typed `ParameterInterface`: `ControllerParams` declares the scalars that `Controller` exposes through its fixed-name `parameters` port. A parameter set is an attribute def marked `:> ParameterSet`, applied to a component usage with `bind` at the composition root. A bind is oriented by role, with the parameter port on the left and the set usage on the right (`bind controller.parameters.kp = nominal.kp_value;`); the reversed form is rejected. `mapping_specs` turns each applied set into the `(set member, component member)` entries that an implementer consumes.

## Run

```bash
python examples/07-parameter-dialect/run.py
```

## Expected output

```text
declarations: enable Boolean, ki Real, kp Real
applied sets: controller NominalGains usage=nominal identity=False
bind: parameter=controller.parameters.kp target=nominal.kp_value (parameter port left, set usage right)
mapping: component=controller set=NominalGains member=kp_value target=controller.kp
```
