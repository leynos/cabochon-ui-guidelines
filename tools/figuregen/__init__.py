"""Generate the Cabochon book's SVG figures from one shared drawing package.

The package holds `canvas` SVG primitives, a `palette` of colour roles and font
stacks, the `figdata` catalogue loader for `tools/figure-data.json`, shared
`ornaments`, `glyphs`, `widgets` and `production` fixtures, and one builder per
figure under `figuregen.figures`. `figuregen.cli` registers those builders,
loads the catalogue and threads it through them, and `tools/make-figures.py` is
the entry point that runs it.
"""
