---
id: INFO-009
type: info
title: Roadmap
summary: What is shipped through v0.4.0, and the six v0.2.0 items that remain open.
date: 2026-11-23
status: current
---

# Roadmap

**Shipped through v0.4.0.** Parsing, the IR, variation capture and resolution,
configuration-derived selection, analysis plans, constraint evaluation, and
every SSP and FMI marker and metadata accessor, behind explicit policies. Since
v0.1.0: 0.2.0 added package-scoped definitions, `FmuModel`, and `base_index`;
0.3.0 added part-definition inheritance and the effective-member view,
specialization checks, experiments and tolerance, typed metadata
classification, and the single-report `validate`; 0.4.0 moved the `PysspCore`
vocabulary to `pyssp-sysml-definitions`. No artifact is emitted.

**Status at v0.4.0.** The six items below were scoped for v0.2.0; all are still
open.

1. **FMI authoring attributes — still open.** Guid policy, modelName override,
   capabilities and flags, units, declared causality and variability, binary
   name, and source language. `FmuMetadata` still carries only `source` and
   `implementation`, and the README states the authoring attributes are out of
   scope for 0.4.0. `pyfmi_interfaces` v0.1.0 derives defaults for all of them;
   the markers are added here first, with their recognizers, and only then
   consumed.
2. **A second policy — still open.** An explicit FMI-only or test
   `DialectPolicy` that exercises the seam without a second dialect.
   `parameters/policy.py` binds only `SSP_POLICY`; the seam exists, but only the
   SSP instance is exercised today.
3. **Array and list policy — still open.** FMI 2.0 has no arrays, so list
   parameters expand to `<name>[<index>]` scalar entries
   (`parameters/dialect/declarations.py`, `mapping.py`). Whether the dialect
   carries a count field and what the C header exposes stays open; the current
   policy is the expansion.
4. **Grammar review — still open.** Evaluate a newer `sysmlpy` against the
   private touchpoints (INFO-006) before any bump. `pyproject.toml` still pins
   `sysmlpy==0.96.4`, and no review or bump is recorded. A bump is a dialect
   decision, not a refresh.
5. **Synthesis boundary — still open; status unconfirmed.** No
   `parameters/synthesis/` exists in the current tree, and the history records
   no move or seam decision. Keep it open until a recorded decision says where
   artifact-to-SysML synthesis lives; it reads `pyssp_standard` objects, so
   moving it here would break the no-`pyssp_standard` rule and needs a different
   seam than a policy object.
6. **`fmu_resource_path` — still open.**
   `core/fmi_helpers.fmu_resource_path` still returns `resources/<class>.fmu`,
   an SSP-archive path kept in v0.1.0 for verbatim fidelity (INFO-010), and
   `metadata/fmu_metadata.py` still derives the resource name from it. Move it
   to the SSP implementer.
