"""Figure generator module: figures.window."""

from __future__ import annotations

from figuregen.canvas import circle, line, para, path, rect, svg_doc, txt
from figuregen.ornaments import state_chip, title_block
from figuregen.palette import (
    F_DISPLAY,
    F_MONO,
    HIGH,
    INK,
    LINE,
    OXIDE,
    PAPER,
    PINE2,
    SOFT,
    WHITE,
)
from figuregen.widgets import checkbox, inspector_row, pane_head, window_shell


def _glyph_select(cx: float, cy: float, colour: str) -> str:
    """Draw the selection tool glyph."""
    return path(
        f"M {cx - 5} {cy - 7} L {cx + 3} {cy + 4} L {cx - 1} {cy + 4} L {cx + 1} {cy + 10} L {cx - 3} {cy + 11} L {cx - 5} {cy + 5} L {cx - 8} {cy + 8} Z",
        stroke=colour,
        sw=1.4,
    )


def _glyph_text(cx: float, cy: float, colour: str) -> str:
    """Draw the text tool glyph."""
    return txt(cx, cy + 5, "T", size=13, fill=colour, weight="bold", anchor="middle")


def _glyph_rect(cx: float, cy: float, colour: str) -> str:
    """Draw the rectangle tool glyph."""
    return rect(cx - 7, cy - 5, 14, 10, fill="none", stroke=colour, sw=1.4)


def _glyph_pen(cx: float, cy: float, colour: str) -> str:
    """Draw the pen tool glyph."""
    return path(
        f"M {cx - 6} {cy + 7} L {cx - 4} {cy} L {cx + 5} {cy - 9} L {cx + 9} {cy - 5} L {cx} {cy + 4} Z",
        stroke=colour,
        sw=1.4,
    )


def _glyph_link(cx: float, cy: float, colour: str) -> str:
    """Draw the link tool glyph."""
    return path(
        f"M {cx - 6} {cy + 4} L {cx - 8} {cy + 6} M {cx + 6} {cy - 4} L {cx + 8} {cy - 6} M {cx - 7} {cy + 2} L {cx + 7} {cy - 2}",
        stroke=colour,
        sw=1.4,
    )


_GLYPHS = {
    "select": _glyph_select,
    "text": _glyph_text,
    "rect": _glyph_rect,
    "pen": _glyph_pen,
    "link": _glyph_link,
}


def _tool_strip(x: float, y: float, w: float) -> str:
    """Draw the tool strip."""
    body = rect(x, y + 60, w, 30, fill=PAPER, stroke=None)
    body += line(x, y + 90, x + w, y + 90, stroke=LINE)
    for index, glyph in enumerate(["select", "text", "rect", "pen", "link"]):
        bx = x + 10 + index * 38
        active = index == 1
        body += rect(bx, y + 60, 30, 30, fill=PINE2 if active else HIGH, stroke=LINE)
        colour = WHITE if active else INK
        body += _GLYPHS[glyph](bx + 15, y + 75, colour)
    return body


def _tree_rows(x: float, y: float, tree_w: float) -> str:
    """Draw the note tree rows."""
    body = ""
    rows = [
        ("Project", 0, False),
        ("North Sea transition", 1, True),
        ("Sources", 1, False),
        ("Generation mix", 2, False),
        ("Currency", 2, False),
        ("Figures", 1, False),
    ]
    for index, (name, depth, selected) in enumerate(rows):
        ry = y + 120 + index * 28
        if selected:
            body += rect(x, ry - 18, tree_w, 26, fill=PINE2, stroke=None)
        body += txt(
            x + 12 + depth * 14, ry, name, size=11, fill=WHITE if selected else INK
        )
        if depth == 0:
            body += txt(
                x + tree_w - 14,
                ry,
                "▾",
                size=10,
                fill=WHITE if selected else SOFT,
                anchor="end",
            )
    return body


def _editor(y: float, splitter_1: float, splitter_2: float) -> str:
    """Draw the document pane."""
    width = splitter_2 - splitter_1
    body = pane_head(splitter_1, y + 90, width, "Document", right="Edited 14:02")
    ex = splitter_1 + 22
    body += txt(
        ex, y + 150, "North Sea transition", size=24, family=F_DISPLAY, style="italic"
    )
    body += para(
        ex,
        y + 180,
        width - 44,
        "The project note holds prose, a dataframe and a diagram without flattening any of them.",
        size=11,
        leading=16,
    )
    body += rect(ex, y + 230, width - 44, 74, fill=HIGH, stroke=LINE)
    body += txt(ex + 12, y + 252, "Generation mix", size=12, weight="bold")
    body += txt(
        ex + 12,
        y + 270,
        "Table · 12 rows · 4 columns",
        size=10,
        fill=SOFT,
        family=F_MONO,
    )
    state_body, _ = state_chip(splitter_2 - 100, y + 246, "Current")
    body += state_body
    body += rect(ex, y + 316, width - 44, 74, fill=HIGH, stroke=LINE)
    body += txt(ex + 12, y + 338, "Transition pathways", size=12, weight="bold")
    body += txt(
        ex + 12, y + 356, "Diagram · Mermaid source", size=10, fill=SOFT, family=F_MONO
    )
    state_body, _ = state_chip(splitter_2 - 100, y + 332, "Stale")
    body += state_body
    return body + para(
        ex,
        y + 424,
        width - 44,
        "Links remain links. A reader can open the source, change the presentation, or inspect the object behind it.",
        size=11,
        leading=16,
    )


def _inspector(y: float, splitter_2: float, inspector_w: float) -> str:
    """Draw the object inspector."""
    body = pane_head(splitter_2, y + 90, inspector_w, "Inspector")
    ix, iw = splitter_2 + 14, inspector_w - 28
    body += txt(ix, y + 132, "Generation mix", size=12, weight="bold")
    body += txt(ix, y + 148, "Table object", size=11, fill=SOFT)
    body += inspector_row(ix, y + 178, iw, "Object", value="obj:8f3a")
    body += inspector_row(ix, y + 204, iw, "Provider", value="enfilade.table")
    body += inspector_row(ix, y + 230, iw, "Revision", value="r17")
    body += txt(
        ix,
        y + 262,
        "PRESENTATION",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=0.6,
    )
    body += checkbox(ix, y + 286, "In note", checked=True)
    body += checkbox(ix, y + 308, "Dataframe", checked=True)
    body += checkbox(ix, y + 330, "Print table", checked=False)
    body += txt(
        ix,
        y + 362,
        "CAPABILITIES",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=0.6,
    )
    body += txt(ix, y + 384, "Read      granted", size=11, fill=PINE2, family=F_MONO)
    body += txt(ix, y + 402, "Write     granted", size=11, fill=PINE2, family=F_MONO)
    return body + txt(
        ix, y + 420, "Share     denied", size=11, fill=OXIDE, family=F_MONO
    )


def _callouts(x: float, y: float, w: float, h: float) -> str:
    """Draw the numbered callouts."""
    body = ""
    callouts = [
        (1, x - 22, y + 16, x, y + 16),
        (2, x - 22, y + 46, x, y + 46),
        (3, x - 22, y + 75, x, y + 75),
        (4, x - 22, y + 104, x, y + 104),
        (5, x + w + 22, y + 104, x + w, y + 104),
        (6, x - 22, y + h - 13, x, y + h - 13),
    ]
    for number, cx, cy, target_x, target_y in callouts:
        body += line(
            cx + (9 if cx < x else -9), cy, target_x, target_y, stroke=OXIDE, sw=1
        )
        body += circle(cx, cy, 9, fill=OXIDE, stroke=None)
        body += txt(
            cx,
            cy + 3.5,
            str(number),
            size=10,
            fill=WHITE,
            weight="bold",
            anchor="middle",
            family=F_MONO,
        )
    return body


def _legend() -> str:
    """Draw the metric legend."""
    body = ""
    entries = [
        "1  title bar 31 px",
        "2  menu bar 29 px",
        "3  tool strip 30 px",
        "4  pane head 28 px",
        "5  inspector 240 px",
        "6  status line 26 px",
    ]
    for index, text in enumerate(entries):
        body += txt(
            64 + (index % 3) * 380,
            726 + (index // 3) * 18,
            text,
            size=10,
            fill=SOFT,
            family=F_MONO,
        )
    return body


def fig_window() -> str:
    """Draw window anatomy with labelled metrics."""
    body = title_block(
        64,
        70,
        "Window anatomy",
        "A compact frame with direct commands, named panes and a status line that explains what is happening.",
    )
    x, y, w, h = 150, 160, 900, 540
    body += window_shell(
        x,
        y,
        w,
        h,
        title="Facet Notes — North Sea transition",
        menu=["File", "Edit", "View", "Object", "Tools", "Window", "Help"],
        status="Refreshing currency… last value 14:02",
        state="Refreshing",
    )
    body += _tool_strip(x, y, w)
    tree_w, inspector_w = 210, 240
    body += line(x, y + 90, x, y + h - 26, stroke=LINE)
    body += rect(x, y + 90, tree_w, h - 116, fill=PAPER, stroke=None)
    body += pane_head(x, y + 90, tree_w, "Notes", right="+")
    body += _tree_rows(x, y, tree_w)
    splitter_1 = x + tree_w
    splitter_2 = x + w - inspector_w
    body += line(splitter_1, y + 90, splitter_1, y + h - 26, stroke=INK)
    body += line(splitter_2, y + 90, splitter_2, y + h - 26, stroke=INK)
    body += rect(splitter_1 - 3, y + 300, 6, 42, fill=LINE, stroke=INK)
    body += rect(splitter_2 - 3, y + 300, 6, 42, fill=LINE, stroke=INK)
    body += _editor(y, splitter_1, splitter_2)
    body += _inspector(y, splitter_2, inspector_w)
    body += _callouts(x, y, w, h)
    body += _legend()
    return svg_doc(
        1200,
        780,
        "Window anatomy with labelled metrics",
        "A Facet Notes window with title bar, menu bar, tool strip, note tree, document, inspector and status line, annotated with pixel metrics.",
        body=body,
    )
