"""Draw the control gallery figure.

The gallery shows buttons, fields, checkboxes, radio buttons, a slider and
tabs at their target sizes. The exported `fig_controls` function returns the
SVG string, drawn from the shared `figuregen.palette` colours. `figuregen.cli`
calls it to write `fig-18-controls.svg` under `figures/`.
"""

from __future__ import annotations

from figuregen.canvas import circle, line, para, rect, svg_doc, txt
from figuregen.ornaments import title_block
from figuregen.palette import F_MONO, HIGH, INK, LINE, OXIDE, PINE2, SOFT
from figuregen.widgets import button, checkbox, field, radio


def fig_controls() -> str:
    """Draw the control gallery with buttons, fields and selections."""
    body = title_block(
        64,
        70,
        "Controls are direct",
        "A control looks like what it does. It has one job, one label and a target a hand can find.",
    )
    # Buttons.
    body += txt(
        64, 158, "BUTTONS", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1
    )
    body += button(64, 174, 124, "Cancel")
    body += button(200, 174, 140, "Save note", primary=True)
    body += button(352, 174, 132, "Delete", destructive=True)
    body += button(496, 174, 124, "Unavailable", disabled=True)
    # Fields.
    body += txt(
        64, 254, "FIELDS", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1
    )
    body += field(64, 278, 300, "North Sea transition", label="Title")
    body += field(64, 342, 300, "enfilade.table", label="Provider", focus=True)
    body += txt(
        64,
        404,
        "The provider is chosen by the object, not typed by the user.",
        size=10,
        fill=SOFT,
    )
    # Choice.
    body += txt(
        64, 458, "CHOICE", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1
    )
    body += checkbox(64, 484, "Show grid", checked=True)
    body += checkbox(64, 512, "Snap to guides", checked=True)
    body += checkbox(64, 540, "Show rulers", checked=False)
    body += radio(260, 484, "Current value", selected=True)
    body += radio(260, 512, "Last saved value", selected=False)
    body += radio(260, 540, "Both, side by side", selected=False)
    # Slider and tabs.
    body += txt(
        500,
        458,
        "RANGE AND TABS",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    body += txt(500, 484, "Stroke", size=11, fill=INK)
    body += line(560, 494, 780, 494, stroke=LINE, sw=4)
    body += line(560, 494, 668, 494, stroke=PINE2, sw=4)
    body += circle(668, 494, 8, fill=HIGH, stroke=PINE2, sw=2)
    body += txt(796, 498, "2 px", size=11, fill=SOFT, family=F_MONO)
    for index, (name, active) in enumerate([
        ("Note", True),
        ("Table", False),
        ("Diagram", False),
    ]):
        tx = 500 + index * 100
        body += rect(tx, 526, 100, 32, fill=HIGH, stroke=LINE)
        body += txt(
            tx + 50, 547, name, size=11, fill=INK if active else SOFT, anchor="middle"
        )
        if active:
            body += line(tx, 557, tx + 100, 557, stroke=OXIDE, sw=3)
    body += para(
        500,
        586,
        360,
        "A slider shows its value and its unit. A tab names a view, never a verb. A checkbox is a state; a button is an action.",
        size=11,
        leading=17,
    )
    # Targets.
    body += line(64, 600, 1136, 600, stroke=LINE)
    body += txt(
        64,
        630,
        "TARGETS AND SPACING",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    body += rect(64, 650, 28, 28, fill=HIGH, stroke=INK)
    body += rect(100, 650, 28, 28, fill=HIGH, stroke=INK)
    body += line(92, 686, 100, 686, stroke=OXIDE, sw=1, dash="3 3")
    body += txt(96, 700, "8", size=9, fill=OXIDE, family=F_MONO, anchor="middle")
    body += rect(144, 646, 32, 32, fill=HIGH, stroke=INK)
    body += rect(188, 644, 36, 36, fill=HIGH, stroke=INK)
    body += txt(
        64,
        712,
        "28 minimum · 32 preferred · 36 primary",
        size=10,
        fill=SOFT,
        family=F_MONO,
    )
    body += para(
        440,
        640,
        700,
        "Labels sit above fields and beside choices. Units and shortcuts use the metadata voice. A control that needs a paragraph of explanation needs a different control.",
        size=11,
        leading=17,
    )
    return svg_doc(
        1200,
        760,
        "Control gallery",
        "Buttons, fields, checkboxes, radio buttons, a slider, tabs and target-size examples.",
        body=body,
    )
