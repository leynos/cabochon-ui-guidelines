"""Command-line entry point for the registry checks.

The `main` function runs `requirementcheck.checks.run` over the repository and
selects `requirementcheck.selftest` when `--self-test` is given. The
`tools/check-requirements.py` script imports and calls it.
"""

from __future__ import annotations

import sys

from requirementcheck.checks import run
from requirementcheck.contract import ROOT
from requirementcheck.selftest import self_test


def main() -> None:
    """Run the registry checks, or the self-test when requested.

    ``--self-test`` anywhere in `sys.argv` selects `self_test` instead of the
    registry check. Otherwise every problem `run` reports is printed, one per
    line, and the process exits non-zero; a clean result prints
    ``"requirements: registry and checklist agree"``. Errors other than
    `SystemExit` are not caught.

    Returns
    -------
    None
        The function returns nothing; its outcome is the printed report and
        the exit status.

    Raises
    ------
    SystemExit
        With status one when the checks report any problem, and likewise
        when the self-test fails.
    """
    if "--self-test" in sys.argv:
        self_test()
        return
    problems = run(ROOT)
    if problems:
        print("\n".join(problems))
        raise SystemExit(1)
    print("requirements: registry and checklist agree")
