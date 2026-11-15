"""Constants and validated state records shared by the figure checks."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
FIGURES = ROOT / "figures"
DATA = json.loads((ROOT / "tools" / "figure-data.json").read_text(encoding="utf-8"))

SVG_NS = "{http://www.w3.org/2000/svg}"
CLASSES = {"schematic", "editorial", "production"}
MARK_KINDS = {"dot", "arc", "triangle", "broken", "lock", "hatch", "dashed", "crossed"}
GEOMETRY_TAGS = {"rect", "circle", "ellipse", "line", "polyline", "polygon", "path"}
TRANSFORM_RE = re.compile(r"([a-zA-Z]+)\s*\(([^)]*)\)")
NUMBER_RE = re.compile(r"-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?")
PATH_TOKEN_RE = re.compile(r"[A-Za-z]|-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?")

IDENTITY = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
BBox = tuple[float, float, float, float]

STATE_FIELDS = ("id", "word", "cue", "mark", "role", "colour")


class GeometryError(Exception):
    """A drawn element falls outside the checker's constrained SVG subset."""


def _require_fields(state: dict[str, object]) -> None:
    """Reject a state record that leaves a required field blank."""
    missing = [
        field for field in STATE_FIELDS if not str(state.get(field, "")).strip()
    ]
    if missing:
        raise SystemExit(
            f"figure contract: state {state.get('word')!r} lacks {missing}"
        )


def _state_record(
    state: dict[str, object],
    records: dict[str, dict[str, str]],
    words: set[str],
) -> dict[str, str]:
    """Validate one state record, returning it keyed for later checks."""
    _require_fields(state)
    identifier = str(state["id"])
    if identifier in records:
        raise SystemExit(f"figure contract: duplicate state identity {identifier!r}")
    word = str(state["word"]).upper()
    if word in words:
        raise SystemExit(f"figure contract: duplicate state word {word!r}")
    words.add(word)
    if state["mark"] not in MARK_KINDS:
        raise SystemExit(
            f"figure contract: state {word!r} has unknown mark {state['mark']!r}"
        )
    role_colour = DATA["palette_roles"].get(str(state["role"]))
    if role_colour is None:
        raise SystemExit(
            f"figure contract: state {word!r} names unknown role {state['role']!r}"
        )
    if role_colour.upper() != str(state["colour"]).upper():
        raise SystemExit(
            f"figure contract: state {word!r} colour {state['colour']} "
            f"disagrees with role {state['role']!r}"
        )
    return {
        "id": identifier,
        "word": word,
        "mark": str(state["mark"]),
        "role": str(state["role"]),
        "colour": str(state["colour"]).upper(),
    }


def state_records() -> dict[str, dict[str, str]]:
    """Load and validate one record per state, keyed by identity."""
    records: dict[str, dict[str, str]] = {}
    words: set[str] = set()
    for group in ("live_states", "resolution_states"):
        for state in DATA[group].values():
            record = _state_record(state, records, words)
            records[record["id"]] = record
    return records


STATE_RECORDS = state_records()
