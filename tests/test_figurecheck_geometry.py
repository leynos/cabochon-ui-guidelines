"""Tests for the figure checker's geometry measurements.

`path_bbox` must ignore the points of a subpath that draws no segment, and
`paint_visible` must resolve inline styles and inherited presentation values so
that a mark painted with nothing visible is reported rather than trusted.
`parse_transform`, `compose` and `viewbox` decide the frame a mark is measured
in, so their orderings and bounds are pinned here.
"""

from __future__ import annotations

# The tests build their own elements; they never parse external XML.
from xml.etree import ElementTree  # ruff: ignore[suspicious-xml-etree-import]

import pytest
from figurecheck.geometry import (
    GeometryError,
    apply_matrix,
    compose,
    paint_visible,
    parse_transform,
    path_bbox,
    viewbox,
)

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


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("translate(3, 4)", (1.0, 0.0, 0.0, 1.0, 3.0, 4.0)),
        ("translate(5)", (1.0, 0.0, 0.0, 1.0, 5.0, 0.0)),
        ("scale(2)", (2.0, 0.0, 0.0, 2.0, 0.0, 0.0)),
        ("scale(2, 3)", (2.0, 0.0, 0.0, 3.0, 0.0, 0.0)),
        ("matrix(1 2 3 4 5 6)", (1.0, 2.0, 3.0, 4.0, 5.0, 6.0)),
    ],
    ids=["translate-pair", "translate-one", "scale-one", "scale-pair", "matrix"],
)
def test_parse_transform_returns_the_stated_matrix(
    value: str, expected: tuple[float, ...]
) -> None:
    """Each single operation parses to the matrix the SVG transform defines."""
    assert parse_transform(value) == expected, "the operation's matrix is exact"


def test_compose_applies_the_inner_matrix_first() -> None:
    """Composition scales before it translates, never the other way round."""
    outer = (1.0, 0.0, 0.0, 1.0, 10.0, 0.0)
    inner = (2.0, 0.0, 0.0, 2.0, 0.0, 0.0)
    assert compose(outer, inner) == (2.0, 0.0, 0.0, 2.0, 10.0, 0.0), (
        "the composed matrix keeps the inner scale and the outer translation"
    )
    assert apply_matrix(parse_transform("translate(10, 0) scale(2)"), 1, 1) == (
        12.0,
        2.0,
    ), "a left-to-right list scales the point before it translates it"
    assert apply_matrix(parse_transform("scale(2) translate(10, 0)"), 1, 1) == (
        22.0,
        2.0,
    ), "the reversed list translates before it scales"


def test_viewbox_prefers_the_declared_attribute() -> None:
    """A declared view box becomes its corner and opposite corner."""
    root = ElementTree.Element("svg", {"viewBox": "10 20 100 50"})
    assert viewbox(root) == (10.0, 20.0, 110.0, 70.0), (
        "the view box is reported as x, y, x + width, y + height"
    )


def test_viewbox_falls_back_to_the_canvas_size() -> None:
    """Without a view box the canvas starts at the origin and spans its size."""
    root = ElementTree.Element("svg", {"width": "120", "height": "80"})
    assert viewbox(root) == (0.0, 0.0, 120.0, 80.0), (
        "the fallback bounds are the declared width and height"
    )
