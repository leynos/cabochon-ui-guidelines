"""Figure generator module: figures.document_centre."""

from __future__ import annotations

from figuregen.canvas import circle, ellipse, line, rect, svg_doc, txt
from figuregen.ornaments import mini_note, mini_page, mini_table, title_block
from figuregen.palette import (
    F_DISPLAY,
    F_MONO,
    HIGH,
    INK,
    LINE,
    OXIDE,
    PINE,
    PINE2,
    SOFT,
    WHITE,
)


def fig_document_centre() -> str:
    """Draw one object with its four presentations."""
    body = title_block(
        64,
        70,
        "One object, four presentations",
        "The document is the stable thing. Presentation is how the same object appears for a task.",
    )
    body += ellipse(600, 420, 76, 48, fill=PINE2, stroke=PINE, sw=2)
    body += txt(
        600,
        426,
        "OBJ",
        size=15,
        fill=WHITE,
        family=F_MONO,
        weight="bold",
        anchor="middle",
    )
    body += txt(
        600,
        498,
        "stable identity",
        size=11,
        fill=SOFT,
        family=F_MONO,
        anchor="middle",
        spacing=0.6,
    )
    frames = [
        (64, 166, "NOTE", "prose"),
        (896, 166, "TABLE", "data"),
        (64, 570, "REPORT", "card"),
        (896, 570, "PROOF", "page"),
    ]
    for x, y, label, kind in frames:
        body += rect(x, y, 240, 170, fill=HIGH, stroke=INK)
        body += txt(
            x + 12,
            y + 22,
            label,
            size=10,
            fill=OXIDE,
            family=F_MONO,
            weight="bold",
            spacing=0.8,
        )
        body += txt(
            x + 228, y + 22, "GBP 1,284", size=9, fill=SOFT, family=F_MONO, anchor="end"
        )
        if kind == "prose":
            body += mini_note(x + 12, y + 34, 216, 120)
            body += rect(x + 30, y + 86, 76, 16, fill=HIGH, stroke=PINE2)
            body += txt(x + 34, y + 97, "GBP 1,284", size=10, fill=PINE2, family=F_MONO)
        elif kind == "data":
            body += mini_table(x + 12, y + 34, 216, 120)
        elif kind == "card":
            body += rect(x + 12, y + 34, 216, 120, fill=WHITE, stroke=LINE)
            body += txt(x + 24, y + 60, "North Sea currency", size=11, fill=SOFT)
            body += txt(
                x + 24,
                y + 94,
                "GBP 1,284",
                size=24,
                fill=INK,
                family=F_MONO,
                weight="bold",
            )
            body += txt(
                x + 24, y + 120, "report card · 2026", size=10, fill=SOFT, family=F_MONO
            )
        else:
            body += mini_page(x + 12, y + 34, 216, 120)
        start_x = x + 240 if x < 600 else x
        start_y = y + 85
        end_x = 524 if x < 600 else 676
        body += line(start_x, start_y, end_x, 420, stroke=LINE, sw=1.5, dash="4 4")
        body += circle(start_x, start_y, 3, fill=OXIDE, stroke=None)
    body += txt(
        64,
        700,
        "Presentation changes. Identity does not.",
        size=20,
        family=F_DISPLAY,
        style="italic",
        fill=PINE,
    )
    body += txt(
        64,
        726,
        "A conversion is not a new object unless the user duplicates or derives one.",
        size=12,
        fill=SOFT,
    )
    return svg_doc(
        1200,
        760,
        "One object with four presentations",
        "A central object connected to note, table, drawing and page presentations.",
        body=body,
    )
