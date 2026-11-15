# Developer guide

The book is Markdown and generated SVG, but its validation tools are a small
Python project. This guide records how that project is configured and how to
run its gates.

## Toolchain

The tools are checked with the df12 Python health standards imported from the
`leynos/agent-template-python` copier template. Development dependencies are
declared in `[dependency-groups] dev` in `pyproject.toml` and pinned in
`uv.lock`. Run every Python command through `uv`, which supplies the pinned
environment:

```sh
uv run ruff check tools
uv run interrogate tools
uv run pylint tools
uv run ty check tools
uv run pytest
```

`make python-lint`, `make python-typecheck` and `make python-test` wrap those
commands, and `make check` runs them with the Markdown, figure and SVG gates.

## Standards in force

The configuration lives in `pyproject.toml` so that each tool's settings travel
with the source.

- Ruff enables a broad rule set, including `D`, `ANN`, `C90`, `PLR`, `S` and
  `TRY`, with a line length of 88 and preview rules on. `E501`, `FBT001` and
  `FBT003` apply everywhere except the figure generator, which is a drawing
  library whose calls spell out geometry and style inline.
- Interrogate requires a docstring on every module, class, function and method,
  including private helpers, at a threshold of 100 per cent.
- Pylint holds the design limits used by the template: at most 4 arguments, 4
  positional arguments, 20 locals and 70 statements per function, and 400 lines
  per module. Modules longer than that are split into packages beside their
  entry-point script rather than exempted.
- Ty type-checks the tools against Python 3.12, the oldest interpreter the
  project supports.
- Pytest runs with a 30-second timeout per test. Hypothesis property tests live
  under `tests/`.

## Documented exemptions

Each exemption is narrow, is recorded beside the rule it relaxes, and states the
reason:

- `tools/figuregen/**` may exceed the argument and local-variable limits. Its
  helpers mirror SVG element attributes and hold one local per drawing
  coordinate; the generated figures are checked byte for byte instead.
- The figure and state checkers disable `S314` and `S405` because they parse the
  repository's own generated SVGs, which are trusted build output rather than
  untrusted input.
- The layout checker disables `RUF001` because its diagnostics reproduce the
  typographic multiplication sign that chapter 14 uses for document-plane sizes.

## Packages beside the scripts

The commit gates call `tools/check-figures.py`, `tools/check-states.py`,
`tools/check-links.py` and `tools/check-requirements.py` directly, and each
remains a thin command-line entry point. Their implementations live in
`figurecheck/`, `statecheck/`, `linkcheck/` and `requirementcheck/` so that no
module exceeds the line limit. Keep new behaviour in the package and the entry
point as a docstring plus a `main()` call.

## Figures

Edit `tools/make-figures.py` or the modules under `tools/figuregen/`, never the
generated SVGs. `make figures` must reproduce the committed figures exactly;
`make validate-svg` also renders the proof sheet with `agent-browser` and fails
if regenerating the figures changes them.
