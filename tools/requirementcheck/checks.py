"""Run the registry check against the checklist in one pass.

The `run` function delegates to `requirementcheck.checklist` and
`requirementcheck.registry` with the contract it is given.
`requirementcheck.cli` and `requirementcheck.selftest` import it.
"""

from __future__ import annotations

import typing as typ

from requirementcheck.checklist import parse_checklist
from requirementcheck.registry import check_records, load_registry

if typ.TYPE_CHECKING:
    from pathlib import Path

    from requirementcheck.contract import RequirementContract


def run(root: Path, contract: RequirementContract) -> list[str]:
    """Check the registry against the checklist and return any problems.

    Parameters
    ----------
    root : Path
        The repository root. The checklist and registry files the contract
        names are read relative to it.
    contract : RequirementContract
        The declared checklist and registry file names.

    Returns
    -------
    list[str]
        Every diagnostic that `parse_checklist`, `load_registry` and
        `check_records` recorded, in the order they were produced. The list
        is empty when the registry and checklist agree. A checklist that
        cannot be read is reported in place of the comparison, so the caller
        still receives diagnostics rather than an exception.
    """
    problems: list[str] = []
    try:
        checklist = parse_checklist(root / "book" / contract.checklist, problems)
    except (OSError, UnicodeDecodeError) as error:
        problems.append(f"requirement checklist is unreadable: {error}")
        return problems
    registry = load_registry(root / "tools" / contract.registry, problems)
    check_records(registry, checklist, root, problems)
    return problems
