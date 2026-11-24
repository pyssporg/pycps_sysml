"""SysML v2 model adapter for pycps_sysml.

Anti-corruption layer over the external `sysmlpy` parser:

- ``model.py``    — the repo-owned dataclasses every generator works against.
- ``parser.py``   — the ONLY module that imports ``sysmlpy``; parses one
  file's packages and exposes the grammar-layer walks.
- ``variation.py``— captures variation points from the raw parse tree, which
  ``sysmlpy`` drops from its wrapper objects.
- ``loader.py``   — walks a file or directory, merges the packages, and
  builds the repo-owned model.
- ``effective.py``— the inherited member view; the IR stays source-faithful.
- ``attribution.py`` — the per-file scan that ties each merged definition
  back to the file that declared it.
- ``exporter.py`` — emits conformant SysML v2 text from the repo-owned model
  (no parser involvement, so the output format is a repo contract).

If sysmlpy's API changes, only ``parser.py`` needs fixes.
"""

from collections.abc import Sequence
from pathlib import Path

from pycps_sysml.model.effective import EffectiveMembers, effective_members
from pycps_sysml.model.model import (
    Architecture,
    Attribute,
    AttributeDefinition,
    Binding,
    Connection,
    ConstraintDefinition,
    ConstraintParameter,
    ConstraintUsage,
    Definition,
    PartDefinition,
    PartUsage,
    PortDefinition,
    PortUsage,
    RequirementDefinition,
    SemanticIssue,
    VariantBody,
    VariantMember,
    endpoint_text,
)

__all__ = [
    "Architecture",
    "Attribute",
    "AttributeDefinition",
    "Binding",
    "Connection",
    "ConstraintDefinition",
    "ConstraintParameter",
    "ConstraintUsage",
    "Definition",
    "EffectiveMembers",
    "PartDefinition",
    "PartUsage",
    "PortDefinition",
    "PortUsage",
    "RequirementDefinition",
    "SemanticIssue",
    "VariantBody",
    "VariantMember",
    "effective_members",
    "endpoint_text",
    "load",
]


def load(
    path: Path | str | Sequence[Path | str],
    *includes: Path | str,
    analyze_semantics: bool = False,
) -> Architecture:
    """Load a primary architecture root plus any number of included roots.

    ``path`` is one root or a sequence whose first element is the primary model
    root; further elements and ``*includes`` are included roots.
    ``analyze_semantics=True`` opts into specialization diagnostics. See
    :func:`pycps_sysml.model.loader.load`. Implemented in
    :mod:`pycps_sysml.model.loader`.
    """
    from pycps_sysml.model.loader import load as _load

    return _load(path, *includes, analyze_semantics=analyze_semantics)
