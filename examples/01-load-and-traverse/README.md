# Example 01: Load and traverse

`load` takes the model root and the packaged `PysspCore` definitions as a second root, so the model imports that vocabulary instead of redeclaring it. The driver then traverses the merged IR: the package name, the part-definition keys, one definition's declared parts, ports, and attributes, another definition's source file, and how many definitions the include supplied. Inheriting the core part defs is example 02, not this example.

## Run

```bash
python examples/01-load-and-traverse/run.py
```

## Expected output

```text
package: Plant
part defs: ['Ball', 'Local', 'PysspCore::Analysis', 'PysspCore::FmuModel', 'PysspCore::SspModel', 'System']
System declared: attributes=[] ports=['y'] parts=['ball', 'local']
Ball source file: model.sysml
get_part_def('Ball'): Ball (PartDefinition)
included definitions: 10 from PysspCore
```
