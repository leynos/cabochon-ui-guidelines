"""Paths, patterns and the loaded contract shared by the link checks.

The module locates `book/`, `figures/` and `tools/book-contract.json`, and
defines the `Contract` record the sibling link modules read. It performs no
file I/O at import: `load_document` reads one JSON document, `load_contract`
validates the sections the checks need and compiles the declared identifier
pattern, and `linkcheck.cli` builds the contract once.
"""

from __future__ import annotations

import json
import re
import typing as typ
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BOOK = ROOT / "book"
FIGURES = ROOT / "figures"
DATA_PATH = ROOT / "tools" / "book-contract.json"

FRONT_FIGURE_RE = re.compile(r"^figure:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)
FRONT_PART_RE = re.compile(r"^part:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)
FRONT_MATTER_RE = re.compile(r"\A---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)", re.DOTALL)
REQUIREMENT_RE = re.compile(r"\*\*([A-Z]{3}-[0-9]{2})\*\*")
OWNER_RE = re.compile(r"Owner:\s*\[[^\]]*\]\(([^)]+)\)")

EXTERNAL_PREFIXES = ("http://", "https://", "mailto:")


class ContractError(Exception):
    """A link contract document cannot be read, decoded or parsed.

    The error also reports a document that violates the shape the checks
    require. The loader raises it rather than stopping the interpreter, so the
    command-line entry point can report the defect and choose its own exit
    status.
    """


class ChapterEntry(typ.TypedDict):
    """One manifest entry: the chapter file and the part that holds it."""

    file: str
    part: str


class RequirementSpec(typ.TypedDict):
    """The checklist, registry and identifier pattern for requirements."""

    checklist: str
    registry: str
    id_pattern: str


class StateSpec(typ.TypedDict):
    """The two state groups and the chapters that own their tables."""

    live: list[str]
    live_owner: str
    resolution: list[str]
    resolution_owner: str


class ProfileSpec(typ.TypedDict):
    """The conformance profiles and the chapter that declares them."""

    names: list[str]
    owner: str


class CommandSpec(typ.TypedDict):
    """The command record's owner and the views that must reference it."""

    record_owner: str
    views: list[str]


class ResourceSpec(typ.TypedDict):
    """The resource owner and the consumers that must reference it."""

    owner: str
    consumers: list[str]


class Contract(typ.NamedTuple):
    """The validated link contract and the pattern compiled from it.

    A `Contract` is built once by `load_contract` at a command-line entry point.
    Passing it to the checks keeps the file read explicit and avoids a hidden
    import-time value.
    """

    chapters: list[ChapterEntry]
    navigation: str
    requirements: RequirementSpec
    states: StateSpec
    profiles: ProfileSpec
    commands: CommandSpec
    resources: ResourceSpec
    requirement_ids: re.Pattern[str]


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


def _text(document: dict[str, object], field: str) -> str:
    """Return a declared string field, or report its absence."""
    value = document.get(field)
    if not isinstance(value, str):
        raise ContractError(f"contract document does not declare a string {field}")
    return value


def _strings(document: dict[str, object], field: str) -> list[str]:
    """Return a declared array of strings, or report its absence."""
    value = document.get(field)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ContractError(f"contract document does not declare {field} as strings")
    return typ.cast("list[str]", value)


def _chapters(document: dict[str, object]) -> list[ChapterEntry]:
    """Return the manifest entries, each naming a file and its part."""
    entries: list[ChapterEntry] = []
    for index, entry in enumerate(_sequence(document, "chapters")):
        if not isinstance(entry, dict):
            raise ContractError(f"chapters[{index}] is not a JSON object")
        file = entry.get("file")
        part = entry.get("part")
        if not isinstance(file, str) or not isinstance(part, str):
            raise ContractError(f"chapters[{index}] lacks a string file and part")
        entries.append({"file": file, "part": part})
    return entries


def _requirements(document: dict[str, object]) -> RequirementSpec:
    """Return the requirements section, which names three strings."""
    section = _mapping(document, "requirements")
    return {
        "checklist": _text(section, "checklist"),
        "registry": _text(section, "registry"),
        "id_pattern": _text(section, "id_pattern"),
    }


def _states(document: dict[str, object]) -> StateSpec:
    """Return the states section, which names both groups and their owners."""
    section = _mapping(document, "states")
    return {
        "live": _strings(section, "live"),
        "live_owner": _text(section, "live_owner"),
        "resolution": _strings(section, "resolution"),
        "resolution_owner": _text(section, "resolution_owner"),
    }


def _profiles(document: dict[str, object]) -> ProfileSpec:
    """Return the profiles section, which names the profiles and their owner."""
    section = _mapping(document, "profiles")
    return {
        "names": _strings(section, "names"),
        "owner": _text(section, "owner"),
    }


def _commands(document: dict[str, object]) -> CommandSpec:
    """Return the commands section, which names the record owner and views."""
    section = _mapping(document, "commands")
    return {
        "record_owner": _text(section, "record_owner"),
        "views": _strings(section, "views"),
    }


def _resources(document: dict[str, object]) -> ResourceSpec:
    """Return the resources section, which names the owner and consumers."""
    section = _mapping(document, "resources")
    return {
        "owner": _text(section, "owner"),
        "consumers": _strings(section, "consumers"),
    }


def _book_references(contract: Contract) -> list[tuple[str, str]]:
    """Return every named book file with the contract field that names it."""
    return [
        ("requirements.checklist", contract.requirements["checklist"]),
        ("states.live_owner", contract.states["live_owner"]),
        ("states.resolution_owner", contract.states["resolution_owner"]),
        ("profiles.owner", contract.profiles["owner"]),
        ("commands.record_owner", contract.commands["record_owner"]),
        *[("commands.views", name) for name in contract.commands["views"]],
        ("resources.owner", contract.resources["owner"]),
        *[("resources.consumers", name) for name in contract.resources["consumers"]],
    ]


def _validate_references(contract: Contract) -> None:
    """Report a named book file that the manifest does not declare.

    Every file these fields name is a chapter, and `check_manifest` only
    reports chapters the manifest declares, so a reference outside the
    manifest would otherwise be skipped without any diagnostic.
    """
    declared = {entry["file"] for entry in contract.chapters}
    for field, name in _book_references(contract):
        if name not in declared:
            raise ContractError(
                f"{field} names {name!r}, which the manifest does not declare"
            )


def load_contract(path: Path) -> Contract:
    """Load and validate the link contract at ``path``.

    Parameters
    ----------
    path
        The contract document to load.

    Returns
    -------
    Contract
        The validated sections and the compiled identifier pattern.

    Raises
    ------
    ContractError
        If the document cannot be read, does not declare a section the checks
        read, declares an identifier pattern that does not compile, or names
        a book file that the manifest does not declare.
    """
    document = load_document(path)
    requirements = _requirements(document)
    try:
        requirement_ids = re.compile(requirements["id_pattern"])
    except re.error as error:
        raise ContractError(
            f"requirement identifier pattern does not compile: {error}"
        ) from error
    contract = Contract(
        chapters=_chapters(document),
        navigation=_text(document, "navigation"),
        requirements=requirements,
        states=_states(document),
        profiles=_profiles(document),
        commands=_commands(document),
        resources=_resources(document),
        requirement_ids=requirement_ids,
    )
    _validate_references(contract)
    return contract


def resolved_destination(base: Path, target: str) -> Path | None:
    """Resolve a local link destination against a base directory."""
    path_part = target.partition("#")[0]
    if not path_part or path_part.startswith(EXTERNAL_PREFIXES):
        return None
    return (base / path_part).resolve()
