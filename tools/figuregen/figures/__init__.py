"""Collect one module for each generated figure.

Every module exports a `fig_*` function that `figuregen.cli` imports and calls
to write its SVG under `figures/`. `tools/make-figures.py` runs that CLI and so
regenerates the whole figure set.
"""
