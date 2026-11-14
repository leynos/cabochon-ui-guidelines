#!/usr/bin/env python3
"""Check the declared Escape routing order.

Chapter 18 fixes one order: composition, completion, text draft, transient
surface, tool. The completion-before-draft rule is easy to state and easy to
implement backwards, so this checker runs ordered Escape fixtures. The first
Escape in the central fixture must leave the draft text and its dirty flag
untouched while removing the completion.

Run from the repository root with ``python3 -I tools/check-keyboard.py``. Pass
``--self-test`` to prove that reversing the order or clearing the draft on
completion dismissal is detected.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = json.loads(
    (ROOT / "tools" / "keyboard-fixtures.json").read_text(encoding="utf-8")
)
FACT_KEYS = set(FIXTURES["defaults"])


def validate_step(scenario: str, index: int, step: dict[str, object]) -> list[str]:
    """Check that an expectation names known facts with the right types."""
    errors: list[str] = []
    expected = step.get("expected")
    where = f"scenario {scenario!r} step {index + 1}"
    if not isinstance(expected, dict) or not expected:
        return [f"{where}: no expected facts"]
    unknown = set(expected) - FACT_KEYS
    if unknown:
        errors.append(f"{where}: unknown facts {sorted(unknown)!r}")
    for key, value in expected.items():
        if key in FACT_KEYS and type(value) is not type(FIXTURES["defaults"][key]):
            errors.append(f"{where}: {key!r} has the wrong type")
    return errors


def apply_escape(
    facts: dict[str, object],
    *,
    completion_first: bool = True,
    clear_draft_on_completion: bool = False,
) -> None:
    """Apply the chapter's Escape order to one mutable fact set."""
    if facts["composition"]:
        facts["composition"] = False
        return
    if completion_first and facts["completion_open"]:
        facts["completion_open"] = False
        if clear_draft_on_completion and facts["draft_dirty"]:
            facts["draft"] = facts["committed"]
            facts["draft_dirty"] = False
        return
    if facts["mode"] == "text":
        facts["draft"] = facts["committed"]
        facts["draft_dirty"] = False
        facts["mode"] = "navigation"
        return
    if not completion_first and facts["completion_open"]:
        facts["completion_open"] = False
        return
    if facts["surface_open"]:
        facts["surface_open"] = False
        return
    if facts["tool_gesture"]:
        facts["tool_gesture"] = False


def run_scenario(
    scenario: dict[str, object],
    *,
    completion_first: bool = True,
    clear_draft_on_completion: bool = False,
) -> list[str]:
    """Run one Escape sequence and report every expectation mismatch."""
    errors: list[str] = []
    facts = copy.deepcopy(FIXTURES["defaults"])
    facts.update(copy.deepcopy(scenario.get("facts", {})))
    for index, step in enumerate(scenario["steps"]):
        step_errors = validate_step(str(scenario["name"]), index, step)
        if step_errors:
            errors.extend(step_errors)
            continue
        apply_escape(
            facts,
            completion_first=completion_first,
            clear_draft_on_completion=clear_draft_on_completion,
        )
        for key, expected in step["expected"].items():
            if facts[key] != expected:
                errors.append(
                    f"scenario {scenario['name']!r} after Escape "
                    f"{index + 1}: {key} is {facts[key]!r}, "
                    f"expected {expected!r}"
                )
    return errors


def run_scenarios() -> list[str]:
    errors: list[str] = []
    for scenario in FIXTURES["scenarios"]:
        errors.extend(run_scenario(scenario))
    return errors


def main() -> int:
    if "--self-test" in sys.argv:
        failures: list[str] = []
        checks = 0
        scenario = next(
            (
                scenario
                for scenario in FIXTURES["scenarios"]
                if scenario["name"]
                == "first Escape dismisses completion before the draft"
            ),
            None,
        )
        if scenario is None:
            print(
                "keyboard self-test: central fixture is missing",
                file=sys.stderr,
            )
            return 1
        if run_scenario(scenario):
            failures.append("central completion-before-draft fixture does not pass")
            checks += 1

        for label, options in (
            ("draft reverted before completion", {"completion_first": False}),
            (
                "draft cleared when completion is dismissed",
                {"clear_draft_on_completion": True},
            ),
        ):
            checks += 1
            if not run_scenario(scenario, **options):
                failures.append(f"{label} was not detected")

        if failures:
            for failure in failures:
                print(f"keyboard self-test: {failure}", file=sys.stderr)
            return 1
        print(f"keyboard: self-test detected all {checks} mutations")
        return 0

    errors = run_scenarios()
    if errors:
        for error in errors:
            print(f"keyboard: {error}", file=sys.stderr)
        return 1
    print(
        f"keyboard: ok ({len(FIXTURES['scenarios'])} ordered Escape scenarios)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())