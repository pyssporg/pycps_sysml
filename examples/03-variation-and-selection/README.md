# Example 03: Variation, selection, and constraints

Selects a variation point, then evaluates the constraint that guards it.

## Run

From the workspace root (`pyssp_dev/`), with the workspace venv active (see
[`examples/README.md`](../README.md#setup)):

```bash
python repos/pycps_sysml2/examples/03-variation-and-selection/run.py
```

## Expected output

```text
before selection: MassChoice
canonical: {'mass': 'light'}
resolved mass: LightMass
original mass: MassChoice
parse_selection: {'mass': 'light'}
selection light: massIsLight pass
selection heavy: massIsLight fail
enforce: ConstraintViolation: massIsLight
```

## What the definition encodes

A variation point is a declaration, not a choice: `System.mass` stays typed `MassChoice` until a selection names one of its variants. `parse_selection` turns the `key=variant;...` text into a map, and `resolve_selected` returns a deep copy with each selected type applied plus the canonical sorted selection map, leaving the original architecture unchanged. After selection, `evaluate` runs every asserted constraint and reports `pass`, `fail`, `invalid`, or `unasserted`, with usages collected root-first and a derived usage replacing an ancestor of the same name. Here `massIsLight` binds `chosen` to `mass`, so it passes for `mass=light` and fails for `mass=heavy`. `enforce_constraints` is the fail-fast door over the same report: it raises `ConstraintViolation` naming the failing constraint, and returns silently when no selection was requested.
