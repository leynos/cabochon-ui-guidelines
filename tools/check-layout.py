#!/usr/bin/env python3
"""Derive the layout budgets from declared component tokens.

The chapter may not state a band total or a document-plane size that the
declared tokens do not produce. Every configuration names its profile, window
and panes; this checker sums the bands and panes, applies separator ownership
and compares the derived document plane with the worked value. The chapter's
band table and worked table are parsed row by row, so an exchanged plane or a
changed total fails rather than merely moving a string elsewhere in the prose.

The implementation lives in the ``layoutcheck`` package beside this script. Run
from the repository root with ``python3 -I tools/check-layout.py``. Pass
``--self-test`` to prove that seven deliberate token, value or table changes fail.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from layoutcheck.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
