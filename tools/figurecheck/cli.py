"""Command-line entry point for the figure contract checks.

The `main` function runs the checks from `figurecheck.checks` over the
`figures/` directory and selects `figurecheck.selftest` when `--self-test` is
given. The `tools/check-figures.py` script imports and calls it.
"""

from __future__ import annotations

import sys

from figurecheck.checks import run
from figurecheck.contract import FIGURES
from figurecheck.selftest import self_test


def main() -> int:
    """Run the figure checks and report the result."""
    if "--self-test" in sys.argv:
        return self_test()
    errors = run(FIGURES)
    if errors:
        for error in errors:
            print(f"figure contract: {error}", file=sys.stderr)
        return 1
    print(
        f"figure contract: {len(list(FIGURES.glob('*.svg')))} figures "
        "satisfy their declared class, inventory and geometry"
    )
    return 0
