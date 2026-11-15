"""Verify that a state mark draws the primitive its record claims.

The `mark_is_drawn` function maps a declared mark kind such as `dot` or `lock`
to the filled, stroked or linear primitives it requires. `figurecheck.states`
imports it to check each state mark group.
"""

from __future__ import annotations

import typing as typ

from figurecheck.geometry import local_name

if typ.TYPE_CHECKING:
    import collections.abc as cabc
    from xml.etree import ElementTree


class _Drawing(typ.NamedTuple):
    """The primitives a mark group offers, filtered by how they paint."""

    children: list[ElementTree.Element]
    filled: list[ElementTree.Element]
    stroked: list[ElementTree.Element]
    lines: list[ElementTree.Element]


def _has(tag: str, elements: list[ElementTree.Element]) -> bool:
    """Return whether any listed element carries the tag."""
    return any(local_name(element) == tag for element in elements)


def _dot(drawing: _Drawing) -> bool:
    """Check that a filled circle draws the dot mark."""
    return _has("circle", drawing.filled)


def _arc(drawing: _Drawing) -> bool:
    """Check that a stroked path draws the arc mark."""
    return _has("path", drawing.stroked)


def _triangle(drawing: _Drawing) -> bool:
    """Check that a filled path draws the triangle mark."""
    return _has("path", drawing.filled)


def _broken(drawing: _Drawing) -> bool:
    """Check that two or more lines draw the broken mark."""
    return len(drawing.lines) >= 2


def _lock(drawing: _Drawing) -> bool:
    """Check that a filled rectangle and stroked path draw the lock mark."""
    return _has("rect", drawing.filled) and _has("path", drawing.stroked)


def _hatch(drawing: _Drawing) -> bool:
    """Check that a stroked rectangle and three lines draw the hatch mark."""
    return _has("rect", drawing.stroked) and len(drawing.lines) >= 3


def _dashed(drawing: _Drawing) -> bool:
    """Check that a dashed rectangle draws the dashed mark."""
    return any(
        local_name(child) == "rect" and child.get("stroke-dasharray")
        for child in drawing.children
    )


def _crossed(drawing: _Drawing) -> bool:
    """Check that a stroked rectangle and two lines draw the crossed mark."""
    return _has("rect", drawing.stroked) and len(drawing.lines) == 2


_MARK_CHECKS: dict[str, cabc.Callable[[_Drawing], bool]] = {
    "dot": _dot,
    "arc": _arc,
    "triangle": _triangle,
    "broken": _broken,
    "lock": _lock,
    "hatch": _hatch,
    "dashed": _dashed,
    "crossed": _crossed,
}


def mark_is_drawn(group: ElementTree.Element, kind: str, colour: str) -> bool:
    """Check that the mark group contains the primitive its record claims."""
    colour = colour.upper()
    children = list(group)
    drawing = _Drawing(
        children=children,
        filled=[
            child for child in children if (child.get("fill") or "").upper() == colour
        ],
        stroked=[
            child for child in children if (child.get("stroke") or "").upper() == colour
        ],
        lines=[child for child in children if local_name(child) == "line"],
    )
    check = _MARK_CHECKS.get(kind)
    return check is not None and check(drawing)
