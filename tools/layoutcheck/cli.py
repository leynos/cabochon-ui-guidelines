"""Command-line entry point for the layout budget checks.

The `main` function validates the configurations and chapter 14, and selects
`layoutcheck.selftest` when `--self-test` is given. The `tools/check-layout.py`
script imports and calls it.
"""

from __future__ import annotations

import sys

from layoutcheck.budget import validate
from layoutcheck.chapter import check_chapter
from layoutcheck.contract import (
    DATA_PATH,
    Budgets,
    ContractError,
    load_budgets,
)
from layoutcheck.selftest import self_test


def run(budgets: Budgets) -> list[str]:
    """Validate every declared configuration and the chapter's worked values.

    Parameters
    ----------
    budgets : Budgets
        The declared tokens, profiles and configurations.

    Returns
    -------
    list[str]
        One diagnostic per configuration or chapter value that fails.
    """
    errors: list[str] = []
    for configuration in budgets.configurations:
        errors.extend(validate(configuration, budgets.tokens, budgets.profiles))
    errors.extend(check_chapter(budgets))
    return errors


def main() -> int:
    """Validate the layout budgets, or run the self-test when requested.

    Returns
    -------
    int
        The process exit status: zero on success, one on failure.
    """
    try:
        budgets = load_budgets(DATA_PATH)
        errors = run(budgets)
    except ContractError as error:
        print(f"layout contract: {error}", file=sys.stderr)
        return 1
    if "--self-test" in sys.argv:
        return self_test(errors, budgets)
    if errors:
        for error in errors:
            print(f"layout budget: {error}", file=sys.stderr)
        return 1
    print(
        f"layout budget: {len(budgets.configurations)} configurations "
        "derive from the declared tokens"
    )
    return 0
