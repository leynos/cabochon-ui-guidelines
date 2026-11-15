"""Figure generator module: figures.cover."""

from __future__ import annotations

from figuregen.canvas import circle, ellipse, line, lines, path, svg_doc, txt
from figuregen.palette import (
    AMBER,
    F_DISPLAY,
    F_MONO,
    INK,
    OXIDE,
    PINE,
    PINE2,
    SOFT,
    TEAL,
)


def fig_cover() -> str:
    """Draw the cover plate with the cabochon and its four instruments."""
    body = ""
    body += txt(
        72,
        86,
        "CABOCHON",
        size=11,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=2.4,
    )
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
    body += txt(
        72, 530, "Edition 0.1", size=12, family=F_MONO, weight="bold", spacing=1.2
    )
    body += txt(72, 552, "2026", size=12, family=F_MONO, spacing=1.2)
    body += txt(
        72,
        732,
        "Written for the en-GB Oxford house style.",
        size=11,
        fill=SOFT,
        family=F_MONO,
    )

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
    body += path(
        "M 724 430 C 788 300, 990 260, 1068 386", stroke="#FFFFFF", sw=10, dash=None
    )
    body += path(
        "M 724 430 C 788 300, 990 260, 1068 386", stroke="#FFFFFF", sw=2, opacity=0.55
    )
    body += path("M 766 470 C 842 408, 960 396, 1020 448", stroke=TEAL, sw=2)

    for label, lx, ly, anchor in [
        ("FACET NOTES", 602, 198, "end"),
        ("ENFILADE TABLE", 1128, 198, "end"),
        ("BURIN DRAW", 602, 590, "end"),
        ("CABOCHON PRESS", 1128, 590, "end"),
    ]:
        body += txt(
            lx,
            ly,
            label,
            size=10,
            fill=PINE2,
            family=F_MONO,
            weight="bold",
            anchor=anchor,
            spacing=0.8,
        )
        body += circle(
            lx + (8 if anchor == "start" else -8), ly + 18, 3, fill=AMBER, stroke=None
        )

    body += txt(
        1128,
        736,
        "Plate 00 / Material",
        size=10,
        fill=SOFT,
        family=F_MONO,
        anchor="end",
        spacing=0.8,
    )
    return svg_doc(
        1200,
        800,
        "Cover plate: a polished cabochon surrounded by four instruments",
        "A green cabochon stone on a warm paper ground, with Facet Notes, Enfilade Table, Burin Draw and Cabochon Press named around it.",
        body=body,
    )
