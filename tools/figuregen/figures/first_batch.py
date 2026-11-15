"""Figure generator module: figures.first_batch."""

from __future__ import annotations

from figuregen.canvas import line, rect, svg_doc, txt
from figuregen.ornaments import title_block
from figuregen.palette import (
    F_DISPLAY,
    F_MONO,
    HIGH,
    INK,
    LINE,
    PAPER,
    PINE,
    PINE2,
    SOFT,
    TEAL_INK,
)


def fig_first_batch() -> str:
    """Draw the first batch as now, next and later bands."""
    body = title_block(
        64,
        70,
        "The first batch",
        "Ship the contracts, then the workspace, then the studio. A tool may be deferred; the interface rules are not.",
    )
    bands = [
        (
            "NOW",
            "Contracts",
            PINE,
            ["hello-window", "escutcheon-check", "Lapidary scene", "Burin output"],
            "done",
        ),
        (
            "NEXT",
            "Workspace",
            PINE2,
            [
                "Facet Notes",
                "dataframe",
                "diagram",
                "bitmap",
                "formula",
                "inspector",
                "project window",
            ],
            "active",
        ),
        (
            "LATER",
            "Studio",
            TEAL_INK,
            ["Burin Draw", "Cabochon Press", "Enfilade Table"],
            "later",
        ),
    ]
    for index, (when, name, colour, tools, mark) in enumerate(bands):
        y = 170 + index * 178
        body += txt(
            64,
            y + 18,
            when,
            size=10,
            fill=colour,
            family=F_MONO,
            weight="bold",
            spacing=1.2,
        )
        body += txt(64, y + 48, name, size=24, family=F_DISPLAY, style="italic")
        body += line(64, y + 64, 1136, y + 64, stroke=LINE)
        for tool_index, tool in enumerate(tools):
            x = 300 + (tool_index % 4) * 208
            yy = y + 4 + (tool_index // 4) * 46
            body += rect(
                x,
                yy,
                192,
                34,
                fill=HIGH if mark != "later" else PAPER,
                stroke=colour if mark == "active" else LINE,
            )
            body += txt(
                x + 10,
                yy + 22,
                tool,
                size=10,
                family=F_MONO,
                fill=INK if mark != "later" else SOFT,
            )
        if mark == "done":
            body += txt(
                1136,
                y + 22,
                "shipped",
                size=10,
                fill=PINE2,
                family=F_MONO,
                anchor="end",
            )
        elif mark == "active":
            body += txt(
                1136,
                y + 22,
                "in progress",
                size=10,
                fill=PINE2,
                family=F_MONO,
                anchor="end",
            )
        else:
            body += txt(
                1136,
                y + 22,
                "held to the same rules",
                size=10,
                fill=SOFT,
                family=F_MONO,
                anchor="end",
            )
    body += txt(
        64,
        716,
        "A deferred tool is not a different design language.",
        size=13,
        fill=SOFT,
        family=F_DISPLAY,
        style="italic",
    )
    return svg_doc(
        1200,
        760,
        "The first batch in three bands",
        "Three bands labelled now, next and later, listing contracts, workspace tools and studio instruments.",
        body=body,
    )
