"""Paths, typed fixture shapes and shared constants for the state contract."""

from __future__ import annotations

import json
import re
import typing as typ
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA = json.loads((ROOT / "tools" / "figure-data.json").read_text(encoding="utf-8"))
FIXTURES = json.loads(
    (ROOT / "tools" / "state-fixtures.json").read_text(encoding="utf-8")
)
CHAPTER = ROOT / "book" / "08-live-relationships.md"
FIGURE = ROOT / "figures" / "fig-06-state.svg"

SVG_NS = "{http://www.w3.org/2000/svg}"
STATES = set(DATA["live_states"])
FROM_TOKENS = STATES | {"Any state", "Any state except Denied"}
TARGETS = STATES | {"Recomputed", "No change"}
EDGE_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# ``from`` is a Python keyword, so the transition record is declared with the
# functional TypedDict syntax that keeps the document's own field name.
LiveTransition = typ.TypedDict(
    "LiveTransition",
    {
        "id": str,
        "from": list[str],
        "event": str,
        "to": str,
        "owner": str,
    },
)


class Facts(typ.TypedDict, total=False):
    """One fact set; a scenario overrides only the facts that it changes."""

    authorized: bool
    availability: str
    accepted: bool
    accepted_validated: dict[str, int]
    accepted_epoch: int
    known_source: dict[str, int]
    invalidation_epoch: int
    request_active: bool
    request_generation: int
    request_covers: dict[str, int]


class Step(typ.TypedDict, total=False):
    """One fixture event and the state that it must project."""

    event: str
    expected: str
    generation: int
    epoch: int
    validated: dict[str, int]


class Scenario(typ.TypedDict, total=False):
    """One fixture sequence with the facts that differ from the defaults."""

    name: str
    events: list[Step]
    facts: Facts


def transition_rows() -> list[LiveTransition]:
    """Return the typed transition records from the figure contract."""
    return DATA["live_transitions"]


def scenarios() -> list[Scenario]:
    """Return every declared fixture sequence."""
    return FIXTURES["scenarios"]


def defaults() -> Facts:
    """Return the initial fact set that every scenario starts from."""
    return FIXTURES["defaults"]
