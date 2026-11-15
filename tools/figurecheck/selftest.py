"""Prove that the figure checker detects the defects it claims to prevent."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import typing as typ
from pathlib import Path

from figurecheck.checks import run
from figurecheck.contract import FIGURES, ROOT

MUTATION_FILE = ROOT / "tools" / "figure-mutations.json"


class _Mutation(typ.NamedTuple):
    """One deliberate defect and the diagnostic that must report it."""

    label: str
    filename: str
    old: str
    new: str
    expected: str


def _as_text(entry: dict[str, object], field: str, *, allow_empty: bool = False) -> str:
    """Return a text field from one declared mutation."""
    value = entry.get(field)
    if not isinstance(value, str):
        raise SystemExit(f"figure contract: mutation field {field!r} is missing")
    if not allow_empty and not value:
        raise SystemExit(f"figure contract: mutation field {field!r} is empty")
    return value


def load_mutations(path: Path) -> tuple[_Mutation, ...]:
    """Load the declared mutations that the self-test applies."""
    declared = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(declared, list) or not declared:
        raise SystemExit("figure contract: the mutation file declares no mutations")
    mutations: list[_Mutation] = []
    for entry in declared:
        if not isinstance(entry, dict):
            raise SystemExit(f"figure contract: malformed mutation {entry!r}")
        mutations.append(
            _Mutation(
                _as_text(entry, "label"),
                _as_text(entry, "filename"),
                _as_text(entry, "old"),
                _as_text(entry, "new", allow_empty=True),
                _as_text(entry, "expected"),
            )
        )
    return tuple(mutations)


MUTATIONS = load_mutations(MUTATION_FILE)


def _detect(work: Path, mutation: _Mutation) -> str | None:
    """Apply one mutation, returning a failure description if it escapes."""
    target = work / mutation.filename
    original = target.read_text(encoding="utf-8")
    if mutation.old not in original:
        return f"{mutation.label}: mutation target not found"
    target.write_text(
        original.replace(mutation.old, mutation.new, 1), encoding="utf-8"
    )
    errors = run(work)
    target.write_text(original, encoding="utf-8")
    if not any(mutation.expected in error for error in errors):
        return f"{mutation.label}: not detected; errors were {errors[:3]}"
    return None


def self_test() -> int:
    """Prove that the checker detects the defects it claims to prevent."""
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as directory:
        work = Path(directory)
        for source in FIGURES.glob("*.svg"):
            shutil.copy2(source, work / source.name)
        baseline = run(work)
        if baseline:
            failures.append(f"baseline copy did not pass: {baseline[:3]}")
        for mutation in MUTATIONS:
            failure = _detect(work, mutation)
            if failure is not None:
                failures.append(failure)
    if failures:
        for failure in failures:
            print(f"figure contract self-test: {failure}", file=sys.stderr)
        return 1
    print(f"figure contract self-test detected all {len(MUTATIONS)} mutations")
    return 0
