"""Figure generator module: figures.material_palette."""

from __future__ import annotations

from figuregen.canvas import lines, rect, svg_doc, txt
from figuregen.ornaments import title_block
from figuregen.palette import (
    AMBER,
    AMBER_INK,
    DARK,
    DARK_AMBER,
    DARK_MUTED,
    DARK_OXIDE,
    DARK_PINE,
    DARK_SURFACE,
    DARK_TEXT,
    F_MONO,
    HIGH,
    INK,
    LINE,
    OXIDE,
    PAPER,
    PINE,
    PINE2,
    SOFT,
    TEAL,
    TEAL_INK,
)


def fig_palette() -> str:
    """Draw the material palette in light and dark."""
    body = title_block(
        64,
        70,
        "The material palette",
        "Paper, ink, pine, teal, oxide and amber. Colour is material and state, not decoration.",
    )
    light = [
        ("Paper", PAPER, INK, "ground"),
        ("High", HIGH, INK, "raised pane"),
        ("Ink", INK, PAPER, "text"),
        ("Soft", SOFT, PAPER, "secondary"),
        ("Pine", PINE, PAPER, "window edge"),
        ("Pine 2", PINE2, PAPER, "selection"),
        ("Teal", TEAL, INK, "decoration only"),
        ("Teal ink", TEAL_INK, PAPER, "refresh text"),
        ("Oxide", OXIDE, PAPER, "authority"),
        ("Amber", AMBER, INK, "large marks"),
        ("Amber ink", AMBER_INK, PAPER, "stale text"),
        ("Line", LINE, INK, "hairline"),
    ]
    for index, (name, colour, text_colour, note) in enumerate(light):
        x = 64 + (index % 6) * 180
        y = 166 + (index // 6) * 150
        body += rect(x, y, 168, 128, fill=colour, stroke=INK)
        body += txt(
            x + 12,
            y + 22,
            name,
            size=11,
            fill=text_colour,
            family=F_MONO,
            weight="bold",
        )
        body += txt(x + 12, y + 44, colour, size=10, fill=text_colour, family=F_MONO)
        body += txt(x + 12, y + 108, note, size=10, fill=text_colour)
    body += txt(
        64, 500, "DARK", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1
    )
    dark = [
        ("Ground", DARK, DARK_TEXT),
        ("Surface", DARK_SURFACE, DARK_TEXT),
        ("Text", DARK_TEXT, DARK),
        ("Muted", DARK_MUTED, DARK),
        ("Pine", DARK_PINE, DARK),
        ("Oxide", DARK_OXIDE, DARK),
        ("Amber", DARK_AMBER, DARK),
    ]
    for index, (name, colour, text_colour) in enumerate(dark):
        x = 64 + index * 158
        body += rect(x, 522, 144, 96, fill=colour, stroke=INK)
        body += txt(
            x + 10, 546, name, size=10, fill=text_colour, family=F_MONO, weight="bold"
        )
        body += txt(x + 10, 566, colour, size=9, fill=text_colour, family=F_MONO)
    body += lines(
        64,
        664,
        [
            "Amber #B8792E is a large-text and icon accent; use #8A5B24 for body-size text.",
            "Teal #678E86 is decoration and refresh motion, never body text on paper.",
            "Line #AAA99F is a hairline, not a text colour.",
        ],
        size=11,
        fill=SOFT,
        leading=18,
    )
    return svg_doc(
        1200,
        760,
        "The material palette in light and dark",
        "Light and dark swatches with names, hex values and contrast-safe roles.",
        body=body,
    )
