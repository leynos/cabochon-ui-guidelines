"""Property tests for the live-state event rules.

Chapter 08 states its transitions as invariants rather than examples: a reply
that does not match the in-flight request never changes the accepted value, a
denied grant never projects anything but Denied, and each event leaves the
projection its own rule implies. These tests draw fact sets, reply identities
and event sequences from the declared vocabulary.
"""

from __future__ import annotations

import copy

from hypothesis import example, given
from hypothesis import strategies as st
from statecheck.contract import (
    DATA_PATH,
    FIXTURES_PATH,
    Facts,
    Step,
    defaults,
    load_document,
    states,
)
from statecheck.events import EVENTS, PROVIDER_EVENTS, REPLY_FIELDS, apply
from statecheck.projection import project

DATA = load_document(DATA_PATH)
FIXTURES = load_document(FIXTURES_PATH)
DEFAULT_FACTS = defaults(FIXTURES)
STATE_NAMES = states(DATA)
REPLY_EVENTS = frozenset(REPLY_FIELDS)
VECTORS = st.dictionaries(
    st.sampled_from(["document", "profile", "rate"]),
    st.integers(min_value=0, max_value=8),
    min_size=1,
    max_size=3,
)
EPOCHS = st.integers(min_value=0, max_value=6)
GENERATIONS = st.integers(min_value=1, max_value=6)
AVAILABILITY = st.sampled_from(sorted({"present", "uncertain", "lost"}))


def facts_for(overrides: dict[str, object]) -> Facts:
    """Return a complete fact set with the drawn facts applied."""
    facts: Facts = copy.deepcopy(DEFAULT_FACTS)
    facts.update(overrides)  # type: ignore[typeddict-item]
    return facts


def _step(event: str, facts: Facts, match: bool, vector: dict[str, int]) -> Step:
    """Return an event step, matching the in-flight request when asked.

    A matching reply reuses the in-flight generation and epoch and validates
    every value the request claimed to cover. The drawn vector supplies the
    rest of the reply, but the required value wins wherever it is higher, so
    a matching reply always covers the source it must. Any other reply shifts
    the generation, so the rule must ignore it whatever it validates.
    """
    step: Step = {"event": event, "expected": "Current"}
    if event not in REPLY_EVENTS:
        return step
    step["generation"] = (
        facts["request_generation"] if match else facts["request_generation"] + 1
    )
    if event == "refresh_cancelled":
        return step
    step["epoch"] = (
        facts["invalidation_epoch"] if match else facts["invalidation_epoch"] + 1
    )
    if event == "refresh_succeeded":
        if not match:
            step["validated"] = vector
        else:
            required = {**facts["known_source"], **facts["request_covers"]}
            step["validated"] = {
                key: max(value, required.get(key, 0))
                for key, value in {**required, **vector}.items()
            }
    return step


@given(
    st.lists(
        st.tuples(st.sampled_from(sorted(EVENTS)), st.booleans(), VECTORS),
        max_size=6,
    )
)
@example(
    [
        ("refresh_requested", True, {"rate": 1}),
        ("refresh_succeeded", True, {"rate": 2}),
    ]
)
@example(
    [
        ("refresh_requested", True, {"rate": 1}),
        ("refresh_succeeded", True, {"rate": 0}),
    ]
)
@example(
    [
        ("refresh_requested", True, {"rate": 1}),
        ("refresh_failed", True, {"rate": 2}),
        ("refresh_succeeded", True, {"rate": 2}),
    ]
)
@example(
    [
        ("refresh_requested", True, {"rate": 1}),
        ("refresh_succeeded", False, {"rate": 2}),
    ]
)
@example(
    [
        ("source_advanced", True, {"rate": 1}),
        ("refresh_succeeded", True, {"rate": 3}),
    ]
)
@example(
    [
        ("grant_revoked", True, {"rate": 1}),
        ("provider_lost", True, {"rate": 1}),
        ("grant_issued", True, {"rate": 1}),
        ("refresh_requested", True, {"rate": 1}),
    ]
)
def test_each_event_leaves_the_projection_its_rule_implies(
    drawn: list[tuple[str, bool, dict[str, int]]],
) -> None:
    """Every event's effect decides the projection that follows it.

    Half the drawn replies match the in-flight request and half do not, so
    both the accepted and the ignored reply are covered. A dispatch is
    expected from the facts before the event rather than from what the
    handler did, so a dispatch that changes nothing fails here. An applied
    event must leave the projection its own rule requires, so a rule that
    writes the wrong facts fails here rather than merely leaving the state
    undeclared.
    """
    facts = facts_for({"authorized": True})
    assert project(facts) == "Broken", (
        "a cache that has accepted nothing projects Broken"
    )
    for event, match, vector in drawn:
        step = _step(event, facts, match, vector)
        before = copy.deepcopy(facts)
        projection_before = project(facts)
        apply(facts, step)
        projection = project(facts)
        assert projection in STATE_NAMES, "the projection stays declared"
        changed = facts != before
        if event in REPLY_EVENTS:
            permitted = before["request_active"] and (
                before["authorized"] or event == "refresh_cancelled"
            )
            assert changed == (match and permitted), (
                "only a permitted reply that matches the request changes a fact"
            )
        if event in {"refresh_requested", "source_advanced"}:
            dispatch = before["authorized"] and before["availability"] in (
                {"present", "uncertain"}
                if event == "refresh_requested"
                else {"present"}
            )
            assert changed == dispatch, (
                "a permitted dispatch changes the facts and a refused one does not"
            )
            assert projection == ("Refreshing" if dispatch else projection_before), (
                "a permitted dispatch projects Refreshing and a refused one "
                "leaves the projection untouched"
            )
        elif event == "refresh_succeeded":
            assert projection == ("Current" if changed else projection_before), (
                "an accepted reply projects Current and an ignored one changes "
                "nothing"
            )
            if changed:
                assert facts["accepted_validated"] == step["validated"], (
                    "the matching reply's vector becomes the accepted value"
                )
        elif event == "refresh_failed":
            assert projection == ("Broken" if changed else projection_before), (
                "a refused source projects Broken and an ignored reply changes "
                "nothing"
            )
        elif event == "grant_revoked":
            assert projection == "Denied", "a revoked grant always projects Denied"
        elif event == "provider_lost":
            assert projection == (
                "Denied" if not facts["authorized"] else "Broken"
            ), "a lost provider projects Broken unless the grant is denied"
        else:
            assert changed or projection == projection_before, (
                "an event that changes nothing leaves the projection alone"
            )


@given(VECTORS, VECTORS, GENERATIONS, EPOCHS)
def test_a_reply_from_another_generation_never_changes_the_accepted_value(
    accepted: dict[str, int],
    reply: dict[str, int],
    generation: int,
    epoch: int,
) -> None:
    """A success carrying a superseded generation is ignored whole."""
    facts = facts_for(
        {
            "availability": "uncertain",
            "accepted": True,
            "accepted_validated": accepted,
            "accepted_epoch": epoch,
            "invalidation_epoch": epoch,
            "request_active": True,
            "request_generation": generation,
            "request_covers": dict(accepted),
        }
    )
    before = copy.deepcopy(facts)
    apply(
        facts,
        {
            "event": "refresh_succeeded",
            "expected": "Current",
            "generation": generation + 1,
            "epoch": epoch,
            "validated": reply,
        },
    )
    assert facts == before, (
        "a reply from another generation changes no accepted fact"
    )


@given(VECTORS, VECTORS, GENERATIONS, EPOCHS)
def test_a_reply_from_another_epoch_never_changes_the_accepted_value(
    accepted: dict[str, int],
    reply: dict[str, int],
    generation: int,
    epoch: int,
) -> None:
    """A success invalidated since the request is ignored whole."""
    facts = facts_for(
        {
            "availability": "uncertain",
            "accepted": True,
            "accepted_validated": accepted,
            "accepted_epoch": epoch,
            "invalidation_epoch": epoch,
            "request_active": True,
            "request_generation": generation,
            "request_covers": dict(accepted),
        }
    )
    before = copy.deepcopy(facts)
    apply(
        facts,
        {
            "event": "refresh_succeeded",
            "expected": "Current",
            "generation": generation,
            "epoch": epoch + 1,
            "validated": reply,
        },
    )
    assert facts == before, (
        "a reply invalidated since the request changes no accepted fact"
    )


@given(st.sampled_from(sorted(PROVIDER_EVENTS)), AVAILABILITY)
def test_a_provider_change_while_denied_leaves_the_grant_denied(
    event: str, availability: str
) -> None:
    """Observing the provider cannot restore a revoked grant."""
    facts = facts_for({"authorized": False, "availability": availability})
    apply(facts, {"event": event, "expected": "Denied"})
    assert project(facts) == "Denied", (
        "a provider change cannot restore a revoked grant"
    )


@given(GENERATIONS, EPOCHS, VECTORS)
def test_a_success_while_denied_is_ignored(
    generation: int, epoch: int, validated: dict[str, int]
) -> None:
    """A reply cannot accept data without the grant that requested it."""
    facts = facts_for(
        {
            "authorized": False,
            "request_active": True,
            "request_generation": generation,
            "invalidation_epoch": epoch,
        }
    )
    before = copy.deepcopy(facts)
    apply(
        facts,
        {
            "event": "refresh_succeeded",
            "expected": "Denied",
            "generation": generation,
            "epoch": epoch,
            "validated": validated,
        },
    )
    assert facts == before, "a success while denied changes no fact"
    assert project(facts) == "Denied", "the grant stays denied"


@given(VECTORS, GENERATIONS, EPOCHS)
def test_a_matching_reply_that_under_covers_the_source_is_ignored(
    reply: dict[str, int], generation: int, epoch: int
) -> None:
    """A reply at the request's identity is ignored unless it covers the source.

    The reply carries the in-flight generation and epoch, so only its
    coverage can refuse it. Every drawn component sits one below the value
    the source already knows, which no covering reply may do.
    """
    known = {key: value + 1 for key, value in reply.items()}
    facts = facts_for(
        {
            "availability": "uncertain",
            "known_source": known,
            "request_active": True,
            "request_generation": generation,
            "request_covers": dict(known),
            "invalidation_epoch": epoch,
        }
    )
    before = copy.deepcopy(facts)
    apply(
        facts,
        {
            "event": "refresh_succeeded",
            "expected": "Refreshing",
            "generation": generation,
            "epoch": epoch,
            "validated": dict(reply),
        },
    )
    assert facts == before, (
        "a reply that under-covers the known source changes no fact"
    )
    assert project(facts) == "Refreshing", "the under-covering reply leaves the request"


@given(st.integers(min_value=1, max_value=8), GENERATIONS, EPOCHS)
def test_a_matching_success_accepts_the_reply(
    rate: int, generation: int, epoch: int
) -> None:
    """A covering reply at the current identity becomes the accepted value."""
    facts = facts_for(
        {
            "availability": "uncertain",
            "request_active": True,
            "request_generation": generation,
            "invalidation_epoch": epoch,
        }
    )
    apply(
        facts,
        {
            "event": "refresh_succeeded",
            "expected": "Current",
            "generation": generation,
            "epoch": epoch,
            "validated": {"rate": rate},
        },
    )
    assert facts["accepted"] is True, "the matching reply becomes the accepted value"
    assert facts["accepted_validated"] == {"rate": rate}, (
        "the accepted vector is the reply's own vector"
    )
    assert facts["request_active"] is False, "the request is no longer in flight"
    assert project(facts) == "Current", "the accepted reply projects Current"
