# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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

