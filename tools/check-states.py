#!/usr/bin/env python3
"""Check the live-relationship state contract.

The five visible states are a projection of independent facts. This checker
holds one typed source for the legal transitions, compares it with the chapter
table and the generated figure, and runs bounded event sequences against the
projection declared in the book. Replies carry a request generation, a dispatch
epoch and a validated vector, so a stale completion or failure is rejected by
identity rather than by a pre-classified event name. Provider availability is
recorded even while authority is denied; the projection still returns Denied.

The implementation lives in the ``statecheck`` package beside this script. Run
from the repository root with ``python3 -I tools/check-states.py``. Pass
``--self-test`` to prove that each projection, fact and reply-identity mutation
is detected.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from statecheck.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
