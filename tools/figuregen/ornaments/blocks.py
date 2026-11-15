"""Draw the page furniture: kickers, title blocks and frames.

`kicker` sets a small section label, `title_block` pairs an italic display
title with its explanatory paragraph, and `frame` outlines a group of
related tiles. The `figuregen.ornaments` package re-exports all three for the
`figuregen.figures.*` builders, which open every page with a kicker and a
title block.
"""

from __future__ import annotations

from figuregen.canvas import lines, rect, txt
from figuregen.palette import F_DISPLAY, F_MONO, HIGH, INK, OXIDE, SOFT


def kicker(x: float, y: float, value: str, *, colour: str = OXIDE) -> str:
    """Draw a small upper-case section label.

    Parameters
    ----------
    x, y : float
    value : str
    colour : str

    Returns
    -------
    str
    """
    return txt(
        x,
        y,
        value.upper(),
        size=10,
        fill=colour,
        family=F_MONO,
        weight="bold",
        spacing=1.1,
    )


def title_block(x: float, y: float, heading: str, deck: str | None = None) -> str:
    """Draw a heading with an optional deck.

    The deck is drawn as one line rather than wrapped. Its baseline is
    ``y + 80``, while almost every figure begins its content between ``y + 150``
    and ``y + 166``, so a wrapped deck would overlap the figure it introduces.

    Parameters
    ----------
    x, y : float
        The heading's left edge and baseline in logical units.
    heading : str
        The display heading, drawn italic at 34 logical units.
    deck : str | None
        The explanatory paragraph, drawn as one line of 13 logical units, or
        ``None``, the default, to omit it.

    Returns
    -------
    str
        The SVG fragment string for the kicker, heading and optional deck.
    """
    body = kicker(x, y, "Cabochon interface guidelines")
    body += txt(x, y + 48, heading, size=34, family=F_DISPLAY, style="italic")
    if deck:
        body += lines(x, y + 80, [deck], size=13, fill=SOFT, leading=19)
    return body


def frame(  # pylint: disable=too-many-arguments
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    label: str | None = None,
    fill: str = HIGH,
    stroke: str = INK,
) -> str:
    """Draw a framed panel with an optional label.

    Parameters
    ----------
    x, y, w, h : float
    label : str | None
    fill, stroke : str

    Returns
    -------
    str
    """
    body = rect(x, y, w, h, fill=fill, stroke=stroke)
    if label:
        body += txt(
            x + 12,
            y + 20,
            label.upper(),
            size=10,
            fill=OXIDE,
            family=F_MONO,
            weight="bold",
            spacing=0.8,
        )
    return body
