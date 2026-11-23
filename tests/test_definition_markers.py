"""The shipped vocabulary and the code constants must stay in sync.

Marker names, metadata slot names, and member names live twice by design: once
in Python as constants the dialect reads, and once in ``core.sysml`` as the
definitions a model includes. A rename in either place that misses the other
would split the vocabulary across releases, so this guard reads the constants
and requires every term to occur in the installed file.
"""

from __future__ import annotations

import importlib

from pycps_sysml2 import core_definitions

#: Modules whose module-level constants are part of the vocabulary contract.
_MODULE_NAMES = (
    "pycps_sysml2.metadata.roles",
    "pycps_sysml2.metadata.fmu_metadata",
    "pycps_sysml2.metadata.ssp_metadata",
    "pycps_sysml2.parameters.dialect.markers",
)

#: Constant suffixes that name a term ``core.sysml`` must declare. A port name
#: (``PARAMETERS_PORT_NAME``) and the SSD implementation enumeration
#: (``FMU_IMPLEMENTATION_VALUES``) are authoring/deployment vocabulary, not
#: definitions the core library declares, so they are deliberately out of scope.
_TERM_SUFFIXES = ("_MARKER", "_ATTR", "_FIELDS")


def _vocabulary_terms() -> set[str]:
    """Read the constants from the owning modules; never restate their values."""

    terms: set[str] = set()
    for module_name in _MODULE_NAMES:
        module = importlib.import_module(module_name)
        for name, value in vars(module).items():
            if not name.endswith(_TERM_SUFFIXES):
                continue
            if isinstance(value, str):
                terms.add(value)
            elif isinstance(value, tuple):
                terms.update(item for item in value if isinstance(item, str))
    return terms


def test_core_definitions_carry_every_vocabulary_constant() -> None:
    text = core_definitions().read_text(encoding="utf-8")

    missing = sorted(term for term in _vocabulary_terms() if term not in text)

    assert not missing, (
        "core.sysml no longer carries these constants from code: "
        + ", ".join(missing)
    )


def test_core_definitions_state_the_reserved_parameter_port_name() -> None:
    """The reserved usage name is canonical in ``core.sysml``, not only code."""

    markers = importlib.import_module("pycps_sysml2.parameters.dialect.markers")
    text = core_definitions().read_text(encoding="utf-8")

    assert f"in port {markers.PARAMETERS_PORT_NAME}" in text
