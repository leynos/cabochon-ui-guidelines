"""Draw the object inspector figure.

The panel lists an object's identity, presentation, authority and state. The
exported `fig_inspector` function returns the SVG string, drawn from the shared
`figuregen.palette` colours. `figuregen.cli` calls it to write
`fig-17-inspector.svg` under `figures/`.
"""

from __future__ import annotations

from figuregen.canvas import line, lines, para, rect, svg_doc, txt
from figuregen.ornaments import state_chip, title_block
from figuregen.palette import F_DISPLAY, F_MONO, INK, LINE, OXIDE, PAPER, PINE2, SOFT
from figuregen.widgets import inspector_row, pane_head, radio


def fig_inspector() -> str:
    """Draw the object inspector."""
    body = title_block(
        64,
        70,
        "The inspector explains the object",
        "Identity, presentation, state and authority, in that order. The inspector describes; it does not become a second application.",
    )
    x, y, w, h = 64, 160, 420, 580
    body += rect(x + 6, y + 6, w, h, fill="#17201C18", stroke=None)
    body += rect(x, y, w, h, fill=PAPER, stroke=INK)
    body += pane_head(x, y, w, "Inspector", right="object")
    ix, iw = x + 16, w - 32
    body += txt(ix, y + 52, "Generation mix", size=18, family=F_DISPLAY, style="italic")
    body += txt(ix, y + 72, "Table · obj:8f3a", size=11, fill=SOFT, family=F_MONO)
    state_body, _ = state_chip(x + w - 110, y + 38, "Current")
    body += state_body
    body += txt(
        ix,
        y + 106,
        "IDENTITY",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=0.7,
    )
    body += inspector_row(ix, y + 130, iw, "Object", value="obj:8f3a")
    body += inspector_row(ix, y + 154, iw, "Provider", value="enfilade.table")
    body += inspector_row(ix, y + 178, iw, "Revision", value="r17")
    body += inspector_row(ix, y + 202, iw, "Parent", value="note:transition")
    body += txt(
        ix,
        y + 238,
        "PRESENTATION",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=0.7,
    )
    for index, (name, detail) in enumerate([
        ("In note", "12 rows · 4 columns"),
        ("Dataframe", "focused editor"),
        ("Print", "facing page"),
    ]):
        ry = y + 262 + index * 34
        body += radio(ix, ry, name, selected=index == 0)
        body += txt(ix + 110, ry, detail, size=11, fill=SOFT, family=F_MONO)
    body += txt(
        ix,
        y + 356,
        "STATE",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=0.7,
    )
    state_body, _ = state_chip(ix, y + 368, "Current")
    body += state_body
    body += txt(ix, y + 406, "Last refresh", size=11, fill=INK)
    body += txt(
        ix + iw, y + 406, "14:02", size=11, fill=SOFT, anchor="end", family=F_MONO
    )
    body += line(ix, y + 424, ix + iw, y + 424, stroke=LINE)
    body += txt(
        ix,
        y + 444,
        "AUTHORITY",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=0.7,
    )
    body += txt(ix, y + 468, "Read", size=11, fill=INK)
    body += txt(
        ix + iw, y + 468, "granted", size=11, fill=PINE2, anchor="end", family=F_MONO
    )
    body += txt(ix, y + 490, "Write", size=11, fill=INK)
    body += txt(
        ix + iw, y + 490, "granted", size=11, fill=PINE2, anchor="end", family=F_MONO
    )
    body += txt(ix, y + 512, "Share", size=11, fill=INK)
    body += txt(
        ix + iw, y + 512, "denied", size=11, fill=OXIDE, anchor="end", family=F_MONO
    )
    body += line(ix, y + 530, ix + iw, y + 530, stroke=LINE)
    body += txt(
        ix,
        y + 552,
        "The last value is kept while the source is refreshed.",
        size=11,
        fill=SOFT,
    )
    # Annotations.
    ax = 540
    body += txt(
        ax,
        190,
        "WHAT BELONGS",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    body += lines(
        ax,
        222,
        [
            "Stable identity and revision.",
            "Every presentation of the object.",
            "The state of each live relationship.",
            "The grants that allow an action.",
            "The provider that owns the data.",
        ],
        size=11,
        leading=28,
        fill=SOFT,
    )
    body += txt(
        ax,
        402,
        "WHAT DOES NOT",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    body += lines(
        ax,
        434,
        [
            "A second copy of the document.",
            "Raw provider diagnostics as primary text.",
            "A place to edit every property at once.",
            "A marketing surface for unused features.",
        ],
        size=11,
        leading=28,
        fill=SOFT,
    )
    body += line(ax, 580, 1136, 580, stroke=LINE)
    body += para(
        ax,
        606,
        596,
        "The inspector is read-mostly by default. Editing a property happens in the document or in the focused editor, through a transaction. The inspector may offer the same command, but it does not invent a parallel editing model.",
        size=12,
        leading=19,
    )
    return svg_doc(
        1200,
        760,
        "Object inspector",
        "An inspector panel listing identity, presentation, authority and state, with notes on what belongs and what does not.",
        body=body,
    )
