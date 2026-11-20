# Example 09: Packages and export

An included root is a separate package: `load(MODEL, VOCAB, core_definitions())` merges its definitions, but they stay visible only through an explicit `private import Shared::*;`. Definitions from another package are stored under qualified keys such as `Shared::Sensor`, while `resolve` and `get_part_def` accept either the bare or the qualified name. `architecture.export_declared()` returns `{filename: text}` for the architecture's own package only, so the included vocabulary never appears and `run.py` passes it again when reloading the export. The export text is canonicalized rather than the input text, so only an export → reload → export cycle is byte-identical. This example is repo-only and writes solely under `tempfile`.

## Run

```bash
python examples/09-packages-and-export/run.py
```

## Expected output

```text
package: Plant
included definitions: ['PysspCore::Analysis', 'PysspCore::DefaultExperiment', 'PysspCore::Experiment', 'PysspCore::FmuMetadata', 'PysspCore::FmuModel', 'PysspCore::ParameterInterface', 'PysspCore::ParameterSet', 'PysspCore::SourcedMetadata', 'PysspCore::SspMetadata', 'PysspCore::SspModel', 'Shared::Sensor']
bare Sensor: Sensor in Shared
qualified Shared::Sensor: Sensor in Shared
same definition: True
imports: ['PysspCore', 'Shared']
exported files: ['model.sysml']
round trip: identical
```
