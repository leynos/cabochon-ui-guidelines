"""Parse the checklist into the requirement identifiers it declares.

The `parse_checklist` function strips comments, fenced examples and code spans,
then maps each visible checklist item to the owner links it names.
`requirementcheck.checks` imports it before the registry comparison.
"""

from __future__ import annotations

import typing as typ

from markdown_structure import checklist_items, strip_code_and_comments

from requirementcheck.contract import OWNER_RE, REQUIREMENT_RE

if typ.TYPE_CHECKING:
    from pathlib import Path


def parse_checklist(path: Path, problems: list[str]) -> dict[str, list[str]]:
    """Parse visible checklist items, ignoring comments, fences and code."""
    items: dict[str, list[str]] = {}
    text = strip_code_and_comments(path.read_text(encoding="utf-8"))
    for block in checklist_items(text):
        match = REQUIREMENT_RE.match(block)
        if not match:
            problems.append("checklist item has no requirement identifier")
            continue
        identifier = match.group(1)
        if identifier in items:
            problems.append(f"duplicate checklist identifier {identifier}")
        items[identifier] = OWNER_RE.findall(block)
    return items
