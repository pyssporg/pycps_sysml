---
id: INFO-002
type: info
title: Dialect inventory
summary: Every marker, typed attribute container, and variation construct the library owns, and where each lives.
date: 2026-11-05
status: current
---

# Dialect inventory

The dialect is the set of SysML v2 constructs this library gives meaning to.
Anything not listed here is language the IR keeps but no marker interprets.
Field schemas are canonical in `pyssp_sysml_definitions/core.sysml`; this table
maps each construct to the code that recognizes it and the role or disposition
it carries.

| marker or construct | attaches to | role or disposition | code ref |
|---|---|---|---|
| `part def SspModel` | part def | SSP model marker; an inherited unfilled slot authors no metadata | `metadata/roles.py` |
| `part def Analysis` | part def, empty marker | model marker | `metadata/roles.py` |
| `part def FmuModel` | part def | FMI model marker; an inherited unfilled slot authors no metadata | `metadata/roles.py` |
| `attribute def SourcedMetadata` | attribute def | build metadata: family base; reaching it is what makes a typed container build metadata, and no slot records it | `metadata/sourced_metadata.py` |
| `attribute def DefaultExperiment` | attribute def | build metadata: SSP experiment container | `metadata/roles.py` |
| `attribute def Experiment :> DefaultExperiment` | attribute def marker | build metadata: FMI experiment superset | `metadata/roles.py` |
| `attribute def SspMetadata :> SourcedMetadata` | attribute def | build metadata: SSP container | `metadata/ssp_metadata.py` |
| `attribute def FmuMetadata :> SourcedMetadata` | attribute def | build metadata: FMI container; `implementation` validated here against the SSP enum | `metadata/fmu_metadata.py` |
| `port def ParameterInterface` | port def, empty marker | initialization: interface marker | `parameters/dialect/markers.py` |
| `attribute def ParameterSet` | attribute def, empty marker | initialization: set marker | `parameters/dialect/markers.py` |
| `pyssp_*` names | any attribute | migration error naming the typed-container replacement | `core/control.py` |
| `variation part def`, `variation attribute def` | definition | `is_variation` | `model/variation.py` |
| `variant part n : T` or `variant part n { body }` | variation point; body holds parts, connections, binds, named typed attributes, a nested variation point; typed and bodied is refused, as is a third level; unnamed `variant part { ... }` parses but is dropped, bare `variant { ... }` is a syntax error | `variants` | `model/variation.py` |
| `:>> p = T::v` | configuration selection | binding | `parameters/configuration.py` |
| `constraint def`, `assert [not] <expr>` | constraint usage | Boolean expression | `model/parser.py`, `parameters/constraints.py` |

**Role contract.** The vocabulary defines the three roles — build metadata,
initialization configuration, runtime signal — and the carrier that means each:
`pyssp_sysml_definitions` `docs/roles.md` (short contract in `core.sysml`).
This library implements recognition and does not restate the contract.

| role | recognized by | gate |
|---|---|---|
| build metadata | typed attribute whose attribute def reaches `SourcedMetadata` — `FmuMetadata`, `SspMetadata`, or another family container, checked in that order — or an experiment container | `metadata/*`, `fmu-marker` |
| initialization | port def reaching `ParameterInterface` under the reserved usage name `parameters`; attribute def `:> ParameterSet` | `parameter-dialect` (`validate_parameter_port_names`) |
| runtime signal | every other port | `specialization` |

Metadata never becomes a signal, and the dialect has no runtime-tuning marker:
parameters are initialization configuration. A `ParameterInterface` port under
any name but `parameters` is rejected rather than silently skipped by the
exporters.

**Experiment disposition.** `core.sysml` defines both containers and their
fields. Exporters project by disposition: FMI copies every authored field, SSD
only `startTime` and `stopTime`. A local vocabulary may redeclare all four; the
reader stays permissive.

**Ownership boundary.** Implementers select a domain with policy objects, never
by re-declaring markers: `RolePolicy` binds the model, analysis, and FmuModel
markers and predicates, and `metadata/roles.py` owns the experiment recognizers;
`DialectPolicy` adds the metadata recognizers — the FMU and SSP containers and
the generic `SourcedMetadata` family base — and the retired and flat-connector
rejections. `core/control.py` holds one retired-tag map and the residual
`pyssp_*` catch-all, migration vocabulary not a domain policy. Marker names stay
exported as defaults; another domain constructs its policy (INFO-003).

**Validation.** Validators stay fail-fast and collect each `ValueError` under a
stable code: `role-markers`, `marker-kinds`, `retired-control-attributes`,
`parameter-dialect` (with a composition root), `specialization` (cyclic,
incompatible redefinition, usage-kind mismatch), `fmu-metadata` (rejects an
`implementation` outside `any|ModelExchange|CoSimulation|ScheduledExecution`),
`fmu-marker` (a local `fmu_meta` requires `:> FmuModel`), and nothing for an
undefined supertype or definition-kind mismatch, because the pinned analyzer
emits no code. `require_fmu_metadata` returns problems instead of raising.

**Core vocabulary.** The markers and schemas ship in
`pyssp-sysml-definitions` as `core.sysml`; `pycps_sysml2` re-exports
`core_definitions` from its `definitions/` facade. `load(model,
core_definitions())` supplies the definitions, `private import PysspCore::*;`
supplies visibility, and Core definitions (INFO-012) holds the canonical
snippet. The marker/constant drift test is `tests/test_definition_markers.py`.
