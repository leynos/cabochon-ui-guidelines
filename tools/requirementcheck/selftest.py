"""Prove each registry check detects its defect and benign edits pass.

The `self_test` function applies the cases from `requirementcheck.mutations` to
a temporary copy and requires each diagnostic while benign edits still pass.
`requirementcheck.cli` invokes it for `--self-test`.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from requirementcheck.mutations import (
    _benign_edit_failures,
    _checklist_cases,
    _fresh_repository,
    _owner_copy_case,
    _registry_cases,
    _run,
    _run_checklist_case,
    _run_registry_case,
    _tally,
)


def self_test() -> None:
    """Prove each check detects its defect and that benign edits still pass.

    A temporary copy of the book and registry tools is made, the mutations
    from `requirementcheck.mutations` are applied one at a time, and each
    must produce its expected diagnostic while the untouched baseline, a
    wording-only edit and a comment-only checklist item still pass.

    Returns
    -------
    None
        The function returns nothing; it reports through standard output.

    Raises
    ------
    SystemExit
        With status one when the baseline, a mutation or a benign edit
        misbehaves; each failure is printed with a ``self-test:`` prefix.
    """
    failures: list[str] = []
    detected = 0
    with tempfile.TemporaryDirectory() as temporary:
        root = _fresh_repository(Path(temporary))
        if baseline := _run(root):
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
