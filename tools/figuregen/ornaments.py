"""Draw the shared page ornaments, state chips and miniature document views.

`title_block`, `kicker` and `frame` set the page furniture, `state_chip` pairs
each declared state with a distinct non-colour mark, and `mini_note`,
`mini_table`, `mini_page` and `mini_canvas` draw the document previews. Nearly
every `figuregen.figures.*` builder imports the module, as does
`figuregen.widgets`.
"""

# The drawing primitives take geometry and style arguments positionally; see
# the matching ruff exemption for tools/figuregen in pyproject.toml.
# pylint: disable=too-many-arguments

from __future__ import annotations

from figuregen.canvas import attrs, circle, line, lines, para, path, rect, txt
from figuregen.figdata import LIVE_STATES, RESOLUTION_STATES
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


def kicker(x: float, y: float, value: str, *, colour: str = OXIDE) -> str:
    """Draw a small upper-case section label."""
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

    Colour is never the only carrier of meaning, so every state declares a
    distinct shape. An unknown mark is a generation failure.
    """
    builder = _MARKS.get(kind)
    if builder is None:
        raise ValueError(f"unknown state mark {kind!r}")
    return builder(cx, cy, colour)


def mark_group(mark: str, state_id: str, role: str, body: str) -> str:
    """Wrap a state mark so identity, role and drawn geometry travel together."""
    attributes = attrs(data_mark=mark, data_state_id=state_id, data_role=role)
    return f"<g {attributes}>{body}</g>"


def chip(
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
    """Draw a labelled chip in the requested tone."""
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

    Every supported state has one declared identity, word, cue, mark and colour
    role. An unknown state is a generation failure, not a silent fallback to a
    plausible colour.
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


def title_block(
    x: float, y: float, heading: str, deck: str | None = None, *, width: int = 520
) -> str:
    """Draw a heading with an optional deck."""
    body = kicker(x, y, "Cabochon interface guidelines")
    body += txt(x, y + 48, heading, size=34, family=F_DISPLAY, style="italic")
    if deck:
        body += lines(x, y + 80, [deck], size=13, fill=SOFT, leading=19)
    return body


def frame(
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    label: str | None = None,
    fill: str = HIGH,
    stroke: str = INK,
) -> str:
    """Draw a framed panel with an optional label."""
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


def mini_note(x: float, y: float, w: float, h: float, *, dark: bool = False) -> str:
    """Draw a miniature note page."""
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
    """Draw a miniature data table."""
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
    """Draw a miniature publication page."""
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
    """Draw a miniature drawing canvas."""
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
