"""Draw the motion timing chart figure.

The chart plots ease-out curves for 80, 140 and 180 millisecond transitions.
The exported `fig_motion` function returns the SVG string, drawn from the
shared `figuregen.palette` colours. `figuregen.cli` calls it to write
`fig-12-motion.svg` under `figures/`.
"""

from __future__ import annotations

from figuregen.canvas import circle, line, lines, path, rect, svg_doc, txt
from figuregen.ornaments import title_block
from figuregen.palette import F_DISPLAY, F_MONO, HIGH, INK, OXIDE, PINE2, SOFT, TEAL


def fig_motion() -> str:
    """Draw the motion timing chart."""
    body = title_block(
        64,
        70,
        "Motion with a reason",
        "Motion explains a change of state. It does not perform.",
    )
    # Axes.
    ox, oy = 150, 560
    w, h = 760, 360
    body += line(ox, oy, ox + w, oy, stroke=INK)
    body += line(ox, oy, ox, oy - h, stroke=INK)
    for index in range(5):
        x = ox + index * w / 4
        body += line(x, oy, x, oy + 6, stroke=INK)
        body += txt(
            x,
            oy + 24,
            f"{index * 55}",
            size=9,
            fill=SOFT,
            family=F_MONO,
            anchor="middle",
        )
    body += txt(
        ox + w / 2,
        oy + 50,
        "milliseconds",
        size=10,
        fill=SOFT,
        family=F_MONO,
        anchor="middle",
    )
    body += txt(ox - 16, oy - h, "1", size=9, fill=SOFT, family=F_MONO, anchor="end")
    body += txt(ox - 16, oy, "0", size=9, fill=SOFT, family=F_MONO, anchor="end")

    curves = [
        (80, PINE2, "state change"),
        (140, TEAL, "pane reveal"),
        (180, OXIDE, "window"),
    ]
    for duration, colour, _label in curves:
        x_end = ox + (duration / 220) * w
        d = f"M {ox} {oy} C {ox + (x_end - ox) * 0.2} {oy - h * 0.55}, {ox + (x_end - ox) * 0.55} {oy - h * 0.92}, {x_end} {oy - h}"
        body += path(d, stroke=colour, sw=2.5)
        body += circle(x_end, oy - h, 5, fill=colour, stroke=None)
        body += txt(
            x_end + 10,
            oy - h + 4,
            f"{duration} ms",
            size=10,
            fill=colour,
            family=F_MONO,
        )
    body += txt(ox + 40, oy - h - 24, "progress", size=10, fill=SOFT, family=F_MONO)

    body += rect(940, 166, 196, 250, fill=HIGH, stroke=INK)
    body += txt(
        956, 194, "RULES", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1
    )
    body += lines(
        956,
        224,
        [
            "Ease out, never bounce.",
            "No parallax.",
            "No animation for its own sake.",
            "Reduced motion: 0.01 ms.",
        ],
        size=11,
        fill=SOFT,
        leading=34,
    )
    body += txt(
        64,
        690,
        "If a change cannot be explained in one sentence, it does not need a transition.",
        size=13,
        fill=SOFT,
        family=F_DISPLAY,
        style="italic",
    )
    return svg_doc(
        1200,
        720,
        "Motion timing chart",
        "Ease-out curves for 80, 140 and 180 millisecond transitions, with rules for restrained motion.",
        body=body,
    )
