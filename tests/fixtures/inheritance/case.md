# Case: `inheritance`

Effective-member inheritance over the repo-owned definition graph.

## Artifacts

| Path | Kind |
| --- | --- |
| `fmu-interop.sysml` | Input |
| `edges.sysml` | Input |

No expected artifact: the tests assert the effective view and the captured
redefinition fields.

## What this case proves

`fmu-interop.sysml` reproduces the consumer shape: `ActuatorLink :> FmuInterop`
inherits the `interop_metadata` attribute and exposes its own `command` and
`feedback` ports, while `FmuInterop` inherits the empty `FmuModel` marker.

`edges.sysml` isolates the merge rules: an inherited part, boundary connection,
binding, and constraint; a named override that keeps its ancestor position; a
four-node diamond that is not pruned; a cycle that terminates; an unknown
supertype that is skipped; `PortDefinition :> PortDefinition` and
`AttributeDefinition :> AttributeDefinition` inheritance; and a port
redefinition (`out port :>> y`) that records `redefines`.

## Update history

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-19 | Created | Evidence for the generic effective-member view and port redefinition capture. |

## Provenance

Authored here for `tests/test_inheritance.py`; the `fmu-interop.sysml` shape is
the user's requested `part def ActuatorLink :> FmuInterop` composition.
