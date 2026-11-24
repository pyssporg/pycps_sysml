# Example 04: Variant forms

Shows the three forms a variant can take: typed, a body, or a usage-level point.

## Run

From the workspace root (`pyssp_dev/`), with the workspace venv active (see
[`examples/README.md`](../README.md#setup)):

```bash
python repos/pycps_sysml/examples/04-variant-bodies/run.py
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

## What the definition encodes

A variant can be typed (`variant part directPath : Gain`), a body (`variant part nestedPath { ... }`), or a point on a usage rather than a definition (`variation part source : SignalSource { ... }`); a variant is never both typed and bodied. A body variant carries its own parts and connections, so `nestedPath` wires a `Gain` into a nested `stage` point and out to the boundary. That nested point is selected with a dotted key, `path.stage=attenuateStage`, while `path=nestedPath` selects the enclosing body first. Unsupported forms are not alternative spellings: a bare `variant { ... }` is a syntax error, an unnamed `variant part` is dropped, and a variant that is both typed and bodied is refused. Selection mechanics live in example 03, and configuration-based selection in the next example.
