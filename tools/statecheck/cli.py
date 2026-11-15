"""Command-line entry point for the state contract checks."""

from __future__ import annotations

import sys

from statecheck.contract import FIXTURES, transition_rows
from statecheck.scenarios import run_scenarios
from statecheck.selftest import self_test
from statecheck.transitions import compare_chapter, compare_figure, validate_transitions


def main() -> int:
    """Run the state contract checks or the mutation self-test."""
    if "--self-test" in sys.argv:
        return self_test()
    transitions = transition_rows()
    errors = validate_transitions(transitions)
    errors.extend(compare_chapter(transitions))
    errors.extend(compare_figure(transitions))
    errors.extend(run_scenarios())
    if errors:
        for error in errors:
            print(f"state contract: {error}", file=sys.stderr)
        return 1
    print(
        f"state contract: {len(transitions)} transitions and "
        f"{len(FIXTURES['scenarios'])} event scenarios satisfy the projection"
    )
    return 0
