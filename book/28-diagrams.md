---
title: Diagrams
part: The workspace
summary: Source, rendering and diagnostics for logical diagrams, kept together.
---

# Diagrams

A Cabochon diagram is a logical diagram with a source. The source is the
object's primary content; the rendered drawing is a presentation of it. The
instrument keeps both visible, because a diagram that cannot be edited as
source is a picture, and a diagram that cannot be seen as a drawing is a
program.

## The two views

The diagram editor offers two views of one object.

- **Source** shows the Mermaid text, with syntax highlighting and line
  numbers in the operational mono role at the 12-unit floor.
- **Drawing** shows the rendered diagram, fitted to the pane and scrollable.

A split view may show both, with the source on the left and the drawing on the
right. The split ratio is remembered per project.

Switching views does not change the object. The source has a committed revision
and a draft. Editing the source creates a draft; the drawing remains bound to
the last committed source revision that rendered successfully. The drawing is
marked **Unrendered changes** while the draft differs, not **Stale**: staleness
belongs to an external source relationship, and a local draft is a different
fact.

## Rendering

- Rendering is automatic after a short pause in typing, and on demand from the
  **Render** command.
- A successful render replaces the drawing, records the source revision it
  rendered and clears any diagnostics.
- A failed render keeps the last successful drawing, dims it slightly and
  shows the diagnostic beside the source line that caused it.
- The status line reports the render state: **Rendered 14:02**, **Rendering**,
  **Source error at line 12**.

A render must never block the source editor. A large diagram renders in the
background and shows progress in the status line. A render completion from an
older source revision cannot replace a newer successful render.

## Failure kinds

Four failures are distinct and must not share one label.

- **Envelope or schema failure.** The stored object cannot be read as a
  diagram. The embed shows **Malformed** and offers no drawing.
- **Draft syntax error.** The editable source draft does not parse. The
  committed object and the last successful drawing are untouched; the
  diagnostic points at the draft.
- **Committed render error.** The committed source revision is valid text but
  the renderer cannot draw it. The object keeps its last successful drawing,
  reports the render failure and offers the diagnostic.
- **Provider failure.** The provider that supplies the diagram or its data is
  unavailable. The relationship is **Broken** and the last authorised drawing
  may remain visible with its state mark.

## Diagnostics

A diagnostic carries a severity, a source location, a message and a suggested
fix where one is known.

- Errors appear in the oxide role, warnings in the amber-ink role, information
  in the soft-text role.
- The source line is marked in the gutter and underlined with a 1-unit wavy
  rule.
- The message appears below the source pane in the 12-unit operational
  metadata role, with the line number.
- Selecting a diagnostic moves the caret to its location.
- A diagnostic must not be shown as a modal dialog.

The instrument must never discard invalid source. A malformed diagram remains
editable, exportable and recoverable. A diagnostic is subject to the metadata
disclosure policy when it names a protected object.

## Drawing presentation

The drawing uses the Cabochon palette by default: ink lines, paper or high
ground, pine for emphasis and oxide for a selected element. It does not use a
diagramming tool's stock colours unless the object declares a theme. A declared
theme is authored content, not interface chrome; it is preserved within the
target's gamut and is not coerced into an interface role.

- Text in the drawing uses the interface voice, at a size that remains legible
  at the current zoom.
- A selected element carries a 2-unit oxide outline. Selection does not change
  the element's saved fill or stroke.
- Hovering an element shows its label and its source location in a tooltip.
- The drawing may be zoomed from 25 to 400 per cent; the fit command resets it
  to the pane.

## Elements and selection

A rendered diagram exposes its elements as selectable objects.

- Clicking an element selects it and highlights its source location.
- Selecting source text highlights the corresponding element, where the
  renderer can map them.
- The inspector shows the element's kind, label and stable element identity.
- A diagram element may be addressed by the formula tool when its provider
  declares a scalar selector, such as a node's value.

A source location is a presentation address, not an identity. Reordering the
source changes line numbers without changing element identity. An expression
that reads a diagram element declares whether it uses the stable element
identity or a positional source location; the default is the stable identity.
Deleting an element produces a recoverable broken reference, not a silent
attachment to the next element.

The rendered drawing, its element mapping, its hit regions and its accessible
nodes all refer to the same committed source revision. A render from an older
revision cannot replace a newer one.

## Embedded diagrams

A note embeds the diagram using the block, inline or thumbnail profile from
[Embeds](32-embeds.md). The block carries the state edge and chip; the inline
form keeps the state mark and an inspection route. Opening the embed opens the
diagram editor, not a separate copy.

A diagram whose committed source has changed but whose drawing has not been
re-rendered shows **Unrendered changes**. The last drawing remains visible and
printable, labelled with that state. A diagram whose external source has
advanced shows **Stale**; a diagram whose provider is unavailable shows
**Broken**.

## Accessibility

The diagram must expose a semantic projection that describes its structure, not
only its title. The accessibility tree exposes nodes, edges, labels and
relationships in reading order, with actions for selecting and inspecting an
element. The source is an additional view, not the only successful
accessibility path. A purely visual diagram is not acceptable.

## Export

A diagram exports to SVG, PNG and PDF through the shared Burin targets, and its
source exports as text. SVG is a supported vector encoding in the studio
profile, not a separate Burin target. The export must preserve the drawing's
geometry and its text as text where the target supports it, and it must
identify the source revision and presentation intent it rendered. The
instrument must not flatten the source into the drawing on export. These are
user exports; they do not create the eight-artefact conformance bundle, which
is a separate review command.

## What the diagram is not

- A bitmap with a hidden text layer.
- A one-way render that discards the source after the first draw.
- A canvas that cannot be read by assistive technology.
- A separate file format that other instruments cannot open.
