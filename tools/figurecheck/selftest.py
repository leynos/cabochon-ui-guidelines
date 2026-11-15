"""Prove that the figure checker detects the defects it claims to prevent."""

from __future__ import annotations

import shutil
import sys
import tempfile
import typing as typ
from pathlib import Path

from figurecheck.checks import run
from figurecheck.contract import FIGURES


class _Mutation(typ.NamedTuple):
    """One deliberate defect and the diagnostic that must report it."""

    label: str
    filename: str
    old: str
    new: str
    expected: str


MUTATIONS = (
    _Mutation(
        "state mark removed",
        "fig-06-state.svg",
        '<circle cx="86" cy="194" r="3" fill="#285E50" stroke-width="1"/>',
        "",
        "does not draw it",
    ),
    _Mutation(
        "state colour changed",
        "fig-06-state.svg",
        'fill="#285E50" font-family="&#x27;DejaVu Sans Mono&#x27;,',
        'fill="#8A302F" font-family="&#x27;DejaVu Sans Mono&#x27;,',
        "drawn in",
    ),
    _Mutation(
        "mark declaration removed",
        "fig-06-state.svg",
        '<g data-mark="dot" data-state-id="current" data-role="pine2">',
        '<g data-state-id="current" data-role="pine2">',
        "has no declared mark",
    ),
    _Mutation(
        "zero radius dot",
        "fig-06-state.svg",
        '<circle cx="86" cy="194" r="3"',
        '<circle cx="86" cy="194" r="0"',
        "zero radius",
    ),
    _Mutation(
        "invisible dot",
        "fig-06-state.svg",
        '<circle cx="86" cy="194" r="3"',
        '<circle cx="86" cy="194" r="3" opacity="0"',
        "zero opacity",
    ),
    _Mutation(
        "contradictory label",
        "fig-06-state.svg",
        'data-state="denied">DENIED</text>',
        'data-state="denied">CURRENT</text>',
        "label 'CURRENT' disagrees",
    ),
    _Mutation(
        "annotation removed",
        "fig-06-state.svg",
        'data-state="current">CURRENT</text>',
        'data-state="current-removed">CURRENT</text>',
        "unknown state identity",
    ),
    _Mutation(
        "state removed from inventory",
        "fig-06-state.svg",
        'data-state="current">CURRENT</text>',
        'data-state-removed="current">CURRENT</text>',
        "state inventory expects 1 of 'current', found 0",
    ),
    _Mutation(
        "transformed production geometry",
        "fig-prod-chrome.svg",
        '<g data-component="title_bar" data-height="31">',
        '<g data-component="title_bar" data-height="31" transform="scale(1,2)">',
        "rendered height",
    ),
    _Mutation(
        "production scale metadata",
        "fig-prod-chrome.svg",
        'data-figure-scale="1.0"',
        'data-figure-scale="2.0"',
        "declares scale",
    ),
    _Mutation(
        "hidden production component",
        "fig-prod-chrome.svg",
        '<g data-component="menu_bar" data-height="29">',
        '<g data-component="menu_bar" data-height="29" display="none">',
        "is not visible",
    ),
    _Mutation(
        "figure class changed",
        "fig-06-state.svg",
        'data-figure-class="schematic"',
        'data-figure-class="production"',
        "disagrees with data",
    ),
    _Mutation(
        "metadata removed",
        "fig-06-state.svg",
        "<metadata>",
        '<metadata xmlns="urn:removed">',
        "missing embedded metadata",
    ),
)


def _detect(work: Path, mutation: _Mutation) -> str | None:
    """Apply one mutation, returning a failure description if it escapes."""
    target = work / mutation.filename
    original = target.read_text(encoding="utf-8")
    if mutation.old not in original:
        return f"{mutation.label}: mutation target not found"
    target.write_text(
        original.replace(mutation.old, mutation.new, 1), encoding="utf-8"
    )
    errors = run(work)
    target.write_text(original, encoding="utf-8")
    if not any(mutation.expected in error for error in errors):
        return f"{mutation.label}: not detected; errors were {errors[:3]}"
    return None


def self_test() -> int:
    """Prove that the checker detects the defects it claims to prevent."""
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as directory:
        work = Path(directory)
        for source in FIGURES.glob("*.svg"):
            shutil.copy2(source, work / source.name)
        baseline = run(work)
        if baseline:
            failures.append(f"baseline copy did not pass: {baseline[:3]}")
        for mutation in MUTATIONS:
            failure = _detect(work, mutation)
            if failure is not None:
                failures.append(failure)
    if failures:
        for failure in failures:
            print(f"figure contract self-test: {failure}", file=sys.stderr)
        return 1
    print(f"figure contract self-test detected all {len(MUTATIONS)} mutations")
    return 0
