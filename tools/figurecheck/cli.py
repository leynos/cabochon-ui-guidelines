"""Command-line entry point for the figure contract checks.

The `main` function loads `tools/figure-data.json`, validates the state records
and runs the checks from `figurecheck.checks` over the `figures/` directory. It
selects `figurecheck.selftest` when `--self-test` is given. The
`tools/check-figures.py` script imports and calls it.
"""

from __future__ import annotations

import argparse
import sys

from figurecheck.checks import run
from figurecheck.contract import (
    DATA_PATH,
    FIGURES,
    ContractError,
    load_document,
    state_records,
)
from figurecheck.selftest import self_test


def _parser() -> argparse.ArgumentParser:
    """Return the parser for the figure-check command line."""
    parser = argparse.ArgumentParser(
        prog="check-figures",
        description="Check generated SVG figures against the figure contract.",
        allow_abbrev=False,
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="prove that each declared mutation is detected",
    )
    return parser


def main() -> int:
    """Run the figure checks and report the result."""
    arguments = _parser().parse_args()
    try:
        if arguments.self_test:
            return self_test()
        data = load_document(DATA_PATH)
        records, messages = state_records(data)
    except ContractError as error:
        print(f"figure contract: {error}", file=sys.stderr)
        return 1
    if messages:
        for message in messages:
            print(f"figure contract: {message}", file=sys.stderr)
        return 1
    errors = run(FIGURES, data, records)
    if errors:
        for error in errors:
            print(f"figure contract: {error}", file=sys.stderr)
        return 1
    print(
        f"figure contract: {len(list(FIGURES.glob('*.svg')))} figures "
        "satisfy their declared class, inventory and geometry"
    )
    return 0
