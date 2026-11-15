"""Run every figure check and assemble the failure report."""

from __future__ import annotations

import typing as typ
from xml.etree import ElementTree

from figurecheck.annotation import check_annotation
from figurecheck.contract import DATA
from figurecheck.production import check_production_geometry
from figurecheck.states import check_states

if typ.TYPE_CHECKING:
    from pathlib import Path


def run(figures: Path) -> list[str]:
    """Run every figure check and return the failure report."""
    errors: list[str] = []
    specs: dict[str, dict[str, object]] = DATA["figures"]
    present = {path.stem for path in figures.glob("*.svg")}
    errors.extend(
        f"{name}: declared in figure-data.json but not generated"
        for name in sorted(set(specs) - present)
    )
    errors.extend(
        f"{name}: generated but not declared in figure-data.json"
        for name in sorted(present - set(specs))
    )

    for name in sorted(present & set(specs)):
        path = figures / f"{name}.svg"
        try:
            root = ElementTree.parse(path).getroot()
        except ElementTree.ParseError as exc:
            errors.append(f"{name}: not well-formed XML: {exc}")
            continue
        spec = specs[name]
        errors.extend(check_annotation(name, root, spec))
        errors.extend(check_states(name, root, spec))
        errors.extend(check_production_geometry(name, root, spec))
    return errors
