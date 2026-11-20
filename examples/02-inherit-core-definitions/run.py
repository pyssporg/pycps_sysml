"""Show what inheriting a core part def gives a model, and what it does not."""

from pathlib import Path

from pycps_sysml2 import core_definitions, effective_members, load
from pycps_sysml2.metadata import fmu_metadata, read_experiment, ssp_metadata

MODEL = Path(__file__).with_name("model.sysml")

architecture = load(MODEL, core_definitions())

system = architecture.get_part_def("System")
ball = architecture.get_part_def("Ball")
simulation = architecture.get_part_def("Simulation")

for part_def in (system, ball, simulation):
    print(f"{part_def.name} specializes: {part_def.specializes}")

slot = effective_members(architecture, system).attributes["ssp_meta"]
print(f"System ssp_meta type: {architecture.resolve_attribute_def(slot).name}")
print(f"System ssp_metadata: {ssp_metadata(architecture, system)!r}")
print(f"System declares ssp_meta locally: {'ssp_meta' in system.attributes}")

metadata = fmu_metadata(architecture, ball)
print(f"Ball source: {metadata.source!r}")
print(f"Ball implementation: {metadata.implementation!r}")

experiment = read_experiment(architecture, simulation, required=True)
print(f"Experiment name: {experiment.name!r}")
print(f"Experiment start_time: {experiment.start_time!r}")
print(f"Experiment stop_time: {experiment.stop_time!r}")
print(f"Experiment step_size: {experiment.step_size!r}")
print(f"Experiment tolerance: {experiment.tolerance!r}")
