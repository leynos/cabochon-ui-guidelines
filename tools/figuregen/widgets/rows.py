"""Draw pane headers and inspector rows.

The `figuregen.widgets` package re-exports these functions for the
`figuregen.figures.*` builders that draw panes and inspectors.
"""

# The drawing primitives take geometry and style arguments positionally; see
# the matching ruff exemption for tools/figuregen in pyproject.toml.

from __future__ import annotations

from figuregen.canvas import line, rect, txt
from figuregen.palette import F_MONO, INK, LINE, PAPER, SOFT


def pane_head(  # pylint: disable=too-many-arguments
    x: float, y: float, w: float, title: str, *, right: str | None = None
) -> str:
    """Draw a pane header with an optional right-hand label.

    The header is 28 logical units high and carries a bottom edge line.

    Parameters
    ----------
    x : float
        The header's left edge in logical units.
    y : float
        The header's top edge in logical units.
    w : float
        The header's width in logical units.
    title : str
        The pane title, upper-cased and drawn bold at 10 logical units.
    right : str | None
        The label drawn at the right edge in 10 logical-unit text, or
        ``None``, the default, to leave that side empty.

    Returns
    -------
    str
        The SVG fragment string for the pane header.
    """
    body = rect(x, y, w, 28, fill=PAPER, stroke=None)
    body += line(x, y + 27.5, x + w, y + 27.5, stroke=LINE)
    body += txt(
        x + 10, y + 18, title.upper(), size=10, fill=SOFT, weight="bold", spacing=0.8
    )
    if right:
        body += txt(x + w - 10, y + 18, right, size=10, fill=SOFT, anchor="end")
    return body


def inspector_row(  # pylint: disable=too-many-arguments
    x: float, y: float, w: float, label: str, *, value: str, value_colour: str = INK
) -> str:
    """Draw one inspector row of label and value.

    Parameters
    ----------
    x : float
        The row's left edge in logical units.
    y : float
        The text baseline in logical units; the rule is drawn 8 logical units
        below it.
    w : float
        The row's width in logical units.
    label : str
        The label, upper-cased and drawn at 10 logical units in mono.
    value : str
        The value, drawn at 11 logical units and anchored to the right edge.
    value_colour : str
        The colour of the value; the default is the ink colour.

    Returns
    -------
    str
        The SVG fragment string for the inspector row.
    """
    body = txt(x, y, label.upper(), size=10, fill=SOFT, family=F_MONO, spacing=0.5)
    body += txt(x + w, y, value, size=11, fill=value_colour, anchor="end")
    body += line(x, y + 8, x + w, y + 8, stroke=LINE, sw=0.5)
    return body
