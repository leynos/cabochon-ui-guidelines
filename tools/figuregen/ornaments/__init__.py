"""Draw the shared page ornaments, state chips and miniature document views.

`title_block`, `kicker` and `frame` set the page furniture, `state_chip` pairs
each declared state with a distinct non-colour mark, and `mini_note`,
`mini_table`, `mini_page` and `mini_canvas` draw the document previews. Nearly
every `figuregen.figures.*` builder imports the module, as does
`figuregen.widgets`.
"""

from __future__ import annotations

from figuregen.ornaments.blocks import frame, kicker, title_block
from figuregen.ornaments.chips import chip, state_chip
from figuregen.ornaments.marks import mark_group, state_mark
from figuregen.ornaments.miniatures import (
    mini_canvas,
    mini_note,
    mini_page,
    mini_table,
)

__all__ = [
    "chip",
    "frame",
    "kicker",
    "mark_group",
    "mini_canvas",
    "mini_note",
    "mini_page",
    "mini_table",
    "state_chip",
    "state_mark",
    "title_block",
]
