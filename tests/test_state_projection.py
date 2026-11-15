"""Property tests for the live-state projection order.

The five visible states are a projection of independent facts. These tests draw
fact sets from the declared vocabulary and assert the precedence the book
promises: Denied outranks everything, a request in flight outranks a broken
source, and freshness is decided last.
"""

from __future__ import annotations

import copy

from hypothesis import given
from hypothesis import strategies as st
from statecheck.contract import (
    DATA_PATH,
    FIXTURES_PATH,
    Facts,
    defaults,
    load_document,
    states,
)
from statecheck.events import request_allowed
from statecheck.projection import project, vector_at_least

DATA = load_document(DATA_PATH)
FIXTURES = load_document(FIXTURES_PATH)
DEFAULT_FACTS = defaults(FIXTURES)
AVAILABILITY = st.sampled_from(sorted({"present", "uncertain", "lost"}))
STATE_NAMES = states(DATA)

VECTORS = st.dictionaries(
    st.sampled_from(["document", "profile", "rate"]),
    st.integers(min_value=0, max_value=8),
    max_size=3,
)
EPOCHS = st.integers(min_value=0, max_value=6)

FACT_OVERRIDES = st.fixed_dictionaries(
    {
        "authorized": st.booleans(),
        "availability": AVAILABILITY,
        "accepted": st.booleans(),
        "accepted_validated": VECTORS,
        "accepted_epoch": EPOCHS,
        "known_source": VECTORS,
        "invalidation_epoch": EPOCHS,
        "request_active": st.booleans(),
    }
)


def facts_for(overrides: dict[str, object]) -> Facts:
    """Return a complete fact set with the drawn facts applied."""
    facts: Facts = copy.deepcopy(DEFAULT_FACTS)
    facts.update(overrides)  # type: ignore[typeddict-item]
    return facts


@given(FACT_OVERRIDES)
def test_projection_is_total(overrides: dict[str, object]) -> None:
    """Every fact set projects to one of the declared visible states."""
    assert project(facts_for(overrides)) in STATE_NAMES, (
        "every fact set projects to a declared state"
    )


@given(FACT_OVERRIDES)
def test_projection_does_not_mutate_its_facts(overrides: dict[str, object]) -> None:
    """Projecting a fact set leaves the facts untouched."""
    facts = facts_for(overrides)
    before = copy.deepcopy(facts)
    project(facts)
    assert facts == before, "projecting leaves the facts unchanged"


@given(FACT_OVERRIDES)
def test_denied_outranks_every_other_fact(overrides: dict[str, object]) -> None:
    """A missing grant projects Denied whatever else the facts say."""
    facts = facts_for({**overrides, "authorized": False})
    assert project(facts) == "Denied", (
        "a missing grant outranks every other fact"
    )


@given(FACT_OVERRIDES)
def test_refreshing_outranks_broken(overrides: dict[str, object]) -> None:
    """A request in flight projects Refreshing over a broken source."""
    facts = facts_for(
        {
            **overrides,
            "authorized": True,
            "request_active": True,
            "availability": "lost",
        }
    )
    assert project(facts) == "Refreshing", (
        "a request in flight outranks a lost source"
    )


@given(FACT_OVERRIDES)
def test_broken_outranks_stale(overrides: dict[str, object]) -> None:
    """A refused or uncertain source projects Broken rather than Stale."""
    facts = facts_for(
        {
            **overrides,
            "authorized": True,
            "request_active": False,
            "availability": "uncertain",
        }
    )
    assert project(facts) == "Broken", (
        "an uncertain source outranks a stale accepted value"
    )


@given(FACT_OVERRIDES)
def test_current_requires_a_matching_epoch_and_coverage(
    overrides: dict[str, object],
) -> None:
    """Only a fresh accepted vector at the current epoch projects Current."""
    facts = facts_for(
        {
            **overrides,
            "authorized": True,
            "request_active": False,
            "availability": "present",
            "accepted": True,
        }
    )
    validated = facts["accepted_validated"]
    known = facts["known_source"]
    covers = all(
        key in validated and validated[key] >= value
        for key, value in known.items()
    )
    fresh = facts["accepted_epoch"] == facts["invalidation_epoch"] and covers
    assert project(facts) == ("Current" if fresh else "Stale"), (
        "Current needs a covering vector at the current epoch; otherwise Stale"
    )


def test_a_covering_vector_at_the_same_epoch_projects_current() -> None:
    """A validated vector that covers its source at one epoch is Current."""
    facts = facts_for(
        {
            "authorized": True,
            "availability": "present",
            "accepted": True,
            "accepted_validated": {"rate": 2},
            "accepted_epoch": 4,
            "known_source": {"rate": 1},
            "invalidation_epoch": 4,
            "request_active": False,
        }
    )
    assert project(facts) == "Current", (
        "a covering vector at the same epoch projects Current"
    )


@given(st.dictionaries(st.text(max_size=4), EPOCHS, max_size=4))
def test_a_vector_covers_itself(vector: dict[str, int]) -> None:
    """Any validated vector is at least as advanced as itself."""
    assert vector_at_least(vector, vector), (
        "a validated vector covers its own values"
    )


@given(st.dictionaries(st.text(max_size=4), EPOCHS, max_size=4), EPOCHS)
def test_a_missing_source_value_is_not_covered(
    vector: dict[str, int], value: int
) -> None:
    """A source the validated vector omits blocks coverage."""
    assert not vector_at_least(vector, {**vector, "absent": value + 1}), (
        "a source value the validated vector omits is not covered"
    )


@given(FACT_OVERRIDES)
def test_requests_require_authority(overrides: dict[str, object]) -> None:
    """A denied grant never permits a request, whatever the availability says."""
    facts = facts_for({**overrides, "authorized": False})
    assert not request_allowed(facts), "a denied grant never permits a request"


def test_declared_states_are_the_projection_image() -> None:
    """The projection can reach every declared state, and only those."""
    reached = {
        project(
            facts_for(
                {
                    "authorized": authorized,
                    "availability": availability,
                    "accepted": accepted,
                    "accepted_validated": {"rate": 1 if fresh else 0},
                    "accepted_epoch": 0,
                    "known_source": {"rate": 1},
                    "invalidation_epoch": 0,
                    "request_active": active,
                }
            )
        )
        for authorized in (True, False)
        for availability in ("present", "uncertain", "lost")
        for accepted in (True, False)
        for active in (True, False)
        for fresh in (True, False)
    }
    assert reached == STATE_NAMES, (
        "the projection reaches every declared state and no others"
    )
