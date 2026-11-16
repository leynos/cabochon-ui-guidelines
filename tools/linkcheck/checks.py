"""Run every structural link check in one pass.

The `run_checks` function walks `book/*.md` and calls the link, front-figure
and manifest checks from `linkcheck.links` plus the requirement checks from
`linkcheck.requirements`. `linkcheck.cli` imports it.
"""

from __future__ import annotations

from linkcheck.contract import BOOK, Contract
from linkcheck.links import check_front_figure, check_links, check_manifest
from linkcheck.requirements import (
    check_commands,
    check_profiles,
    check_requirements,
    check_resources,
    check_states,
)


def run_checks(contract: Contract) -> list[str]:
    """Run every structural check and return the accumulated problems."""
    problems: list[str] = []
    chapters = sorted(BOOK.glob("*.md"))
    if not chapters:
        problems.append("no chapters found under book/")
        return problems
    check_links(chapters, problems)
    check_front_figure(chapters, problems)
    check_manifest(chapters, contract, problems)
    check_requirements(contract, problems)
    check_states(contract, problems)
    check_profiles(contract, problems)
    check_commands(contract, problems)
    check_resources(contract, problems)
    return problems
