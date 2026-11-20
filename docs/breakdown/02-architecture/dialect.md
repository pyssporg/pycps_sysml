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

| marker or construct | attaches to | value | code ref |
|---|---|---|---|
| `part def SspModel` | part def; declares `ssp_meta : SspMetadata` | marker; an inherited unfilled slot authors no metadata | `metadata/roles.py`, `definitions/core.sysml` |
| `part def Analysis` | part def, empty marker | marker | `metadata/roles.py` |
| `part def FmuModel` | part def; declares `fmu_meta : FmuMetadata` | marker; an inherited unfilled slot authors no metadata | `metadata/roles.py`, `definitions/core.sysml` |
| `attribute def SourcedMetadata` | attribute def | `source` String; shared base for artifact sources | `definitions/core.sysml` |
| `attribute def DefaultExperiment` | attribute def | `startTime`, `stopTime` Real; the SSP disposition | `metadata/roles.py`, `definitions/core.sysml` |
| `attribute def Experiment :> DefaultExperiment` | attribute def marker | adds `stepSize`, `tolerance` Real; the FMI disposition | `metadata/roles.py`, `definitions/core.sysml` |
| `attribute def SspMetadata :> SourcedMetadata` | attribute def | `source` inherited | `metadata/ssp_metadata.py` |
| `attribute def FmuMetadata :> SourcedMetadata` | attribute def | `source` inherited, `implementation` String validated against the SSP enum | `metadata/fmu_metadata.py` |
| `port def ParameterInterface` | port def, empty marker | marker | `parameters/dialect/markers.py` |
| `attribute def ParameterSet` | attribute def, empty marker | marker | `parameters/dialect/markers.py` |
| `pyssp_*` names | any attribute | migration error naming the typed-container replacement | `core/control.py` |
| `variation part def`, `variation attribute def` | definition | `is_variation` | `model/variation.py` |
| `variant part n : T` or `variant part n { body }` | variation point; body holds parts, connections, binds, named typed attributes, a nested variation point; typed and bodied is refused, as is a third level; unnamed `variant part { ... }` parses but is dropped, bare `variant { ... }` is a syntax error | `variants` | `model/variation.py` |
| `:>> p = T::v` | configuration selection | binding | `parameters/configuration.py` |
| `constraint def`, `assert [not] <expr>` | constraint usage | Boolean expression | `model/parser.py`, `parameters/constraints.py` |

**Experiment split.** `DefaultExperiment` mirrors `ssd:DefaultExperiment`
(`startTime`, `stopTime`, required, numeric, seconds, informational in the XSD);
`Experiment` adds the FMI `stepSize` and `tolerance` (optional, positive, no
numeric default). Exporters project by disposition: FMI copies every authored
field, SSD only `startTime` and `stopTime`. A local vocabulary may redeclare all
four; the reader stays permissive.

**Ownership boundary.** Implementers select a domain with policy objects, never
by re-declaring markers: `RolePolicy` binds the model, analysis, and FmuModel
markers and predicates, and `metadata/roles.py` owns the experiment recognizers;
`DialectPolicy` adds the metadata recognizers and retired and flat-connector
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

**Core vocabulary.** The markers and schemas ship in one packaged
`definitions/core.sysml`: `load(model, core_definitions())` supplies the
definitions, `private import PysspCore::*;` supplies visibility, and Core
definitions (INFO-012) holds the canonical snippet.
