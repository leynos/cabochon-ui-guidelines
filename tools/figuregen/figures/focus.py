"""Figure generator module: figures.focus."""

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
from figuregen.widgets import button


def fig_focus() -> str:
    """Draw the focus ring, tab order and keyboard map."""
    body = title_block(
        64,
        70,
        "Focus is a place you can see",
        "The keyboard reaches everything. The focus ring is never removed to make a screenshot look calmer.",
    )
    # Focus ring anatomy.
    body += txt(
        64,
        158,
        "FOCUS RING",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    body += rect(64, 180, 260, 150, fill=HIGH, stroke=LINE)
    body += button(96, 222, 150, "Open source", primary=True)
    body += rect(93, 219, 156, 38, fill="none", stroke=OXIDE, sw=3)
    body += line(252, 200, 286, 200, stroke=OXIDE)
    body += txt(292, 204, "3 px oxide", size=10, fill=OXIDE, family=F_MONO)
    body += line(252, 238, 286, 238, stroke=OXIDE)
    body += txt(292, 242, "3 px offset", size=10, fill=OXIDE, family=F_MONO)
    body += txt(
        64, 360, "Only the focused control carries the ring.", size=10, fill=SOFT
    )
    # Tab order.
    body += txt(
        420,
        158,
        "TAB ORDER",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    steps = [
        ("1", "Navigator tree"),
        ("2", "Splitter after the navigator"),
        ("3", "Document body"),
        ("4", "First embed or object"),
        ("5", "Splitter before the inspector"),
        ("6", "Inspector fields"),
        ("7", "Status line actions"),
    ]
    for index, (number, label) in enumerate(steps):
        sy = 180 + index * 32
        body += circle(434, sy - 4, 10, fill=PINE2, stroke=None)
        body += txt(
            434,
            sy,
            number,
            size=10,
            fill=WHITE,
            anchor="middle",
            family=F_MONO,
            weight="bold",
        )
        body += txt(458, sy, label, size=12, fill=INK)
        if index < len(steps) - 1:
            body += line(434, sy + 8, 434, sy + 20, stroke=LINE)
    # Key table.
    body += txt(
        64,
        430,
        "KEYS THAT MUST WORK",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    keys = [
        ("Tab / Shift+Tab", "move between groups and controls"),
        ("Arrow keys", "move within a tree, list or grid"),
        ("Enter", "activate the focused control"),
        ("Space", "toggle a checkbox or press a button"),
        ("Esc", "dismiss a menu, popover or dialog"),
        ("F6", "cycle panes"),
        ("F1", "open help for the focused object"),
        ("Ctrl+Q", "quit the application"),
    ]
    for index, (key, action) in enumerate(keys):
        ky = 462 + index * 28
        body += txt(64, ky, key, size=11, fill=INK, family=F_MONO, weight="bold")
        body += txt(300, ky, action, size=11, fill=SOFT)
        body += line(64, ky + 8, 740, ky + 8, stroke=LINE, sw=0.5)
    body += para(
        780,
        186,
        356,
        "Focus moves in reading order. A composite control is one stop; arrows move inside it. The ring is drawn outside the control so it never changes the layout.",
        size=11,
        leading=18,
    )
    body += para(
        780,
        300,
        356,
        "Shortcuts are labels, not secrets. Every shortcut appears beside its command in a menu and is searchable in the command palette.",
        size=11,
        leading=18,
    )
    body += para(
        780,
        414,
        356,
        "A window that loses focus keeps a muted focus memory. When it returns, the last focused control receives the ring again.",
        size=11,
        leading=18,
    )
    body += txt(
        780,
        540,
        "Never trap focus except in a modal dialog.",
        size=12,
        fill=OXIDE,
        family=F_DISPLAY,
        style="italic",
    )
    return svg_doc(
        1200,
        760,
        "Focus ring, tab order and keyboard map",
        "A focus ring measured at three pixels with a three pixel offset, a tab order for a document window, and the essential keyboard commands.",
        body=body,
    )
