"""Draw the formula tool popover figure.

The figure shows selected table cells and a formula popover with expression,
sources, authority and state. The exported `fig_formula` function returns the
SVG string, drawn from the shared `figuregen.palette` colours. `figuregen.cli`
calls it to write `fig-26-formula.svg` under `figures/`.
"""

from __future__ import annotations

import typing as typ

from figuregen.canvas import line, lines, para, rect, svg_doc, txt
from figuregen.ornaments import chip, state_chip, title_block
from figuregen.palette import (
    F_DISPLAY,
    F_MONO,
    HIGH,
    INK,
    LINE,
    OXIDE,
    PINE2,
    SOFT,
    WHITE,
)
from figuregen.widgets import button, titlebar

if typ.TYPE_CHECKING:
    from figuregen.figdata import StateTables


def fig_formula(states: StateTables) -> str:
    """Draw the formula tool popover over selected cells.

    Parameters
    ----------
    states : StateTables
        The live and resolution state records passed to `state_chip`.

    Returns
    -------
    str
    """
    body = title_block(
        64,
        70,
        "The formula tool at the point of use",
        "A tool appears beside the selection it can act on. It shows its sources, its authority and its result without taking over the document.",
    )
    # Document.
    body += rect(64, 150, 760, 540, fill=HIGH, stroke=INK)
    body += titlebar(64, 150, 760, "Facet Notes — Generation mix")
    body += txt(92, 210, "Generation mix", size=22, family=F_DISPLAY, style="italic")
    body += para(
        92,
        238,
        700,
        "The table is selected. A compatible tool is offered beside it rather than in a global services menu.",
        size=11,
        leading=16,
    )
    # Table with selected cells.
    for r in range(4):
        for c in range(4):
            body += rect(
                92 + c * 150,
                286 + r * 34,
                150,
                34,
                fill=PINE2 if (r == 1 and c == 2) else WHITE,
                stroke=LINE,
            )
    body += rect(92 + 150, 286 + 34, 300, 34, fill="none", stroke=OXIDE, sw=2)
    body += txt(104, 310, "Source", size=10, fill=SOFT, family=F_MONO)
    body += txt(254, 310, "Capacity", size=10, fill=SOFT, family=F_MONO)
    body += txt(404, 310, "Output", size=10, fill=SOFT, family=F_MONO)
    body += txt(554, 310, "Share", size=10, fill=SOFT, family=F_MONO)
    # Formula popover.
    x, y, w, h = 400, 340, 420, 300
    body += rect(x + 8, y + 8, w, h, fill="#17201C30", stroke=None)
    body += rect(x, y, w, h, fill=HIGH, stroke=INK)
    body += txt(
        x + 18,
        y + 28,
        "FORMULA",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=0.8,
    )
    body += txt(
        x + w - 18, y + 28, "Esc", size=10, fill=SOFT, family=F_MONO, anchor="end"
    )
    body += rect(x + 18, y + 42, w - 36, 38, fill=WHITE, stroke=OXIDE, sw=2)
    body += txt(x + 30, y + 66, "=SUM(B2:B9) * rate", size=13, fill=INK, family=F_MONO)
    body += txt(
        x + 18,
        y + 108,
        "SOURCES",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=0.6,
    )
    src_body, _ = chip(x + 18, y + 120, "TABLE B2:B9", colour=PINE2)
    body += src_body
    src_body, _ = chip(x + 156, y + 120, "RATE · GBP", colour=PINE2)
    body += src_body
    body += txt(
        x + 18,
        y + 172,
        "AUTHORITY",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=0.6,
    )
    body += txt(x + 18, y + 194, "Read table", size=11, fill=INK)
    body += txt(
        x + w - 18, y + 194, "granted", size=11, fill=PINE2, family=F_MONO, anchor="end"
    )
    body += txt(x + 18, y + 214, "Read rate", size=11, fill=INK)
    body += txt(
        x + w - 18, y + 214, "granted", size=11, fill=PINE2, family=F_MONO, anchor="end"
    )
    body += line(x + 18, y + 232, x + w - 18, y + 232, stroke=LINE)
    body += txt(
        x + 18,
        y + 258,
        "1,284.00 GBP",
        size=18,
        fill=PINE2,
        family=F_MONO,
        weight="bold",
    )
    state_body, _ = state_chip(x + w - 104, y + 242, "Current", states)
    body += state_body
    body += button(x + 18, y + 268, 150, "Insert live value", primary=True, height=30)
    body += button(x + 180, y + 268, 92, "Cancel", height=30)
    # Notes.
    body += txt(
        860, 200, "RULES", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1
    )
    body += lines(
        860,
        232,
        [
            "Offer only applicable tools.",
            "Name every source.",
            "Show the grants used.",
            "Keep the last result visible.",
            "Deny instead of inventing.",
        ],
        size=11,
        leading=28,
        fill=SOFT,
    )
    body += line(860, 400, 1136, 400, stroke=LINE)
    body += para(
        860,
        426,
        276,
        "The result enters the document as a live value with its own identity. It is not a pasted number, and it is not a private macro.",
        size=11,
        leading=17,
    )
    body += para(
        860,
        520,
        276,
        "If a source moves or its grant is withdrawn, the formula becomes stale or denied. The last computed value remains visible and labelled.",
        size=11,
        leading=17,
    )
    return svg_doc(
        1200,
        760,
        "Formula tool popover over a selected table",
        "A table with selected cells and a formula popover showing the expression, sources, authority, result and state.",
        body=body,
    )
