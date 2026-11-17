"""Check the requirement identifiers, owners and semantic relationships.

The module provides `check_requirements`, `check_states`, `check_profiles`,
`check_commands` and `check_resources`, which read `tools/book-contract.json`
and the chapters it names. `linkcheck.checks` imports all five.
"""

from __future__ import annotations

import typing as typ

if typ.TYPE_CHECKING:
    from pathlib import Path


from markdown_links import link_targets
from markdown_structure import (
    anchors,
    checklist_items,
    slug,
    strip_code_and_comments,
    strip_fences_and_comments,
)

from linkcheck.contract import (
    OWNER_RE,
    REQUIREMENT_RE,
    Contract,
    resolved_destination,
)


def _check_owner(
    identifier: str, owner: str, checklist: Path, problems: list[str]
) -> None:
    """Check that a contract entry names every owning chapter."""
    path_part, _, fragment = owner.partition("#")
    path = (checklist.parent / path_part).resolve()
    if not path.exists():
        problems.append(f"requirement {identifier}: missing owner {owner}")
        return
    if fragment and fragment not in anchors(path):
        problems.append(f"requirement {identifier}: missing owner anchor {owner}")


class _Context(typ.NamedTuple):
    """The shared inputs for one checklist item's checks."""

    checklist: Path
    contract: Contract
    seen: set[str]
    problems: list[str]


def _requirement_identifier(block: str, context: _Context) -> str | None:
    """Return the item's requirement identifier after checking its form."""
    ids = REQUIREMENT_RE.findall(block)
    if not ids:
        context.problems.append("checklist item has no requirement identifier")
        return None
    identifier = ids[0]
    if not context.contract.requirement_ids.fullmatch(identifier):
        context.problems.append(f"requirement {identifier} does not match the pattern")
    if identifier in context.seen:
        context.problems.append(f"duplicate requirement identifier {identifier}")
    context.seen.add(identifier)
    return identifier


def _check_requirement(block: str, context: _Context) -> None:
    """Check one checklist item's identifier and every owner it names."""
    identifier = _requirement_identifier(block, context)
    if identifier is None:
        return
    owners = OWNER_RE.findall(block)
    if not owners:
        context.problems.append(f"requirement {identifier} names no owner")
    for owner in owners:
        _check_owner(identifier, owner, context.checklist, context.problems)


def check_requirements(book: Path, contract: Contract, problems: list[str]) -> None:
    """Check checklist identifiers, owners and the anchors they name."""
    checklist = book / contract.requirements["checklist"]
    text = strip_code_and_comments(checklist.read_text(encoding="utf-8"))
    context = _Context(
        checklist=checklist,
        contract=contract,
        seen=set(),
        problems=problems,
    )
    for block in checklist_items(text):
        _check_requirement(block, context)


def _data_cell(parts: list[str]) -> str | None:
    """Return the first table cell when it is data rather than a rule marker."""
    if not parts or not parts[0]:
        return None
    if set(parts[0]) <= {"-", ":"}:
        return None
    return parts[0]


def first_cells(text: str) -> set[str]:
    """Return the first cell of every data row in the text's Markdown tables."""
    cells: set[str] = set()
    for line in strip_code_and_comments(text).splitlines():
        if not line.startswith("|"):
            continue
        parts = [part.strip().strip("*").strip() for part in line.strip("|").split("|")]
        cell = _data_cell(parts)
        if cell is not None:
            cells.add(cell)
    return cells


def section(text: str, heading: str) -> str:
    """Return the lines of the level-two section whose anchor is ``heading``."""
    kept: list[str] = []
    active = False
    for line in text.splitlines():
        if line.startswith("## "):
            active = slug(line[3:]) == heading
            continue
        if active:
            kept.append(line)
    return "\n".join(kept)


def check_states(book: Path, contract: Contract, problems: list[str]) -> None:
    """Check that every declared live and resolution state leads a state table."""
    spec = contract.states
    for group, owner_key, heading in (
        ("live", "live_owner", "the-five-states"),
        (
            "resolution",
            "resolution_owner",
            "resolution-authority-and-cache-are-independent",
        ),
    ):
        owner = book / spec[owner_key]
        text = strip_fences_and_comments(owner.read_text(encoding="utf-8"))
        cells = first_cells(section(text, heading))
        problems.extend(
            f"{owner.name}: {group} state {state!r} is not declared in its state table"
            for state in spec[group]
            if state not in cells
        )


def check_profiles(book: Path, contract: Contract, problems: list[str]) -> None:
    """Check that each conformance profile is declared in its owning file."""
    spec = contract.profiles
    owner = book / spec["owner"]
    text = strip_code_and_comments(owner.read_text(encoding="utf-8"))
    problems.extend(
        f"{owner.name}: profile {name!r} is not declared"
        for name in spec["names"]
        if name not in text
    )


def _references_path(path: Path, owner: Path) -> bool:
    """Return whether a chapter links to a contract owner file."""
    resolved_owner = owner.resolve()
    return any(
        resolved_destination(path.parent, target) == resolved_owner
        for target in link_targets(path.read_text(encoding="utf-8"))
    )


def check_commands(book: Path, contract: Contract, problems: list[str]) -> None:
    """Check that every command view references the command record owner."""
    spec = contract.commands
    owner = book / spec["record_owner"]
    if not owner.exists():
        problems.append(f"command record owner {owner.name} is missing")
        return
    for view in spec["views"]:
        path = book / view
        if not path.exists():
            problems.append(f"command view {view} is missing")
            continue
        if not _references_path(path, owner):
            problems.append(f"{view}: does not reference the command record owner")


def check_resources(book: Path, contract: Contract, problems: list[str]) -> None:
    """Check that every resource consumer references the resource owner."""
    spec = contract.resources
    owner = book / spec["owner"]
    if not owner.exists():
        problems.append(f"resource owner {owner.name} is missing")
        return
    for consumer in spec["consumers"]:
        path = book / consumer
        if not path.exists():
            problems.append(f"resource consumer {consumer} is missing")
            continue
        if not _references_path(path, owner):
            problems.append(f"{consumer}: does not reference the resource owner")
