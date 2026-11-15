"""Check the production fixtures against the component catalogue.

The `check_production_geometry` function derives each component's rendered
height and bounds from the drawn primitives and compares them with the
catalogue in `tools/figure-data.json`. `figurecheck.checks` calls it for every
production figure.
"""

from __future__ import annotations

import math
import typing as typ
from itertools import starmap

from figurecheck.contract import DATA, NUMBER_RE, GeometryError
from figurecheck.geometry import hidden_reason, parse_number, rendered_bbox

if typ.TYPE_CHECKING:
    from xml.etree import ElementTree

TOLERANCE = 0.01
CANVAS_FIELDS = ("x", "y", "width", "height")


class _Context(typ.NamedTuple):
    """The catalogue and report that the component checks share."""

    name: str
    root: ElementTree.Element
    parents: dict[ElementTree.Element, ElementTree.Element]
    catalogue: dict[str, dict[str, float]]
    bounds: dict[str, object]
    errors: list[str]


def _agrees(actual: float, expected: float) -> bool:
    """Return whether two measurements agree within the tolerance."""
    return math.isclose(actual, expected, abs_tol=TOLERANCE)


def _declared(value: object, label: str) -> float:
    """Parse a measurement declared by the figure data."""
    return parse_number(str(value), label)


def _check_canvas(
    name: str, root: ElementTree.Element, spec: dict[str, object], errors: list[str]
) -> bool:
    """Check the declared canvas against the document, returning its validity."""
    size = spec.get("size")
    if not isinstance(size, dict) or not isinstance(spec.get("bounds"), dict):
        errors.append(f"{name}: production figure lacks size or bounds")
        return False
    width = parse_number(root.get("width"), "svg width")
    height = parse_number(root.get("height"), "svg height")
    if not (
        _agrees(width, _declared(size["width"], "declared width"))
        and _agrees(height, _declared(size["height"], "declared height"))
    ):
        errors.append(
            f"{name}: canvas {width}x{height} disagrees with declared "
            f"{size['width']}x{size['height']}"
        )
    box = [float(item) for item in NUMBER_RE.findall(root.get("viewBox", ""))]
    if len(box) != 4 or not all(
        starmap(_agrees, zip(box[2:], [width, height], strict=True))
    ):
        errors.append(f"{name}: viewBox disagrees with the declared canvas")
    return True


def _check_height(
    context: _Context,
    component: str,
    group: ElementTree.Element,
    rendered: float,
) -> None:
    """Check a component's rendered height against the catalogue."""
    expected = context.catalogue[component]["height"]
    if not _agrees(rendered, expected):
        context.errors.append(
            f"{context.name}: {component!r} rendered height {rendered:.2f} "
            f"disagrees with catalogue {expected:.2f}"
        )
    annotation = group.get("data-height")
    if annotation is None:
        context.errors.append(
            f"{context.name}: component {component!r} has no measured height"
        )
    elif not _agrees(parse_number(annotation, "data-height"), rendered):
        context.errors.append(
            f"{context.name}: {component!r} annotation says {annotation}, geometry "
            f"renders {rendered:.2f}"
        )


def _check_bounds(context: _Context, component: str, box: tuple[float, ...]) -> None:
    """Check a component's rendered box against its declared bounds."""
    declared = context.bounds.get(component)
    if not isinstance(declared, dict):
        context.errors.append(
            f"{context.name}: component {component!r} has no declared bounds"
        )
        return
    actual = {
        "x": box[0],
        "y": box[1],
        "width": box[2] - box[0],
        "height": box[3] - box[1],
    }
    for field in CANVAS_FIELDS:
        if not _agrees(actual[field], _declared(declared[field], field)):
            context.errors.append(
                f"{context.name}: {component!r} rendered {field} "
                f"{actual[field]:.2f} disagrees with declared {declared[field]}"
            )


def _check_component(
    context: _Context, component: str, groups: list[ElementTree.Element]
) -> None:
    """Check that a component is drawn once and as the catalogue says."""
    if component not in context.catalogue:
        context.errors.append(f"{context.name}: unknown component {component!r}")
        return
    if not groups:
        context.errors.append(
            f"{context.name}: no rendered geometry for {component!r}"
        )
        return
    if len(groups) != 1:
        context.errors.append(
            f"{context.name}: component {component!r} is rendered {len(groups)} times"
        )
    group = groups[0]
    reason = hidden_reason(group, context.parents)
    if reason is not None:
        context.errors.append(
            f"{context.name}: component {component!r} is not visible ({reason})"
        )
        return
    label = f"component {component!r}"
    try:
        box = rendered_bbox(group, context.parents, label)
    except GeometryError as exc:
        context.errors.append(f"{context.name}: {label} is invalid: {exc}")
        return
    _check_height(context, component, group, box[3] - box[1])
    _check_bounds(context, component, box)


def _rendered_components(
    root: ElementTree.Element,
) -> dict[str, list[ElementTree.Element]]:
    """Group the rendered elements by the component they declare."""
    rendered: dict[str, list[ElementTree.Element]] = {}
    for element in root.iter():
        component = element.get("data-component")
        if component is not None:
            rendered.setdefault(component, []).append(element)
    return rendered


def _check_figure_class(
    name: str, spec: dict[str, object], errors: list[str]
) -> bool:
    """Return whether the figure declares itself to be a production fixture."""
    if spec["class"] == "production":
        return True
    if spec.get("components"):
        errors.append(f"{name}: non-production figure declares components")
    return False


def _check_components(context: _Context, declared: list[str]) -> None:
    """Check every declared component and reject undeclared ones."""
    rendered = _rendered_components(context.root)
    context.errors.extend(
        f"{context.name}: component {component!r} is drawn but not declared"
        for component in rendered
        if component not in declared
    )
    for component in declared:
        _check_component(context, component, rendered.get(component, []))
    context.errors.extend(
        f"{context.name}: bounds name undeclared component {component!r}"
        for component in context.bounds
        if component not in declared
    )


def check_production_geometry(
    name: str, root: ElementTree.Element, spec: dict[str, object]
) -> list[str]:
    """Check the production fixtures against the catalogue."""
    errors: list[str] = []
    if not _check_figure_class(name, spec, errors):
        return errors
    if not math.isclose(_declared(spec["scale"] or 0, "figure scale"), 1.0):
        errors.append(f"{name}: production figure must declare scale 1.0")
    if not _check_canvas(name, root, spec, errors):
        return errors

    raw_components = spec.get("components")
    if not isinstance(raw_components, list):
        errors.append(f"{name}: production figure declares no component list")
        return errors
    declared = [str(component) for component in raw_components]
    if not declared:
        errors.append(f"{name}: production figure declares no components")
    bounds = spec["bounds"]
    context = _Context(
        name=name,
        root=root,
        parents={child: parent for parent in root.iter() for child in parent},
        catalogue=DATA["component_catalogue"],
        bounds=bounds if isinstance(bounds, dict) else {},
        errors=errors,
    )
    _check_components(context, declared)
    return errors
