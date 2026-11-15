"""Run the fixture event sequences against the declared projection.

The `run_scenario` and `run_scenarios` functions apply each step from
`tools/state-fixtures.json` and compare the projected state with the expected
one. `statecheck.cli` and `statecheck.selftest` import them.
"""

from __future__ import annotations

import copy

from statecheck.contract import Facts, Scenario, defaults, scenarios
from statecheck.events import apply, validate_step
from statecheck.projection import project


def run_scenario(
    scenario: Scenario,
    *,
    observe_provider_while_denied: bool = True,
    check_reply_identity: bool = True,
) -> list[str]:
    """Run one fixture sequence and report every projection mismatch."""
    errors: list[str] = []
    facts: Facts = copy.deepcopy(defaults())
    facts.update(copy.deepcopy(scenario.get("facts", {})))
    for index, step in enumerate(scenario["events"]):
        step_errors = validate_step(str(scenario["name"]), index, step)
        if step_errors:
            errors.extend(step_errors)
            continue
        apply(
            facts,
            step,
            observe_provider_while_denied=observe_provider_while_denied,
            check_reply_identity=check_reply_identity,
        )
        actual = project(facts)
        if actual != step["expected"]:
            errors.append(
                f"scenario {scenario['name']!r} after {step['event']!r}: "
                f"projected {actual}, expected {step['expected']}"
            )
    return errors


def run_scenarios() -> list[str]:
    """Run every fixture sequence and return all projection mismatches."""
    errors: list[str] = []
    for scenario in scenarios():
        errors.extend(run_scenario(scenario))
    return errors


def scenario_named(name: str) -> Scenario:
    """Return the named fixture, or stop when the fixture is missing."""
    for scenario in scenarios():
        if scenario["name"] == name:
            return scenario
    raise SystemExit(f"state contract: fixture {name!r} is missing")
