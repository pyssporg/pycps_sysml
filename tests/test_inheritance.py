"""Effective member inheritance: the generic view over the definition graph."""

from __future__ import annotations

from pathlib import Path

from pycps_sysml2 import EffectiveMembers, effective_members
from pycps_sysml2.model import load
from tests.fixture_files import fixture_text
from tests.testhelpers import write_model


def _load(tmp_path: Path, name: str):
    path = tmp_path / name.removesuffix(".sysml") / name
    write_model(path, fixture_text(f"inheritance/{name}"))
    return load(path)


def _view(architecture, name: str):
    return effective_members(architecture, architecture.get_part_def(name))


def test_inherited_attribute_and_ports_are_exposed(tmp_path: Path) -> None:
    """``ActuatorLink :> FmuInterop`` exposes the inherited attribute and own ports."""
    architecture = _load(tmp_path, "fmu-interop.sysml")

    view = _view(architecture, "ActuatorLink")

    assert isinstance(view, EffectiveMembers)
    assert list(view.attributes) == ["interop_metadata"]
    assert view.attributes["interop_metadata"].type_name == "FmuInteropMetadata"
    assert list(view.ports) == ["command", "feedback"]
    assert view.ports["command"].direction == "in"
    assert view.ports["feedback"].direction == "out"


def test_derived_members_follow_inherited_members(tmp_path: Path) -> None:
    """Parts, connectors, bindings, and constraints inherit before own members."""
    architecture = _load(tmp_path, "edges.sysml")

    view = _view(architecture, "Derived")

    assert list(view.attributes) == ["root", "own"]
    assert list(view.parts) == ["child", "extra"]
    assert list(view.connections) == ["child.emit->boundary"]
    assert [binding.key for binding in view.bindings] == [
        "child.emit.value=boundary.value"
    ]
    assert [usage.name for usage in view.constraints] == [
        "inheritedRule",
        "ownRule",
    ]


def test_named_override_keeps_position_and_uses_derived_member(
    tmp_path: Path,
) -> None:
    """A derived member replaces the inherited one at the inherited position."""
    architecture = _load(tmp_path, "edges.sysml")
    child = architecture.get_part_def("OverrideChild")

    view = effective_members(architecture, child)

    assert list(view.attributes) == ["root"]
    assert view.attributes["root"] is child.attributes["root"]
    assert view.attributes["root"].type_name == "Real"


def test_inherited_value_fills_derived_member_without_losing_its_fields(
    tmp_path: Path,
) -> None:
    """A value-less derived attribute keeps its multiplicity and the inherited value."""
    architecture = _load(tmp_path, "edges.sysml")
    child = architecture.get_part_def("ValueChild")

    sample = effective_members(architecture, child).attributes["sample"]

    assert (sample.name, sample.type_name, sample.multiplicity) == (
        "sample",
        "Integer",
        "2",
    )
    assert sample.value == 7


def test_diamond_keeps_each_branch(tmp_path: Path) -> None:
    """A diamond is not pruned: both branches contribute their own members."""
    architecture = _load(tmp_path, "edges.sysml")

    view = _view(architecture, "Diamond")

    assert list(view.attributes) == ["root", "left", "right", "bottom"]


def test_cycle_terminates(tmp_path: Path) -> None:
    """A supertype cycle stops at the repeated stored key and still merges once."""
    architecture = _load(tmp_path, "edges.sysml")

    view = _view(architecture, "CycleA")

    assert set(view.attributes) == {"a", "b"}


def test_unknown_supertype_is_skipped(tmp_path: Path) -> None:
    """An unresolved supertype contributes nothing to the effective view."""
    architecture = _load(tmp_path, "edges.sysml")

    view = _view(architecture, "Orphan")

    assert list(view.attributes) == ["own"]


def test_port_definition_inherits_attributes(tmp_path: Path) -> None:
    """``PortDefinition :> PortDefinition`` merges the inherited attributes."""
    architecture = _load(tmp_path, "edges.sysml")

    view = effective_members(
        architecture, architecture.get_port_def("DerivedPort")
    )

    assert list(view.attributes) == ["base_member", "derived_member"]
    assert view.attributes["base_member"].type_name == "Real"
    assert view.attributes["derived_member"].type_name == "Integer"


def test_attribute_definition_inherits_attributes(tmp_path: Path) -> None:
    """``AttributeDefinition :> AttributeDefinition`` merges inherited attributes."""
    architecture = _load(tmp_path, "edges.sysml")

    view = effective_members(
        architecture, architecture.get_attribute_def("DerivedAttr")
    )

    assert list(view.attributes) == ["base_member", "derived_member"]
    assert view.attributes["base_member"].type_name == "Integer"
    assert view.attributes["derived_member"].type_name == "Real"


def test_port_redefinition_records_redefines(tmp_path: Path) -> None:
    """``out port :>> y`` keeps the inherited name and records the target."""
    architecture = _load(tmp_path, "edges.sysml")
    child = architecture.get_part_def("RedefinitionChild")

    assert child.ports["y"].redefines == ("y",)
    assert child.ports["y"].subsets == ()
    assert effective_members(architecture, child).ports["y"] is child.ports["y"]


def test_attribute_subsetting_records_subsets(tmp_path: Path) -> None:
    """``attribute narrowed :> ValueBase::sample`` records the subsetting target."""
    architecture = _load(tmp_path, "edges.sysml")

    narrowed = architecture.get_part_def("SubsettingChild").attributes["narrowed"]

    assert narrowed.subsets == ("ValueBase::sample",)
    assert narrowed.redefines == ()
