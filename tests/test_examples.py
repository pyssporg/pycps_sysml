"""Every documented example is executed and checked against its own README.

An example that is not executed rots: the API moves, the README keeps showing
the old call. The oracle is therefore the example's documented stdout. Each
``examples/<case>/README.md`` carries exactly one ```` ```text ```` block, and
this module runs ``run.py`` in a subprocess and compares stdout byte for byte
after stripping the trailing newline. Volatile values (absolute paths) must be
normalized by the example itself, never here.

The examples tree is repo-only: it is not packaged and not installed. The
subprocess therefore runs against ``src/`` through ``PYTHONPATH`` from a
temporary cwd, which also keeps any example that writes a file out of the
repository. ``conftest.GUARDED_ROOTS`` covers ``examples/`` so a run that
rewrites its own README fails the session.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[1]
EXAMPLES = PROJECT / "examples"

#: The documented-output fence. One per example README, nothing normalized.
TEXT_FENCE = re.compile(r"```text\n(.*?)```", re.DOTALL)

#: Files every example directory carries.
REQUIRED_FILES = ("README.md", "model.sysml", "run.py")


def _cases() -> list[Path]:
    return sorted(path for path in EXAMPLES.iterdir() if path.is_dir())


def test_every_example_directory_has_its_three_files() -> None:
    missing = {
        case.name: [name for name in REQUIRED_FILES if not (case / name).is_file()]
        for case in _cases()
    }
    missing = {case: files for case, files in missing.items() if files}

    assert not missing, f"incomplete examples: {missing}"


def test_every_example_is_listed_in_the_index() -> None:
    index = (EXAMPLES / "README.md").read_text(encoding="utf-8")
    unlisted = [case.name for case in _cases() if case.name not in index]

    assert not unlisted, f"examples missing from examples/README.md: {unlisted}"


@pytest.mark.parametrize("case", _cases(), ids=lambda path: path.name)
def test_example_output_matches_its_readme(case: Path, tmp_path: Path) -> None:
    readme = case / "README.md"
    fences = TEXT_FENCE.findall(readme.read_text(encoding="utf-8"))

    assert len(fences) == 1, (
        f"{readme}: exactly one ```text block is the oracle, found {len(fences)}"
    )

    environment = {**os.environ, "PYTHONPATH": str(PROJECT / "src")}
    result = subprocess.run(
        [sys.executable, str(case / "run.py")],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr
    #: The documented block is the contract; a stale README is a failure.
    assert result.stdout.rstrip("\n") == fences[0].rstrip("\n"), (
        f"{readme}: stdout differs from the documented block"
    )
