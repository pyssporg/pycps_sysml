# Case: `interop-definitions`

Input for `tests/test_interop_definitions.py`: a component that uses the shipped
`PyfmiInterop` vocabulary as an include root instead of copying it.

## Artifacts

| Path | Kind |
| --- | --- |
| `link.sysml` | Input, a `FmuInterop` subtype with one runtime signal port |

`link.sysml` imports both shipped packages and never declares `FmuInterop`,
`InteropDeployment`, `InteropMetadata`, or any `PysspCore` definition. The
`parameters` port and its `InteropDeployment` type are inherited from the
shipped `FmuInterop`; the only authored port is the runtime signal.

## What this case proves

The interop vocabulary is usable exactly as shipped: `include_roots()` supplies
`PysspCore` first and `PyfmiInterop` second, `InteropDeployment` reads as a
parameter interface under the reserved usage name `parameters`, and the
inherited port is found by the parameter accessors. `InteropMetadata` stays a
family container, outside the FMI metadata slot, and the deployment attributes
never appear as runtime signal ports.

## Update history

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-23 | Created | The shipped `PyfmiInterop` vocabulary had no consumer coverage in this repository |

## Provenance

Authored here for `tests/test_interop_definitions.py`.
