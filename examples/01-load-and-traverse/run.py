from pathlib import Path

from pycps_sysml import core_definitions, load

MODEL = Path(__file__).resolve().parent / "model.sysml"

architecture = load(MODEL, core_definitions())

system = architecture.get_part_def("System")
ball = architecture.get_part_def("Ball")

print(f"package: {architecture.package_name}")
print(f"part defs: {sorted(architecture.part_definitions)}")
print(
    f"System declared: attributes={sorted(system.attributes)} "
    f"ports={sorted(system.ports)} parts={sorted(system.parts)}"
)
print(f"Ball source file: {Path(ball.source_file).name}")
print(f"get_part_def('Ball'): {ball.name} ({type(ball).__name__})")
print(
    f"included definitions: {len(architecture.included_definitions)} from PysspCore"
)
