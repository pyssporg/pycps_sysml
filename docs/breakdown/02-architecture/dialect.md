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
| `variant part n : T` or `variant { body }` | variation point | `variants` | `model/variation.py` |
| `:>> p = T::v` | configuration selection | binding | `parameters/configuration.py` |
| `constraint def`, `assert [not] <expr>` | constraint usage | Boolean expression | `model/parser.py`, `parameters/constraints.py` |

**Experiment split.** `DefaultExperiment` mirrors `ssd:DefaultExperiment`
(`startTime`, `stopTime`; seconds, informational in the XSD); `Experiment`
specializes it and adds the `fmi2:DefaultExperiment` fields `stepSize` and
`tolerance`. `startTime` and `stopTime` are required and numeric; `stepSize`
and `tolerance` are optional, positive when authored, and no field authors a
numeric default. Exporters project by disposition: the FMI model-description
exporter copies every authored field, while the SSD exporter copies only
`startTime` and `stopTime`, so `stepSize` and `tolerance` are intentionally
dropped from `.ssd`. A local vocabulary may redeclare its own
`DefaultExperiment` with all four fields; the reader stays permissive.

**Ownership boundary.** An implementing library selects a domain by passing
policy objects, not by re-declaring markers: `RolePolicy` binds the model,
analysis, and FmuModel markers and their predicates, and `metadata/roles.py`
also owns the experiment recognizers. `DialectPolicy` adds those recognizers
plus the metadata recognizers and the retired and flat-connector rejections.
`core/control.py` holds one retired-tag map and the residual `pyssp_*`
catch-all; it is migration vocabulary, not a domain policy. Marker names stay
exported as defaults (`SSP_MODEL_MARKER`, `ANALYSIS_MARKER`,
`FMU_MODEL_MARKER`, the `Parameter*` names), so a caller that wants the default
writes nothing; a caller that wants another domain constructs the policy
(INFO-003).

**Validation.** The dialect validators stay fail-fast, because a generator has
nothing to emit after the first bad marker. `pycps_sysml2.validation.validate`
calls each one in turn and collects the `ValueError` under a stable check code:
`role-markers`, `marker-kinds`, `retired-control-attributes`,
`parameter-dialect` (when a composition root is given), `specialization`
(cyclic specialization, incompatible redefinition, usage-kind mismatch
collected by `analyze_semantics`), and `fmu-metadata` (which also rejects an
`implementation` outside the closed SSP set
`any|ModelExchange|CoSimulation|ScheduledExecution`). An undefined supertype
and a definition-kind mismatch are not reported, because the pinned analyzer
emits no code for them.
`require_fmu_metadata` is the one FMU assertion that returns its problems
instead of raising, so a report can name every leaf component at once.

**Core vocabulary.** The markers and metadata schemas in the table ship in
one packaged file, `definitions/core.sysml`; a model loads it as one included
root with `load(model, core_definitions())` instead of declaring the names
itself (INFO-012).
