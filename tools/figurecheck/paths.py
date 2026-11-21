"""Measure the bounding boxes of SVG path data.

`path_bbox` computes the bounds of the segments a path data string draws, using
the path token grammar and error type from `figurecheck.contract`. The geometry
module re-exports it beside the other bounding box helpers.
"""

from __future__ import annotations

import typing as typ

from figurecheck.contract import PATH_TOKEN_RE, BBox, GeometryError


def _consume_arc(
    tokens: list[str], index: int, radius: float
) -> tuple[float, tuple[float, float], int]:
    """Read one arc's radii and endpoint, widening the radius it spans."""
    if index + 7 > len(tokens):
        raise GeometryError("truncated arc in path")
    radius = max(radius, float(tokens[index]), float(tokens[index + 1]))
    point = (float(tokens[index + 5]), float(tokens[index + 6]))
    return radius, point, index + 7


def _consume_point(tokens: list[str], index: int) -> tuple[tuple[float, float], int]:
    """Read one coordinate pair from path tokens."""
    if index + 2 > len(tokens):
        raise GeometryError("truncated point in path")
    return (float(tokens[index]), float(tokens[index + 1])), index + 2


class _Subpath(typ.NamedTuple):
    """The points, widest arc radius and drawn flag of one path subpath."""

    points: list[tuple[float, float]]
    radius: float
    drawn: bool


def _subpaths(data: str) -> list[_Subpath]:
    """Split path data into the subpaths it declares."""
    tokens = PATH_TOKEN_RE.findall(data)
    subpaths: list[_Subpath] = []
    points: list[tuple[float, float]] = []
    radius = 0.0
    drawn = False
    command: str | None = None
    starts_here = False
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token.isalpha():
            command = token
            if command == "M":
                subpaths.append(_Subpath(points, radius, drawn))
                points, radius, drawn = [], 0.0, False
            starts_here = True
            index += 1
            continue
        if command not in {"M", "L", "A"}:
            raise GeometryError(f"unsupported path command {command!r}")
        if command == "A":
            radius, point, index = _consume_arc(tokens, index, radius)
        else:
            point, index = _consume_point(tokens, index)
        if command != "M" or not starts_here:
            drawn = True
        starts_here = False
        points.append(point)
    subpaths.append(_Subpath(points, radius, drawn))
    return subpaths


def path_bbox(data: str) -> BBox:
    """Compute the bounding box of the segments an SVG path data string draws."""
    drawn = [subpath for subpath in _subpaths(data) if subpath.drawn]
    if not drawn:
        raise GeometryError("path draws no segments")
    radius = max(subpath.radius for subpath in drawn)
    points = [point for subpath in drawn for point in subpath.points]
    return (
        min(point[0] for point in points) - radius,
        min(point[1] for point in points) - radius,
        max(point[0] for point in points) + radius,
        max(point[1] for point in points) + radius,
    )
