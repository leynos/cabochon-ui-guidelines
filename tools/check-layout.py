#!/usr/bin/env python3
"""Derive the layout budgets from declared component tokens.

The chapter may not state a band total or a document-plane size that the
declared tokens do not produce. Every configuration names its profile, window
and panes; this checker sums the bands and panes, applies separator ownership
and compares the derived document plane with the worked value.

Run from the repository root with ``python3 -I tools/check-layout.py``. Pass
``--self-test`` to prove that four deliberate token or value changes fail.
"""

from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUDGETS = json.loads(
    (ROOT / "tools" / "layout-budgets.json").read_text(encoding="utf-8")
)
CHAPTER = ROOT / "book" / "14-spacing-metrics.md"


def number(tokens: dict[str, int], value: object) -> int:
    if isinstance(value, int):
        return value
    return tokens[str(value)]


def bands(tokens: dict[str, int], profiles: dict[str, list[str]], name: str) -> int:
    return sum(tokens[band] for band in profiles[name])


def pane_width(tokens: dict[str, int], name: str) -> int:
    """A collapsed strip includes its splitter; an expanded pane does not."""
    return tokens[name]


def side_width(tokens: dict[str, int], configuration: dict[str, object]) -> int:
    total = 0
    for side in ("left", "right"):
        pane = str(configuration[side])
        total += pane_width(tokens, pane)
        if pane != "collapsed_strip":
            total += tokens["splitter"]
    return total


def derive(
    tokens: dict[str, int],
    profiles: dict[str, list[str]],
    configuration: dict[str, object],
) -> tuple[int, int, int]:
    height = number(tokens, configuration["height"])
    width = number(tokens, configuration["width"])
    band_total = bands(tokens, profiles, str(configuration["profile"]))
    document_width = width - side_width(tokens, configuration)
    document_height = height - band_total
    return band_total, document_width, document_height


def validate(
    configuration: dict[str, object],
    tokens: dict[str, int] | None = None,
    profiles: dict[str, list[str]] | None = None,
) -> list[str]:
    errors: list[str] = []
    tokens = BUDGETS["tokens"] if tokens is None else tokens
    profiles = BUDGETS["profiles"] if profiles is None else profiles
    band_total, width, height = derive(tokens, profiles, configuration)
    expected_width, expected_height = configuration["expected"]
    if (width, height) != (expected_width, expected_height):
        errors.append(
            f"{configuration['name']}: derives {width} × {height}, "
            f"worked value is {expected_width} × {expected_height}"
        )
    if width < tokens["document_width_min"]:
        errors.append(
            f"{configuration['name']}: document width {width} is below "
            f"the {tokens['document_width_min']}-unit minimum"
        )
    viewport_min = (
        tokens["compact_viewport_min"]
        if configuration.get("compact")
        else tokens["document_viewport_min"]
    )
    if height < viewport_min:
        errors.append(
            f"{configuration['name']}: viewport {height} is below "
            f"the {viewport_min}-unit minimum"
        )
    if band_total + viewport_min > number(tokens, configuration["height"]):
        errors.append(
            f"{configuration['name']}: {band_total} units of bands plus a "
            f"{viewport_min}-unit viewport do not fit the window"
        )
    content = tokens["document_content_height"]
    if configuration.get("compact") and height >= content:
        errors.append(
            f"{configuration['name']}: compact viewport {height} does not "
            f"require the {content}-unit content extent to scroll"
        )
    return errors


def check_chapter() -> list[str]:
    errors: list[str] = []
    text = CHAPTER.read_text(encoding="utf-8")
    for configuration in BUDGETS["configurations"]:
        width, height = configuration["expected"]
        worked = f"{width} × {height}"
        if worked not in text:
            errors.append(
                f"chapter 14 does not state the worked value {worked!r} "
                f"for {configuration['name']}"
            )
    return errors


def run() -> list[str]:
    errors: list[str] = []
    for configuration in BUDGETS["configurations"]:
        errors.extend(validate(configuration))
    errors.extend(check_chapter())
    return errors


def self_test() -> int:
    failures: list[str] = []
    if run():
        failures.append("baseline budgets did not pass")

    tokens = BUDGETS["tokens"]
    profiles = BUDGETS["profiles"]
    configuration = BUDGETS["configurations"][0]
    baseline = derive(tokens, profiles, configuration)

    taller_strip = copy.deepcopy(tokens)
    taller_strip["tool_strip"] += 8
    changed = derive(taller_strip, profiles, configuration)
    if changed[2] == baseline[2]:
        failures.append("a changed tool-strip token did not change the budget")

    narrow_document = copy.deepcopy(configuration)
    narrow_document["expected"] = [baseline[1] - 100, baseline[2]]
    if not any(
        "derives" in error
        for error in validate(narrow_document, tokens, profiles)
    ):
        failures.append("a wrong worked width was not detected")

    big_floor = copy.deepcopy(tokens)
    big_floor["document_width_min"] += 1000
    if not any(
        "below the" in error
        for error in validate(configuration, big_floor, profiles)
    ):
        failures.append("a document below the width minimum was not detected")

    wide_splitter = copy.deepcopy(tokens)
    wide_splitter["splitter"] += 10
    if derive(wide_splitter, profiles, configuration)[1] == baseline[1]:
        failures.append("a changed splitter token did not change the width")

    if failures:
        for failure in failures:
            print(f"layout budget self-test: {failure}", file=sys.stderr)
        return 1
    print("layout budget self-test detected all 4 mutations")
    return 0


def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()
    errors = run()
    if errors:
        for error in errors:
            print(f"layout budget: {error}", file=sys.stderr)
        return 1
    print(
        f"layout budget: {len(BUDGETS['configurations'])} configurations "
        "derive from the declared tokens"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
