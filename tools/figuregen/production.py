"""Figure generator module: production."""

# The drawing primitives take geometry and style arguments positionally; see
# the matching ruff exemption for tools/figuregen in pyproject.toml.
# pylint: disable=too-many-arguments

from __future__ import annotations

import json
from html import escape

from figuregen.canvas import attrs, rect, svg_doc, txt
from figuregen.figdata import FIGURE_SPECS
from figuregen.palette import F_MONO, HIGH, INK


def annotate(name: str, svg: str) -> str:
    """Attach the figure's declared class, scale, profile and components.

    The annotation is machine-readable so that a checker can compare it with
    the rendered geometry instead of trusting a caption.
    """
    spec = FIGURE_SPECS.get(name)
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


def production_component(
    x: float, y: float, w: float, h: float, *, kind: str, label: str
) -> str:
    """Draw one component at its catalogue height for the production fixtures.

    The group carries its identity and measured height, but the checker derives
    the rendered bounds from the geometry and transforms rather than trusting
    the annotation.
    """
    attributes = attrs(data_component=kind, data_height=h)
    body = f"<g {attributes}>"
    body += rect(x, y, w, h, fill=HIGH, stroke=INK)
    body += txt(x + 8, y + h / 2 + 4, label, size=10, fill=INK, family=F_MONO)
    body += "</g>"
    return body


def fig_prod_chrome() -> str:
    """Draw the production chrome fixture at catalogue heights."""
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
    """Draw the production control fixture at catalogue heights."""
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
