"""Run the registry check against the checklist in one pass.

The `run` function loads `tools/book-contract.json` and delegates to
`requirementcheck.checklist` and `requirementcheck.registry`.
`requirementcheck.cli` and `requirementcheck.selftest` import it.
"""

from __future__ import annotations

import json
import typing as typ

from requirementcheck.checklist import parse_checklist
from requirementcheck.registry import check_records, load_registry

if typ.TYPE_CHECKING:
    from pathlib import Path


def run(root: Path) -> list[str]:
    """Check the registry against the checklist and return any problems.

    Parameters
    ----------
    root : Path
        The repository root. The contract is read from
        ``root / "tools" / "book-contract.json"``; it names the checklist
        and registry files, which are then read relative to ``root``.

    Returns
    -------
    list[str]
        Every diagnostic that `parse_checklist`, `load_registry` and
        `check_records` recorded, in the order they were produced. The list
        is empty when the registry and checklist agree.

    Raises
    ------
    OSError
        If a file named by the contract cannot be read.
    UnicodeDecodeError
        If a file cannot be decoded.
    json.JSONDecodeError
        If the contract is not valid JSON. A malformed registry is recorded
        as a problem instead.
    KeyError
        If the contract lacks its ``requirements``, ``checklist`` or
        ``registry`` keys.
    """
    contract = json.loads((root / "tools" / "book-contract.json").read_text())
    spec = contract["requirements"]
    problems: list[str] = []
    checklist = parse_checklist(root / "book" / spec["checklist"], problems)
    registry = load_registry(root / "tools" / spec["registry"], problems)
    check_records(registry, checklist, root, problems)
    return problems
