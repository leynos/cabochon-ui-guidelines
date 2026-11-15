"""Command-line entry point for the registry checks."""

from __future__ import annotations

import sys

from requirementcheck.checks import run
from requirementcheck.contract import ROOT
from requirementcheck.selftest import self_test


def main() -> None:
    """Run the registry checks, or the self-test when requested."""
    if "--self-test" in sys.argv:
        self_test()
        return
    problems = run(ROOT)
    if problems:
        print("\n".join(problems))
        raise SystemExit(1)
    print("requirements: registry and checklist agree")
