"""Run every structural link check in one pass."""

from __future__ import annotations

from linkcheck.contract import BOOK
from linkcheck.links import check_front_figure, check_links, check_manifest
from linkcheck.requirements import (
    check_commands,
    check_profiles,
    check_requirements,
    check_resources,
    check_states,
)


def run_checks() -> list[str]:
    """Run every structural check and return the accumulated problems."""
    problems: list[str] = []
    chapters = sorted(BOOK.glob("*.md"))
    if not chapters:
        problems.append("no chapters found under book/")
        return problems
    check_links(chapters, problems)
    check_front_figure(chapters, problems)
    check_manifest(chapters, problems)
    check_requirements(problems)
    check_states(problems)
    check_profiles(problems)
    check_commands(problems)
    check_resources(problems)
    return problems
