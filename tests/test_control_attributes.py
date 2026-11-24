"""The retired ``pyssp_*`` vocabulary fails with a migration hint.

Nothing in the dialect recognizes a name prefix any more. These tests pin the
one surviving rule: a document that still writes a removed name must raise, and
the message must name the typed-container replacement. A name outside the map
is not skipped either — the whole prefix was removed in 0.3.0.
"""

from __future__ import annotations

import pytest

from pycps_sysml.core.control import (
    RETIRED_ATTRIBUTES,
    validate_retired_attributes,
)
from pycps_sysml.model import Architecture, Attribute, PartDefinition, PortDefinition


def _architecture(*attribute_names: str) -> Architecture:
    """One part def carrying the named attributes, for validation tests."""
    part_def = PartDefinition(
        name="Component",
        attributes={
            name: Attribute(name=name, type_name="String")
            for name in attribute_names
        },
    )
    return Architecture(
        package_name="Pkg",
        part_definitions={"Component": part_def},
    )


def test_the_retired_map_covers_every_removed_tag() -> None:
    assert set(RETIRED_ATTRIBUTES) == {
        "pyssp_default_start_time",
        "pyssp_default_stop_time",
        "pyssp_flat_connector",
        "pyssp_implementation",
        "pyssp_parameter_set",
    }


@pytest.mark.parametrize(
    ("name", "replacement"),
    [
        ("pyssp_default_start_time", "DefaultExperiment"),
        ("pyssp_default_stop_time", "DefaultExperiment"),
        ("pyssp_flat_connector", "--flat-connector"),
        ("pyssp_implementation", "fmu_meta"),
        ("pyssp_parameter_set", "ParameterSet"),
    ],
)
def test_each_retired_tag_names_its_replacement(
    name: str, replacement: str
) -> None:
    architecture = _architecture(name)

    with pytest.raises(ValueError) as excinfo:
        validate_retired_attributes(architecture)

    message = str(excinfo.value)
    assert message.startswith(f"Component.{name} is no longer supported; ")
    assert replacement in message


def test_an_unlisted_pyssp_name_is_an_error_not_a_skip() -> None:
    architecture = _architecture("pyssp_something_else")

    with pytest.raises(ValueError) as excinfo:
        validate_retired_attributes(architecture)

    message = str(excinfo.value)
    assert "Component.pyssp_something_else is no longer supported" in message
    assert "removed in 0.3.0" in message
    assert "typed attribute container" in message
    assert "attribute <name> : <Def>;" in message


def test_a_retired_name_on_a_port_definition_is_also_rejected() -> None:
    architecture = Architecture(
        package_name="Pkg",
        port_definitions={
            "Signal": PortDefinition(
                name="Signal",
                attributes={"pyssp_flat_connector": Attribute(name="pyssp_flat_connector")},
            )
        },
    )

    with pytest.raises(ValueError, match="--flat-connector"):
        validate_retired_attributes(architecture)


def test_a_non_pyssp_name_is_left_alone() -> None:
    validate_retired_attributes(_architecture("gain", "fmu_meta"))
