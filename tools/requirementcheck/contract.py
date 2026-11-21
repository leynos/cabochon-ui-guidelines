"""Paths, patterns and the requirement contract loader.

The module defines `ROOT`, the requirement and owner regular expressions, the
`PROFILE_ORDER` ranking and `load_requirements`, which reads the checklist and
registry names from `tools/book-contract.json`. It performs no file I/O at
import: `load_document` reads one JSON document, and the command-line entry
point loads the contract once.
"""

from __future__ import annotations

import json
import re
import typing as typ
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = ROOT / "tools" / "book-contract.json"

REQUIREMENT_RE = re.compile(r"\*\*([A-Z]{3}-[0-9]{2})\*\*")
OWNER_RE = re.compile(r"Owner:\s*\[[^\]]*\]\(([^)]+)\)")

PROFILE_ORDER = {"substrate": 0, "semantic": 1, "studio": 2}


class ContractError(Exception):
    """The requirement contract cannot be read, decoded or parsed.

    The error also reports a document that does not name the checklist and
    registry files. The loader raises it rather than stopping the interpreter,
    so the command-line entry point can report the defect and choose its own
    exit status.
    """


class RequirementContract(typ.NamedTuple):
    """The checklist and registry files the checks read.

    A `RequirementContract` is built once by `load_requirements` at the
    command-line entry point and passed to the checks, so the file read is
    explicit rather than an import-time side effect.
    """

    checklist: str
    registry: str


def load_document(path: Path) -> dict[str, object]:
    """Load one contract document as a decoded JSON object.

    Parameters
    ----------
    path : Path
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


def load_requirements(path: Path) -> RequirementContract:
    """Load and validate the requirement contract at ``path``.

    Parameters
    ----------
    path : Path
        The contract document to load.

    Returns
    -------
    RequirementContract
        The declared checklist and registry file names.

    Raises
    ------
    ContractError
        If the document cannot be read or does not declare the
        ``requirements`` section with a string ``checklist`` and ``registry``.
    """
    document = load_document(path)
    section = document.get("requirements")
    if not isinstance(section, dict):
        raise ContractError("contract document does not declare requirements")
    checklist = section.get("checklist")
    registry = section.get("registry")
    if not isinstance(checklist, str) or not isinstance(registry, str):
        raise ContractError(
            "requirement contract does not declare the checklist and registry"
        )
    return RequirementContract(checklist=checklist, registry=registry)
