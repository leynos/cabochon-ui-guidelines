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
    """Parse visible checklist items, ignoring comments, fences and code.

    Each item body must begin with a bold requirement identifier such as
    ``**CON-01**``. The body is stored against that identifier together with
    the destinations of every ``Owner:`` link it names.

    Parameters
    ----------
    path : Path
        The checklist Markdown file to read as UTF-8.
    problems : list[str]
        Diagnostics collected for the caller. The list is appended to in
        place and never cleared. It receives:

        * ``"checklist item has no requirement identifier"`` for an item
          body that does not start with a bold identifier;
        * ``"duplicate checklist identifier CON-01"``, with the real
          identifier in place of the example, when an identifier is
          already present.

    Returns
    -------
    dict[str, list[str]]
        Each requirement identifier mapped to the owner destinations its
        item names, in source order; the list is empty when the item names
        no owner. A later item repeating an identifier replaces the earlier
        entry's owner list rather than merging with it.

    Raises
    ------
    OSError
        If the checklist file cannot be read.
    UnicodeDecodeError
        If the file is not valid UTF-8.
    """
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
