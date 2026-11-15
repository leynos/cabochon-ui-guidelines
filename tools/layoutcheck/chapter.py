"""Check the chapter's band and worked tables against the derived budgets.

The `check_chapter` function parses the tables in chapter 14 and compares each
row with the values derived by `layoutcheck.budget`. `layoutcheck.cli` and
`layoutcheck.selftest` import it.
"""

from __future__ import annotations

import re

from layoutcheck.budget import bands, derive
from layoutcheck.contract import (
    BAND_PROFILES,
    BUDGETS,
    MalformedCellError,
    addends,
    chapter_text,
    number,
    plane_size,
    stated_total,
    table_with,
)


def _complete_number(value: int) -> str:
    """Return a pattern matching a whole number, not part of a longer one."""
    return rf"(?<![\d.]){value}(?![\d.])"


def check_band_rows(
    rows: list[list[str]], tokens: dict[str, int], profiles: dict[str, list[str]]
) -> list[str]:
    """Check that each band table row sums to its stated total."""
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
        for name in names:
            expected = bands(tokens, profiles, name)
            if stated_total(row[2]) != expected:
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
    """Check the window cell against the declared window and pane widths."""
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
    """Check that a worked cell's addends sum to its stated total."""
    try:
        values = addends(cell)
    except MalformedCellError as error:
        return [f"worked table row {name!r}: {error}"]
    if sum(values) != total:
        return [
            f"worked table row {name!r}: addends {cell!r} do not sum to {total}"
        ]
    return []


def _check_worked_side(
    configuration: dict[str, object], side: str, expected: int
) -> list[str]:
    """Check the side-allocation cell against its derived total."""
    errors: list[str] = []
    name = str(configuration["name"])
    total = stated_total(side)
    if total != expected:
        errors.append(
            f"worked table row {name!r}: side allocation {side!r} is not "
            f"the derived {expected}"
        )
    if "=" in side:
        errors.extend(_check_addends(name, side, total))
    return errors


def _check_worked_plane(
    configuration: dict[str, object],
    plane: str,
    derived: tuple[int, int],
    tokens: dict[str, int],
) -> list[str]:
    """Check the document-plane cell against its derived size."""
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
    """Check one worked table row against its configuration."""
    band_total, width, height = derive(tokens, profiles, configuration)
    window, stated_bands, side, plane = row
    name = str(configuration["name"])
    errors = _check_worked_window(configuration, window, tokens)
    if stated_total(stated_bands) != band_total:
        errors.append(
            f"worked table row {name!r}: bands {stated_bands!r} are not "
            f"the derived {band_total}"
        )
    if "=" in stated_bands:
        errors.extend(
            _check_addends(name, stated_bands, stated_total(stated_bands))
        )
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
    """Check every worked table row against its configuration."""
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


def check_chapter(text: str | None = None) -> list[str]:
    """Check that chapter 14's tables state the derived worked values."""
    source = chapter_text() if text is None else text
    tokens = BUDGETS["tokens"]
    profiles = BUDGETS["profiles"]
    errors = check_band_rows(table_with(source, "Bands"), tokens, profiles)
    errors.extend(
        check_worked_rows(
            table_with(source, "Document plane"),
            tokens,
            profiles,
            BUDGETS["configurations"],
        )
    )
    return errors
