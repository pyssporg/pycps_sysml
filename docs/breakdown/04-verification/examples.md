---
id: TEST-003
type: test
title: Examples
summary: What the runnable examples tree is for, its three-file layout, the README stdout oracle, and why it ships in no package.
date: 2026-11-20
status: current
---

# Examples

**Purpose.** `examples/` teaches a workflow: a reader follows the public API
from a small SysML input to a printed result without reading the test suite.

**Layout.** Every example carries three required files: `model.sysml`, the
input, small enough for one screen; `run.py`, the driver that resolves its model
from `__file__` and prints one block; and `README.md`, which explains the
example and carries the expected output. A second input file is allowed when
the example needs one (a broken model, an included package).
`examples/README.md` indexes every directory.

**The oracle.** Each `README.md` holds exactly one ```` ```text ```` fence, the
expected stdout. `tests/test_examples.py` runs each `run.py` in a subprocess
with `cwd=tmp_path` and `PYTHONPATH=<repo>/src`, then compares stdout to the
fence after stripping the trailing newline. It also fails a directory missing
one of its three files or absent from the index. Its level is `system`: the
public API is driven as a consumer would drive it.

**The guard.** `examples` is a guarded root in `tests/conftest.py`, beside
`tests/fixtures`: the session hashes it at start and finish, so an example that
rewrites its own README fails the session. An example never writes into the
repository; a needed file goes under `tempfile` in the temporary cwd.

**Repo-only packaging.** `packages.find` selects `src` only, so the wheel omits
`examples/`, and `MANIFEST.in` says `prune examples`, so the sdist omits it too.
A reader gets the examples from the checkout, never an installed package.

**No artifact, deterministic output.** The library reads SysML and emits no
artifact; examples print only, never an `.ssd`, `.ssv`, `.ssm`, `.ssp`, or
`.fmu`. No absolute paths, no timestamps, every printed set sorted; a changed
output updates the README fence in the same change.

**Current examples.** `01-load-and-traverse` loads a model and walks packages,
definitions, declared members, and source files. `02-inherit-core-definitions`
specializes `SspModel`/`FmuModel` and reads inherited metadata and experiment.
`03-variation-and-selection` shows variation points, `resolve_selected`, the
canonical map, `parse_selection`, then constraint statuses and
`enforce_constraints`. `04-variant-bodies` contrasts typed, body, and
usage-level variants with a nested variation point.
`05-configuration-and-plans` covers `:>>` configuration, `derived_selection`,
and analysis plans. `06-design-space-limits` enumerates two design points and
shows a typed cross-point constraint limiting the combinations; configurations
pinning only `source` derive `gain` from the constraint, the unconstrained root
is refused as ambiguous, and a fully pinned illegal pair is left for the plan
to report. `07-parameter-dialect`
covers parameter ports, sets, bind orientation, and `mapping_specs`. `08-validation-report`
turns `validate` into one report with `format()`, `ok`, and `raise_for_issues()`.
`09-packages-and-export` follows qualified names across packages, imports, and
the `export_declared()` round trip.
