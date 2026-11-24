# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-11-24

### Added

- The repo-only `examples/` tree: nine runnable examples, one directory per
  task with `model.sysml`, `run.py`, and a `README.md` whose `text` fence is
  the expected stdout. `tests/test_examples.py` executes every `run.py` from a
  temporary cwd.
- `derived_selection` infers an unbound variation point from the family's
  asserted constraints when exactly one completion is valid; zero or several
  valid completions is still an error.
- Build-metadata recognition for the `SourcedMetadata` family: a container that
  specializes `SourcedMetadata` but neither `FmuMetadata` nor `SspMetadata`
  (for example `InteropMetadata`) classifies as build metadata, after the
  reserved FMU and SSP slots.
- Exported text declares `private import PysspCore::*;` in a file that refers
  to a shipped name, and no longer emits a synthesized copy of the vocabulary
  definitions.
- Drift guards binding the marker constants and the exporter's shipped-name set
  to the `core.sysml` and `interop.sysml` shipped by
  `pyssp-sysml-definitions`.

### Changed

- Rename the distribution and import package from `pycps_sysml2` to
  `pycps_sysml`; `pyproject.toml` `[project].name`, docs, fixtures, and
  examples follow, as do links to the renamed upstream repositories.
- Depend on `pyssp-sysml-definitions>=0.1.0`; the `PysspCore` vocabulary now
  ships in that package, and `definitions/core.sysml` is no longer bundled
  here. `core_definitions()` and `CORE_FILE` stay as re-exports.
- Pin the new dependency as a plain specifier because no release asset exists
  yet. Release order: `pyssp-sysml-definitions` 0.1.0 first, then
  `pycps_sysml` 0.4.0.
- Fixtures and examples consume `PysspCore` from the shared package instead of
  redeclaring its markers.

### Fixed

- Parameter composition ignores the inherited unfilled `fmu_meta` schema slot
  of an `FmuModel`, so a nested part is not counted as authoring metadata; an
  authored `fmu_meta` on a non-FMU part is still rejected.
- Reject a `ParameterInterface` port declared under a name other than
  `parameters`, which the FMI and SSP emitters would otherwise skip silently.

## [0.3.0] - 2026-11-19

### Removed

- The `pyssp_*` attribute vocabulary: `CONTROL_PREFIX`, `ControlAttributes`,
  `pyssp_default_start_time`, `pyssp_default_stop_time`,
  `pyssp_flat_connector`, and the control-name skips in the parameter dialect.
  Every remaining `pyssp_*` name is a migration error naming the typed
  container to use instead.
- The flat-connector rejection of a port-def attribute; pass
  `--flat-connector` at export time.

### Added

- The repo-only `examples/` tree: runnable worked examples, one directory per
  task with `model.sysml`, `run.py`, and a `README.md` whose single `text` fence
  is the expected stdout. `tests/test_examples.py` executes every `run.py` from
  a temporary cwd and fails a stale README.
- Part-definition inheritance: `PartDefinition`, `PortDefinition`, and
  `AttributeDefinition` carry `specializes`, and `model/effective.py` resolves
  ancestors on demand, so inherited parts, ports, attributes, connections, and
  bindings appear in the effective view while the IR stores only declared
  members. A same-name redefinition keeps the inherited position.
- `model/semantics.py` specialization checks (`unknown-supertype`, `cycle`,
  `kind-mismatch`, `usage-kind-mismatch`), opted into with
  `analyze_semantics=True`.
- `DefaultExperiment` core attribute definition and `Experiment :>
  DefaultExperiment`; `experiment_attribute`/`read_experiment` take a required
  keyword, step size is mandatory only for `Experiment`, and
  `Experiment.step_size` may be `None`.
- The optional FMI 2.0 `DefaultExperiment.tolerance`; `read_experiment` reads it
  from the effective-member view and rejects a non-positive value.
- `classify_attribute` and `AttributeKind` as the one classification point for
  FMU metadata, SSP metadata, parameter sets, experiments, and plain typed or
  untyped attributes.
- `SourcedMetadata` as the shared core base for containers that name an
  external artifact; `FmuMetadata` and `SspMetadata` inherit `source` from it.
- The `fmu-marker` validation check: a part definition that locally declares
  `fmu_meta` must specialize `FmuModel`; the inherited unfilled core slot is
  not a local declaration.

### Changed

- `validate(architecture, composition=None, *, roles=SSP_ROLES, policy=SSP_POLICY)`
  runs every applicable dialect validator as one `ValidationReport` with stable
  check codes, instead of stopping at the first `ValueError`.
- `require_fmu_metadata(architecture, part_defs, *, implementation=None)`
  returns the missing or mismatched FMU metadata of leaf part definitions as
  messages, without raising.
- `EXPERIMENT_FIELDS` and `Experiment` carry `tolerance`, `None` when not
  authored; no default value is assumed.

## [0.2.0] - 2026-11-09

### Added

- `FmuModel` marker for export units carrying optional FMU metadata.
- Package-scoped definitions: every root is loaded in one parse and included
  definition roots are merged; the dialect core definitions ship with the package.
- Configurable `base_index` on parameter items and mappings.

### Changed

- Cross-package visibility is gated behind imports.
- Harden the ecosystem CI workflows and seed the `CHANGELOG.md`.

