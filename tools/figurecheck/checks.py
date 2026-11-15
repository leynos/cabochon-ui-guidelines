"""Run every figure check and assemble the failure report.

The `run` function compares the generated SVG inventory with
`tools/figure-data.json`, then dispatches each figure to the annotation, state
and production-geometry checks. `figurecheck.cli` and `figurecheck.selftest`
both import it.
"""

from __future__ import annotations

import typing as typ
from xml.etree import ElementTree

from figurecheck.annotation import check_annotation
from figurecheck.contract import component_catalogue, figure_specs
from figurecheck.production import check_production_geometry
from figurecheck.states import check_states

if typ.TYPE_CHECKING:
    from pathlib import Path


def run(
    figures: Path,
    data: dict[str, object],
    records: dict[str, dict[str, str]],
) -> list[str]:
    """Run every figure check and return the failure report.

    Parameters
    ----------
    figures
        The directory that holds the generated SVG figures.
    data
        The decoded figure contract document.
    records
        The validated state records keyed by identity.

    Returns
    -------
    list[str]
        Every defect the checks found, or an empty list.
    """
    errors: list[str] = []
    specs = figure_specs(data)
    catalogue = component_catalogue(data)
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
        errors.extend(check_states(name, root, spec, records))
        errors.extend(check_production_geometry(name, root, spec, catalogue))
    return errors
