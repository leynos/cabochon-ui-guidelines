"""Figure generator module: figures.small_world."""

from __future__ import annotations

from figuregen.canvas import line, para, rect, svg_doc, txt
from figuregen.ornaments import title_block
from figuregen.palette import (
    F_DISPLAY,
    F_MONO,
    HIGH,
    INK,
    LINE,
    OXIDE,
    PAPER,
    PINE,
    PINE2,
    SOFT,
    TEAL,
    WHITE,
)


def _compact_specimen(x: float, y: float) -> str:
    """Draw the compactness specimen bands."""
    body = ""
    bands = [
        ("title bar", "31", PINE, WHITE),
        ("menu bar", "29", PINE2, WHITE),
        ("tree row", "28", TEAL, INK),
    ]
    for index, (name, measure, fill, colour) in enumerate(bands):
        by = y + 148 + index * 24
        body += rect(x + 20, by, 220, 18, fill=fill, stroke=None)
        body += txt(x + 30, by + 13, name, size=9, fill=colour, family=F_MONO)
        body += txt(
            x + 252, by + 13, f"{measure} px", size=10, fill=SOFT, family=F_MONO
        )
    return body


def _document_specimen(x: float, y: float) -> str:
    """Draw the document-centred specimen."""
    body = rect(x + 20, y + 142, 280, 60, fill=HIGH, stroke=INK)
    body += rect(x + 20, y + 142, 42, 60, fill=PAPER, stroke=LINE)
    body += rect(x + 68, y + 148, 180, 48, fill=WHITE, stroke=LINE)
    body += rect(x + 254, y + 142, 46, 60, fill=PAPER, stroke=LINE)
    return body + txt(
        x + 20,
        y + 220,
        "rail 126 · document ≥ 420 · inspector 240",
        size=10,
        fill=SOFT,
        family=F_MONO,
    )


def _liberal_specimen(x: float, y: float) -> str:
    """Draw the liberal specimen chips."""
    body = ""
    cursor = x + 20
    for label, chip_w in [
        ("Export", 84),
        ("Open format", 120),
        ("No account", 116),
    ]:
        body += rect(cursor, y + 150, chip_w, 26, fill=PAPER, stroke=INK)
        body += txt(cursor + 12, y + 168, label, size=11, fill=INK)
        cursor += chip_w + 12
    return body + txt(x + 20, y + 206, "The user owns the work.", size=11, fill=SOFT)


def _practical_specimen(x: float, y: float) -> str:
    """Draw the surface treatment specimens."""
    body = ""
    specimens = [
        ("flat fill", HIGH, True, 0),
        ("1 px keyline", PAPER, True, 0),
        ("2 px radius", HIGH, True, 2),
        ("offset shadow", HIGH, False, 0),
    ]
    for index, (label, fill, stroked, radius) in enumerate(specimens):
        sx = x + 20 + index * 120
        if not stroked:
            body += rect(sx + 4, y + 150, 40, 40, fill="#17201C18", stroke=None)
        body += rect(
            sx,
            y + 146,
            40,
            40,
            fill=fill,
            stroke=INK if stroked else None,
            rx=radius,
        )
        body += txt(sx, y + 204, label, size=10, fill=SOFT, family=F_MONO)
    return body


_SPECIMENS = {
    "compact": _compact_specimen,
    "document": _document_specimen,
    "liberal": _liberal_specimen,
    "practical": _practical_specimen,
}


def fig_small_world() -> str:
    """Draw the four structural choices of the Cabochon character."""
    body = title_block(
        64,
        70,
        "The Cabochon character",
        "Four structural choices, not a decoration kit. Each one can be recognized in a window without reading its label.",
    )
    cards = [
        (
            "01",
            "Compact",
            "rather than cramped",
            "Short rows and generous padding. Density never removes the space a hand or an eye needs.",
            "compact",
        ),
        (
            "02",
            "Document-centred",
            "rather than application-centred",
            "The document holds the largest plane; the instrument sits at its edges.",
            "document",
        ),
        (
            "03",
            "Liberal",
            "rather than paternal",
            "The user owns the work. Export stays available, formats stay open and no account gates local content.",
            "liberal",
        ),
        (
            "04",
            "Practical",
            "rather than ornamental",
            "A rule separates planes, a tint marks a state, a shadow lifts a sheet. Nothing decorates.",
            "practical",
        ),
    ]
    for index, (number, title, aside, claim, kind) in enumerate(cards):
        x = 64 + (index % 2) * 548
        y = 166 + (index // 2) * 252
        w, h = 524, 236
        body += rect(x, y, w, h, fill=HIGH, stroke=INK)
        body += txt(
            x + 20,
            y + 28,
            number,
            size=10,
            fill=OXIDE,
            family=F_MONO,
            weight="bold",
            spacing=1,
        )
        body += txt(x + 20, y + 62, title, size=22, family=F_DISPLAY, style="italic")
        body += txt(x + 20, y + 82, aside, size=12, fill=SOFT)
        body += line(x + 20, y + 96, x + w - 20, y + 96, stroke=LINE)
        body += para(x + 20, y + 118, w - 40, claim, size=11, leading=16)
        body += _SPECIMENS[kind](x, y)
    body += txt(
        64,
        700,
        "A surface that fails any one of these choices is not Cabochon, however closely it copies the palette.",
        size=13,
        fill=SOFT,
        family=F_DISPLAY,
        style="italic",
    )
    return svg_doc(
        1200,
        760,
        "Four structural choices of the Cabochon character",
        "Cards for compact, document-centred, liberal and practical character, each with a small specimen.",
        body=body,
    )
