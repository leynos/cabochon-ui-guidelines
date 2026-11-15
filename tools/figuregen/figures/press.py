"""Draw the Cabochon Press window figure.

The window shows a pages panel, an A4 page with bleed and crop marks, and a
preflight panel. The exported `fig_press` function returns the SVG string,
drawn from the shared `figuregen.palette` colours. `figuregen.cli` calls it to
write `fig-24-press.svg` under `figures/`.
"""

# Figure builders hold one local per drawing coordinate; see the matching
# ruff exemption for tools/figuregen in pyproject.toml.

from __future__ import annotations

import typing as typ

from figuregen.canvas import line, para, rect, svg_doc, txt
from figuregen.ornaments import title_block
from figuregen.palette import (
    AMBER_INK,
    F_DISPLAY,
    F_MONO,
    INK,
    LINE,
    OXIDE,
    PAPER,
    PINE2,
    SOFT,
    TEAL,
    TEAL_INK,
    WHITE,
)
from figuregen.widgets import button, pane_head, window_shell

if typ.TYPE_CHECKING:
    from figuregen.figdata import StateTables


def fig_press(states: StateTables) -> str:  # pylint: disable=too-many-locals
    """Draw Cabochon Press with pages and preflight.

    Parameters
    ----------
    states : StateTables
        The live and resolution state records passed to `window_shell`.

    Returns
    -------
    str
    """
    body = title_block(
        64,
        70,
        "Cabochon Press",
        "A page is a surface with intent. Press shows the page, its pages panel and its preflight in one window.",
    )
    x, y, w, h = 64, 150, 1072, 540
    body += window_shell(
        x,
        y,
        w,
        h,
        states=states,
        title="Cabochon Press — Currency brief",
        menu=["File", "Edit", "View", "Page", "Object", "Window", "Help"],
        status="Page 2 of 6 · PDF/X-4 · 3 mm bleed",
        state="Current",
    )
    pages_w = 150
    body += rect(x, y + 60, pages_w, h - 86, fill=PAPER, stroke=None)
    body += pane_head(x, y + 60, pages_w, "Pages", right="+")
    for index in range(6):
        py = y + 98 + index * 64
        body += rect(
            x + 14,
            py,
            52,
            44,
            fill=WHITE,
            stroke=OXIDE if index == 1 else LINE,
            sw=2 if index == 1 else 1,
        )
        body += txt(x + 78, py + 18, f"0{index + 1}", size=10, fill=INK, family=F_MONO)
        body += txt(
            x + 78,
            py + 34,
            "A4" if index < 4 else "Plate",
            size=9,
            fill=SOFT,
            family=F_MONO,
        )
    body += line(x + pages_w, y + 60, x + pages_w, y + h - 26, stroke=INK)
    # Page.
    px, py, pw, ph = x + pages_w + 60, y + 82, 430, 384
    body += rect(px + 14, py + 14, pw, ph, fill="#17201C18", stroke=None)
    body += rect(px, py, pw, ph, fill=WHITE, stroke=INK)
    body += txt(
        px + 32,
        py + 62,
        "A currency for the",
        size=26,
        family=F_DISPLAY,
        style="italic",
    )
    body += txt(
        px + 32,
        py + 94,
        "North Sea transition",
        size=26,
        family=F_DISPLAY,
        style="italic",
    )
    body += line(px + 32, py + 116, px + pw - 32, py + 116, stroke=INK)
    body += para(
        px + 32,
        py + 146,
        pw - 64,
        "A short brief for the first Cabochon currency object, with its sources and its print presentation.",
        size=11,
        leading=16,
    )
    body += rect(px + 32, py + 220, pw - 64, 120, fill=PAPER, stroke=LINE)
    body += txt(
        px + 46,
        py + 246,
        "GBP · 1.00",
        size=20,
        fill=PINE2,
        family=F_MONO,
        weight="bold",
    )
    body += txt(
        px + 46,
        py + 268,
        "Source · European Central Bank",
        size=10,
        fill=SOFT,
        family=F_MONO,
    )
    for row in range(4):
        body += line(
            px + 46,
            py + 286 + row * 12,
            px + pw - 46,
            py + 286 + row * 12,
            stroke=LINE,
            sw=0.5,
        )
    # Crop marks and bleed.
    for cx1, cy1, cx2, cy2 in [
        (px - 18, py, px - 6, py),
        (px, py - 18, px, py - 6),
        (px + pw + 6, py, px + pw + 18, py),
        (px, py + ph + 6, px, py + ph + 18),
    ]:
        body += line(cx1, cy1, cx2, cy2, stroke=INK, sw=0.8)
    body += line(px - 12, py - 12, px + pw + 12, py - 12, stroke=TEAL, dash="3 4")
    body += line(
        px - 12, py + ph + 12, px + pw + 12, py + ph + 12, stroke=TEAL, dash="3 4"
    )
    body += txt(
        px + pw + 20, py + ph + 16, "bleed 3 mm", size=9, fill=TEAL_INK, family=F_MONO
    )
    # Preflight.
    ix = x + w - 300
    body += rect(ix, y + 60, 300, h - 86, fill=PAPER, stroke=None)
    body += line(ix, y + 60, ix, y + h - 26, stroke=INK)
    body += pane_head(ix, y + 60, 300, "Preflight")
    checks = [
        ("Fonts embedded", True),
        ("Images at 300 dpi", True),
        ("Colour intent PDF/X-4", True),
        ("Bleed 3 mm", True),
        ("Live object will flatten", False),
    ]
    for index, (label, ok) in enumerate(checks):
        cy = y + 116 + index * 40
        body += txt(
            ix + 16,
            cy,
            "✓" if ok else "!",
            size=14,
            fill=PINE2 if ok else AMBER_INK,
            weight="bold",
        )
        body += txt(ix + 38, cy, label, size=11, fill=INK if ok else AMBER_INK)
        body += line(ix + 16, cy + 14, ix + 284, cy + 14, stroke=LINE, sw=0.5)
    body += para(
        ix + 16,
        y + 340,
        268,
        "A live object prints through its print presentation. Press reports the resolution and intent it will use, and never silently exports the screen view.",
        size=11,
        leading=17,
    )
    body += button(ix + 16, y + 438, 124, "Proof", height=32)
    body += button(ix + 152, y + 438, 132, "Export PDF", primary=True, height=32)
    return svg_doc(
        1200,
        760,
        "Cabochon Press with pages and preflight",
        "A page-layout window with a pages panel, an A4 page with bleed and crop marks, and a preflight panel checking fonts, images, colour and bleed.",
        body=body,
    )
