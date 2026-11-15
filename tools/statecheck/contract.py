"""Paths, typed fixture shapes and contract loading for the state contract.

The module locates `tools/figure-data.json`, `tools/state-fixtures.json`,
`book/08-live-relationships.md` and `figures/fig-06-state.svg`, and defines the
`Facts`, `Step` and `Scenario` shapes that every sibling module imports. It
performs no file I/O at import: `load_document` reads one JSON document and
`load_contract` combines both documents with the vocabularies derived from
them.
"""

from __future__ import annotations

import json
import re
import typing as typ
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = ROOT / "tools" / "figure-data.json"
FIXTURES_PATH = ROOT / "tools" / "state-fixtures.json"
CHAPTER = ROOT / "book" / "08-live-relationships.md"
FIGURE = ROOT / "figures" / "fig-06-state.svg"

SVG_NS = "{http://www.w3.org/2000/svg}"
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


class ContractError(Exception):
    """A contract document cannot be read, decoded or parsed.

    The error also reports a document that violates the shape it declares. The
    loaders raise it rather than stopping the interpreter, so each command-line
    entry point can report the defect and choose its own exit status.
    """


def load_document(path: Path) -> dict[str, object]:
    """Load one contract document as a decoded JSON object.

    Parameters
    ----------
    path
        The document to read.

    Returns
    -------
    dict[str, object]
        The decoded JSON object.

    Raises
    ------
    ContractError
        If the file cannot be read as UTF-8 text, does not decode to JSON or
        does not declare a JSON object.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ContractError(f"cannot read {path}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise ContractError(f"cannot decode {path} as UTF-8: {exc}") from exc
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ContractError(f"cannot parse {path} as JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise ContractError(f"{path} does not declare a JSON object")
    return document


def _mapping(document: dict[str, object], field: str) -> dict[str, object]:
    """Return a declared JSON object field, or report its absence."""
    value = document.get(field)
    if not isinstance(value, dict):
        raise ContractError(f"contract document does not declare {field}")
    return value


def _sequence(document: dict[str, object], field: str) -> list[object]:
    """Return a declared JSON array field, or report its absence."""
    value = document.get(field)
    if not isinstance(value, list):
        raise ContractError(f"contract document does not declare {field}")
    return value


def states(data: dict[str, object]) -> set[str]:
    """Return every live state name the figure contract declares."""
    return set(_mapping(data, "live_states"))


def from_tokens(data: dict[str, object]) -> set[str]:
    """Return every source token a transition may name."""
    return states(data) | {"Any state", "Any state except Denied"}


def targets(data: dict[str, object]) -> set[str]:
    """Return every target token a transition may name."""
    return states(data) | {"Recomputed", "No change"}


def transition_rows(data: dict[str, object]) -> list[LiveTransition]:
    """Return the typed transition records from the figure contract."""
    return typ.cast("list[LiveTransition]", _sequence(data, "live_transitions"))


def scenarios(fixtures: dict[str, object]) -> list[Scenario]:
    """Return every fixture sequence the fixtures document declares."""
    return typ.cast("list[Scenario]", _sequence(fixtures, "scenarios"))


def defaults(fixtures: dict[str, object]) -> Facts:
    """Return the initial fact set that every scenario starts from."""
    return typ.cast("Facts", _mapping(fixtures, "defaults"))


class Contract(typ.NamedTuple):
    """The loaded contract documents and the vocabularies derived from them.

    A `Contract` is built once by `load_contract` at a command-line entry point.
    Passing it to the checks keeps the file read explicit and avoids a second
    derivation or a hidden import-time value.
    """

    data: dict[str, object]
    fixtures: dict[str, object]
    transitions: list[LiveTransition]
    states: set[str]
    from_tokens: set[str]
    targets: set[str]


def load_contract(data_path: Path, fixtures_path: Path) -> Contract:
    """Load both contract documents and derive the shared vocabularies.

    Parameters
    ----------
    data_path
        The figure contract that declares the states and transitions.
    fixtures_path
        The fixture document that declares the event scenarios.

    Returns
    -------
    Contract
        The decoded documents and the vocabularies derived from them.

    Raises
    ------
    ContractError
        If either document cannot be read or does not declare its shape.
    """
    data = load_document(data_path)
    fixtures = load_document(fixtures_path)
    return Contract(
        data=data,
        fixtures=fixtures,
        transitions=transition_rows(data),
        states=states(data),
        from_tokens=from_tokens(data),
        targets=targets(data),
    )
