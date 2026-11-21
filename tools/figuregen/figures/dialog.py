"""Draw the destructive confirmation dialog figure.

The dialog asks whether to replace an embedded table, naming the object and
offering a way out. The exported `fig_dialog` function returns the SVG string,
drawn from the shared `figuregen.palette` colours. `figuregen.cli` calls it to
write `fig-19-dialog.svg` under `figures/`.
"""

from __future__ import annotations

from figuregen.canvas import para, rect, svg_doc, txt
from figuregen.ornaments import title_block
from figuregen.palette import F_MONO, HIGH, INK, LINE, OXIDE, PAPER, SOFT, WHITE
from figuregen.widgets import button, checkbox, titlebar


def fig_dialog() -> str:
    """Draw the destructive confirmation dialog for replacing a table.

    Returns
    -------
    str
    """
    body = title_block(
        64,
        70,
        "Dialogs interrupt with a reason",
        "A dialog asks one question, names the object and offers a way out. It is not a place to arrange the application.",
    )
    # Background.
    body += rect(64, 150, 1072, 540, fill=PAPER, stroke=LINE)
    body += rect(64, 150, 1072, 540, fill=INK, stroke=None, opacity=0.18)
    body += txt(
        90, 184, "Document (inert while the dialog is open)", size=11, fill=WHITE
    )
    # Dialog.
    x, y, w, h = 330, 210, 540, 340
    body += rect(x + 8, y + 8, w, h, fill="#17201C30", stroke=None)
    body += rect(x, y, w, h, fill=HIGH, stroke=INK)
    body += titlebar(x, y, w, "Replace the embedded table?")
    body += para(
        x + 24,
        y + 62,
        w - 48,
        "The note currently embeds “Generation mix” as a live table. Replacing it will remove the embed, not delete the table object.",
        size=12,
        leading=19,
    )
    body += rect(x + 24, y + 130, w - 48, 52, fill=PAPER, stroke=LINE)
    body += txt(x + 38, y + 152, "Generation mix", size=12, weight="bold")
    body += txt(
        x + 38, y + 170, "Table · r17 · obj:8f3a", size=10, fill=SOFT, family=F_MONO
    )
    body += checkbox(x + 24, y + 214, "Keep a copy in this note", checked=False)
    body += txt(
        x + 24,
        y + 244,
        "This cannot be undone after the note is saved.",
        size=10,
        fill=OXIDE,
    )
    body += button(x + w - 300, y + h - 64, 120, "Cancel", height=36)
    body += button(x + w - 164, y + h - 64, 140, "Replace", destructive=True, height=36)
    # Focus ring on Cancel.
    body += rect(x + w - 306, y + h - 70, 132, 48, fill="none", stroke=OXIDE, sw=3)
    body += txt(
        x + w - 300, y + h - 82, "default focus", size=10, fill=OXIDE, family=F_MONO
    )
    # Annotations.
    nx = 64
    body += txt(
        nx,
        726,
        "One question per dialog. The destructive verb names the object. Cancel is the default for destruction. Esc cancels. No dialog opens another dialog.",
        size=11,
        fill=SOFT,
    )
    return svg_doc(
        1200,
        760,
        "Destructive confirmation dialog",
        "A modal dialog asking whether to replace an embedded table, with object identity, a keep-a-copy choice and a destructive Replace button.",
        body=body,
    )
