"""Draw labelled and live-state chips."""

from __future__ import annotations

from figuregen.canvas import rect, txt
from figuregen.figdata import LIVE_STATES, RESOLUTION_STATES
from figuregen.ornaments.marks import mark_group, state_mark
from figuregen.palette import F_MONO, HIGH, PINE2


def chip(  # pylint: disable=too-many-arguments
    x: float,
    y: float,
    label: str,
    *,
    colour: str = PINE2,
    fill: str = HIGH,
    size: float = 11,
    state: str | None = None,
    mark: str = "dot",
    role: str = "pine2",
) -> tuple[str, float]:
    """Draw a labelled chip in the requested tone.

    Parameters
    ----------
    x : float
        The chip's left edge in logical units.
    y : float
        The chip's top edge in logical units; the body is 20 logical units
        high.
    label : str
        The label text, drawn in bold mono 18 logical units from the left
        edge.
    colour : str
        The colour of the outline, the mark and the label.
    fill : str
        The colour that fills the chip body.
    size : float
        The label font size in logical units, which also sets the chip width.
    state : str | None
        The state identifier recorded as the ``data-state`` annotation, or
        ``None`` to record none.
    mark : str
        The mark name, which selects the non-colour mark drawn beside the
        label.
    role : str
        The colour role recorded alongside the mark.

    Returns
    -------
    tuple[str, float]
        The SVG fragment string for the chip group and the chip's width in
        logical units, which is ``max(58.0, len(label) * size * 0.62 + 18)``
        and therefore never less than 58.
    """
    width = max(58.0, len(label) * size * 0.62 + 18)
    body = '<g data-state-chip="true">'
    body += rect(x, y, width, 20, fill=fill, stroke=colour, sw=1)
    body += mark_group(
        mark,
        state or "",
        role,
        state_mark(x + 10, y + 10, mark, colour),
    )
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

    The chip takes its label, colour, mark and role from the named state, and
    the label is drawn in upper case.

    Parameters
    ----------
    x : float
        The chip's left edge in logical units.
    y : float
        The chip's top edge in logical units; the body is 20 logical units
        high.
    name : str
        The state name, looked up first among the live states and then among
        the resolution states.

    Returns
    -------
    tuple[str, float]
        The SVG fragment string for the chip group and the chip's computed
        width in logical units.

    Raises
    ------
    ValueError
        If ``name`` is not a known state, or if the state it names declares no
        non-colour mark. The known live states are ``Current``, ``Refreshing``,
        ``Stale``, ``Broken`` and ``Denied``, and the known resolution states
        are ``Resolved``, ``Opaque``, ``Unavailable`` and ``Malformed``.
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
        state=str(state["id"]),
        mark=str(mark),
        role=str(state["role"]),
    )
