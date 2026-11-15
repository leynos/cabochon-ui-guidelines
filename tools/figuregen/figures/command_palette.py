"""Draw the command palette over a document figure.

The figure overlays a search field, grouped results and keyboard hints on a
dimmed document. The exported `fig_command_palette` function returns the SVG
string, drawn from the shared `figuregen.palette` colours. `figuregen.cli`
calls it to write `fig-21-command-palette.svg` under `figures/`.
"""

from __future__ import annotations

from figuregen.canvas import line, rect, svg_doc, txt
from figuregen.ornaments import title_block
from figuregen.palette import F_MONO, HIGH, INK, LINE, OXIDE, PAPER, PINE2, SOFT, WHITE
from figuregen.widgets import field


def fig_command_palette() -> str:
    """Draw the command palette over a document.

    Returns
    -------
    str
    """
    body = title_block(
        64,
        70,
        "The command palette is a second door",
        "It finds commands, objects and tools by name. It does not replace the menu bar or the document.",
    )
    body += rect(64, 150, 1072, 540, fill=PAPER, stroke=LINE)
    body += rect(64, 150, 1072, 540, fill=INK, stroke=None, opacity=0.14)
    x, y, w, h = 300, 180, 600, 420
    body += rect(x + 8, y + 8, w, h, fill="#17201C30", stroke=None)
    body += rect(x, y, w, h, fill=HIGH, stroke=INK)
    body += field(x + 18, y + 18, w - 36, "curr", height=40, focus=True)
    body += txt(
        x + w - 28, y + 43, "Esc", size=10, fill=SOFT, family=F_MONO, anchor="end"
    )
    # Groups.
    groups = [
        (
            "OBJECTS",
            [
                ("Currency — GBP · obj:4c21", "note:transition"),
                ("Currency table — 12 rows", "obj:8f3a"),
            ],
        ),
        (
            "COMMANDS",
            [
                ("Insert currency object", "Ctrl+Shift+C"),
                ("Refresh live values", "F5"),
                ("Open inspector", "Ctrl+I"),
            ],
        ),
    ]
    row_y = y + 78
    selected_row = 3
    row_index = 0
    for group, rows in groups:
        body += txt(
            x + 22,
            row_y,
            group,
            size=10,
            fill=OXIDE,
            family=F_MONO,
            weight="bold",
            spacing=0.8,
        )
        row_y += 20
        for label, detail in rows:
            if row_index == selected_row:
                body += rect(x + 12, row_y - 16, w - 24, 34, fill=PINE2, stroke=None)
                colour = WHITE
            else:
                colour = INK
            body += txt(x + 24, row_y + 6, label, size=12, fill=colour)
            body += txt(
                x + w - 24,
                row_y + 6,
                detail,
                size=10,
                fill=WHITE if row_index == selected_row else SOFT,
                family=F_MONO,
                anchor="end",
            )
            row_y += 38
            row_index += 1
        row_y += 6
    body += line(x, y + h - 36, x + w, y + h - 36, stroke=LINE)
    body += txt(
        x + 20,
        y + h - 14,
        "Enter run   ·   Tab next group   ·   Esc close",
        size=10,
        fill=SOFT,
        family=F_MONO,
    )
    # Notes.
    nx = 64
    body += txt(
        nx,
        726,
        "Results are grouped by kind. Objects carry identity; commands carry shortcuts; tools appear only when the current selection makes them applicable.",
        size=11,
        fill=SOFT,
    )
    return svg_doc(
        1200,
        760,
        "Command palette over a document",
        "A command palette with a search field, grouped object and command results, a selected row and keyboard hints.",
        body=body,
    )
