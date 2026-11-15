"""Draw the Burin Draw window figure.

The window shows a canvas with a tool palette, rulers, guides and an object
inspector. The exported `fig_draw` function returns the SVG string, drawn from
the shared `figuregen.palette` colours. `figuregen.cli` calls it to write
`fig-23-draw.svg` under `figures/`.
"""

from __future__ import annotations

from figuregen.canvas import ellipse, line, path, rect, svg_doc, txt
from figuregen.ornaments import title_block
from figuregen.palette import (
    F_MONO,
    HIGH,
    INK,
    LINE,
    OXIDE,
    PAPER,
    PINE2,
    SOFT,
    TEAL,
    WHITE,
)
from figuregen.widgets import checkbox, inspector_row, pane_head, window_shell


def _tool_select(cx: float, cy: float, colour: str) -> str:
    """Draw the selection tool glyph."""
    return path(
        f"M {cx - 6} {cy - 8} L {cx + 4} {cy + 5} L {cx - 1} {cy + 5} L {cx + 1} {cy + 11} L {cx - 3} {cy + 12} L {cx - 5} {cy + 6} L {cx - 9} {cy + 9} Z",
        stroke=colour,
        sw=1.5,
    )


def _tool_pen(cx: float, cy: float, colour: str) -> str:
    """Draw the pen tool glyph."""
    return path(
        f"M {cx - 7} {cy + 8} L {cx - 5} {cy} L {cx + 5} {cy - 10} L {cx + 9} {cy - 6} L {cx} {cy + 4} Z",
        stroke=colour,
        sw=1.5,
    )


def _tool_line(cx: float, cy: float, colour: str) -> str:
    """Draw the line tool glyph."""
    return line(cx - 7, cy + 7, cx + 7, cy - 7, stroke=colour, sw=2)


def _tool_rect(cx: float, cy: float, colour: str) -> str:
    """Draw the rectangle tool glyph."""
    return rect(cx - 8, cy - 6, 16, 12, fill="none", stroke=colour, sw=1.5)


def _tool_ellipse(cx: float, cy: float, colour: str) -> str:
    """Draw the ellipse tool glyph."""
    return ellipse(cx, cy, 9, 7, fill="none", stroke=colour, sw=1.5)


def _tool_text(cx: float, cy: float, colour: str) -> str:
    """Draw the text tool glyph."""
    return txt(cx, cy + 6, "T", size=15, fill=colour, weight="bold", anchor="middle")


def _tool_hand(cx: float, cy: float, colour: str) -> str:
    """Draw the hand tool glyph."""
    return path(
        f"M {cx - 6} {cy + 6} V {cy - 8} M {cx - 2} {cy + 6} V {cy - 8} M {cx + 2} {cy + 6} V {cy - 8} M {cx + 6} {cy + 6} V {cy - 8}",
        stroke=colour,
        sw=1.4,
    )


_TOOLS = {
    "select": _tool_select,
    "pen": _tool_pen,
    "line": _tool_line,
    "rect": _tool_rect,
    "ellipse": _tool_ellipse,
    "text": _tool_text,
    "hand": _tool_hand,
}


def _tool_palette(x: float, y: float, w: float, h: float) -> str:
    """Draw the tool palette with its active tool."""
    palette_w = 48
    body = rect(x, y + 60, palette_w, h - 86, fill=PAPER, stroke=None)
    body += line(x + palette_w, y + 60, x + palette_w, y + h - 26, stroke=INK)
    for index, glyph in enumerate([
        "select",
        "pen",
        "line",
        "rect",
        "ellipse",
        "text",
        "hand",
    ]):
        bx, by = x + 8, y + 72 + index * 40
        active = index == 1
        body += rect(bx, by, 32, 32, fill=PINE2 if active else HIGH, stroke=LINE)
        colour = WHITE if active else INK
        body += _TOOLS[glyph](bx + 16, by + 16, colour)
    return body


def _canvas(cx0: float, cy0: float, cw: int, ch: int) -> str:
    """Draw the canvas, rulers, guides and the selected object."""
    body = rect(cx0, cy0, cw, ch, fill=WHITE, stroke=INK)
    for index in range(0, cw, 50):
        body += line(cx0 + index, cy0 - 20, cx0 + index, cy0, stroke=LINE)
        body += txt(
            cx0 + index,
            cy0 - 26,
            str(index),
            size=9,
            fill=SOFT,
            family=F_MONO,
            anchor="middle",
        )
    for index in range(0, ch, 50):
        body += line(cx0 - 20, cy0 + index, cx0, cy0 + index, stroke=LINE)
        body += txt(
            cx0 - 24,
            cy0 + index + 3,
            str(index),
            size=9,
            fill=SOFT,
            family=F_MONO,
            anchor="end",
        )
    for gx in (cx0 + 150, cx0 + 400):
        body += line(gx, cy0, gx, cy0 + ch, stroke=TEAL, sw=1, dash="4 5")
    for gy in (cy0 + 120, cy0 + 360):
        body += line(cx0, gy, cx0 + cw, gy, stroke=TEAL, sw=1, dash="4 5")
    body += rect(cx0 + 150, cy0 + 120, 250, 240, fill="none", stroke=INK, sw=1.5)
    body += ellipse(cx0 + 275, cy0 + 240, 80, 54, fill=HIGH, stroke=PINE2, sw=2)
    body += txt(
        cx0 + 275,
        cy0 + 246,
        "GBP",
        size=18,
        fill=PINE2,
        family=F_MONO,
        weight="bold",
        anchor="middle",
    )
    body += path(
        f"M {cx0 + 150} {cy0 + 340} C {cx0 + 220} {cy0 + 260}, {cx0 + 330} {cy0 + 420}, {cx0 + 400} {cy0 + 300}",
        stroke=OXIDE,
        sw=2,
    )
    for hx, hy in [
        (cx0 + 150, cy0 + 120),
        (cx0 + 400, cy0 + 120),
        (cx0 + 150, cy0 + 360),
        (cx0 + 400, cy0 + 360),
    ]:
        body += rect(hx - 4, hy - 4, 8, 8, fill=WHITE, stroke=OXIDE)
    return body


def _inspector(ix: float, y: float, width: float) -> str:
    """Draw the object inspector."""
    body = pane_head(ix, y + 60, width, "Inspector")
    body += txt(ix + 10, y + 108, "Currency plate", size=12, weight="bold")
    body += txt(
        ix + 10, y + 124, "Group · 14 objects", size=10, fill=SOFT, family=F_MONO
    )
    body += inspector_row(ix + 10, y + 152, 220, "Size", value="240 × 180 mm")
    body += inspector_row(ix + 10, y + 176, 220, "Position", value="24, 42 mm")
    body += inspector_row(ix + 10, y + 200, 220, "Rotation", value="0°")
    body += txt(
        ix + 10,
        y + 232,
        "FILL",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=0.6,
    )
    body += rect(ix + 10, y + 244, 24, 24, fill=HIGH, stroke=INK)
    body += txt(ix + 42, y + 261, "Paper", size=11, fill=INK)
    body += txt(
        ix + 10,
        y + 288,
        "STROKE",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=0.6,
    )
    body += rect(ix + 10, y + 300, 24, 24, fill=INK, stroke=INK)
    body += txt(ix + 42, y + 317, "Ink · 2 px", size=11, fill=INK)
    body += txt(
        ix + 10,
        y + 350,
        "GUIDES",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=0.6,
    )
    body += checkbox(ix + 10, y + 374, "Show guides", checked=True)
    body += checkbox(ix + 10, y + 398, "Snap to grid", checked=True)
    return body + txt(
        ix + 10, y + 430, "Grid 16 px · guides teal", size=10, fill=SOFT, family=F_MONO
    )


def fig_draw() -> str:
    """Draw Burin Draw with rulers, guides and the tool palette."""
    body = title_block(
        64,
        70,
        "Burin Draw",
        "A drawing surface with rulers, guides and a compact tool palette. The canvas is the document, not a preview of one.",
    )
    x, y, w, h = 64, 150, 1072, 540
    body += window_shell(
        x,
        y,
        w,
        h,
        title="Burin Draw — Currency plate",
        menu=["File", "Edit", "View", "Object", "Tools", "Window", "Help"],
        status="Pen · 2 px · 14 objects · 100%",
        state="Current",
    )
    body += _tool_palette(x, y, w, h)
    cx0, cy0 = x + 48 + 28, y + 92
    cw, ch = 736, 414
    body += _canvas(cx0, cy0, cw, ch)
    ix = cx0 + cw + 20
    body += _inspector(ix, y, w - (ix - x))
    return svg_doc(
        1200,
        760,
        "Burin Draw with rulers, guides and tool palette",
        "A drawing window with a 48 pixel tool palette, rulers, teal guides, an object with selection handles, and an inspector.",
        body=body,
    )
