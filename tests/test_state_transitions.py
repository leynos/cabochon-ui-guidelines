"""Property tests for the live-state event rules.

Chapter 08 states its transitions as invariants rather than examples: a reply
that does not match the in-flight request never changes the accepted value, a
denied grant never projects anything but Denied, and each event leaves the
projection its own rule implies. These tests draw fact sets, reply identities
and event sequences from the declared vocabulary.
"""

from __future__ import annotations

import copy
import typing as typ

import pytest
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
    every value the known source or the in-flight request requires, taking
    the higher where the two disagree. The drawn vector supplies the rest of
    the reply, but a required value wins wherever it is higher, so a matching
    reply always covers both vectors it must. Any other reply shifts the
    generation, so the rule must ignore it whatever it validates.
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
            required = dict(facts["known_source"])
            for key, value in facts["request_covers"].items():
                required[key] = max(required.get(key, 0), value)
            step["validated"] = {
                key: max(value, required.get(key, 0))
                for key, value in {**required, **vector}.items()
            }
    return step


@pytest.mark.parametrize(
    ("known", "covers", "drawn", "expected"),
    [
        pytest.param(
            {"rate": 2}, {"rate": 1}, {"rate": 0}, {"rate": 2}, id="source-higher"
        ),
        pytest.param(
            {"rate": 1}, {"rate": 2}, {"rate": 0}, {"rate": 2}, id="request-higher"
        ),
        pytest.param(
            {"rate": 1},
            {"document": 3},
            {"rate": 0, "document": 1},
            {"rate": 1, "document": 3},
            id="disjoint-keys",
        ),
        pytest.param(
            {"rate": 1}, {"rate": 1}, {"rate": 5}, {"rate": 5}, id="reply-higher"
        ),
    ],
)
def test_a_matching_reply_covers_the_higher_of_every_required_vector(
    known: dict[str, int],
    covers: dict[str, int],
    drawn: dict[str, int],
    expected: dict[str, int],
) -> None:
    """A matching reply validates the component-wise maximum of all three.

    The known source and the in-flight request can disagree, and a key may
    appear in only one of them. The reply must still cover both, so the drawn
    value never lowers a required component.
    """
    facts = facts_for(
        {
            "known_source": known,
            "request_covers": covers,
            "request_active": True,
            "request_generation": 4,
            "invalidation_epoch": 2,
        }
    )
    step = _step("refresh_succeeded", facts, True, drawn)
    assert step["validated"] == expected, (
        "the reply covers the highest required value for every key"
    )


class _Effect(typ.NamedTuple):
    """The facts and projections either side of one applied event."""

    event: str
    match: bool
    before: Facts
    step: Step
    facts: Facts
    projection_before: str
    projection: str
    changed: bool


def _reply_permitted(effect: _Effect) -> bool:
    """Return whether a reply was permitted from the facts before it."""
    return effect.before["request_active"] and (
        effect.before["authorized"] or effect.event == "refresh_cancelled"
    )


def _dispatch_expected(effect: _Effect) -> bool:
    """Return whether the event dispatches, read from the facts before it."""
    required = (
        {"present", "uncertain"}
        if effect.event == "refresh_requested"
        else {"present"}
    )
    return effect.before["authorized"] and effect.before["availability"] in required


def _assert_reply_effect(effect: _Effect) -> None:
    """Assert the rule a permitted, matching reply leaves behind."""
    assert effect.changed == (effect.match and _reply_permitted(effect)), (
        "only a permitted reply that matches the request changes a fact"
    )
    if effect.event == "refresh_succeeded":
        assert effect.projection == (
            "Current" if effect.changed else effect.projection_before
        ), "an accepted reply projects Current and an ignored one changes nothing"
        if effect.changed:
            assert effect.facts["accepted_validated"] == effect.step["validated"], (
                "the matching reply's vector becomes the accepted value"
            )
    elif effect.event == "refresh_failed":
        assert effect.projection == (
            "Broken" if effect.changed else effect.projection_before
        ), "a refused source projects Broken and an ignored reply changes nothing"
    else:
        assert effect.changed or effect.projection == effect.projection_before, (
            "a cancelled reply that changes nothing leaves the projection alone"
        )


def _assert_dispatch_effect(effect: _Effect) -> None:
    """Assert that a permitted dispatch projects Refreshing and a refusal not."""
    dispatch = _dispatch_expected(effect)
    assert effect.changed == dispatch, (
        "a permitted dispatch changes the facts and a refused one does not"
    )
    assert effect.projection == (
        "Refreshing" if dispatch else effect.projection_before
    ), "a permitted dispatch projects Refreshing and a refused one leaves it alone"


def _assert_revoked_effect(effect: _Effect) -> None:
    """Assert that a revoked grant projects Denied whatever came before it."""
    assert effect.projection == "Denied", "a revoked grant always projects Denied"


def _assert_provider_effect(effect: _Effect) -> None:
    """Assert that a lost provider projects Broken unless the grant is denied."""
    assert effect.projection == (
        "Denied" if not effect.facts["authorized"] else "Broken"
    ), "a lost provider projects Broken unless the grant is denied"


def _assert_unchanged_effect(effect: _Effect) -> None:
    """Assert that an event with no rule of its own leaves the projection alone."""
    assert effect.changed or effect.projection == effect.projection_before, (
        "an event that changes nothing leaves the projection alone"
    )


EFFECT_CHECKERS: dict[str, typ.Callable[[_Effect], None]] = {
    "refresh_succeeded": _assert_reply_effect,
    "refresh_failed": _assert_reply_effect,
    "refresh_cancelled": _assert_reply_effect,
    "refresh_requested": _assert_dispatch_effect,
    "source_advanced": _assert_dispatch_effect,
    "grant_revoked": _assert_revoked_effect,
    "provider_lost": _assert_provider_effect,
}


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
        effect = _Effect(
            event=event,
            match=match,
            before=before,
            step=step,
            facts=facts,
            projection_before=projection_before,
            projection=projection,
            changed=facts != before,
        )
        EFFECT_CHECKERS.get(event, _assert_unchanged_effect)(effect)


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


@pytest.mark.parametrize(
    ("known", "covers", "validated", "accepted"),
    [
        pytest.param(
            {"rate": 2}, {"rate": 1}, {"rate": 1}, False, id="covers-request-only"
        ),
        pytest.param(
            {"rate": 1}, {"rate": 2}, {"rate": 1}, False, id="covers-source-only"
        ),
        pytest.param({"rate": 1}, {"rate": 1}, {"rate": 1}, True, id="covers-both"),
    ],
)
@given(GENERATIONS, EPOCHS)
def test_a_matching_reply_must_cover_the_source_and_the_request(
    known: dict[str, int],
    covers: dict[str, int],
    validated: dict[str, int],
    accepted: bool,
    generation: int,
    epoch: int,
) -> None:
    """Each coverage guard refuses a reply the other guard alone would accept.

    The generation, epoch and grant are valid in every case, so only coverage
    can decide the reply. A reply that covers one required vector but not the
    other is ignored whole; one that covers both becomes the accepted value.
    """
    facts = facts_for(
        {
            "availability": "uncertain",
            "known_source": dict(known),
            "request_active": True,
            "request_generation": generation,
            "request_covers": dict(covers),
            "invalidation_epoch": epoch,
        }
    )
    before = copy.deepcopy(facts)
    apply(
        facts,
        {
            "event": "refresh_succeeded",
            "expected": "Current",
            "generation": generation,
            "epoch": epoch,
            "validated": dict(validated),
        },
    )
    if accepted:
        assert facts["accepted"] is True, "a fully covering reply is accepted"
        assert facts["accepted_validated"] == validated, (
            "the covering reply becomes the accepted value"
        )
        assert project(facts) == "Current", "the covering reply projects Current"
    else:
        assert facts == before, "a partially covering reply changes no fact"
        assert project(facts) == "Refreshing", (
            "the partially covering reply leaves the request in flight"
        )


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
