"""Figure generator module: figures.spacing."""

from __future__ import annotations

from figuregen.canvas import line, lines, rect, svg_doc, txt
from figuregen.ornaments import title_block
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


def fig_spacing() -> str:
    """Draw the spacing scale and the measured tool strip."""
    body = title_block(
        64,
        70,
        "Spacing, density and targets",
        "A four-pixel grid, eight steps, and a floor under every pointer target.",
    )
    steps = [4, 8, 12, 16, 24, 32, 48, 64]
    for index, step in enumerate(steps):
        y = 166 + index * 58
        body += txt(
            64, y + 14, str(step), size=10, fill=SOFT, family=F_MONO, anchor="end"
        )
        body += rect(80, y, step * 3, 22, fill=PINE2, stroke=None)
        body += txt(
            92 + step * 3, y + 16, f"{step} px", size=10, fill=SOFT, family=F_MONO
        )
    body += txt(
        64,
        660,
        "Use 4/8/12/16 for in-pane rhythm; 24/32/48/64 for structure.",
        size=11,
        fill=SOFT,
    )

    body += rect(600, 166, 536, 390, fill=HIGH, stroke=INK)
    body += txt(
        620,
        196,
        "A measured tool strip",
        size=11,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=0.8,
    )
    body += rect(620, 224, 496, 58, fill=PAPER, stroke=LINE)
    body += rect(636, 238, 30, 30, fill=WHITE, stroke=INK, sw=2)
    body += txt(651, 258, "↖", size=16, anchor="middle")
    body += rect(674, 238, 30, 30, fill=WHITE, stroke=LINE)
    body += txt(689, 258, "T", size=14, anchor="middle")
    body += rect(712, 238, 30, 30, fill=WHITE, stroke=LINE)
    body += txt(727, 258, "□", size=14, anchor="middle")
    body += txt(760, 258, "Body · 10.5 pt · 14 pt", size=10, fill=SOFT, family=F_MONO)
    body += rect(1000, 238, 100, 30, fill="#E7F0ED", stroke=PINE2)
    body += txt(1010, 258, "3 tools", size=10, fill=PINE2, family=F_MONO, weight="bold")

    # Dimension lines.
    body += line(636, 300, 666, 300, stroke=OXIDE, sw=1)
    body += line(636, 294, 636, 306, stroke=OXIDE)
    body += line(666, 294, 666, 306, stroke=OXIDE)
    body += txt(651, 320, "30", size=9, fill=OXIDE, family=F_MONO, anchor="middle")
    body += line(666, 336, 674, 336, stroke=OXIDE)
    body += txt(670, 352, "8", size=9, fill=OXIDE, family=F_MONO, anchor="middle")
    body += line(620, 366, 1116, 366, stroke=OXIDE, dash="3 3")
    body += txt(620, 386, "16 px pane padding", size=9, fill=OXIDE, family=F_MONO)
    body += lines(
        620,
        432,
        [
            "Minimum target 28 x 28. Preferred 32 x 32.",
            "Primary action 36 high; dialog buttons 32 high.",
            "Hit slop may extend 4 px beyond a drawn glyph.",
        ],
        size=11,
        fill=SOFT,
        leading=20,
    )
    body += txt(
        600,
        600,
        "Density is a property of the pane, not an excuse to shrink the hit target.",
        size=13,
        fill=SOFT,
        family=F_DISPLAY,
        style="italic",
    )
    return svg_doc(
        1200,
        720,
        "Spacing scale and measured tool strip",
        "Eight spacing steps and an annotated toolbar with target and padding measurements.",
        body=body,
    )
