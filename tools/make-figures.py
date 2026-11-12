#!/usr/bin/env python3
"""Generate the SVG figures for the Cabochon interface guidelines.

The figures share one palette and one geometry vocabulary. Run from the
repository root with ``python3 -I tools/make-figures.py``; the generated SVGs
are written to ``figures/``.
"""

from __future__ import annotations

import json
from html import escape
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "figures"
DATA = json.loads((ROOT / "tools" / "figure-data.json").read_text(encoding="utf-8"))

LIVE_STATES: dict[str, dict[str, str]] = DATA["live_states"]
LIVE_TRANSITIONS: list[dict[str, object]] = DATA["live_transitions"]
RESOLUTION_STATES: dict[str, dict[str, str]] = DATA["resolution_states"]
FIGURE_SPECS: dict[str, dict[str, object]] = DATA["figures"]

# Material palette, with accessible text variants.
PAPER = "#F1EEE5"
HIGH = "#FAF8F2"
INK = "#17201C"
SOFT = "#59625D"
PINE = "#173F35"
PINE2 = "#285E50"
TEAL = "#678E86"
TEAL_INK = "#456A62"
OXIDE = "#8A302F"
AMBER = "#B8792E"
AMBER_INK = "#8A5B24"
LINE = "#AAA99F"
DARK = "#121816"
DARK_SURFACE = "#1B2420"
DARK_TEXT = "#EDE9DE"
DARK_MUTED = "#A9B1AB"
DARK_PINE = "#7FB3A3"
DARK_OXIDE = "#D98C86"
DARK_AMBER = "#E0B36A"
WHITE = "#FFFFFF"

F_DISPLAY = "Georgia, 'DejaVu Serif', 'Times New Roman', serif"
F_UI = "'DejaVu Sans', 'Liberation Sans', Arial, sans-serif"
F_MONO = "'DejaVu Sans Mono', 'Liberation Mono', monospace"


def attrs(**values: object) -> str:
    """Render SVG attributes, converting snake_case names to kebab-case."""
    rendered: list[str] = []
    for key, value in values.items():
        if value is None:
            continue
        name = key.rstrip("_").replace("_", "-")
        rendered.append(f'{name}="{escape(str(value), quote=True)}"')
    return " ".join(rendered)


def rect(
    x: float,
    y: float,
    w: float,
    h: float,
    fill: str = "none",
    stroke: str | None = INK,
    sw: float = 1,
    rx: float = 0,
    dash: str | None = None,
    opacity: float | None = None,
) -> str:
    return (
        f"<rect {attrs(x=x, y=y, width=w, height=h, fill=fill, stroke=stroke, stroke_width=sw, rx=rx, stroke_dasharray=dash, opacity=opacity)}/>"
    )


def line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    stroke: str = INK,
    sw: float = 1,
    dash: str | None = None,
    opacity: float | None = None,
) -> str:
    return (
        f"<line {attrs(x1=x1, y1=y1, x2=x2, y2=y2, stroke=stroke, stroke_width=sw, stroke_dasharray=dash, opacity=opacity)}/>"
    )


def path(d: str, fill: str = "none", stroke: str | None = INK, sw: float = 1, dash: str | None = None, opacity: float | None = None) -> str:
    return f"<path {attrs(d=d, fill=fill, stroke=stroke, stroke_width=sw, stroke_dasharray=dash, opacity=opacity)}/>"


def circle(cx: float, cy: float, r: float, fill: str = "none", stroke: str | None = INK, sw: float = 1) -> str:
    return f"<circle {attrs(cx=cx, cy=cy, r=r, fill=fill, stroke=stroke, stroke_width=sw)}/>"


def ellipse(cx: float, cy: float, rx: float, ry: float, fill: str = "none", stroke: str | None = INK, sw: float = 1) -> str:
    return f"<ellipse {attrs(cx=cx, cy=cy, rx=rx, ry=ry, fill=fill, stroke=stroke, stroke_width=sw)}/>"


def txt(
    x: float,
    y: float,
    value: str,
    size: float = 14,
    fill: str = INK,
    family: str = F_UI,
    weight: str = "normal",
    anchor: str = "start",
    style: str = "normal",
    spacing: float | None = None,
    opacity: float | None = None,
    data_state: str | None = None,
) -> str:
    return (
        f"<text {attrs(x=x, y=y, fill=fill, font_family=family, font_size=size, font_weight=weight, text_anchor=anchor, font_style=style, letter_spacing=spacing, opacity=opacity, data_state=data_state)}>{escape(value)}</text>"
    )


def lines(
    x: float,
    y: float,
    values: list[str],
    size: float = 14,
    leading: float = 20,
    **kwargs: object,
) -> str:
    return "".join(txt(x, y + index * leading, value, size=size, **kwargs) for index, value in enumerate(values))


def svg_doc(width: int, height: int, title: str, desc: str, body: str, bg: str = PAPER) -> str:
    return dedent(
        f"""\
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-labelledby="title desc">
          <title id="title">{escape(title)}</title>
          <desc id="desc">{escape(desc)}</desc>
          <rect width="{width}" height="{height}" fill="{bg}"/>
        {body}
        </svg>
        """
    )


def kicker(x: float, y: float, value: str, colour: str = OXIDE) -> str:
    return txt(x, y, value.upper(), size=10, fill=colour, family=F_MONO, weight="bold", spacing=1.1)


def state_mark(cx: float, cy: float, kind: str, colour: str) -> str:
    """Draw the non-colour mark that distinguishes a state chip.

    Colour is never the only carrier of meaning, so every state declares a
    distinct shape. An unknown mark is a generation failure.
    """
    if kind == "dot":
        return circle(cx, cy, 3, fill=colour, stroke=None)
    if kind == "arc":
        return path(
            f"M {cx + 2.6:.2f} {cy - 1.4:.2f} A 2.9 2.9 0 1 0 {cx + 2.7:.2f} {cy + 1.2:.2f}",
            stroke=colour,
            sw=1.5,
        ) + path(
            f"M {cx + 3.4:.2f} {cy - 2.6:.2f} L {cx + 2.6:.2f} {cy - 1.4:.2f} L {cx + 1.4:.2f} {cy - 1.8:.2f}",
            stroke=colour,
            sw=1.3,
        )
    if kind == "triangle":
        return path(
            f"M {cx:.2f} {cy - 3.4:.2f} L {cx + 3.4:.2f} {cy + 2.8:.2f} L {cx - 3.4:.2f} {cy + 2.8:.2f} Z",
            fill=colour,
            stroke=None,
        )
    if kind == "broken":
        return (
            line(cx - 3.4, cy, cx - 1.3, cy, stroke=colour, sw=1.8)
            + line(cx + 1.3, cy, cx + 3.4, cy, stroke=colour, sw=1.8)
            + line(cx - 2.8, cy - 2.4, cx - 1.8, cy - 1.2, stroke=colour, sw=1)
            + line(cx + 2.8, cy + 2.4, cx + 1.8, cy + 1.2, stroke=colour, sw=1)
        )
    if kind == "lock":
        return (
            path(
                f"M {cx - 1.8:.2f} {cy - 0.6:.2f} L {cx - 1.8:.2f} {cy - 1.8:.2f} "
                f"A 1.8 1.8 0 0 1 {cx + 1.8:.2f} {cy - 1.8:.2f} L {cx + 1.8:.2f} {cy - 0.6:.2f}",
                stroke=colour,
                sw=1.2,
            )
            + rect(cx - 2.8, cy - 0.6, 5.6, 4.2, fill=colour, stroke=None, rx=0.6)
        )
    if kind == "hatch":
        return (
            rect(cx - 3, cy - 3, 6, 6, stroke=colour, sw=1)
            + line(cx - 2.2, cy + 2.2, cx + 2.2, cy - 2.2, stroke=colour, sw=0.9)
            + line(cx - 0.4, cy + 2.6, cx + 2.6, cy - 0.4, stroke=colour, sw=0.9)
            + line(cx - 2.6, cy + 0.4, cx + 0.4, cy - 2.6, stroke=colour, sw=0.9)
        )
    if kind == "dashed":
        return rect(cx - 3, cy - 3, 6, 6, stroke=colour, sw=1.2, dash="1.6 1.4")
    if kind == "crossed":
        return (
            rect(cx - 3, cy - 3, 6, 6, stroke=colour, sw=1)
            + line(cx - 2, cy - 2, cx + 2, cy + 2, stroke=colour, sw=1.2)
            + line(cx - 2, cy + 2, cx + 2, cy - 2, stroke=colour, sw=1.2)
        )
    raise ValueError(f"unknown state mark {kind!r}")


def chip(
    x: float,
    y: float,
    label: str,
    colour: str = PINE2,
    fill: str = HIGH,
    size: float = 11,
    state: str | None = None,
    mark: str = "dot",
) -> tuple[str, float]:
    width = max(58.0, len(label) * size * 0.62 + 18)
    body = f'<g data-mark="{mark}">'
    body += rect(x, y, width, 20, fill=fill, stroke=colour, sw=1)
    body += state_mark(x + 10, y + 10, mark, colour)
    body += txt(
        x + 18,
        y + 14,
        label,
        size=size,
        fill=colour,
        family=F_MONO,
        weight="bold",
        data_state=state,
    )
    body += "</g>"
    return body, width


def state_chip(x: float, y: float, name: str) -> tuple[str, float]:
    """Draw a live or resolution state chip.

    Every supported state has one declared word, cue and colour role. An
    unknown state is a generation failure, not a silent fallback to a plausible
    colour.
    """
    state = LIVE_STATES.get(name) or RESOLUTION_STATES.get(name)
    if state is None:
        known = sorted({*LIVE_STATES, *RESOLUTION_STATES})
        raise ValueError(f"unknown figure state {name!r}; known states are {known}")
    mark = state.get("mark")
    if not mark:
        raise ValueError(f"figure state {name!r} declares no non-colour mark")
    return chip(
        x,
        y,
        state["word"].upper(),
        colour=str(state["colour"]),
        state=name,
        mark=str(mark),
    )


def title_block(x: float, y: float, heading: str, deck: str | None = None, width: int = 520) -> str:
    body = kicker(x, y, "Cabochon interface guidelines")
    body += txt(x, y + 48, heading, size=34, family=F_DISPLAY, style="italic")
    if deck:
        body += lines(x, y + 80, [deck], size=13, fill=SOFT, leading=19)
    return body


def frame(x: float, y: float, w: float, h: float, label: str | None = None, fill: str = HIGH, stroke: str = INK) -> str:
    body = rect(x, y, w, h, fill=fill, stroke=stroke)
    if label:
        body += txt(x + 12, y + 20, label.upper(), size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.8)
    return body


def mini_note(x: float, y: float, w: float, h: float, dark: bool = False) -> str:
    ink = INK if not dark else DARK_TEXT
    soft = SOFT if not dark else DARK_MUTED
    fill = HIGH if not dark else DARK_SURFACE
    body = rect(x, y, w, h, fill=fill, stroke=LINE)
    body += txt(x + 18, y + 30, "North Sea transition", size=18, family=F_DISPLAY, style="italic", fill=ink)
    body += line(x + 18, y + 44, x + w - 18, y + 44, stroke=LINE)
    for index, width in enumerate([0.82, 0.9, 0.72, 0.86, 0.64]):
        body += rect(x + 18, y + 60 + index * 16, (w - 36) * width, 5, fill=soft, stroke=None)
    return body


def mini_table(x: float, y: float, w: float, h: float) -> str:
    body = rect(x, y, w, h, fill=WHITE, stroke=LINE)
    body += rect(x, y, w, 24, fill=PINE2, stroke=None)
    body += txt(x + 10, y + 16, "GBP · DAILY RATES", size=9, fill=WHITE, family=F_MONO, weight="bold")
    body += txt(x + 10, y + 40, "DATE", size=8, fill=SOFT, family=F_MONO, weight="bold")
    body += txt(x + w - 74, y + 40, "RATE", size=8, fill=SOFT, family=F_MONO, weight="bold", anchor="end")
    body += txt(x + w - 10, y + 40, "SOURCE", size=8, fill=SOFT, family=F_MONO, weight="bold", anchor="end")
    rows = [("13 Apr 2026", "1.2840", "ECB"), ("12 Apr 2026", "1.2790", "ECB"), ("11 Apr 2026", "1.2860", "ECB")]
    for index, (date, rate, source) in enumerate(rows):
        ry = y + 58 + index * 20
        if index == 0:
            body += rect(x + 6, ry - 12, w - 12, 17, fill=PINE2, stroke=None)
        fill = WHITE if index == 0 else INK
        body += txt(x + 10, ry, date, size=9, fill=fill, family=F_MONO)
        body += txt(x + w - 74, ry, rate, size=9, fill=fill, family=F_MONO, anchor="end")
        body += txt(x + w - 10, ry, source, size=9, fill=WHITE if index == 0 else SOFT, family=F_MONO, anchor="end")
    return body


def mini_page(x: float, y: float, w: float, h: float) -> str:
    body = rect(x, y, w, h, fill=WHITE, stroke=LINE)
    body += txt(x + 16, y + 26, "NORTH SEA CURRENCY", size=8, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    body += txt(x + 16, y + 52, "GBP 1,284", size=22, fill=INK, family=F_MONO, weight="bold")
    body += line(x + 16, y + 64, x + w - 16, y + 64, stroke=LINE)
    body += para(x + 16, y + 82, w - 32, "Printed from the same object, with its source and revision attached.", size=8, leading=11, fill=SOFT)
    body += txt(x + 16, y + h - 8, "1 / 1 · proof · obj:c128", size=8, fill=SOFT, family=F_MONO)
    return body


def mini_canvas(x: float, y: float, w: float, h: float) -> str:
    body = rect(x, y, w, h, fill=WHITE, stroke=LINE)
    for gx in range(1, 6):
        body += line(x + gx * w / 6, y, x + gx * w / 6, y + h, stroke="#D9DED9", sw=0.6)
    for gy in range(1, 4):
        body += line(x, y + gy * h / 4, x + w, y + gy * h / 4, stroke="#D9DED9", sw=0.6)
    body += path(
        f"M {x + 30} {y + h * 0.62} C {x + w * 0.28} {y + h * 0.15}, {x + w * 0.48} {y + h * 0.18}, {x + w * 0.56} {y + h * 0.58} S {x + w * 0.82} {y + h * 0.82}, {x + w - 30} {y + h * 0.42}",
        stroke=OXIDE,
        sw=3,
    )
    for ax, ay in [(0.2, 0.62), (0.42, 0.28), (0.56, 0.58), (0.78, 0.72)]:
        body += rect(x + w * ax - 4, y + h * ay - 4, 8, 8, fill=WHITE, stroke=OXIDE, sw=1.5)
    return body


# ---------------------------------------------------------------------------
# Front matter figures


def fig_cover() -> str:
    body = ""
    body += txt(72, 86, "CABOCHON", size=11, fill=OXIDE, family=F_MONO, weight="bold", spacing=2.4)
    body += txt(72, 214, "Interface", size=78, family=F_DISPLAY, style="italic")
    body += txt(72, 288, "guidelines", size=78, family=F_DISPLAY, style="italic")
    body += line(72, 330, 540, 330, stroke=INK)
    body += lines(
        72,
        374,
        [
            "A compact, document-centred",
            "environment for the first",
            "small world of Cabochon tools.",
        ],
        size=20,
        fill=SOFT,
        leading=28,
    )
    body += txt(72, 530, "Edition 0.1", size=12, family=F_MONO, weight="bold", spacing=1.2)
    body += txt(72, 552, "2026", size=12, family=F_MONO, spacing=1.2)
    body += txt(72, 732, "Written for the en-GB Oxford house style.", size=11, fill=SOFT, family=F_MONO)

    # The material plate: a polished cabochon with four instrument labels.
    body += "<defs>"
    body += '<linearGradient id="stone" x1="0" y1="0" x2="1" y2="1">'
    body += f'<stop offset="0" stop-color="{PINE2}"/><stop offset="0.62" stop-color="{PINE}"/><stop offset="1" stop-color="#0D2A23"/>'
    body += "</linearGradient>"
    body += '<radialGradient id="glow" cx="0.32" cy="0.24" r="0.62">'
    body += '<stop offset="0" stop-color="#FFFFFF" stop-opacity="0.34"/><stop offset="0.55" stop-color="#FFFFFF" stop-opacity="0.04"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>'
    body += "</radialGradient>"
    body += "</defs>"
    body += ellipse(892, 382, 246, 178, fill="url(#stone)", stroke=PINE, sw=2)
    body += ellipse(892, 382, 232, 166, fill="url(#glow)", stroke=None)
    body += ellipse(892, 382, 246, 178, fill="none", stroke=AMBER, sw=1.5)
    body += path("M 724 430 C 788 300, 990 260, 1068 386", stroke="#FFFFFF", sw=10, dash=None)
    body += path("M 724 430 C 788 300, 990 260, 1068 386", stroke="#FFFFFF", sw=2, opacity=0.55)
    body += path("M 766 470 C 842 408, 960 396, 1020 448", stroke=TEAL, sw=2)

    for label, lx, ly, anchor in [
        ("FACET NOTES", 602, 198, "end"),
        ("ENFILADE TABLE", 1128, 198, "end"),
        ("BURIN DRAW", 602, 590, "end"),
        ("CABOCHON PRESS", 1128, 590, "end"),
    ]:
        body += txt(lx, ly, label, size=10, fill=PINE2, family=F_MONO, weight="bold", anchor=anchor, spacing=0.8)
        body += circle(lx + (8 if anchor == "start" else -8), ly + 18, 3, fill=AMBER, stroke=None)

    body += txt(1128, 736, "Plate 00 / Material", size=10, fill=SOFT, family=F_MONO, anchor="end", spacing=0.8)
    return svg_doc(1200, 800, "Cover plate: a polished cabochon surrounded by four instruments", "A green cabochon stone on a warm paper ground, with Facet Notes, Enfilade Table, Burin Draw and Cabochon Press named around it.", body)


def fig_map() -> str:
    body = title_block(64, 70, "Two planes, one substrate", "An application draws through the upper plane and reaches objects through the lower. It never reaches around either.")
    # Application.
    body += rect(64, 158, 740, 96, fill=HIGH, stroke=INK)
    body += txt(84, 184, "APPLICATION", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    body += txt(84, 212, "Facet Notes", size=18, family=F_DISPLAY, style="italic")
    body += txt(84, 236, "Uses the substrate; never reaches around it.", size=11, fill=SOFT)
    # Upper plane.
    body += rect(64, 276, 740, 190, fill=HIGH, stroke=INK)
    body += txt(84, 300, "UPPER PLANE · GEM SUBSTRATE", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
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
    body += txt(448, 494, "selectors · capabilities · transactions", size=10, fill=OXIDE, family=F_MONO)
    # Lower plane.
    body += rect(64, 506, 740, 170, fill=HIGH, stroke=INK)
    body += txt(84, 530, "LOWER PLANE · SEMANTIC", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    body += rect(86, 544, 696, 62, fill=PAPER, stroke=LINE)
    body += txt(98, 568, "Enfilade", size=13, weight="bold")
    body += txt(98, 588, "object identity · selectors · capabilities · transactions · live relationships", size=10, fill=SOFT, family=F_MONO)
    body += txt(98, 632, "runtime services: portals · storage · identity providers", size=10, fill=SOFT, family=F_MONO)
    # Deferred shell.
    body += rect(830, 158, 306, 150, fill=PAPER, stroke=INK)
    body += txt(850, 184, "DEFERRED SHELL", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    body += rect(850, 200, 266, 88, fill=HIGH, stroke=INK, dash="5 5")
    body += txt(864, 226, "Mullion", size=14, family=F_DISPLAY, style="italic")
    body += para(864, 246, 238, "A future compositor and shell. It must not add a second object system or rendering path.", size=10, leading=15)
    # Consequences.
    body += rect(830, 326, 306, 350, fill=HIGH, stroke=INK)
    body += txt(850, 352, "WHAT THE MAP IMPLIES", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    consequences = [
        ("Chrome is shared; content is specific.", "Windows, menus, state chips and inspectors are environment furniture."),
        ("Identity outlives presentation.", "One object, many presentations, one identity."),
        ("Failure is a first-class surface.", "Stale, broken and denied are interface states, not log lines."),
    ]
    for index, (headline, detail) in enumerate(consequences):
        cy = 388 + index * 92
        body += txt(850, cy, f"{index + 1:02d}", size=10, fill=OXIDE, family=F_MONO, weight="bold")
        body += txt(880, cy, headline, size=12, weight="bold")
        body += para(880, cy + 18, 234, detail, size=10, leading=15)
    body += txt(64, 716, "The substrate is production, even when the shell is deferred.", size=13, fill=SOFT, family=F_DISPLAY, style="italic")
    return svg_doc(1200, 760, "The two-plane Cabochon ecosystem map", "An application above the GEM substrate of Clerestory, Escutcheon, Lapidary and Burin, and a semantic lower plane led by Enfilade, with Mullion deferred.", body)


def fig_small_world() -> str:
    body = title_block(64, 70, "The Cabochon character", "Four structural choices, not a decoration kit. Each one can be recognised in a window without reading its label.")
    cards = [
        ("01", "Compact", "rather than cramped", "Short rows and generous padding. Density never removes the space a hand or an eye needs.", "compact"),
        ("02", "Document-centred", "rather than application-centred", "The document holds the largest plane; the instrument sits at its edges.", "document"),
        ("03", "Liberal", "rather than paternal", "The user owns the work. Export stays available, formats stay open and no account gates local content.", "liberal"),
        ("04", "Practical", "rather than ornamental", "A rule separates planes, a tint marks a state, a shadow lifts a sheet. Nothing decorates.", "practical"),
    ]
    for index, (number, title, aside, claim, kind) in enumerate(cards):
        x = 64 + (index % 2) * 548
        y = 166 + (index // 2) * 252
        w, h = 524, 236
        body += rect(x, y, w, h, fill=HIGH, stroke=INK)
        body += txt(x + 20, y + 28, number, size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
        body += txt(x + 20, y + 62, title, size=22, family=F_DISPLAY, style="italic")
        body += txt(x + 20, y + 82, aside, size=12, fill=SOFT)
        body += line(x + 20, y + 96, x + w - 20, y + 96, stroke=LINE)
        body += para(x + 20, y + 118, w - 40, claim, size=11, leading=16)
        if kind == "compact":
            bands = [("title bar", "31", PINE, WHITE), ("menu bar", "29", PINE2, WHITE), ("tree row", "28", TEAL, INK)]
            for band_index, (name, measure, fill, colour) in enumerate(bands):
                by = y + 148 + band_index * 24
                body += rect(x + 20, by, 220, 18, fill=fill, stroke=None)
                body += txt(x + 30, by + 13, name, size=9, fill=colour, family=F_MONO)
                body += txt(x + 252, by + 13, f"{measure} px", size=10, fill=SOFT, family=F_MONO)
        elif kind == "document":
            body += rect(x + 20, y + 142, 280, 60, fill=HIGH, stroke=INK)
            body += rect(x + 20, y + 142, 42, 60, fill=PAPER, stroke=LINE)
            body += rect(x + 68, y + 148, 180, 48, fill=WHITE, stroke=LINE)
            body += rect(x + 254, y + 142, 46, 60, fill=PAPER, stroke=LINE)
            body += txt(x + 20, y + 220, "rail 126 · document ≥ 420 · inspector 240", size=10, fill=SOFT, family=F_MONO)
        elif kind == "liberal":
            cx = x + 20
            for label, chip_w in [("Export", 84), ("Open format", 120), ("No account", 116)]:
                body += rect(cx, y + 150, chip_w, 26, fill=PAPER, stroke=INK)
                body += txt(cx + 12, y + 168, label, size=11, fill=INK)
                cx += chip_w + 12
            body += txt(x + 20, y + 206, "The user owns the work.", size=11, fill=SOFT)
        else:
            specimens = [("flat fill", HIGH, True, 0), ("1 px keyline", PAPER, True, 0), ("2 px radius", HIGH, True, 2), ("offset shadow", HIGH, False, 0)]
            for spec_index, (label, fill, stroked, radius) in enumerate(specimens):
                sx = x + 20 + spec_index * 120
                if not stroked:
                    body += rect(sx + 4, y + 150, 40, 40, fill="#17201C18", stroke=None)
                body += rect(sx, y + 146, 40, 40, fill=fill, stroke=INK if stroked else None, rx=radius)
                body += txt(sx, y + 204, label, size=10, fill=SOFT, family=F_MONO)
    body += txt(64, 700, "A surface that fails any one of these choices is not Cabochon, however closely it copies the palette.", size=13, fill=SOFT, family=F_DISPLAY, style="italic")
    return svg_doc(1200, 760, "Four structural choices of the Cabochon character", "Cards for compact, document-centred, liberal and practical character, each with a small specimen.", body)


def fig_first_batch() -> str:
    body = title_block(64, 70, "The first batch", "Ship the contracts, then the workspace, then the studio. A tool may be deferred; the interface rules are not.")
    bands = [
        ("NOW", "Contracts", PINE, ["hello-window", "escutcheon-check", "Lapidary scene", "Burin output"], "done"),
        ("NEXT", "Workspace", PINE2, ["Facet Notes", "dataframe", "diagram", "bitmap", "formula", "inspector", "project window"], "active"),
        ("LATER", "Studio", TEAL_INK, ["Burin Draw", "Cabochon Press", "Enfilade Table"], "later"),
    ]
    for index, (when, name, colour, tools, mark) in enumerate(bands):
        y = 170 + index * 178
        body += txt(64, y + 18, when, size=10, fill=colour, family=F_MONO, weight="bold", spacing=1.2)
        body += txt(64, y + 48, name, size=24, family=F_DISPLAY, style="italic")
        body += line(64, y + 64, 1136, y + 64, stroke=LINE)
        for tool_index, tool in enumerate(tools):
            x = 300 + (tool_index % 4) * 208
            yy = y + 4 + (tool_index // 4) * 46
            body += rect(x, yy, 192, 34, fill=HIGH if mark != "later" else PAPER, stroke=colour if mark == "active" else LINE)
            body += txt(x + 10, yy + 22, tool, size=10, family=F_MONO, fill=INK if mark != "later" else SOFT)
        if mark == "done":
            body += txt(1136, y + 22, "shipped", size=10, fill=PINE2, family=F_MONO, anchor="end")
        elif mark == "active":
            body += txt(1136, y + 22, "in progress", size=10, fill=PINE2, family=F_MONO, anchor="end")
        else:
            body += txt(1136, y + 22, "held to the same rules", size=10, fill=SOFT, family=F_MONO, anchor="end")
    body += txt(64, 716, "A deferred tool is not a different design language.", size=13, fill=SOFT, family=F_DISPLAY, style="italic")
    return svg_doc(1200, 760, "The first batch in three bands", "Three bands labelled now, next and later, listing contracts, workspace tools and studio instruments.", body)


def fig_principles() -> str:
    body = title_block(64, 70, "Four principles", "They are short enough to remember and specific enough to settle an argument.")
    items = [
        ("01", "Rectangles behave", "Compact panes, direct menus and precise geometry. No hamburger archaeology.", "rect"),
        ("02", "Objects persist", "A note, table or drawing keeps its identity when another tool presents it.", "object"),
        ("03", "Output is native", "The same scene reaches display, PDF, thumbnail and print without translation.", "page"),
        ("04", "State speaks", "Current, refreshing, stale, broken and denied never hide behind a spinner.", "state"),
    ]
    for index, (num, title, text, glyph) in enumerate(items):
        col = index % 2
        row = index // 2
        x = 64 + col * 552
        y = 166 + row * 268
        body += rect(x, y, 528, 240, fill=HIGH, stroke=INK)
        body += txt(x + 20, y + 34, num, size=11, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.8)
        body += txt(x + 20, y + 76, title, size=28, family=F_DISPLAY, style="italic")
        body += lines(x + 20, y + 110, [text], size=12, fill=SOFT, leading=18)
        gx = x + 420
        gy = y + 150
        if glyph == "rect":
            body += rect(gx - 46, gy - 28, 92, 56, fill=PAPER, stroke=PINE2, sw=2)
            body += rect(gx - 34, gy - 16, 40, 18, fill=WHITE, stroke=LINE)
            body += rect(gx + 12, gy - 16, 22, 18, fill=WHITE, stroke=LINE)
        elif glyph == "object":
            body += ellipse(gx, gy, 40, 26, fill=PINE2, stroke=PINE)
            for angle, label in [(-60, "N"), (-10, "T"), (40, "D"), (90, "P")]:
                body += line(gx, gy, gx + 62 * __import__("math").cos(__import__("math").radians(angle)), gy + 62 * __import__("math").sin(__import__("math").radians(angle)), stroke=LINE)
                body += txt(gx + 68 * __import__("math").cos(__import__("math").radians(angle)), gy + 68 * __import__("math").sin(__import__("math").radians(angle)) + 4, label, size=9, fill=OXIDE, family=F_MONO, anchor="middle")
        elif glyph == "page":
            body += rect(gx - 38, gy - 34, 76, 68, fill=WHITE, stroke=INK)
            body += txt(gx, gy + 4, "PDF", size=13, family=F_MONO, weight="bold", anchor="middle", fill=OXIDE)
            body += line(gx - 26, gy + 18, gx + 26, gy + 18, stroke=LINE)
        else:
            sx = gx - 50
            for label, colour in [("CUR", PINE2), ("REF", TEAL_INK), ("STA", AMBER_INK)]:
                body += rect(sx, gy - 12, 32, 24, fill=HIGH, stroke=colour)
                body += txt(sx + 16, gy + 4, label, size=10, family=F_MONO, anchor="middle", fill=colour)
                sx += 36
    return svg_doc(1200, 740, "Four principles", "Four cards: rectangles behave, objects persist, output is native, and state speaks.", body)


def fig_document_centre() -> str:
    body = title_block(64, 70, "One object, four presentations", "The document is the stable thing. Presentation is how the same object appears for a task.")
    body += ellipse(600, 420, 76, 48, fill=PINE2, stroke=PINE, sw=2)
    body += txt(600, 426, "OBJ", size=15, fill=WHITE, family=F_MONO, weight="bold", anchor="middle")
    body += txt(600, 498, "stable identity", size=11, fill=SOFT, family=F_MONO, anchor="middle", spacing=0.6)
    frames = [
        (64, 166, "NOTE", "prose"),
        (896, 166, "TABLE", "data"),
        (64, 570, "REPORT", "card"),
        (896, 570, "PROOF", "page"),
    ]
    for x, y, label, kind in frames:
        body += rect(x, y, 240, 170, fill=HIGH, stroke=INK)
        body += txt(x + 12, y + 22, label, size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.8)
        body += txt(x + 228, y + 22, "GBP 1,284", size=9, fill=SOFT, family=F_MONO, anchor="end")
        if kind == "prose":
            body += mini_note(x + 12, y + 34, 216, 120)
            body += rect(x + 30, y + 86, 76, 16, fill=HIGH, stroke=PINE2)
            body += txt(x + 34, y + 97, "GBP 1,284", size=10, fill=PINE2, family=F_MONO)
        elif kind == "data":
            body += mini_table(x + 12, y + 34, 216, 120)
        elif kind == "card":
            body += rect(x + 12, y + 34, 216, 120, fill=WHITE, stroke=LINE)
            body += txt(x + 24, y + 60, "North Sea currency", size=11, fill=SOFT)
            body += txt(x + 24, y + 94, "GBP 1,284", size=24, fill=INK, family=F_MONO, weight="bold")
            body += txt(x + 24, y + 120, "report card · 2026", size=10, fill=SOFT, family=F_MONO)
        else:
            body += mini_page(x + 12, y + 34, 216, 120)
        start_x = x + 240 if x < 600 else x
        start_y = y + 85
        end_x = 524 if x < 600 else 676
        body += line(start_x, start_y, end_x, 420, stroke=LINE, sw=1.5, dash="4 4")
        body += circle(start_x, start_y, 3, fill=OXIDE, stroke=None)
    body += txt(64, 700, "Presentation changes. Identity does not.", size=20, family=F_DISPLAY, style="italic", fill=PINE)
    body += txt(64, 726, "A conversion is not a new object unless the user duplicates or derives one.", size=12, fill=SOFT)
    return svg_doc(1200, 760, "One object with four presentations", "A central object connected to note, table, drawing and page presentations.", body)


def fig_state() -> str:
    body = title_block(64, 70, "Failure has a shape", "Five visible states, one vocabulary. A spinner is not a state description.")
    states = [
        ("Current", PINE2, "The accepted value matches every known source revision.", "Use the value."),
        ("Refreshing", TEAL_INK, "A refresh is in flight. The last accepted value may remain visible.", "Keep the old value."),
        ("Stale", AMBER_INK, "The source reports a newer revision than the accepted value.", "Keep and label it."),
        ("Broken", OXIDE, "The source is unreachable, or no value has been accepted.", "Keep the link."),
        ("Denied", OXIDE, "Current authority does not permit the read.", "Explain the grant."),
    ]
    for index, (name, colour, text, action) in enumerate(states):
        x = 64 + index * 220
        mark = str(LIVE_STATES[name]["mark"])
        body += f'<g data-mark="{mark}">'
        body += rect(x, 166, 204, 190, fill=HIGH, stroke=colour, sw=2 if name in {"Stale", "Denied"} else 1)
        body += state_mark(x + 22, 194, mark, colour)
        body += txt(x + 38, 200, name.upper(), size=12, fill=colour, family=F_MONO, weight="bold", spacing=0.6, data_state=name)
        body += para(x + 18, 226, 168, text, size=11, leading=16)
        body += line(x + 18, 300, x + 186, 300, stroke=LINE)
        body += txt(x + 18, 326, action, size=11, fill=INK, weight="bold")
        body += "</g>"

    # Legal transitions, taken from the state table in chapter 8.
    body += txt(64, 400, "LEGAL TRANSITIONS", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    body += txt(80, 430, "FROM", size=9, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.6)
    body += txt(300, 430, "EVENT", size=9, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.6)
    body += txt(700, 430, "TO", size=9, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.6)
    body += txt(850, 430, "OWNER", size=9, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.6)
    for index, transition in enumerate(LIVE_TRANSITIONS):
        ty = 460 + index * 24
        source = ", ".join(transition["from"])
        body += line(64, ty - 17, 1136, ty - 17, stroke=LINE, sw=0.5)
        body += txt(80, ty, source, size=11, fill=INK, family=F_MONO)
        body += txt(300, ty, transition["event"], size=11, fill=SOFT)
        body += txt(700, ty, transition["to"], size=11, fill=PINE2, family=F_MONO)
        body += txt(850, ty, transition["owner"], size=11, fill=SOFT, family=F_MONO)
    body += txt(64, 810, "Authority and provider loss move the state directly. Every refresh passes through Refreshing.", size=13, fill=SOFT, family=F_DISPLAY, style="italic")
    body += txt(64, 836, "A cancelled request recomputes the chip from the facts; it never restores an old label.", size=13, fill=SOFT, family=F_DISPLAY, style="italic")
    return svg_doc(1200, 880, "Five live-relationship states and their legal transitions", "Cards for current, refreshing, stale, broken and denied, followed by the legal transition table with owners.", body)


# ---------------------------------------------------------------------------
# Foundations


def fig_palette() -> str:
    body = title_block(64, 70, "The material palette", "Paper, ink, pine, teal, oxide and amber. Colour is material and state, not decoration.")
    light = [
        ("Paper", PAPER, INK, "ground"),
        ("High", HIGH, INK, "raised pane"),
        ("Ink", INK, PAPER, "text"),
        ("Soft", SOFT, PAPER, "secondary"),
        ("Pine", PINE, PAPER, "window edge"),
        ("Pine 2", PINE2, PAPER, "selection"),
        ("Teal", TEAL, INK, "decoration only"),
        ("Teal ink", TEAL_INK, PAPER, "refresh text"),
        ("Oxide", OXIDE, PAPER, "authority"),
        ("Amber", AMBER, INK, "large marks"),
        ("Amber ink", AMBER_INK, PAPER, "stale text"),
        ("Line", LINE, INK, "hairline"),
    ]
    for index, (name, colour, text_colour, note) in enumerate(light):
        x = 64 + (index % 6) * 180
        y = 166 + (index // 6) * 150
        body += rect(x, y, 168, 128, fill=colour, stroke=INK)
        body += txt(x + 12, y + 22, name, size=11, fill=text_colour, family=F_MONO, weight="bold")
        body += txt(x + 12, y + 44, colour, size=10, fill=text_colour, family=F_MONO)
        body += txt(x + 12, y + 108, note, size=10, fill=text_colour)
    body += txt(64, 500, "DARK", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    dark = [
        ("Ground", DARK, DARK_TEXT),
        ("Surface", DARK_SURFACE, DARK_TEXT),
        ("Text", DARK_TEXT, DARK),
        ("Muted", DARK_MUTED, DARK),
        ("Pine", DARK_PINE, DARK),
        ("Oxide", DARK_OXIDE, DARK),
        ("Amber", DARK_AMBER, DARK),
    ]
    for index, (name, colour, text_colour) in enumerate(dark):
        x = 64 + index * 158
        body += rect(x, 522, 144, 96, fill=colour, stroke=INK)
        body += txt(x + 10, 546, name, size=10, fill=text_colour, family=F_MONO, weight="bold")
        body += txt(x + 10, 566, colour, size=9, fill=text_colour, family=F_MONO)
    body += lines(
        64,
        664,
        [
            "Amber #B8792E is a large-text and icon accent; use #8A5B24 for body-size text.",
            "Teal #678E86 is decoration and refresh motion, never body text on paper.",
            "Line #AAA99F is a hairline, not a text colour.",
        ],
        size=11,
        fill=SOFT,
        leading=18,
    )
    return svg_doc(1200, 760, "The material palette in light and dark", "Light and dark swatches with names, hex values and contrast-safe roles.", body)


def fig_type() -> str:
    body = title_block(64, 70, "Three typographic voices", "Display argues, interface explains, metadata accounts. They do not trade places.")
    body += rect(64, 166, 352, 240, fill=HIGH, stroke=INK)
    body += kicker(84, 196, "Display / Georgia italic")
    body += lines(84, 248, ["Pages know", "where they", "are going."], size=42, family=F_DISPLAY, style="italic", leading=46)
    body += txt(84, 380, "Long-form titles and pull quotes only.", size=10, fill=SOFT, family=F_MONO)

    body += rect(432, 166, 352, 240, fill=HIGH, stroke=INK)
    body += kicker(452, 196, "Interface / humanist sans")
    body += lines(452, 250, ["Selection:", "Annual energy balance", "4 tools available"], size=19, leading=28)
    body += txt(452, 380, "Controls, labels, prose in panels.", size=10, fill=SOFT, family=F_MONO)

    body += rect(800, 166, 336, 240, fill=HIGH, stroke=INK)
    body += kicker(820, 196, "Metadata / humanist mono")
    body += lines(820, 250, ["OBJ 7F4C", "CURRENT", "PDF/X-4 · 125%"], size=13, family=F_MONO, leading=26)
    body += txt(820, 380, "Identity, state, units, shortcuts.", size=10, fill=SOFT, family=F_MONO)

    rows = [
        ("Display", "42-96 / 0.95", "Georgia italic", "chapter and cover titles"),
        ("Title", "24-32 / 1.1", "Georgia italic", "tool and document titles"),
        ("Subtitle", "18 / 1.2", "Georgia italic", "inspector object names"),
        ("Section", "16-20 / 1.2", "Humanist sans bold", "pane and dialog headings"),
        ("Body", "15-16 / 1.6", "Georgia or humanist sans", "notes and long-form prose"),
        ("Interface", "12 / 1.35", "Humanist sans", "controls, labels, menus"),
        ("Metadata", "11 / 1.4", "Humanist mono", "identity, state, units"),
        ("Folio", "10 / 1.2", "Humanist mono", "folios and plate marks"),
    ]
    body += txt(64, 458, "SIZE", size=9, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    body += txt(180, 458, "SIZE / LINE", size=9, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    body += txt(330, 458, "FACE", size=9, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    body += txt(560, 458, "USE", size=9, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    for index, (name, size, face, use) in enumerate(rows):
        y = 482 + index * 30
        body += line(64, y, 1136, y, stroke=LINE)
        body += txt(64, y + 20, name, size=12, weight="bold")
        body += txt(180, y + 20, size, size=11, family=F_MONO, fill=SOFT)
        body += txt(330, y + 20, face, size=11, fill=SOFT)
        body += txt(560, y + 20, use, size=11, fill=SOFT)
    body += txt(64, 740, "No interface text below 12 px. 11 px metadata is for non-essential labels; 10 px only for folios and plate marks.", size=11, fill=OXIDE)
    return svg_doc(1200, 760, "Three typographic voices and a type scale", "Display, interface and metadata specimens above an eight-row type scale.", body)


def fig_spacing() -> str:
    body = title_block(64, 70, "Spacing, density and targets", "A four-pixel grid, eight steps, and a floor under every pointer target.")
    steps = [4, 8, 12, 16, 24, 32, 48, 64]
    for index, step in enumerate(steps):
        y = 166 + index * 58
        body += txt(64, y + 14, str(step), size=10, fill=SOFT, family=F_MONO, anchor="end")
        body += rect(80, y, step * 3, 22, fill=PINE2, stroke=None)
        body += txt(92 + step * 3, y + 16, f"{step} px", size=10, fill=SOFT, family=F_MONO)
    body += txt(64, 660, "Use 4/8/12/16 for in-pane rhythm; 24/32/48/64 for structure.", size=11, fill=SOFT)

    body += rect(600, 166, 536, 390, fill=HIGH, stroke=INK)
    body += txt(620, 196, "A measured tool strip", size=11, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.8)
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
    body += txt(600, 600, "Density is a property of the pane, not an excuse to shrink the hit target.", size=13, fill=SOFT, family=F_DISPLAY, style="italic")
    return svg_doc(1200, 720, "Spacing scale and measured tool strip", "Eight spacing steps and an annotated toolbar with target and padding measurements.", body)


def fig_planes() -> str:
    body = title_block(64, 70, "Planes, borders and elevation", "The interface is made of flat planes with exact edges. Depth is a border and an offset, not a glow.")
    planes = [
        ("PAPER", PAPER, 0, 0, "the document ground"),
        ("PANE", HIGH, 120, 70, "a region of work"),
        ("CONTROL", "#E4E3DD", 240, 140, "a thing you can press"),
        ("OVERLAY", HIGH, 360, 210, "a thing that must be seen"),
    ]
    for name, colour, dx, dy, note in planes:
        x = 220 + dx
        y = 200 + dy
        body += rect(x + 12, y + 14, 420, 210, fill="#17201C18", stroke=None)
        body += rect(x, y, 420, 210, fill=colour, stroke=INK, sw=1.5 if name == "OVERLAY" else 1)
        body += txt(x + 16, y + 28, name, size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.8)
        body += txt(x + 16, y + 52, note, size=12, fill=SOFT)
    body += txt(780, 242, "1 px border", size=11, fill=SOFT, family=F_MONO)
    body += line(720, 254, 880, 254, stroke=LINE)
    body += txt(780, 284, "No blur", size=11, fill=SOFT, family=F_MONO)
    body += txt(780, 326, "Offset shadow only for overlays", size=11, fill=SOFT, family=F_MONO)
    body += txt(780, 368, "Never raise a control with a glow", size=11, fill=SOFT, family=F_MONO)
    body += txt(64, 690, "A border says where a thing ends. An offset says that it floats. Nothing else needs to be said.", size=13, fill=SOFT, family=F_DISPLAY, style="italic")
    return svg_doc(1200, 740, "Four interface planes", "Paper, pane, control and overlay planes, each with a border and only the overlay with an offset shadow.", body)


def fig_icons() -> str:
    body = title_block(64, 70, "Icons and glyphs", "Monochrome line drawings at 16, 20 and 24 pixels. Colour is reserved for state.")
    glyphs = [
        ("select", "M 8 6 L 22 18 L 16 19 L 19 28 L 15 29 L 12 20 L 8 25 Z"),
        ("text", "M 10 9 H 30 M 20 9 V 29"),
        ("rect", "M 8 10 H 32 V 28 H 8 Z"),
        ("ellipse", "M 20 8 C 28 8 34 13 34 19 C 34 25 28 30 20 30 C 12 30 6 25 6 19 C 6 13 12 8 20 8 Z"),
        ("pen", "M 9 30 L 12 20 L 25 7 L 31 13 L 18 26 Z M 12 20 L 18 26"),
        ("line", "M 8 28 L 32 10"),
        ("table", "M 7 9 H 33 V 29 H 7 Z M 7 16 H 33 M 7 22 H 33 M 15 9 V 29 M 24 9 V 29"),
        ("formula", "M 9 28 C 12 28 13 24 14 19 C 15 13 17 9 21 9 M 10 18 H 20 M 24 16 L 30 24 M 30 16 L 24 24"),
        ("link", "M 15 24 L 12 27 C 8 30 4 26 7 22 L 12 17 M 25 16 L 28 13 C 31 9 27 5 23 8 L 18 13 M 14 22 L 26 10"),
        ("lock", "M 11 19 V 14 C 11 8 29 8 29 14 V 19 M 8 19 H 32 V 31 H 8 Z"),
        ("warning", "M 20 8 L 34 30 H 6 Z M 20 15 V 22 M 20 26 V 27"),
        ("check", "M 8 20 L 16 28 L 32 10"),
        ("refresh", "M 29 15 C 27 9 18 7 13 12 C 8 17 10 26 17 29 M 29 15 V 8 M 29 15 H 22"),
        ("gear", "M 20 13 A 7 7 0 1 0 20 27 A 7 7 0 1 0 20 13 M 20 6 V 10 M 20 30 V 34 M 6 20 H 10 M 30 20 H 34 M 10 10 L 13 13 M 27 27 L 30 30 M 30 10 L 27 13 M 13 27 L 10 30"),
    ]
    for index, (name, d) in enumerate(glyphs):
        col = index % 7
        row = index // 7
        x = 64 + col * 156
        y = 166 + row * 142
        body += rect(x, y, 132, 116, fill=HIGH, stroke=LINE)
        body += f'<g transform="translate({x + 26} {y + 26}) scale(1.25)">{path(d, stroke=INK, sw=2)}</g>'
        body += txt(x + 10, y + 100, name, size=10, fill=SOFT, family=F_MONO)

    body += txt(64, 500, "SIZES", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    for index, size in enumerate([16, 20, 24]):
        x = 64 + index * 180
        body += rect(x, 520, 156, 120, fill=HIGH, stroke=LINE)
        body += f'<g transform="translate({x + 60} {570 - size / 2}) scale({size / 24})">{path("M 8 20 L 16 28 L 32 10", stroke=INK, sw=2)}</g>'
        body += txt(x + 12, 620, f"{size} px", size=10, fill=SOFT, family=F_MONO)

    body += txt(640, 500, "STATES", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    for index, (label, colour, note) in enumerate(
        [("Default", INK, "inherits text"), ("Active", OXIDE, "current tool"), ("Stale", AMBER_INK, "with a label"), ("Disabled", LINE, "not focusable")]
    ):
        y = 520 + index * 44
        body += rect(640, y, 44, 32, fill=HIGH, stroke=LINE)
        body += f'<g transform="translate(650 {y + 2})">{path("M 8 20 L 16 28 L 32 10", stroke=colour, sw=2)}</g>'
        body += txt(700, y + 16, label, size=11, weight="bold", fill=colour if colour != LINE else SOFT)
        body += txt(700, y + 32, note, size=10, fill=SOFT)
    body += txt(640, 712, "A 16 px icon may sit inside a 28 px target; the target, not the glyph, is the contract.", size=11, fill=SOFT)
    return svg_doc(1200, 760, "Icon grid, sizes and states", "Fourteen line glyphs across two rows, plus size and state examples.", body)


def fig_motion() -> str:
    body = title_block(64, 70, "Motion with a reason", "Motion explains a change of state. It does not perform.")
    # Axes.
    ox, oy = 150, 560
    w, h = 760, 360
    body += line(ox, oy, ox + w, oy, stroke=INK)
    body += line(ox, oy, ox, oy - h, stroke=INK)
    for index in range(5):
        x = ox + index * w / 4
        body += line(x, oy, x, oy + 6, stroke=INK)
        body += txt(x, oy + 24, f"{index * 55}", size=9, fill=SOFT, family=F_MONO, anchor="middle")
    body += txt(ox + w / 2, oy + 50, "milliseconds", size=10, fill=SOFT, family=F_MONO, anchor="middle")
    body += txt(ox - 16, oy - h, "1", size=9, fill=SOFT, family=F_MONO, anchor="end")
    body += txt(ox - 16, oy, "0", size=9, fill=SOFT, family=F_MONO, anchor="end")

    curves = [
        (80, PINE2, "state change"),
        (140, TEAL, "pane reveal"),
        (180, OXIDE, "window"),
    ]
    for duration, colour, label in curves:
        x_end = ox + (duration / 220) * w
        d = f"M {ox} {oy} C {ox + (x_end - ox) * 0.2} {oy - h * 0.55}, {ox + (x_end - ox) * 0.55} {oy - h * 0.92}, {x_end} {oy - h}"
        body += path(d, stroke=colour, sw=2.5)
        body += circle(x_end, oy - h, 5, fill=colour, stroke=None)
        body += txt(x_end + 10, oy - h + 4, f"{duration} ms", size=10, fill=colour, family=F_MONO)
    body += txt(ox + 40, oy - h - 24, "progress", size=10, fill=SOFT, family=F_MONO)

    body += rect(940, 166, 196, 250, fill=HIGH, stroke=INK)
    body += txt(956, 194, "RULES", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
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
    body += txt(64, 690, "If a change cannot be explained in one sentence, it does not need a transition.", size=13, fill=SOFT, family=F_DISPLAY, style="italic")
    return svg_doc(1200, 720, "Motion timing chart", "Ease-out curves for 80, 140 and 180 millisecond transitions, with rules for restrained motion.", body)


# ---------------------------------------------------------------------------
# Interface chrome


def wrap_words(value: str, max_chars: int) -> list[str]:
    wrapped: list[str] = []
    current = ""
    for word in value.split():
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= max_chars:
            current = f"{current} {word}"
        else:
            wrapped.append(current)
            current = word
    if current:
        wrapped.append(current)
    return wrapped


def para(x: float, y: float, width: float, value: str, size: float = 11, leading: float = 16, fill: str = SOFT, **kwargs: object) -> str:
    return lines(x, y, wrap_words(value, max(8, int(width / (size * 0.52)))), size=size, leading=leading, fill=fill, **kwargs)


def titlebar(x: float, y: float, w: float, title: str, rtl: bool = False, controls: bool = True) -> str:
    body = rect(x, y, w, 31, fill=PAPER, stroke=None)
    body += line(x, y + 30.5, x + w, y + 30.5, stroke=LINE)
    if rtl:
        body += txt(x + w - (112 if controls else 12), y + 20, title, size=12, weight="bold", anchor="end")
    else:
        body += txt(x + 12, y + 20, title, size=12, weight="bold")
    if controls:
        for index, glyph in enumerate(["–", "□", "×"]):
            bx = x + 4 + index * 36 if rtl else x + w - 104 + index * 36
            body += txt(bx + 14, y + 22, glyph, size=16, anchor="middle")
    return body


def menu_strip(x: float, y: float, w: float, items: list[str], active: str | None = None, rtl: bool = False) -> str:
    body = rect(x, y, w, 29, fill=PAPER, stroke=None)
    body += line(x, y + 28.5, x + w, y + 28.5, stroke=LINE)
    cursor = x + w - 15 if rtl else x + 10
    for item in items:
        item_width = len(item) * 7 + 20
        if rtl:
            if item == active:
                body += rect(cursor - item_width + 5, y + 3, item_width, 23, fill=PINE2, stroke=None)
                body += txt(cursor - 5, y + 19, item, size=12, fill=WHITE, weight="bold", anchor="end")
            else:
                body += txt(cursor - 5, y + 19, item, size=12, fill=INK, anchor="end")
            cursor -= item_width
        else:
            if item == active:
                body += rect(cursor - 5, y + 3, item_width, 23, fill=PINE2, stroke=None)
                body += txt(cursor + 5, y + 19, item, size=12, fill=WHITE, weight="bold")
            else:
                body += txt(cursor + 5, y + 19, item, size=12, fill=INK)
            cursor += item_width
    return body


def status_bar(x: float, y: float, w: float, message: str, state: str | None = None, rtl: bool = False) -> str:
    body = rect(x, y, w, 26, fill=PAPER, stroke=None)
    body += line(x, y + 0.5, x + w, y + 0.5, stroke=LINE)
    if rtl:
        body += txt(x + w - 10, y + 17, message, size=11, fill=SOFT, anchor="end")
        if state:
            chip_body, _ = state_chip(x + 10, y + 1, state)
            body += chip_body
    else:
        body += txt(x + 10, y + 17, message, size=11, fill=SOFT)
        if state:
            chip_body, _ = state_chip(x + w - 120, y + 1, state)
            body += chip_body
    return body


def pane_head(x: float, y: float, w: float, title: str, right: str | None = None) -> str:
    body = rect(x, y, w, 28, fill=PAPER, stroke=None)
    body += line(x, y + 27.5, x + w, y + 27.5, stroke=LINE)
    body += txt(x + 10, y + 18, title.upper(), size=10, fill=SOFT, weight="bold", spacing=0.8)
    if right:
        body += txt(x + w - 10, y + 18, right, size=10, fill=SOFT, anchor="end")
    return body


def window_shell(x: float, y: float, w: float, h: float, title: str, menu: list[str], active_menu: str | None = None, status: str | None = None, state: str | None = None, rtl: bool = False) -> str:
    body = rect(x + 8, y + 8, w, h, fill="#17201C20", stroke=None)
    body += rect(x, y, w, h, fill=HIGH, stroke=INK)
    body += titlebar(x, y, w, title, rtl=rtl)
    body += menu_strip(x, y + 31, w, menu, active_menu, rtl=rtl)
    body += line(x, y + 60, x + w, y + 60, stroke=LINE)
    if status is not None:
        body += status_bar(x, y + h - 26, w, status, state, rtl=rtl)
    return body


def field(x: float, y: float, w: float, value: str, label: str | None = None, height: float = 32, focus: bool = False) -> str:
    body = ""
    if label:
        body += txt(x, y - 6, label, size=11, fill=SOFT)
    body += rect(x, y, w, height, fill=WHITE, stroke=OXIDE if focus else LINE, sw=2 if focus else 1)
    body += txt(x + 10, y + height / 2 + 4, value, size=12, fill=INK)
    return body


def button(x: float, y: float, w: float, label: str, primary: bool = False, destructive: bool = False, height: float = 32, disabled: bool = False) -> str:
    fill = PINE if primary else HIGH
    stroke = PINE if primary else LINE
    colour = WHITE if primary else (OXIDE if destructive else INK)
    if disabled:
        fill = PAPER
        stroke = LINE
        colour = SOFT
    body = rect(x, y, w, height, fill=fill, stroke=stroke)
    body += txt(x + w / 2, y + height / 2 + 4, label, size=12, fill=colour, weight="bold", anchor="middle")
    return body


def checkbox(x: float, y: float, label: str, checked: bool = False) -> str:
    body = rect(x, y - 13, 16, 16, fill=WHITE, stroke=INK)
    if checked:
        body += path(f"M {x + 3} {y - 4} L {x + 7} {y} L {x + 14} {y - 9}", stroke=PINE2, sw=2.5)
    body += txt(x + 24, y, label, size=12, fill=INK)
    return body


def radio(x: float, y: float, label: str, selected: bool = False) -> str:
    body = circle(x + 8, y - 5, 8, fill=WHITE, stroke=INK)
    if selected:
        body += circle(x + 8, y - 5, 4, fill=PINE2, stroke=None)
    body += txt(x + 24, y, label, size=12, fill=INK)
    return body


def inspector_row(x: float, y: float, w: float, label: str, value: str, value_colour: str = INK) -> str:
    body = txt(x, y, label.upper(), size=10, fill=SOFT, family=F_MONO, spacing=0.5)
    body += txt(x + w, y, value, size=11, fill=value_colour, anchor="end")
    body += line(x, y + 8, x + w, y + 8, stroke=LINE, sw=0.5)
    return body


def fig_window() -> str:
    body = title_block(64, 70, "Window anatomy", "A compact frame with direct commands, named panes and a status line that explains what is happening.")
    x, y, w, h = 150, 160, 900, 540
    body += window_shell(x, y, w, h, "Facet Notes — North Sea transition", ["File", "Edit", "View", "Object", "Tools", "Window", "Help"], status="Refreshing currency… last value 14:02", state="Refreshing")
    # Tool strip.
    body += rect(x, y + 60, w, 30, fill=PAPER, stroke=None)
    body += line(x, y + 90, x + w, y + 90, stroke=LINE)
    for index, glyph in enumerate(["select", "text", "rect", "pen", "link"]):
        bx = x + 10 + index * 38
        active = index == 1
        body += rect(bx, y + 60, 30, 30, fill=PINE2 if active else HIGH, stroke=LINE)
        colour = WHITE if active else INK
        cx, cy = bx + 15, y + 75
        if glyph == "select":
            body += path(f"M {cx - 5} {cy - 7} L {cx + 3} {cy + 4} L {cx - 1} {cy + 4} L {cx + 1} {cy + 10} L {cx - 3} {cy + 11} L {cx - 5} {cy + 5} L {cx - 8} {cy + 8} Z", stroke=colour, sw=1.4)
        elif glyph == "text":
            body += txt(cx, cy + 5, "T", size=13, fill=colour, weight="bold", anchor="middle")
        elif glyph == "rect":
            body += rect(cx - 7, cy - 5, 14, 10, fill="none", stroke=colour, sw=1.4)
        elif glyph == "pen":
            body += path(f"M {cx - 6} {cy + 7} L {cx - 4} {cy} L {cx + 5} {cy - 9} L {cx + 9} {cy - 5} L {cx} {cy + 4} Z", stroke=colour, sw=1.4)
        else:
            body += path(f"M {cx - 6} {cy + 4} L {cx - 8} {cy + 6} M {cx + 6} {cy - 4} L {cx + 8} {cy - 6} M {cx - 7} {cy + 2} L {cx + 7} {cy - 2}", stroke=colour, sw=1.4)
    # Panes.
    tree_w, inspector_w = 210, 240
    body += line(x, y + 90, x, y + h - 26, stroke=LINE)
    body += rect(x, y + 90, tree_w, h - 116, fill=PAPER, stroke=None)
    body += pane_head(x, y + 90, tree_w, "Notes", "+")
    tree_rows = [("Project", 0, False), ("North Sea transition", 1, True), ("Sources", 1, False), ("Generation mix", 2, False), ("Currency", 2, False), ("Figures", 1, False)]
    for index, (name, depth, selected) in enumerate(tree_rows):
        ry = y + 120 + index * 28
        if selected:
            body += rect(x, ry - 18, tree_w, 26, fill=PINE2, stroke=None)
        body += txt(x + 12 + depth * 14, ry, name, size=11, fill=WHITE if selected else INK)
        if depth == 0:
            body += txt(x + tree_w - 14, ry, "▾", size=10, fill=WHITE if selected else SOFT, anchor="end")
    splitter_1 = x + tree_w
    splitter_2 = x + w - inspector_w
    body += line(splitter_1, y + 90, splitter_1, y + h - 26, stroke=INK)
    body += line(splitter_2, y + 90, splitter_2, y + h - 26, stroke=INK)
    body += rect(splitter_1 - 3, y + 300, 6, 42, fill=LINE, stroke=INK)
    body += rect(splitter_2 - 3, y + 300, 6, 42, fill=LINE, stroke=INK)
    # Editor.
    body += pane_head(splitter_1, y + 90, splitter_2 - splitter_1, "Document", "Edited 14:02")
    ex = splitter_1 + 22
    body += txt(ex, y + 150, "North Sea transition", size=24, family=F_DISPLAY, style="italic")
    body += para(ex, y + 180, splitter_2 - splitter_1 - 44, "The project note holds prose, a dataframe and a diagram without flattening any of them.", size=11, leading=16)
    body += rect(ex, y + 230, splitter_2 - splitter_1 - 44, 74, fill=HIGH, stroke=LINE)
    body += txt(ex + 12, y + 252, "Generation mix", size=12, weight="bold")
    body += txt(ex + 12, y + 270, "Table · 12 rows · 4 columns", size=10, fill=SOFT, family=F_MONO)
    state_body, _ = state_chip(splitter_2 - 100, y + 246, "Current")
    body += state_body
    body += rect(ex, y + 316, splitter_2 - splitter_1 - 44, 74, fill=HIGH, stroke=LINE)
    body += txt(ex + 12, y + 338, "Transition pathways", size=12, weight="bold")
    body += txt(ex + 12, y + 356, "Diagram · Mermaid source", size=10, fill=SOFT, family=F_MONO)
    state_body, _ = state_chip(splitter_2 - 100, y + 332, "Stale")
    body += state_body
    body += para(ex, y + 424, splitter_2 - splitter_1 - 44, "Links remain links. A reader can open the source, change the presentation, or inspect the object behind it.", size=11, leading=16)
    # Inspector.
    body += pane_head(splitter_2, y + 90, inspector_w, "Inspector")
    ix, iw = splitter_2 + 14, inspector_w - 28
    body += txt(ix, y + 132, "Generation mix", size=12, weight="bold")
    body += txt(ix, y + 148, "Table object", size=11, fill=SOFT)
    body += inspector_row(ix, y + 178, iw, "Object", "obj:8f3a")
    body += inspector_row(ix, y + 204, iw, "Provider", "enfilade.table")
    body += inspector_row(ix, y + 230, iw, "Revision", "r17")
    body += txt(ix, y + 262, "PRESENTATION", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.6)
    body += checkbox(ix, y + 286, "In note", True)
    body += checkbox(ix, y + 308, "Dataframe", True)
    body += checkbox(ix, y + 330, "Print table", False)
    body += txt(ix, y + 362, "CAPABILITIES", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.6)
    body += txt(ix, y + 384, "Read      granted", size=11, fill=PINE2, family=F_MONO)
    body += txt(ix, y + 402, "Write     granted", size=11, fill=PINE2, family=F_MONO)
    body += txt(ix, y + 420, "Share     denied", size=11, fill=OXIDE, family=F_MONO)
    # Callout numbers.
    callouts = [(1, x - 22, y + 16, x, y + 16), (2, x - 22, y + 46, x, y + 46), (3, x - 22, y + 75, x, y + 75), (4, x - 22, y + 104, x, y + 104), (5, x + w + 22, y + 104, x + w, y + 104), (6, x - 22, y + h - 13, x, y + h - 13)]
    for number, cx, cy, target_x, target_y in callouts:
        body += line(cx + (9 if cx < x else -9), cy, target_x, target_y, stroke=OXIDE, sw=1)
        body += circle(cx, cy, 9, fill=OXIDE, stroke=None)
        body += txt(cx, cy + 3.5, str(number), size=10, fill=WHITE, weight="bold", anchor="middle", family=F_MONO)
    legend = [
        "1  title bar 31 px",
        "2  menu bar 29 px",
        "3  tool strip 30 px",
        "4  pane head 28 px",
        "5  inspector 240 px",
        "6  status line 26 px",
    ]
    for index, text in enumerate(legend):
        body += txt(64 + (index % 3) * 380, 726 + (index // 3) * 18, text, size=10, fill=SOFT, family=F_MONO)
    return svg_doc(1200, 780, "Window anatomy with labelled metrics", "A Facet Notes window with title bar, menu bar, tool strip, note tree, document, inspector and status line, annotated with pixel metrics.", body)


def fig_menus() -> str:
    body = title_block(64, 70, "Menus name commands", "A menu is a list of verbs. It is not a catalogue of everything the application can do.")
    x, y, w, h = 64, 160, 700, 450
    body += window_shell(x, y, w, h, "Facet Notes — North Sea transition", ["File", "Edit", "View", "Object", "Tools", "Window", "Help"], active_menu="File", status="North Sea transition · saved 14:02")
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
            body += txt(mx + mw - 18, item_y + 18, shortcut, size=11, fill=SOFT, family=F_MONO, anchor="end")
        row += 1
    # Hover highlight on Save.
    body += rect(mx + 6, my + 8 + 4 * 28, mw - 12, 28, fill=PINE2, stroke=None, opacity=0.12)
    # Notes.
    nx = 820
    body += txt(nx, 190, "RULES", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
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
    body += para(nx, 440, 316, "Submenus collect variations of one verb. They do not bury unrelated features. A submenu that exists only to shorten a long menu should be removed.", size=11, leading=17)
    body += para(nx, 522, 316, "Menu bars stay visible. When the window is narrow, whole menus move into More; commands do not become a hamburger.", size=11, leading=17)
    return svg_doc(1200, 760, "A menu bar with an open File menu", "A File menu showing commands, shortcuts, a disabled item and separators, with rules for naming and availability.", body)


def fig_toolbars() -> str:
    body = title_block(64, 70, "Tool strips and status", "Tools sit next to the work. The status line says what the tool will do, what it just did, and what state the data is in.")
    x, y, w = 64, 160, 1072
    body += rect(x + 8, y + 8, w, 76, fill="#17201C18", stroke=None)
    body += rect(x, y, w, 76, fill=HIGH, stroke=INK)
    body += titlebar(x, y, w, "Burin Draw — Currency plate")
    body += rect(x, y + 31, w, 30, fill=PAPER, stroke=None)
    body += line(x, y + 61, x + w, y + 61, stroke=LINE)
    for index, glyph in enumerate(["select", "pen", "line", "rect", "ellipse", "text"]):
        bx = x + 12 + index * 38
        active = index == 1
        body += rect(bx, y + 31, 30, 30, fill=PINE2 if active else HIGH, stroke=LINE)
        cx, cy = bx + 15, y + 46
        colour = WHITE if active else INK
        if glyph == "select":
            body += path(f"M {cx - 5} {cy - 7} L {cx + 3} {cy + 4} L {cx - 1} {cy + 4} L {cx + 1} {cy + 10} L {cx - 3} {cy + 11} L {cx - 5} {cy + 5} L {cx - 8} {cy + 8} Z", stroke=colour, sw=1.4)
        elif glyph == "pen":
            body += path(f"M {cx - 6} {cy + 7} L {cx - 4} {cy} L {cx + 5} {cy - 9} L {cx + 9} {cy - 5} L {cx} {cy + 4} Z", stroke=colour, sw=1.4)
        elif glyph == "line":
            body += line(cx - 7, cy + 7, cx + 7, cy - 7, stroke=colour, sw=2)
        elif glyph == "rect":
            body += rect(cx - 7, cy - 5, 14, 10, fill="none", stroke=colour, sw=1.4)
        elif glyph == "ellipse":
            body += ellipse(cx, cy, 8, 6, fill="none", stroke=colour, sw=1.4)
        else:
            body += txt(cx, cy + 5, "T", size=14, fill=colour, weight="bold", anchor="middle")
    body += line(x + 240, y + 37, x + 240, y + 57, stroke=LINE)
    body += txt(x + 248, y + 50, "Stroke  1 px", size=11, fill=SOFT)
    body += txt(x + 400, y + 50, "Grid  16 px", size=11, fill=SOFT)
    body += txt(x + 520, y + 50, "Zoom  100%", size=11, fill=SOFT)
    body += txt(x + w - 14, y + 50, "Inspector", size=11, fill=SOFT, anchor="end")
    # Status line example.
    sy = 300
    body += rect(x, sy, w, 26, fill=PAPER, stroke=INK)
    body += txt(x + 14, sy + 17, "Pen · dragging a 2 px stroke · 14 objects selected", size=12, fill=INK)
    state_body, _ = state_chip(x + w - 130, sy + 3, "Current")
    body += state_body
    body += txt(x + w - 150, sy + 17, "Saved 14:02", size=11, fill=SOFT, anchor="end", family=F_MONO)
    # Target sizes.
    body += txt(64, 404, "TARGET SIZES", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    sizes = [(28, "minimum", HIGH, INK), (32, "preferred", HIGH, INK), (36, "primary action", PINE, WHITE)]
    for index, (size, role, fill, colour) in enumerate(sizes):
        bx = 64 + index * 220
        body += rect(bx, 430, size, size, fill=fill, stroke=INK)
        body += txt(bx + size / 2, 430 + size / 2 + 4, "Aa", size=11, fill=colour, anchor="middle")
        body += txt(bx, 488, f"{size} × {size}  {role}", size=11, fill=SOFT, family=F_MONO)
    body += para(64, 540, 500, "The glyph may be 16 px. The target is never smaller than 28 px, and a primary action in a dialog is 36 px high.", size=11, leading=17)
    body += para(64, 610, 500, "Tool strips contain tools, not commands. Save, print and preferences belong in menus or the command palette.", size=11, leading=17)
    body += para(620, 540, 516, "A status line is a sentence, not a progress ornament. It names the object, the operation and the result, and it keeps the last useful value visible while a refresh is in flight.", size=11, leading=17)
    body += txt(620, 640, "Spinners may accompany a sentence. They never replace one.", size=12, fill=OXIDE, family=F_DISPLAY, style="italic")
    return svg_doc(1200, 760, "Tool strip, status line and target sizes", "A drawing tool strip, a status line with a live state, and minimum, preferred and primary target sizes.", body)


def fig_panes() -> str:
    body = title_block(64, 70, "Panes that keep their promises", "A pane has a name, a minimum width and a remembered position. It never disappears without leaving a handle.")
    # Diagram.
    x, y, h = 64, 170, 360
    body += rect(x, y, 210, h, fill=PAPER, stroke=INK)
    body += pane_head(x, y, 210, "Navigator")
    body += para(x + 14, y + 56, 182, "Project tree, saved views and recent objects.", size=11, leading=16)
    body += rect(x + 210, y, 6, h, fill=LINE, stroke=INK)
    body += rect(x + 216, y, 632, h, fill=HIGH, stroke=INK)
    body += pane_head(x + 216, y, 632, "Document")
    body += para(x + 238, y + 56, 588, "The document takes the remaining width. It is the only pane that may grow without limit.", size=11, leading=16)
    body += rect(x + 848, y, 240, h, fill=PAPER, stroke=INK)
    body += pane_head(x + 848, y, 240, "Inspector")
    body += para(x + 862, y + 56, 212, "Identity, presentation, state and capabilities for the selection.", size=11, leading=16)
    for px, label in [(x + 105, "210 min"), (x + 532, "flexible · ≥ 420"), (x + 968, "240 min")]:
        body += txt(px, y + h + 22, label, size=10, fill=SOFT, family=F_MONO, anchor="middle")
    body += line(x, y + h + 8, x + 210, y + h + 8, stroke=LINE)
    body += line(x + 216, y + h + 8, x + 848, y + h + 8, stroke=LINE)
    body += line(x + 848, y + h + 8, x + 1088, y + h + 8, stroke=LINE)
    # Splitter detail.
    body += txt(64, 596, "SPLITTER", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    body += rect(64, 620, 6, 80, fill=LINE, stroke=INK)
    body += line(70, 620, 250, 620, stroke=LINE, dash="2 4")
    body += line(70, 700, 250, 700, stroke=LINE, dash="2 4")
    body += txt(270, 640, "6 px visible rule, 8 px hit area", size=11, fill=SOFT)
    body += txt(270, 662, "Double-click restores the default", size=11, fill=SOFT)
    body += txt(270, 684, "Drag is immediate; no preview pane", size=11, fill=SOFT)
    # Collapsed pane.
    body += txt(620, 596, "COLLAPSED", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    body += rect(620, 620, 42, 120, fill=PAPER, stroke=INK)
    body += txt(641, 660, "Inspector", size=10, fill=SOFT, anchor="middle", family=F_MONO)
    body += path("M 632 740 L 650 740 M 641 732 L 641 748", stroke=INK, sw=1.5)
    body += txt(680, 646, "A collapsed pane keeps its head and handle.", size=11, fill=SOFT)
    body += txt(680, 668, "Its state is remembered per project.", size=11, fill=SOFT)
    body += txt(680, 690, "It never reopens at a new width.", size=11, fill=SOFT)
    body += para(64, 744, 1072, "Two panes beside a document is the practical limit. A third pane becomes a tab or a separate window. Nested splitters are allowed only when each level keeps a named head.", size=11, leading=16)
    return svg_doc(1200, 800, "Pane layout with minimum widths and splitters", "Navigator, document and inspector panes with minimum widths, a splitter detail and a collapsed pane.", body)


def fig_inspector() -> str:
    body = title_block(64, 70, "The inspector explains the object", "Identity, presentation, state and authority, in that order. The inspector describes; it does not become a second application.")
    x, y, w, h = 64, 160, 420, 580
    body += rect(x + 6, y + 6, w, h, fill="#17201C18", stroke=None)
    body += rect(x, y, w, h, fill=PAPER, stroke=INK)
    body += pane_head(x, y, w, "Inspector", "object")
    ix, iw = x + 16, w - 32
    body += txt(ix, y + 52, "Generation mix", size=18, family=F_DISPLAY, style="italic")
    body += txt(ix, y + 72, "Table · obj:8f3a", size=11, fill=SOFT, family=F_MONO)
    state_body, _ = state_chip(x + w - 110, y + 38, "Current")
    body += state_body
    body += txt(ix, y + 106, "IDENTITY", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.7)
    body += inspector_row(ix, y + 130, iw, "Object", "obj:8f3a")
    body += inspector_row(ix, y + 154, iw, "Provider", "enfilade.table")
    body += inspector_row(ix, y + 178, iw, "Revision", "r17")
    body += inspector_row(ix, y + 202, iw, "Parent", "note:transition")
    body += txt(ix, y + 238, "PRESENTATION", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.7)
    for index, (name, detail) in enumerate([("In note", "12 rows · 4 columns"), ("Dataframe", "focused editor"), ("Print", "facing page")]):
        ry = y + 262 + index * 34
        body += radio(ix, ry, name, index == 0)
        body += txt(ix + 110, ry, detail, size=11, fill=SOFT, family=F_MONO)
    body += txt(ix, y + 356, "STATE", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.7)
    state_body, _ = state_chip(ix, y + 368, "Current")
    body += state_body
    body += txt(ix, y + 406, "Last refresh", size=11, fill=INK)
    body += txt(ix + iw, y + 406, "14:02", size=11, fill=SOFT, anchor="end", family=F_MONO)
    body += line(ix, y + 424, ix + iw, y + 424, stroke=LINE)
    body += txt(ix, y + 444, "AUTHORITY", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.7)
    body += txt(ix, y + 468, "Read", size=11, fill=INK)
    body += txt(ix + iw, y + 468, "granted", size=11, fill=PINE2, anchor="end", family=F_MONO)
    body += txt(ix, y + 490, "Write", size=11, fill=INK)
    body += txt(ix + iw, y + 490, "granted", size=11, fill=PINE2, anchor="end", family=F_MONO)
    body += txt(ix, y + 512, "Share", size=11, fill=INK)
    body += txt(ix + iw, y + 512, "denied", size=11, fill=OXIDE, anchor="end", family=F_MONO)
    body += line(ix, y + 530, ix + iw, y + 530, stroke=LINE)
    body += txt(ix, y + 552, "The last value is kept while the source is refreshed.", size=11, fill=SOFT)
    # Annotations.
    ax = 540
    body += txt(ax, 190, "WHAT BELONGS", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    body += lines(
        ax,
        222,
        [
            "Stable identity and revision.",
            "Every presentation of the object.",
            "The state of each live relationship.",
            "The grants that allow an action.",
            "The provider that owns the data.",
        ],
        size=11,
        leading=28,
        fill=SOFT,
    )
    body += txt(ax, 402, "WHAT DOES NOT", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    body += lines(
        ax,
        434,
        [
            "A second copy of the document.",
            "Raw provider diagnostics as primary text.",
            "A place to edit every property at once.",
            "A marketing surface for unused features.",
        ],
        size=11,
        leading=28,
        fill=SOFT,
    )
    body += line(ax, 580, 1136, 580, stroke=LINE)
    body += para(ax, 606, 596, "The inspector is read-mostly by default. Editing a property happens in the document or in the focused editor, through a transaction. The inspector may offer the same command, but it does not invent a parallel editing model.", size=12, leading=19)
    return svg_doc(1200, 760, "Object inspector", "An inspector panel listing identity, presentation, authority and state, with notes on what belongs and what does not.", body)


def fig_controls() -> str:
    body = title_block(64, 70, "Controls are direct", "A control looks like what it does. It has one job, one label and a target a hand can find.")
    # Buttons.
    body += txt(64, 158, "BUTTONS", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    body += button(64, 174, 124, "Cancel")
    body += button(200, 174, 140, "Save note", primary=True)
    body += button(352, 174, 132, "Delete", destructive=True)
    body += button(496, 174, 124, "Unavailable", disabled=True)
    # Fields.
    body += txt(64, 254, "FIELDS", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    body += field(64, 278, 300, "North Sea transition", label="Title")
    body += field(64, 342, 300, "enfilade.table", label="Provider", focus=True)
    body += txt(64, 404, "The provider is chosen by the object, not typed by the user.", size=10, fill=SOFT)
    # Choice.
    body += txt(64, 458, "CHOICE", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    body += checkbox(64, 484, "Show grid", True)
    body += checkbox(64, 512, "Snap to guides", True)
    body += checkbox(64, 540, "Show rulers", False)
    body += radio(260, 484, "Current value", True)
    body += radio(260, 512, "Last saved value", False)
    body += radio(260, 540, "Both, side by side", False)
    # Slider and tabs.
    body += txt(500, 458, "RANGE AND TABS", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    body += txt(500, 484, "Stroke", size=11, fill=INK)
    body += line(560, 494, 780, 494, stroke=LINE, sw=4)
    body += line(560, 494, 668, 494, stroke=PINE2, sw=4)
    body += circle(668, 494, 8, fill=HIGH, stroke=PINE2, sw=2)
    body += txt(796, 498, "2 px", size=11, fill=SOFT, family=F_MONO)
    for index, (name, active) in enumerate([("Note", True), ("Table", False), ("Diagram", False)]):
        tx = 500 + index * 100
        body += rect(tx, 526, 100, 32, fill=HIGH, stroke=LINE)
        body += txt(tx + 50, 547, name, size=11, fill=INK if active else SOFT, anchor="middle")
        if active:
            body += line(tx, 557, tx + 100, 557, stroke=OXIDE, sw=3)
    body += para(500, 586, 360, "A slider shows its value and its unit. A tab names a view, never a verb. A checkbox is a state; a button is an action.", size=11, leading=17)
    # Targets.
    body += line(64, 600, 1136, 600, stroke=LINE)
    body += txt(64, 630, "TARGETS AND SPACING", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    body += rect(64, 650, 28, 28, fill=HIGH, stroke=INK)
    body += rect(100, 650, 28, 28, fill=HIGH, stroke=INK)
    body += line(92, 686, 100, 686, stroke=OXIDE, sw=1, dash="3 3")
    body += txt(96, 700, "8", size=9, fill=OXIDE, family=F_MONO, anchor="middle")
    body += rect(144, 646, 32, 32, fill=HIGH, stroke=INK)
    body += rect(188, 644, 36, 36, fill=HIGH, stroke=INK)
    body += txt(64, 712, "28 minimum · 32 preferred · 36 primary", size=10, fill=SOFT, family=F_MONO)
    body += para(440, 640, 700, "Labels sit above fields and beside choices. Units and shortcuts use the metadata voice. A control that needs a paragraph of explanation needs a different control.", size=11, leading=17)
    return svg_doc(1200, 760, "Control gallery", "Buttons, fields, checkboxes, radio buttons, a slider, tabs and target-size examples.", body)


def fig_dialog() -> str:
    body = title_block(64, 70, "Dialogs interrupt with a reason", "A dialog asks one question, names the object and offers a way out. It is not a place to arrange the application.")
    # Background.
    body += rect(64, 150, 1072, 540, fill=PAPER, stroke=LINE)
    body += rect(64, 150, 1072, 540, fill=INK, stroke=None, opacity=0.18)
    body += txt(90, 184, "Document (inert while the dialog is open)", size=11, fill=WHITE)
    # Dialog.
    x, y, w, h = 330, 210, 540, 340
    body += rect(x + 8, y + 8, w, h, fill="#17201C30", stroke=None)
    body += rect(x, y, w, h, fill=HIGH, stroke=INK)
    body += titlebar(x, y, w, "Replace the embedded table?")
    body += para(x + 24, y + 62, w - 48, "The note currently embeds “Generation mix” as a live table. Replacing it will remove the embed, not delete the table object.", size=12, leading=19)
    body += rect(x + 24, y + 130, w - 48, 52, fill=PAPER, stroke=LINE)
    body += txt(x + 38, y + 152, "Generation mix", size=12, weight="bold")
    body += txt(x + 38, y + 170, "Table · r17 · obj:8f3a", size=10, fill=SOFT, family=F_MONO)
    body += checkbox(x + 24, y + 214, "Keep a copy in this note", False)
    body += txt(x + 24, y + 244, "This cannot be undone after the note is saved.", size=10, fill=OXIDE)
    body += button(x + w - 300, y + h - 64, 120, "Cancel", height=36)
    body += button(x + w - 164, y + h - 64, 140, "Replace", destructive=True, height=36)
    # Focus ring on Cancel.
    body += rect(x + w - 306, y + h - 70, 132, 48, fill="none", stroke=OXIDE, sw=3)
    body += txt(x + w - 300, y + h - 82, "default focus", size=10, fill=OXIDE, family=F_MONO)
    # Annotations.
    nx = 64
    body += txt(nx, 726, "One question per dialog. The destructive verb names the object. Cancel is the default for destruction. Esc cancels. No dialog opens another dialog.", size=11, fill=SOFT)
    return svg_doc(1200, 760, "Destructive confirmation dialog", "A modal dialog asking whether to replace an embedded table, with object identity, a keep-a-copy choice and a destructive Replace button.", body)


def fig_focus() -> str:
    body = title_block(64, 70, "Focus is a place you can see", "The keyboard reaches everything. The focus ring is never removed to make a screenshot look calmer.")
    # Focus ring anatomy.
    body += txt(64, 158, "FOCUS RING", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    body += rect(64, 180, 260, 150, fill=HIGH, stroke=LINE)
    body += button(96, 222, 150, "Open source", primary=True)
    body += rect(93, 219, 156, 38, fill="none", stroke=OXIDE, sw=3)
    body += line(252, 200, 286, 200, stroke=OXIDE)
    body += txt(292, 204, "3 px oxide", size=10, fill=OXIDE, family=F_MONO)
    body += line(252, 238, 286, 238, stroke=OXIDE)
    body += txt(292, 242, "3 px offset", size=10, fill=OXIDE, family=F_MONO)
    body += txt(64, 360, "Only the focused control carries the ring.", size=10, fill=SOFT)
    # Tab order.
    body += txt(420, 158, "TAB ORDER", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
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
        body += txt(434, sy, number, size=10, fill=WHITE, anchor="middle", family=F_MONO, weight="bold")
        body += txt(458, sy, label, size=12, fill=INK)
        if index < len(steps) - 1:
            body += line(434, sy + 8, 434, sy + 20, stroke=LINE)
    # Key table.
    body += txt(64, 430, "KEYS THAT MUST WORK", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
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
    body += para(780, 186, 356, "Focus moves in reading order. A composite control is one stop; arrows move inside it. The ring is drawn outside the control so it never changes the layout.", size=11, leading=18)
    body += para(780, 300, 356, "Shortcuts are labels, not secrets. Every shortcut appears beside its command in a menu and is searchable in the command palette.", size=11, leading=18)
    body += para(780, 414, 356, "A window that loses focus keeps a muted focus memory. When it returns, the last focused control receives the ring again.", size=11, leading=18)
    body += txt(780, 540, "Never trap focus except in a modal dialog.", size=12, fill=OXIDE, family=F_DISPLAY, style="italic")
    return svg_doc(1200, 760, "Focus ring, tab order and keyboard map", "A focus ring measured at three pixels with a three pixel offset, a tab order for a document window, and the essential keyboard commands.", body)


def fig_command_palette() -> str:
    body = title_block(64, 70, "The command palette is a second door", "It finds commands, objects and tools by name. It does not replace the menu bar or the document.")
    body += rect(64, 150, 1072, 540, fill=PAPER, stroke=LINE)
    body += rect(64, 150, 1072, 540, fill=INK, stroke=None, opacity=0.14)
    x, y, w, h = 300, 180, 600, 420
    body += rect(x + 8, y + 8, w, h, fill="#17201C30", stroke=None)
    body += rect(x, y, w, h, fill=HIGH, stroke=INK)
    body += field(x + 18, y + 18, w - 36, "curr", height=40, focus=True)
    body += txt(x + w - 28, y + 43, "Esc", size=10, fill=SOFT, family=F_MONO, anchor="end")
    # Groups.
    groups = [
        ("OBJECTS", [("Currency — GBP · obj:4c21", "note:transition"), ("Currency table — 12 rows", "obj:8f3a")]),
        ("COMMANDS", [("Insert currency object", "Ctrl+Shift+C"), ("Refresh live values", "F5"), ("Open inspector", "Ctrl+I")]),
    ]
    row_y = y + 78
    selected_row = 3
    row_index = 0
    for group, rows in groups:
        body += txt(x + 22, row_y, group, size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.8)
        row_y += 20
        for label, detail in rows:
            if row_index == selected_row:
                body += rect(x + 12, row_y - 16, w - 24, 34, fill=PINE2, stroke=None)
                colour = WHITE
            else:
                colour = INK
            body += txt(x + 24, row_y + 6, label, size=12, fill=colour)
            body += txt(x + w - 24, row_y + 6, detail, size=10, fill=WHITE if row_index == selected_row else SOFT, family=F_MONO, anchor="end")
            row_y += 38
            row_index += 1
        row_y += 6
    body += line(x, y + h - 36, x + w, y + h - 36, stroke=LINE)
    body += txt(x + 20, y + h - 14, "Enter run   ·   Tab next group   ·   Esc close", size=10, fill=SOFT, family=F_MONO)
    # Notes.
    nx = 64
    body += txt(nx, 726, "Results are grouped by kind. Objects carry identity; commands carry shortcuts; tools appear only when the current selection makes them applicable.", size=11, fill=SOFT)
    return svg_doc(1200, 760, "Command palette over a document", "A command palette with a search field, grouped object and command results, a selected row and keyboard hints.", body)


def fig_notes() -> str:
    body = title_block(64, 70, "Facet Notes", "The document is the workspace. Prose, tables and diagrams share one page without becoming one file format.")
    x, y, w, h = 64, 150, 1072, 540
    body += window_shell(x, y, w, h, "Facet Notes — North Sea transition", ["File", "Edit", "View", "Object", "Tools", "Window", "Help"], status="Saved · 3 embeds · 1 stale relationship", state="Stale")
    tree_w, back_w = 210, 220
    body += rect(x, y + 60, tree_w, h - 86, fill=PAPER, stroke=None)
    body += pane_head(x, y + 60, tree_w, "Notes", "+")
    rows = [("Project", 0, False), ("North Sea transition", 1, True), ("Sources", 1, False), ("Generation mix", 2, False), ("Currency", 2, False), ("Figures", 1, False), ("Archive", 0, False)]
    for index, (name, depth, selected) in enumerate(rows):
        ry = y + 92 + index * 28
        if selected:
            body += rect(x, ry - 18, tree_w, 26, fill=PINE2, stroke=None)
        body += txt(x + 12 + depth * 14, ry, name, size=11, fill=WHITE if selected else INK)
    body += line(x + tree_w, y + 60, x + tree_w, y + h - 26, stroke=INK)
    body += line(x + w - back_w, y + 60, x + w - back_w, y + h - 26, stroke=INK)
    ex = x + tree_w + 22
    ew = w - tree_w - back_w - 44
    body += txt(ex, y + 98, "North Sea transition", size=24, family=F_DISPLAY, style="italic")
    body += txt(ex, y + 120, "Updated 14:02 · 1,240 words · 3 embeds", size=10, fill=SOFT, family=F_MONO)
    body += para(ex, y + 152, ew, "The transition is not one decision but a sequence of small ones. Each source below stays editable, and each object keeps its own identity when the note is renamed or moved.", size=12, leading=19)
    # Embed 1.
    body += rect(ex, y + 224, ew, 86, fill=HIGH, stroke=LINE)
    body += rect(ex, y + 224, 4, 86, fill=PINE2, stroke=None)
    body += txt(ex + 16, y + 250, "Generation mix", size=12, weight="bold")
    body += txt(ex + 16, y + 268, "Table · 12 rows · 4 columns · obj:8f3a", size=10, fill=SOFT, family=F_MONO)
    state_body, _ = state_chip(ex + ew - 104, y + 242, "Current")
    body += state_body
    for col in range(4):
        for row in range(2):
            body += rect(ex + 16 + col * 92, y + 282 + row * 14, 88, 11, fill=PAPER, stroke=LINE, sw=0.5)
    # Embed 2.
    body += rect(ex, y + 328, ew, 86, fill=HIGH, stroke=LINE)
    body += rect(ex, y + 328, 4, 86, fill=AMBER, stroke=None)
    body += txt(ex + 16, y + 354, "Transition pathways", size=12, weight="bold")
    body += txt(ex + 16, y + 372, "Diagram · Mermaid source · obj:1b90", size=10, fill=SOFT, family=F_MONO)
    state_body, _ = state_chip(ex + ew - 104, y + 346, "Stale")
    body += state_body
    body += circle(ex + 44, y + 398, 10, fill=PINE2, stroke=None)
    body += line(ex + 54, y + 398, ex + 96, y + 398, stroke=INK)
    body += circle(ex + 106, y + 398, 10, fill=HIGH, stroke=OXIDE, sw=2)
    body += line(ex + 116, y + 398, ex + 158, y + 398, stroke=INK)
    body += circle(ex + 168, y + 398, 10, fill=HIGH, stroke=PINE2, sw=2)
    # Embed 3.
    body += rect(ex, y + 432, ew, 74, fill=HIGH, stroke=LINE)
    body += rect(ex, y + 432, 4, 74, fill=TEAL, stroke=None)
    body += txt(ex + 16, y + 458, "North Sea currency", size=12, weight="bold")
    body += txt(ex + 16, y + 476, "Currency · GBP · last read 14:02", size=10, fill=SOFT, family=F_MONO)
    state_body, _ = state_chip(ex + ew - 104, y + 450, "Refreshing")
    body += state_body
    # Backlinks.
    bx = x + w - back_w
    body += pane_head(bx, y + 60, back_w, "Relations")
    body += txt(bx + 14, y + 108, "LINKED FROM", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.6)
    body += txt(bx + 14, y + 132, "Projects / 2026", size=11, fill=INK)
    body += txt(bx + 14, y + 152, "Reading list", size=11, fill=INK)
    body += txt(bx + 14, y + 190, "LINKS TO", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.6)
    body += txt(bx + 14, y + 214, "Generation mix", size=11, fill=INK)
    body += txt(bx + 14, y + 234, "Transition pathways", size=11, fill=INK)
    body += txt(bx + 14, y + 254, "Currency · GBP", size=11, fill=INK)
    body += line(bx + 14, y + 284, bx + back_w - 14, y + 284, stroke=LINE)
    body += para(bx + 14, y + 310, back_w - 28, "A link survives renames and moves. It records the object, not a file path.", size=11, leading=17)
    body += txt(bx + 14, y + 400, "No convert-to-text command.", size=11, fill=OXIDE, family=F_DISPLAY, style="italic")
    return svg_doc(1200, 760, "Facet Notes with a note tree and live embeds", "A note editor with a project tree, three embedded objects in different states, and a relations panel.", body)


def fig_draw() -> str:
    body = title_block(64, 70, "Burin Draw", "A drawing surface with rulers, guides and a compact tool palette. The canvas is the document, not a preview of one.")
    x, y, w, h = 64, 150, 1072, 540
    body += window_shell(x, y, w, h, "Burin Draw — Currency plate", ["File", "Edit", "View", "Object", "Tools", "Window", "Help"], status="Pen · 2 px · 14 objects · 100%", state="Current")
    palette_w = 48
    body += rect(x, y + 60, palette_w, h - 86, fill=PAPER, stroke=None)
    body += line(x + palette_w, y + 60, x + palette_w, y + h - 26, stroke=INK)
    tools = ["select", "pen", "line", "rect", "ellipse", "text", "hand"]
    for index, glyph in enumerate(tools):
        bx, by = x + 8, y + 72 + index * 40
        active = index == 1
        body += rect(bx, by, 32, 32, fill=PINE2 if active else HIGH, stroke=LINE)
        colour = WHITE if active else INK
        cx, cy = bx + 16, by + 16
        if glyph == "select":
            body += path(f"M {cx - 6} {cy - 8} L {cx + 4} {cy + 5} L {cx - 1} {cy + 5} L {cx + 1} {cy + 11} L {cx - 3} {cy + 12} L {cx - 5} {cy + 6} L {cx - 9} {cy + 9} Z", stroke=colour, sw=1.5)
        elif glyph == "pen":
            body += path(f"M {cx - 7} {cy + 8} L {cx - 5} {cy} L {cx + 5} {cy - 10} L {cx + 9} {cy - 6} L {cx} {cy + 4} Z", stroke=colour, sw=1.5)
        elif glyph == "line":
            body += line(cx - 7, cy + 7, cx + 7, cy - 7, stroke=colour, sw=2)
        elif glyph == "rect":
            body += rect(cx - 8, cy - 6, 16, 12, fill="none", stroke=colour, sw=1.5)
        elif glyph == "ellipse":
            body += ellipse(cx, cy, 9, 7, fill="none", stroke=colour, sw=1.5)
        elif glyph == "text":
            body += txt(cx, cy + 6, "T", size=15, fill=colour, weight="bold", anchor="middle")
        else:
            body += path(f"M {cx - 6} {cy + 6} V {cy - 8} M {cx - 2} {cy + 6} V {cy - 8} M {cx + 2} {cy + 6} V {cy - 8} M {cx + 6} {cy + 6} V {cy - 8}", stroke=colour, sw=1.4)
    # Canvas.
    cx0, cy0 = x + palette_w + 28, y + 92
    cw, ch = 736, 414
    body += rect(cx0, cy0, cw, ch, fill=WHITE, stroke=INK)
    for index in range(0, cw, 50):
        body += line(cx0 + index, cy0 - 20, cx0 + index, cy0, stroke=LINE)
        body += txt(cx0 + index, cy0 - 26, str(index), size=9, fill=SOFT, family=F_MONO, anchor="middle")
    for index in range(0, ch, 50):
        body += line(cx0 - 20, cy0 + index, cx0, cy0 + index, stroke=LINE)
        body += txt(cx0 - 24, cy0 + index + 3, str(index), size=9, fill=SOFT, family=F_MONO, anchor="end")
    for gx in (cx0 + 150, cx0 + 400):
        body += line(gx, cy0, gx, cy0 + ch, stroke=TEAL, sw=1, dash="4 5")
    for gy in (cy0 + 120, cy0 + 360):
        body += line(cx0, gy, cx0 + cw, gy, stroke=TEAL, sw=1, dash="4 5")
    # Figure.
    body += rect(cx0 + 150, cy0 + 120, 250, 240, fill="none", stroke=INK, sw=1.5)
    body += ellipse(cx0 + 275, cy0 + 240, 80, 54, fill=HIGH, stroke=PINE2, sw=2)
    body += txt(cx0 + 275, cy0 + 246, "GBP", size=18, fill=PINE2, family=F_MONO, weight="bold", anchor="middle")
    body += path(f"M {cx0 + 150} {cy0 + 340} C {cx0 + 220} {cy0 + 260}, {cx0 + 330} {cy0 + 420}, {cx0 + 400} {cy0 + 300}", stroke=OXIDE, sw=2)
    # Selection handles.
    for hx, hy in [(cx0 + 150, cy0 + 120), (cx0 + 400, cy0 + 120), (cx0 + 150, cy0 + 360), (cx0 + 400, cy0 + 360)]:
        body += rect(hx - 4, hy - 4, 8, 8, fill=WHITE, stroke=OXIDE)
    # Inspector.
    ix = cx0 + cw + 20
    body += pane_head(ix, y + 60, w - (ix - x), "Inspector")
    body += txt(ix + 10, y + 108, "Currency plate", size=12, weight="bold")
    body += txt(ix + 10, y + 124, "Group · 14 objects", size=10, fill=SOFT, family=F_MONO)
    body += inspector_row(ix + 10, y + 152, 220, "Size", "240 × 180 mm")
    body += inspector_row(ix + 10, y + 176, 220, "Position", "24, 42 mm")
    body += inspector_row(ix + 10, y + 200, 220, "Rotation", "0°")
    body += txt(ix + 10, y + 232, "FILL", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.6)
    body += rect(ix + 10, y + 244, 24, 24, fill=HIGH, stroke=INK)
    body += txt(ix + 42, y + 261, "Paper", size=11, fill=INK)
    body += txt(ix + 10, y + 288, "STROKE", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.6)
    body += rect(ix + 10, y + 300, 24, 24, fill=INK, stroke=INK)
    body += txt(ix + 42, y + 317, "Ink · 2 px", size=11, fill=INK)
    body += txt(ix + 10, y + 350, "GUIDES", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.6)
    body += checkbox(ix + 10, y + 374, "Show guides", True)
    body += checkbox(ix + 10, y + 398, "Snap to grid", True)
    body += txt(ix + 10, y + 430, "Grid 16 px · guides teal", size=10, fill=SOFT, family=F_MONO)
    return svg_doc(1200, 760, "Burin Draw with rulers, guides and tool palette", "A drawing window with a 48 pixel tool palette, rulers, teal guides, an object with selection handles, and an inspector.", body)


def fig_press() -> str:
    body = title_block(64, 70, "Cabochon Press", "A page is a surface with intent. Press shows the page, its pages panel and its preflight in one window.")
    x, y, w, h = 64, 150, 1072, 540
    body += window_shell(x, y, w, h, "Cabochon Press — Currency brief", ["File", "Edit", "View", "Page", "Object", "Window", "Help"], status="Page 2 of 6 · PDF/X-4 · 3 mm bleed", state="Current")
    pages_w = 150
    body += rect(x, y + 60, pages_w, h - 86, fill=PAPER, stroke=None)
    body += pane_head(x, y + 60, pages_w, "Pages", "+")
    for index in range(6):
        py = y + 98 + index * 64
        body += rect(x + 14, py, 52, 44, fill=WHITE, stroke=OXIDE if index == 1 else LINE, sw=2 if index == 1 else 1)
        body += txt(x + 78, py + 18, f"0{index + 1}", size=10, fill=INK, family=F_MONO)
        body += txt(x + 78, py + 34, "A4" if index < 4 else "Plate", size=9, fill=SOFT, family=F_MONO)
    body += line(x + pages_w, y + 60, x + pages_w, y + h - 26, stroke=INK)
    # Page.
    px, py, pw, ph = x + pages_w + 60, y + 82, 430, 384
    body += rect(px + 14, py + 14, pw, ph, fill="#17201C18", stroke=None)
    body += rect(px, py, pw, ph, fill=WHITE, stroke=INK)
    body += txt(px + 32, py + 62, "A currency for the", size=26, family=F_DISPLAY, style="italic")
    body += txt(px + 32, py + 94, "North Sea transition", size=26, family=F_DISPLAY, style="italic")
    body += line(px + 32, py + 116, px + pw - 32, py + 116, stroke=INK)
    body += para(px + 32, py + 146, pw - 64, "A short brief for the first Cabochon currency object, with its sources and its print presentation.", size=11, leading=16)
    body += rect(px + 32, py + 220, pw - 64, 120, fill=PAPER, stroke=LINE)
    body += txt(px + 46, py + 246, "GBP · 1.00", size=20, fill=PINE2, family=F_MONO, weight="bold")
    body += txt(px + 46, py + 268, "Source · European Central Bank", size=10, fill=SOFT, family=F_MONO)
    for row in range(4):
        body += line(px + 46, py + 286 + row * 12, px + pw - 46, py + 286 + row * 12, stroke=LINE, sw=0.5)
    # Crop marks and bleed.
    for cx1, cy1, cx2, cy2 in [(px - 18, py, px - 6, py), (px, py - 18, px, py - 6), (px + pw + 6, py, px + pw + 18, py), (px, py + ph + 6, px, py + ph + 18)]:
        body += line(cx1, cy1, cx2, cy2, stroke=INK, sw=0.8)
    body += line(px - 12, py - 12, px + pw + 12, py - 12, stroke=TEAL, dash="3 4")
    body += line(px - 12, py + ph + 12, px + pw + 12, py + ph + 12, stroke=TEAL, dash="3 4")
    body += txt(px + pw + 20, py + ph + 16, "bleed 3 mm", size=9, fill=TEAL_INK, family=F_MONO)
    # Preflight.
    ix = x + w - 300
    body += rect(ix, y + 60, 300, h - 86, fill=PAPER, stroke=None)
    body += line(ix, y + 60, ix, y + h - 26, stroke=INK)
    body += pane_head(ix, y + 60, 300, "Preflight")
    checks = [("Fonts embedded", True), ("Images at 300 dpi", True), ("Colour intent PDF/X-4", True), ("Bleed 3 mm", True), ("Live object will flatten", False)]
    for index, (label, ok) in enumerate(checks):
        cy = y + 116 + index * 40
        body += txt(ix + 16, cy, "✓" if ok else "!", size=14, fill=PINE2 if ok else AMBER_INK, weight="bold")
        body += txt(ix + 38, cy, label, size=11, fill=INK if ok else AMBER_INK)
        body += line(ix + 16, cy + 14, ix + 284, cy + 14, stroke=LINE, sw=0.5)
    body += para(ix + 16, y + 340, 268, "A live object prints through its print presentation. Press reports the resolution and intent it will use, and never silently exports the screen view.", size=11, leading=17)
    body += button(ix + 16, y + 438, 124, "Proof", height=32)
    body += button(ix + 152, y + 438, 132, "Export PDF", primary=True, height=32)
    return svg_doc(1200, 760, "Cabochon Press with pages and preflight", "A page-layout window with a pages panel, an A4 page with bleed and crop marks, and a preflight panel checking fonts, images, colour and bleed.", body)


def fig_table() -> str:
    body = title_block(64, 70, "Enfilade Table", "Typed cells, a visible formula bar and a selection that states its own extent. The grid is an editor, not a spreadsheet costume.")
    x, y, w, h = 64, 150, 1072, 540
    body += window_shell(x, y, w, h, "Enfilade Table — Generation mix", ["File", "Edit", "View", "Data", "Object", "Window", "Help"], status="Sum 1,284 GWh · 12 rows · 4 columns", state="Current")
    cat_w = 210
    body += rect(x, y + 60, cat_w, h - 86, fill=PAPER, stroke=None)
    body += pane_head(x, y + 60, cat_w, "Categories")
    cats = [("All rows", 12), ("Wind", 5), ("Solar", 3), ("Hydro", 2), ("Imported", 2)]
    for index, (name, count) in enumerate(cats):
        cy = y + 100 + index * 32
        if index == 0:
            body += rect(x, cy - 18, cat_w, 28, fill=PINE2, stroke=None)
        body += txt(x + 14, cy, name, size=11, fill=WHITE if index == 0 else INK)
        body += txt(x + cat_w - 14, cy, str(count), size=10, fill=WHITE if index == 0 else SOFT, family=F_MONO, anchor="end")
    body += line(x + cat_w, y + 60, x + cat_w, y + h - 26, stroke=INK)
    # Formula bar.
    fx = x + cat_w
    body += rect(fx, y + 60, w - cat_w, 34, fill=PAPER, stroke=None)
    body += line(fx, y + 94, x + w, y + 94, stroke=LINE)
    body += txt(fx + 12, y + 82, "fx", size=12, fill=SOFT, family=F_MONO, weight="bold")
    body += rect(fx + 36, y + 66, w - cat_w - 48, 22, fill=WHITE, stroke=LINE)
    body += txt(fx + 48, y + 81, "11,040", size=11, fill=INK, family=F_MONO)
    # Grid.
    gx, gy = fx + 12, y + 104
    cols = ["Source", "Capacity", "Output", "Share"]
    widths = [228, 130, 130, 110]
    for c, (name, cw) in enumerate(zip(cols, widths)):
        cx = gx + sum(widths[:c])
        body += rect(cx, gy, cw, 30, fill=PAPER, stroke=LINE)
        if c == 0:
            body += txt(cx + 10, gy + 20, name, size=11, fill=SOFT, weight="bold", family=F_MONO, spacing=0.5)
        else:
            body += txt(cx + cw - 10, gy + 20, name, size=11, fill=SOFT, weight="bold", family=F_MONO, spacing=0.5, anchor="end")
    data = [
        ("Wind · Dogger Bank", "3.6 GW", "14,210", "38%"),
        ("Wind · Hornsea", "2.8 GW", "11,040", "29%"),
        ("Solar · East Anglia", "1.2 GW", "2,180", "6%"),
        ("Hydro · Norway", "0.8 GW", "4,320", "11%"),
        ("Imported · France", "2.0 GW", "6,090", "16%"),
    ]
    for r, row in enumerate(data):
        for c, (value, cw) in enumerate(zip(row, widths)):
            cxx = gx + sum(widths[:c])
            cyy = gy + 30 + r * 34
            selected = r == 1 and c == 2
            fill = PINE2 if selected else (HIGH if r % 2 == 0 else WHITE)
            body += rect(cxx, cyy, cw, 34, fill=fill, stroke=LINE)
            if c == 0:
                body += txt(cxx + 12, cyy + 22, value, size=11, fill=WHITE if selected else INK)
            else:
                body += txt(cxx + cw - 12, cyy + 22, value, size=11, fill=WHITE if selected else INK, family=F_MONO, anchor="end")
    # Active cell caret and selection range outline.
    range_x = gx + widths[0]
    range_y = gy + 30
    active_x = range_x + widths[1]
    active_y = range_y + 34
    body += line(active_x + 7, active_y + 8, active_x + 7, active_y + 26, stroke=WHITE, sw=1)
    body += rect(range_x, range_y, widths[1] + widths[2], 68, fill="none", stroke=OXIDE, sw=2)
    # Cell inspector.
    ix = x + w - 240
    body += rect(ix, y + 60, 240, h - 86, fill=PAPER, stroke=None)
    body += line(ix, y + 60, ix, y + h - 26, stroke=INK)
    body += pane_head(ix, y + 60, 240, "Cell")
    body += inspector_row(ix + 14, y + 110, 212, "Address", "C3")
    body += inspector_row(ix + 14, y + 134, 212, "Type", "number · GWh")
    body += inspector_row(ix + 14, y + 158, 212, "Value", "11,040")
    body += inspector_row(ix + 14, y + 182, 212, "Format", "0,000")
    body += txt(ix + 14, y + 216, "VALIDATION", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.6)
    body += txt(ix + 14, y + 240, "Number, 0–99,999", size=11, fill=INK)
    body += txt(ix + 14, y + 262, "No empty cells in this column", size=11, fill=INK)
    body += txt(ix + 14, y + 302, "SELECTION", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.6)
    body += txt(ix + 14, y + 326, "B2:C3 · 4 cells", size=11, fill=INK, family=F_MONO)
    body += txt(ix + 14, y + 348, "2 numeric · 2 text", size=10, fill=SOFT, family=F_MONO)
    body += txt(ix + 14, y + 370, "Sum 25,250 GWh", size=11, fill=PINE2, family=F_MONO)
    body += txt(ix + 14, y + 392, "Average 12,625 GWh", size=11, fill=PINE2, family=F_MONO)
    body += para(ix + 14, y + 424, 212, "A typed value stays a number. The displayed format never becomes the stored value.", size=10, leading=16)
    return svg_doc(1200, 760, "Enfilade Table with categories, grid and cell inspector", "A data table with category filters, a formula bar, typed numeric cells, a selected range and a cell inspector.", body)


def fig_formula() -> str:
    body = title_block(64, 70, "The formula tool at the point of use", "A tool appears beside the selection it can act on. It shows its sources, its authority and its result without taking over the document.")
    # Document.
    body += rect(64, 150, 760, 540, fill=HIGH, stroke=INK)
    body += titlebar(64, 150, 760, "Facet Notes — Generation mix")
    body += txt(92, 210, "Generation mix", size=22, family=F_DISPLAY, style="italic")
    body += para(92, 238, 700, "The table is selected. A compatible tool is offered beside it rather than in a global services menu.", size=11, leading=16)
    # Table with selected cells.
    for r in range(4):
        for c in range(4):
            body += rect(92 + c * 150, 286 + r * 34, 150, 34, fill=PINE2 if (r == 1 and c == 2) else WHITE, stroke=LINE)
    body += rect(92 + 150, 286 + 34, 300, 34, fill="none", stroke=OXIDE, sw=2)
    body += txt(104, 310, "Source", size=10, fill=SOFT, family=F_MONO)
    body += txt(254, 310, "Capacity", size=10, fill=SOFT, family=F_MONO)
    body += txt(404, 310, "Output", size=10, fill=SOFT, family=F_MONO)
    body += txt(554, 310, "Share", size=10, fill=SOFT, family=F_MONO)
    # Formula popover.
    x, y, w, h = 470, 340, 430, 300
    body += rect(x + 8, y + 8, w, h, fill="#17201C30", stroke=None)
    body += rect(x, y, w, h, fill=HIGH, stroke=INK)
    body += txt(x + 18, y + 28, "FORMULA", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.8)
    body += txt(x + w - 18, y + 28, "Esc", size=10, fill=SOFT, family=F_MONO, anchor="end")
    body += rect(x + 18, y + 42, w - 36, 38, fill=WHITE, stroke=OXIDE, sw=2)
    body += txt(x + 30, y + 66, "=SUM(B2:B9) * rate", size=13, fill=INK, family=F_MONO)
    body += txt(x + 18, y + 108, "SOURCES", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.6)
    src_body, _ = chip(x + 18, y + 120, "TABLE B2:B9", colour=PINE2)
    body += src_body
    src_body, _ = chip(x + 156, y + 120, "RATE · GBP", colour=PINE2)
    body += src_body
    body += txt(x + 18, y + 172, "AUTHORITY", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.6)
    body += txt(x + 18, y + 194, "Read table", size=11, fill=INK)
    body += txt(x + w - 18, y + 194, "granted", size=11, fill=PINE2, family=F_MONO, anchor="end")
    body += txt(x + 18, y + 214, "Read rate", size=11, fill=INK)
    body += txt(x + w - 18, y + 214, "granted", size=11, fill=PINE2, family=F_MONO, anchor="end")
    body += line(x + 18, y + 232, x + w - 18, y + 232, stroke=LINE)
    body += txt(x + 18, y + 258, "1,284.00 GBP", size=18, fill=PINE2, family=F_MONO, weight="bold")
    state_body, _ = state_chip(x + w - 104, y + 242, "Current")
    body += state_body
    body += button(x + 18, y + 268, 150, "Insert live value", primary=True, height=30)
    body += button(x + 180, y + 268, 92, "Cancel", height=30)
    # Notes.
    body += txt(860, 200, "RULES", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    body += lines(860, 232, ["Offer only applicable tools.", "Name every source.", "Show the grants used.", "Keep the last result visible.", "Deny instead of inventing."], size=11, leading=28, fill=SOFT)
    body += line(860, 400, 1136, 400, stroke=LINE)
    body += para(860, 426, 276, "The result enters the document as a live value with its own identity. It is not a pasted number, and it is not a private macro.", size=11, leading=17)
    body += para(860, 520, 276, "If a source moves or its grant is withdrawn, the formula becomes stale or denied. The last computed value remains visible and labelled.", size=11, leading=17)
    return svg_doc(1200, 760, "Formula tool popover over a selected table", "A table with selected cells and a formula popover showing the expression, sources, authority, result and state.", body)


def fig_hello() -> str:
    body = title_block(64, 70, "hello-window", "The smallest application that proves the contract. It is small on purpose, and complete on purpose.")
    x, y, w, h = 64, 158, 470, 300
    body += window_shell(x, y, w, h, "hello-window", ["File", "View", "Help"], status="1 document · exported 14:02", state="Current")
    body += txt(x + 28, y + 108, "Hello, Cabochon.", size=28, family=F_DISPLAY, style="italic")
    body += para(x + 28, y + 138, w - 56, "One window, three menus, one document and one command. Everything the environment requires is present, and nothing else is.", size=11, leading=16)
    body += button(x + 28, y + 206, 122, "Export", primary=True, height=34)
    body += button(x + 162, y + 206, 112, "About", height=34)
    body += txt(x + 28, y + 262, "Ctrl+Q quits · F1 opens About", size=10, fill=SOFT, family=F_MONO)
    # Artefacts.
    ax = 590
    body += txt(ax, 190, "EXPORT BUNDLE", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    artefacts = ["content.pdf", "content-print.pdf", "content.png", "thumbnail.png", "accessibility.json", "clipboard/", "hit-map.json", "export.json"]
    for index, name in enumerate(artefacts):
        col, row = index % 2, index // 2
        bx = ax + col * 270
        by = 214 + row * 44
        body += rect(bx, by, 250, 32, fill=HIGH, stroke=LINE)
        body += txt(bx + 12, by + 21, name, size=11, fill=INK, family=F_MONO)
        body += txt(bx + 238, by + 21, "✓", size=12, fill=PINE2, anchor="end", weight="bold")
    body += para(ax, 420, 520, "Each artefact comes from the same Lapidary scene. Geometry, text placement, clipping and metadata agree within the declared tolerances, and the accessibility and hit-map outputs describe the same objects that were drawn.", size=11, leading=17)
    body += txt(ax, 520, "The reference application is not a demo.", size=12, fill=OXIDE, family=F_DISPLAY, style="italic")
    body += line(64, 560, 1136, 560, stroke=LINE)
    body += txt(64, 592, "WHAT IT PROVES", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    proofs = [
        ("Resources", "Menus, strings and shortcuts load from Escutcheon."),
        ("Scene", "One Lapidary scene renders every target."),
        ("Output", "Burin writes display, PDF, raster and metadata."),
        ("Access", "Roles, names and focus order are extractable."),
        ("Locale", "en-XA and ar-XB run without layout breaks."),
    ]
    for index, (name, detail) in enumerate(proofs):
        px = 64 + index * 216
        body += txt(px, 622, name.upper(), size=10, fill=PINE2, family=F_MONO, weight="bold")
        body += para(px, 644, 190, detail, size=10, leading=15)
    return svg_doc(1200, 760, "hello-window reference application", "A small hello-window application with File, View and Help menus, an Export button and the complete export bundle, plus the contracts it proves.", body)


def fig_project() -> str:
    body = title_block(64, 70, "A project is a working context", "Documents, objects, links, tools and views belong to a project. Renaming a file does not rename the object behind it.")
    x, y, w, h = 64, 150, 1072, 520
    body += window_shell(x, y, w, h, "Projects — North Sea transition", ["File", "Edit", "View", "Project", "Window", "Help"], status="3 documents · 8 objects · 2 links", state="Current")
    left_w, right_w = 260, 280
    body += rect(x, y + 60, left_w, h - 86, fill=PAPER, stroke=None)
    body += pane_head(x, y + 60, left_w, "Project")
    tree = [("North Sea transition", 0), ("notes/", 1), ("transition.md", 2), ("sources.md", 2), ("data/", 1), ("generation.csv", 2), ("figures/", 1), ("plate.svg", 2)]
    for index, (name, depth) in enumerate(tree):
        ty = y + 100 + index * 30
        selected = name == "transition.md"
        if selected:
            body += rect(x, ty - 18, left_w, 27, fill=PINE2, stroke=None)
        body += txt(x + 14 + depth * 16, ty, name, size=11, fill=WHITE if selected else (INK if depth < 2 else SOFT))
    body += line(x + left_w, y + 60, x + left_w, y + h - 26, stroke=INK)
    # Centre list.
    cx = x + left_w + 24
    body += txt(cx, y + 98, "Documents", size=16, family=F_DISPLAY, style="italic")
    docs = [
        ("transition.md", "note:transition", "3 embeds · updated 14:02", "Current"),
        ("sources.md", "note:sources", "12 links · updated 13:40", "Current"),
        ("generation.csv", "obj:8f3a", "table · 12 rows", "Stale"),
    ]
    for index, (name, identity, detail, state) in enumerate(docs):
        dy = y + 120 + index * 92
        body += rect(cx, dy, 520, 76, fill=HIGH, stroke=LINE)
        body += txt(cx + 16, dy + 26, name, size=12, weight="bold")
        body += txt(cx + 16, dy + 46, identity, size=11, fill=SOFT, family=F_MONO)
        body += txt(cx + 16, dy + 64, detail, size=11, fill=SOFT)
        state_body, _ = state_chip(cx + 400, dy + 14, state)
        body += state_body
    body += para(cx, y + 430, 520, "A project remembers which views were open, which panes were collapsed and which objects were pinned. It does not own the objects inside it.", size=11, leading=17)
    # Right links.
    rx = x + w - right_w
    body += rect(rx, y + 60, right_w, h - 86, fill=PAPER, stroke=None)
    body += line(rx, y + 60, rx, y + h - 26, stroke=INK)
    body += pane_head(rx, y + 60, right_w, "Identity")
    body += inspector_row(rx + 14, y + 116, right_w - 28, "Document", "note:transition")
    body += inspector_row(rx + 14, y + 140, right_w - 28, "File", "notes/transition.md")
    body += inspector_row(rx + 14, y + 164, right_w - 28, "Revision", "r42")
    body += txt(rx + 14, y + 200, "RENAME", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.6)
    body += para(rx + 14, y + 224, right_w - 28, "Moving notes/transition.md to notes/archive/transition.md keeps note:transition and every link to it.", size=11, leading=17)
    body += line(rx + 14, y + 312, rx + right_w - 14, y + 312, stroke=LINE)
    body += txt(rx + 14, y + 340, "Recent views", size=11, weight="bold")
    body += txt(rx + 14, y + 364, "Note · editor", size=11, fill=SOFT)
    body += txt(rx + 14, y + 384, "Table · generation", size=11, fill=SOFT)
    body += txt(rx + 14, y + 404, "Output · print proof", size=11, fill=SOFT)
    return svg_doc(1200, 760, "Project window with tree, documents and identity panel", "A project window showing a file tree, a document list with live states and an identity panel explaining rename behaviour.", body)


def fig_embed() -> str:
    body = title_block(64, 70, "An embed is a promise", "The document owns a presentation. The object keeps its identity, its provider and its state.")
    # Document side.
    dx, dy, dw, dh = 64, 180, 340, 380
    body += rect(dx, dy, dw, dh, fill=HIGH, stroke=INK)
    body += pane_head(dx, dy, dw, "Document")
    body += txt(dx + 18, dy + 54, "North Sea transition", size=16, family=F_DISPLAY, style="italic")
    body += para(dx + 18, dy + 82, dw - 36, "The note contains a table. The table is not copied into the note file.", size=11, leading=16)
    body += rect(dx + 18, dy + 150, dw - 36, 120, fill=PAPER, stroke=LINE)
    body += txt(dx + 32, dy + 176, "Generation mix", size=12, weight="bold")
    body += txt(dx + 32, dy + 194, "Table · 12 rows", size=10, fill=SOFT, family=F_MONO)
    state_body, _ = state_chip(dx + dw - 122, dy + 166, "Current")
    body += state_body
    for row in range(3):
        body += line(dx + 32, dy + 210 + row * 16, dx + dw - 32, dy + 210 + row * 16, stroke=LINE, sw=0.5)
    body += txt(dx + 18, dy + 316, "EMBED ENVELOPE", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=0.6)
    body += txt(dx + 18, dy + 340, "obj:8f3a · r17 · table", size=11, fill=INK, family=F_MONO)
    body += txt(dx + 18, dy + 360, "presentation: in-note", size=11, fill=INK, family=F_MONO)
    # Arrow.
    ax = dx + dw + 30
    body += line(ax, 330, ax + 130, 330, stroke=INK, sw=2)
    body += path(f"M {ax + 122} 322 L {ax + 134} 330 L {ax + 122} 338", stroke=INK, sw=2)
    body += txt(ax + 6, 320, "resolve", size=10, fill=SOFT, family=F_MONO)
    # Provider side.
    px = ax + 160
    body += rect(px, 180, 340, 240, fill=PAPER, stroke=INK)
    body += pane_head(px, 180, 340, "Provider")
    body += txt(px + 18, 234, "enfilade.table", size=13, weight="bold", family=F_MONO)
    body += txt(px + 18, 254, "owns payload · revisions · grants", size=10, fill=SOFT)
    body += inspector_row(px + 18, 286, 304, "Object", "obj:8f3a")
    body += inspector_row(px + 18, 310, 304, "Revision", "r17")
    body += inspector_row(px + 18, 334, 304, "State", "current")
    body += txt(px + 18, 372, "A second presentation reads the same object.", size=10, fill=SOFT)
    # States.
    body += txt(64, 612, "HOW RESOLUTION ENDS", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    states = [("Resolved", "provider answered"), ("Opaque", "unknown object type"), ("Unavailable", "provider absent"), ("Malformed", "payload unreadable")]
    for index, (name, detail) in enumerate(states):
        sx = 64 + index * 216
        state = RESOLUTION_STATES[name]
        colour = str(state["colour"])
        mark = str(state["mark"])
        body += f'<g data-mark="{mark}">'
        body += rect(sx, 630, 200, 58, fill=HIGH, stroke=colour)
        body += state_mark(sx + 18, 652, mark, colour)
        body += txt(sx + 32, 652, name, size=12, fill=colour, weight="bold", data_state=name)
        body += txt(sx + 12, 672, detail, size=10, fill=SOFT, family=F_MONO)
        body += "</g>"
    body += para(944, 638, 192, "Only a resolved embed carries a live state: Current, Refreshing, Stale, Broken or Denied.", size=10, leading=15)
    body += para(64, 710, 1072, "No state deletes the embed or flattens it into pixels. The last readable value remains visible, with its state and the operation that would restore it.", size=11, leading=16)
    return svg_doc(1200, 760, "Embed envelope and provider", "A document embed pointing to a provider-owned object, with the five failure states listed below.", body)


def fig_output() -> str:
    body = title_block(64, 70, "One scene, every output", "The scene is the contract. Display, paper and metadata are workstations that read it.")
    cx, cy = 600, 380
    body += rect(cx - 150, cy - 64, 300, 128, fill=PINE, stroke=INK, sw=2)
    body += txt(cx, cy - 20, "LAPIDARY SCENE", size=13, fill=WHITE, family=F_MONO, weight="bold", anchor="middle", spacing=0.8)
    body += txt(cx, cy + 4, "geometry · text · clipping", size=10, fill=DARK_MUTED, family=F_MONO, anchor="middle")
    body += txt(cx, cy + 24, "transforms · hit regions", size=10, fill=DARK_MUTED, family=F_MONO, anchor="middle")
    body += txt(cx, cy + 44, "physical units · intent", size=10, fill=DARK_MUTED, family=F_MONO, anchor="middle")
    targets = [
        ("Display", "interactive", 64, 200),
        ("PDF", "vector pages", 64, 360),
        ("Print", "printer-bound", 64, 520),
        ("Thumbnail", "small raster", 330, 660),
        ("Raster", "PNG export", 530, 660),
        ("Clipboard", "geometry + text", 730, 660),
        ("Accessibility", "roles + names", 930, 520),
        ("Hit map", "regions + ids", 930, 360),
        ("Manifest", "export.json", 930, 200),
    ]
    for name, detail, tx, ty in targets:
        tw, th = 206, 64
        body += line(cx, cy, tx + tw / 2, ty + th / 2, stroke=LINE, sw=1.2)
    for name, detail, tx, ty in targets:
        tw, th = 206, 64
        body += rect(tx, ty, tw, th, fill=HIGH, stroke=INK)
        body += txt(tx + 12, ty + 25, name, size=12, weight="bold")
        body += txt(tx + 12, ty + 44, detail, size=10, fill=SOFT, family=F_MONO)
    body += txt(64, 752, "Parity is measured: geometry, text placement, clipping and metadata, within declared tolerances. A target that cannot agree fails the build.", size=11, fill=SOFT)
    return svg_doc(1200, 780, "Scene to output workstations", "A central Lapidary scene connected to display, PDF, print, thumbnail, raster, clipboard, accessibility, hit-map and manifest outputs.", body)


def fig_localization() -> str:
    body = title_block(64, 70, "Language is not a later coat of paint", "Pseudo-locales expose hard-coded widths, concatenated strings and left-to-right assumptions before translation begins.")
    # LTR expanded.
    x, y, w, h = 64, 160, 480, 340
    body += txt(x, 150, "EN-XA · +35% MINIMUM", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    body += window_shell(x, y, w, h, "Facet Notes — ⟦Ŵöŕļď ťŕáńšîťîöń ··⟧", ["⟦Fîļé⟧", "⟦Édîť⟧", "⟦Vîéŵ⟧", "⟦Héļþ⟧"], status="⟦Ŝávéď · 3 émбédš ····⟧", state="Current")
    body += txt(x + 22, y + 96, "⟦Ťŕáńšîťîöń þáťĥŵáýš ···⟧", size=20, family=F_DISPLAY, style="italic")
    body += para(x + 22, y + 124, w - 44, "⟦Ťĥé ťŕáńšîťîöń îš ńöť öńé déçîšîöń бůť á šéqůéńçé öf šмáļļ öńéš. ······⟧", size=11, leading=17)
    body += button(x + 22, y + 216, 190, "⟦Éхþöŕť áš PDF ·⟧", primary=True, height=36)
    body += button(x + 224, y + 218, 130, "⟦Çáńçéļ ·⟧", height=32)
    body += txt(x + 22, y + 292, "Controls grow; labels do not clip.", size=10, fill=OXIDE, family=F_MONO)
    # RTL mirrored.
    x2 = 656
    body += txt(x2, 150, "AR-XB · MIRRORED", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    body += window_shell(x2, y, 480, h, "مفكرة الأوجه — انتقال بحر الشمال", ["ملف", "تحرير", "عرض", "مساعدة"], status="محفوظ · ٣ كائنات", state="Current", rtl=True)
    body += txt(x2 + w - 22, y + 96, "انتقال بحر الشمال", size=20, family=F_DISPLAY, style="italic", anchor="end")
    body += para(x2 + w - 22, y + 124, w - 44, "الانتقال ليس قراراً واحداً بل سلسلة من القرارات الصغيرة. يبقى كل مصدر قابلاً للتحرير، ويحتفظ كل كائن بهويته.", size=11, leading=17, anchor="end")
    body += button(x2 + w - 182, y + 214, 160, "تصدير PDF", primary=True, height=38)
    body += button(x2 + w - 324, y + 214, 130, "إلغاء", height=38)
    body += txt(x2 + w - 22, y + 284, "تنتقل الواجهة كاملة إلى اليمين.", size=10, fill=OXIDE, family=F_MONO, anchor="end")
    # Notes.
    body += txt(64, 552, "WHAT THE PSEUDO-LOCALES CATCH", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    notes = [
        ("en-XA", "Expanded accents reveal clipped labels and fixed-width buttons."),
        ("ar-XB", "Mirrored layout reveals panes, icons and reading order that assume left-to-right."),
        ("Numbers", "Digits, dates and currency are formatted by locale, never assembled from strings."),
        ("Strings", "Full sentences are resources. Fragments are not concatenated."),
    ]
    for index, (name, detail) in enumerate(notes):
        nx = 64 + index * 270
        body += txt(nx, 582, name.upper(), size=10, fill=PINE2, family=F_MONO, weight="bold")
        body += para(nx, 602, 246, detail, size=11, leading=16)
    body += txt(64, 704, "A localized build is a gate, not a screenshot. The pseudo-locales run in the same export bundle as the default language.", size=11, fill=SOFT)
    return svg_doc(1200, 760, "Pseudo-localized left-to-right and right-to-left windows", "Two windows showing expanded en-XA text and mirrored ar-XB layout, with notes on what the pseudo-locales test.", body)


def fig_accessibility() -> str:
    body = title_block(64, 70, "The accessibility tree is another output", "Names, roles, states and order come from the same scene that draws the pixels. They are not reconstructed afterwards.")
    # Window with focus order.
    x, y, w, h = 64, 160, 560, 480
    body += window_shell(x, y, w, h, "Facet Notes — North Sea transition", ["File", "Edit", "View", "Object", "Tools", "Window", "Help"], status="North Sea transition · 1 embed selected")
    body += pane_head(x, y + 60, 180, "Notes")
    body += pane_head(x + 180, y + 60, 380, "Document")
    for index, label in enumerate(["Project", "North Sea transition", "Sources", "Figures"]):
        ty = y + 104 + index * 28
        body += txt(x + 14, ty, label, size=11, fill=INK)
    body += txt(x + 202, y + 112, "North Sea transition", size=18, family=F_DISPLAY, style="italic")
    body += para(x + 202, y + 140, 336, "A note with one selected embed and a visible focus ring.", size=11, leading=16)
    body += rect(x + 202, y + 194, 336, 72, fill=HIGH, stroke=OXIDE, sw=3)
    body += txt(x + 218, y + 222, "Generation mix", size=12, weight="bold")
    body += txt(x + 218, y + 240, "Table · 12 rows", size=10, fill=SOFT, family=F_MONO)
    # Focus order badges.
    for number, bx, by in [(1, x + 20, y + 96), (2, x + 500, y + 112), (3, x + 520, y + 206), (4, x + 500, y + h - 12)]:
        body += circle(bx, by, 10, fill=PINE2, stroke=None)
        body += txt(bx, by + 3.5, str(number), size=9, fill=WHITE, anchor="middle", family=F_MONO, weight="bold")
    # Tree.
    tx = 680
    body += txt(tx, 190, "ACCESSIBILITY TREE", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
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
    body += txt(tx, 490, "TARGETS AND CONTRAST", size=10, fill=OXIDE, family=F_MONO, weight="bold", spacing=1)
    body += rect(tx, 510, 28, 28, fill=HIGH, stroke=INK)
    body += rect(tx + 52, 506, 36, 36, fill=HIGH, stroke=INK)
    body += txt(tx + 104, 530, "28 minimum · 36 primary", size=11, fill=SOFT, family=F_MONO)
    body += para(tx, 566, 456, "Text meets 4.5:1 at body size and 3:1 at large size. Focus is visible at 3:1 against both the control and its surround. State is never carried by colour alone.", size=11, leading=17)
    body += para(tx, 650, 456, "The same tree drives screen readers, keyboard traversal and automated checks. If a name is missing from the scene, it is missing from every target.", size=11, leading=17)
    return svg_doc(1200, 760, "Accessibility tree and focus order", "A document window with numbered focus order and an accessibility tree listing roles and names, plus target-size and contrast rules.", body)


def annotate(name: str, svg: str) -> str:
    """Attach the figure's declared class, scale, profile and components.

    The annotation is machine-readable so that a checker can compare it with
    the rendered geometry instead of trusting a caption.
    """
    spec = FIGURE_SPECS.get(name)
    if spec is None:
        raise ValueError(f"figure {name!r} has no entry in tools/figure-data.json")
    figure_class = str(spec["class"])
    if figure_class not in {"schematic", "editorial", "production"}:
        raise ValueError(f"figure {name!r} has unknown class {figure_class!r}")
    scale = spec["scale"]
    components = spec["components"]
    profile = str(spec["profile"])
    metadata = {
        "name": name,
        "class": figure_class,
        "scale": scale,
        "profile": profile,
        "components": components,
    }
    payload = escape(json.dumps(metadata, sort_keys=True))
    scale_attr = "" if scale is None else f' data-figure-scale="{scale}"'
    attrs_text = (
        f' data-figure-class="{figure_class}"'
        f"{scale_attr}"
        f' data-figure-profile="{profile}"'
    )
    svg = svg.replace('role="img"', f'role="img"{attrs_text}', 1)
    marker = ">\n"
    index = svg.index(marker) + len(marker)
    return svg[:index] + f"  <metadata>{payload}</metadata>\n" + svg[index:]


def main() -> int:
    OUT.mkdir(exist_ok=True)
    figures = {
        "fig-00-cover": fig_cover,
        "fig-01-map": fig_map,
        "fig-02-small-world": fig_small_world,
        "fig-03-first-batch": fig_first_batch,
        "fig-04-principles": fig_principles,
        "fig-05-document-centre": fig_document_centre,
        "fig-06-state": fig_state,
        "fig-07-palette": fig_palette,
        "fig-08-type": fig_type,
        "fig-09-spacing": fig_spacing,
        "fig-10-planes": fig_planes,
        "fig-11-icons": fig_icons,
        "fig-12-motion": fig_motion,
        "fig-13-window": fig_window,
        "fig-14-menus": fig_menus,
        "fig-15-toolbars": fig_toolbars,
        "fig-16-panes": fig_panes,
        "fig-17-inspector": fig_inspector,
        "fig-18-controls": fig_controls,
        "fig-19-dialog": fig_dialog,
        "fig-20-focus": fig_focus,
        "fig-21-command-palette": fig_command_palette,
        "fig-22-notes": fig_notes,
        "fig-23-draw": fig_draw,
        "fig-24-press": fig_press,
        "fig-25-table": fig_table,
        "fig-26-formula": fig_formula,
        "fig-27-hello-window": fig_hello,
        "fig-28-project": fig_project,
        "fig-29-embed": fig_embed,
        "fig-30-output": fig_output,
        "fig-31-localization": fig_localization,
        "fig-32-accessibility": fig_accessibility,
    }
    missing = sorted(set(figures) - set(FIGURE_SPECS))
    extra = sorted(set(FIGURE_SPECS) - set(figures))
    if missing or extra:
        raise SystemExit(
            f"figure-data.json does not match the generator: "
            f"missing={missing} extra={extra}"
        )
    for name, draw in figures.items():
        (OUT / f"{name}.svg").write_text(annotate(name, draw()) + "\n", encoding="utf-8")
    print(f"wrote {len(figures)} figures to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
