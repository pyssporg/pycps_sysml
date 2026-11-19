# Case: `inheritance-consumers`

Consumer accessors read the effective member view rather than a definition's
own declarations.

## Artifacts

| Path | Kind |
| --- | --- |
| `consumers.sysml` | Input |

No expected artifact: the tests assert the resolved metadata, experiment, and
parameter declarations.

## What this case proves

`DerivedAnalysis`, `DerivedSsp`, `DerivedFmuPart`, and `DerivedSetOwner` each
specialize a base that carries the typed container, so the metadata, role, and
composition accessors must find an inherited `Experiment`, `SspMetadata`,
`FmuMetadata`, or `ParameterSet` usage. `PortOwner.parameters` is typed by
`DerivedParameters :> BaseParameters, ParameterInterface`, so the parameter
declarations expose the ancestor member first and then the derived member.

The port and composition paths are covered too: `InheritedPortOwner` inherits
its `parameters` port from `ParameterPortBase`, `MarkerDerived` reaches
`ParameterInterface` only through `MarkerBase`, `DerivedComposition` inherits
`inherited_child`, and `MappingOwner` maps `InheritedSet` onto the inherited
interface members of its `component`.

`DerivedNestedFmu` inherits both `fmu_meta` and a subpart, so it is a nested
system and cannot be an FMU component. `DerivedModelUsageAnalysis` and
`DerivedVariationAnalysis` inherit their model usage and variation point through
a base analysis. `InheritedPortChoice` connects to a port that
`InheritedParametersComponent` inherits, so the variation resolver must read the
effective ports.

## Update history

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-19 | Created | Evidence that consumer accessors see inherited members. |
| 2026-11-19 | Extended | Cover inherited ports, deep interface markers, subparts, and mapping members. |
| 2026-11-19 | Extended | Cover inherited FMU subparts, analysis model usages and variation points, and body connections to inherited ports. |

## Provenance

Authored here for `tests/test_inherited_consumers.py`.
