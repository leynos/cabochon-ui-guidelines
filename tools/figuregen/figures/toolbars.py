"""Figure generator module: figures.toolbars."""

from __future__ import annotations

from figuregen.canvas import line, para, rect, svg_doc, txt
from figuregen.glyphs import tool_glyph
from figuregen.ornaments import state_chip, title_block
from figuregen.palette import (
    F_DISPLAY,
    F_MONO,
    HIGH,
    INK,
    LINE,
    OXIDE,
    PAPER,
    PINE,
    PINE2,
    SOFT,
    WHITE,
)
from figuregen.widgets import titlebar


def fig_toolbars() -> str:
    """Draw the tool strip, status line and target sizes."""
    body = title_block(
        64,
        70,
        "Tool strips and status",
        "Tools sit next to the work. The status line says what the tool will do, what it just did, and what state the data is in.",
    )
    x, y, w = 64, 160, 1072
    body += rect(x + 8, y + 8, w, 76, fill="#17201C18", stroke=None)
    body += rect(x, y, w, 76, fill=HIGH, stroke=INK)
    body += titlebar(x, y, w, "Burin Draw — Currency plate")
    body += rect(x, y + 31, w, 30, fill=PAPER, stroke=None)
    body += line(x, y + 61, x + w, y + 61, stroke=LINE)
    for index, glyph in enumerate(["select", "pen", "line", "rect", "ellipse", "text"]):
        bx = x + 12 + index * 38
        active = index == 1
        body += rect(bx, y + 31, 30, 30, fill=PINE2 if active else HIGH, stroke=LINE)
        colour = WHITE if active else INK
        body += tool_glyph(glyph, bx + 15, y + 46, colour)
    body += line(x + 240, y + 37, x + 240, y + 57, stroke=LINE)
    body += txt(x + 248, y + 50, "Stroke  1 px", size=11, fill=SOFT)
    body += txt(x + 400, y + 50, "Grid  16 px", size=11, fill=SOFT)
    body += txt(x + 520, y + 50, "Zoom  100%", size=11, fill=SOFT)
    body += txt(x + w - 14, y + 50, "Inspector", size=11, fill=SOFT, anchor="end")
    # Status line example.
    sy = 300
    body += rect(x, sy, w, 26, fill=PAPER, stroke=INK)
    body += txt(
        x + 14,
        sy + 17,
        "Pen · dragging a 2 px stroke · 14 objects selected",
        size=12,
        fill=INK,
    )
    state_body, _ = state_chip(x + w - 130, sy + 3, "Current")
    body += state_body
    body += txt(
        x + w - 150,
        sy + 17,
        "Saved 14:02",
        size=11,
        fill=SOFT,
        anchor="end",
        family=F_MONO,
    )
    # Target sizes.
    body += txt(
        64,
        404,
        "TARGET SIZES",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    sizes = [
        (28, "minimum", HIGH, INK),
        (32, "preferred", HIGH, INK),
        (36, "primary action", PINE, WHITE),
    ]
    for index, (size, role, fill, colour) in enumerate(sizes):
        bx = 64 + index * 220
        body += rect(bx, 430, size, size, fill=fill, stroke=INK)
        body += txt(
            bx + size / 2,
            430 + size / 2 + 4,
            "Aa",
            size=11,
            fill=colour,
            anchor="middle",
        )
        body += txt(
            bx, 488, f"{size} × {size}  {role}", size=11, fill=SOFT, family=F_MONO
        )
    body += para(
        64,
        540,
        500,
        "The glyph may be 16 px. The target is never smaller than 28 px, and a primary action in a dialog is 36 px high.",
        size=11,
        leading=17,
    )
    body += para(
        64,
        610,
        500,
        "Tool strips contain tools, not commands. Save, print and preferences belong in menus or the command palette.",
        size=11,
        leading=17,
    )
    body += para(
        620,
        540,
        516,
        "A status line is a sentence, not a progress ornament. It names the object, the operation and the result, and it keeps the last useful value visible while a refresh is in flight.",
        size=11,
        leading=17,
    )
    body += txt(
        620,
        640,
        "Spinners may accompany a sentence. They never replace one.",
        size=12,
        fill=OXIDE,
        family=F_DISPLAY,
        style="italic",
    )
    return svg_doc(
        1200,
        760,
        "Tool strip, status line and target sizes",
        "A drawing tool strip, a status line with a live state, and minimum, preferred and primary target sizes.",
        body=body,
    )
