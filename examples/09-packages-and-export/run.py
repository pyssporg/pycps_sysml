"""Show package visibility, qualified names, and canonical export text."""

import tempfile
from pathlib import Path

from pycps_sysml import core_definitions, load

HERE = Path(__file__).resolve().parent
MODEL = HERE / "model.sysml"
VOCAB = HERE / "vocabulary.sysml"

architecture = load(MODEL, VOCAB, core_definitions())

print(f"package: {architecture.package_name}")
print(f"included definitions: {sorted(architecture.included_definitions)}")

bare = architecture.get_part_def("Sensor")
qualified = architecture.get_part_def("Shared::Sensor")
print(f"bare Sensor: {bare.name} in {bare.package}")
print(f"qualified Shared::Sensor: {qualified.name} in {qualified.package}")
print(f"same definition: {bare is qualified}")

print(f"imports: {sorted(architecture.imports)}")

first = architecture.export_declared()
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    for name, text in first.items():
        (root / name).write_text(text, encoding="utf-8")
    reloaded = load(root / "model.sysml", VOCAB, core_definitions())
    second = reloaded.export_declared()
    print(f"exported files: {sorted(first)}")
    print(f"round trip: {'identical' if second == first else 'different'}")
