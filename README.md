# Cabochon interface guidelines

The interface guidelines for Cabochon's first small world: the contracts,
workspace instruments and studio tools that share one document-centred
environment.

The book is written in Markdown, one chapter per file, with SVG figures under
`figures/`. Start at [the contents](book/README.md).

## Build and check

```sh
make figures      # regenerate the SVG figures
make check        # run every gate: formatting, Markdown lint, spelling, Python
                  # lint, typing and tests, links, figures, the state, keyboard,
                  # layout and requirement contracts, and the SVG proof sheet
```

The validation tools are Python, and they follow the df12 Python health
standards imported from `leynos/agent-template-python`: ruff, interrogate,
pylint, ty and pytest, all run through `uv`. See the
[developer guide](docs/developers-guide.md) for the standards in force and the
documented exemptions.

The book targets the en-GB Oxford spelling used by Cabochon's own documentation.
