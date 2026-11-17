"""Check the chapter's band and worked tables against the derived budgets.

The `check_chapter` function parses the tables in chapter 14 and compares each
row with the values derived by `layoutcheck.budget`. `layoutcheck.cli` and
`layoutcheck.selftest` import it.
"""

from __future__ import annotations

import re

from layoutcheck.budget import bands, derive
from layoutcheck.contract import BAND_PROFILES, Budgets, number
from layoutcheck.tables import (
    MalformedCellError,
    addends,
    plane_size,
    stated_total,
    table_with,
)


def _stated_total(cell: str, label: str, errors: list[str]) -> int | None:
    """Return the cell's stated total, or record that it is not an integer."""
    try:
        return stated_total(cell)
    except ValueError:
        errors.append(f"{label} {cell!r} is not an integer")
        return None


def _complete_number(value: int) -> str:
    """Return a pattern matching a whole number, not part of a longer one.

    Parameters
    ----------
    value : int
        The whole number to match.

    Returns
    -------
    str
        A regular expression that matches the number on its own.
    """
    return rf"(?<![\d.]){value}(?![\d.])"


def check_band_rows(
    rows: list[list[str]], tokens: dict[str, int], profiles: dict[str, list[str]]
) -> list[str]:
    """Check that each band table row sums to its stated total.

    Parameters
    ----------
    rows : list[list[str]]
        The band table's data rows.
    tokens : dict[str, int]
        The declared token table, keyed by token name.
    profiles : dict[str, list[str]]
        The declared band profiles, keyed by profile name.

    Returns
    -------
    list[str]
        One diagnostic per row that does not match a profile, plus one for
        each declared profile the table omits.
    """
    errors: list[str] = []
    matched: set[str] = set()
    for row in rows:
        if len(row) != 3:
            errors.append(f"band table row {row!r}: expected three cells")
            continue
        try:
            values = addends(row[1])
        except MalformedCellError as error:
            errors.append(f"band table row {row[0]!r}: {error}")
            continue
        names = [
            name
            for name, members in profiles.items()
            if [tokens[band] for band in members] == values
        ]
        if not names:
            errors.append(
                f"band table row {row[0]!r}: bands are not a declared profile"
            )
            continue
        matched.update(names)
        total = _stated_total(
            row[2], f"band table row {row[0]!r}: total", errors
        )
        if total is None:
            continue
        for name in names:
            expected = bands(tokens, profiles, name)
            if total != expected:
                errors.append(
                    f"band table row {row[0]!r}: total {row[2]!r} is not "
                    f"the derived {expected}"
                )
    errors.extend(
        f"band table omits the {name!r} profile"
        for name in BAND_PROFILES
        if name not in matched
    )
    return errors


def _check_worked_window(
    configuration: dict[str, object], window: str, tokens: dict[str, int]
) -> list[str]:
    """Check the window cell against the declared window and pane widths.

    Parameters
    ----------
    configuration : dict[str, object]
        The configuration that the row describes.
    window : str
        The row's window cell.
    tokens : dict[str, int]
        The declared token table, keyed by token name.

    Returns
    -------
    list[str]
        One diagnostic per value the cell omits.
    """
    errors: list[str] = []
    name = str(configuration["name"])
    declared_width = number(tokens, configuration["width"])
    declared_height = number(tokens, configuration["height"])
    width_pattern = _complete_number(declared_width)
    height_pattern = _complete_number(declared_height)
    size = rf"{width_pattern}\s*×\s*{height_pattern}"
    if re.search(size, window) is None:
        errors.append(
            f"worked table row {name!r}: window cell {window!r} is not "
            f"{declared_width} × {declared_height}"
        )
    for side_name in ("left", "right"):
        pane = str(configuration[side_name])
        if re.search(_complete_number(tokens[pane]), window) is None:
            errors.append(
                f"worked table row {name!r}: window cell omits the "
                f"{pane} width {tokens[pane]}"
            )
    return errors


def _check_addends(name: str, cell: str, total: int) -> list[str]:
    """Check that a worked cell's addends sum to its stated total.

    Parameters
    ----------
    name : str
        The configuration name, used in diagnostics.
    cell : str
        The worked arithmetic cell.
    total : int
        The total that the cell states.

    Returns
    -------
    list[str]
        A diagnostic when the addends are malformed or do not sum to the
        total.
    """
    try:
        values = addends(cell)
    except MalformedCellError as error:
        return [f"worked table row {name!r}: {error}"]
    if sum(values) != total:
        return [
            f"worked table row {name!r}: addends {cell!r} do not sum to {total}"
        ]
    return []


def _check_stated_bands(name: str, cell: str, expected: int) -> list[str]:
    """Check a worked band cell's stated total and, when stated, its addends.

    Parameters
    ----------
    name : str
        The configuration name, used in diagnostics.
    cell : str
        The row's stated-bands cell.
    expected : int
        The band total that the configuration derives.

    Returns
    -------
    list[str]
        A diagnostic when the stated total is not an integer or does not
        match the derived total, plus one when its addends do not sum to it.
    """
    errors: list[str] = []
    total = _stated_total(cell, f"worked table row {name!r}: bands", errors)
    if total is not None and total != expected:
        errors.append(
            f"worked table row {name!r}: bands {cell!r} are not "
            f"the derived {expected}"
        )
    if "=" in cell and total is not None:
        errors.extend(_check_addends(name, cell, total))
    return errors


def _check_worked_side(
    configuration: dict[str, object], side: str, expected: int
) -> list[str]:
    """Check the side-allocation cell against its derived total.

    Parameters
    ----------
    configuration : dict[str, object]
        The configuration that the row describes.
    side : str
        The row's side-allocation cell.
    expected : int
        The side allocation that the configuration derives.

    Returns
    -------
    list[str]
        One diagnostic per value the cell states incorrectly.
    """
    errors: list[str] = []
    name = str(configuration["name"])
    total = _stated_total(
        side, f"worked table row {name!r}: side allocation", errors
    )
    if total is not None and total != expected:
        errors.append(
            f"worked table row {name!r}: side allocation {side!r} is not "
            f"the derived {expected}"
        )
    if "=" in side and total is not None:
        errors.extend(_check_addends(name, side, total))
    return errors


def _check_worked_plane(
    configuration: dict[str, object],
    plane: str,
    derived: tuple[int, int],
    tokens: dict[str, int],
) -> list[str]:
    """Check the document-plane cell against its derived size.

    Parameters
    ----------
    configuration : dict[str, object]
        The configuration that the row describes.
    plane : str
        The row's document-plane cell.
    derived : tuple[int, int]
        The document width and height that the configuration derives.
    tokens : dict[str, int]
        The declared token table, keyed by token name.

    Returns
    -------
    list[str]
        One diagnostic per value the cell states incorrectly.
    """
    errors: list[str] = []
    name = str(configuration["name"])
    width, height = derived
    if plane_size(plane) != (width, height):
        errors.append(
            f"worked table row {name!r}: document plane {plane!r} is not "
            f"the derived {width} × {height}"
        )
    if configuration.get("compact"):
        content = tokens["document_content_height"]
        if f"content {content} scrolls" not in plane:
            errors.append(
                f"worked table row {name!r}: compact plane does not say "
                f"its {content}-unit content scrolls"
            )
    return errors


def check_worked_row(
    configuration: dict[str, object],
    row: list[str],
    tokens: dict[str, int],
    profiles: dict[str, list[str]],
) -> list[str]:
    """Check one worked table row against its configuration.

    Parameters
    ----------
    configuration : dict[str, object]
        The configuration that the row describes.
    row : list[str]
        The worked table row.
    tokens : dict[str, int]
        The declared token table, keyed by token name.
    profiles : dict[str, list[str]]
        The declared band profiles, keyed by profile name.

    Returns
    -------
    list[str]
        One diagnostic per value the row states incorrectly.
    """
    band_total, width, height = derive(tokens, profiles, configuration)
    window, stated_bands, side, plane = row
    name = str(configuration["name"])
    errors = _check_worked_window(configuration, window, tokens)
    errors.extend(_check_stated_bands(name, stated_bands, band_total))
    declared_width = number(tokens, configuration["width"])
    errors.extend(_check_worked_side(configuration, side, declared_width - width))
    errors.extend(_check_worked_plane(configuration, plane, (width, height), tokens))
    return errors


def check_worked_rows(
    rows: list[list[str]],
    tokens: dict[str, int],
    profiles: dict[str, list[str]],
    configurations: list[dict[str, object]],
) -> list[str]:
    """Check every worked table row against its configuration.

    Parameters
    ----------
    rows : list[list[str]]
        The worked table's data rows.
    tokens : dict[str, int]
        The declared token table, keyed by token name.
    profiles : dict[str, list[str]]
        The declared band profiles, keyed by profile name.
    configurations : list[dict[str, object]]
        The configurations that the rows should describe, in order.

    Returns
    -------
    list[str]
        One diagnostic per row and per count mismatch.
    """
    errors: list[str] = []
    if len(rows) != len(configurations):
        errors.append(
            f"worked table lists {len(rows)} configurations, "
            f"the budget declares {len(configurations)}"
        )
    for configuration, row in zip(configurations, rows, strict=False):
        if len(row) != 4:
            errors.append(f"worked table row {row!r}: expected four cells")
            continue
        errors.extend(check_worked_row(configuration, row, tokens, profiles))
    return errors


def check_chapter(budgets: Budgets, text: str) -> list[str]:
    """Check that chapter 14's tables state the derived worked values.

    Parameters
    ----------
    budgets : Budgets
        The declared tokens, profiles and configurations to check against.
    text : str
        The chapter source to check.

    Returns
    -------
    list[str]
        One diagnostic per table value that does not match the derived
        budgets.
    """
    source = text
    tokens = budgets.tokens
    profiles = budgets.profiles
    errors = check_band_rows(table_with(source, "Bands"), tokens, profiles)
    errors.extend(
        check_worked_rows(
            table_with(source, "Document plane"),
            tokens,
            profiles,
            budgets.configurations,
        )
    )
    return errors
