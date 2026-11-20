"""Enumerate every pair of variants and keep the ones the constraints allow."""

from itertools import product
from pathlib import Path

from pycps_sysml2 import core_definitions, load
from pycps_sysml2.parameters import (
    SSP_POLICY,
    analysis_selection,
    evaluate,
    resolve_selected,
)

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

# A configuration may pin only some points: the asserted constraint derives the
# rest, but only when exactly one completion is valid.
for analysis, configuration in (("step", "StepSystem"), ("sine", "SineSystem")):
    selection = analysis_selection(architecture, analysis, roles=ROLES)
    resolved, canonical = resolve_selected(
        architecture, COMPOSITION, selection, roles=ROLES
    )
    report = evaluate(resolved, COMPOSITION, canonical)
    status = "legal" if report.ok else "violated"
    print(
        f"derived: {configuration}"
        f" source={selection['source']}"
        f" gain={selection['gain']} ({status})"
    )

try:
    analysis_selection(architecture, "system", roles=ROLES)
except ValueError as error:
    print(f"ambiguous: {type(error).__name__}: {error}")
