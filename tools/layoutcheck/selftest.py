"""Prove that the layout checks detect the defects they exist to prevent.

The `self_test` function runs twelve probes over changed tokens, worked values
and table cells, requiring the matching diagnostic from the budget and chapter
checks. `layoutcheck.cli` invokes it for `--self-test`.
"""

from __future__ import annotations

import copy
import sys

from layoutcheck.budget import derive, expected_plane, validate
from layoutcheck.chapter import check_band_rows, check_worked_rows
from layoutcheck.contract import Budgets, chapter_text
from layoutcheck.tables import table_with


def _worked_diagnostics(
    budgets: Budgets, row: int, column: int, cell: str
) -> list[str]:
    """Return the diagnostics for a worked table with one cell replaced."""
    rows = copy.deepcopy(table_with(chapter_text(), "Document plane"))
    rows[row][column] = cell
    return check_worked_rows(
        rows,
        budgets.tokens,
        budgets.profiles,
        budgets.configurations,
    )


def probe_tool_strip(budgets: Budgets) -> str | None:
    """Return a failure if a changed tool-strip token is not detected."""
    configuration = budgets.configurations[0]
    tokens = copy.deepcopy(budgets.tokens)
    tokens["tool_strip"] += 8
    baseline = derive(budgets.tokens, budgets.profiles, configuration)
    changed = derive(tokens, budgets.profiles, configuration)
    if changed[2] == baseline[2]:
        return "a changed tool-strip token did not change the budget"
    return None


def probe_wrong_width(budgets: Budgets) -> str | None:
    """Return a failure if a wrong worked width is not detected."""
    configuration = copy.deepcopy(budgets.configurations[0])
    width, height = expected_plane(budgets.tokens, configuration)
    configuration["expected"] = [width - 100, height]
    errors = validate(configuration, budgets.tokens, budgets.profiles)
    if not any("derives" in error for error in errors):
        return "a wrong worked width was not detected"
    return None


def probe_width_floor(budgets: Budgets) -> str | None:
    """Return a failure if a breached width minimum is not detected."""
    configuration = budgets.configurations[0]
    tokens = copy.deepcopy(budgets.tokens)
    tokens["document_width_min"] += 1000
    errors = validate(configuration, tokens, budgets.profiles)
    if not any("below the" in error for error in errors):
        return "a document below the width minimum was not detected"
    return None


def probe_splitter(budgets: Budgets) -> str | None:
    """Return a failure if a changed splitter token is not detected."""
    configuration = budgets.configurations[0]
    tokens = copy.deepcopy(budgets.tokens)
    tokens["splitter"] += 10
    baseline = derive(budgets.tokens, budgets.profiles, configuration)
    changed = derive(tokens, budgets.profiles, configuration)
    if changed[1] == baseline[1]:
        return "a changed splitter token did not change the width"
    return None


def probe_exchanged_planes(budgets: Budgets) -> str | None:
    """Return a failure if exchanged document-plane cells are not detected."""
    rows = copy.deepcopy(table_with(chapter_text(), "Document plane"))
    rows[0][3], rows[1][3] = rows[1][3], rows[0][3]
    errors = check_worked_rows(
        rows,
        budgets.tokens,
        budgets.profiles,
        budgets.configurations,
    )
    if not any("document plane" in error for error in errors):
        return "an exchanged document-plane cell was not detected"
    return None


def probe_plane_digit(budgets: Budgets) -> str | None:
    """Return a failure if an extra digit in a plane size is not detected."""
    rows = copy.deepcopy(table_with(chapter_text(), "Document plane"))
    width, height = expected_plane(budgets.tokens, budgets.configurations[0])
    rows[0][3] = f"{width}0 × {height}"
    errors = check_worked_rows(
        rows,
        budgets.tokens,
        budgets.profiles,
        budgets.configurations,
    )
    if not any("document plane" in error for error in errors):
        return "a plane size with an extra digit was not detected"
    return None


def probe_band_total(budgets: Budgets) -> str | None:
    """Return a failure if a changed band total is not detected."""
    rows = copy.deepcopy(table_with(chapter_text(), "Bands"))
    rows[0][2] = "999"
    errors = check_band_rows(rows, budgets.tokens, budgets.profiles)
    if not any("total" in error for error in errors):
        return "a changed band total was not detected"
    return None


def probe_window_longer_number(budgets: Budgets) -> str | None:
    """Return a failure if a window value matches inside a longer number."""
    errors = _worked_diagnostics(
        budgets, 0, 0, "11280 × 800, studio + strip, 210 / 240"
    )
    if not any("window cell" in error for error in errors):
        return "a window size inside a longer number was not detected"
    errors = _worked_diagnostics(
        budgets, 3, 0, "512 × 384, compact, two 1280-unit edge strips"
    )
    if not any("omits the" in error for error in errors):
        return "a pane width inside a longer number was not detected"
    return None


def probe_band_addends(budgets: Budgets) -> str | None:
    """Return a failure if a worked band cell's addends are not checked."""
    errors = _worked_diagnostics(budgets, 0, 1, "44 + 999 = 160")
    if not any("do not sum" in error for error in errors):
        return "worked band addends that miss their total were not detected"
    return None


def probe_plane_decimal(budgets: Budgets) -> str | None:
    """Return a failure if a plane size with a decimal tail is accepted."""
    errors = _worked_diagnostics(budgets, 0, 3, "818 × 640.5")
    if not any("document plane" in error for error in errors):
        return "a plane size with a decimal tail was not detected"
    return None


def probe_addend_operator(budgets: Budgets) -> str | None:
    """Return a failure if an operator other than `+` is not rejected."""
    errors = _worked_diagnostics(budgets, 0, 2, "210 - 6 + 6 + 240 = 462")
    if not any("not a sum" in error for error in errors):
        return "a side allocation using '-' was not rejected"
    rows = copy.deepcopy(table_with(chapter_text(), "Bands"))
    rows[0][1] = "31 - 29 + 26"
    errors = check_band_rows(rows, budgets.tokens, budgets.profiles)
    if not any("not a sum" in error for error in errors):
        return "a band row using '-' was not rejected"
    return None


def probe_unguarded_totals(budgets: Budgets) -> str | None:
    """Return a failure if a cell without an integer total escapes the check."""
    cells = (
        (1, "160 - 6"),
        (2, "210 - 6"),
        (1, "160 + 6 ="),
    )
    for column, cell in cells:
        errors = _worked_diagnostics(budgets, 0, column, cell)
        reported = [error for error in errors if "is not an integer" in error]
        if len(reported) != 1:
            return (
                f"a worked cell {cell!r} without an integer total produced "
                f"{len(reported)} diagnostics rather than one"
            )
    errors = _worked_diagnostics(budgets, 0, 1, "160 + 6 =")
    if any("do not sum" in error for error in errors):
        return "an unparsable band total still had its addends checked"
    rows = copy.deepcopy(table_with(chapter_text(), "Bands"))
    rows[0][2] = "86 - 6"
    errors = check_band_rows(rows, budgets.tokens, budgets.profiles)
    reported = [error for error in errors if "is not an integer" in error]
    if len(reported) != 1:
        return "a band total without an integer was not reported once"
    rows = copy.deepcopy(table_with(chapter_text(), "Document plane"))
    rows[0][2] = "210 - 6"
    rows[0][3] = "1 × 1"
    rows[1][3] = "1 × 1"
    errors = check_worked_rows(
        rows,
        budgets.tokens,
        budgets.profiles,
        budgets.configurations,
    )
    reported = [error for error in errors if "is not an integer" in error]
    if len(reported) != 1:
        return "a bad side allocation was not reported once"
    if not any("document plane" in error for error in errors):
        return "a bad side allocation stopped the remaining cells being checked"
    return None


PROBES = (
    probe_tool_strip,
    probe_wrong_width,
    probe_width_floor,
    probe_splitter,
    probe_exchanged_planes,
    probe_plane_digit,
    probe_band_total,
    probe_window_longer_number,
    probe_band_addends,
    probe_plane_decimal,
    probe_addend_operator,
    probe_unguarded_totals,
)


def self_test(baseline_errors: list[str], budgets: Budgets) -> int:
    """Prove that twelve deliberate token, value or table changes are detected."""
    failures = ["baseline budgets did not pass"] if baseline_errors else []
    failures.extend(failure for probe in PROBES if (failure := probe(budgets)))

    if failures:
        for failure in failures:
            print(f"layout budget self-test: {failure}", file=sys.stderr)
        return 1
    print(f"layout budget self-test detected all {len(PROBES)} mutations")
    return 0
