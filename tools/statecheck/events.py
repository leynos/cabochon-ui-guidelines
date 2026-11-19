"""Validate fixture events and apply them to the fact set.

The `validate_step` and `apply` functions check each fixture step's shape and
derive its effect on the `Facts` record. `statecheck.scenarios` and
`statecheck.selftest` import them.
"""

from __future__ import annotations

import typing as typ

from statecheck.contract import ContractError, Facts, Step
from statecheck.projection import NO_MUTATION, Mutation, vector_at_least

if typ.TYPE_CHECKING:
    import collections.abc as cabc

NO_DATA_EVENTS = {
    "grant_revoked",
    "grant_issued",
    "provider_lost",
    "provider_recovered",
    "source_advanced",
    "refresh_requested",
}
REPLY_FIELDS = {
    "refresh_succeeded": ("generation", "epoch", "validated"),
    "refresh_failed": ("generation", "epoch"),
    "refresh_cancelled": ("generation",),
}
EVENTS = NO_DATA_EVENTS | set(REPLY_FIELDS)
PROVIDER_EVENTS = {"provider_lost", "provider_recovered"}


def _is_integer(value: object, minimum: int) -> bool:
    """Return whether a value is an integer, not a boolean, at least minimum."""
    if isinstance(value, bool):
        return False
    if not isinstance(value, int):
        return False
    return value >= minimum


def _is_source_value(value: object) -> bool:
    """Return whether a fixture source value is well formed."""
    return _is_integer(value, 0)


def _valid_vector(value: object) -> bool:
    """Return whether a fixture guard vector is well formed."""
    if not isinstance(value, dict) or not value:
        return False
    return all(
        isinstance(key, str) and _is_source_value(item) for key, item in value.items()
    )


def _validate_identity_field(
    value: object, field: str, where: str, errors: list[str]
) -> None:
    """Check that an identity field declares a usable value."""
    if value is None:
        errors.append(f"{where}: missing reply field {field!r}")
        return
    if field == "validated":
        if not _valid_vector(value):
            errors.append(
                f"{where}: validated vector is not a non-empty "
                "map of names to non-negative integers"
            )
        return
    minimum = 1 if field == "generation" else 0
    if not _is_integer(value, minimum):
        qualifier = "positive" if field == "generation" else "non-negative"
        errors.append(f"{where}: {field} is not a {qualifier} integer")


def validate_step(
    scenario: str, index: int, step: Step, states: cabc.Set[str]
) -> list[str]:
    """Check that a fixture step carries exactly the data its event needs.

    Parameters
    ----------
    scenario
        The fixture name, repeated in every message.
    index
        The zero-based position of the step within its fixture.
    step
        The fixture step to validate.
    states
        The live state names the contract declares.

    Returns
    -------
    list[str]
        Every defect the step declares, or an empty list.
    """
    errors: list[str] = []
    event = step.get("event")
    where = f"scenario {scenario!r} step {index + 1}"
    if event not in EVENTS:
        return [f"{where}: unknown event {event!r}"]
    if step.get("expected") not in states:
        errors.append(f"{where}: invalid expected state {step.get('expected')!r}")
    fields = REPLY_FIELDS.get(str(event), ())
    allowed = {"event", "expected"} | set(fields)
    extra = set(step) - allowed
    if extra:
        errors.append(f"{where}: unexpected fields {sorted(extra)!r}")
    declared: dict[str, object] = {
        "generation": step.get("generation"),
        "epoch": step.get("epoch"),
        "validated": step.get("validated"),
    }
    for field in fields:
        _validate_identity_field(declared[field], field, where, errors)
    return errors


def _grant_revoked(facts: Facts, step: Step) -> None:
    """Derive the facts of a revoked grant."""
    facts["authorized"] = False
    facts["request_active"] = False
    facts["invalidation_epoch"] += 1


def _grant_issued(facts: Facts, step: Step) -> None:
    """Derive the facts of a newly issued grant."""
    facts["authorized"] = True


def _source_advanced(facts: Facts, step: Step) -> None:
    """Derive the facts of a source advance since the token."""
    if not facts["authorized"] or facts["availability"] != "present":
        return
    for key in facts["known_source"]:
        facts["known_source"][key] += 1
    # The notification supersedes any in-flight generation. When nothing is in
    # flight it dispatches a refresh, exactly as an explicit request does.
    facts["request_generation"] += 1
    facts["request_active"] = True
    facts["request_covers"] = dict(facts["known_source"])


def request_allowed(facts: Facts, mutation: Mutation = NO_MUTATION) -> bool:
    """Derive whether the request is permitted.

    Parameters
    ----------
    facts
        The fact set the request would be issued from.
    mutation
        A deviation the self-test asks for; ``present_only`` refuses a request
        whose source is merely uncertain.
    """
    if not facts["authorized"]:
        return False
    if mutation.present_only:
        return facts["availability"] == "present"
    return facts["availability"] in {"present", "uncertain"}


def _refresh_requested(facts: Facts, step: Step, mutation: Mutation) -> None:
    """Derive the facts of a permitted refresh request."""
    if not request_allowed(facts, mutation):
        return
    facts["request_generation"] += 1
    facts["request_active"] = True
    facts["request_covers"] = dict(facts["known_source"])


def _merge_known_source(facts: Facts, validated: dict[str, int]) -> None:
    """Merge a provider response into a known source value."""
    known = facts["known_source"]
    for key, value in validated.items():
        known[key] = max(known.get(key, 0), value)


def _success_matches(facts: Facts, step: Step, *, check_reply_identity: bool) -> bool:
    """Return whether a success response matches the request."""
    if not check_reply_identity:
        return True
    identity = (
        step["generation"] == facts["request_generation"]
        and step["epoch"] == facts["invalidation_epoch"]
    )
    coverage = vector_at_least(
        step["validated"], facts["known_source"]
    ) and vector_at_least(step["validated"], facts["request_covers"])
    return identity and coverage


def _refresh_succeeded(
    facts: Facts, step: Step, *, check_reply_identity: bool
) -> None:
    """Derive the state after a successful refresh."""
    if not facts["authorized"] or not facts["request_active"]:
        return
    if not _success_matches(facts, step, check_reply_identity=check_reply_identity):
        return
    facts["request_active"] = False
    facts["availability"] = "present"
    facts["accepted"] = True
    facts["accepted_validated"] = dict(step["validated"])
    facts["accepted_epoch"] = facts["invalidation_epoch"]
    _merge_known_source(facts, step["validated"])


def _failure_matches(facts: Facts, step: Step, *, check_reply_identity: bool) -> bool:
    """Return whether a failure response matches the request."""
    if not check_reply_identity:
        return True
    return (
        step["generation"] == facts["request_generation"]
        and step["epoch"] == facts["invalidation_epoch"]
    )


def _refresh_failed(facts: Facts, step: Step, *, check_reply_identity: bool) -> None:
    """Derive the state after a failed refresh."""
    if not facts["authorized"] or not facts["request_active"]:
        return
    if not _failure_matches(facts, step, check_reply_identity=check_reply_identity):
        return
    facts["request_active"] = False
    facts["availability"] = "uncertain"
    # A failure invalidates freshness: a later provider recovery must project
    # Stale until a new validated reply is accepted.
    facts["invalidation_epoch"] += 1


def _cancel_matches(facts: Facts, step: Step, *, check_reply_identity: bool) -> bool:
    """Return whether a cancellation matches the request."""
    return not check_reply_identity or step["generation"] == facts["request_generation"]


def _refresh_cancelled(
    facts: Facts, step: Step, *, check_reply_identity: bool
) -> None:
    """Derive the state after a cancelled refresh."""
    if not facts["request_active"]:
        return
    if not _cancel_matches(facts, step, check_reply_identity=check_reply_identity):
        return
    facts["request_active"] = False


PLAIN_HANDLERS: dict[str, cabc.Callable[[Facts, Step], None]] = {
    "grant_revoked": _grant_revoked,
    "grant_issued": _grant_issued,
    "source_advanced": _source_advanced,
}


class ReplyHandler(typ.Protocol):
    """A reply handler that can be told to ignore reply identity."""

    def __call__(
        self, facts: Facts, step: Step, *, check_reply_identity: bool
    ) -> None:
        """Apply the reply to the fact set."""


REPLY_HANDLERS: dict[str, ReplyHandler] = {
    "refresh_succeeded": _refresh_succeeded,
    "refresh_failed": _refresh_failed,
    "refresh_cancelled": _refresh_cancelled,
}


def _provider_event(facts: Facts, step: Step, *, observe: bool) -> None:
    """Derive the state a provider event projects."""
    if not observe and not facts["authorized"]:
        return
    if step["event"] == "provider_lost":
        facts["availability"] = "lost"
        facts["request_active"] = False
        facts["invalidation_epoch"] += 1
        return
    facts["availability"] = "present"


def apply(  # ruff: ignore[too-many-arguments]  # pylint: disable=too-many-arguments
    facts: Facts,
    step: Step,
    *,
    observe_provider_while_denied: bool = True,
    check_reply_identity: bool = True,
    mutation: Mutation = NO_MUTATION,
) -> None:
    """Apply one event and its reply identity to the fact set.

    Parameters
    ----------
    facts
        The fact set to advance; updated in place.
    step
        The event to apply.
    observe_provider_while_denied
        Whether a provider event is recorded while the grant is denied.
    check_reply_identity
        Whether a reply must match the in-flight request's identity.
    mutation
        A deviation from the request policy that the self-test asks for.

    Raises
    ------
    ContractError
        If the step names an event the contract does not declare.
    """
    event = step["event"]
    if event in PROVIDER_EVENTS:
        _provider_event(facts, step, observe=observe_provider_while_denied)
        return
    if event == "refresh_requested":
        _refresh_requested(facts, step, mutation)
        return
    if event in PLAIN_HANDLERS:
        PLAIN_HANDLERS[event](facts, step)
        return
    handler = REPLY_HANDLERS.get(event)
    if handler is None:
        raise ContractError(f"unknown fixture event {event!r}")
    handler(facts, step, check_reply_identity=check_reply_identity)
