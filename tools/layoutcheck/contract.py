"""Paths, declared data and the layout contract loader.

The module locates `tools/layout-budgets.json` and `book/14-spacing-metrics.md`,
and provides the `Budgets` record and `load_budgets`, which validates the three
sections the checks read. It performs no file I/O at import: `load_document`
reads the JSON document and the command-line entry point loads it once.
"""

from __future__ import annotations

import json
import typing as typ
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = ROOT / "tools" / "layout-budgets.json"
CHAPTER = ROOT / "book" / "14-spacing-metrics.md"
BAND_PROFILES = ("document", "document_strip", "studio", "studio_strip")

# The configuration fields the budget and chapter checks read, and the tokens
# `layoutcheck.budget` reads without naming them in a configuration.
CONFIGURATION_FIELDS = (
    "name",
    "width",
    "height",
    "profile",
    "left",
    "right",
    "expected",
)
REQUIRED_TOKENS = (
    "splitter",
    "document_width_min",
    "document_content_height",
    "document_viewport_min",
    "compact_viewport_min",
)


class ContractError(Exception):
    """The layout budgets document cannot be read, decoded or parsed.

    The error also reports a document that does not declare the three sections
    the checks read. The loader raises it rather than stopping the interpreter,
    so the command-line entry point can report the defect and choose its own
    exit status.
    """


class Budgets(typ.NamedTuple):
    """The validated layout budgets.

    A `Budgets` is built once by `load_budgets` at the command-line entry point
    and passed to the budget, chapter and self-test checks, so the file read is
    explicit rather than an import-time side effect.
    """

    tokens: dict[str, int]
    profiles: dict[str, list[str]]
    configurations: list[dict[str, object]]


def load_document(path: Path) -> dict[str, object]:
    """Load the layout budgets document as a decoded JSON object.

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
        raise ContractError(f"layout budgets do not declare {field}")
    return value


def _sequence(document: dict[str, object], field: str) -> list[object]:
    """Return a declared JSON array field, or report its absence."""
    value = document.get(field)
    if not isinstance(value, list):
        raise ContractError(f"layout budgets do not declare {field}")
    return value


def _token_reference(tokens: dict[str, int], value: object, where: str) -> None:
    """Report a value that is neither an integer nor a declared token name."""
    if isinstance(value, int) and not isinstance(value, bool):
        return
    if not isinstance(value, str) or value not in tokens:
        raise ContractError(f"layout budget {where} names no declared token: {value!r}")


def _pane_reference(tokens: dict[str, int], value: object, where: str) -> None:
    """Report a side pane that is not the name of a declared token.

    Both `layoutcheck.budget.side_width` and `layoutcheck.chapter` read a side
    pane's width from the token table by name, so a literal number would be
    looked up as a name and could only fail there.
    """
    if not isinstance(value, str) or value not in tokens:
        raise ContractError(
            f"layout budget {where} names no declared pane token: {value!r}"
        )


def _expected(tokens: dict[str, int], expected: object, where: str) -> None:
    """Report a worked plane that is not a pair of resolvable sizes."""
    if not isinstance(expected, list) or len(expected) != 2:
        raise ContractError(f"{where}.expected is not a pair of plane sizes")
    for entry in expected:
        _token_reference(tokens, entry, f"{where}.expected")


def _configuration(
    index: int,
    value: object,
    tokens: dict[str, int],
    profiles: dict[str, list[str]],
) -> dict[str, object]:
    """Validate one worked configuration and return it unchanged."""
    where = f"configurations[{index}]"
    if not isinstance(value, dict):
        raise ContractError(f"{where} is not a JSON object")
    missing = [field for field in CONFIGURATION_FIELDS if field not in value]
    if missing:
        raise ContractError(f"{where} lacks {missing}")
    if not isinstance(value["name"], str) or not value["name"]:
        raise ContractError(f"{where}.name is not a non-empty string")
    for field in ("width", "height"):
        _token_reference(tokens, value[field], f"{where}.{field}")
    for field in ("left", "right"):
        _pane_reference(tokens, value[field], f"{where}.{field}")
    profile = value["profile"]
    if not isinstance(profile, str) or profile not in profiles:
        raise ContractError(f"{where}.profile names no declared profile: {profile!r}")
    _expected(tokens, value["expected"], where)
    if not isinstance(value.get("compact", False), bool):
        raise ContractError(f"{where}.compact is not a boolean")
    return value


def load_budgets(path: Path) -> Budgets:
    """Load and validate the layout budgets at ``path``.

    Parameters
    ----------
    path
        The budgets document to load.

    Returns
    -------
    Budgets
        The token table, band profiles and worked configurations.

    Raises
    ------
    ContractError
        If the document cannot be read, does not declare the three sections,
        or declares a token table, profile or configuration that the budget
        and chapter checks could not use.
    """
    document = load_document(path)
    tokens = _mapping(document, "tokens")
    if not all(isinstance(value, int) for value in tokens.values()):
        raise ContractError("layout budgets declare a non-integer token")
    absent = [name for name in REQUIRED_TOKENS if name not in tokens]
    if absent:
        raise ContractError(f"layout budgets declare no {absent}")
    profiles = _mapping(document, "profiles")
    for name, bands in profiles.items():
        if not isinstance(bands, list) or not all(
            isinstance(band, str) for band in bands
        ):
            raise ContractError(
                f"layout budget profile {name!r} is not a list of names"
            )
        undeclared = [band for band in bands if band not in tokens]
        if undeclared:
            raise ContractError(
                f"layout budget profile {name!r} names undeclared tokens {undeclared}"
            )
    token_table = typ.cast("dict[str, int]", tokens)
    profile_table = typ.cast("dict[str, list[str]]", profiles)
    configurations = [
        _configuration(index, value, token_table, profile_table)
        for index, value in enumerate(_sequence(document, "configurations"))
    ]
    return Budgets(
        tokens=token_table,
        profiles=profile_table,
        configurations=configurations,
    )


def chapter_text() -> str:
    """Return the chapter's Markdown source.

    Returns
    -------
    str
        The full text of chapter 14.
    """
    return CHAPTER.read_text(encoding="utf-8")


def number(tokens: dict[str, int], value: object) -> int:
    """Return a literal number, or resolve a named token against the table.

    An ``int`` value, which includes a ``bool``, is returned unchanged. Any
    other value is converted with ``str()`` and looked up in ``tokens`` by the
    resulting name.

    Parameters
    ----------
    tokens : dict[str, int]
        The declared token table, keyed by token name.
    value : object
        A literal ``int`` or the name of a token.

    Returns
    -------
    int
        The literal integer, or the token's declared value.

    Raises
    ------
    ContractError
        If the name of a value that is not an ``int`` has no entry in
        ``tokens``.
    """
    if isinstance(value, int):
        return value
    name = str(value)
    if name not in tokens:
        raise ContractError(f"layout budget names no declared token: {name!r}")
    return tokens[name]
