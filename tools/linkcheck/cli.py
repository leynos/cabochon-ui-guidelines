"""Command-line entry point for the link checks."""

from __future__ import annotations

import sys

from linkcheck.checks import run_checks
from linkcheck.contract import BOOK, FIGURES
from linkcheck.selftest import self_test


def main() -> int:
    """Run the structural checks, or the self-test when requested."""
    if "--self-test" in sys.argv[1:]:
        return self_test()
    problems = run_checks()
    if problems:
        for problem in problems:
            print(f"error: {problem}", file=sys.stderr)
        return 1
    chapters = len(list(BOOK.glob("*.md")))
    figures = len(list(FIGURES.glob("*.svg")))
    print(f"links: ok ({chapters} chapters, {figures} figures)")
    return 0
