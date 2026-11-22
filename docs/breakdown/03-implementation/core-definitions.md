---
id: INFO-012
type: info
title: Core definitions
summary: The dialect markers and metadata schemas ship once as package data; a model loads that file as one include root and never redeclares one.
date: 2026-11-05
status: current
---

# Core definitions

The `core.sysml` shipped by `pyssp-sysml-definitions`
(`src/pyssp_sysml_definitions/core.sysml`) is the single copy of `package
PysspCore`: markers `SspModel`, `Analysis`, `FmuModel`; `ParameterInterface`;
`ParameterSet`; schemas `SourcedMetadata`, `FmuMetadata`, `SspMetadata`; and
`DefaultExperiment` with `Experiment :> DefaultExperiment`. The file ships as
package data of `pyssp-sysml-definitions`; `pycps_sysml2.definitions` is a
compatibility facade re-exporting `core_definitions` and `CORE_FILE`, so the
historical import path and names keep working.

**Include plus import.** `load(model, core_definitions())` supplies the
definitions and `private import PysspCore::*;` supplies visibility; both are
required, and without the import supertypes stay unresolved.

**Inheritance.** A part def specializing `SspModel` or `FmuModel` with `:>`
inherits its members (attributes, ports, subparts, connections, bindings,
constraints) and the unfilled `ssp_meta`/`fmu_meta` slot; the subclass supplies
values and its own members only, and consumers read the ancestor-merged view.

```sysml
package Plant {
  private import PysspCore::*;
  attribute def PlantMetadata :> SspMetadata { attribute source = "models/plant"; }
  part def PlantModel :> SspModel { attribute ssp_meta : PlantMetadata; }
}
```

In Python: `load(path, core_definitions())`.

`SspModel` declares `ssp_meta : SspMetadata`, `FmuModel` declares `fmu_meta :
FmuMetadata`, and `Analysis` stays empty. An inherited slot authored nowhere
reads as "no metadata": the accessor returns `None` and `require_fmu_metadata`
reports "no FMU metadata". A local usage typed by the schema raises "schema
directly"; a same-name concrete usage shadows the slot, and any other name is
accepted. A local `fmu_meta` still requires `:> FmuModel` (INFO-002).

`DefaultExperiment` carries `startTime` and `stopTime`; `Experiment` adds
`stepSize` and `tolerance`, under the experiment split's field and export rules
(INFO-002). A local vocabulary may redeclare all four; the reader stays permissive.

Generated and tooling fields stay out: FMI `fmiVersion`, `modelName`, `guid`, `generationTool`,
`generationDateAndTime`, `variableNamingConvention`, `valueReference`, `numberOfEventIndicators`,
`ModelStructure` indices; SSP `version`, `name`, `fileversion`, `id`, geometry, `GraphicalElements`, `Signature`.

| rule | behavior |
|---|---|
| package data | `pyssp-sysml-definitions` lists `*.sysml`, so its wheel carries `core.sysml`; `core_definitions()` returns a real `Path`, refusing a zipped install |
| drift test | `tests/test_definition_markers.py` asserts that the Python marker constants and the shipped vocabulary declare the same names; `tests/test_core_definitions.py` asserts the real path lives under `pyssp_sysml_definitions` |
| multi-root load | `load(path, *includes)` takes a primary root plus any included roots; `path` may be a sequence whose first element is primary, and `*includes` are included roots; no includes is unchanged |
| primary vs included | every primary file declares the same package; an included root may declare any, supplying definitions rather than composition |
| duplicate rule | only a repeated stored key (same package and name) raises `ValueError`; another package's same bare name coexists. A repeat against a model key names the definition, kind, both sources, and the local declaration to remove, never an override; two included roots repeating a key also raise, naming both roots |
| storage keys | bare name for the primary package (or a synthesized definition), `Pkg::Name` otherwise; `Definition.name` stays bare and every included key lands in `Architecture.included_definitions` |
| export exclusion | `export_declared()` emits only the architecture's own package, so an included root never appears in the model's declaration text |
| implementers | `pyssp_sysml2` exposes the merge as keyword-only `includes` (a sequence of roots), off by default; `--core-definitions` is sugar for one `core_definitions()` include |
