"""Prove that the figure checker detects the defects it claims to prevent.

The `self_test` function copies the figures, applies each mutation from
`tools/figure-mutations.json` and requires the matching diagnostic from
`figurecheck.checks.run`. `figurecheck.cli` invokes it for `--self-test`.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import typing as typ
from pathlib import Path

from figurecheck.checks import run
from figurecheck.contract import (
    DATA_PATH,
    FIGURES,
    ROOT,
    ContractError,
    load_document,
    state_records,
)

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
        raise ContractError(f"mutation field {field!r} is missing")
    if not allow_empty and not value:
        raise ContractError(f"mutation field {field!r} is empty")
    return value


def load_mutations(path: Path) -> tuple[_Mutation, ...]:
    """Load the declared mutations that the self-test applies.

    Parameters
    ----------
    path
        The JSON array of mutation records to read.

    Returns
    -------
    tuple[_Mutation, ...]
        The typed mutation records, in declaration order.

    Raises
    ------
    ContractError
        If the file cannot be read as UTF-8 text, is not valid JSON, declares
        no mutation records, or holds a record with a missing or mistyped
        field.
    """
    try:
        declared = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ContractError(f"cannot read {path}: {error}") from error
    except UnicodeDecodeError as error:
        raise ContractError(f"cannot decode {path}: {error}") from error
    except json.JSONDecodeError as error:
        raise ContractError(f"cannot parse {path}: {error}") from error
    if not isinstance(declared, list) or not declared:
        raise ContractError("the mutation file declares no mutations")
    mutations: list[_Mutation] = []
    for entry in declared:
        if not isinstance(entry, dict):
            raise ContractError(f"malformed mutation {entry!r}")
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


def _detect(
    work: Path,
    mutation: _Mutation,
    data: dict[str, object],
    records: dict[str, dict[str, str]],
) -> str | None:
    """Apply one mutation, returning a failure description if it escapes."""
    target = work / mutation.filename
    original = target.read_text(encoding="utf-8")
    if mutation.old not in original:
        return f"{mutation.label}: mutation target not found"
    target.write_text(
        original.replace(mutation.old, mutation.new, 1), encoding="utf-8"
    )
    errors = run(work, data, records)
    target.write_text(original, encoding="utf-8")
    if not any(mutation.expected in error for error in errors):
        return f"{mutation.label}: not detected; errors were {errors[:3]}"
    return None


def _run_mutations(
    data: dict[str, object],
    records: dict[str, dict[str, str]],
    mutations: tuple[_Mutation, ...],
) -> list[str]:
    """Apply every mutation to a working copy and return the failures."""
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as directory:
        work = Path(directory)
        for source in FIGURES.glob("*.svg"):
            shutil.copy2(source, work / source.name)
        baseline = run(work, data, records)
        if baseline:
            failures.append(f"baseline copy did not pass: {baseline[:3]}")
        for mutation in mutations:
            failure = _detect(work, mutation, data, records)
            if failure is not None:
                failures.append(failure)
    return failures


def self_test() -> int:
    """Prove that the checker detects the defects it claims to prevent."""
    data = load_document(DATA_PATH)
    records, messages = state_records(data)
    if messages:
        for message in messages:
            print(f"figure contract: {message}", file=sys.stderr)
        return 1
    mutations = load_mutations(MUTATION_FILE)
    failures = _run_mutations(data, records, mutations)
    if failures:
        for failure in failures:
            print(f"figure contract self-test: {failure}", file=sys.stderr)
        return 1
    print(f"figure contract self-test detected all {len(mutations)} mutations")
    return 0
