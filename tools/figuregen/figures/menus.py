"""Draw the menu bar with an open File menu figure.

The figure shows an open File menu with shortcuts, a disabled item and
separators. The exported `fig_menus` function returns the SVG string, drawn
from the shared `figuregen.palette` colours. `figuregen.cli` calls it to write
`fig-14-menus.svg` under `figures/`.
"""

from __future__ import annotations

from figuregen.canvas import line, lines, para, rect, svg_doc, txt
from figuregen.ornaments import title_block
from figuregen.palette import F_MONO, HIGH, INK, LINE, OXIDE, PINE2, SOFT
from figuregen.widgets import window_shell


def fig_menus() -> str:
    """Draw a menu bar with an open File menu.

    Returns
    -------
    str
    """
    body = title_block(
        64,
        70,
        "Menus name commands",
        "A menu is a list of verbs. It is not a catalogue of everything the application can do.",
    )
    x, y, w, h = 64, 160, 700, 450
    body += window_shell(
        x,
        y,
        w,
        h,
        title="Facet Notes — North Sea transition",
        menu=["File", "Edit", "View", "Object", "Tools", "Window", "Help"],
        active_menu="File",
        status="North Sea transition · saved 14:02",
    )
    # Open File menu.
    mx, my, mw = x + 8, y + 60, 300
    body += rect(mx + 4, my + 4, mw, 352, fill="#17201C18", stroke=None)
    body += rect(mx, my, mw, 352, fill=HIGH, stroke=INK)
    items = [
        ("New note", "Ctrl+N", "normal"),
        ("New from template…", "", "normal"),
        ("Open…", "Ctrl+O", "normal"),
        ("sep", "", ""),
        ("Save", "Ctrl+S", "normal"),
        ("Save as…", "Ctrl+Shift+S", "normal"),
        ("Revert to saved", "", "disabled"),
        ("sep", "", ""),
        ("Export", "▸", "normal"),
        ("sep", "", ""),
        ("Close", "Ctrl+W", "normal"),
        ("Quit", "Ctrl+Q", "normal"),
    ]
    row = 0
    for label, shortcut, kind in items:
        item_y = my + 8 + row * 28
        if label == "sep" or kind == "sep":
            body += line(mx + 10, item_y + 14, mx + mw - 10, item_y + 14, stroke=LINE)
            row += 1
            continue
        if kind == "disabled":
            body += txt(mx + 18, item_y + 18, label, size=12, fill=LINE)
            row += 1
            continue
        body += txt(mx + 18, item_y + 18, label, size=12, fill=INK)
        if shortcut:
            body += txt(
                mx + mw - 18,
                item_y + 18,
                shortcut,
                size=11,
                fill=SOFT,
                family=F_MONO,
                anchor="end",
            )
        row += 1
    # Hover highlight on Save.
    body += rect(
        mx + 6, my + 8 + 4 * 28, mw - 12, 28, fill=PINE2, stroke=None, opacity=0.12
    )
    # Notes.
    nx = 820
    body += txt(
        nx, 190, "RULES", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1
    )
    body += lines(
        nx,
        222,
        [
            "Name commands with verbs.",
            "Show the shortcut beside the item.",
            "Disable a command that is unavailable for now.",
            "Omit one that can never apply to the object.",
            "Every menu command is also searchable.",
            "Quit is always Ctrl+Q.",
        ],
        size=11,
        leading=28,
        fill=SOFT,
    )
    body += line(nx, 414, 1136, 414, stroke=LINE)
    body += para(
        nx,
        440,
        316,
        "Submenus collect variations of one verb. They do not bury unrelated features. A submenu that exists only to shorten a long menu should be removed.",
        size=11,
        leading=17,
    )
    body += para(
        nx,
        522,
        316,
        "Menu bars stay visible. When the window is narrow, whole menus move into More; commands do not become a hamburger.",
        size=11,
        leading=17,
    )
    return svg_doc(
        1200,
        760,
        "A menu bar with an open File menu",
        "A File menu showing commands, shortcuts, a disabled item and separators, with rules for naming and availability.",
        body=body,
    )
