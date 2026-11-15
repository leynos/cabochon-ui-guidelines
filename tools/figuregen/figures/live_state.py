"""Draw the live state and transition figure.

The figure pairs five state cards with the table of legal transitions and
their owners. The exported `fig_state` function returns the SVG string, drawn
from `LIVE_STATES` and `LIVE_TRANSITIONS` in `figuregen.figdata`.
`figuregen.cli` calls it to write `fig-06-state.svg` under `figures/`.
"""

from __future__ import annotations

from figuregen.canvas import attrs, line, para, rect, svg_doc, txt
from figuregen.figdata import LIVE_STATES, LIVE_TRANSITIONS
from figuregen.ornaments import mark_group, state_mark, title_block
from figuregen.palette import (
    AMBER_INK,
    F_DISPLAY,
    F_MONO,
    HIGH,
    INK,
    LINE,
    OXIDE,
    PINE2,
    SOFT,
    TEAL_INK,
)


def fig_state() -> str:
    """Draw the five live states and their legal transitions."""
    body = title_block(
        64,
        70,
        "Failure has a shape",
        "Five visible states, one vocabulary. A spinner is not a state description.",
    )
    states = [
        (
            "Current",
            PINE2,
            "The accepted value matches every known source revision.",
            "Use the value.",
        ),
        (
            "Refreshing",
            TEAL_INK,
            "A refresh is in flight. The last accepted value may remain visible.",
            "Keep the old value.",
        ),
        (
            "Stale",
            AMBER_INK,
            "The source reports a newer revision than the accepted value.",
            "Keep and label it.",
        ),
        (
            "Broken",
            OXIDE,
            "The source is unreachable, or no value has been accepted.",
            "Keep the link.",
        ),
        (
            "Denied",
            OXIDE,
            "Current authority does not permit the read.",
            "Explain the grant.",
        ),
    ]
    for index, (name, colour, text, action) in enumerate(states):
        x = 64 + index * 220
        record = LIVE_STATES[name]
        mark = str(record["mark"])
        body += '<g data-state-card="true">'
        body += rect(
            x,
            166,
            204,
            190,
            fill=HIGH,
            stroke=colour,
            sw=2 if name in {"Stale", "Denied"} else 1,
        )
        body += mark_group(
            mark,
            str(record["id"]),
            str(record["role"]),
            state_mark(x + 22, 194, mark, colour),
        )
        body += txt(
            x + 38,
            200,
            name.upper(),
            size=12,
            fill=colour,
            family=F_MONO,
            weight="bold",
            spacing=0.6,
            data_state=str(record["id"]),
        )
        body += para(x + 18, 226, 168, text, size=11, leading=16)
        body += line(x + 18, 300, x + 186, 300, stroke=LINE)
        body += txt(x + 18, 326, action, size=11, fill=INK, weight="bold")
        body += "</g>"

    # Legal transitions, taken from the state table in chapter 8.
    body += txt(
        64,
        400,
        "LEGAL TRANSITIONS",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    body += txt(
        80, 430, "FROM", size=9, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.6
    )
    body += txt(
        300, 430, "EVENT", size=9, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.6
    )
    body += txt(
        700, 430, "TO", size=9, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.6
    )
    body += txt(
        850, 430, "OWNER", size=9, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.6
    )
    for index, transition in enumerate(LIVE_TRANSITIONS):
        ty = 460 + index * 24
        source = ", ".join(transition["from"])
        identifier = str(transition["id"])
        body += f"<g {attrs(data_transition_id=identifier)}>"
        body += line(64, ty - 17, 1136, ty - 17, stroke=LINE, sw=0.5)
        body += txt(80, ty, source, size=11, fill=INK, family=F_MONO)
        body += txt(300, ty, transition["event"], size=11, fill=SOFT)
        body += txt(700, ty, transition["to"], size=11, fill=PINE2, family=F_MONO)
        body += txt(850, ty, transition["owner"], size=11, fill=SOFT, family=F_MONO)
        body += "</g>"
    body += txt(
        64,
        840,
        "Authority and provider loss move the state directly. Every refresh passes through Refreshing.",
        size=13,
        fill=SOFT,
        family=F_DISPLAY,
        style="italic",
    )
    body += txt(
        64,
        866,
        "A cancelled request recomputes the chip from the facts; it never restores an old label.",
        size=13,
        fill=SOFT,
        family=F_DISPLAY,
        style="italic",
    )
    return svg_doc(
        1200,
        910,
        "Five live-relationship states and their legal transitions",
        "Cards for current, refreshing, stale, broken and denied, followed by the legal transition table with owners.",
        body=body,
    )
