# pycps_sysml

The SysML dialect layer for our CPS artifacts: it parses SysML v2 into a
repo-owned IR and owns variation, selection, constraints, and every marker and
metadata accessor for the SSP and the FMI dialects.

**Boundary.** This library reads and interprets SysML. It emits no artifact: no
SSD, SSV, SSM, SSP, modelDescription, C header, or FMU. `pyssp_sysml` (SSP
artifacts) and `pyfmi_interfaces` (FMI artifacts) are implementers: both import
`pycps_sysml` for every SysML read and keep no parser, marker set, or IR of
their own. The shared vocabulary ships in `pyssp-sysml-definitions`;
`pycps_sysml` re-exports `core_definitions` and keeps the parser, IR, and
policies. A consumer that needs SysML knowledge installs this package; a
consumer that needs an artifact installs an implementer.

It is not a SysML v2 conformance suite, not a general SysML toolchain, and not a
`pyssp_standard` wrapper. 0.4.0 carries no FMI authoring attributes.

## Install

From the release wheel:

```bash
pip install "pycps-sysml2 @ https://github.com/pyssporg/pycps_sysml/releases/download/v0.4.0/pycps_sysml2-0.4.0-py3-none-any.whl"
```

Runtime dependencies are the exact `sysmlpy==0.96.4` parser pin and
`pyssp-sysml-definitions` for the shared vocabulary; the latter is pinned to
its immutable `v0.1.0` release wheel, not a PyPI name. From a checkout:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

Requires Python 3.11 or newer; CI runs 3.11 and 3.12.

## No CLI

0.4.0 ships no console script. There is no entry point, no
`python -m pycps_sysml`, and nothing installed on `PATH`: the Python API is the
surface.

## Python API

The dialect definitions ship in `pyssp-sysml-definitions` (`package
PysspCore`); `pycps_sysml` re-exports `core_definitions` for the historical
import path. A model imports them with `private import PysspCore::*;`, and
`load` receives that library as an include root. Save this as `plant.sysml`:

```sysml
package Plant {
  private import PysspCore::*;
  part def PlantComposition :> SspModel {
    part ball : Ball;
  }
  part def Ball;
}
```

Load it with the definitions as an include root and read the composition:

```python
from pycps_sysml import core_definitions, load

architecture = load("plant.sysml", core_definitions())
composition = architecture.get_part_def("PlantComposition")
print(composition.parts["ball"].type_name)
```

```text
Ball
```

## Examples

The repo ships runnable worked examples: loading, inheritance, variation and
variant forms, selection and design-space limits, configuration and analysis
plans, the parameter dialect, validation reports, and packages/export. Run one
from a checkout: `python examples/01-load-and-traverse/run.py`.

`tests/test_examples.py` executes each example and compares its stdout with the
documented output. `examples/README.md` is the index.

- `01-load-and-traverse` — `load` with the core include, package and definition lookup, declared members and source files.
- `02-inherit-core-definitions` — specializing `SspModel`/`FmuModel` and reading the inherited metadata slot and experiment.
- `03-variation-and-selection` — variation points, `resolve_selected`, the canonical selection map, `parse_selection`, then constraint statuses and `enforce_constraints`.
- `04-variant-bodies` — typed, body, and usage-level variants, and a nested variation point.
- `05-configuration-and-plans` — `:>>` configuration, `derived_selection`, and analysis plans.
- `06-design-space-limits` — two enumerated design points, a typed cross-point constraint, a pinned configuration, and an incomplete selection refused.
- `07-parameter-dialect` — parameter ports, declarations, applied sets, binds, `mapping_specs`.
- `08-validation-report` — `validate` as one report, `format()`, `ok`, and `raise_for_issues()`, with a broken second model.
- `09-packages-and-export` — qualified names across packages, imports, and an `export_declared()` round trip.

## Multi-root loading and core definitions

`load()` takes one primary model root plus any number of included definition
roots:

```python
architecture = load(["plant.sysml", "shared/vocabulary"], "another/file.sysml")
```

`path` is either one root or a sequence whose first element is the primary
model root; later elements and `*includes` are included roots. A root is a
`.sysml` file or a directory of them. With no includes, `load(primary)` requires
one package name across the primary's files.

An included root merges definitions and may use any package name, because it
supplies vocabulary rather than composition. A definition the model already
declares is a `ValueError` naming the definition, its kind, both sources, and
the local declaration to remove; one name supplied by two included roots is
also an error and names both roots. Merged names are recorded in
`Architecture.included_definitions` and excluded from `export_declared()`.

Inclusion does not make definitions visible: the model still needs
`private import PysspCore::*;`. A `part def` specializing `SspModel` or
`FmuModel` inherits its metadata slot unfilled, which reads as "no metadata".

`core_definitions()` returns the `core.sysml` shipped by
`pyssp-sysml-definitions` (`package PysspCore`): `SspModel`, `Analysis`,
`FmuModel`, `ParameterInterface`, `ParameterSet`, `SourcedMetadata`,
`FmuMetadata`, `SspMetadata`, `DefaultExperiment`, and `Experiment`. It is one
possible include, not a special case. `tests/test_definition_markers.py` is the
drift test: the Python marker constants and the shipped vocabulary must declare
the same names. `DefaultExperiment` is the one deliberate licence: a local
vocabulary may redeclare it, and the reader is permissive.

## Errors and limits

- `load()` raises `FileNotFoundError` for a missing path or an empty directory,
  `sysmlpy`'s `SysMLSyntaxError` for a syntax error, and `ValueError` for a
  package mismatch or a duplicate definition across files.
- Loading does not validate. An unresolved reference surfaces later as a missing
  lookup or a `ValueError` from the consumer that needed it.
- `resolve` and `resolve_selected` raise `ValueError` naming the key, its owner,
  and the paths that are reachable when a selection is unknown, ambiguous, or
  not a variation point.
- `ssp_metadata` and `fmu_metadata` raise `ValueError` for a missing marker
  definition, an unmarked owner, an unknown member, or a non-String value.
- One dialect ships: SSP. There is no `GENERIC_POLICY`; a non-SSP domain passes
  an explicit policy.
- Dialect limits: one `parameters` port per part, tuple-valued list attributes,
  and `metadata`/`comment` reserved as words.
- FMI authoring attributes (guid policy, modelName override, capabilities, units,
  declared causality) are out of scope for 0.4.0; `pyfmi_interfaces` derives them.

## Development

```bash
ruff check src tests examples
python -m pytest -m "not slow"      # the CI gate
python -m pytest                    # includes slow
python -m build                     # wheel and sdist
```

Intent, architecture, and the dialect inventory live in
[`docs/breakdown/`](docs/breakdown/); [`AGENTS.md`](AGENTS.md) states the rules
a change must satisfy.
