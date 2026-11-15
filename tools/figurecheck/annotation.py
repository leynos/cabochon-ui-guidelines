"""Compare a figure's embedded annotation with the shared figure data."""

from __future__ import annotations

import json
import math
import typing as typ

from figurecheck.contract import CLASSES, SVG_NS
from figurecheck.geometry import parse_number

if typ.TYPE_CHECKING:
    from xml.etree import ElementTree

METADATA_KEYS = ("class", "profile", "components", "states")
GEOMETRY_KEYS = ("size", "bounds")


def _check_class(
    name: str, root: ElementTree.Element, spec: dict[str, object], errors: list[str]
) -> None:
    """Check that the figure declares a known class matching its data."""
    figure_class = root.get("data-figure-class")
    if figure_class is None:
        errors.append(f"{name}: missing data-figure-class")
    elif figure_class not in CLASSES:
        errors.append(f"{name}: unknown figure class {figure_class!r}")
    elif figure_class != spec["class"]:
        errors.append(
            f"{name}: class {figure_class!r} disagrees with data {spec['class']!r}"
        )


def _check_profile(
    name: str, root: ElementTree.Element, spec: dict[str, object], errors: list[str]
) -> None:
    """Check that the figure profile matches its data."""
    profile = root.get("data-figure-profile")
    if profile != spec["profile"]:
        errors.append(
            f"{name}: profile {profile!r} disagrees with data {spec['profile']!r}"
        )


def _check_scale(
    name: str, root: ElementTree.Element, spec: dict[str, object], errors: list[str]
) -> None:
    """Check that the declared scale matches its data."""
    scale = root.get("data-figure-scale")
    declared = spec["scale"]
    if declared is None:
        if scale is not None:
            errors.append(f"{name}: declares scale {scale!r} but data declares none")
    elif scale is None:
        errors.append(f"{name}: missing data-figure-scale")
    elif not math.isclose(
        parse_number(scale, "figure scale"),
        parse_number(str(declared), "declared scale"),
    ):
        errors.append(
            f"{name}: declares scale {scale!r} but data declares {declared!r}"
        )


def _check_metadata(
    name: str, root: ElementTree.Element, spec: dict[str, object], errors: list[str]
) -> None:
    """Check that the embedded metadata repeats the figure data."""
    metadata = root.find(f"{SVG_NS}metadata")
    if metadata is None or not (metadata.text or "").strip():
        errors.append(f"{name}: missing embedded metadata")
        return
    try:
        embedded = json.loads(metadata.text or "{}")
    except json.JSONDecodeError as exc:
        errors.append(f"{name}: metadata is not valid JSON: {exc}")
        return
    errors.extend(
        f"{name}: metadata {key} disagrees with data"
        for key in METADATA_KEYS
        if embedded.get(key) != spec.get(key)
    )
    errors.extend(
        f"{name}: metadata {key} disagrees with data"
        for key in GEOMETRY_KEYS
        if key in spec and embedded.get(key) != spec[key]
    )


def check_annotation(
    name: str, root: ElementTree.Element, spec: dict[str, object]
) -> list[str]:
    """Check that production annotations match rendered geometry."""
    errors: list[str] = []
    for check in (_check_class, _check_profile, _check_scale, _check_metadata):
        check(name, root, spec, errors)
    return errors
