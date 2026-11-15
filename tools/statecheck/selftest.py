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
    Facts,
    LiveTransition,
    Step,
    defaults,
    transition_rows,
)
from statecheck.events import request_allowed, validate_step
from statecheck.projection import project, vector_at_least
from statecheck.scenarios import run_scenario, scenario_named
from statecheck.transitions import compare_chapter, compare_figure, validate_transitions


def _broken_first(facts: Facts) -> str:
    """Return whether broken outranks stale in the projection order."""
    if not facts["accepted"]:
        return "Broken"
    return project(facts)


def _ignore_epoch(facts: Facts) -> str:
    """Return whether a response belongs to a superseded epoch."""
    if not facts["authorized"]:
        return "Denied"
    if facts["request_active"]:
        return "Refreshing"
    if facts["availability"] != "present" or not facts["accepted"]:
        return "Broken"
    fresh = vector_at_least(facts["accepted_validated"], facts["known_source"])
    return "Current" if fresh else "Stale"


def _present_only_request(facts: Facts) -> bool:
    """Return whether a request carries only present values."""
    return bool(facts["authorized"]) and facts["availability"] == "present"


class MutationChecks:
    """Accumulate the outcome of self-test mutations."""

    def __init__(self) -> None:
        self.count = 0
        self.failures: list[str] = []

    def require(self, condition: object, message: str) -> None:
        """Record one mutation check, retaining any failure message."""
        self.count += 1
        if not condition:
            self.failures.append(message)


def _edge_mutations(
    checks: MutationChecks, transitions: list[LiveTransition]
) -> None:
    """Yield mutations that break the declared edges."""
    without_revocation = [
        record for record in transitions if record["id"] != "authority-revoked"
    ]
    checks.require(
        any(
            "revocation is not available" in error
            for error in validate_transitions(without_revocation)
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
            for error in validate_transitions(without_absent_grant)
        ),
        "missing provider-absent grant edge was not detected",
    )

    wrong_owner = copy.deepcopy(transitions)
    for record in wrong_owner:
        if record["id"] == "refresh-denied":
            record["owner"] = "Host"
    checks.require(
        any("unknown transition" in error for error in compare_chapter(wrong_owner)),
        "owner drift from the chapter table was not detected",
    )


def _projection_mutations(checks: MutationChecks) -> None:
    """Yield mutations that break the projection order."""
    first_load: Facts = copy.deepcopy(defaults())
    first_load["request_active"] = True
    checks.require(
        _broken_first(first_load) != project(first_load),
        "Broken no-cache projection was not detected",
    )

    recovered: Facts = copy.deepcopy(defaults())
    recovered["accepted"] = True
    recovered["accepted_validated"] = {"rate": 1}
    recovered["invalidation_epoch"] = 1
    checks.require(
        _ignore_epoch(recovered) != project(recovered),
        "ignored invalidation epoch was not detected",
    )

    after_failure: Facts = copy.deepcopy(defaults())
    after_failure["availability"] = "uncertain"
    checks.require(
        _present_only_request(after_failure) != request_allowed(after_failure),
        "retry after an uncertain timeout was not detected",
    )


def _validation_mutations(checks: MutationChecks) -> None:
    """Require malformed reply identity fields to be rejected."""
    base: dict[str, object] = {
        "event": "refresh_succeeded",
        "expected": "Current",
        "generation": 1,
        "epoch": 0,
        "validated": {"rate": 1},
    }
    checks.require(
        not validate_step("self-test", 0, typ.cast("Step", base)),
        "a well-formed reply identity was rejected",
    )
    for field in ("generation", "epoch"):
        for invalid in (True, False):
            step = typ.cast("Step", {**base, field: invalid})
            checks.require(
                bool(validate_step("self-test", 0, step)),
                f"boolean {field} was not rejected",
            )
    vector_step = typ.cast("Step", {**base, "validated": {"rate": True}})
    checks.require(
        bool(validate_step("self-test", 0, vector_step)),
        "boolean validated component was not rejected",
    )


def _fixture_mutations(checks: MutationChecks) -> None:
    """Yield mutations that break the event fixtures."""
    for name in (
        "provider loss while denied is remembered",
        "superseded reply is discarded",
        "timeout then retry",
        "accepted vector advances source knowledge",
        "failure invalidates freshness before recovery",
        "source notification while broken with a provider",
        "source notification during Current",
    ):
        checks.require(
            not run_scenario(scenario_named(name)),
            f"{name} fixture does not pass",
        )
    checks.require(
        run_scenario(
            scenario_named("provider loss while denied is remembered"),
            observe_provider_while_denied=False,
        ),
        "provider facts ignored while denied were not detected",
    )
    checks.require(
        run_scenario(
            scenario_named("superseded reply is discarded"),
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
            for error in compare_figure(missing_event)
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
            for error in compare_figure(drifted_target)
        ),
        "figure target drift to another rendered label was not detected",
    )


def self_test() -> int:
    """Prove that each projection, fact, reply and figure mutation is caught."""
    checks = MutationChecks()
    transitions = copy.deepcopy(transition_rows())
    _edge_mutations(checks, transitions)
    _projection_mutations(checks)
    _validation_mutations(checks)
    _fixture_mutations(checks)
    _figure_mutation(checks, transitions)
    if checks.failures:
        for failure in checks.failures:
            print(f"state contract self-test: {failure}", file=sys.stderr)
        return 1
    print(f"state contract self-test detected all {checks.count} mutations")
    return 0
