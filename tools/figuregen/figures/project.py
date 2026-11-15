"""Draw the project window figure.

The window shows a file tree, a document list with live states and an identity
panel. The exported `fig_project` function returns the SVG string, drawn from
the shared `figuregen.palette` colours. `figuregen.cli` calls it to write
`fig-28-project.svg` under `figures/`.
"""

# Figure builders hold one local per drawing coordinate; see the matching
# ruff exemption for tools/figuregen in pyproject.toml.

from __future__ import annotations

from figuregen.canvas import line, para, rect, svg_doc, txt
from figuregen.ornaments import state_chip, title_block
from figuregen.palette import (
    F_DISPLAY,
    F_MONO,
    HIGH,
    INK,
    LINE,
    OXIDE,
    PAPER,
    PINE2,
    SOFT,
    WHITE,
)
from figuregen.widgets import inspector_row, pane_head, window_shell


def _chip_width(name: str) -> float:
    """Measure a state chip without keeping its drawing.

    Parameters
    ----------
    name : str
        State name.

    Returns
    -------
    float
        The chip's width in logical units, so a card can right-align it.
    """
    _, width = state_chip(0, 0, name)
    return width


def fig_project() -> str:  # pylint: disable=too-many-locals
    """Draw the project window with tree, documents and identity panel.

    Returns
    -------
    str
    """
    body = title_block(
        64,
        70,
        "A project is a working context",
        "Documents, objects, links, tools and views belong to a project. Renaming a file does not rename the object behind it.",
    )
    x, y, w, h = 64, 150, 1072, 520
    body += window_shell(
        x,
        y,
        w,
        h,
        title="Projects — North Sea transition",
        menu=["File", "Edit", "View", "Project", "Window", "Help"],
        status="3 documents · 8 objects · 2 links",
        state="Current",
    )
    left_w, right_w = 260, 280
    body += rect(x, y + 60, left_w, h - 86, fill=PAPER, stroke=None)
    body += pane_head(x, y + 60, left_w, "Project")
    tree = [
        ("North Sea transition", 0),
        ("notes/", 1),
        ("transition.md", 2),
        ("sources.md", 2),
        ("data/", 1),
        ("generation.csv", 2),
        ("figures/", 1),
        ("plate.svg", 2),
    ]
    for index, (name, depth) in enumerate(tree):
        ty = y + 100 + index * 30
        selected = name == "transition.md"
        if selected:
            body += rect(x, ty - 18, left_w, 27, fill=PINE2, stroke=None)
        body += txt(
            x + 14 + depth * 16,
            ty,
            name,
            size=11,
            fill=WHITE if selected else (INK if depth < 2 else SOFT),
        )
    body += line(x + left_w, y + 60, x + left_w, y + h - 26, stroke=INK)
    # Centre list. The identity panel begins at rx, so the cards stop a
    # 24-unit gutter short of it and the separator never covers their border.
    rx = x + w - right_w
    cx = x + left_w + 24
    card_w = rx - cx - 24
    body += txt(cx, y + 98, "Documents", size=16, family=F_DISPLAY, style="italic")
    docs = [
        ("transition.md", "note:transition", "3 embeds · updated 14:02", "Current"),
        ("sources.md", "note:sources", "12 links · updated 13:40", "Current"),
        ("generation.csv", "obj:8f3a", "table · 12 rows", "Stale"),
    ]
    for index, (name, identity, detail, state) in enumerate(docs):
        dy = y + 120 + index * 92
        body += rect(cx, dy, card_w, 76, fill=HIGH, stroke=LINE)
        body += txt(cx + 16, dy + 26, name, size=12, weight="bold")
        body += txt(cx + 16, dy + 46, identity, size=11, fill=SOFT, family=F_MONO)
        body += txt(cx + 16, dy + 64, detail, size=11, fill=SOFT)
        chip_x = cx + card_w - 12 - _chip_width(state)
        state_body, _ = state_chip(chip_x, dy + 14, state)
        body += state_body
    body += para(
        cx,
        y + 430,
        card_w,
        "A project remembers which views were open, which panes were collapsed and which objects were pinned. It does not own the objects inside it.",
        size=11,
        leading=17,
    )
    # Right links.
    body += rect(rx, y + 60, right_w, h - 86, fill=PAPER, stroke=None)
    body += line(rx, y + 60, rx, y + h - 26, stroke=INK)
    body += pane_head(rx, y + 60, right_w, "Identity")
    body += inspector_row(
        rx + 14, y + 116, right_w - 28, "Document", value="note:transition"
    )
    body += inspector_row(
        rx + 14, y + 140, right_w - 28, "File", value="notes/transition.md"
    )
    body += inspector_row(rx + 14, y + 164, right_w - 28, "Revision", value="r42")
    body += txt(
        rx + 14,
        y + 200,
        "RENAME",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=0.6,
    )
    body += para(
        rx + 14,
        y + 224,
        right_w - 28,
        "Moving notes/transition.md to notes/archive/transition.md keeps note:transition and every link to it.",
        size=11,
        leading=17,
    )
    body += line(rx + 14, y + 312, rx + right_w - 14, y + 312, stroke=LINE)
    body += txt(rx + 14, y + 340, "Recent views", size=11, weight="bold")
    body += txt(rx + 14, y + 364, "Note · editor", size=11, fill=SOFT)
    body += txt(rx + 14, y + 384, "Table · generation", size=11, fill=SOFT)
    body += txt(rx + 14, y + 404, "Output · print proof", size=11, fill=SOFT)
    return svg_doc(
        1200,
        760,
        "Project window with tree, documents and identity panel",
        "A project window showing a file tree, a document list with live states and an identity panel explaining rename behaviour.",
        body=body,
    )
