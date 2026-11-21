"""Pure constants and validated state records shared by the figure checks.

The module locates the repository's `figures/` directory and defines the
accepted class and mark names, the constrained SVG grammar, and the `BBox`,
`GeometryError` and `ContractError` types. It performs no file I/O at import:
`load_document` reads `tools/figure-data.json` and `state_records` validates it.
"""

from __future__ import annotations

import json
import re
import typing as typ
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
FIGURES = ROOT / "figures"
DATA_PATH = ROOT / "tools" / "figure-data.json"

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


class ContractError(Exception):
    """A figure contract document cannot be read, decoded or parsed.

    The error also reports a document that violates the shape it declares, such
    as a state record that omits a field or names an unknown mark. The loaders
    raise it rather than stopping the interpreter, so the command-line entry
    point can report the defect and choose its own exit status.
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


def figure_specs(data: dict[str, object]) -> dict[str, dict[str, object]]:
    """Return every figure specification the contract declares."""
    return typ.cast("dict[str, dict[str, object]]", _mapping(data, "figures"))


def component_catalogue(data: dict[str, object]) -> dict[str, dict[str, float]]:
    """Return the component catalogue the production figures declare."""
    return typ.cast(
        "dict[str, dict[str, float]]", _mapping(data, "component_catalogue")
    )


def _state_group(data: dict[str, object], group: str) -> list[dict[str, object]]:
    """Return the state records declared under one document key."""
    declared = _mapping(data, group)
    records: list[dict[str, object]] = []
    for state in declared.values():
        if not isinstance(state, dict):
            raise ContractError(f"figure data declares a malformed state in {group}")
        records.append(state)
    return records


def _text(value: object) -> str | None:
    """Return a declared text value, or None when it is absent or not text."""
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _validated_record(
    state: dict[str, object], roles: dict[str, object]
) -> tuple[dict[str, str] | None, list[str]]:
    """Validate one state record in isolation, returning it and its defects."""
    values: dict[str, str] = {}
    missing: list[str] = []
    for field in STATE_FIELDS:
        value = _text(state.get(field))
        if value is None:
            missing.append(field)
        else:
            values[field] = value
    if missing:
        return None, [f"state {state.get('word')!r} lacks {missing}"]
    word = values["word"].upper()
    messages: list[str] = []
    if values["mark"] not in MARK_KINDS:
        messages.append(f"state {word!r} has unknown mark {values['mark']!r}")
    role = values["role"]
    role_colour = roles.get(role)
    if role_colour is None:
        messages.append(f"state {word!r} names unknown role {role!r}")
    elif str(role_colour).upper() != values["colour"].upper():
        messages.append(
            f"state {word!r} colour {values['colour']} "
            f"disagrees with role {role!r}"
        )
    record = {
        "id": values["id"],
        "word": word,
        "mark": values["mark"],
        "role": role,
        "colour": values["colour"].upper(),
    }
    return record, messages


def state_records(
    data: dict[str, object],
) -> tuple[dict[str, dict[str, str]], list[str]]:
    """Validate one record per state, returning the records and every defect.

    Parameters
    ----------
    data
        The decoded figure contract document.

    Returns
    -------
    tuple[dict[str, dict[str, str]], list[str]]
        The valid records keyed by identity, and every validation message. A
        state that omits a required field or repeats an identity is left out,
        so the mapping may be partial or empty when messages are present.

    Raises
    ------
    ContractError
        If the document does not declare the palette or a state group.
    """
    records: dict[str, dict[str, str]] = {}
    words: set[str] = set()
    messages: list[str] = []
    roles = _mapping(data, "palette_roles")
    for group in ("live_states", "resolution_states"):
        for state in _state_group(data, group):
            record, defects = _validated_record(state, roles)
            messages.extend(defects)
            if record is None:
                continue
            if record["id"] in records:
                messages.append(f"duplicate state identity {record['id']!r}")
                continue
            if record["word"] in words:
                messages.append(f"duplicate state word {record['word']!r}")
                continue
            words.add(record["word"])
            records[record["id"]] = record
    return records, messages
