"""Show parameter ports, applied sets, bind orientation, and mapping specs."""

from pathlib import Path

from pycps_sysml2 import core_definitions, load
from pycps_sysml2.parameters import (
    SSP_POLICY,
    applied_sets,
    mapping_specs,
    parameter_bind,
    parameter_declarations,
)

MODEL = Path(__file__).with_name("model.sysml")
COMPOSITION = "System"

architecture = load(MODEL, core_definitions())
system = architecture.get_part_def(COMPOSITION)
controller = architecture.resolve_part(system.parts["controller"])

declarations = sorted(
    (attribute.name, attribute.primitive_type_str())
    for attribute in parameter_declarations(architecture, controller)
)
print(
    "declarations: "
    + ", ".join(f"{name} {type_name}" for name, type_name in declarations)
)

applications = sorted(
    applied_sets(architecture, system, policy=SSP_POLICY),
    key=lambda applied: (applied.component_name, applied.usage_name),
)
print(
    "applied sets: "
    + ", ".join(
        f"{applied.component_name} {applied.set_definition.name} "
        f"usage={applied.usage_name} identity={applied.identity}"
        for applied in applications
    )
)

binding = parameter_bind(system.bindings[0])
print(
    f"bind: parameter={binding.port_reference()} "
    f"target={'.'.join(binding.set_path)} "
    "(parameter port left, set usage right)"
)

specs = sorted(
    mapping_specs(architecture, system, policy=SSP_POLICY),
    key=lambda spec: (spec.component_name, spec.set_name),
)
for spec in specs:
    for source, target in sorted(spec.entries):
        print(
            f"mapping: component={spec.component_name} set={spec.set_name} "
            f"member={source} target={target}"
        )
