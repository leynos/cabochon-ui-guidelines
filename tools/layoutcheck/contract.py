"""Paths, declared data and Markdown table helpers for the layout contract.

The module locates `tools/layout-budgets.json` and `book/14-spacing-metrics.md`,
and provides the `Budgets` record plus the table and arithmetic helpers that
the budget and chapter checks share. It performs no file I/O at import:
`load_document` reads the JSON document, `load_budgets` validates its three
sections, and the command-line entry point loads them once.
"""

from __future__ import annotations

import json
import re
import typing as typ
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = ROOT / "tools" / "layout-budgets.json"
CHAPTER = ROOT / "book" / "14-spacing-metrics.md"
BAND_PROFILES = ("document", "document_strip", "studio", "studio_strip")
PLANE_RE = re.compile(r"^(\d+)\s*×\s*(\d+)(?![\d.])")


class ContractError(Exception):
    """The layout budgets document cannot be read, decoded or parsed.

    The error also reports a document that does not declare the three sections
    the checks read. The loader raises it rather than stopping the interpreter,
    so the command-line entry point can report the defect and choose its own
    exit status.
    """


class Budgets(typ.NamedTuple):
    """The validated layout budgets.

    A `Budgets` is built once by `load_budgets` at the command-line entry point
    and passed to the budget, chapter and self-test checks, so the file read is
    explicit rather than an import-time side effect.
    """

    tokens: dict[str, int]
    profiles: dict[str, list[str]]
    configurations: list[dict[str, object]]


def load_document(path: Path) -> dict[str, object]:
    """Load the layout budgets document as a decoded JSON object.

    Parameters
    ----------
    path
        The document to read.

    Returns
    -------
    dict[str, object]
        The decoded JSON object.

    Raises
    ------
    ContractError
        If the file cannot be read as UTF-8 text, does not decode to JSON or
        does not declare a JSON object.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ContractError(f"cannot read {path}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise ContractError(f"cannot decode {path} as UTF-8: {exc}") from exc
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ContractError(f"cannot parse {path} as JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise ContractError(f"{path} does not declare a JSON object")
    return document


def _mapping(document: dict[str, object], field: str) -> dict[str, object]:
    """Return a declared JSON object field, or report its absence."""
    value = document.get(field)
    if not isinstance(value, dict):
        raise ContractError(f"layout budgets do not declare {field}")
    return value


def _sequence(document: dict[str, object], field: str) -> list[object]:
    """Return a declared JSON array field, or report its absence."""
    value = document.get(field)
    if not isinstance(value, list):
        raise ContractError(f"layout budgets do not declare {field}")
    return value


def load_budgets(path: Path) -> Budgets:
    """Load and validate the layout budgets at ``path``.

    Parameters
    ----------
    path
        The budgets document to load.

    Returns
    -------
    Budgets
        The token table, band profiles and worked configurations.

    Raises
    ------
    ContractError
        If the document cannot be read, does not declare the three sections,
        or declares a token table whose values are not integers.
    """
    document = load_document(path)
    tokens = _mapping(document, "tokens")
    if not all(isinstance(value, int) for value in tokens.values()):
        raise ContractError("layout budgets declare a non-integer token")
    profiles = _mapping(document, "profiles")
    for name, bands in profiles.items():
        if not isinstance(bands, list) or not all(
            isinstance(band, str) for band in bands
        ):
            raise ContractError(
                f"layout budget profile {name!r} is not a list of names"
            )
    configurations: list[dict[str, object]] = []
    for index, value in enumerate(_sequence(document, "configurations")):
        if not isinstance(value, dict):
            raise ContractError(f"configurations[{index}] is not a JSON object")
        configurations.append(value)
    return Budgets(
        tokens=typ.cast("dict[str, int]", tokens),
        profiles=typ.cast("dict[str, list[str]]", profiles),
        configurations=configurations,
    )


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


def number(tokens: dict[str, int], value: object) -> int:
    """Return a literal number, or resolve a named token against the table.

    An ``int`` value, which includes a ``bool``, is returned unchanged. Any
    other value is converted with ``str()`` and looked up in ``tokens`` by the
    resulting name.

    Parameters
    ----------
    tokens : dict[str, int]
        The declared token table, keyed by token name.
    value : object
        A literal ``int`` or the name of a token.

    Returns
    -------
    int
        The literal integer, or the token's declared value.

    Raises
    ------
    KeyError
        If the name of a value that is not an ``int`` has no entry in
        ``tokens``.
    """
    if isinstance(value, int):
        return value
    return tokens[str(value)]
