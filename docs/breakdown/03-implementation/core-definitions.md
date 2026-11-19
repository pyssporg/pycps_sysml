---
id: INFO-012
type: info
title: Core definitions
summary: The dialect markers and metadata schemas ship once as package data; a model loads that file as one include root and never redeclares one.
date: 2026-11-05
status: current
---

# Core definitions

`src/pycps_sysml2/definitions/core.sysml` is the single copy of the shared
vocabulary (`package PysspCore`): `SspModel`, `Analysis`, `FmuModel`,
`ParameterInterface`, `ParameterSet`, `SourcedMetadata`, `FmuMetadata`,
`SspMetadata`, `DefaultExperiment`, and `Experiment` (`:> DefaultExperiment`).
`FmuMetadata` and `SspMetadata` inherit `source` from `SourcedMetadata`.
`SspModel` declares `attribute ssp_meta : SspMetadata;` and `FmuModel` declares
`attribute fmu_meta : FmuMetadata;`; `Analysis` stays empty. A model that
specializes a marker and authors no metadata inherits that slot unfilled, which
reads as "no metadata": both `_metadata_usage` helpers skip it, so the accessor
returns `None` and `require_fmu_metadata` reports "no FMU metadata". A locally
declared usage typed by the schema itself still raises "schema directly", a
same-name concrete usage shadows the slot, and any other concrete name is
accepted. No new core key carries this: the slots reuse the two schemas already
in the package.
`FmuMetadata` carries `implementation : String`, validated against the closed SSP
set `any`, `ModelExchange`, `CoSimulation`, `ScheduledExecution`.
`DefaultExperiment` mirrors `ssd:DefaultExperiment` and carries `startTime` and
`stopTime`; `Experiment` specializes it and adds the FMI
`fmi2:DefaultExperiment` fields `stepSize` and `tolerance`. `startTime` and
`stopTime` are required and numeric; `stepSize` and `tolerance` are optional,
positive when authored, and author no numeric default, so an unset value stays
unset. Exporters project by
disposition: the FMI model-description exporter copies every authored field,
while the SSD exporter copies only `startTime` and `stopTime` and intentionally
drops `stepSize` and `tolerance`. A local vocabulary may redeclare its own
`DefaultExperiment` with all four fields; the reader stays permissive.

Generated and tooling fields stay out of the vocabulary: on the FMI side
`fmiVersion`, `modelName`, `guid`, `generationTool`, `generationDateAndTime`,
`variableNamingConvention`, `valueReference`, `numberOfEventIndicators`, and
the `ModelStructure` indices; on the SSP side `version`, `name`, `fileversion`,
`id`, geometry, `GraphicalElements`, and `Signature`.

- **Package data:** `pyproject.toml` lists `definitions/*.sysml`, so the wheel
  carries the file; `core_definitions()` returns it as a real `Path` and
  refuses a zipped install.
- **Multi-root load:** `load(path, *includes)` takes one primary model root and
  any number of included definition roots. `path` is one root or a sequence
  whose first element is the primary; further elements and `*includes` are
  included roots. With no includes, `load(primary)` behaves exactly as before.
- **Primary vs included:** every primary file must declare the same package;
  an included root may declare any package, because it supplies definitions
  rather than composition.
- **Duplicate rule:** only a repeated *stored key* (same package and same name)
  raises `ValueError`; a definition of the same bare name in a different package
  is a distinct definition and coexists. An included definition that repeats a
  key the model declares raises naming the definition, its kind, both sources,
  and the local declaration to remove; never an override. The same key supplied
  by two included roots is also an error and names both roots.
- **Storage keys:** a definition of the primary package (or a synthesized one)
  is keyed by its bare name; one from any other package is keyed
  `Pkg::Name`. `Definition.name` stays bare, so no qualifier reaches an
  artifact surface. Every included key lands in
  `Architecture.included_definitions`.
- **Visibility:** including a root is not enough to reach its definitions. The
  model must `private import <package>::*;` (or import specific members);
  `Architecture.imports` records what is visible and gates resolution.
- **Export exclusion:** `export_declared()` emits only the definitions of the
  architecture's own package, so an included root never appears in the model's
  declaration text.
- **Implementers:** `pyssp_sysml2` exposes the same merge as keyword-only
  `includes` (a sequence of roots), off by default; its `--core-definitions`
  flag is sugar for one `core_definitions()` include.
