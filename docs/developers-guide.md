# Developer guide

The book is Markdown and generated SVG, but its validation tools are a small
Python project. This guide records what those tools require, what every gate
does, and how the Python code is configured.

## Prerequisites

The gates run on Linux. Install these tools before running `make check`:

| Tool              | Version used here          | Purpose                                       |
| :---------------- | :------------------------- | :-------------------------------------------- |
| Python            | 3.12.15                    | Runs every checker and the figure generator   |
| uv                | 0.13.2                     | Supplies the pinned Python environment        |
| xmllint           | libxml 2.12                | Checks that each SVG is well-formed XML       |
| agent-browser     | 0.34.0                     | Renders the SVG proof sheet in Chromium       |
| Chromium          | bundled with agent-browser | Draws the proof sheet and per-figure captures |
| markdownlint-cli2 | 0.23.2                     | Lints the Markdown                            |
| mdtablefix        | 0.6.1                      | Formats tables and wraps prose                |
| typos             | 1.50.1                     | Checks spelling                               |

The Python linting, typing and test tools are declared in
`[dependency-groups] dev` in `pyproject.toml` and pinned in `uv.lock`, so `uv`
installs the same versions everywhere.

## Make targets

Run `make help` for the same list. Each target is safe to run on its own.

| Target             | Purpose                                                                                                 |
| :----------------- | :------------------------------------------------------------------------------------------------------ |
| `figures`          | Regenerate every SVG from the figure generator                                                          |
| `figures-check`    | Check each figure against its declared class and geometry                                               |
| `validate-svg`     | Regenerate, validate the XML, render the proof sheet, and require the committed figures to be unchanged |
| `check-fmt`        | Check Markdown table and paragraph formatting                                                           |
| `fmt`              | Apply that formatting in place                                                                          |
| `markdownlint`     | Lint the Markdown                                                                                       |
| `spelling`         | Check spelling with `typos`                                                                             |
| `python-lint`      | Run ruff, interrogate and pylint over `tools/`                                                          |
| `python-typecheck` | Type-check `tools/` with ty                                                                             |
| `python-test`      | Run the property tests under `tests/`                                                                   |
| `links`            | Check links, anchors, figures, owners and the structural contract                                       |
| `states`           | Check the live-state projection, transitions and event fixtures                                         |
| `keyboard`         | Check the declared Escape routing order                                                                 |
| `layout`           | Derive and check the layout budgets from the declared tokens                                            |
| `requirements`     | Check the requirement registry against the checklist                                                    |
| `check`            | Run every gate above                                                                                    |
| `all`              | Compatibility alias for `check`                                                                         |

`make check` is the commit gate. It runs the targets in Makefile order and
finishes with `All gates passed.`

## Python toolchain

The tools are checked with the df12 Python health standards imported from the
`leynos/agent-template-python` copier template. Run every Python command through
`uv`, which supplies the pinned environment:

```sh
uv run ruff check tools
uv run interrogate tools
uv run pylint tools
uv run ty check tools
uv run pytest
```

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

## Checkers

Each checker is a `tools/check-*.py` script that prints a one-line summary and
exits non-zero on the first contract violation it reports.

| Checker                 | What it checks                                                                                     |
| :---------------------- | :------------------------------------------------------------------------------------------------- |
| `check-figures.py`      | Every generated SVG against its declared figure class, inventory and geometry                      |
| `check-states.py`       | The live-state projection, the chapter's transition table, the state figure and the event fixtures |
| `check-keyboard.py`     | The ordered Escape fixtures                                                                        |
| `check-layout.py`       | The layout budgets, and chapter 14's band and worked tables, against the declared tokens           |
| `check-links.py`        | Links, heading anchors, figure embedding, and the chapter, owner, state and profile manifest       |
| `check-requirements.py` | That the checklist and the structured requirement registry are the same set, with owned evidence   |

Every checker accepts `--self-test`. A self-test applies named mutations to a
temporary copy of the book or its data and requires each check to report the
defect it exists to prevent; it also requires the unmodified baseline to pass.
The Makefile runs both the plain check and its self-test for each checker, so a
gate that silently stops checking anything fails the build.

## Shared Markdown parser

`tools/markdown_structure.py` is the single implementation the Markdown
checkers import for structural parsing. It extracts heading anchors and link or
image destinations, and it removes HTML comments and fenced code before
parsing, so text that a renderer would not display cannot satisfy a structural
contract. Change it rather than copying its rules into a checker.

## Contract sources

The gates compare the book against these data files rather than against
hand-copied expectations:

| File                           | Contract                                                                              |
| :----------------------------- | :------------------------------------------------------------------------------------ |
| `tools/book-contract.json`     | Chapter navigation, part mapping, requirement and owner patterns, states and profiles |
| `tools/figure-data.json`       | Palette roles, state marks, live-state projection, transitions, and figure metadata   |
| `tools/figure-mutations.json`  | The deliberate figure defects that the checker's self-test must detect                |
| `tools/keyboard-fixtures.json` | The ordered Escape scenarios                                                          |
| `tools/layout-budgets.json`    | Layout tokens, profiles and worked configurations                                     |
| `tools/requirements.json`      | The structured requirement registry                                                   |
| `tools/state-fixtures.json`    | The live-state event scenarios                                                        |

## Documented exemptions

Each exemption is narrow, is recorded beside the rule it relaxes, and states
the reason:

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
`tools/check-links.py`, `tools/check-layout.py` and
`tools/check-requirements.py` directly, and each remains a thin command-line
entry point. Their implementations live in `figurecheck/`, `statecheck/`,
`linkcheck/`, `layoutcheck/` and `requirementcheck/` so that no module exceeds
the line limit. Keep new behaviour in the package and the entry point as a
docstring plus a `main()` call.

## Figures

`figures/` holds build output that is committed so that the book renders on
GitHub. Never edit an SVG by hand: edit `tools/make-figures.py` or the modules
under `tools/figuregen/`, then run `make figures`. The output must reproduce
the committed figures exactly, and `make validate-svg` fails if regenerating
them changes a byte. It also renders the proof sheet and one capture per figure
with `agent-browser`, which must be read rather than trusted for XML validity
alone.
