#!/usr/bin/env python3
"""Generate the SVG figures for the Cabochon interface guidelines.

The figures share one palette and one geometry vocabulary; the implementation
lives in the ``figuregen`` package beside this script. Run from the repository
root with ``python3 -I tools/make-figures.py``; the generated SVGs are written
to ``figures/``.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from figuregen.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
