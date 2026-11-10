---
title: Output parity
part: The studio and the contracts
figure: fig-30-output.svg
summary: One Lapidary scene, nine Burin targets and the tolerances that bind them.
---

# Output parity

![One scene, every output.](../figures/fig-30-output.svg)

Cabochon renders every surface from a Lapidary scene through a Burin target.
Display, PDF, print, thumbnail, raster, clipboard, accessibility, hit-testing
and manifest output are workstations that read the same scene. Parity is the
claim that they describe the same drawing.

## The targets

| Target        | Output                                           |
| ------------- | ------------------------------------------------ |
| Display       | Interactive pixels at the current zoom and scale |
| PDF           | Vector pages with selectable text                |
| Print         | Printer-bound output at a declared intent        |
| Thumbnail     | Small raster for lists and previews              |
| Raster        | PNG or equivalent at a declared scale            |
| Clipboard     | Text plus geometry for other applications        |
| Accessibility | Roles, names, states and bounds                  |
| Hit map       | Regions keyed by object identity                 |
| Manifest      | Intents, tolerances, versions and substitutions  |

A target may omit a feature that it cannot represent. It may not invent
geometry, text or state that the scene does not contain.

## What must agree

- **Geometry.** Object bounds, clipping and transforms agree within 0.5
  device pixels at the same scale, and within 0.25 millimetres at print size.
- **Text.** Text placement agrees within 1 pixel, and text remains text in PDF
  and in the accessibility tree wherever the format supports it.
- **Clipping.** A clipped object is clipped identically in every raster and
  vector target, and its hit region is clipped to match.
- **State.** A state mark appears in every target that renders the object,
  including print and thumbnail.
- **Metadata.** Object identity, revision and presentation appear in the
  manifest for every target that can carry metadata.

## Text

Text is never converted to outlines to make parity easier.

- PDF keeps text as text, with embedded fonts.
- Print output embeds fonts or substitutes only with a recorded warning.
- Raster output may anti-alias, but its placement must match the vector
  output.
- Accessibility extraction reads the same text runs that were drawn.
- Clipboard output carries text and its geometry separately.

A font substitution is a documented event, not a silent change. The manifest
records the original font, the substitute and the reason.

## Colour

- Display targets honour the interface palette.
- Print targets declare a colour intent and convert explicitly.
- A colour outside the target's gamut is reported in preflight and recorded in
  the manifest.
- The output must not apply a display-only tint to a print target.

## Hit regions

The hit map describes the same objects that were drawn. A control drawn at a
28-pixel target has a hit region of at least 28 pixels, extended by any
declared hit slop. The hit region is clipped by its parent and transformed with
the object.

A hit map that disagrees with the drawing is a contract failure, because it
makes the visible interface dishonest.

## Failure behaviour

- If a target cannot render an object, it reports the object's identity and
  the reason, and renders the rest of the scene.
- If the renderer fails entirely, the application keeps the last successful
  display and reports the failure in the status line and the diagnostics
  surface.
- A failed export leaves the previous file intact.
- A partial export is marked as partial in the manifest.

Silence is never an acceptable failure mode. A target that cannot render must
say so.

## The manifest

Every export writes `export.json`, which records:

- the scene's version and the renderer's version;
- the target and its options;
- the declared tolerances;
- each object's identity, revision and presentation;
- font substitutions and colour conversions;
- objects that could not be rendered and why;
- whether the output is complete or partial.

The manifest is the evidence that the other artefacts are trustworthy. It is
also the record a support conversation needs.

## Testing parity

A parity test renders a scene that varies clipping, text, transforms, hit
regions and output intent, then compares the targets.

- Geometry and text are compared numerically, not by eye.
- Clipping is compared at the edges, where rounding differs.
- Hit regions are compared with the scene's declared regions.
- Accessibility output is compared with the scene's roles and names.
- A failure names the target, the object and the tolerance that was exceeded.

A visual check is still required. It catches the defects that a numeric
comparison cannot: a missing glyph, a wrong state colour, a shadow that
printed. The SVG proof sheet in this repository is an example of that check for
figures, and the same discipline applies to application output.
