"""Draw the accessibility tree and focus order figure.

The figure sets a numbered focus order inside a document window beside an
accessibility tree of roles and names. The exported `fig_accessibility`
function returns the SVG string, drawn from the shared `figuregen.palette`
colours. `figuregen.cli` calls it to write `fig-32-accessibility.svg` under
`figures/`.
"""

from __future__ import annotations

from figuregen.canvas import circle, line, para, rect, svg_doc, txt
from figuregen.ornaments import title_block
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
from figuregen.widgets import pane_head, window_shell


def fig_accessibility() -> str:
    """Draw the accessibility tree, focus order and target sizes.

    Returns
    -------
    str
    """
    body = title_block(
        64,
        70,
        "The accessibility tree is another output",
        "Names, roles, states and order come from the same scene that draws the pixels. They are not reconstructed afterwards.",
    )
    # Window with focus order.
    x, y, w, h = 64, 160, 560, 480
    body += window_shell(
        x,
        y,
        w,
        h,
        title="Facet Notes — North Sea transition",
        menu=["File", "Edit", "View", "Object", "Tools", "Window", "Help"],
        status="North Sea transition · 1 embed selected",
    )
    body += pane_head(x, y + 60, 180, "Notes")
    body += pane_head(x + 180, y + 60, 380, "Document")
    for index, label in enumerate([
        "Project",
        "North Sea transition",
        "Sources",
        "Figures",
    ]):
        ty = y + 104 + index * 28
        body += txt(x + 14, ty, label, size=11, fill=INK)
    body += txt(
        x + 202,
        y + 112,
        "North Sea transition",
        size=18,
        family=F_DISPLAY,
        style="italic",
    )
    body += para(
        x + 202,
        y + 140,
        336,
        "A note with one selected embed and a visible focus ring.",
        size=11,
        leading=16,
    )
    body += rect(x + 202, y + 194, 336, 72, fill=HIGH, stroke=OXIDE, sw=3)
    body += txt(x + 218, y + 222, "Generation mix", size=12, weight="bold")
    body += txt(x + 218, y + 240, "Table · 12 rows", size=10, fill=SOFT, family=F_MONO)
    # Focus order badges.
    for number, bx, by in [
        (1, x + 20, y + 96),
        (2, x + 500, y + 112),
        (3, x + 520, y + 206),
        (4, x + 500, y + h - 12),
    ]:
        body += circle(bx, by, 10, fill=PINE2, stroke=None)
        body += txt(
            bx,
            by + 3.5,
            str(number),
            size=9,
            fill=WHITE,
            anchor="middle",
            family=F_MONO,
            weight="bold",
        )
    # Tree.
    tx = 680
    body += txt(
        tx,
        190,
        "ACCESSIBILITY TREE",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    entries = [
        ("window", "Facet Notes — North Sea transition"),
        ("  menu bar", "File, Edit, View, Object, Tools, Window, Help"),
        ("  tree", "Notes, 7 items"),
        ("    tree item", "North Sea transition, selected"),
        ("  document", "North Sea transition"),
        ("    group", "Generation mix, table, 12 rows"),
        ("      button", "Open source"),
        ("  status", "North Sea transition, 1 embed selected"),
    ]
    for index, (role, name) in enumerate(entries):
        ey = 220 + index * 30
        body += txt(tx, ey, role, size=11, fill=PINE2, family=F_MONO, weight="bold")
        body += txt(tx + 150, ey, name, size=11, fill=INK)
        body += line(tx, ey + 8, 1136, ey + 8, stroke=LINE, sw=0.5)
    # Targets.
    body += txt(
        tx,
        490,
        "TARGETS AND CONTRAST",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    body += rect(tx, 510, 28, 28, fill=HIGH, stroke=INK)
    body += rect(tx + 52, 506, 36, 36, fill=HIGH, stroke=INK)
    body += txt(
        tx + 104, 530, "28 minimum · 36 primary", size=11, fill=SOFT, family=F_MONO
    )
    body += para(
        tx,
        566,
        456,
        "Text meets 4.5:1 at body size and 3:1 at large size. Focus is visible at 3:1 against both the control and its surround. State is never carried by colour alone.",
        size=11,
        leading=17,
    )
    body += para(
        tx,
        650,
        456,
        "The same tree drives screen readers, keyboard traversal and automated checks. If a name is missing from the scene, it is missing from every target.",
        size=11,
        leading=17,
    )
    return svg_doc(
        1200,
        760,
        "Accessibility tree and focus order",
        "A document window with numbered focus order and an accessibility tree listing roles and names, plus target-size and contrast rules.",
        body=body,
    )
