"""Tests for the figure checker's geometry measurements.

`path_bbox` must ignore the points of a subpath that draws no segment, and
`paint_visible` must resolve inline styles and inherited presentation values so
that a mark painted with nothing visible is reported rather than trusted.
"""

from __future__ import annotations

# The tests build their own elements; they never parse external XML.
from xml.etree import ElementTree  # ruff: ignore[suspicious-xml-etree-import]

import pytest
from figurecheck.geometry import GeometryError, paint_visible, path_bbox

Parents = dict[ElementTree.Element, ElementTree.Element]


def _parents(root: ElementTree.Element) -> Parents:
    """Return the parent of every element in a tree."""
    return {child: parent for parent in root.iter() for child in parent}


def test_mixed_path_ignores_move_only_subpath() -> None:
    """A trailing move-only subpath contributes nothing to the bounds."""
    assert path_bbox("M 0 0 L 1 1 M 20 20") == (0.0, 0.0, 1.0, 1.0), (
        "only the drawn segment bounds the path"
    )


def test_move_only_path_has_no_segments() -> None:
    """A path that only moves draws no segment at all."""
    with pytest.raises(GeometryError, match="path draws no segments"):
        path_bbox("M 0 0 M 20 20")


def test_inline_style_zero_stroke_width_hides_line() -> None:
    """An inline style outranks the element's own stroke-width attribute."""
    line = ElementTree.Element(
        "line",
        {
            "x1": "0",
            "y1": "0",
            "x2": "1",
            "y2": "1",
            "stroke": "#000000",
            "stroke-width": "1",
            "style": "stroke-width:0",
        },
    )
    assert not paint_visible(line, {}), (
        "an inline zero stroke width hides the line"
    )


def test_ancestor_zero_stroke_width_hides_line() -> None:
    """A zero stroke width on the ancestor hides a stroked child."""
    group = ElementTree.Element("g", {"stroke-width": "0"})
    line = ElementTree.Element(
        "line", {"x1": "0", "y1": "0", "x2": "1", "y2": "1", "stroke": "#000000"}
    )
    group.append(line)
    assert not paint_visible(line, _parents(group)), (
        "an inherited zero stroke width hides the line"
    )


def test_ancestor_inline_style_hides_line() -> None:
    """An inline style on an ancestor carries into its descendants."""
    group = ElementTree.Element("g", {"stroke-width": "1", "style": "stroke-width:0"})
    line = ElementTree.Element(
        "line", {"x1": "0", "y1": "0", "x2": "1", "y2": "1", "stroke": "#000000"}
    )
    group.append(line)
    assert not paint_visible(line, _parents(group)), (
        "an ancestor's inline zero stroke width hides the line"
    )


def test_visible_paint_is_reported() -> None:
    """A stroked line and a filled rectangle both paint visibly."""
    root = ElementTree.Element("svg")
    line = ElementTree.Element(
        "line",
        {
            "x1": "0",
            "y1": "0",
            "x2": "1",
            "y2": "1",
            "stroke": "#000000",
            "stroke-width": "1",
        },
    )
    rect = ElementTree.Element(
        "rect", {"x": "0", "y": "0", "width": "1", "height": "1", "fill": "#000000"}
    )
    root.extend([line, rect])
    parents = _parents(root)
    assert paint_visible(line, parents), "a stroked line paints visibly"
    assert paint_visible(rect, parents), "a filled rectangle paints visibly"
