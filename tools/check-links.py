#!/usr/bin/env python3
"""Check the book's links and its structural contract.

Links, images and headings are parsed from Markdown after HTML comments, fenced
code blocks and inline code spans have been removed. Local fragments are checked
against the current file as well as other files, and duplicate headings receive
the same numeric suffixes a Markdown renderer assigns. The semantic checks cover
the contents graph, requirement identifiers, state and profile ownership, and
the command and resource relationships. They are structural: they do not parse
prose or assert whole paragraphs.

The implementation lives in the ``linkcheck`` package beside this script. Run
from the repository root with ``python3 -I tools/check-links.py``. Pass
``--self-test`` to require a clean baseline, prove each mutation actually
changed its target, and assert the expected diagnostic for every defect.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from linkcheck.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
