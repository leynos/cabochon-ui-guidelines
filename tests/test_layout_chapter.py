"""Tests for the chapter 14 worked-row checks.

A worked side allocation may state at most one total, just as a band cell may,
and the check reports the extra equality rather than reading past it to the
last total.
"""

from __future__ import annotations

from layoutcheck import contract as layoutcheck_contract
from layoutcheck.chapter import check_worked_rows
from layoutcheck.contract import chapter_text
from layoutcheck.tables import table_with


def test_a_side_allocation_with_two_totals_is_reported() -> None:
    """An intermediate equality in a side allocation earns one diagnostic."""
    budgets = layoutcheck_contract.load_budgets(layoutcheck_contract.DATA_PATH)
    rows = [list(row) for row in table_with(chapter_text(), "Document plane")]
    rows[0][2] = "210 + 6 + 240 = 999 = 462"

    errors = check_worked_rows(
        rows, budgets.tokens, budgets.profiles, budgets.configurations
    )

    assert len(errors) == 1, "the extra equality is the row's only defect"
    assert "side allocation" in errors[0], "the diagnostic names the side cell"
    assert "states more than one total" in errors[0], (
        "the diagnostic names the second equals sign"
    )