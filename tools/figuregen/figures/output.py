"""Figure generator module: figures.output."""

from __future__ import annotations

from figuregen.canvas import line, rect, svg_doc, txt
from figuregen.ornaments import title_block
from figuregen.palette import DARK_MUTED, F_MONO, HIGH, INK, LINE, PINE, SOFT, WHITE


def fig_output() -> str:
    """Draw the scene-to-output workstations."""
    body = title_block(
        64,
        70,
        "One scene, every output",
        "The scene is the contract. Display, paper and metadata are workstations that read it.",
    )
    cx, cy = 600, 380
    body += rect(cx - 150, cy - 64, 300, 128, fill=PINE, stroke=INK, sw=2)
    body += txt(
        cx,
        cy - 20,
        "LAPIDARY SCENE",
        size=13,
        fill=WHITE,
        family=F_MONO,
        weight="bold",
        anchor="middle",
        spacing=0.8,
    )
    body += txt(
        cx,
        cy + 4,
        "geometry · text · clipping",
        size=10,
        fill=DARK_MUTED,
        family=F_MONO,
        anchor="middle",
    )
    body += txt(
        cx,
        cy + 24,
        "transforms · hit regions",
        size=10,
        fill=DARK_MUTED,
        family=F_MONO,
        anchor="middle",
    )
    body += txt(
        cx,
        cy + 44,
        "physical units · intent",
        size=10,
        fill=DARK_MUTED,
        family=F_MONO,
        anchor="middle",
    )
    targets = [
        ("Display", "interactive", 64, 200),
        ("PDF", "vector pages", 64, 360),
        ("Print", "printer-bound", 64, 520),
        ("Thumbnail", "small raster", 330, 660),
        ("Raster", "PNG export", 530, 660),
        ("Clipboard", "geometry + text", 730, 660),
        ("Accessibility", "roles + names", 930, 520),
        ("Hit map", "regions + ids", 930, 360),
        ("Manifest", "export.json", 930, 200),
    ]
    for _name, _detail, tx, ty in targets:
        tw, th = 206, 64
        body += line(cx, cy, tx + tw / 2, ty + th / 2, stroke=LINE, sw=1.2)
    for name, detail, tx, ty in targets:
        tw, th = 206, 64
        body += rect(tx, ty, tw, th, fill=HIGH, stroke=INK)
        body += txt(tx + 12, ty + 25, name, size=12, weight="bold")
        body += txt(tx + 12, ty + 44, detail, size=10, fill=SOFT, family=F_MONO)
    body += txt(
        64,
        752,
        "Parity is measured: geometry, text placement, clipping and metadata, within declared tolerances. A target that cannot agree fails the build.",
        size=11,
        fill=SOFT,
    )
    return svg_doc(
        1200,
        780,
        "Scene to output workstations",
        "A central Lapidary scene connected to display, PDF, print, thumbnail, raster, clipboard, accessibility, hit-map and manifest outputs.",
        body=body,
    )
