"""Draw the window furniture and form controls that the figures compose.

`window_shell` combines `titlebar`, `menu_strip` and `status_bar`, and the
module also exports `pane_head`, `field`, `button`, `checkbox`, `radio` and
`inspector_row`. Most `figuregen.figures.*` builders import it, and it takes
state chips from `figuregen.ornaments`.
"""

# The drawing primitives take geometry and style arguments positionally; see
# the matching ruff exemption for tools/figuregen in pyproject.toml.
# pylint: disable=too-many-arguments

from __future__ import annotations

from figuregen.canvas import circle, line, path, rect, txt
from figuregen.ornaments import state_chip
from figuregen.palette import (
    F_MONO,
    HIGH,
    INK,
    LINE,
    OXIDE,
    PAPER,
    PINE,
    PINE2,
    SOFT,
    WHITE,
)


def titlebar(
    x: float,
    y: float,
    w: float,
    title: str,
    *,
    rtl: bool = False,
    controls: bool = True,
) -> str:
    """Draw a window title bar with optional window controls."""
    body = rect(x, y, w, 31, fill=PAPER, stroke=None)
    body += line(x, y + 30.5, x + w, y + 30.5, stroke=LINE)
    if rtl:
        body += txt(
            x + w - (112 if controls else 12),
            y + 20,
            title,
            size=12,
            weight="bold",
            anchor="end",
        )
    else:
        body += txt(x + 12, y + 20, title, size=12, weight="bold")
    if controls:
        for index, glyph in enumerate(["–", "□", "×"]):
            bx = x + 4 + index * 36 if rtl else x + w - 104 + index * 36
            body += txt(bx + 14, y + 22, glyph, size=16, anchor="middle")
    return body


def menu_strip(
    x: float,
    y: float,
    w: float,
    items: list[str],
    *,
    active: str | None = None,
    rtl: bool = False,
) -> str:
    """Draw a menu strip with one active menu."""
    body = rect(x, y, w, 29, fill=PAPER, stroke=None)
    body += line(x, y + 28.5, x + w, y + 28.5, stroke=LINE)
    cursor = x + w - 15 if rtl else x + 10
    for item in items:
        item_width = len(item) * 7 + 20
        if rtl:
            if item == active:
                body += rect(
                    cursor - item_width + 5,
                    y + 3,
                    item_width,
                    23,
                    fill=PINE2,
                    stroke=None,
                )
                body += txt(
                    cursor - 5,
                    y + 19,
                    item,
                    size=12,
                    fill=WHITE,
                    weight="bold",
                    anchor="end",
                )
            else:
                body += txt(cursor - 5, y + 19, item, size=12, fill=INK, anchor="end")
            cursor -= item_width
        else:
            if item == active:
                body += rect(cursor - 5, y + 3, item_width, 23, fill=PINE2, stroke=None)
                body += txt(
                    cursor + 5, y + 19, item, size=12, fill=WHITE, weight="bold"
                )
            else:
                body += txt(cursor + 5, y + 19, item, size=12, fill=INK)
            cursor += item_width
    return body


def status_bar(
    x: float,
    y: float,
    w: float,
    message: str,
    *,
    state: str | None = None,
    rtl: bool = False,
) -> str:
    """Draw a status line with an optional live state."""
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


def pane_head(
    x: float, y: float, w: float, title: str, *, right: str | None = None
) -> str:
    """Draw a pane header with an optional right-hand label."""
    body = rect(x, y, w, 28, fill=PAPER, stroke=None)
    body += line(x, y + 27.5, x + w, y + 27.5, stroke=LINE)
    body += txt(
        x + 10, y + 18, title.upper(), size=10, fill=SOFT, weight="bold", spacing=0.8
    )
    if right:
        body += txt(x + w - 10, y + 18, right, size=10, fill=SOFT, anchor="end")
    return body


def window_shell(
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    title: str,
    menu: list[str],
    active_menu: str | None = None,
    status: str | None = None,
    state: str | None = None,
    rtl: bool = False,
) -> str:
    """Draw a window shell with title bar, menu strip and status line."""
    body = rect(x + 8, y + 8, w, h, fill="#17201C20", stroke=None)
    body += rect(x, y, w, h, fill=HIGH, stroke=INK)
    body += titlebar(x, y, w, title, rtl=rtl)
    body += menu_strip(x, y + 31, w, menu, active=active_menu, rtl=rtl)
    body += line(x, y + 60, x + w, y + 60, stroke=LINE)
    if status is not None:
        body += status_bar(x, y + h - 26, w, status, state=state, rtl=rtl)
    return body


def field(
    x: float,
    y: float,
    w: float,
    value: str,
    *,
    label: str | None = None,
    height: float = 32,
    focus: bool = False,
) -> str:
    """Draw a labelled text field, optionally focused."""
    body = ""
    if label:
        body += txt(x, y - 6, label, size=11, fill=SOFT)
    body += rect(
        x,
        y,
        w,
        height,
        fill=WHITE,
        stroke=OXIDE if focus else LINE,
        sw=2 if focus else 1,
    )
    body += txt(x + 10, y + height / 2 + 4, value, size=12, fill=INK)
    return body


def button(
    x: float,
    y: float,
    w: float,
    label: str,
    *,
    primary: bool = False,
    destructive: bool = False,
    height: float = 32,
    disabled: bool = False,
) -> str:
    """Draw a button in primary, destructive or default form."""
    fill = PINE if primary else HIGH
    stroke = PINE if primary else LINE
    colour = WHITE if primary else (OXIDE if destructive else INK)
    if disabled:
        fill = PAPER
        stroke = LINE
        colour = SOFT
    body = rect(x, y, w, height, fill=fill, stroke=stroke)
    body += txt(
        x + w / 2,
        y + height / 2 + 4,
        label,
        size=12,
        fill=colour,
        weight="bold",
        anchor="middle",
    )
    return body


def checkbox(x: float, y: float, label: str, *, checked: bool = False) -> str:
    """Draw a checkbox with its label."""
    body = rect(x, y - 13, 16, 16, fill=WHITE, stroke=INK)
    if checked:
        body += path(
            f"M {x + 3} {y - 4} L {x + 7} {y} L {x + 14} {y - 9}", stroke=PINE2, sw=2.5
        )
    body += txt(x + 24, y, label, size=12, fill=INK)
    return body


def radio(x: float, y: float, label: str, *, selected: bool = False) -> str:
    """Draw a radio button with its label."""
    body = circle(x + 8, y - 5, 8, fill=WHITE, stroke=INK)
    if selected:
        body += circle(x + 8, y - 5, 4, fill=PINE2, stroke=None)
    body += txt(x + 24, y, label, size=12, fill=INK)
    return body


def inspector_row(
    x: float, y: float, w: float, label: str, *, value: str, value_colour: str = INK
) -> str:
    """Draw one inspector row of label and value."""
    body = txt(x, y, label.upper(), size=10, fill=SOFT, family=F_MONO, spacing=0.5)
    body += txt(x + w, y, value, size=11, fill=value_colour, anchor="end")
    body += line(x, y + 8, x + w, y + 8, stroke=LINE, sw=0.5)
    return body
