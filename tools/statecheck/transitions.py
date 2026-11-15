"""Check the declared transitions against the chapter table and the figure.

The `validate_transitions`, `compare_chapter` and `compare_figure` functions
check `tools/figure-data.json` against `book/08-live-relationships.md` and
`figures/fig-06-state.svg`. `statecheck.cli` and `statecheck.selftest` import
them.
"""

from __future__ import annotations

import re
from xml.etree import ElementTree

from statecheck.contract import (
    CHAPTER,
    EDGE_ID,
    FIGURE,
    FROM_TOKENS,
    STATES,
    SVG_NS,
    TARGETS,
    LiveTransition,
)


def _check_identifier(
    record: LiveTransition, seen: set[str], errors: list[str]
) -> str:
    """Check that a state declares its identifier."""
    identifier = str(record.get("id", ""))
    if not EDGE_ID.match(identifier):
        errors.append(f"transition {identifier!r}: id is not kebab-case")
    if identifier in seen:
        errors.append(f"transition {identifier!r}: duplicate id")
    seen.add(identifier)
    return identifier


def _check_sources(record: LiveTransition, errors: list[str]) -> None:
    """Check that a transition declares its source states."""
    identifier = str(record.get("id", ""))
    sources = record.get("from")
    if not isinstance(sources, list) or not sources:
        errors.append(f"transition {identifier!r}: no source states")
        return
    errors.extend(
        f"transition {identifier!r}: unknown source {source!r}"
        for source in sources
        if source not in FROM_TOKENS
    )


def _check_target_and_text(record: LiveTransition, errors: list[str]) -> None:
    """Check that a transition declares a target and a trigger."""
    identifier = str(record.get("id", ""))
    if record.get("to") not in TARGETS:
        target = record.get("to")
        errors.append(f"transition {identifier!r}: unknown target {target!r}")
    if not str(record.get("owner", "")).strip():
        errors.append(f"transition {identifier!r}: no owner")
    if not str(record.get("event", "")).strip():
        errors.append(f"transition {identifier!r}: no event")


def _has_edge(
    transitions: list[LiveTransition],
    target: str,
    source: str,
    event_fragment: str = "",
) -> bool:
    """Return whether the declared transitions contain an edge."""
    return any(
        record.get("to") == target
        and source in record.get("from", [])
        and event_fragment in record.get("event", "")
        for record in transitions
    )


def _check_state_coverage(
    transitions: list[LiveTransition], errors: list[str]
) -> None:
    """Check that every live state appears in a transition."""
    targets = {record.get("to") for record in transitions}
    errors.extend(
        f"state {state!r} is not the target of any transition"
        for state in sorted(STATES - targets)
    )


def _check_special_edges(
    transitions: list[LiveTransition], errors: list[str]
) -> None:
    """Check that the mandatory special transitions are declared."""
    if not _has_edge(transitions, "Denied", "Any state"):
        errors.append("revocation is not available from every state")
    if not _has_edge(transitions, "Broken", "Any state except Denied"):
        errors.append("provider loss is not available from every state but Denied")
    if not _has_edge(transitions, "Broken", "Denied", "provider is absent"):
        errors.append("a grant issued while the provider is absent is not modelled")


def validate_transitions(transitions: list[LiveTransition]) -> list[str]:
    """Check that the typed transition source is complete and well formed."""
    errors: list[str] = []
    seen: set[str] = set()
    for record in transitions:
        _check_identifier(record, seen, errors)
        _check_sources(record, errors)
        _check_target_and_text(record, errors)
    _check_state_coverage(transitions, errors)
    _check_special_edges(transitions, errors)
    return errors


def chapter_rows() -> list[tuple[str, str, str, str]]:
    """Read the transition table under the chapter's Transitions heading."""
    text = CHAPTER.read_text(encoding="utf-8")
    match = re.search(
        r"^## Transitions\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL
    )
    if match is None:
        raise SystemExit("state contract: chapter 08 has no Transitions section")
    rows: list[tuple[str, str, str, str]] = []
    for raw in match.group(1).splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 4:
            continue
        if cells[0] in {"From", "-------"} or set(cells[0]) <= {"-"}:
            continue
        if all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        rows.append((cells[0], cells[1], cells[2], cells[3]))
    return rows


def compare_chapter(transitions: list[LiveTransition]) -> list[str]:
    """Compare the typed transitions with the chapter's table."""
    errors: list[str] = []
    declared = [
        (
            ", ".join(record["from"]),
            record["event"],
            record["to"],
            record["owner"],
        )
        for record in transitions
    ]
    actual = chapter_rows()
    errors.extend(
        f"chapter 08 is missing transition {row!r}"
        for row in sorted(set(declared) - set(actual))
    )
    errors.extend(
        f"chapter 08 declares unknown transition {row!r}"
        for row in sorted(set(actual) - set(declared))
    )
    if len(actual) != len(declared):
        errors.append(
            f"chapter 08 lists {len(actual)} transitions, "
            f"the typed source has {len(declared)}"
        )
    return errors


def _transition_groups(
    root: ElementTree.Element,
) -> dict[str, list[ElementTree.Element]]:
    """Index the figure's annotated transition rows by identifier."""
    groups: dict[str, list[ElementTree.Element]] = {}
    for element in root.iter(f"{SVG_NS}g"):
        identifier = element.get("data-transition-id")
        if identifier is not None:
            groups.setdefault(identifier, []).append(element)
    return groups


def _row_labels(group: ElementTree.Element) -> set[str]:
    """Return the text labels rendered inside one transition row."""
    return {
        (element.text or "").strip() for element in group.iter(f"{SVG_NS}text")
    }


def _check_figure_row(
    record: LiveTransition,
    groups: dict[str, list[ElementTree.Element]],
    errors: list[str],
) -> None:
    """Check one transition against the row annotated with its identifier."""
    identifier = record["id"]
    elements = groups.get(identifier, [])
    if not elements:
        errors.append(f"figure does not render transition {identifier!r}")
        return
    if len(elements) > 1:
        errors.append(f"figure renders transition {identifier!r} more than once")
        return
    labels = _row_labels(elements[0])
    source = ", ".join(record["from"])
    for field, value in (
        ("event", record["event"]),
        ("to", record["to"]),
        ("owner", record["owner"]),
    ):
        if value not in labels:
            errors.append(
                f"figure does not render {field} of {identifier!r} "
                f"in its row: {value!r}"
            )
    if source not in labels:
        errors.append(
            f"figure does not render source of {identifier!r} "
            f"in its row: {source!r}"
        )


def compare_figure(transitions: list[LiveTransition]) -> list[str]:
    """Check that the rendered state figure labels every transition field."""
    errors: list[str] = []
    if not FIGURE.exists():
        return [f"{FIGURE.name} does not exist; run make figures"]
    root = ElementTree.parse(FIGURE).getroot()
    groups = _transition_groups(root)
    for record in transitions:
        _check_figure_row(record, groups, errors)
    declared = {record["id"] for record in transitions}
    errors.extend(
        f"figure renders unknown transition {identifier!r}"
        for identifier in sorted(set(groups) - declared)
    )
    return errors
