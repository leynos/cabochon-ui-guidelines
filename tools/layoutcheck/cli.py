"""Command-line entry point for the layout budget checks.

The `main` function validates the configurations and chapter 14, and selects
`layoutcheck.selftest` when `--self-test` is given. The `tools/check-layout.py`
script imports and calls it.
"""

from __future__ import annotations

import sys

from layoutcheck.budget import validate
from layoutcheck.chapter import check_chapter
from layoutcheck.contract import BUDGETS
from layoutcheck.selftest import self_test


def run() -> list[str]:
    """Validate every declared configuration and the chapter's worked values."""
    errors: list[str] = []
    for configuration in BUDGETS["configurations"]:
        errors.extend(validate(configuration))
    errors.extend(check_chapter())
    return errors


def main() -> int:
    """Validate the layout budgets, or run the self-test when requested."""
    errors = run()
    if "--self-test" in sys.argv:
        return self_test(errors)
    if errors:
        for error in errors:
            print(f"layout budget: {error}", file=sys.stderr)
        return 1
    print(
        f"layout budget: {len(BUDGETS['configurations'])} configurations "
        "derive from the declared tokens"
    )
    return 0
