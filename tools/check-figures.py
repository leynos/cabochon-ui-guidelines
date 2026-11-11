#!/usr/bin/env python3
"""Check generated figures against the shared figure contract.

The generator embeds a machine-readable annotation in every SVG. This checker
compares that annotation with ``tools/figure-data.json`` and with the rendered
geometry, so a figure cannot claim a class, scale, component or state mark it
does not draw. It fails closed: an unknown class, a missing annotation, a state
word in an undeclared colour, a declared mark with no matching primitive or a
production figure whose drawn component height disagrees with the catalogue is
an error.

Run from the repository root with ``python3 -I tools/check-figures.py``. Pass
``--self-test`` to prove that five deliberate mutations are detected.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIGURES = ROOT / "figures"
DATA = json.loads((ROOT / "tools" / "figure-data.json").read_text(encoding="utf-8"))

SVG_NS = "{http://www.w3.org/2000/svg}"
CLASSES = {"schematic", "editorial", "production"}


def state_colours() -> dict[str, str]:
    colours: dict[str, str] = {}
    for group in ("live_states", "resolution_states"):
        for state in DATA[group].values():
            colours[state["word"].upper()] = state["colour"]
    return colours


def state_marks() -> dict[str, str]:
    marks: dict[str, str] = {}
    for group in ("live_states", "resolution_states"):
        for state in DATA[group].values():
            mark = state.get("mark")
            if not mark:
                raise SystemExit(
                    f"figure contract: state {state['word']!r} declares no mark"
                )
            marks[state["word"].upper()] = mark
    return marks


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

    metadata = root.find(f"{SVG_NS}metadata")
    if metadata is None or not (metadata.text or "").strip():
        errors.append(f"{name}: missing embedded metadata")
    else:
        try:
            embedded = json.loads(metadata.text or "{}")
        except json.JSONDecodeError as exc:
            errors.append(f"{name}: metadata is not valid JSON: {exc}")
        else:
            if embedded.get("class") != spec["class"]:
                errors.append(f"{name}: metadata class disagrees with data")
            if embedded.get("profile") != spec["profile"]:
                errors.append(f"{name}: metadata profile disagrees with data")
            if embedded.get("components") != spec["components"]:
                errors.append(f"{name}: metadata components disagree with data")
    return errors


def local_name(element: ET.Element) -> str:
    return element.tag.replace(SVG_NS, "")


def mark_is_drawn(group: ET.Element, kind: str, colour: str) -> bool:
    """Check that the group contains the primitive the mark claims to draw."""
    colour = colour.upper()
    children = list(group)
    filled = [
        child
        for child in children
        if (child.get("fill") or "").upper() == colour
    ]
    stroked = [
        child
        for child in children
        if (child.get("stroke") or "").upper() == colour
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
        return any(local_name(child) == "rect" for child in stroked) and len(
            lines
        ) >= 3
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


def check_states(name: str, root: ET.Element) -> list[str]:
    errors: list[str] = []
    colours = state_colours()
    marks = state_marks()
    parents = {child: parent for parent in root.iter() for child in parent}
    for element in root.iter(f"{SVG_NS}text"):
        state = element.get("data-state")
        if state is None:
            continue
        word = (element.text or "").strip()
        key = word.upper()
        if key not in colours:
            errors.append(f"{name}: unknown state word {word!r}")
            continue
        fill = (element.get("fill") or "").upper()
        expected = colours[key].upper()
        if fill != expected:
            errors.append(
                f"{name}: state {word!r} drawn in {fill or 'no fill'}, "
                f"declared {expected}"
            )
        parent = parents.get(element)
        drawn = parent.get("data-mark") if parent is not None else None
        if not drawn:
            errors.append(f"{name}: state {word!r} has no declared mark")
        elif drawn != marks[key]:
            errors.append(
                f"{name}: state {word!r} drawn with mark {drawn!r}, "
                f"declared {marks[key]!r}"
            )
        elif parent is not None and not mark_is_drawn(parent, drawn, expected):
            errors.append(
                f"{name}: state {word!r} declares mark {drawn!r} "
                f"but does not draw it"
            )
    return errors


def check_production_geometry(
    name: str, root: ET.Element, spec: dict[str, object]
) -> list[str]:
    errors: list[str] = []
    if spec["class"] != "production":
        return errors
    if spec["scale"] != 1.0:
        errors.append(f"{name}: production figure must declare scale 1.0")
    catalogue = DATA["component_catalogue"]
    declared = spec["components"]
    if not declared:
        errors.append(f"{name}: production figure declares no components")
    for component in declared:
        if component not in catalogue:
            errors.append(f"{name}: unknown component {component!r}")
            continue
        expected = catalogue[component]["height"]
        groups = [
            element
            for element in root.iter()
            if element.get("data-component") == component
        ]
        if not groups:
            errors.append(f"{name}: no rendered geometry for {component!r}")
            continue
        for group in groups:
            rects = [
                element
                for element in group.iter(f"{SVG_NS}rect")
                if element.get("height") is not None
            ]
            if not rects:
                errors.append(
                    f"{name}: {component!r} has no rendered rectangle"
                )
                continue
            actual = float(rects[0].get("height") or 0)
            if actual != float(expected):
                errors.append(
                    f"{name}: {component!r} draws {actual}, "
                    f"catalogue says {expected}"
                )
            measured = group.get("data-height")
            if measured is None:
                errors.append(f"{name}: {component!r} has no measured height")
            elif float(measured) != actual:
                errors.append(
                    f"{name}: {component!r} annotation says {measured}, "
                    f"geometry draws {actual}"
                )
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
        errors.extend(check_states(name, root))
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
            '<g data-mark="dot">',
            "<g>",
            "no declared mark",
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
            failures.append("baseline copy did not pass")
        for label, filename, old, new, expected in mutations:
            target = work / filename
            original = target.read_text(encoding="utf-8")
            if old not in original:
                failures.append(f"{label}: mutation target not found")
                continue
            target.write_text(original.replace(old, new, 1), encoding="utf-8")
            errors = run(work)
            if not any(expected in error for error in errors):
                failures.append(f"{label}: not detected")
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
        "satisfy their declared class"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
