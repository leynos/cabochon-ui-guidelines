"""Draw the two-plane ecosystem map figure.

The map places an application above the GEM substrate and a semantic lower
plane, with Mullion deferred. The exported `fig_map` function returns the SVG
string, drawn from the shared `figuregen.palette` colours. `figuregen.cli`
calls it to write `fig-01-map.svg` under `figures/`.
"""

from __future__ import annotations

from figuregen.canvas import line, para, path, rect, svg_doc, txt
from figuregen.ornaments import title_block
from figuregen.palette import F_DISPLAY, F_MONO, HIGH, INK, LINE, OXIDE, PAPER, SOFT


def fig_map() -> str:
    """Draw the two-plane Cabochon ecosystem map.

    Returns
    -------
    str
    """
    body = title_block(
        64,
        70,
        "Two planes, one substrate",
        "An application draws through the upper plane and reaches objects through the lower. It never reaches around either.",
    )
    # Application.
    body += rect(64, 158, 740, 96, fill=HIGH, stroke=INK)
    body += txt(
        84,
        184,
        "APPLICATION",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    body += txt(84, 212, "Facet Notes", size=18, family=F_DISPLAY, style="italic")
    body += txt(
        84, 236, "Uses the substrate; never reaches around it.", size=11, fill=SOFT
    )
    # Upper plane.
    body += rect(64, 276, 740, 190, fill=HIGH, stroke=INK)
    body += txt(
        84,
        300,
        "UPPER PLANE · GEM SUBSTRATE",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    upper = [
        ("Clerestory", "windows · menus · commands · focus"),
        ("Escutcheon", "menus · strings · icons · shortcuts"),
        ("Lapidary", "rectangles · paths · text · images"),
        ("Burin", "display · PDF · raster · print · a11y"),
    ]
    for index, (name, role) in enumerate(upper):
        bx = 86 + (index % 2) * 352
        by = 316 + (index // 2) * 72
        body += rect(bx, by, 332, 62, fill=PAPER, stroke=LINE)
        body += txt(bx + 12, by + 24, name, size=13, weight="bold")
        body += txt(bx + 12, by + 44, role, size=10, fill=SOFT, family=F_MONO)
    # Boundary.
    body += line(434, 466, 434, 506, stroke=OXIDE, sw=2)
    body += path("M 428 500 L 434 506 L 440 500", stroke=OXIDE, sw=2)
    body += txt(
        448,
        494,
        "selectors · capabilities · transactions",
        size=10,
        fill=OXIDE,
        family=F_MONO,
    )
    # Lower plane.
    body += rect(64, 506, 740, 170, fill=HIGH, stroke=INK)
    body += txt(
        84,
        530,
        "LOWER PLANE · SEMANTIC",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    body += rect(86, 544, 696, 62, fill=PAPER, stroke=LINE)
    body += txt(98, 568, "Enfilade", size=13, weight="bold")
    body += txt(
        98,
        588,
        "object identity · selectors · capabilities · transactions · live relationships",
        size=10,
        fill=SOFT,
        family=F_MONO,
    )
    body += txt(
        98,
        632,
        "runtime services: portals · storage · identity providers",
        size=10,
        fill=SOFT,
        family=F_MONO,
    )
    # Deferred shell.
    body += rect(830, 158, 306, 150, fill=PAPER, stroke=INK)
    body += txt(
        850,
        184,
        "DEFERRED SHELL",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    body += rect(850, 200, 266, 88, fill=HIGH, stroke=INK, dash="5 5")
    body += txt(864, 226, "Mullion", size=14, family=F_DISPLAY, style="italic")
    body += para(
        864,
        246,
        238,
        "A future compositor and shell. It must not add a second object system or rendering path.",
        size=10,
        leading=15,
    )
    # Consequences.
    body += rect(830, 326, 306, 350, fill=HIGH, stroke=INK)
    body += txt(
        850,
        352,
        "WHAT THE MAP IMPLIES",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    consequences = [
        (
            "Chrome is shared; content is specific.",
            "Windows, menus, state chips and inspectors are environment furniture.",
        ),
        (
            "Identity outlives presentation.",
            "One object, many presentations, one identity.",
        ),
        (
            "Failure is a first-class surface.",
            "Stale, broken and denied are interface states, not log lines.",
        ),
    ]
    for index, (headline, detail) in enumerate(consequences):
        cy = 388 + index * 92
        body += txt(
            850,
            cy,
            f"{index + 1:02d}",
            size=10,
            fill=OXIDE,
            family=F_MONO,
            weight="bold",
        )
        body += txt(880, cy, headline, size=12, weight="bold")
        body += para(880, cy + 18, 234, detail, size=10, leading=15)
    body += txt(
        64,
        716,
        "The substrate is production, even when the shell is deferred.",
        size=13,
        fill=SOFT,
        family=F_DISPLAY,
        style="italic",
    )
    return svg_doc(
        1200,
        760,
        "The two-plane Cabochon ecosystem map",
        "An application above the GEM substrate of Clerestory, Escutcheon, Lapidary and Burin, and a semantic lower plane led by Enfilade, with Mullion deferred.",
        body=body,
    )
