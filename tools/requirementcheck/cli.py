"""Command-line entry point for the registry checks.

The `main` function loads `tools/book-contract.json` and runs
`requirementcheck.checks.run` over the repository, and selects
`requirementcheck.selftest` when `--self-test` is given. The
`tools/check-requirements.py` script imports and calls it.
"""

from __future__ import annotations

import sys

from requirementcheck.checks import run
from requirementcheck.contract import DATA_PATH, ROOT, ContractError, load_requirements
from requirementcheck.selftest import self_test


def main() -> int:
    """Run the registry checks, or the self-test when requested.

    ``--self-test`` anywhere in `sys.argv` selects `self_test` instead of the
    registry check. Otherwise every problem `run` reports is printed, one per
    line. A contract the loader rejects is reported in one line on standard
    error.

    Returns
    -------
    int
        The process exit status: zero on success, one on failure.
    """
    if "--self-test" in sys.argv:
        self_test()
        return 0
    try:
        contract = load_requirements(DATA_PATH)
    except ContractError as error:
        print(f"requirement contract: {error}", file=sys.stderr)
        return 1
    problems = run(ROOT, contract)
    if problems:
        print("\n".join(problems))
        return 1
    print("requirements: registry and checklist agree")
    return 0
