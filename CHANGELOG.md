# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `SourcedMetadata` as the shared core base for containers that name an
  external artifact; `FmuMetadata` and `SspMetadata` inherit `source` from it.
- The optional FMI 2.0 `DefaultExperiment.tolerance`; `read_experiment` reads it
  from the effective-member view and rejects a non-positive value.

### Changed

- `EXPERIMENT_FIELDS` and `Experiment` carry `tolerance`, `None` when not
  authored; no default value is assumed.

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

- `DefaultExperiment` core attribute definition and `Experiment :>
  DefaultExperiment`; `experiment_attribute`/`read_experiment` take a required
  keyword, step size is mandatory only for `Experiment`, and
  `Experiment.step_size` may be `None`.
- `classify_attribute` and `AttributeKind` as the one classification point for
  FMU metadata, SSP metadata, parameter sets, experiments, and plain typed or
  untyped attributes.

### Changed

- `validate(architecture, composition=None, *, roles=SSP_ROLES, policy=SSP_POLICY)`
  runs every applicable dialect validator as one `ValidationReport` with stable
  check codes, instead of stopping at the first `ValueError`.
- `require_fmu_metadata(architecture, part_defs, *, implementation=None)`
  returns the missing or mismatched FMU metadata of leaf part definitions as
  messages, without raising.

## [0.2.0] - 2026-11-09

### Added

- `FmuModel` marker for export units carrying optional FMU metadata.
- Package-scoped definitions: every root is loaded in one parse and included
  definition roots are merged; the dialect core definitions ship with the package.
- Configurable `base_index` on parameter items and mappings.

### Changed

- Cross-package visibility is gated behind imports.
- Harden the ecosystem CI workflows and seed the `CHANGELOG.md`.

