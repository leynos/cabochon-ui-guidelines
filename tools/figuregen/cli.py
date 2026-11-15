"""Register each figure name with its builder and write the SVG files.

`main` loads the figure catalogue from `tools/figure-data.json`, checks its
registry against the catalogue's figure specifications, annotates every
rendered figure with the metadata declared there, and writes `figures/*.svg`.
`tools/make-figures.py` is the only caller.
"""

from __future__ import annotations

import os
import sys
import tempfile
import typing as typ
from pathlib import Path

from figuregen.figdata import DATA_PATH, OUT, ContractError, load_catalogue
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

if typ.TYPE_CHECKING:
    import collections.abc as cabc

# Builders that read state records outside the shared helpers take the whole
# catalogue; builders that only forward state tables take ``Catalogue.states``.
CATALOGUE_BUILDERS = frozenset({fig_embed, fig_state})
STATE_BUILDERS = frozenset({
    fig_accessibility,
    fig_draw,
    fig_formula,
    fig_hello,
    fig_inspector,
    fig_localization,
    fig_menus,
    fig_notes,
    fig_press,
    fig_project,
    fig_table,
    fig_toolbars,
    fig_window,
})


def _write_svg(destination: Path, text: str) -> None:
    """Write one complete SVG document through a unique scratch file.

    A unique scratch name keeps concurrent runs from replacing the same file
    twice, and the rename publishes the document atomically.

    Parameters
    ----------
    destination : Path
        The final SVG path, in an existing directory.
    text : str
        The complete SVG document, including its trailing newline.

    Returns
    -------
    None

    Notes
    -----
    The scratch file is created beside the destination, given mode ``0o644``
    and renamed over the destination. It is unlinked even when a write or the
    rename fails.
    """
    descriptor, scratch_name = tempfile.mkstemp(
        prefix=f".{destination.stem}.", suffix=".svg.tmp", dir=destination.parent
    )
    scratch = Path(scratch_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
        scratch.chmod(0o644)
        scratch.replace(destination)
    finally:
        scratch.unlink(missing_ok=True)


def main() -> int:
    """Write every figure and report the count.

    Returns
    -------
    int
        0 once every figure is written, or 1 when the figure contract cannot
        be loaded.
    """
    try:
        catalogue = load_catalogue(DATA_PATH)
    except ContractError as error:
        print(f"figure contract: {error}", file=sys.stderr)
        return 1
    OUT.mkdir(exist_ok=True)
    figures: dict[str, cabc.Callable[..., str]] = {
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
    missing = sorted(set(figures) - set(catalogue.figure_specs))
    extra = sorted(set(catalogue.figure_specs) - set(figures))
    if missing or extra:
        raise SystemExit(
            f"figure-data.json does not match the generator: "
            f"missing={missing} extra={extra}"
        )
    for name, draw in figures.items():
        if draw in CATALOGUE_BUILDERS:
            svg = draw(catalogue)
        elif draw in STATE_BUILDERS:
            svg = draw(catalogue.states)
        else:
            svg = draw()
        text = annotate(name, svg, catalogue.figure_specs) + "\n"
        _write_svg(OUT / f"{name}.svg", text)
    print(f"wrote {len(figures)} figures to {OUT}")
    return 0
