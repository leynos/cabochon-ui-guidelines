"""Draw the window furniture and form controls that the figures compose.

`window_shell` combines `titlebar`, `menu_strip` and `status_bar`, and the
package also exports `pane_head`, `field`, `button`, `checkbox`, `radio` and
`inspector_row`. Most `figuregen.figures.*` builders import it, and it takes
state chips from `figuregen.ornaments`.
"""

from __future__ import annotations

from figuregen.widgets.chrome import menu_strip, status_bar, titlebar, window_shell
from figuregen.widgets.controls import button, checkbox, field, radio
from figuregen.widgets.rows import inspector_row, pane_head

__all__ = [
    "button",
    "checkbox",
    "field",
    "inspector_row",
    "menu_strip",
    "pane_head",
    "radio",
    "status_bar",
    "titlebar",
    "window_shell",
]
