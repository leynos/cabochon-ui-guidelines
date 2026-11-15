"""Figure generator module: shared tool-strip glyphs.

Every tool strip draws the same select, pen, line, rectangle, ellipse and text
symbols, so the geometry lives here once. A strip chooses the glyph sequence and
the offsets; it never redraws the symbol.
"""

from __future__ import annotations

import typing as typ

if typ.TYPE_CHECKING:
    from collections import abc as cabc

from figuregen.canvas import ellipse, line, path, rect, txt

# The drawing primitives take geometry and style arguments positionally; see
# the matching ruff exemption for tools/figuregen in pyproject.toml.
# pylint: disable=too-many-arguments


def _select(cx: float, cy: float, colour: str) -> str:
    """Draw the selection tool glyph."""
    return path(
        f"M {cx - 5} {cy - 7} L {cx + 3} {cy + 4} L {cx - 1} {cy + 4} L {cx + 1} {cy + 10} L {cx - 3} {cy + 11} L {cx - 5} {cy + 5} L {cx - 8} {cy + 8} Z",
        stroke=colour,
        sw=1.4,
    )


def _pen(cx: float, cy: float, colour: str) -> str:
    """Draw the pen tool glyph."""
    return path(
        f"M {cx - 6} {cy + 7} L {cx - 4} {cy} L {cx + 5} {cy - 9} L {cx + 9} {cy - 5} L {cx} {cy + 4} Z",
        stroke=colour,
        sw=1.4,
    )


def _line(cx: float, cy: float, colour: str) -> str:
    """Draw the line tool glyph."""
    return line(cx - 7, cy + 7, cx + 7, cy - 7, stroke=colour, sw=2)


def _rectangle(cx: float, cy: float, colour: str) -> str:
    """Draw the rectangle tool glyph."""
    return rect(cx - 7, cy - 5, 14, 10, fill="none", stroke=colour, sw=1.4)


def _ellipse(cx: float, cy: float, colour: str) -> str:
    """Draw the ellipse tool glyph."""
    return ellipse(cx, cy, 8, 6, fill="none", stroke=colour, sw=1.4)


def _link(cx: float, cy: float, colour: str) -> str:
    """Draw the link tool glyph."""
    return path(
        f"M {cx - 6} {cy + 4} L {cx - 8} {cy + 6} M {cx + 6} {cy - 4} L {cx + 8} {cy - 6} M {cx - 7} {cy + 2} L {cx + 7} {cy - 2}",
        stroke=colour,
        sw=1.4,
    )


_SHAPES: dict[str, cabc.Callable[[float, float, str], str]] = {
    "select": _select,
    "pen": _pen,
    "line": _line,
    "rect": _rectangle,
    "ellipse": _ellipse,
    "link": _link,
}


def tool_glyph(
    kind: str, cx: float, cy: float, colour: str, *, text_size: float = 14
) -> str:
    """Draw the tool glyph for ``kind`` centred on ``cx`` and ``cy``.

    The text tool is the only glyph whose size a strip varies, so it takes an
    explicit ``text_size``. An unknown glyph is a generation failure.
    """
    if kind == "text":
        return txt(
            cx, cy + 5, "T", size=text_size, fill=colour, weight="bold", anchor="middle"
        )
    shape = _SHAPES.get(kind)
    if shape is None:
        raise ValueError(f"unknown tool glyph {kind!r}")
    return shape(cx, cy, colour)
