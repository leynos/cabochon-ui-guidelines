"""Figure generator module: figures.planes."""

from __future__ import annotations

from figuregen.canvas import line, rect, svg_doc, txt
from figuregen.ornaments import title_block
from figuregen.palette import F_DISPLAY, F_MONO, HIGH, INK, LINE, OXIDE, PAPER, SOFT


def fig_planes() -> str:
    """Draw the four interface planes and their borders."""
    body = title_block(
        64,
        70,
        "Planes, borders and elevation",
        "The interface is made of flat planes with exact edges. Depth is a border and an offset, not a glow.",
    )
    planes = [
        ("PAPER", PAPER, 0, 0, "the document ground"),
        ("PANE", HIGH, 120, 70, "a region of work"),
        ("CONTROL", "#E4E3DD", 240, 140, "a thing you can press"),
        ("OVERLAY", HIGH, 360, 210, "a thing that must be seen"),
    ]
    for name, colour, dx, dy, note in planes:
        x = 220 + dx
        y = 200 + dy
        body += rect(x + 12, y + 14, 420, 210, fill="#17201C18", stroke=None)
        body += rect(
            x, y, 420, 210, fill=colour, stroke=INK, sw=1.5 if name == "OVERLAY" else 1
        )
        body += txt(
            x + 16,
            y + 28,
            name,
            size=10,
            fill=OXIDE,
            family=F_MONO,
            weight="bold",
            spacing=0.8,
        )
        body += txt(x + 16, y + 52, note, size=12, fill=SOFT)
    body += txt(780, 242, "1 px border", size=11, fill=SOFT, family=F_MONO)
    body += line(720, 254, 880, 254, stroke=LINE)
    body += txt(780, 284, "No blur", size=11, fill=SOFT, family=F_MONO)
    body += txt(
        780, 326, "Offset shadow only for overlays", size=11, fill=SOFT, family=F_MONO
    )
    body += txt(
        780, 368, "Never raise a control with a glow", size=11, fill=SOFT, family=F_MONO
    )
    body += txt(
        64,
        690,
        "A border says where a thing ends. An offset says that it floats. Nothing else needs to be said.",
        size=13,
        fill=SOFT,
        family=F_DISPLAY,
        style="italic",
    )
    return svg_doc(
        1200,
        740,
        "Four interface planes",
        "Paper, pane, control and overlay planes, each with a border and only the overlay with an offset shadow.",
        body=body,
    )
