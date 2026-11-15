"""Draw the typographic voices and type scale figure.

Display, interface and metadata specimens sit above an eight-row type scale.
The exported `fig_type` function returns the SVG string, drawn from the shared
`figuregen.palette` colours. `figuregen.cli` calls it to write
`fig-08-type.svg` under `figures/`.
"""

from __future__ import annotations

from figuregen.canvas import line, lines, rect, svg_doc, txt
from figuregen.ornaments import kicker, title_block
from figuregen.palette import F_DISPLAY, F_MONO, HIGH, INK, LINE, OXIDE, SOFT


def fig_type() -> str:
    """Draw the three typographic voices and the type scale."""
    body = title_block(
        64,
        70,
        "Three typographic voices",
        "Display argues, interface explains, metadata accounts. They do not trade places.",
    )
    body += rect(64, 166, 352, 240, fill=HIGH, stroke=INK)
    body += kicker(84, 196, "Display / Georgia italic")
    body += lines(
        84,
        248,
        ["Pages know", "where they", "are going."],
        size=42,
        family=F_DISPLAY,
        style="italic",
        leading=46,
    )
    body += txt(
        84,
        380,
        "Long-form titles and pull quotes only.",
        size=10,
        fill=SOFT,
        family=F_MONO,
    )

    body += rect(432, 166, 352, 240, fill=HIGH, stroke=INK)
    body += kicker(452, 196, "Interface / humanist sans")
    body += lines(
        452,
        250,
        ["Selection:", "Annual energy balance", "4 tools available"],
        size=19,
        leading=28,
    )
    body += txt(
        452,
        380,
        "Controls, labels, prose in panels.",
        size=10,
        fill=SOFT,
        family=F_MONO,
    )

    body += rect(800, 166, 336, 240, fill=HIGH, stroke=INK)
    body += kicker(820, 196, "Metadata / humanist mono")
    body += lines(
        820,
        250,
        ["OBJ 7F4C", "CURRENT", "PDF/X-4 · 125%"],
        size=13,
        family=F_MONO,
        leading=26,
    )
    body += txt(
        820,
        380,
        "Identity, state, units, shortcuts.",
        size=10,
        fill=SOFT,
        family=F_MONO,
    )

    rows = [
        ("Display", "42-96 / 0.95", "Georgia italic", "chapter and cover titles"),
        ("Title", "24-32 / 1.1", "Georgia italic", "tool and document titles"),
        ("Subtitle", "18 / 1.2", "Georgia italic", "inspector object names"),
        ("Section", "16-20 / 1.2", "Humanist sans bold", "pane and dialog headings"),
        (
            "Body",
            "15-16 / 1.6",
            "Georgia or humanist sans",
            "notes and long-form prose",
        ),
        ("Interface", "12 / 1.35", "Humanist sans", "controls, labels, menus"),
        ("Metadata", "11 / 1.4", "Humanist mono", "identity, state, units"),
        ("Folio", "10 / 1.2", "Humanist mono", "folios and plate marks"),
    ]
    body += txt(
        64, 458, "SIZE", size=9, fill=OXIDE, family=F_MONO, weight="bold", spacing=1
    )
    body += txt(
        180,
        458,
        "SIZE / LINE",
        size=9,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    body += txt(
        330, 458, "FACE", size=9, fill=OXIDE, family=F_MONO, weight="bold", spacing=1
    )
    body += txt(
        560, 458, "USE", size=9, fill=OXIDE, family=F_MONO, weight="bold", spacing=1
    )
    for index, (name, size, face, use) in enumerate(rows):
        y = 482 + index * 30
        body += line(64, y, 1136, y, stroke=LINE)
        body += txt(64, y + 20, name, size=12, weight="bold")
        body += txt(180, y + 20, size, size=11, family=F_MONO, fill=SOFT)
        body += txt(330, y + 20, face, size=11, fill=SOFT)
        body += txt(560, y + 20, use, size=11, fill=SOFT)
    body += txt(
        64,
        740,
        "No interface text below 12 px. 11 px metadata is for non-essential labels; 10 px only for folios and plate marks.",
        size=11,
        fill=OXIDE,
    )
    return svg_doc(
        1200,
        760,
        "Three typographic voices and a type scale",
        "Display, interface and metadata specimens above an eight-row type scale.",
        body=body,
    )
