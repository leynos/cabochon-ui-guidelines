"""Parse the Markdown tables and worked cells of chapter 14.

The `tables`, `table_with`, `addends`, `stated_total` and `plane_size`
functions read the chapter source that `layoutcheck.chapter` and
`layoutcheck.selftest` supply. `table_with` raises the layout package's
`ContractError` when the text lacks the table the caller needs.
"""

from __future__ import annotations

import re

from layoutcheck.contract import ContractError

PLANE_RE = re.compile(r"^(\d+)\s*×\s*(\d+)(?![\d.])")


class MalformedCellError(ValueError):
    """A worked cell is not a sum of integers joined by ``+``."""

    def __init__(self, cell: str) -> None:
        """Describe the cell that is not a plain sum.

        Parameters
        ----------
        cell : str
            The worked cell that could not be parsed as a sum.
        """
        super().__init__(f"{cell!r} is not a sum of integers joined by '+'")


def tables(text: str) -> list[list[list[str]]]:
    """Return every Markdown table as rows of stripped cells.

    Parameters
    ----------
    text : str
        The Markdown source to scan.

    Returns
    -------
    list[list[list[str]]]
        Each table as its rows, with each row as its stripped cells.
    """
    found: list[list[list[str]]] = []
    rows: list[list[str]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("|"):
            rows.append([cell.strip() for cell in line.strip("|").split("|")])
        elif rows:
            found.append(rows)
            rows = []
    if rows:
        found.append(rows)
    return found


def is_rule(cells: list[str]) -> bool:
    """Return whether a table row is a separator rule.

    Parameters
    ----------
    cells : list[str]
        The row's stripped cells.

    Returns
    -------
    bool
        Whether every cell contains only hyphens or colons.
    """
    return bool(cells) and all(
        bool(cell) and set(cell) <= {"-", ":"} for cell in cells
    )


def table_with(text: str, header: str) -> list[list[str]]:
    """Return the data rows of the table whose header names a column.

    Parameters
    ----------
    text : str
        The Markdown source to scan.
    header : str
        The column header that identifies the table.

    Returns
    -------
    list[list[str]]
        The table's data rows, excluding its separator rule.

    Raises
    ------
    ContractError
        If no table has a column with the requested header.
    """
    for table in tables(text):
        if header in table[0]:
            return [row for row in table[1:] if not is_rule(row)]
    raise ContractError(f"chapter 14 has no table with a {header!r} column")


def addends(cell: str) -> list[int]:
    """Return the integer addends of a worked arithmetic cell.

    Only ``+`` may join the addends. Any other operator, or a term that is not
    an integer, raises `MalformedCellError` instead of extracting numbers from a
    malformed cell.

    Parameters
    ----------
    cell : str
        The worked arithmetic cell.

    Returns
    -------
    list[int]
        The addends that precede any stated total.
    """
    try:
        return [int(term) for term in cell.split("=")[0].split("+")]
    except ValueError as error:
        raise MalformedCellError(cell) from error


def stated_total(cell: str) -> int:
    """Return the total that a worked arithmetic cell states.

    A cell that states no total, because it has no equals sign, still supplies
    its own integer as the total. The total is read from the text after the
    last equals sign.

    Parameters
    ----------
    cell : str
        The worked arithmetic cell, such as ``28 + 28 = 56``.

    Returns
    -------
    int
        The integer after the last equals sign, or the integer that the whole
        cell holds when the cell states no total.

    Raises
    ------
    ValueError
        If the stated total is not an integer.
    """
    return int(cell.split("=")[-1])


def plane_size(cell: str) -> tuple[int, int] | None:
    """Return the complete width and height that a plane cell states.

    A complete size is a pair of integers joined by a multiplication sign,
    with whitespace optional on either side of it. Anything after the height
    is allowed as an annotation provided that it does not begin with a digit
    or a full stop. A fractional height such as ``320 \u00d7 20.5`` and
    an incomplete size such as ``320 \u00d7`` do not state a complete
    size.

    Parameters
    ----------
    cell : str
        The document-plane cell, such as ``456 \u00d7 298, content 320
        scrolls``.

    Returns
    -------
    tuple[int, int] | None
        The width and height in logical units, or ``None`` when the cell does
        not state a complete size.
    """
    match = PLANE_RE.match(cell)
    if match is None:
        return None
    return int(match.group(1)), int(match.group(2))
