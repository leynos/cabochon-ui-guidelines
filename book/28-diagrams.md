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
  numbers in metadata type.
- **Drawing** shows the rendered diagram, fitted to the pane and scrollable.

A split view may show both, with the source on the left and the drawing on the
right. The split ratio is remembered per project.

Switching views does not change the object. Editing the source marks the
drawing stale until it is rendered, and the drawing keeps its last successful
render while the new source is invalid.

## Rendering

- Rendering is automatic after a short pause in typing, and on demand from the
  **Render** command.
- A successful render replaces the drawing and clears any diagnostics.
- A failed render keeps the last successful drawing, dims it slightly and
  shows the diagnostic beside the source line that caused it.
- The status line reports the render state: **Rendered 14:02**, **Rendering**,
  **Source error at line 12**.

A render must never block the source editor. A large diagram renders in the
background and shows progress in the status line.

## Diagnostics

A diagnostic carries a severity, a line and column, a message and a suggested
fix where one is known.

- Errors appear in oxide, warnings in amber ink, information in soft.
- The source line is marked in the gutter and underlined with a 1-pixel wavy
  rule.
- The message appears below the source pane in 11-pixel metadata, with the
  line number.
- Selecting a diagnostic moves the caret to its location.
- A diagnostic must not be shown as a modal dialog.

The instrument must never discard invalid source. A malformed diagram remains
editable, exportable and recoverable.

## Drawing presentation

The drawing uses the Cabochon palette by default: ink lines, paper or high
ground, pine for emphasis and oxide for a selected element. It does not use a
diagramming tool's stock colours unless the object declares a theme.

- Text in the drawing uses the interface voice, at a size that remains legible
  at the current zoom.
- A selected element carries a 2-pixel oxide outline.
- Hovering an element shows its label and its source line in a tooltip.
- The drawing may be zoomed from 25 to 400 per cent; the fit command resets it
  to the pane.

## Elements and selection

A rendered diagram exposes its elements as selectable objects.

- Clicking an element selects it and highlights its source line.
- Selecting source text highlights the corresponding element, where the
  renderer can map them.
- The inspector shows the element's kind, label and source location.
- A diagram element may be addressed by the formula tool when its provider
  declares a scalar selector, such as a node's value.

## Embedded diagrams

A note embeds the diagram as a block, with its state edge and chip. The
presentation may be the drawing, a thumbnail or a caption. Opening the embed
opens the diagram editor, not a separate copy.

A diagram whose source has changed shows **Stale** until the drawing is
re-rendered. The last drawing remains visible and printable, labelled with its
state.

## Accessibility

The diagram must expose a text alternative that describes its structure, not
only its title. The source is that alternative in its most precise form, and
the accessibility tree should expose nodes, edges and labels in reading order.
A purely visual diagram is not acceptable.

## Export

A diagram exports to SVG, PNG and PDF through the shared Burin targets, and its
source exports as text. The export must preserve the drawing's geometry and its
text as text where the target supports it. The instrument must not flatten the
source into the drawing on export.

## What the diagram is not

- A bitmap with a hidden text layer.
- A one-way render that discards the source after the first draw.
- A canvas that cannot be read by assistive technology.
- A separate file format that other instruments cannot open.
