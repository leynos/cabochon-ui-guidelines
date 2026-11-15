"""Property tests for the live-state event rules.

Chapter 08 states its transitions as invariants rather than examples: a reply
that does not match the in-flight request never changes the accepted value, a
denied grant never projects anything but Denied, and every prefix of an event
sequence projects one of the declared states. These tests draw fact sets, reply
identities and event sequences from the declared vocabulary.
"""

from __future__ import annotations

import copy
import typing as typ

from hypothesis import given
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
from statecheck.events import EVENTS, PROVIDER_EVENTS, apply
from statecheck.projection import project

DATA = load_document(DATA_PATH)
FIXTURES = load_document(FIXTURES_PATH)
DEFAULT_FACTS = defaults(FIXTURES)
STATE_NAMES = states(DATA)
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


def step_for(event: str) -> st.SearchStrategy[Step]:
    """Return a strategy for one well-formed event of the given kind."""
    fields: dict[str, st.SearchStrategy[object]] = {
        "event": st.just(event),
        "expected": st.just("Current"),
    }
    if event == "refresh_succeeded":
        fields |= {
            "generation": GENERATIONS,
            "epoch": EPOCHS,
            "validated": VECTORS,
        }
    elif event == "refresh_failed":
        fields |= {"generation": GENERATIONS, "epoch": EPOCHS}
    elif event == "refresh_cancelled":
        fields |= {"generation": GENERATIONS}
    return st.fixed_dictionaries(fields).map(lambda raw: typ.cast("Step", raw))


@given(
    st.lists(
        st.sampled_from(sorted(EVENTS)).flatmap(step_for),
        max_size=6,
    )
)
def test_an_event_sequence_never_leaves_the_declared_states(
    steps: list[Step],
) -> None:
    """Every prefix of declared events keeps a declared projection."""
    facts = facts_for({"authorized": True})
    assert project(facts) in STATE_NAMES, (
        "the starting facts project to a declared state"
    )
    for step in steps:
        apply(facts, step)
        assert project(facts) in STATE_NAMES, (
            "every event prefix keeps a declared projection"
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
