---
id: INFO-003
type: info
title: Model and policy
summary: The IR, the layering rule, and the two policy objects a domain is selected with.
date: 2026-11-05
status: current
---

# Model and policy

**Layering.** `model` ← `core` ← `metadata` ← `parameters`, where an arrow means
"may import": `model` has no internal dependency, `core` may use `model`,
`metadata` may use `core` and `model`, and `parameters` may use all three.
`parameters/dialect` sits above `metadata`. Nothing below `parameters` imports
`parameters`, and no module below `metadata` imports a marker constant or calls
`is_ssp_model`/`is_analysis`/`is_fmu_model`; a static layering test enforces both
rules. `validation.py` at the package root sits above `parameters` and composes
their validators into one report.

**The IR.** `Architecture` is a merged, insertion-ordered dataclass tree
(definitions, usages, attributes, ports, connections, bindings, constraints,
variation facts, `semantic_issues`); no sysmlpy object crosses the parser boundary,
and loading is non-validating unless `analyze_semantics=True` asks for diagnostics.

**Inheritance.** A definition stores only the members it declares; inherited
members are resolved on demand by `model/effective.py`, never at load (INFO-004).

**Package namespace.** Packages are first-class in storage only: a definition of
the architecture's own package (or a synthesized one) is keyed by its bare
`name`, one from any other package by `Pkg::Name`, and `Definition.name` stays
bare so no qualifier reaches an artifact surface. One resolver
(`Architecture.resolve`) serves every lookup: an exact stored key wins, a bare
name falls back to qualified keys (one match resolves, several raise naming each
candidate), a qualified miss returns `None`.

**Imports.** `Architecture.imports` maps an imported package to the members it
exposes (`None` is a `::*` wildcard). A qualified definition is visible only
through a matching import, so a bare name never falls back to an unimported
package; an explicit `Pkg::Name` that names a stored definition in an unimported
package raises and names the `private import` to add. Visibility is
architecture-wide, not per importing file — a deliberate simplification until
SysML scopes are modelled. Unknown import targets load silently and are left to
`analyze`.

**Two policy objects.** `RolePolicy` (`metadata/roles.py`) binds the model,
analysis, and FmuModel markers to their predicates; the same module owns the
experiment recognizers. `DialectPolicy` (`parameters/policy.py`) composes a
`RolePolicy` with the SSP/FMI metadata and experiment recognizers plus the
retired-attribute and flat-connector rejections. `core/control.py` holds the
single `RETIRED_ATTRIBUTES` map and residual `pyssp_*` catch-all: history, not
a third policy object.

**Defaults.** Marker names stay exported (`SSP_MODEL_MARKER`, `ANALYSIS_MARKER`,
`FMU_MODEL_MARKER`, `PARAMETER_INTERFACE_MARKER`, `PARAMETER_SET_MARKER`);
`SSP_ROLES`/`SSP_POLICY` are the defaults, and no `GENERIC_POLICY` exists.

**Injection.** Public entry points in `parameters/` and `parameters/dialect/`
take the policy keyword-only and required; private helpers take it positionally
and forward it, so every call site states its domain.
