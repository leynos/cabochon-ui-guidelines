"""Paths, declared data and Markdown table helpers for the layout contract."""

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
PLANE_RE = re.compile(r"^(\d+)\s*×\s*(\d+)(?!\d)")


def chapter_text() -> str:
    """Return the chapter's Markdown source."""
    return CHAPTER.read_text(encoding="utf-8")


def tables(text: str) -> list[list[list[str]]]:
    """Return every Markdown table as rows of stripped cells."""
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
    """Return whether a table row is a separator rule."""
    return bool(cells) and all(
        bool(cell) and set(cell) <= {"-", ":"} for cell in cells
    )


def table_with(text: str, header: str) -> list[list[str]]:
    """Return the data rows of the table whose header names a column."""
    for table in tables(text):
        if header in table[0]:
            return [row for row in table[1:] if not is_rule(row)]
    raise SystemExit(
        f"layout contract: chapter 14 has no table with a {header!r} column"
    )


def addends(cell: str) -> list[int]:
    """Return the integer addends of a worked arithmetic cell."""
    return [int(part) for part in re.findall(r"\d+", cell.split("=")[0])]


def stated_total(cell: str) -> int:
    """Return the total that a worked arithmetic cell states."""
    return int(cell.split("=")[-1])


def plane_size(cell: str) -> tuple[int, int] | None:
    """Return the complete width and height that a plane cell states."""
    match = PLANE_RE.match(cell)
    if match is None:
        return None
    return int(match.group(1)), int(match.group(2))


def number(tokens: dict[str, int], value: object) -> int:
    """Return a literal number, or resolve a named token against the table."""
    if isinstance(value, int):
        return value
    return tokens[str(value)]
