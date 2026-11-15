"""Draw form controls: fields, buttons, checkboxes and radio buttons.

The `figuregen.widgets` package re-exports these functions for the
`figuregen.figures.*` builders that draw forms and dialogs.
"""

# The drawing primitives take geometry and style arguments positionally; see
# the matching ruff exemption for tools/figuregen in pyproject.toml.

from __future__ import annotations

from figuregen.canvas import circle, path, rect, txt
from figuregen.palette import HIGH, INK, LINE, OXIDE, PAPER, PINE, PINE2, SOFT, WHITE


def field(  # pylint: disable=too-many-arguments
    x: float,
    y: float,
    w: float,
    value: str,
    *,
    label: str | None = None,
    height: float = 32,
    focus: bool = False,
) -> str:
    """Draw a labelled text field, optionally focused.

    Parameters
    ----------
    x : float
        The field's left edge in logical units.
    y : float
        The field's top edge in logical units.
    w : float
        The field's width in logical units.
    value : str
        The text drawn in the field at 12 logical units.
    label : str | None
        The label drawn above the field at 11 logical units, or ``None``, the
        default, to draw no label.
    height : float
        The field's height in logical units; the default is 32.
    focus : bool
        Draw a thick oxide outline when true, and a thin line outline when
        false, which is the default.

    Returns
    -------
    str
        The SVG fragment string for the field.
    """
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


def button(  # pylint: disable=too-many-arguments
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
    """Draw a button in primary, destructive or default form.

    Parameters
    ----------
    x : float
        The button's left edge in logical units.
    y : float
        The button's top edge in logical units.
    w : float
        The button's width in logical units.
    label : str
        The label text, drawn bold at 12 logical units and centred.
    primary : bool
        Fill the button and its outline with pine and draw white text when
        true; the default ``False`` uses the high surface and a line outline.
    destructive : bool
        Draw the label in oxide when true and ``primary`` is false; the
        default ``False`` draws the ink colour.
    height : float
        The button's height in logical units; the default is 32.
    disabled : bool
        Draw a paper surface with soft text and a line outline when true,
        overriding the other styles; the default ``False`` leaves the button
        enabled.

    Returns
    -------
    str
        The SVG fragment string for the button.
    """
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
    """Draw a checkbox with its label.

    Parameters
    ----------
    x : float
        The left edge of the box in logical units.
    y : float
        The label's baseline in logical units; the box is drawn above it,
        starting 13 logical units higher.
    label : str
        The label text, drawn at 12 logical units to the right of the box.
    checked : bool
        Draw the check mark when true; the default ``False`` draws an empty
        box.

    Returns
    -------
    str
        The SVG fragment string for the checkbox.
    """
    body = rect(x, y - 13, 16, 16, fill=WHITE, stroke=INK)
    if checked:
        body += path(
            f"M {x + 3} {y - 4} L {x + 7} {y} L {x + 14} {y - 9}", stroke=PINE2, sw=2.5
        )
    body += txt(x + 24, y, label, size=12, fill=INK)
    return body


def radio(x: float, y: float, label: str, *, selected: bool = False) -> str:
    """Draw a radio button with its label.

    Parameters
    ----------
    x : float
        The left edge of the outer ring in logical units.
    y : float
        The label's baseline in logical units; the ring is centred 5 logical
        units above it.
    label : str
        The label text, drawn at 12 logical units to the right of the ring.
    selected : bool
        Draw the filled inner dot when true; the default ``False`` draws an
        empty ring.

    Returns
    -------
    str
        The SVG fragment string for the radio button.
    """
    body = circle(x + 8, y - 5, 8, fill=WHITE, stroke=INK)
    if selected:
        body += circle(x + 8, y - 5, 4, fill=PINE2, stroke=None)
    body += txt(x + 24, y, label, size=12, fill=INK)
    return body
