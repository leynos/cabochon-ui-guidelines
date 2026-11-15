"""Figure generator module: figures.icons."""

from __future__ import annotations

from figuregen.canvas import path, rect, svg_doc, txt
from figuregen.ornaments import title_block
from figuregen.palette import AMBER_INK, F_MONO, HIGH, INK, LINE, OXIDE, SOFT


def fig_icons() -> str:
    """Draw the icon grid, sizes and states."""
    body = title_block(
        64,
        70,
        "Icons and glyphs",
        "Monochrome line drawings at 16, 20 and 24 pixels. Colour is reserved for state.",
    )
    glyphs = [
        ("select", "M 8 6 L 22 18 L 16 19 L 19 28 L 15 29 L 12 20 L 8 25 Z"),
        ("text", "M 10 9 H 30 M 20 9 V 29"),
        ("rect", "M 8 10 H 32 V 28 H 8 Z"),
        (
            "ellipse",
            "M 20 8 C 28 8 34 13 34 19 C 34 25 28 30 20 30 C 12 30 6 25 6 19 C 6 13 12 8 20 8 Z",
        ),
        ("pen", "M 9 30 L 12 20 L 25 7 L 31 13 L 18 26 Z M 12 20 L 18 26"),
        ("line", "M 8 28 L 32 10"),
        (
            "table",
            "M 7 9 H 33 V 29 H 7 Z M 7 16 H 33 M 7 22 H 33 M 15 9 V 29 M 24 9 V 29",
        ),
        (
            "formula",
            "M 9 28 C 12 28 13 24 14 19 C 15 13 17 9 21 9 M 10 18 H 20 M 24 16 L 30 24 M 30 16 L 24 24",
        ),
        (
            "link",
            "M 15 24 L 12 27 C 8 30 4 26 7 22 L 12 17 M 25 16 L 28 13 C 31 9 27 5 23 8 L 18 13 M 14 22 L 26 10",
        ),
        ("lock", "M 11 19 V 14 C 11 8 29 8 29 14 V 19 M 8 19 H 32 V 31 H 8 Z"),
        ("warning", "M 20 8 L 34 30 H 6 Z M 20 15 V 22 M 20 26 V 27"),
        ("check", "M 8 20 L 16 28 L 32 10"),
        (
            "refresh",
            "M 29 15 C 27 9 18 7 13 12 C 8 17 10 26 17 29 M 29 15 V 8 M 29 15 H 22",
        ),
        (
            "gear",
            "M 20 13 A 7 7 0 1 0 20 27 A 7 7 0 1 0 20 13 M 20 6 V 10 M 20 30 V 34 M 6 20 H 10 M 30 20 H 34 M 10 10 L 13 13 M 27 27 L 30 30 M 30 10 L 27 13 M 13 27 L 10 30",
        ),
    ]
    for index, (name, d) in enumerate(glyphs):
        col = index % 7
        row = index // 7
        x = 64 + col * 156
        y = 166 + row * 142
        body += rect(x, y, 132, 116, fill=HIGH, stroke=LINE)
        body += f'<g transform="translate({x + 26} {y + 26}) scale(1.25)">{path(d, stroke=INK, sw=2)}</g>'
        body += txt(x + 10, y + 100, name, size=10, fill=SOFT, family=F_MONO)

    body += txt(
        64, 500, "SIZES", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1
    )
    for index, size in enumerate([16, 20, 24]):
        x = 64 + index * 180
        body += rect(x, 520, 156, 120, fill=HIGH, stroke=LINE)
        body += f'<g transform="translate({x + 60} {570 - size / 2}) scale({size / 24})">{path("M 8 20 L 16 28 L 32 10", stroke=INK, sw=2)}</g>'
        body += txt(x + 12, 620, f"{size} px", size=10, fill=SOFT, family=F_MONO)

    body += txt(
        640, 500, "STATES", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1
    )
    for index, (label, colour, note) in enumerate([
        ("Default", INK, "inherits text"),
        ("Active", OXIDE, "current tool"),
        ("Stale", AMBER_INK, "with a label"),
        ("Disabled", LINE, "not focusable"),
    ]):
        y = 520 + index * 44
        body += rect(640, y, 44, 32, fill=HIGH, stroke=LINE)
        body += f'<g transform="translate(650 {y + 2})">{path("M 8 20 L 16 28 L 32 10", stroke=colour, sw=2)}</g>'
        body += txt(
            700,
            y + 16,
            label,
            size=11,
            weight="bold",
            fill=colour if colour != LINE else SOFT,
        )
        body += txt(700, y + 32, note, size=10, fill=SOFT)
    body += txt(
        640,
        712,
        "A 16 px icon may sit inside a 28 px target; the target, not the glyph, is the contract.",
        size=11,
        fill=SOFT,
    )
    return svg_doc(
        1200,
        760,
        "Icon grid, sizes and states",
        "Fourteen line glyphs across two rows, plus size and state examples.",
        body=body,
    )
