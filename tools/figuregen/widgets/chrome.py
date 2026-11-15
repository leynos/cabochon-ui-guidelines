"""Draw the window chrome: title bar, menu strip, status line and shell.

The `figuregen.widgets` package re-exports these functions for the
`figuregen.figures.*` builders that draw application windows.
"""

# The drawing primitives take geometry and style arguments positionally; see
# the matching ruff exemption for tools/figuregen in pyproject.toml.

from __future__ import annotations

import typing as typ

from figuregen.canvas import line, rect, txt
from figuregen.ornaments import state_chip
from figuregen.palette import HIGH, INK, LINE, PAPER, PINE2, SOFT, WHITE

if typ.TYPE_CHECKING:
    from figuregen.figdata import StateTables


def titlebar(  # pylint: disable=too-many-arguments
    x: float,
    y: float,
    w: float,
    title: str,
    *,
    rtl: bool = False,
    controls: bool = True,
) -> str:
    """Draw a window title bar with optional window controls.

    The bar is 31 logical units high and carries a bottom edge line.

    Parameters
    ----------
    x : float
        The bar's left edge in logical units.
    y : float
        The bar's top edge in logical units.
    w : float
        The bar's width in logical units.
    title : str
        The title text, drawn bold at 12 logical units and inset from the
        leading edge.
    rtl : bool
        Draw the title and controls right to left when true; the default
        ``False`` places them from the left.
    controls : bool
        Draw the minimise, maximise and close glyphs when true, which is the
        default; ``False`` omits them.

    Returns
    -------
    str
        The SVG fragment string for the title bar.
    """
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


def menu_strip(  # pylint: disable=too-many-arguments
    x: float,
    y: float,
    w: float,
    items: list[str],
    *,
    active: str | None = None,
    rtl: bool = False,
) -> str:
    """Draw a menu strip with one active menu.

    The strip is 29 logical units high and carries a bottom edge line. The
    active label gains a filled background and white bold text.

    Parameters
    ----------
    x : float
        The strip's left edge in logical units.
    y : float
        The strip's top edge in logical units.
    w : float
        The strip's width in logical units.
    items : list[str]
        The menu labels, drawn at 12 logical units.
    active : str | None
        The label to highlight, or ``None``, the default, to highlight none.
    rtl : bool
        Lay the labels out from the right edge when true; the default
        ``False`` lays them out from the left.

    Returns
    -------
    str
        The SVG fragment string for the menu strip.
    """
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


def status_bar(  # pylint: disable=too-many-arguments
    x: float,
    y: float,
    w: float,
    message: str,
    *,
    states: StateTables,
    state: str | None = None,
    rtl: bool = False,
) -> str:
    """Draw a status line with an optional live state.

    The bar is 26 logical units high and carries a top edge line.

    Parameters
    ----------
    x : float
        The bar's left edge in logical units.
    y : float
        The bar's top edge in logical units.
    w : float
        The bar's width in logical units.
    message : str
        The message text, drawn at 11 logical units.
    states : StateTables
        The live and resolution state records passed to
        `figuregen.ornaments.state_chip`.
    state : str | None
        The state name whose chip is drawn on the bar, or ``None``, the
        default, to draw no chip.
    rtl : bool
        Draw the message from the right edge and the chip at the left when
        true; the default ``False`` does the opposite.

    Returns
    -------
    str
        The SVG fragment string for the status bar.
    """
    body = rect(x, y, w, 26, fill=PAPER, stroke=None)
    body += line(x, y + 0.5, x + w, y + 0.5, stroke=LINE)
    if rtl:
        body += txt(x + w - 10, y + 17, message, size=11, fill=SOFT, anchor="end")
        if state:
            chip_body, _ = state_chip(x + 10, y + 1, state, states)
            body += chip_body
    else:
        body += txt(x + 10, y + 17, message, size=11, fill=SOFT)
        if state:
            chip_body, _ = state_chip(x + w - 120, y + 1, state, states)
            body += chip_body
    return body


def window_shell(  # pylint: disable=too-many-arguments
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    states: StateTables,
    title: str,
    menu: list[str],
    active_menu: str | None = None,
    status: str | None = None,
    state: str | None = None,
    rtl: bool = False,
) -> str:
    """Draw a window shell with title bar, menu strip and status line.

    The body is backed by a shadow offset 8 logical units right and down, the
    title bar and menu strip occupy the top 60 logical units, and a divider
    separates them from the content.

    Parameters
    ----------
    x : float
        The shell's left edge in logical units.
    y : float
        The shell's top edge in logical units.
    w : float
        The shell's width in logical units.
    h : float
        The shell's height in logical units; the status line sits at its
        lower edge.
    states : StateTables
        The live and resolution state records passed to `status_bar` and on to
        `figuregen.ornaments.state_chip`.
    title : str
        The window title, passed to `titlebar`.
    menu : list[str]
        The menu labels, passed to `menu_strip`.
    active_menu : str | None
        The label of the menu to highlight, or ``None``, the default, to
        highlight none.
    status : str | None
        The status message; ``None``, the default, omits the status line
        entirely.
    state : str | None
        The state name shown as a chip on the status line, or ``None``, the
        default, for no chip. It has no effect when ``status`` is ``None``.
    rtl : bool
        Lay out the title, menu strip and status line right to left when
        true; the default ``False`` lays them out from the left.

    Returns
    -------
    str
        The SVG fragment string for the window shell.
    """
    body = rect(x + 8, y + 8, w, h, fill="#17201C20", stroke=None)
    body += rect(x, y, w, h, fill=HIGH, stroke=INK)
    body += titlebar(x, y, w, title, rtl=rtl)
    body += menu_strip(x, y + 31, w, menu, active=active_menu, rtl=rtl)
    body += line(x, y + 60, x + w, y + 60, stroke=LINE)
    if status is not None:
        body += status_bar(
            x, y + h - 26, w, status, states=states, state=state, rtl=rtl
        )
    return body
