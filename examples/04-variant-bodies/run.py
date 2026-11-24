"""Show what a variant can be: typed, a body, or a usage-level point."""

from pathlib import Path

from pycps_sysml import core_definitions, load
from pycps_sysml.parameters import SSP_POLICY, resolve_selected

MODEL = Path(__file__).with_name("model.sysml")
COMPOSITION = "System"

architecture = load(MODEL, core_definitions())
system = architecture.part_definitions[COMPOSITION]
path_choice = architecture.part_definitions["PathChoice"]

for variant in path_choice.variants:
    print(
        f"variant {variant.name}: type={variant.type_name} "
        f"body={variant.body is not None}"
    )

print(
    "before selection: "
    + ", ".join(
        f"{name} {system.parts[name].type_name}" for name in ("source", "path")
    )
)

selection = {
    "path": "nestedPath",
    "path.stage": "attenuateStage",
    "source": "stepSource",
}
resolved, canonical = resolve_selected(
    architecture, COMPOSITION, selection, roles=SSP_POLICY.roles
)
resolved_system = resolved.part_definitions[COMPOSITION]

source = resolved_system.parts["source"]
print(f"resolved source: {source.type_name} (is_variation {source.is_variation})")
print(f"resolved path: {resolved_system.parts['path'].type_name}")

body = resolved.part_definitions["PathChoice__nestedPath"]
print("body ports: " + ", ".join(body.ports))
print("body parts: " + ", ".join(body.parts))
print(
    "body connections: "
    + ", ".join(connection.key for connection in body.connections.values())
)
print(f"stage type: {body.parts['stage'].type_name}")
print("canonical: " + str(dict(sorted(canonical.items()))))
