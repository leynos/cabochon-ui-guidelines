"""Prove that the state contract rejects the mutations it claims to catch.

The `self_test` function mutates the transitions, projection and fixtures and
requires each defect to surface through the sibling checks.
`statecheck.cli` invokes it for `--self-test`.
"""

from __future__ import annotations

import copy
import sys
import typing as typ

from statecheck.contract import (
    CHAPTER,
    DATA_PATH,
    FIGURE,
    FIXTURES_PATH,
    Contract,
    LiveTransition,
    Step,
    load_contract,
)
from statecheck.events import validate_step
from statecheck.projection import Mutation
from statecheck.scenarios import run_scenario, scenario_named
from statecheck.transitions import compare_chapter, compare_figure, validate_transitions


class MutationChecks:
    """Accumulate the outcome of self-test mutations."""

    def __init__(self) -> None:
        """Start with no checks counted and no failures recorded."""
        self.count = 0
        self.failures: list[str] = []

    def require(self, condition: object, message: str) -> None:
        """Record one mutation check, retaining any failure message."""
        self.count += 1
        if not condition:
            self.failures.append(message)


def _edge_mutations(
    checks: MutationChecks, transitions: list[LiveTransition], contract: Contract
) -> None:
    """Yield mutations that break the declared edges."""
    without_revocation = [
        record for record in transitions if record["id"] != "authority-revoked"
    ]
    checks.require(
        any(
            "revocation is not available" in error
            for error in validate_transitions(without_revocation, contract)
        ),
        "missing revocation edge was not detected",
    )

    without_absent_grant = [
        record
        for record in transitions
        if record["id"] != "grant-issued-provider-absent"
    ]
    checks.require(
        any(
            "provider is absent is not modelled" in error
            for error in validate_transitions(without_absent_grant, contract)
        ),
        "missing provider-absent grant edge was not detected",
    )

    wrong_owner = copy.deepcopy(transitions)
    for record in wrong_owner:
        if record["id"] == "refresh-denied":
            record["owner"] = "Host"
    checks.require(
        any(
            "unknown transition" in error
            for error in compare_chapter(wrong_owner, CHAPTER)
        ),
        "owner drift from the chapter table was not detected",
    )


def _projection_mutations(checks: MutationChecks, contract: Contract) -> None:
    """Require the fixtures to catch each deviation from the declared rules."""
    checks.require(
        run_scenario(
            scenario_named("first load without a cached value", contract.fixtures),
            contract,
            mutation=Mutation(broken_first=True),
        ),
        "Broken no-cache projection was not detected",
    )
    checks.require(
        run_scenario(
            scenario_named(
                "failure invalidates freshness before recovery", contract.fixtures
            ),
            contract,
            mutation=Mutation(ignore_epoch=True),
        ),
        "ignored invalidation epoch was not detected",
    )
    checks.require(
        run_scenario(
            scenario_named("timeout then retry", contract.fixtures),
            contract,
            mutation=Mutation(present_only=True),
        ),
        "retry after an uncertain timeout was not detected",
    )


def _validation_mutations(checks: MutationChecks, contract: Contract) -> None:
    """Require malformed reply identity fields to be rejected."""
    base: dict[str, object] = {
        "event": "refresh_succeeded",
        "expected": "Current",
        "generation": 1,
        "epoch": 0,
        "validated": {"rate": 1},
    }
    checks.require(
        not validate_step("self-test", 0, typ.cast("Step", base), contract.states),
        "a well-formed reply identity was rejected",
    )
    for field in ("generation", "epoch"):
        for invalid in (True, False):
            step = typ.cast("Step", {**base, field: invalid})
            checks.require(
                bool(validate_step("self-test", 0, step, contract.states)),
                f"boolean {field} was not rejected",
            )
    vector_step = typ.cast("Step", {**base, "validated": {"rate": True}})
    checks.require(
        bool(validate_step("self-test", 0, vector_step, contract.states)),
        "boolean validated component was not rejected",
    )


def _fixture_mutations(checks: MutationChecks, contract: Contract) -> None:
    """Yield mutations that break the event fixtures."""
    for name in (
        "first load without a cached value",
        "provider loss while denied is remembered",
        "superseded reply is discarded",
        "timeout then retry",
        "accepted vector advances source knowledge",
        "failure invalidates freshness before recovery",
        "source notification while broken with a provider",
        "source notification during Current",
    ):
        checks.require(
            not run_scenario(
                scenario_named(name, contract.fixtures), contract
            ),
            f"{name} fixture does not pass",
        )
    checks.require(
        run_scenario(
            scenario_named(
                "provider loss while denied is remembered", contract.fixtures
            ),
            contract,
            observe_provider_while_denied=False,
        ),
        "provider facts ignored while denied were not detected",
    )
    checks.require(
        run_scenario(
            scenario_named("superseded reply is discarded", contract.fixtures),
            contract,
            check_reply_identity=False,
        ),
        "ignored reply identity was not detected",
    )


def _figure_mutation(
    checks: MutationChecks, transitions: list[LiveTransition]
) -> None:
    """Yield the mutations that break a misplaced figure mark or label."""
    missing_event = copy.deepcopy(transitions)
    missing_event[0]["event"] = "An event the figure omits"
    checks.require(
        any(
            "figure does not render event" in error
            for error in compare_figure(missing_event, FIGURE)
        ),
        "figure drift from the typed source was not detected",
    )

    drifted_target = copy.deepcopy(transitions)
    for record in drifted_target:
        if record["id"] == "refresh-current":
            record["to"] = "Broken"
    checks.require(
        any(
            "figure does not render to" in error
            for error in compare_figure(drifted_target, FIGURE)
        ),
        "figure target drift to another rendered label was not detected",
    )


def self_test() -> int:
    """Prove that each projection, fact, reply and figure mutation is caught."""
    checks = MutationChecks()
    contract = load_contract(DATA_PATH, FIXTURES_PATH)
    transitions = copy.deepcopy(contract.transitions)
    _edge_mutations(checks, transitions, contract)
    _projection_mutations(checks, contract)
    _validation_mutations(checks, contract)
    _fixture_mutations(checks, contract)
    _figure_mutation(checks, transitions)
    if checks.failures:
        for failure in checks.failures:
            print(f"state contract self-test: {failure}", file=sys.stderr)
        return 1
    print(f"state contract self-test detected all {checks.count} mutations")
    return 0
