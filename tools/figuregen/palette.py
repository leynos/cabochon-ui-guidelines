"""Define the colour roles and font stacks that every figure shares.

The module holds plain string constants: paper and ink tones, the pine, oxide
and amber accents, their dark-theme counterparts, and the display, UI and
monospace font stacks. `figuregen.canvas` imports `F_UI`, `INK`, `PAPER` and
`SOFT`, and every `figuregen.figures.*` builder imports the roles it needs.
"""

from __future__ import annotations

PAPER = "#F1EEE5"

HIGH = "#FAF8F2"

INK = "#17201C"

SOFT = "#59625D"

PINE = "#173F35"

PINE2 = "#285E50"

TEAL = "#678E86"

TEAL_INK = "#456A62"

OXIDE = "#8A302F"

AMBER = "#B8792E"

AMBER_INK = "#8A5B24"

LINE = "#AAA99F"

DARK = "#121816"

DARK_SURFACE = "#1B2420"

DARK_TEXT = "#EDE9DE"

DARK_MUTED = "#A9B1AB"

DARK_PINE = "#7FB3A3"

DARK_OXIDE = "#D98C86"

DARK_AMBER = "#E0B36A"

WHITE = "#FFFFFF"

F_DISPLAY = "Georgia, 'DejaVu Serif', 'Times New Roman', serif"

F_UI = "'DejaVu Sans', 'Liberation Sans', Arial, sans-serif"

F_MONO = "'DejaVu Sans Mono', 'Liberation Mono', monospace"
