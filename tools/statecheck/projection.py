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


def vector_at_least(validated: dict[str, int], known: dict[str, int]) -> bool:
    """Return whether a validated vector covers every known source value."""
    return all(validated.get(key, -1) >= value for key, value in known.items())


def project(facts: Facts) -> str:
    """Project the visible state from facts in the book's declared order."""
    if not facts["authorized"]:
        return "Denied"
    if facts["request_active"]:
        return "Refreshing"
    if facts["availability"] != "present" or not facts["accepted"]:
        return "Broken"
    fresh = facts["accepted_epoch"] == facts["invalidation_epoch"] and vector_at_least(
        facts["accepted_validated"],
        facts["known_source"],
    )
    return "Current" if fresh else "Stale"
