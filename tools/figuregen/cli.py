"""Register each figure name with its builder and write the SVG files.

`main` checks its registry against `FIGURE_SPECS` from `tools/figure-data.json`,
annotates every rendered figure with the metadata declared there, and writes
`figures/*.svg`. `tools/make-figures.py` is the only caller.
"""

from __future__ import annotations

from figuregen.figdata import FIGURE_SPECS, OUT
from figuregen.figures.accessibility import fig_accessibility
from figuregen.figures.command_palette import fig_command_palette
from figuregen.figures.controls import fig_controls
from figuregen.figures.cover import fig_cover
from figuregen.figures.dialog import fig_dialog
from figuregen.figures.document_centre import fig_document_centre
from figuregen.figures.draw import fig_draw
from figuregen.figures.ecosystem_map import fig_map
from figuregen.figures.embed import fig_embed
from figuregen.figures.first_batch import fig_first_batch
from figuregen.figures.focus import fig_focus
from figuregen.figures.formula import fig_formula
from figuregen.figures.hello import fig_hello
from figuregen.figures.icons import fig_icons
from figuregen.figures.inspector import fig_inspector
from figuregen.figures.live_state import fig_state
from figuregen.figures.localization import fig_localization
from figuregen.figures.material_palette import fig_palette
from figuregen.figures.menus import fig_menus
from figuregen.figures.motion import fig_motion
from figuregen.figures.notes import fig_notes
from figuregen.figures.output import fig_output
from figuregen.figures.panes import fig_panes
from figuregen.figures.planes import fig_planes
from figuregen.figures.press import fig_press
from figuregen.figures.principles import fig_principles
from figuregen.figures.project import fig_project
from figuregen.figures.small_world import fig_small_world
from figuregen.figures.spacing import fig_spacing
from figuregen.figures.table import fig_table
from figuregen.figures.toolbars import fig_toolbars
from figuregen.figures.type_scale import fig_type
from figuregen.figures.window import fig_window
from figuregen.production import annotate, fig_prod_chrome, fig_prod_control


def main() -> int:
    """Write every figure and report the count."""
    OUT.mkdir(exist_ok=True)
    figures = {
        "fig-00-cover": fig_cover,
        "fig-01-map": fig_map,
        "fig-02-small-world": fig_small_world,
        "fig-03-first-batch": fig_first_batch,
        "fig-04-principles": fig_principles,
        "fig-05-document-centre": fig_document_centre,
        "fig-06-state": fig_state,
        "fig-07-palette": fig_palette,
        "fig-08-type": fig_type,
        "fig-09-spacing": fig_spacing,
        "fig-10-planes": fig_planes,
        "fig-11-icons": fig_icons,
        "fig-12-motion": fig_motion,
        "fig-13-window": fig_window,
        "fig-14-menus": fig_menus,
        "fig-15-toolbars": fig_toolbars,
        "fig-16-panes": fig_panes,
        "fig-17-inspector": fig_inspector,
        "fig-18-controls": fig_controls,
        "fig-19-dialog": fig_dialog,
        "fig-20-focus": fig_focus,
        "fig-21-command-palette": fig_command_palette,
        "fig-22-notes": fig_notes,
        "fig-23-draw": fig_draw,
        "fig-24-press": fig_press,
        "fig-25-table": fig_table,
        "fig-26-formula": fig_formula,
        "fig-27-hello-window": fig_hello,
        "fig-28-project": fig_project,
        "fig-29-embed": fig_embed,
        "fig-30-output": fig_output,
        "fig-31-localization": fig_localization,
        "fig-32-accessibility": fig_accessibility,
        "fig-prod-chrome": fig_prod_chrome,
        "fig-prod-control": fig_prod_control,
    }
    missing = sorted(set(figures) - set(FIGURE_SPECS))
    extra = sorted(set(FIGURE_SPECS) - set(figures))
    if missing or extra:
        raise SystemExit(
            f"figure-data.json does not match the generator: "
            f"missing={missing} extra={extra}"
        )
    for name, draw in figures.items():
        (OUT / f"{name}.svg").write_text(
            annotate(name, draw()) + "\n", encoding="utf-8"
        )
    print(f"wrote {len(figures)} figures to {OUT}")
    return 0
