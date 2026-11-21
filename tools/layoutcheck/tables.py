"""Parse the Markdown tables and worked cells of chapter 14.

The `tables`, `table_with`, `addends`, `stated_total` and `plane_size`
functions read the chapter source that `layoutcheck.chapter` and
`layoutcheck.selftest` supply. `table_with` raises the layout package's
`ContractError` when the text lacks the table the caller needs. Fenced code
blocks and HTML comments are removed before any table is read, so an example
table that a renderer would not display cannot stand in for the real one.
"""

from __future__ import annotations

import re

from markdown_structure import strip_fences_and_comments

from layoutcheck.contract import ContractError

PLANE_RE = re.compile(r"^(\d+)\s*×\s*(\d+)(?![\d.])")


class MalformedCellError(ValueError):
    """A worked cell is not a sum of integers with at most one total."""

    def __init__(self, cell: str, reason: str = "") -> None:
        """Describe the cell that could not be read as worked arithmetic.

        Parameters
        ----------
        cell : str
            The worked cell that could not be parsed.
        reason : str
            The defect, as a clause that follows the quoted cell. It
            defaults to the cell not being a plain sum.
        """
        detail = reason or "is not a sum of integers joined by '+'"
        super().__init__(f"{cell!r} {detail}")


def tables(text: str) -> list[list[list[str]]]:
    """Return every rendered Markdown table as rows of stripped cells.

    Fenced code blocks and HTML comments are discarded first, so a table that
    a renderer would only show as an example, or not show at all, is not read
    as the chapter's table.

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
    for raw in strip_fences_and_comments(text).splitlines():
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


def _worked_parts(cell: str) -> tuple[str, str | None]:
    """Split a worked cell into its addend text and its stated total.

    A worked cell states its total at most once. A cell that joins two totals
    with more than one equals sign, such as ``44 + 116 = 999 = 160``, would
    leave the intermediate equality unchecked, so it is rejected rather than
    read from its last total.

    Parameters
    ----------
    cell : str
        The worked arithmetic cell.

    Returns
    -------
    tuple[str, str | None]
        The text before the equals sign, and the text after it when the cell
        states a total.

    Raises
    ------
    MalformedCellError
        If the cell states more than one total.
    """
    parts = cell.split("=")
    if len(parts) > 2:
        raise MalformedCellError(cell, "states more than one total")
    return parts[0], parts[1] if len(parts) == 2 else None


def addends(cell: str) -> list[int]:
    """Return the integer addends of a worked arithmetic cell.

    Only ``+`` may join the addends. Any other operator, or a term that is not
    an integer, raises `MalformedCellError` instead of extracting numbers from a
    malformed cell. A cell that states more than one total is rejected too,
    because the extra equality would go unchecked.

    Parameters
    ----------
    cell : str
        The worked arithmetic cell.

    Returns
    -------
    list[int]
        The addends that precede any stated total.
    """
    terms, _total = _worked_parts(cell)
    try:
        return [int(term) for term in terms.split("+")]
    except ValueError as error:
        raise MalformedCellError(cell) from error


def stated_total(cell: str) -> int:
    """Return the total that a worked arithmetic cell states.

    A cell that states no total, because it has no equals sign, still supplies
    its own integer as the total. The total is read from the text after the one
    equals sign that the cell may hold.

    Parameters
    ----------
    cell : str
        The worked arithmetic cell, such as ``28 + 28 = 56``.

    Returns
    -------
    int
        The integer after the equals sign, or the integer that the whole cell
        holds when the cell states no total.

    Raises
    ------
    ValueError
        If the stated total is not an integer.
    """
    terms, total = _worked_parts(cell)
    return int(terms if total is None else total)


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
