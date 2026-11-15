"""Prove that the layout checks detect the defects they exist to prevent.

The `self_test` function runs eleven probes over changed tokens, worked values
and table cells, requiring the matching diagnostic from the budget and chapter
checks. `layoutcheck.cli` invokes it for `--self-test`.
"""

from __future__ import annotations

import copy
import sys

from layoutcheck.budget import derive, validate
from layoutcheck.chapter import check_band_rows, check_worked_rows
from layoutcheck.contract import BUDGETS, chapter_text, table_with


def _worked_diagnostics(row: int, column: int, cell: str) -> list[str]:
    """Return the diagnostics for a worked table with one cell replaced."""
    rows = copy.deepcopy(table_with(chapter_text(), "Document plane"))
    rows[row][column] = cell
    return check_worked_rows(
        rows,
        BUDGETS["tokens"],
        BUDGETS["profiles"],
        BUDGETS["configurations"],
    )


def probe_tool_strip() -> str | None:
    """Return a failure if a changed tool-strip token is not detected."""
    configuration = BUDGETS["configurations"][0]
    tokens = copy.deepcopy(BUDGETS["tokens"])
    tokens["tool_strip"] += 8
    baseline = derive(BUDGETS["tokens"], BUDGETS["profiles"], configuration)
    changed = derive(tokens, BUDGETS["profiles"], configuration)
    if changed[2] == baseline[2]:
        return "a changed tool-strip token did not change the budget"
    return None


def probe_wrong_width() -> str | None:
    """Return a failure if a wrong worked width is not detected."""
    configuration = copy.deepcopy(BUDGETS["configurations"][0])
    width, height = configuration["expected"]
    configuration["expected"] = [width - 100, height]
    errors = validate(configuration, BUDGETS["tokens"], BUDGETS["profiles"])
    if not any("derives" in error for error in errors):
        return "a wrong worked width was not detected"
    return None


def probe_width_floor() -> str | None:
    """Return a failure if a breached width minimum is not detected."""
    configuration = BUDGETS["configurations"][0]
    tokens = copy.deepcopy(BUDGETS["tokens"])
    tokens["document_width_min"] += 1000
    errors = validate(configuration, tokens, BUDGETS["profiles"])
    if not any("below the" in error for error in errors):
        return "a document below the width minimum was not detected"
    return None


def probe_splitter() -> str | None:
    """Return a failure if a changed splitter token is not detected."""
    configuration = BUDGETS["configurations"][0]
    tokens = copy.deepcopy(BUDGETS["tokens"])
    tokens["splitter"] += 10
    baseline = derive(BUDGETS["tokens"], BUDGETS["profiles"], configuration)
    changed = derive(tokens, BUDGETS["profiles"], configuration)
    if changed[1] == baseline[1]:
        return "a changed splitter token did not change the width"
    return None


def probe_exchanged_planes() -> str | None:
    """Return a failure if exchanged document-plane cells are not detected."""
    rows = copy.deepcopy(table_with(chapter_text(), "Document plane"))
    rows[0][3], rows[1][3] = rows[1][3], rows[0][3]
    errors = check_worked_rows(
        rows,
        BUDGETS["tokens"],
        BUDGETS["profiles"],
        BUDGETS["configurations"],
    )
    if not any("document plane" in error for error in errors):
        return "an exchanged document-plane cell was not detected"
    return None


def probe_plane_digit() -> str | None:
    """Return a failure if an extra digit in a plane size is not detected."""
    rows = copy.deepcopy(table_with(chapter_text(), "Document plane"))
    width, height = BUDGETS["configurations"][0]["expected"]
    rows[0][3] = f"{width}0 × {height}"
    errors = check_worked_rows(
        rows,
        BUDGETS["tokens"],
        BUDGETS["profiles"],
        BUDGETS["configurations"],
    )
    if not any("document plane" in error for error in errors):
        return "a plane size with an extra digit was not detected"
    return None


def probe_band_total() -> str | None:
    """Return a failure if a changed band total is not detected."""
    rows = copy.deepcopy(table_with(chapter_text(), "Bands"))
    rows[0][2] = "999"
    errors = check_band_rows(rows, BUDGETS["tokens"], BUDGETS["profiles"])
    if not any("total" in error for error in errors):
        return "a changed band total was not detected"
    return None


def probe_window_longer_number() -> str | None:
    """Return a failure if a window value matches inside a longer number."""
    errors = _worked_diagnostics(0, 0, "11280 × 800, studio + strip, 210 / 240")
    if not any("window cell" in error for error in errors):
        return "a window size inside a longer number was not detected"
    errors = _worked_diagnostics(
        3, 0, "512 × 384, compact, two 1280-unit edge strips"
    )
    if not any("omits the" in error for error in errors):
        return "a pane width inside a longer number was not detected"
    return None


def probe_band_addends() -> str | None:
    """Return a failure if a worked band cell's addends are not checked."""
    errors = _worked_diagnostics(0, 1, "44 + 999 = 160")
    if not any("do not sum" in error for error in errors):
        return "worked band addends that miss their total were not detected"
    return None


def probe_plane_decimal() -> str | None:
    """Return a failure if a plane size with a decimal tail is accepted."""
    errors = _worked_diagnostics(0, 3, "818 × 640.5")
    if not any("document plane" in error for error in errors):
        return "a plane size with a decimal tail was not detected"
    return None


def probe_addend_operator() -> str | None:
    """Return a failure if an operator other than `+` is not rejected."""
    errors = _worked_diagnostics(0, 2, "210 - 6 + 6 + 240 = 462")
    if not any("not a sum" in error for error in errors):
        return "a side allocation using '-' was not rejected"
    rows = copy.deepcopy(table_with(chapter_text(), "Bands"))
    rows[0][1] = "31 - 29 + 26"
    errors = check_band_rows(rows, BUDGETS["tokens"], BUDGETS["profiles"])
    if not any("not a sum" in error for error in errors):
        return "a band row using '-' was not rejected"
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
)


def self_test(baseline_errors: list[str]) -> int:
    """Prove that eleven deliberate token, value or table changes are detected."""
    failures = ["baseline budgets did not pass"] if baseline_errors else []
    failures.extend(failure for probe in PROBES if (failure := probe()))

    if failures:
        for failure in failures:
            print(f"layout budget self-test: {failure}", file=sys.stderr)
        return 1
    print(f"layout budget self-test detected all {len(PROBES)} mutations")
    return 0
