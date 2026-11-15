"""Figure generator module: figures.hello."""

from __future__ import annotations

from figuregen.canvas import line, para, rect, svg_doc, txt
from figuregen.ornaments import title_block
from figuregen.palette import F_DISPLAY, F_MONO, HIGH, INK, LINE, OXIDE, PINE2, SOFT
from figuregen.widgets import button, window_shell


def fig_hello() -> str:
    """Draw the hello-window application and its export bundle."""
    body = title_block(
        64,
        70,
        "hello-window",
        "The smallest application that proves the contract. It is small on purpose, and complete on purpose.",
    )
    x, y, w, h = 64, 158, 470, 300
    body += window_shell(
        x,
        y,
        w,
        h,
        title="hello-window",
        menu=["File", "View", "Help"],
        status="1 document · exported 14:02",
        state="Current",
    )
    body += txt(
        x + 28, y + 108, "Hello, Cabochon.", size=28, family=F_DISPLAY, style="italic"
    )
    body += para(
        x + 28,
        y + 138,
        w - 56,
        "One window, three menus, one document and one command. Everything the environment requires is present, and nothing else is.",
        size=11,
        leading=16,
    )
    body += button(x + 28, y + 206, 122, "Export", primary=True, height=34)
    body += button(x + 162, y + 206, 112, "About", height=34)
    body += txt(
        x + 28,
        y + 262,
        "Ctrl+Q quits · F1 opens About",
        size=10,
        fill=SOFT,
        family=F_MONO,
    )
    # Artefacts.
    ax = 590
    body += txt(
        ax,
        190,
        "EXPORT BUNDLE",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    artefacts = [
        "content.pdf",
        "content-print.pdf",
        "content.png",
        "thumbnail.png",
        "accessibility.json",
        "clipboard/",
        "hit-map.json",
        "export.json",
    ]
    for index, name in enumerate(artefacts):
        col, row = index % 2, index // 2
        bx = ax + col * 270
        by = 214 + row * 44
        body += rect(bx, by, 250, 32, fill=HIGH, stroke=LINE)
        body += txt(bx + 12, by + 21, name, size=11, fill=INK, family=F_MONO)
        body += txt(
            bx + 238, by + 21, "✓", size=12, fill=PINE2, anchor="end", weight="bold"
        )
    body += para(
        ax,
        420,
        520,
        "Each artefact comes from the same Lapidary scene. Geometry, text placement, clipping and metadata agree within the declared tolerances, and the accessibility and hit-map outputs describe the same objects that were drawn.",
        size=11,
        leading=17,
    )
    body += txt(
        ax,
        520,
        "The reference application is not a demo.",
        size=12,
        fill=OXIDE,
        family=F_DISPLAY,
        style="italic",
    )
    body += line(64, 560, 1136, 560, stroke=LINE)
    body += txt(
        64,
        592,
        "WHAT IT PROVES",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    proofs = [
        ("Resources", "Menus, strings and shortcuts load from Escutcheon."),
        ("Scene", "One Lapidary scene renders every target."),
        ("Output", "Burin writes display, PDF, raster and metadata."),
        ("Access", "Roles, names and focus order are extractable."),
        ("Locale", "en-XA and ar-XB run without layout breaks."),
    ]
    for index, (name, detail) in enumerate(proofs):
        px = 64 + index * 216
        body += txt(
            px, 622, name.upper(), size=10, fill=PINE2, family=F_MONO, weight="bold"
        )
        body += para(px, 644, 190, detail, size=10, leading=15)
    return svg_doc(
        1200,
        760,
        "hello-window reference application",
        "A small hello-window application with File, View and Help menus, an Export button and the complete export bundle, plus the contracts it proves.",
        body=body,
    )
