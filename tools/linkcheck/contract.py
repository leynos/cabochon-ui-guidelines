"""Paths, patterns and the loaded contract shared by the link checks.

The module loads `tools/book-contract.json` and exposes the `BOOK`, `FIGURES`,
`CONTRACT` and regular-expression values that the sibling link modules share.
The check, link, requirement, self-test and command-line modules import it.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BOOK = ROOT / "book"
FIGURES = ROOT / "figures"
CONTRACT = json.loads(
    (ROOT / "tools" / "book-contract.json").read_text(encoding="utf-8")
)

FRONT_FIGURE_RE = re.compile(r"^figure:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)
FRONT_PART_RE = re.compile(r"^part:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)
FRONT_MATTER_RE = re.compile(r"\A---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)", re.DOTALL)
REQUIREMENT_RE = re.compile(r"\*\*([A-Z]{3}-[0-9]{2})\*\*")
OWNER_RE = re.compile(r"Owner:\s*\[[^\]]*\]\(([^)]+)\)")
REQUIREMENT_ID_RE = re.compile(CONTRACT["requirements"]["id_pattern"])

EXTERNAL_PREFIXES = ("http://", "https://", "mailto:")


def resolved_destination(base: Path, target: str) -> Path | None:
    """Resolve a local link destination against a base directory."""
    path_part = target.partition("#")[0]
    if not path_part or path_part.startswith(EXTERNAL_PREFIXES):
        return None
    return (base / path_part).resolve()
