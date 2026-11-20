"""Recover a selection from a configuration and classify the analyses."""

from pathlib import Path

from pycps_sysml2 import core_definitions, load
from pycps_sysml2.parameters import (
    SSP_POLICY,
    analysis_plans,
    analysis_selections,
    configuration_name,
    derived_selection,
    model_root,
    parse_selection,
    resolve_selected,
)

MODEL = Path(__file__).with_name("model.sysml")
ROOT = "System"
ROLES = SSP_POLICY.roles

architecture = load(MODEL, core_definitions())
configuration = architecture.part_definitions["SineLate"]

print(f"configuration: {configuration_name(architecture, 'sine_late', roles=ROLES)}")
print(f"model root: {model_root(architecture, configuration, roles=ROLES).name}")

derived = derived_selection(architecture, "sine_late", roles=ROLES)
print(f"derived: {dict(sorted(derived.items()))}")
print(
    "parse_selection equal: "
    f"{parse_selection('scenario=late; source=sine') == derived}"
)

resolved, canonical = resolve_selected(
    architecture, ROOT, dict(sorted(derived.items())), roles=ROLES
)
print(f"resolved source: {resolved.part_definitions[ROOT].parts['source'].type_name}")
print(
    "resolved scenario: "
    f"{resolved.part_definitions[ROOT].attributes['scenario'].type_name}"
)

plans = analysis_plans(architecture, roles=ROLES)
for plan in plans:
    print(f"plan: {plan.name} {plan.status} {plan.configuration}")

legal = next(plan for plan in plans if plan.legal)
print(f"canonical {legal.name}: {dict(sorted(legal.canonical.items()))}")

try:
    analysis_selections(architecture, roles=ROLES)
except ValueError as error:
    prefix = str(error).split(";")[0]
    print(
        "analysis_selections: "
        f"{type(error).__name__} at unbound_plan.scenario: {prefix}"
    )

invalid = next(plan for plan in plans if plan.status == "invalid")
print(f"invalid detail: {(invalid.detail or '').split(';')[0]}")
