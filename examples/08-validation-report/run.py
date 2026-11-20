"""One report over every dialect check, instead of the first accessor error."""

from pathlib import Path

from pycps_sysml2 import core_definitions, load, validate

HERE = Path(__file__).parent
COMPOSITION = "System"


def pairs(report):
    """Parse ``format()`` into (status, check, message), never printing paths."""
    for line in report.format().splitlines():
        status, _, rest = line.partition(" ")
        check, _, message = rest.partition(": ")
        yield status, check, message


def show(name: str, path: Path, *, passes: bool):
    report = validate(load(path, core_definitions()), COMPOSITION)
    print(f"{name} ok: {report.ok}")
    for status, check, message in pairs(report):
        if status == "PASS":
            if passes:
                print(f"PASS {check}")
        else:
            # Keep the stable part: the check code and the member it names.
            print(f"FAIL {check}: {message.split(';')[0]}")
    return report


show("model.sysml", HERE / "model.sysml", passes=True)
broken = show("broken.sysml", HERE / "broken.sysml", passes=False)

try:
    broken.raise_for_issues()
except ValueError as error:
    first = str(error).splitlines()[0]
    print(f"raise_for_issues: {type(error).__name__}: {first}")
