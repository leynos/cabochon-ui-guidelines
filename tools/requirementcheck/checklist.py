"""Parse the checklist into the requirement identifiers it declares."""

from __future__ import annotations

import typing as typ

from markdown_structure import strip_fences_and_comments

from requirementcheck.contract import OWNER_RE, REQUIREMENT_RE

if typ.TYPE_CHECKING:
    from pathlib import Path


def parse_checklist(path: Path, problems: list[str]) -> dict[str, list[str]]:
    """Parse visible checklist items, ignoring comments and fenced examples."""
    items: dict[str, list[str]] = {}
    text = strip_fences_and_comments(path.read_text(encoding="utf-8"))
    for block in text.split("- [ ] ")[1:]:
        match = REQUIREMENT_RE.match(block)
        if not match:
            problems.append("checklist item has no requirement identifier")
            continue
        identifier = match.group(1)
        if identifier in items:
            problems.append(f"duplicate checklist identifier {identifier}")
        items[identifier] = OWNER_RE.findall(block)
    return items
