"""Enumerate every pair of variants and keep the ones the constraints allow."""

from itertools import product
from pathlib import Path

from pycps_sysml2 import core_definitions, load
from pycps_sysml2.parameters import SSP_POLICY, evaluate, resolve_selected

MODEL = Path(__file__).with_name("model.sysml")
COMPOSITION = "System"
ROLES = SSP_POLICY.roles

architecture = load(MODEL, core_definitions())
source_variants = architecture.part_definitions["SourceChoice"].variants
gain_variants = architecture.part_definitions["GainChoice"].variants

print(
    f"space: source {len(source_variants)} x gain {len(gain_variants)}"
    f" = {len(source_variants) * len(gain_variants)} assignments"
)

legal_pairs = []
total = 0
for source, gain in product(source_variants, gain_variants):
    total += 1
    selection = {"source": source.name, "gain": gain.name}
    resolved, canonical = resolve_selected(
        architecture, COMPOSITION, selection, roles=ROLES
    )
    report = evaluate(resolved, COMPOSITION, canonical)
    pair = f"{source.name}+{gain.name}"
    if report.ok:
        legal_pairs.append(pair)
        status = "legal -"
    else:
        failed = ", ".join(result.name for result in report.failed)
        status = f"violated {failed}"
    print(f"source={source.name} gain={gain.name}: {status}")

print(f"legal: {len(legal_pairs)} of {total}")
print(f"allowed: {', '.join(legal_pairs)}")

pinned = architecture.part_definitions["StepTwoSystem"]
pinned_report = evaluate(
    architecture, "StepTwoSystem", {"source": "step", "gain": "two"}
)
print(
    f"pinned: {pinned.name}"
    f" source={pinned.parts['source'].value}"
    f" gain={pinned.parts['gain'].value}"
)
print(f"pinned evaluation: {'legal' if pinned_report.ok else 'violated'}")

# A constraint checks a complete assignment; it never fills an unbound point.
unbound = evaluate(architecture, COMPOSITION, {"source": "step"}).results[0]
print(f"unbound: {unbound.name} {unbound.status} {unbound.detail}")

try:
    resolve_selected(architecture, COMPOSITION, {"source": "step"}, roles=ROLES)
except ValueError as error:
    print(f"partial: {type(error).__name__}: {error}")
