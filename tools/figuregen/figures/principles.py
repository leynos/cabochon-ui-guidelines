"""Draw the four principles figure.

Four cards state that rectangles behave, objects persist, output is native and
state speaks. The exported `fig_principles` function returns the SVG string,
drawn from the shared `figuregen.palette` colours. `figuregen.cli` calls it to
write `fig-04-principles.svg` under `figures/`.
"""

from __future__ import annotations

import math

from figuregen.canvas import ellipse, line, lines, rect, svg_doc, txt
from figuregen.ornaments import title_block
from figuregen.palette import (
    AMBER_INK,
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
    TEAL_INK,
    WHITE,
)


def _object_spokes(gx: float, gy: float) -> str:
    """Return the labelled spokes drawn around the object glyph."""
    body = ""
    for angle, label in [(-60, "N"), (-10, "T"), (40, "D"), (90, "P")]:
        radians = math.radians(angle)
        cos_a, sin_a = math.cos(radians), math.sin(radians)
        body += line(
            gx,
            gy,
            gx + 62 * cos_a,
            gy + 62 * sin_a,
            stroke=LINE,
        )
        body += txt(
            gx + 68 * cos_a,
            gy + 68 * sin_a + 4,
            label,
            size=9,
            fill=OXIDE,
            family=F_MONO,
            anchor="middle",
        )
    return body


def fig_principles() -> str:
    """Draw the four principles as cards.

    Returns
    -------
    str
    """
    body = title_block(
        64,
        70,
        "Four principles",
        "They are short enough to remember and specific enough to settle an argument.",
    )
    items = [
        (
            "01",
            "Rectangles behave",
            "Compact panes, direct menus and precise geometry. No hamburger archaeology.",
            "rect",
        ),
        (
            "02",
            "Objects persist",
            "A note, table or drawing keeps its identity when another tool presents it.",
            "object",
        ),
        (
            "03",
            "Output is native",
            "The same scene reaches display, PDF, thumbnail and print without translation.",
            "page",
        ),
        (
            "04",
            "State speaks",
            "Current, refreshing, stale, broken and denied never hide behind a spinner.",
            "state",
        ),
    ]
    for index, (num, title, text, glyph) in enumerate(items):
        col = index % 2
        row = index // 2
        x = 64 + col * 552
        y = 166 + row * 268
        body += rect(x, y, 528, 240, fill=HIGH, stroke=INK)
        body += txt(
            x + 20,
            y + 34,
            num,
            size=11,
            fill=OXIDE,
            family=F_MONO,
            weight="bold",
            spacing=0.8,
        )
        body += txt(x + 20, y + 76, title, size=28, family=F_DISPLAY, style="italic")
        body += lines(x + 20, y + 110, [text], size=12, fill=SOFT, leading=18)
        gx = x + 420
        gy = y + 150
        if glyph == "rect":
            body += rect(gx - 46, gy - 28, 92, 56, fill=PAPER, stroke=PINE2, sw=2)
            body += rect(gx - 34, gy - 16, 40, 18, fill=WHITE, stroke=LINE)
            body += rect(gx + 12, gy - 16, 22, 18, fill=WHITE, stroke=LINE)
        elif glyph == "object":
            body += ellipse(gx, gy, 40, 26, fill=PINE2, stroke=PINE)
            body += _object_spokes(gx, gy)
        elif glyph == "page":
            body += rect(gx - 38, gy - 34, 76, 68, fill=WHITE, stroke=INK)
            body += txt(
                gx,
                gy + 4,
                "PDF",
                size=13,
                family=F_MONO,
                weight="bold",
                anchor="middle",
                fill=OXIDE,
            )
            body += line(gx - 26, gy + 18, gx + 26, gy + 18, stroke=LINE)
        else:
            sx = gx - 50
            for label, colour in [
                ("CUR", PINE2),
                ("REF", TEAL_INK),
                ("STA", AMBER_INK),
            ]:
                body += rect(sx, gy - 12, 32, 24, fill=HIGH, stroke=colour)
                body += txt(
                    sx + 16,
                    gy + 4,
                    label,
                    size=10,
                    family=F_MONO,
                    anchor="middle",
                    fill=colour,
                )
                sx += 36
    return svg_doc(
        1200,
        740,
        "Four principles",
        "Four cards: rectangles behave, objects persist, output is native, and state speaks.",
        body=body,
    )
