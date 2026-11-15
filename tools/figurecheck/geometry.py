"""Measure the geometry that a constrained SVG subset renders.

The module provides `parse_transform`, `path_bbox` and `rendered_bbox`, which
compute transformed bounds for the primitives the checker accepts. The
annotation, production, state and mark checks import these helpers, using the
tags and matrices from `figurecheck.contract`.
"""

from __future__ import annotations

import math
import typing as typ

from figurecheck.contract import (
    GEOMETRY_TAGS,
    IDENTITY,
    NUMBER_RE,
    PATH_TOKEN_RE,
    SVG_NS,
    TRANSFORM_RE,
    BBox,
    GeometryError,
)

if typ.TYPE_CHECKING:
    from xml.etree import ElementTree


def local_name(element: ElementTree.Element) -> str:
    """Strip an XML namespace from a tag name."""
    return element.tag.replace(SVG_NS, "")


def parse_number(value: str | None, label: str) -> float:
    """Parse a length attribute, returning zero for missing values."""
    try:
        return float(value or "")
    except (TypeError, ValueError) as exc:
        raise GeometryError(f"{label} is not a number: {value!r}") from exc


def compose(outer: tuple[float, ...], inner: tuple[float, ...]) -> tuple[float, ...]:
    """Return the matrix that applies ``inner`` and then ``outer``."""
    return (
        outer[0] * inner[0] + outer[2] * inner[1],
        outer[1] * inner[0] + outer[3] * inner[1],
        outer[0] * inner[2] + outer[2] * inner[3],
        outer[1] * inner[2] + outer[3] * inner[3],
        outer[0] * inner[4] + outer[2] * inner[5] + outer[4],
        outer[1] * inner[4] + outer[3] * inner[5] + outer[5],
    )


def _translate(numbers: list[float]) -> tuple[float, ...]:
    """Return the matrix of a ``translate`` operation."""
    return (
        1.0,
        0.0,
        0.0,
        1.0,
        numbers[0],
        numbers[1] if len(numbers) == 2 else 0.0,
    )


def _scale(numbers: list[float]) -> tuple[float, ...]:
    """Return the matrix of a ``scale`` operation."""
    return (
        numbers[0],
        0.0,
        0.0,
        numbers[1] if len(numbers) == 2 else numbers[0],
        0.0,
        0.0,
    )


def _rotate(numbers: list[float]) -> tuple[float, ...]:
    """Return the matrix of a ``rotate`` operation, about a point if given."""
    angle = math.radians(numbers[0])
    cosine, sine = math.cos(angle), math.sin(angle)
    local = (cosine, sine, -sine, cosine, 0.0, 0.0)
    if len(numbers) != 3:
        return local
    cx, cy = numbers[1], numbers[2]
    return compose(
        compose((1.0, 0.0, 0.0, 1.0, cx, cy), local),
        (1.0, 0.0, 0.0, 1.0, -cx, -cy),
    )


def parse_transform(value: str) -> tuple[float, ...]:
    """Parse an SVG transform list into matrix operations."""
    matrix = IDENTITY
    for match in TRANSFORM_RE.finditer(value):
        operation = match.group(1).lower()
        numbers = [float(item) for item in NUMBER_RE.findall(match.group(2))]
        if operation == "translate" and len(numbers) in {1, 2}:
            matrix = compose(matrix, _translate(numbers))
        elif operation == "scale" and len(numbers) in {1, 2}:
            matrix = compose(matrix, _scale(numbers))
        elif operation == "rotate" and len(numbers) in {1, 3}:
            matrix = compose(matrix, _rotate(numbers))
        elif operation == "matrix" and len(numbers) == 6:
            matrix = compose(matrix, tuple(numbers))
        else:
            raise GeometryError(f"unsupported transform {match.group(0)!r}")
    remainder = TRANSFORM_RE.sub("", value).strip(" \t\r\n,")
    if remainder:
        raise GeometryError(f"unsupported transform syntax {value!r}")
    return matrix


def apply_matrix(matrix: tuple[float, ...], x: float, y: float) -> tuple[float, float]:
    """Apply an affine matrix to a point."""
    a, b, c, d, e, f = matrix
    return a * x + c * y + e, b * x + d * y + f


def transform_bbox(box: BBox, matrix: tuple[float, ...]) -> BBox:
    """Transform a bounding box through an affine matrix."""
    min_x, min_y, max_x, max_y = box
    corners = [
        apply_matrix(matrix, x, y) for x in (min_x, max_x) for y in (min_y, max_y)
    ]
    xs = [point[0] for point in corners]
    ys = [point[1] for point in corners]
    return min(xs), min(ys), max(xs), max(ys)


def merge_bbox(first: BBox | None, second: BBox) -> BBox:
    """Merge two bounding boxes, ignoring empty ones."""
    if first is None:
        return second
    return (
        min(first[0], second[0]),
        min(first[1], second[1]),
        max(first[2], second[2]),
        max(first[3], second[3]),
    )


def _consume_arc(
    tokens: list[str], index: int, radius: float
) -> tuple[float, tuple[float, float], int]:
    """Read one arc's radii and endpoint, widening the radius it spans."""
    if index + 7 > len(tokens):
        raise GeometryError("truncated arc in path")
    radius = max(radius, float(tokens[index]), float(tokens[index + 1]))
    point = (float(tokens[index + 5]), float(tokens[index + 6]))
    return radius, point, index + 7


def _consume_point(
    tokens: list[str], index: int
) -> tuple[tuple[float, float], int]:
    """Read one coordinate pair from path tokens."""
    if index + 2 > len(tokens):
        raise GeometryError("truncated point in path")
    return (float(tokens[index]), float(tokens[index + 1])), index + 2


def path_bbox(data: str) -> BBox:
    """Compute the bounding box of an SVG path data string."""
    tokens = PATH_TOKEN_RE.findall(data)
    points: list[tuple[float, float]] = []
    radius = 0.0
    command: str | None = None
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token.isalpha():
            command = token
            index += 1
            continue
        if command not in {"M", "L", "A"}:
            raise GeometryError(f"unsupported path command {command!r}")
        if command == "A":
            radius, point, index = _consume_arc(tokens, index, radius)
        else:
            point, index = _consume_point(tokens, index)
        points.append(point)
    if not points:
        raise GeometryError("path draws no points")
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return (
        min(xs) - radius,
        min(ys) - radius,
        max(xs) + radius,
        max(ys) + radius,
    )


def _rect_bbox(element: ElementTree.Element) -> BBox:
    """Compute the bounding box of a rectangle element."""
    x = parse_number(element.get("x", "0"), "rect x")
    y = parse_number(element.get("y", "0"), "rect y")
    width = parse_number(element.get("width"), "rect width")
    height = parse_number(element.get("height"), "rect height")
    if width <= 0 or height <= 0:
        raise GeometryError("rectangle has zero or negative size")
    return x, y, x + width, y + height


def _circle_bbox(element: ElementTree.Element) -> BBox:
    """Compute the bounding box of a circle element."""
    cx = parse_number(element.get("cx", "0"), "circle cx")
    cy = parse_number(element.get("cy", "0"), "circle cy")
    radius = parse_number(element.get("r"), "circle r")
    if radius <= 0:
        raise GeometryError("zero radius")
    return cx - radius, cy - radius, cx + radius, cy + radius


def _ellipse_bbox(element: ElementTree.Element) -> BBox:
    """Compute the bounding box of an ellipse element."""
    cx = parse_number(element.get("cx", "0"), "ellipse cx")
    cy = parse_number(element.get("cy", "0"), "ellipse cy")
    rx = parse_number(element.get("rx"), "ellipse rx")
    ry = parse_number(element.get("ry"), "ellipse ry")
    if rx <= 0 or ry <= 0:
        raise GeometryError("ellipse has zero radius")
    return cx - rx, cy - ry, cx + rx, cy + ry


def _line_bbox(element: ElementTree.Element) -> BBox:
    """Compute the bounding box of a line element."""
    x1 = parse_number(element.get("x1", "0"), "line x1")
    y1 = parse_number(element.get("y1", "0"), "line y1")
    x2 = parse_number(element.get("x2", "0"), "line x2")
    y2 = parse_number(element.get("y2", "0"), "line y2")
    return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)


def _points_bbox(element: ElementTree.Element) -> BBox:
    """Compute the bounding box of a polyline or polygon element."""
    numbers = [float(item) for item in NUMBER_RE.findall(element.get("points", ""))]
    if len(numbers) < 4:
        raise GeometryError("polyline has fewer than two points")
    xs = numbers[0::2]
    ys = numbers[1::2]
    return min(xs), min(ys), max(xs), max(ys)


def _path_bbox(element: ElementTree.Element) -> BBox:
    """Compute the bounding box of a path element."""
    return path_bbox(element.get("d", ""))


_PRIMITIVES = {
    "rect": _rect_bbox,
    "circle": _circle_bbox,
    "ellipse": _ellipse_bbox,
    "line": _line_bbox,
    "polyline": _points_bbox,
    "polygon": _points_bbox,
    "path": _path_bbox,
}


def primitive_bbox(element: ElementTree.Element) -> BBox:
    """Compute the bounding box a primitive element paints."""
    builder = _PRIMITIVES.get(local_name(element))
    if builder is None:
        raise GeometryError(f"unsupported primitive {local_name(element)!r}")
    return builder(element)


def hidden_reason(
    element: ElementTree.Element,
    parents: dict[ElementTree.Element, ElementTree.Element],
) -> str | None:
    """Return why an element is not painted, or ``None`` if it is."""
    chain = _ancestry(element, parents)
    for node in reversed(chain):
        if node.get("display") == "none":
            return "display none"
        if node.get("visibility") in {"hidden", "collapse"}:
            return "visibility hidden"
        opacity = node.get("opacity")
        if opacity is not None and parse_number(opacity, "opacity") <= 0:
            return "zero opacity"
    return None


def _ancestry(
    element: ElementTree.Element,
    parents: dict[ElementTree.Element, ElementTree.Element],
) -> list[ElementTree.Element]:
    """Return an element and its ancestors, starting with the element."""
    chain: list[ElementTree.Element] = []
    node: ElementTree.Element | None = element
    while node is not None:
        chain.append(node)
        node = parents.get(node)
    return chain


def clip_used(
    element: ElementTree.Element,
    parents: dict[ElementTree.Element, ElementTree.Element],
) -> bool:
    """Return whether a clip path would crop the element."""
    return any(
        node.get("clip-path") or node.get("mask")
        for node in _ancestry(element, parents)
    )


def paint_visible(element: ElementTree.Element) -> bool:
    """Return whether an element paints anything visible."""
    fill = (element.get("fill") or "").lower()
    stroke = (element.get("stroke") or "").lower()
    fill_opacity = parse_number(element.get("fill-opacity", "1"), "fill-opacity")
    stroke_opacity = parse_number(element.get("stroke-opacity", "1"), "stroke-opacity")
    has_fill = fill not in {"", "none", "transparent"} and fill_opacity > 0
    has_stroke = stroke not in {"", "none", "transparent"} and stroke_opacity > 0
    return has_fill or has_stroke


def element_matrix(
    element: ElementTree.Element,
    parents: dict[ElementTree.Element, ElementTree.Element],
) -> tuple[float, ...]:
    """Compose the transform chain that applies to an element."""
    matrix = IDENTITY
    for node in reversed(_ancestry(element, parents)):
        value = node.get("transform")
        if value:
            matrix = compose(matrix, parse_transform(value))
    return matrix


def rendered_bbox(
    group: ElementTree.Element,
    parents: dict[ElementTree.Element, ElementTree.Element],
    label: str,
) -> BBox:
    """Compute the bounding box an element renders within the view box."""
    box: BBox | None = None
    for element in group.iter():
        if local_name(element) not in GEOMETRY_TAGS:
            continue
        reason = hidden_reason(element, parents)
        if reason is not None:
            raise GeometryError(f"{label} is not visible ({reason})")
        if not paint_visible(element):
            raise GeometryError(f"{label} draws nothing visible")
        local_box = primitive_bbox(element)
        box = merge_bbox(
            box, transform_bbox(local_box, element_matrix(element, parents))
        )
    if box is None:
        raise GeometryError(f"{label} draws no geometry")
    if box[2] - box[0] <= 0 and box[3] - box[1] <= 0:
        raise GeometryError(f"{label} has zero visible area")
    return box


def intersect_area(first: BBox, second: BBox) -> float:
    """Return the area shared by two bounding boxes."""
    width = min(first[2], second[2]) - max(first[0], second[0])
    height = min(first[3], second[3]) - max(first[1], second[1])
    return max(0.0, width) * max(0.0, height)


def viewbox(root: ElementTree.Element) -> BBox:
    """Return the document view box as ``(x, y, width, height)``."""
    raw = root.get("viewBox")
    if raw:
        values = [float(item) for item in NUMBER_RE.findall(raw)]
        if len(values) == 4:
            return values[0], values[1], values[0] + values[2], values[1] + values[3]
    width = parse_number(root.get("width"), "svg width")
    height = parse_number(root.get("height"), "svg height")
    return 0.0, 0.0, width, height
