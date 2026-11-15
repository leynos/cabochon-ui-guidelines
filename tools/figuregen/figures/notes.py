"""Draw the Facet Notes window figure.

The window shows a note tree, three embedded objects in different states and a
relations panel. The exported `fig_notes` function returns the SVG string,
drawn from the shared `figuregen.palette` colours. `figuregen.cli` calls it to
write `fig-22-notes.svg` under `figures/`.
"""

# The drawing primitives take geometry and style arguments positionally; see
# the matching ruff exemption for tools/figuregen in pyproject.toml.

from __future__ import annotations

import typing as typ

from figuregen.canvas import circle, line, para, rect, svg_doc, txt
from figuregen.ornaments import state_chip, title_block
from figuregen.palette import (
    AMBER,
    F_DISPLAY,
    F_MONO,
    HIGH,
    INK,
    LINE,
    OXIDE,
    PAPER,
    PINE2,
    SOFT,
    TEAL,
    WHITE,
)
from figuregen.widgets import pane_head, window_shell

if typ.TYPE_CHECKING:
    from figuregen.figdata import StateTables


def _note_tree(x: float, y: float, tree_w: float, h: float) -> str:
    """Draw the note tree."""
    body = rect(x, y + 60, tree_w, h - 86, fill=PAPER, stroke=None)
    body += pane_head(x, y + 60, tree_w, "Notes", right="+")
    rows = [
        ("Project", 0, False),
        ("North Sea transition", 1, True),
        ("Sources", 1, False),
        ("Generation mix", 2, False),
        ("Currency", 2, False),
        ("Figures", 1, False),
        ("Archive", 0, False),
    ]
    for index, (name, depth, selected) in enumerate(rows):
        ry = y + 92 + index * 28
        if selected:
            body += rect(x, ry - 18, tree_w, 26, fill=PINE2, stroke=None)
        body += txt(
            x + 12 + depth * 14, ry, name, size=11, fill=WHITE if selected else INK
        )
    return body


def _embed_card(  # pylint: disable=too-many-arguments
    ex: float,
    y: float,
    ew: float,
    *,
    top: float,
    height: float,
    colour: str,
    title: str,
    meta: str,
    state: str,
    states: StateTables,
) -> str:
    """Draw one embed card with its identity and state."""
    body = rect(ex, y + top, ew, height, fill=HIGH, stroke=LINE)
    body += rect(ex, y + top, 4, height, fill=colour, stroke=None)
    body += txt(ex + 16, y + top + 26, title, size=12, weight="bold")
    body += txt(ex + 16, y + top + 44, meta, size=10, fill=SOFT, family=F_MONO)
    state_body, _ = state_chip(ex + ew - 104, y + top + 18, state, states)
    return body + state_body


def _embed_grid(ex: float, y: float) -> str:
    """Draw the miniature table inside an embed."""
    body = ""
    for col in range(4):
        for row in range(2):
            body += rect(
                ex + 16 + col * 92,
                y + 282 + row * 14,
                88,
                11,
                fill=PAPER,
                stroke=LINE,
                sw=0.5,
            )
    return body


def _embed_diagram(ex: float, y: float) -> str:
    """Draw the miniature diagram inside an embed."""
    body = circle(ex + 44, y + 398, 10, fill=PINE2, stroke=None)
    body += line(ex + 54, y + 398, ex + 96, y + 398, stroke=INK)
    body += circle(ex + 106, y + 398, 10, fill=HIGH, stroke=OXIDE, sw=2)
    body += line(ex + 116, y + 398, ex + 158, y + 398, stroke=INK)
    return body + circle(ex + 168, y + 398, 10, fill=HIGH, stroke=PINE2, sw=2)


def _embeds(ex: float, y: float, ew: float, states: StateTables) -> str:
    """Draw the three live embeds."""
    body = _embed_card(
        ex,
        y,
        ew,
        top=224,
        height=86,
        colour=PINE2,
        title="Generation mix",
        meta="Table · 12 rows · 4 columns · obj:8f3a",
        state="Current",
        states=states,
    )
    body += _embed_grid(ex, y)
    body += _embed_card(
        ex,
        y,
        ew,
        top=328,
        height=86,
        colour=AMBER,
        title="Transition pathways",
        meta="Diagram · Mermaid source · obj:1b90",
        state="Stale",
        states=states,
    )
    body += _embed_diagram(ex, y)
    return body + _embed_card(
        ex,
        y,
        ew,
        top=432,
        height=74,
        colour=TEAL,
        title="North Sea currency",
        meta="Currency · GBP · last read 14:02",
        state="Refreshing",
        states=states,
    )


def _relations(bx: float, y: float, back_w: float) -> str:
    """Draw the relations panel."""
    body = pane_head(bx, y + 60, back_w, "Relations")
    body += txt(
        bx + 14,
        y + 108,
        "LINKED FROM",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=0.6,
    )
    body += txt(bx + 14, y + 132, "Projects / 2026", size=11, fill=INK)
    body += txt(bx + 14, y + 152, "Reading list", size=11, fill=INK)
    body += txt(
        bx + 14,
        y + 190,
        "LINKS TO",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=0.6,
    )
    body += txt(bx + 14, y + 214, "Generation mix", size=11, fill=INK)
    body += txt(bx + 14, y + 234, "Transition pathways", size=11, fill=INK)
    body += txt(bx + 14, y + 254, "Currency · GBP", size=11, fill=INK)
    body += line(bx + 14, y + 284, bx + back_w - 14, y + 284, stroke=LINE)
    body += para(
        bx + 14,
        y + 310,
        back_w - 28,
        "A link survives renames and moves. It records the object, not a file path.",
        size=11,
        leading=17,
    )
    return body + txt(
        bx + 14,
        y + 400,
        "No convert-to-text command.",
        size=11,
        fill=OXIDE,
        family=F_DISPLAY,
        style="italic",
    )


def fig_notes(states: StateTables) -> str:
    """Draw Facet Notes with a note tree, live embeds and relations.

    Parameters
    ----------
    states : StateTables
        The live and resolution state records passed to `window_shell` and
        `state_chip`.

    Returns
    -------
    str
    """
    body = title_block(
        64,
        70,
        "Facet Notes",
        "The document is the workspace. Prose, tables and diagrams share one page without becoming one file format.",
    )
    x, y, w, h = 64, 150, 1072, 540
    body += window_shell(
        x,
        y,
        w,
        h,
        states=states,
        title="Facet Notes — North Sea transition",
        menu=["File", "Edit", "View", "Object", "Tools", "Window", "Help"],
        status="Saved · 3 embeds · 1 stale relationship",
        state="Stale",
    )
    tree_w, back_w = 210, 220
    body += _note_tree(x, y, tree_w, h)
    body += line(x + tree_w, y + 60, x + tree_w, y + h - 26, stroke=INK)
    body += line(x + w - back_w, y + 60, x + w - back_w, y + h - 26, stroke=INK)
    ex = x + tree_w + 22
    ew = w - tree_w - back_w - 44
    body += txt(
        ex, y + 98, "North Sea transition", size=24, family=F_DISPLAY, style="italic"
    )
    body += txt(
        ex,
        y + 120,
        "Updated 14:02 · 1,240 words · 3 embeds",
        size=10,
        fill=SOFT,
        family=F_MONO,
    )
    body += para(
        ex,
        y + 152,
        ew,
        "The transition is not one decision but a sequence of small ones. Each source below stays editable, and each object keeps its own identity when the note is renamed or moved.",
        size=12,
        leading=19,
    )
    body += _embeds(ex, y, ew, states)
    body += _relations(x + w - back_w, y, back_w)
    return svg_doc(
        1200,
        760,
        "Facet Notes with a note tree and live embeds",
        "A note editor with a project tree, three embedded objects in different states, and a relations panel.",
        body=body,
    )
