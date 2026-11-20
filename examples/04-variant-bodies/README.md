# Example 04: Variant forms

A variant can be typed (`variant part directPath : Gain`), a body (`variant part nestedPath { ... }`), or a point on a usage rather than a definition (`variation part source : SignalSource { ... }`); a variant is never both typed and bodied. A body variant carries its own parts and connections, so `nestedPath` wires a `Gain` into a nested `stage` point and out to the boundary. That nested point is selected with a dotted key, `path.stage=attenuateStage`, while `path=nestedPath` selects the enclosing body first. Forms the parser does not support, such as an unnamed `variant` or a variant that is both typed and bodied, are errors rather than alternative spellings. Selection mechanics live in example 03, and configuration-based selection in the next example.

## Run

```bash
python examples/04-variant-bodies/run.py
```

## Expected output

```text
variant directPath: type=Gain body=False
variant nestedPath: type=None body=True
before selection: source SignalSource, path PathChoice
resolved source: Step (is_variation False)
resolved path: PathChoice__nestedPath
body ports: u, y
body parts: gain, stage
body connections: u->gain.u, gain.y->stage.u, stage.y->y
stage type: Attenuate
canonical: {'path': 'nestedPath', 'path.stage': 'attenuateStage', 'source': 'stepSource'}
```
