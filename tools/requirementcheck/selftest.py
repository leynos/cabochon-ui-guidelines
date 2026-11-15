"""Prove each registry check detects its defect and benign edits pass."""

from __future__ import annotations

import tempfile
from pathlib import Path

from requirementcheck.checks import run
from requirementcheck.mutations import (
    _benign_edit_failures,
    _checklist_cases,
    _fresh_repository,
    _owner_copy_case,
    _registry_cases,
    _run_checklist_case,
    _run_registry_case,
    _tally,
)


def self_test() -> None:
    """Prove each check detects its defect and that benign edits still pass."""
    failures: list[str] = []
    detected = 0
    with tempfile.TemporaryDirectory() as temporary:
        root = _fresh_repository(Path(temporary))
        if baseline := run(root):
            failures.append(f"baseline is not clean: {baseline[:3]}")
        for name, edit, expected in _registry_cases():
            detected += _tally(failures, _run_registry_case(root, name, edit, expected))
        for name, edit, expected in _checklist_cases():
            detected += _tally(
                failures, _run_checklist_case(root, name, edit, expected)
            )
        detected += _tally(failures, _owner_copy_case(root))
        failures.extend(_benign_edit_failures(root))
    if failures:
        print("\n".join(f"self-test: {failure}" for failure in failures))
        raise SystemExit(1)
    print(
        f"self-test: {detected} mutations detected, baseline and wording-only edit pass"
    )
