#!/usr/bin/env python3
"""Check generated figures against the shared figure contract.

The generator embeds a machine-readable annotation in every SVG. This checker
compares that annotation with ``tools/figure-data.json`` and with the rendered
geometry. It uses a deliberately constrained SVG subset: the geometry it
measures contains only ``rect``, ``circle``, ``ellipse``, ``line``, ``polyline``,
``polygon`` and absolute ``M``/``L``/``A``/``Z`` paths, with
``translate``/``scale``/``rotate``/``matrix`` transforms. Clipping attributes are
rejected, so a mark's visible bounds are its transformed bounds intersected with
the viewBox.

A state is one record: identity, word, mark, role and colour are checked
together, and a figure must contain the semantic inventory declared for it.
Production figures declare bounds in logical units; the checker derives those
bounds from the drawn primitives and their ancestor transforms rather than
trusting a rectangle attribute or the embedded annotation.

The implementation lives in the ``figurecheck`` package beside this script. Run
from the repository root with ``python3 -I tools/check-figures.py``. Pass
``--self-test`` to prove that each deliberate mutation is detected.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from figurecheck.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
