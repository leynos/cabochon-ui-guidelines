"""Draw the state marks and group them with their identity.

Each declared state maps to one mark — a dot, arc, triangle, broken ring,
lock, hatch, dashed line or cross — so a state still reads in greyscale.
`mark_group` wraps a mark and its label in a group that the figure checker
can attribute to a state. The `figuregen.ornaments` package re-exports both
for `figuregen.ornaments.chips` and for the figures that draw a state legend.
"""

from __future__ import annotations

from figuregen.canvas import attrs, circle, line, path, rect


def _dot(cx: float, cy: float, colour: str) -> str:
    """Draw the dot mark."""
    return circle(cx, cy, 3, fill=colour, stroke=None)


def _arc(cx: float, cy: float, colour: str) -> str:
    """Draw the refresh arc mark."""
    return path(
        f"M {cx + 2.6:.2f} {cy - 1.4:.2f} A 2.9 2.9 0 1 0 {cx + 2.7:.2f} {cy + 1.2:.2f}",
        stroke=colour,
        sw=1.5,
    ) + path(
        f"M {cx + 3.4:.2f} {cy - 2.6:.2f} L {cx + 2.6:.2f} {cy - 1.4:.2f} L {cx + 1.4:.2f} {cy - 1.8:.2f}",
        stroke=colour,
        sw=1.3,
    )


def _triangle(cx: float, cy: float, colour: str) -> str:
    """Draw the stale triangle mark."""
    return path(
        f"M {cx:.2f} {cy - 3.4:.2f} L {cx + 3.4:.2f} {cy + 2.8:.2f} L {cx - 3.4:.2f} {cy + 2.8:.2f} Z",
        fill=colour,
        stroke=None,
    )


def _broken(cx: float, cy: float, colour: str) -> str:
    """Draw the broken-link mark."""
    return (
        line(cx - 3.4, cy, cx - 1.3, cy, stroke=colour, sw=1.8)
        + line(cx + 1.3, cy, cx + 3.4, cy, stroke=colour, sw=1.8)
        + line(cx - 2.8, cy - 2.4, cx - 1.8, cy - 1.2, stroke=colour, sw=1)
        + line(cx + 2.8, cy + 2.4, cx + 1.8, cy + 1.2, stroke=colour, sw=1)
    )


def _lock(cx: float, cy: float, colour: str) -> str:
    """Draw the denied padlock mark."""
    return path(
        f"M {cx - 1.8:.2f} {cy - 0.6:.2f} L {cx - 1.8:.2f} {cy - 1.8:.2f} "
        f"A 1.8 1.8 0 0 1 {cx + 1.8:.2f} {cy - 1.8:.2f} L {cx + 1.8:.2f} {cy - 0.6:.2f}",
        stroke=colour,
        sw=1.2,
    ) + rect(cx - 2.8, cy - 0.6, 5.6, 4.2, fill=colour, stroke=None, rx=0.6)


def _hatch(cx: float, cy: float, colour: str) -> str:
    """Draw the hatched mark."""
    return (
        rect(cx - 3, cy - 3, 6, 6, stroke=colour, sw=1)
        + line(cx - 2.2, cy + 2.2, cx + 2.2, cy - 2.2, stroke=colour, sw=0.9)
        + line(cx - 0.4, cy + 2.6, cx + 2.6, cy - 0.4, stroke=colour, sw=0.9)
        + line(cx - 2.6, cy + 0.4, cx + 0.4, cy - 2.6, stroke=colour, sw=0.9)
    )


def _dashed(cx: float, cy: float, colour: str) -> str:
    """Draw the dashed outline mark."""
    return rect(cx - 3, cy - 3, 6, 6, stroke=colour, sw=1.2, dash="1.6 1.4")


def _crossed(cx: float, cy: float, colour: str) -> str:
    """Draw the crossed-square mark."""
    return (
        rect(cx - 3, cy - 3, 6, 6, stroke=colour, sw=1)
        + line(cx - 2, cy - 2, cx + 2, cy + 2, stroke=colour, sw=1.2)
        + line(cx - 2, cy + 2, cx + 2, cy - 2, stroke=colour, sw=1.2)
    )


_MARKS = {
    "dot": _dot,
    "arc": _arc,
    "triangle": _triangle,
    "broken": _broken,
    "lock": _lock,
    "hatch": _hatch,
    "dashed": _dashed,
    "crossed": _crossed,
}


def state_mark(cx: float, cy: float, kind: str, colour: str) -> str:
    """Draw the non-colour mark that distinguishes a state chip.

    Parameters
    ----------
    cx : float
        The mark's centre, in logical units from the figure's left edge.
    cy : float
        The mark's centre, in logical units from the figure's top edge.
    kind : str
        The mark name, one of ``dot``, ``arc``, ``triangle``, ``broken``,
        ``lock``, ``hatch``, ``dashed`` or ``crossed``.
    colour : str
        The colour applied to the mark's fill or stroke.

    Returns
    -------
    str
        The SVG fragment that draws the mark, with no surrounding group.

    Raises
    ------
    ValueError
        If `kind` names no declared mark.
    """
    builder = _MARKS.get(kind)
    if builder is None:
        raise ValueError(f"unknown state mark {kind!r}")
    return builder(cx, cy, colour)


def mark_group(mark: str, state_id: str, role: str, body: str) -> str:
    """Wrap a state mark so identity, role and geometry travel together.

    Parameters
    ----------
    mark, state_id, role : str
        Mark, state identifier and colour role.
    body : str
        Drawn geometry.

    Returns
    -------
    str
    """
    attributes = attrs(data_mark=mark, data_state_id=state_id, data_role=role)
    return f"<g {attributes}>{body}</g>"
