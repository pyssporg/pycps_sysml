"""Select a variation point, then evaluate the constraint that guards it."""

from pathlib import Path

from pycps_sysml2 import core_definitions, load
from pycps_sysml2.parameters import (
    SSP_POLICY,
    ConstraintViolation,
    enforce_constraints,
    evaluate,
    parse_selection,
    resolve_selected,
)

MODEL = Path(__file__).with_name("model.sysml")
COMPOSITION = "System"

architecture = load(MODEL, core_definitions())
system = architecture.part_definitions[COMPOSITION]

print(f"before selection: {system.parts['mass'].type_name}")

selection = parse_selection("mass=light")
resolved, canonical = resolve_selected(
    architecture, COMPOSITION, selection, roles=SSP_POLICY.roles
)

print(f"canonical: {dict(sorted(canonical.items()))}")
print(
    "resolved mass: "
    f"{resolved.part_definitions[COMPOSITION].parts['mass'].type_name}"
)
print(f"original mass: {system.parts['mass'].type_name}")
print(f"parse_selection: {dict(sorted(selection.items()))}")


def statuses(chosen: dict[str, str]) -> list[tuple[str, str]]:
    report = evaluate(architecture, COMPOSITION, chosen)
    return sorted((result.name, result.status) for result in report.results)


def show(label: str, results: list[tuple[str, str]]) -> None:
    print(f"{label}: " + ", ".join(f"{name} {status}" for name, status in results))


light = parse_selection("mass=light")
heavy = parse_selection("mass=heavy")
light_selection = resolve_selected(
    architecture, COMPOSITION, light, roles=SSP_POLICY.roles
)[1]
heavy_selection = resolve_selected(
    architecture, COMPOSITION, heavy, roles=SSP_POLICY.roles
)[1]

show("selection light", statuses(light_selection))
show("selection heavy", statuses(heavy_selection))

try:
    enforce_constraints(architecture, COMPOSITION, heavy_selection)
except ConstraintViolation as error:
    report = evaluate(architecture, COMPOSITION, heavy_selection)
    failed = sorted((result.name, result.status) for result in report.failed)
    print(f"enforce: {type(error).__name__}: {failed[0][0]}")
