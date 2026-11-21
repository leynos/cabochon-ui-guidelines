"""Annotate rendered figures and draw the production-height fixtures.

`annotate` embeds a metadata block and `data-figure-*` attributes so
`tools/check-figures.py` can compare a figure with `tools/figure-data.json`,
while `production_component`, `fig_prod_chrome` and `fig_prod_control` draw the
catalogue-height fixtures. `figuregen.cli` imports `annotate` and both fixtures.
"""

# The drawing primitives take geometry and style arguments positionally; see
# the matching ruff exemption for tools/figuregen in pyproject.toml.

from __future__ import annotations

import json
from html import escape

from figuregen.canvas import attrs, rect, svg_doc, txt
from figuregen.palette import F_MONO, HIGH, INK


def annotate(name: str, svg: str, specs: dict[str, dict[str, object]]) -> str:
    """Attach the figure's declared class, scale, profile and components.

    Parameters
    ----------
    name : str
        The figure name, which must have an entry in ``specs``.
    svg : str
        The rendered SVG document to annotate.
    specs : dict[str, dict[str, object]]
        The figure specifications loaded from ``tools/figure-data.json``.

    Returns
    -------
    str
        The annotated SVG document, with the ``data-figure-*`` attributes
        added to its first ``role="img"`` element and a ``<metadata>`` block
        inserted after its opening tag.

    Raises
    ------
    ValueError
        If ``name`` has no entry in ``specs``, or if that entry declares a
        class other than ``schematic``, ``editorial`` or ``production``.
    """
    spec = specs.get(name)
    if spec is None:
        raise ValueError(f"figure {name!r} has no entry in tools/figure-data.json")
    figure_class = str(spec["class"])
    if figure_class not in {"schematic", "editorial", "production"}:
        raise ValueError(f"figure {name!r} has unknown class {figure_class!r}")
    scale = spec["scale"]
    components = spec["components"]
    profile = str(spec["profile"])
    metadata: dict[str, object] = {
        "name": name,
        "class": figure_class,
        "scale": scale,
        "profile": profile,
        "components": components,
        "states": spec["states"],
    }
    if "size" in spec:
        metadata["size"] = spec["size"]
    if "bounds" in spec:
        metadata["bounds"] = spec["bounds"]
    payload = escape(json.dumps(metadata, sort_keys=True))
    scale_attr = "" if scale is None else f' data-figure-scale="{scale}"'
    attrs_text = (
        f' data-figure-class="{figure_class}"'
        f"{scale_attr}"
        f' data-figure-profile="{profile}"'
    )
    svg = svg.replace('role="img"', f'role="img"{attrs_text}', 1)
    marker = ">\n"
    index = svg.index(marker) + len(marker)
    return svg[:index] + f"  <metadata>{payload}</metadata>\n" + svg[index:]


def production_component(  # pylint: disable=too-many-arguments
    x: float, y: float, w: float, h: float, *, kind: str, label: str
) -> str:
    """Draw one component at its catalogue height.

    Parameters
    ----------
    x : float
        The component's left edge in logical units.
    y : float
        The component's top edge in logical units.
    w : float
        The component's width in logical units.
    h : float
        The component's height in logical units, which is also recorded as its
        ``data-height`` annotation.
    kind : str
        The catalogue component name, recorded as its ``data-component``
        annotation.
    label : str
        The text drawn in mono at 10 logical units, inset 8 from the left edge
        and centred vertically.

    Returns
    -------
    str
        The SVG fragment string for one component group.
    """
    attributes = attrs(data_component=kind, data_height=h)
    body = f"<g {attributes}>"
    body += rect(x, y, w, h, fill=HIGH, stroke=INK)
    body += txt(x + 8, y + h / 2 + 4, label, size=10, fill=INK, family=F_MONO)
    body += "</g>"
    return body


def fig_prod_chrome() -> str:
    """Draw the production chrome fixture at catalogue heights.

    Returns
    -------
    str
    """
    body = production_component(
        0, 0, 320, 31, kind="title_bar", label="TITLE BAR · 31 lu"
    )
    body += production_component(
        0, 31, 320, 29, kind="menu_bar", label="MENU BAR · 29 lu"
    )
    body += production_component(
        8, 68, 96, 30, kind="tool_button", label="TOOL · 30 lu"
    )
    body += production_component(
        0, 110, 320, 26, kind="status_line", label="STATUS LINE · 26 lu"
    )
    return svg_doc(
        320,
        140,
        "Production chrome fixture",
        "Title bar, menu bar, tool button and status line drawn at exact catalogue heights.",
        body=body,
    )


def fig_prod_control() -> str:
    """Draw the production control fixture at catalogue heights.

    Returns
    -------
    str
    """
    body = production_component(
        8, 8, 120, 36, kind="primary_action", label="PRIMARY · 36 lu"
    )
    body += production_component(
        144, 11, 80, 30, kind="tool_button", label="TOOL · 30 lu"
    )
    return svg_doc(
        320,
        80,
        "Production control fixture",
        "Primary action and tool button drawn at exact catalogue heights.",
        body=body,
    )
