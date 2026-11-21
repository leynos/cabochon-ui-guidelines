"""Project the visible state from the facts the book declares.

The `project` function ranks Denied, Refreshing, Broken and Current or Stale,
using `vector_at_least` to compare validated and known source vectors.
`statecheck.events`, `statecheck.scenarios` and `statecheck.selftest` import
it.
"""

from __future__ import annotations

import typing as typ

if typ.TYPE_CHECKING:
    from statecheck.contract import Facts


class Mutation(typ.NamedTuple):
    """A deviation from the declared rules that the self-test must detect.

    Each field disables one rule of the projection or request policy. The
    self-test runs the fixtures with a mutation in force and requires the
    fixtures' declared states to expose it, so a mutation is proved detectable
    by the product path rather than by a replica of it.
    """

    broken_first: bool = False
    ignore_epoch: bool = False
    present_only: bool = False


NO_MUTATION = Mutation()


def vector_at_least(validated: dict[str, int], known: dict[str, int]) -> bool:
    """Return whether a validated vector covers every known source value."""
    return all(validated.get(key, -1) >= value for key, value in known.items())


def project(facts: Facts, mutation: Mutation = NO_MUTATION) -> str:
    """Project the visible state from facts in the book's declared order.

    Parameters
    ----------
    facts
        The fact set to project.
    mutation
        A deviation the self-test asks for. ``NO_MUTATION`` applies the
        declared order; any other value is a deliberately broken order whose
        effect the fixtures must report.
    """
    if not facts["authorized"]:
        return "Denied"
    if mutation.broken_first and not facts["accepted"]:
        return "Broken"
    if facts["request_active"]:
        return "Refreshing"
    if facts["availability"] != "present" or not facts["accepted"]:
        return "Broken"
    current_epoch = mutation.ignore_epoch or (
        facts["accepted_epoch"] == facts["invalidation_epoch"]
    )
    fresh = current_epoch and vector_at_least(
        facts["accepted_validated"],
        facts["known_source"],
    )
    return "Current" if fresh else "Stale"
