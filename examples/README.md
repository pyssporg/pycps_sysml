# Examples

Runnable worked examples for the public API. They are repo-only: neither the
wheel nor the sdist carries this tree, so read them here, not from an installed
package.

## Setup

The examples run from the **workspace root** (`pyssp_dev/`) against the one
workspace venv, where every repo is already installed editable:

```bash
python -m venv .venv-experimental
source .venv-experimental/bin/activate
pip install --upgrade pip
pip install --no-deps -r requirements-experimental.txt
pip install -r requirements-thirdparty.txt
```

`requirements-experimental.txt` already installs `pycps_sysml` and
`pyssp_sysml_definitions` editable; `sysmlpy` comes from
`requirements-thirdparty.txt`.

## Run

```bash
python repos/pycps_sysml/examples/01-load-and-traverse/run.py
```

`tests/test_examples.py` runs every `run.py` in a subprocess and compares stdout
to the README fence, so a documented example cannot drift from the API. If an
example's output changes on purpose, update its README in the same change.

## Layout

Every example is a directory with the same three required files (a second input
file is allowed where one is needed, such as `broken.sysml` in
`08-validation-report` or `vocabulary.sysml` in `09-packages-and-export`):

| File | Role |
| --- | --- |
| `model.sysml` | the SysML input, kept small enough to read in one screen |
| `run.py` | the Python driver; prints one deterministic block |
| `README.md` | what the example shows, and the exact expected stdout in one ```` ```text ```` fence |

## Index

| Example | Shows |
| --- | --- |
| `01-load-and-traverse` | `load` with the core include, package and definition lookup, declared members, source files |
| `02-inherit-core-definitions` | specializing `SspModel`/`FmuModel` and reading the inherited metadata slot and experiment |
| `03-variation-and-selection` | variation points, `resolve_selected`, the canonical selection map, `parse_selection`, `evaluate`, and `enforce_constraints` |
| `04-variant-bodies` | typed, body, and usage-level variants, and a nested variation point |
| `05-configuration-and-plans` | `:>>` configuration, `derived_selection`, and analysis plans |
| `06-design-space-limits` | two enumerated design points, a typed cross-point constraint, a pinned configuration (`:>>`), and an incomplete selection refused |
| `07-parameter-dialect` | parameter ports, declarations, applied sets, binds, `mapping_specs` |
| `08-validation-report` | `validate` as one report, `format()`, `ok`, and `raise_for_issues()`, with a broken second model |
| `09-packages-and-export` | qualified names across packages, imports, and `export_declared()` round trip |

## Vocabulary

Every model imports the shared vocabulary with `private import PysspCore::*;`,
and every driver passes `core_definitions()` as the include root, so no example
copies a shipped `.sysml` file or redeclares a core definition. The role
contract behind those definitions — build metadata, initialization
configuration, runtime signal, and the reserved names — is stated once in
`pyssp_sysml_definitions` (`src/pyssp_sysml_definitions/core.sysml` and
`docs/roles.md`); the examples use it and do not restate it.

## Conventions

- The driver resolves its model from `__file__`, never from the current
  directory, because the test runs it from a temporary cwd.
- The driver prints only what the README documents; absolute paths are
  normalized to a name so the output is stable across machines.
- An example that needs to write a file writes under `tempfile`, never into the
  repository. No example emits an artifact: this library reads SysML only.
