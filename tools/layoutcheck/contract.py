"""Paths, declared data and Markdown table helpers for the layout contract.

The module loads `tools/layout-budgets.json` and locates
`book/14-spacing-metrics.md`, then provides the table and arithmetic helpers
that the budget and chapter checks share. Every sibling layout module imports
it.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BUDGETS = json.loads(
    (ROOT / "tools" / "layout-budgets.json").read_text(encoding="utf-8")
)
CHAPTER = ROOT / "book" / "14-spacing-metrics.md"
BAND_PROFILES = ("document", "document_strip", "studio", "studio_strip")
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


def chapter_text() -> str:
    """Return the chapter's Markdown source.

    Returns
    -------
    str
        The full text of chapter 14.
    """
    return CHAPTER.read_text(encoding="utf-8")


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
    SystemExit
        If no table has a column with the requested header.
    """
    for table in tables(text):
        if header in table[0]:
            return [row for row in table[1:] if not is_rule(row)]
    raise SystemExit(
        f"layout contract: chapter 14 has no table with a {header!r} column"
    )


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

    Parameters
    ----------
    cell : str
        The worked arithmetic cell.

    Returns
    -------
    int
        The total that follows the equals sign.
    """
    return int(cell.split("=")[-1])


def plane_size(cell: str) -> tuple[int, int] | None:
    """Return the complete width and height that a plane cell states.

    Parameters
    ----------
    cell : str
        The document-plane cell.

    Returns
    -------
    tuple[int, int] | None
        The width and height, or ``None`` when the cell does not state a
        complete size.
    """
    match = PLANE_RE.match(cell)
    if match is None:
        return None
    return int(match.group(1)), int(match.group(2))


def number(tokens: dict[str, int], value: object) -> int:
    """Return a literal number, or resolve a named token against the table.

    Parameters
    ----------
    tokens : dict[str, int]
        The declared token table, keyed by token name.
    value : object
        A literal integer or the name of a token.

    Returns
    -------
    int
        The literal value, or the token's declared value.
    """
    if isinstance(value, int):
        return value
    return tokens[str(value)]
