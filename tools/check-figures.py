#!/usr/bin/env python3
"""Check generated figures against the shared figure contract.

The generator embeds a machine-readable annotation in every SVG. This checker
compares that annotation with ``tools/figure-data.json`` and with the rendered
geometry. It uses a deliberately constrained SVG subset: the geometry it
measures contains only ``rect``, ``circle``, ``ellipse``, ``line``, ``polyline``,
``polygon`` and absolute ``M``/``L``/``A``/``Z`` paths, with
``translate``/``scale``/``rotate``/``matrix`` transforms. Clipping attributes are
rejected, so a mark's visible bounds are its transformed bounds intersected with
the viewBox.

A state is one record: identity, word, mark, role and colour are checked
together, and a figure must contain the semantic inventory declared for it.
Production figures declare bounds in logical units; the checker derives those
bounds from the drawn primitives and their ancestor transforms rather than
trusting a rectangle attribute or the embedded annotation.

Run from the repository root with ``python3 -I tools/check-figures.py``. Pass
``--self-test`` to prove that each deliberate mutation is detected.
"""

from __future__ import annotations

import json
import math
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIGURES = ROOT / "figures"
DATA = json.loads((ROOT / "tools" / "figure-data.json").read_text(encoding="utf-8"))

SVG_NS = "{http://www.w3.org/2000/svg}"
CLASSES = {"schematic", "editorial", "production"}
MARK_KINDS = {"dot", "arc", "triangle", "broken", "lock", "hatch", "dashed", "crossed"}
GEOMETRY_TAGS = {"rect", "circle", "ellipse", "line", "polyline", "polygon", "path"}
TRANSFORM_RE = re.compile(r"([a-zA-Z]+)\s*\(([^)]*)\)")
NUMBER_RE = re.compile(r"-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?")
PATH_TOKEN_RE = re.compile(r"[A-Za-z]|-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?")

IDENTITY = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
BBox = tuple[float, float, float, float]


class GeometryError(Exception):
    """A drawn element falls outside the checker's constrained SVG subset."""


def state_records() -> dict[str, dict[str, str]]:
    """Load and validate one record per state, keyed by identity."""
    records: dict[str, dict[str, str]] = {}
    words: set[str] = set()
    for group in ("live_states", "resolution_states"):
        for state in DATA[group].values():
            missing = [
                field
                for field in ("id", "word", "cue", "mark", "role", "colour")
                if not str(state.get(field, "")).strip()
            ]
            if missing:
                raise SystemExit(
                    f"figure contract: state {state.get('word')!r} lacks {missing}"
                )
            identifier = str(state["id"])
            if identifier in records:
                raise SystemExit(
                    f"figure contract: duplicate state identity {identifier!r}"
                )
            word = str(state["word"]).upper()
            if word in words:
                raise SystemExit(f"figure contract: duplicate state word {word!r}")
            words.add(word)
            if state["mark"] not in MARK_KINDS:
                raise SystemExit(
                    f"figure contract: state {word!r} has unknown mark "
                    f"{state['mark']!r}"
                )
            role_colour = DATA["palette_roles"].get(str(state["role"]))
            if role_colour is None:
                raise SystemExit(
                    f"figure contract: state {word!r} names unknown role "
                    f"{state['role']!r}"
                )
            if role_colour.upper() != str(state["colour"]).upper():
                raise SystemExit(
                    f"figure contract: state {word!r} colour {state['colour']} "
                    f"disagrees with role {state['role']!r}"
                )
            records[identifier] = {
                "id": identifier,
                "word": word,
                "mark": str(state["mark"]),
                "role": str(state["role"]),
                "colour": str(state["colour"]).upper(),
            }
    return records


STATE_RECORDS = state_records()


def local_name(element: ET.Element) -> str:
    return element.tag.replace(SVG_NS, "")


def parse_number(value: str | None, label: str) -> float:
    try:
        return float(value or "")
    except (TypeError, ValueError) as exc:
        raise GeometryError(f"{label} is not a number: {value!r}") from exc


def compose(outer: tuple[float, ...], inner: tuple[float, ...]) -> tuple[float, ...]:
    """Return the matrix that applies ``inner`` and then ``outer``."""
    a1, b1, c1, d1, e1, f1 = outer
    a2, b2, c2, d2, e2, f2 = inner
    return (
        a1 * a2 + c1 * b2,
        b1 * a2 + d1 * b2,
        a1 * c2 + c1 * d2,
        b1 * c2 + d1 * d2,
        a1 * e2 + c1 * f2 + e1,
        b1 * e2 + d1 * f2 + f1,
    )


def parse_transform(value: str) -> tuple[float, ...]:
    matrix = IDENTITY
    for match in TRANSFORM_RE.finditer(value):
        operation = match.group(1).lower()
        numbers = [float(item) for item in NUMBER_RE.findall(match.group(2))]
        if operation == "translate" and len(numbers) in {1, 2}:
            local = (1.0, 0.0, 0.0, 1.0, numbers[0], numbers[1] if len(numbers) == 2 else 0.0)
        elif operation == "scale" and len(numbers) in {1, 2}:
            local = (
                numbers[0],
                0.0,
                0.0,
                numbers[1] if len(numbers) == 2 else numbers[0],
                0.0,
                0.0,
            )
        elif operation == "rotate" and len(numbers) in {1, 3}:
            angle = math.radians(numbers[0])
            cosine, sine = math.cos(angle), math.sin(angle)
            local = (cosine, sine, -sine, cosine, 0.0, 0.0)
            if len(numbers) == 3:
                cx, cy = numbers[1], numbers[2]
                local = compose(
                    compose((1.0, 0.0, 0.0, 1.0, cx, cy), local),
                    (1.0, 0.0, 0.0, 1.0, -cx, -cy),
                )
        elif operation == "matrix" and len(numbers) == 6:
            local = tuple(numbers)  # type: ignore[assignment]
        else:
            raise GeometryError(f"unsupported transform {match.group(0)!r}")
        matrix = compose(matrix, local)
    remainder = TRANSFORM_RE.sub("", value).strip(" \t\r\n,")
    if remainder:
        raise GeometryError(f"unsupported transform syntax {value!r}")
    return matrix


def apply_matrix(matrix: tuple[float, ...], x: float, y: float) -> tuple[float, float]:
    a, b, c, d, e, f = matrix
    return a * x + c * y + e, b * x + d * y + f


def transform_bbox(box: BBox, matrix: tuple[float, ...]) -> BBox:
    min_x, min_y, max_x, max_y = box
    corners = [
        apply_matrix(matrix, x, y)
        for x in (min_x, max_x)
        for y in (min_y, max_y)
    ]
    xs = [point[0] for point in corners]
    ys = [point[1] for point in corners]
    return min(xs), min(ys), max(xs), max(ys)


def merge_bbox(first: BBox | None, second: BBox) -> BBox:
    if first is None:
        return second
    return (
        min(first[0], second[0]),
        min(first[1], second[1]),
        max(first[2], second[2]),
        max(first[3], second[3]),
    )


def path_bbox(data: str) -> BBox:
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
            if command.upper() == "Z":
                continue
            continue
        if command not in {"M", "L", "A"}:
            raise GeometryError(f"unsupported path command {command!r}")
        if command == "A":
            if index + 7 > len(tokens):
                raise GeometryError("truncated arc in path")
            radius = max(
                radius,
                float(tokens[index]),
                float(tokens[index + 1]),
            )
            points.append((float(tokens[index + 5]), float(tokens[index + 6])))
            index += 7
        else:
            if index + 2 > len(tokens):
                raise GeometryError("truncated point in path")
            points.append((float(tokens[index]), float(tokens[index + 1])))
            index += 2
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


def primitive_bbox(element: ET.Element) -> BBox:
    name = local_name(element)
    if name == "rect":
        x = parse_number(element.get("x", "0"), "rect x")
        y = parse_number(element.get("y", "0"), "rect y")
        width = parse_number(element.get("width"), "rect width")
        height = parse_number(element.get("height"), "rect height")
        if width <= 0 or height <= 0:
            raise GeometryError("rectangle has zero or negative size")
        return x, y, x + width, y + height
    if name == "circle":
        cx = parse_number(element.get("cx", "0"), "circle cx")
        cy = parse_number(element.get("cy", "0"), "circle cy")
        radius = parse_number(element.get("r"), "circle r")
        if radius <= 0:
            raise GeometryError("zero radius")
        return cx - radius, cy - radius, cx + radius, cy + radius
    if name == "ellipse":
        cx = parse_number(element.get("cx", "0"), "ellipse cx")
        cy = parse_number(element.get("cy", "0"), "ellipse cy")
        rx = parse_number(element.get("rx"), "ellipse rx")
        ry = parse_number(element.get("ry"), "ellipse ry")
        if rx <= 0 or ry <= 0:
            raise GeometryError("ellipse has zero radius")
        return cx - rx, cy - ry, cx + rx, cy + ry
    if name == "line":
        x1 = parse_number(element.get("x1", "0"), "line x1")
        y1 = parse_number(element.get("y1", "0"), "line y1")
        x2 = parse_number(element.get("x2", "0"), "line x2")
        y2 = parse_number(element.get("y2", "0"), "line y2")
        return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)
    if name in {"polyline", "polygon"}:
        numbers = [float(item) for item in NUMBER_RE.findall(element.get("points", ""))]
        if len(numbers) < 4:
            raise GeometryError("polyline has fewer than two points")
        xs = numbers[0::2]
        ys = numbers[1::2]
        return min(xs), min(ys), max(xs), max(ys)
    if name == "path":
        return path_bbox(element.get("d", ""))
    raise GeometryError(f"unsupported primitive {name!r}")


def hidden_reason(element: ET.Element, parents: dict[ET.Element, ET.Element]) -> str | None:
    chain: list[ET.Element] = []
    node: ET.Element | None = element
    while node is not None:
        chain.append(node)
        node = parents.get(node)
    for node in reversed(chain):
        if node.get("display") == "none":
            return "display none"
        if node.get("visibility") in {"hidden", "collapse"}:
            return "visibility hidden"
        opacity = node.get("opacity")
        if opacity is not None and parse_number(opacity, "opacity") <= 0:
            return "zero opacity"
    return None


def clip_used(element: ET.Element, parents: dict[ET.Element, ET.Element]) -> bool:
    node: ET.Element | None = element
    while node is not None:
        if node.get("clip-path") or node.get("mask"):
            return True
        node = parents.get(node)
    return False


def paint_visible(element: ET.Element) -> bool:
    fill = (element.get("fill") or "").lower()
    stroke = (element.get("stroke") or "").lower()
    fill_opacity = parse_number(element.get("fill-opacity", "1"), "fill-opacity")
    stroke_opacity = parse_number(element.get("stroke-opacity", "1"), "stroke-opacity")
    has_fill = fill not in {"", "none", "transparent"} and fill_opacity > 0
    has_stroke = stroke not in {"", "none", "transparent"} and stroke_opacity > 0
    return has_fill or has_stroke


def element_matrix(
    element: ET.Element, parents: dict[ET.Element, ET.Element]
) -> tuple[float, ...]:
    chain: list[ET.Element] = []
    node: ET.Element | None = element
    while node is not None:
        chain.append(node)
        node = parents.get(node)
    matrix = IDENTITY
    for node in reversed(chain):
        value = node.get("transform")
        if value:
            matrix = compose(matrix, parse_transform(value))
    return matrix


def rendered_bbox(
    group: ET.Element,
    parents: dict[ET.Element, ET.Element],
    label: str,
) -> BBox:
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
        box = merge_bbox(box, transform_bbox(local_box, element_matrix(element, parents)))
    if box is None:
        raise GeometryError(f"{label} draws no geometry")
    if box[2] - box[0] <= 0 and box[3] - box[1] <= 0:
        raise GeometryError(f"{label} has zero visible area")
    return box


def intersect_area(first: BBox, second: BBox) -> float:
    width = min(first[2], second[2]) - max(first[0], second[0])
    height = min(first[3], second[3]) - max(first[1], second[1])
    return max(0.0, width) * max(0.0, height)


def viewbox(root: ET.Element) -> BBox:
    raw = root.get("viewBox")
    if raw:
        values = [float(item) for item in NUMBER_RE.findall(raw)]
        if len(values) == 4:
            return values[0], values[1], values[0] + values[2], values[1] + values[3]
    width = parse_number(root.get("width"), "svg width")
    height = parse_number(root.get("height"), "svg height")
    return 0.0, 0.0, width, height


def mark_is_drawn(group: ET.Element, kind: str, colour: str) -> bool:
    """Check that the mark group contains the primitive its record claims."""
    colour = colour.upper()
    children = list(group)
    filled = [
        child for child in children if (child.get("fill") or "").upper() == colour
    ]
    stroked = [
        child for child in children if (child.get("stroke") or "").upper() == colour
    ]
    lines = [child for child in children if local_name(child) == "line"]
    if kind == "dot":
        return any(local_name(child) == "circle" for child in filled)
    if kind == "arc":
        return any(local_name(child) == "path" for child in stroked)
    if kind == "triangle":
        return any(local_name(child) == "path" for child in filled)
    if kind == "broken":
        return len(lines) >= 2
    if kind == "lock":
        return any(local_name(child) == "rect" for child in filled) and any(
            local_name(child) == "path" for child in stroked
        )
    if kind == "hatch":
        return any(local_name(child) == "rect" for child in stroked) and len(lines) >= 3
    if kind == "dashed":
        return any(
            local_name(child) == "rect" and child.get("stroke-dasharray")
            for child in children
        )
    if kind == "crossed":
        return any(local_name(child) == "rect" for child in stroked) and len(
            lines
        ) == 2
    return False


def check_annotation(name: str, root: ET.Element, spec: dict[str, object]) -> list[str]:
    errors: list[str] = []
    figure_class = root.get("data-figure-class")
    if figure_class is None:
        errors.append(f"{name}: missing data-figure-class")
    elif figure_class not in CLASSES:
        errors.append(f"{name}: unknown figure class {figure_class!r}")
    elif figure_class != spec["class"]:
        errors.append(
            f"{name}: class {figure_class!r} disagrees with data {spec['class']!r}"
        )

    profile = root.get("data-figure-profile")
    if profile != spec["profile"]:
        errors.append(
            f"{name}: profile {profile!r} disagrees with data {spec['profile']!r}"
        )

    scale = root.get("data-figure-scale")
    declared_scale = spec["scale"]
    if declared_scale is None:
        if scale is not None:
            errors.append(
                f"{name}: declares scale {scale!r} but data declares none"
            )
    elif scale is None:
        errors.append(f"{name}: missing data-figure-scale")
    elif parse_number(scale, "figure scale") != float(declared_scale):
        errors.append(
            f"{name}: declares scale {scale!r} but data declares "
            f"{declared_scale!r}"
        )

    metadata = root.find(f"{SVG_NS}metadata")
    if metadata is None or not (metadata.text or "").strip():
        errors.append(f"{name}: missing embedded metadata")
    else:
        try:
            embedded = json.loads(metadata.text or "{}")
        except json.JSONDecodeError as exc:
            errors.append(f"{name}: metadata is not valid JSON: {exc}")
        else:
            for key in ("class", "profile", "components", "states"):
                if embedded.get(key) != spec.get(key):
                    errors.append(f"{name}: metadata {key} disagrees with data")
            for key in ("size", "bounds"):
                if key in spec and embedded.get(key) != spec[key]:
                    errors.append(f"{name}: metadata {key} disagrees with data")
    return errors


def check_states(name: str, root: ET.Element, spec: dict[str, object]) -> list[str]:
    errors: list[str] = []
    parents = {child: parent for parent in root.iter() for child in parent}
    counts: Counter[str] = Counter()
    texts = [
        element
        for element in root.iter(f"{SVG_NS}text")
        if element.get("data-state") is not None
    ]
    for element in texts:
        identifier = element.get("data-state") or ""
        counts[identifier] += 1
        record = STATE_RECORDS.get(identifier)
        if record is None:
            errors.append(f"{name}: unknown state identity {identifier!r}")
            continue
        label = (element.text or "").strip()
        if label.upper() != record["word"]:
            errors.append(
                f"{name}: state {identifier!r} label {label!r} disagrees with "
                f"record {record['word']!r}"
            )
        fill = (element.get("fill") or "").upper()
        if fill != record["colour"]:
            errors.append(
                f"{name}: state {identifier!r} drawn in {fill or 'no fill'}, "
                f"record declares {record['colour']}"
            )

        ancestor = parents.get(element)
        while ancestor is not None and local_name(ancestor) != "g":
            ancestor = parents.get(ancestor)
        if ancestor is None:
            errors.append(f"{name}: state {identifier!r} is not inside a group")
            continue
        labels = [
            item
            for item in ancestor.iter(f"{SVG_NS}text")
            if item.get("data-state") is not None
        ]
        if len(labels) != 1:
            errors.append(
                f"{name}: state card {identifier!r} contains {len(labels)} "
                "state labels"
            )
        groups = [item for item in ancestor.iter() if item.get("data-mark") is not None]
        if not groups:
            errors.append(f"{name}: state {identifier!r} has no declared mark")
            continue
        if len(groups) != 1:
            errors.append(
                f"{name}: state {identifier!r} has {len(groups)} mark groups"
            )
            continue
        group = groups[0]
        if group.get("data-state-id") != identifier:
            errors.append(
                f"{name}: state {identifier!r} mark identity "
                f"{group.get('data-state-id')!r} disagrees with record"
            )
        if group.get("data-role") != record["role"]:
            errors.append(
                f"{name}: state {identifier!r} mark role "
                f"{group.get('data-role')!r} disagrees with record "
                f"{record['role']!r}"
            )
        drawn = group.get("data-mark") or ""
        if drawn != record["mark"]:
            errors.append(
                f"{name}: state {identifier!r} drawn with mark {drawn!r}, "
                f"record declares {record['mark']!r}"
            )
        if not mark_is_drawn(group, drawn, record["colour"]):
            errors.append(
                f"{name}: state {identifier!r} declares mark {drawn!r} "
                "but does not draw it"
            )
        if clip_used(group, parents):
            errors.append(
                f"{name}: state {identifier!r} mark uses clipping, which the "
                "constrained subset forbids"
            )
            continue
        reason = hidden_reason(group, parents)
        if reason is not None:
            errors.append(
                f"{name}: state {identifier!r} mark is not visible ({reason})"
            )
            continue
        try:
            box = rendered_bbox(group, parents, f"state {identifier!r} mark")
        except GeometryError as exc:
            errors.append(f"{name}: state {identifier!r} mark is invalid: {exc}")
            continue
        if intersect_area(box, viewbox(root)) <= 0:
            errors.append(
                f"{name}: state {identifier!r} mark is clipped by the viewBox"
            )

    expected = spec.get("states")
    if not isinstance(expected, dict):
        errors.append(f"{name}: missing state inventory")
        return errors
    for identifier, count in expected.items():
        if identifier not in STATE_RECORDS:
            errors.append(
                f"{name}: inventory names unknown state {identifier!r}"
            )
            continue
        actual = counts.get(identifier, 0)
        if actual != count:
            errors.append(
                f"{name}: state inventory expects {count} of {identifier!r}, "
                f"found {actual}"
            )
    for identifier, actual in counts.items():
        if identifier not in expected:
            errors.append(
                f"{name}: state {identifier!r} is drawn {actual} time(s) but is "
                "absent from the inventory"
            )
    return errors


def check_production_geometry(
    name: str, root: ET.Element, spec: dict[str, object]
) -> list[str]:
    errors: list[str] = []
    if spec["class"] != "production":
        if spec.get("components"):
            errors.append(f"{name}: non-production figure declares components")
        return errors
    if float(spec["scale"] or 0) != 1.0:
        errors.append(f"{name}: production figure must declare scale 1.0")

    size = spec.get("size")
    bounds = spec.get("bounds")
    if not isinstance(size, dict) or not isinstance(bounds, dict):
        errors.append(f"{name}: production figure lacks size or bounds")
        return errors
    width = parse_number(root.get("width"), "svg width")
    height = parse_number(root.get("height"), "svg height")
    if (width, height) != (float(size["width"]), float(size["height"])):
        errors.append(
            f"{name}: canvas {width}x{height} disagrees with declared "
            f"{size['width']}x{size['height']}"
        )
    raw_viewbox = [float(item) for item in NUMBER_RE.findall(root.get("viewBox", ""))]
    if len(raw_viewbox) != 4 or raw_viewbox[2:] != [width, height]:
        errors.append(f"{name}: viewBox disagrees with the declared canvas")

    catalogue = DATA["component_catalogue"]
    declared = spec["components"]
    if not declared:
        errors.append(f"{name}: production figure declares no components")
    parents = {child: parent for parent in root.iter() for child in parent}
    rendered: dict[str, list[ET.Element]] = {}
    for element in root.iter():
        component = element.get("data-component")
        if component is not None:
            rendered.setdefault(component, []).append(element)
    for component in rendered:
        if component not in declared:
            errors.append(
                f"{name}: component {component!r} is drawn but not declared"
            )
    for component in declared:
        if component not in catalogue:
            errors.append(f"{name}: unknown component {component!r}")
            continue
        groups = rendered.get(component, [])
        if not groups:
            errors.append(f"{name}: no rendered geometry for {component!r}")
            continue
        if len(groups) != 1:
            errors.append(
                f"{name}: component {component!r} is rendered {len(groups)} times"
            )
        group = groups[0]
        reason = hidden_reason(group, parents)
        if reason is not None:
            errors.append(f"{name}: component {component!r} is not visible ({reason})")
            continue
        try:
            box = rendered_bbox(group, parents, f"component {component!r}")
        except GeometryError as exc:
            errors.append(f"{name}: component {component!r} is invalid: {exc}")
            continue
        rendered_width = box[2] - box[0]
        rendered_height = box[3] - box[1]
        expected = float(catalogue[component]["height"])
        if abs(rendered_height - expected) > 0.01:
            errors.append(
                f"{name}: {component!r} rendered height {rendered_height:.2f} "
                f"disagrees with catalogue {expected:.2f}"
            )
        annotation = group.get("data-height")
        if annotation is None:
            errors.append(f"{name}: component {component!r} has no measured height")
        elif abs(parse_number(annotation, "data-height") - rendered_height) > 0.01:
            errors.append(
                f"{name}: {component!r} annotation says {annotation}, geometry "
                f"renders {rendered_height:.2f}"
            )
        declared_box = bounds.get(component)
        if not isinstance(declared_box, dict):
            errors.append(f"{name}: component {component!r} has no declared bounds")
            continue
        actual = {
            "x": box[0],
            "y": box[1],
            "width": rendered_width,
            "height": rendered_height,
        }
        for field in ("x", "y", "width", "height"):
            if abs(actual[field] - float(declared_box[field])) > 0.01:
                errors.append(
                    f"{name}: {component!r} rendered {field} {actual[field]:.2f} "
                    f"disagrees with declared {declared_box[field]}"
                )
    for component in bounds:
        if component not in declared:
            errors.append(f"{name}: bounds name undeclared component {component!r}")
    return errors


def run(figures: Path) -> list[str]:
    errors: list[str] = []
    specs: dict[str, dict[str, object]] = DATA["figures"]
    present = {path.stem for path in figures.glob("*.svg")}
    for name in sorted(set(specs) - present):
        errors.append(f"{name}: declared in figure-data.json but not generated")
    for name in sorted(present - set(specs)):
        errors.append(f"{name}: generated but not declared in figure-data.json")

    for name in sorted(present & set(specs)):
        path = figures / f"{name}.svg"
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as exc:
            errors.append(f"{name}: not well-formed XML: {exc}")
            continue
        spec = specs[name]
        errors.extend(check_annotation(name, root, spec))
        errors.extend(check_states(name, root, spec))
        errors.extend(check_production_geometry(name, root, spec))
    return errors


def self_test() -> int:
    """Prove that the checker detects the defects it claims to prevent."""
    mutations = [
        (
            "state mark removed",
            "fig-06-state.svg",
            '<circle cx="86" cy="194" r="3" fill="#285E50" stroke-width="1"/>',
            "",
            "does not draw it",
        ),
        (
            "state colour changed",
            "fig-06-state.svg",
            'fill="#285E50" font-family="&#x27;DejaVu Sans Mono&#x27;,',
            'fill="#8A302F" font-family="&#x27;DejaVu Sans Mono&#x27;,',
            "drawn in",
        ),
        (
            "mark declaration removed",
            "fig-06-state.svg",
            '<g data-mark="dot" data-state-id="current" data-role="pine2">',
            '<g data-state-id="current" data-role="pine2">',
            "has no declared mark",
        ),
        (
            "zero radius dot",
            "fig-06-state.svg",
            '<circle cx="86" cy="194" r="3"',
            '<circle cx="86" cy="194" r="0"',
            "zero radius",
        ),
        (
            "invisible dot",
            "fig-06-state.svg",
            '<circle cx="86" cy="194" r="3"',
            '<circle cx="86" cy="194" r="3" opacity="0"',
            "zero opacity",
        ),
        (
            "contradictory label",
            "fig-06-state.svg",
            'data-state="denied">DENIED</text>',
            'data-state="denied">CURRENT</text>',
            "label 'CURRENT' disagrees",
        ),
        (
            "annotation removed",
            "fig-06-state.svg",
            'data-state="current">CURRENT</text>',
            'data-state="current-removed">CURRENT</text>',
            "unknown state identity",
        ),
        (
            "state removed from inventory",
            "fig-06-state.svg",
            'data-state="current">CURRENT</text>',
            'data-state-removed="current">CURRENT</text>',
            "state inventory expects 1 of 'current', found 0",
        ),
        (
            "transformed production geometry",
            "fig-prod-chrome.svg",
            '<g data-component="title_bar" data-height="31">',
            '<g data-component="title_bar" data-height="31" transform="scale(1,2)">',
            "rendered height",
        ),
        (
            "production scale metadata",
            "fig-prod-chrome.svg",
            'data-figure-scale="1.0"',
            'data-figure-scale="2.0"',
            "declares scale",
        ),
        (
            "hidden production component",
            "fig-prod-chrome.svg",
            '<g data-component="menu_bar" data-height="29">',
            '<g data-component="menu_bar" data-height="29" display="none">',
            "is not visible",
        ),
        (
            "figure class changed",
            "fig-06-state.svg",
            'data-figure-class="schematic"',
            'data-figure-class="production"',
            "disagrees with data",
        ),
        (
            "metadata removed",
            "fig-06-state.svg",
            "<metadata>",
            '<metadata xmlns="urn:removed">',
            "missing embedded metadata",
        ),
    ]
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as directory:
        work = Path(directory)
        for source in FIGURES.glob("*.svg"):
            shutil.copy2(source, work / source.name)
        if run(work):
            failures.append(f"baseline copy did not pass: {run(work)[:3]}")
        for label, filename, old, new, expected in mutations:
            target = work / filename
            original = target.read_text(encoding="utf-8")
            if old not in original:
                failures.append(f"{label}: mutation target not found")
                continue
            target.write_text(original.replace(old, new, 1), encoding="utf-8")
            errors = run(work)
            if not any(expected in error for error in errors):
                failures.append(
                    f"{label}: not detected; errors were {errors[:3]}"
                )
            target.write_text(original, encoding="utf-8")
    if failures:
        for failure in failures:
            print(f"figure contract self-test: {failure}", file=sys.stderr)
        return 1
    print(f"figure contract self-test detected all {len(mutations)} mutations")
    return 0


def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()
    errors = run(FIGURES)
    if errors:
        for error in errors:
            print(f"figure contract: {error}", file=sys.stderr)
        return 1
    print(
        f"figure contract: {len(list(FIGURES.glob('*.svg')))} figures "
        "satisfy their declared class, inventory and geometry"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())