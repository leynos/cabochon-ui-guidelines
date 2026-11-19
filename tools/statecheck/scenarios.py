"""Run the fixture event sequences against the declared projection.

The `run_scenario` and `run_scenarios` functions apply each step from the
loaded fixture document and compare the projected state with the expected one.
`statecheck.cli` and `statecheck.selftest` import them.
"""

from __future__ import annotations

import copy

from statecheck.contract import (
    Contract,
    ContractError,
    Facts,
    Scenario,
    defaults,
    scenarios,
)
from statecheck.events import apply, validate_step
from statecheck.projection import NO_MUTATION, Mutation, project


def run_scenario(  # ruff: ignore[too-many-arguments]  # pylint: disable=too-many-arguments
    scenario: Scenario,
    contract: Contract,
    *,
    observe_provider_while_denied: bool = True,
    check_reply_identity: bool = True,
    mutation: Mutation = NO_MUTATION,
) -> list[str]:
    """Run one fixture sequence and report every projection mismatch.

    Parameters
    ----------
    scenario
        The fixture sequence to run.
    contract
        The loaded contract that supplies the default facts and state names.
    observe_provider_while_denied
        Whether a provider event is recorded while the grant is denied.
    check_reply_identity
        Whether a reply must match the in-flight request's identity.
    mutation
        A deviation from the declared rules that the self-test asks for. The
        fixture's own expected states must report it.

    Returns
    -------
    list[str]
        Every defect the sequence declares, or an empty list.
    """
    errors: list[str] = []
    facts: Facts = copy.deepcopy(defaults(contract.fixtures))
    facts.update(copy.deepcopy(scenario.get("facts", {})))
    for index, step in enumerate(scenario["events"]):
        step_errors = validate_step(
            str(scenario["name"]), index, step, contract.states
        )
        if step_errors:
            errors.extend(step_errors)
            continue
        apply(
            facts,
            step,
            observe_provider_while_denied=observe_provider_while_denied,
            check_reply_identity=check_reply_identity,
            mutation=mutation,
        )
        actual = project(facts, mutation)
        if actual != step["expected"]:
            errors.append(
                f"scenario {scenario['name']!r} after {step['event']!r}: "
                f"projected {actual}, expected {step['expected']}"
            )
    return errors


def run_scenarios(contract: Contract) -> list[str]:
    """Run every fixture sequence and return all projection mismatches."""
    errors: list[str] = []
    for scenario in scenarios(contract.fixtures):
        errors.extend(run_scenario(scenario, contract))
    return errors


def scenario_named(name: str, fixtures: dict[str, object]) -> Scenario:
    """Return the named fixture, or report that the fixture is missing.

    Parameters
    ----------
    name
        The fixture name to find.
    fixtures
        The decoded fixture document to search.

    Returns
    -------
    Scenario
        The matching fixture sequence.

    Raises
    ------
    ContractError
        If the document declares no fixture with the given name.
    """
    for scenario in scenarios(fixtures):
        if scenario["name"] == name:
            return scenario
    raise ContractError(f"fixture {name!r} is missing")
