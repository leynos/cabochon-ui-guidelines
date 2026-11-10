# Cabochon interface guidelines

The interface guidelines for Cabochon's first small world: the contracts,
workspace instruments and studio tools that share one document-centred
environment.

The book is written in Markdown, one chapter per file, with SVG figures under
`figures/`. Start at [the contents](book/README.md).

## Build and check

```sh
make figures      # regenerate the SVG figures
make check        # run formatting, lint, spelling, link and SVG gates
```

The book targets the en-GB Oxford spelling used by Cabochon's own documentation.
