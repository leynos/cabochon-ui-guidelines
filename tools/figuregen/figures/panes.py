"""Draw the pane layout figure.

Navigator, document and inspector panes appear with minimum widths, a splitter
and a collapsed pane. The exported `fig_panes` function returns the SVG
string, drawn from the shared `figuregen.palette` colours. `figuregen.cli`
calls it to write `fig-16-panes.svg` under `figures/`.
"""

from __future__ import annotations

from figuregen.canvas import line, para, path, rect, svg_doc, txt
from figuregen.ornaments import title_block
from figuregen.palette import F_MONO, HIGH, INK, LINE, OXIDE, PAPER, SOFT
from figuregen.widgets import pane_head


def fig_panes() -> str:
    """Draw the pane layout with minimum widths and splitters."""
    body = title_block(
        64,
        70,
        "Panes that keep their promises",
        "A pane has a name, a minimum width and a remembered position. It never disappears without leaving a handle.",
    )
    # Diagram.
    x, y, h = 64, 170, 360
    body += rect(x, y, 210, h, fill=PAPER, stroke=INK)
    body += pane_head(x, y, 210, "Navigator")
    body += para(
        x + 14,
        y + 56,
        182,
        "Project tree, saved views and recent objects.",
        size=11,
        leading=16,
    )
    body += rect(x + 210, y, 6, h, fill=LINE, stroke=INK)
    body += rect(x + 216, y, 632, h, fill=HIGH, stroke=INK)
    body += pane_head(x + 216, y, 632, "Document")
    body += para(
        x + 238,
        y + 56,
        588,
        "The document takes the remaining width. It is the only pane that may grow without limit.",
        size=11,
        leading=16,
    )
    body += rect(x + 848, y, 240, h, fill=PAPER, stroke=INK)
    body += pane_head(x + 848, y, 240, "Inspector")
    body += para(
        x + 862,
        y + 56,
        212,
        "Identity, presentation, state and capabilities for the selection.",
        size=11,
        leading=16,
    )
    for px, label in [
        (x + 105, "210 min"),
        (x + 532, "flexible · ≥ 420"),
        (x + 968, "240 min"),
    ]:
        body += txt(
            px, y + h + 22, label, size=10, fill=SOFT, family=F_MONO, anchor="middle"
        )
    body += line(x, y + h + 8, x + 210, y + h + 8, stroke=LINE)
    body += line(x + 216, y + h + 8, x + 848, y + h + 8, stroke=LINE)
    body += line(x + 848, y + h + 8, x + 1088, y + h + 8, stroke=LINE)
    # Splitter detail.
    body += txt(
        64,
        596,
        "SPLITTER",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    body += rect(64, 620, 6, 80, fill=LINE, stroke=INK)
    body += line(70, 620, 250, 620, stroke=LINE, dash="2 4")
    body += line(70, 700, 250, 700, stroke=LINE, dash="2 4")
    body += txt(270, 640, "6 px visible rule, 8 px hit area", size=11, fill=SOFT)
    body += txt(270, 662, "Double-click restores the default", size=11, fill=SOFT)
    body += txt(270, 684, "Drag is immediate; no preview pane", size=11, fill=SOFT)
    # Collapsed pane.
    body += txt(
        620,
        596,
        "COLLAPSED",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    body += rect(620, 620, 42, 120, fill=PAPER, stroke=INK)
    body += txt(
        641, 660, "Inspector", size=10, fill=SOFT, anchor="middle", family=F_MONO
    )
    body += path("M 632 740 L 650 740 M 641 732 L 641 748", stroke=INK, sw=1.5)
    body += txt(
        680, 646, "A collapsed pane keeps its head and handle.", size=11, fill=SOFT
    )
    body += txt(680, 668, "Its state is remembered per project.", size=11, fill=SOFT)
    body += txt(680, 690, "It never reopens at a new width.", size=11, fill=SOFT)
    body += para(
        64,
        744,
        1072,
        "Two panes beside a document is the practical limit. A third pane becomes a tab or a separate window. Nested splitters are allowed only when each level keeps a named head.",
        size=11,
        leading=16,
    )
    return svg_doc(
        1200,
        800,
        "Pane layout with minimum widths and splitters",
        "Navigator, document and inspector panes with minimum widths, a splitter detail and a collapsed pane.",
        body=body,
    )
