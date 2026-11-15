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
    x, y : float
    label : str
    colour, fill : str
    size : float
    state : str | None
        State identifier.
    mark, role : str
        Mark name and colour role.

    Returns
    -------
    tuple[str, float]
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

    Parameters
    ----------
    x, y : float
    name : str
        State name.

    Returns
    -------
    tuple[str, float]
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
