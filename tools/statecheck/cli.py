"""Command-line entry point for the state contract checks.

The `main` function loads `tools/figure-data.json` and
`tools/state-fixtures.json`, validates the transitions and event scenarios, and
selects `statecheck.selftest` for `--self-test`. The `tools/check-states.py`
script imports and calls it.
"""

from __future__ import annotations

import sys
from xml.etree import ElementTree

from statecheck import contract as state_contract
from statecheck.contract import ContractError
from statecheck.scenarios import run_scenarios
from statecheck.selftest import self_test
from statecheck.transitions import compare_chapter, compare_figure, validate_transitions


def _report(error: object) -> int:
    """Print one handled failure and return the failing exit status."""
    print(f"state contract: {error}", file=sys.stderr)
    return 1


def main() -> int:
    """Run the state contract checks or the mutation self-test."""
    try:
        if "--self-test" in sys.argv:
            return self_test()
        contract = state_contract.load_contract(
            state_contract.DATA_PATH, state_contract.FIXTURES_PATH
        )
        errors = validate_transitions(contract.transitions, contract)
        errors.extend(compare_chapter(contract.transitions, state_contract.CHAPTER))
        errors.extend(compare_figure(contract.transitions, state_contract.FIGURE))
        errors.extend(run_scenarios(contract))
    except (
        ContractError,
        OSError,
        UnicodeDecodeError,
        ElementTree.ParseError,
    ) as error:
        return _report(error)
    if errors:
        for error in errors:
            print(f"state contract: {error}", file=sys.stderr)
        return 1
    print(
        f"state contract: {len(contract.transitions)} transitions and "
        f"{len(state_contract.scenarios(contract.fixtures))} event scenarios "
        "satisfy the projection"
    )
    return 0
