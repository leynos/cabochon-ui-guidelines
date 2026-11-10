---
title: Bitmaps
part: The workspace
summary: A bounded pixel editor that keeps resolution, intent and identity honest.
---

# Bitmaps

A bitmap in Cabochon is an object with pixels, a resolution, a colour intent
and an identity. The editor is deliberately bounded: it provides the operations
needed to prove editable embedding, not a full paint package.

## The object

A bitmap object declares:

- its pixel dimensions;
- its physical resolution, in pixels per inch;
- its colour intent, such as sRGB or a print intent;
- its alpha behaviour, opaque or transparent;
- its identity and revision.

A presentation may scale the bitmap for display, but scaling never changes the
stored pixels. Upscaling for export requires an explicit choice and is recorded
in the exported metadata.

## Layout

The bitmap editor uses a document plane with rulers, a compact tool palette and
an inspector.

- Rulers: 20 pixels, in metadata type, showing the current unit.
- Tool palette: 48 pixels wide, one column of 30-pixel tools.
- Document plane: the image on a checkerboard for transparency, at the current
  zoom.
- Inspector: 240 pixels, showing dimensions, resolution, intent and state.
- Status line: pointer position, colour under the pointer, zoom and the active
  tool.

## Tools

The first batch provides select, move, brush, eraser, rectangle, ellipse,
eyedropper and text. Each tool:

- has a 30-pixel button, a 16-pixel glyph and a tooltip naming its shortcut;
- shows its options in the tool strip or the inspector, not in a floating
  palette;
- commits its stroke as one transaction when the pointer is released;
- cancels cleanly on Escape, restoring the pixels from before the stroke.

A tool must not leave a half-applied stroke when the user switches tools or the
window loses focus.

## Zoom and pan

- Zoom range: 10 to 1600 per cent.
- Zoom steps: 10, 25, 50, 100, 200, 400, 800, 1600.
- At 100 per cent, one image pixel maps to one device pixel at the declared
  scale.
- Space-drag pans; the scroll wheel scrolls; Control with the wheel zooms.
- The zoom level is remembered per bitmap, not per application.

The editor must not resample for display at integer zoom levels, so that pixel
art remains crisp.

## Colour

- The foreground and background colours are shown as two 24-pixel swatches at
  the bottom of the tool palette.
- The palette is the environment palette plus a greyscale ramp. A bitmap may
  contain other colours; the editor does not restrict the image to the
  interface palette.
- The eyedropper samples the displayed colour, and the status line reports
  both the hex value and the colour intent.
- A colour that cannot be represented in the document's intent is marked in
  the inspector, not silently converted.

## Transparency

Transparency is shown as a checkerboard in the document plane and is never
flattened into white on save.

- The checkerboard uses two neutral values derived from the palette, at low
  contrast, so that it does not compete with the image.
- An opaque export flattens transparency against a chosen colour and records
  that choice in the export manifest.
- A PNG export preserves alpha unless the user chooses otherwise.

## Resolution and print

The bitmap's physical resolution determines its printed size. The editor must
show the printed size in the inspector and warn when the resolution falls below
150 pixels per inch for the intended print size.

A warning is not a block. The user may print at a lower resolution, and the
preflight report records the choice.

## Editing and identity

- Every presentation of the bitmap updates when one is edited.
- A crop or a resize is an edit with a revision, not a new object.
- **Duplicate** creates a new object; **Export** writes a file and leaves the
  object in place.
- Undo restores pixels, not identity.

## Embedded bitmaps

A note may embed a bitmap as a block, a thumbnail or an inline mark. The embed
carries the object's state edge and chip. Opening the embed opens the bitmap
editor at the object's last zoom and selection.

## What the bitmap editor is not

- A vector drawing tool. Use Burin Draw for paths and shapes.
- A photo retoucher. The first batch does not provide curves, layers or
  filters.
- A format converter. Export uses the Burin output contract and records its
  intent.
- A place where an image is flattened into a note. The embed keeps the object.
