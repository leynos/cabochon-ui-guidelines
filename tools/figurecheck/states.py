"""Verify the live-state inventory and the marks each figure draws.

The `check_states` function matches each figure's labels and mark groups
against `STATE_RECORDS` from `tools/figure-data.json` and checks the declared
inventory. `figurecheck.checks` calls it, and it in turn uses
`figurecheck.marks`.
"""

from __future__ import annotations

import typing as typ
from collections import Counter

from figurecheck.contract import STATE_RECORDS, SVG_NS, GeometryError
from figurecheck.geometry import (
    clip_used,
    hidden_reason,
    local_name,
    rendered_bbox,
    viewbox,
)
from figurecheck.marks import mark_is_drawn

if typ.TYPE_CHECKING:
    from xml.etree import ElementTree

VIEWBOX_TOLERANCE = 0.01


class _Figure(typ.NamedTuple):
    """The parsed figure under check and its accumulated report."""

    name: str
    root: ElementTree.Element
    parents: dict[ElementTree.Element, ElementTree.Element]
    errors: list[str]


def _state_texts(root: ElementTree.Element) -> list[ElementTree.Element]:
    """Return the labels that name a live state."""
    return [
        element
        for element in root.iter(f"{SVG_NS}text")
        if element.get("data-state") is not None
    ]


def _card(
    element: ElementTree.Element,
    parents: dict[ElementTree.Element, ElementTree.Element],
) -> ElementTree.Element | None:
    """Return the group that holds a state label, or ``None``."""
    ancestor = parents.get(element)
    while ancestor is not None and local_name(ancestor) != "g":
        ancestor = parents.get(ancestor)
    return ancestor


def _check_label(
    figure: _Figure, element: ElementTree.Element, record: dict[str, str]
) -> None:
    """Check a state label's word and colour against the record."""
    identifier = element.get("data-state") or ""
    label = (element.text or "").strip()
    if label.upper() != record["word"]:
        figure.errors.append(
            f"{figure.name}: state {identifier!r} label {label!r} disagrees with "
            f"record {record['word']!r}"
        )
    fill = (element.get("fill") or "").upper()
    if fill != record["colour"]:
        figure.errors.append(
            f"{figure.name}: state {identifier!r} drawn in {fill or 'no fill'}, "
            f"record declares {record['colour']}"
        )
    reason = hidden_reason(element, figure.parents)
    if reason is not None:
        figure.errors.append(
            f"{figure.name}: state {identifier!r} label is not visible ({reason})"
        )


def _contained(box: tuple[float, ...], view: tuple[float, ...]) -> bool:
    """Return whether a box lies inside the view box within tolerance."""
    return all(
        box[index] >= view[index] - VIEWBOX_TOLERANCE
        and box[index + 2] <= view[index + 2] + VIEWBOX_TOLERANCE
        for index in (0, 1)
    )


def _check_mark_geometry(
    figure: _Figure, group: ElementTree.Element, identifier: str
) -> None:
    """Check that a state mark is visible and inside the view box."""
    if any(clip_used(element, figure.parents) for element in group.iter()):
        figure.errors.append(
            f"{figure.name}: state {identifier!r} mark uses clipping, which the "
            "constrained subset forbids"
        )
        return
    reason = hidden_reason(group, figure.parents)
    if reason is not None:
        figure.errors.append(
            f"{figure.name}: state {identifier!r} mark is not visible ({reason})"
        )
        return
    try:
        box = rendered_bbox(group, figure.parents, f"state {identifier!r} mark")
    except GeometryError as exc:
        figure.errors.append(
            f"{figure.name}: state {identifier!r} mark is invalid: {exc}"
        )
        return
    if not _contained(box, viewbox(figure.root)):
        figure.errors.append(
            f"{figure.name}: state {identifier!r} mark is clipped by the viewBox"
        )


def _check_mark(
    figure: _Figure,
    group: ElementTree.Element,
    identifier: str,
    record: dict[str, str],
) -> None:
    """Check that a state mark matches its record and draws that mark."""
    if group.get("data-state-id") != identifier:
        figure.errors.append(
            f"{figure.name}: state {identifier!r} mark identity "
            f"{group.get('data-state-id')!r} disagrees with record"
        )
    if group.get("data-role") != record["role"]:
        figure.errors.append(
            f"{figure.name}: state {identifier!r} mark role "
            f"{group.get('data-role')!r} disagrees with record {record['role']!r}"
        )
    drawn = group.get("data-mark") or ""
    if drawn != record["mark"]:
        figure.errors.append(
            f"{figure.name}: state {identifier!r} drawn with mark {drawn!r}, "
            f"record declares {record['mark']!r}"
        )
    if not mark_is_drawn(group, drawn, record["colour"]):
        figure.errors.append(
            f"{figure.name}: state {identifier!r} declares mark {drawn!r} "
            "but does not draw it"
        )
    _check_mark_geometry(figure, group, identifier)


def _check_card(
    figure: _Figure,
    element: ElementTree.Element,
    identifier: str,
    record: dict[str, str],
) -> None:
    """Check that a state's card holds one label and one mark."""
    ancestor = _card(element, figure.parents)
    if ancestor is None:
        figure.errors.append(
            f"{figure.name}: state {identifier!r} is not inside a group"
        )
        return
    labels = _state_texts(ancestor)
    if len(labels) != 1:
        figure.errors.append(
            f"{figure.name}: state card {identifier!r} contains "
            f"{len(labels)} state labels"
        )
    groups = [item for item in ancestor.iter() if item.get("data-mark") is not None]
    if not groups:
        figure.errors.append(
            f"{figure.name}: state {identifier!r} has no declared mark"
        )
        return
    if len(groups) != 1:
        figure.errors.append(
            f"{figure.name}: state {identifier!r} has {len(groups)} mark groups"
        )
        return
    _check_mark(figure, groups[0], identifier, record)


def _check_inventory(
    figure: _Figure, spec: dict[str, object], counts: Counter[str]
) -> None:
    """Check that the drawn states match the declared inventory."""
    expected = spec.get("states")
    if not isinstance(expected, dict):
        figure.errors.append(f"{figure.name}: missing state inventory")
        return
    for identifier, count in expected.items():
        if identifier not in STATE_RECORDS:
            figure.errors.append(
                f"{figure.name}: inventory names unknown state {identifier!r}"
            )
            continue
        actual = counts.get(identifier, 0)
        if actual != count:
            figure.errors.append(
                f"{figure.name}: state inventory expects {count} of {identifier!r}, "
                f"found {actual}"
            )
    for identifier, actual in counts.items():
        if identifier not in expected:
            figure.errors.append(
                f"{figure.name}: state {identifier!r} is drawn {actual} time(s) but "
                "is absent from the inventory"
            )


def check_states(
    name: str, root: ElementTree.Element, spec: dict[str, object]
) -> list[str]:
    """Check that every figure carries the declared state marks."""
    parents = {child: parent for parent in root.iter() for child in parent}
    figure = _Figure(name=name, root=root, parents=parents, errors=[])
    counts: Counter[str] = Counter()
    for element in _state_texts(root):
        identifier = element.get("data-state") or ""
        counts[identifier] += 1
        record = STATE_RECORDS.get(identifier)
        if record is None:
            figure.errors.append(
                f"{name}: unknown state identity {identifier!r}"
            )
            continue
        _check_label(figure, element, record)
        _check_card(figure, element, identifier, record)
    _check_inventory(figure, spec, counts)
    return figure.errors
