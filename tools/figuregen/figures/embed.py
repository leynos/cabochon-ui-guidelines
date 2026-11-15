"""Draw the embed envelope and provider figure.

The figure shows a note embed resolving to its provider, with the resolved,
opaque, unavailable and malformed outcomes below. The exported `fig_embed`
function returns the SVG string, drawn from the resolution state records of
the `figuregen.figdata` catalogue. `figuregen.cli` calls it to write
`fig-29-embed.svg` under `figures/`.
"""

from __future__ import annotations

import typing as typ

from figuregen.canvas import line, para, path, rect, svg_doc, txt
from figuregen.ornaments import mark_group, state_chip, state_mark, title_block
from figuregen.palette import F_DISPLAY, F_MONO, HIGH, INK, LINE, OXIDE, PAPER, SOFT
from figuregen.widgets import inspector_row, pane_head

if typ.TYPE_CHECKING:
    from figuregen.figdata import Catalogue


def fig_embed(catalogue: Catalogue) -> str:
    """Draw the embed envelope, provider and failure states.

    Parameters
    ----------
    catalogue : Catalogue
        The figure catalogue, which supplies the resolution state records and
        the state tables.

    Returns
    -------
    str
    """
    body = title_block(
        64,
        70,
        "An embed is a promise",
        "The document owns a presentation. The object keeps its identity, its provider and its state.",
    )
    # Document side.
    dx, dy, dw, dh = 64, 180, 340, 380
    body += rect(dx, dy, dw, dh, fill=HIGH, stroke=INK)
    body += pane_head(dx, dy, dw, "Document")
    body += txt(
        dx + 18,
        dy + 54,
        "North Sea transition",
        size=16,
        family=F_DISPLAY,
        style="italic",
    )
    body += para(
        dx + 18,
        dy + 82,
        dw - 36,
        "The note contains a table. The table is not copied into the note file.",
        size=11,
        leading=16,
    )
    body += rect(dx + 18, dy + 150, dw - 36, 120, fill=PAPER, stroke=LINE)
    body += txt(dx + 32, dy + 176, "Generation mix", size=12, weight="bold")
    body += txt(dx + 32, dy + 194, "Table · 12 rows", size=10, fill=SOFT, family=F_MONO)
    state_body, _ = state_chip(dx + dw - 122, dy + 166, "Current", catalogue.states)
    body += state_body
    for row in range(3):
        body += line(
            dx + 32,
            dy + 210 + row * 16,
            dx + dw - 32,
            dy + 210 + row * 16,
            stroke=LINE,
            sw=0.5,
        )
    body += txt(
        dx + 18,
        dy + 316,
        "EMBED ENVELOPE",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=0.6,
    )
    body += txt(
        dx + 18, dy + 340, "obj:8f3a · r17 · table", size=11, fill=INK, family=F_MONO
    )
    body += txt(
        dx + 18, dy + 360, "presentation: in-note", size=11, fill=INK, family=F_MONO
    )
    # Arrow.
    ax = dx + dw + 30
    body += line(ax, 330, ax + 130, 330, stroke=INK, sw=2)
    body += path(
        f"M {ax + 122} 322 L {ax + 134} 330 L {ax + 122} 338", stroke=INK, sw=2
    )
    body += txt(ax + 6, 320, "resolve", size=10, fill=SOFT, family=F_MONO)
    # Provider side.
    px = ax + 160
    body += rect(px, 180, 340, 240, fill=PAPER, stroke=INK)
    body += pane_head(px, 180, 340, "Provider")
    body += txt(px + 18, 234, "enfilade.table", size=13, weight="bold", family=F_MONO)
    body += txt(px + 18, 254, "owns payload · revisions · grants", size=10, fill=SOFT)
    body += inspector_row(px + 18, 286, 304, "Object", value="obj:8f3a")
    body += inspector_row(px + 18, 310, 304, "Revision", value="r17")
    body += inspector_row(px + 18, 334, 304, "State", value="current")
    body += txt(
        px + 18, 372, "A second presentation reads the same object.", size=10, fill=SOFT
    )
    # States.
    body += txt(
        64,
        612,
        "HOW RESOLUTION ENDS",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    states = [
        ("Resolved", "provider answered"),
        ("Opaque", "unknown object type"),
        ("Unavailable", "provider absent"),
        ("Malformed", "payload unreadable"),
    ]
    for index, (name, detail) in enumerate(states):
        sx = 64 + index * 216
        state = catalogue.resolution_states[name]
        colour = str(state["colour"])
        mark = str(state["mark"])
        body += '<g data-state-card="true">'
        body += rect(sx, 630, 200, 58, fill=HIGH, stroke=colour)
        body += mark_group(
            mark,
            str(state["id"]),
            str(state["role"]),
            state_mark(sx + 18, 652, mark, colour),
        )
        body += txt(
            sx + 32,
            652,
            name,
            size=12,
            fill=colour,
            weight="bold",
            data_state=str(state["id"]),
        )
        body += txt(sx + 12, 672, detail, size=10, fill=SOFT, family=F_MONO)
        body += "</g>"
    body += para(
        944,
        638,
        192,
        "Resolved embeds only: Current · Refreshing · Stale · Broken · Denied",
        size=10,
        leading=15,
    )
    body += para(
        64,
        710,
        1072,
        "No state deletes the embed or flattens it into pixels. A cached value stays visible only while one exists and authority permits it; its state and the operation that would restore it are shown. Denied shows no protected value.",
        size=11,
        leading=16,
    )
    return svg_doc(
        1200,
        760,
        "Embed envelope and provider",
        "A document embed pointing to a provider-owned object, with the five failure states listed below.",
        body=body,
    )
