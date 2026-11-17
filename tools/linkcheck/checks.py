"""Run every structural link check in one pass.

The `run_checks` function walks `book/*.md` and calls the link, front-figure
and manifest checks from `linkcheck.links` plus the requirement checks from
`linkcheck.requirements`. `linkcheck.cli` imports it.
"""

from __future__ import annotations

import typing as typ

if typ.TYPE_CHECKING:
    from pathlib import Path

    from linkcheck.contract import Contract

from linkcheck.links import check_front_figure, check_links, check_manifest
from linkcheck.requirements import (
    check_commands,
    check_profiles,
    check_requirements,
    check_resources,
    check_states,
)


def run_checks(contract: Contract, book: Path) -> list[str]:
    """Run every structural check and return the accumulated problems.

    Parameters
    ----------
    contract : Contract
        The loaded link contract.
    book : Path
        The book directory that holds the chapters and their manifest.

    Returns
    -------
    list[str]
        One problem per structural defect the checks found.
    """
    problems: list[str] = []
    chapters = sorted(book.glob("*.md"))
    if not chapters:
        problems.append("no chapters found under book/")
        return problems
    check_links(chapters, book, problems)
    check_front_figure(chapters, book, problems)
    check_manifest(chapters, book, contract, problems)
    check_requirements(book, contract, problems)
    check_states(book, contract, problems)
    check_profiles(book, contract, problems)
    check_commands(book, contract, problems)
    check_resources(book, contract, problems)
    return problems
