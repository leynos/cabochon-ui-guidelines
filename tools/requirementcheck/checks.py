"""Run the registry check against the checklist in one pass."""

from __future__ import annotations

import json
import typing as typ

from requirementcheck.checklist import parse_checklist
from requirementcheck.registry import check_records, load_registry

if typ.TYPE_CHECKING:
    from pathlib import Path


def run(root: Path) -> list[str]:
    """Check the registry against the checklist and return any problems."""
    contract = json.loads((root / "tools" / "book-contract.json").read_text())
    spec = contract["requirements"]
    problems: list[str] = []
    checklist = parse_checklist(root / "book" / spec["checklist"], problems)
    registry = load_registry(root / "tools" / spec["registry"], problems)
    check_records(registry, checklist, root, problems)
    return problems
