"""Draw miniature note, table, page and canvas previews."""

from __future__ import annotations

from figuregen.canvas import line, para, path, rect, txt
from figuregen.palette import (
    DARK_MUTED,
    DARK_SURFACE,
    DARK_TEXT,
    F_DISPLAY,
    F_MONO,
    HIGH,
    INK,
    LINE,
    OXIDE,
    PINE2,
    SOFT,
    WHITE,
)


def mini_note(  # pylint: disable=too-many-arguments
    x: float, y: float, w: float, h: float, *, dark: bool = False
) -> str:
    """Draw a miniature note page.

    Parameters
    ----------
    x, y, w, h : float
    dark : bool

    Returns
    -------
    str
    """
    ink = INK if not dark else DARK_TEXT
    soft = SOFT if not dark else DARK_MUTED
    fill = HIGH if not dark else DARK_SURFACE
    body = rect(x, y, w, h, fill=fill, stroke=LINE)
    body += txt(
        x + 18,
        y + 30,
        "North Sea transition",
        size=18,
        family=F_DISPLAY,
        style="italic",
        fill=ink,
    )
    body += line(x + 18, y + 44, x + w - 18, y + 44, stroke=LINE)
    for index, width in enumerate([0.82, 0.9, 0.72, 0.86, 0.64]):
        body += rect(
            x + 18, y + 60 + index * 16, (w - 36) * width, 5, fill=soft, stroke=None
        )
    return body


def mini_table(x: float, y: float, w: float, h: float) -> str:
    """Draw a miniature data table.

    Parameters
    ----------
    x, y, w, h : float

    Returns
    -------
    str
    """
    body = rect(x, y, w, h, fill=WHITE, stroke=LINE)
    body += rect(x, y, w, 24, fill=PINE2, stroke=None)
    body += txt(
        x + 10,
        y + 16,
        "GBP · DAILY RATES",
        size=9,
        fill=WHITE,
        family=F_MONO,
        weight="bold",
    )
    body += txt(x + 10, y + 40, "DATE", size=8, fill=SOFT, family=F_MONO, weight="bold")
    body += txt(
        x + w - 74,
        y + 40,
        "RATE",
        size=8,
        fill=SOFT,
        family=F_MONO,
        weight="bold",
        anchor="end",
    )
    body += txt(
        x + w - 10,
        y + 40,
        "SOURCE",
        size=8,
        fill=SOFT,
        family=F_MONO,
        weight="bold",
        anchor="end",
    )
    rows = [
        ("13 Apr 2026", "1.2840", "ECB"),
        ("12 Apr 2026", "1.2790", "ECB"),
        ("11 Apr 2026", "1.2860", "ECB"),
    ]
    for index, (date, rate, source) in enumerate(rows):
        ry = y + 58 + index * 20
        if index == 0:
            body += rect(x + 6, ry - 12, w - 12, 17, fill=PINE2, stroke=None)
        fill = WHITE if index == 0 else INK
        body += txt(x + 10, ry, date, size=9, fill=fill, family=F_MONO)
        body += txt(
            x + w - 74, ry, rate, size=9, fill=fill, family=F_MONO, anchor="end"
        )
        body += txt(
            x + w - 10,
            ry,
            source,
            size=9,
            fill=WHITE if index == 0 else SOFT,
            family=F_MONO,
            anchor="end",
        )
    return body


def mini_page(x: float, y: float, w: float, h: float) -> str:
    """Draw a miniature publication page.

    Parameters
    ----------
    x, y, w, h : float

    Returns
    -------
    str
    """
    body = rect(x, y, w, h, fill=WHITE, stroke=LINE)
    body += txt(
        x + 16,
        y + 26,
        "NORTH SEA CURRENCY",
        size=8,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    body += txt(
        x + 16, y + 52, "GBP 1,284", size=22, fill=INK, family=F_MONO, weight="bold"
    )
    body += line(x + 16, y + 64, x + w - 16, y + 64, stroke=LINE)
    body += para(
        x + 16,
        y + 82,
        w - 32,
        "Printed from the same object, with its source and revision attached.",
        size=8,
        leading=11,
        fill=SOFT,
    )
    body += txt(
        x + 16, y + h - 8, "1 / 1 · proof · obj:c128", size=8, fill=SOFT, family=F_MONO
    )
    return body


def mini_canvas(x: float, y: float, w: float, h: float) -> str:
    """Draw a miniature drawing canvas.

    Parameters
    ----------
    x, y, w, h : float

    Returns
    -------
    str
    """
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
        body += rect(
            x + w * ax - 4, y + h * ay - 4, 8, 8, fill=WHITE, stroke=OXIDE, sw=1.5
        )
    return body
