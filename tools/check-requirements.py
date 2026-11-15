#!/usr/bin/env python3
"""Check the structured requirement registry against the checklist.

The registry is the structured record of every checklist requirement. Each
record names an owning file and heading anchor, its force, its conformance
profile, the predicate under which it applies and at least one evidence route.
The checklist is a projection of that registry, so this checker proves set
equality, ownership and coverage rather than parsing the book's prose.

The implementation lives in the ``requirementcheck`` package beside this
script. Run from the repository root with
``python3 -I tools/check-requirements.py``. Pass ``--self-test`` to apply
mutations to a temporary copy and confirm that each check detects the defect it
claims to prevent, that the baseline passes and that a wording-only edit still
passes.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from requirementcheck.cli import main

if __name__ == "__main__":
    main()
