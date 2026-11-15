"""Command-line entry point for the state contract checks.

The `main` function loads `tools/figure-data.json` and
`tools/state-fixtures.json`, validates the transitions and event scenarios, and
selects `statecheck.selftest` for `--self-test`. The `tools/check-states.py`
script imports and calls it.
"""

from __future__ import annotations

import sys

from statecheck.contract import (
    DATA_PATH,
    FIXTURES_PATH,
    ContractError,
    load_contract,
    scenarios,
)
from statecheck.scenarios import run_scenarios
from statecheck.selftest import self_test
from statecheck.transitions import compare_chapter, compare_figure, validate_transitions


def main() -> int:
    """Run the state contract checks or the mutation self-test."""
    try:
        if "--self-test" in sys.argv:
            return self_test()
        contract = load_contract(DATA_PATH, FIXTURES_PATH)
        errors = validate_transitions(contract.transitions, contract)
        errors.extend(compare_chapter(contract.transitions))
        errors.extend(compare_figure(contract.transitions))
        errors.extend(run_scenarios(contract))
    except ContractError as error:
        print(f"state contract: {error}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"state contract: {error}", file=sys.stderr)
        return 1
    print(
        f"state contract: {len(contract.transitions)} transitions and "
        f"{len(scenarios(contract.fixtures))} event scenarios satisfy the projection"
    )
    return 0
