---
title: Bitmaps
part: The workspace
summary: A bounded pixel editor that keeps resolution, intent and identity honest.
---

# Bitmaps

A bitmap in Cabochon is an object with pixels, a resolution, a colour intent
and an identity. The editor is deliberately bounded: it provides the operations
needed to prove editable embedding, not a full paint package.

The editor's chrome follows the interface style in this book. The image does
not. Its colours, its sample values and its own metadata are authored content:
they are preserved across display, scaling and export, and the interface
palette is never imposed on them.

## The object

A bitmap object declares:

- its stored sample format and bit depth;
- its pixel dimensions;
- its physical resolution, in pixels per inch;
- its colour space and embedded profile;
- its output intent when one is declared for print;
- its alpha representation, straight or premultiplied, and whether it is
  opaque or transparent;
- its identity and revision.

Colour space, profile and output intent are distinct. sRGB is a colour space
with a profile; print is an output intent. A presentation may scale the bitmap
for display, but scaling never changes the stored pixels. Upscaling for export
requires an explicit choice and is recorded in the exported metadata.

## Layout

The bitmap editor uses a document plane with rulers, a compact tool palette and
an inspector.

- Rulers: 20 logical units, in the operational metadata role, showing the
  current unit and its scale.
- Tool palette: 48 logical units wide, one column of the **tool button** role
  from [Spacing and metrics](14-spacing-metrics.md): 30 units high, 28 units
  minimum, with a 16-unit glyph and a 28-unit effective target.
- Document plane: the image on a checkerboard for transparency, at the current
  zoom.
- Inspector: 240 logical units, showing dimensions, resolution, colour space,
  intent and state.
- Status line: pointer position, colour under the pointer, zoom and the active
  tool.

The rulers measure document space, not interface space. Their unit labels are
metadata, and the tick spacing is computed from the document zoom rather than
from the interface scale.

## Tools

The first batch provides select, move, brush, eraser, rectangle, ellipse,
eyedropper and text. Each tool:

- has a 30-unit button, a 16-unit glyph and a tooltip naming its shortcut;
- shows its options in the tool strip or the inspector, not in a floating
  palette;
- commits its stroke as one transaction when the pointer is released;
- cancels cleanly on Escape, restoring the pixels from before the stroke.

A tool must not leave a half-applied stroke when the user switches tools, the
window loses focus or the tool is switched by shortcut. The commit boundary is
one deterministic rule and applies to every switching route. Selection and pan
create no content mutation.

Every tool in this palette is a **canvas tool** in the sense of
[Selection and tools](24-selection-tools.md). It has no **Insert** action and
no **Cancel** button of its own; its effect is the gesture it completes, and
Escape cancels the pending gesture. A read-only inspection, such as the
eyedropper's sampled-colour report, is not a canvas tool and does not commit
pixels.

## Zoom and pan

- Zoom range: 10 to 1600 per cent.
- Zoom steps: 10, 25, 50, 100, 200, 400, 800, 1600.
- At 100 per cent, one stored sample maps to one document unit, and one
  document unit is one logical unit. The logical unit then maps to device
  pixels through interface and device scale. The zoom percentage is independent
  of interface scale.
- Space-drag pans; the scroll wheel scrolls; Control with the wheel zooms.
- The zoom level is remembered per bitmap, not per application.

Display sampling follows the scale factor. An exact integer enlargement factor
uses nearest-neighbour sampling so that pixel art remains crisp; a non-integer
factor, including 25 per cent, uses the declared filtered sampling. Neither
changes the stored pixels. The editor does not force an integer factor to
obtain a sharp preview.

Four quantities form the display transform and must be named separately.

| Quantity                   | What it governs                                           |
| -------------------------- | --------------------------------------------------------- |
| Stored samples             | The image's pixel grid and bit depth                      |
| Document zoom              | Stored sample → document unit; 100 per cent is one to one |
| Logical mapping            | One document unit = one logical unit                      |
| Interface and device scale | Logical unit → device pixel → physical pixel              |

At 100 per cent, one stored sample becomes one document unit, which is one
logical unit, which interface scale turns into device pixels and device scale
turns into physical pixels. On a display with a fractional factor, several
device pixels may represent one stored sample. Interface scale therefore sizes
the image and the chrome together; it does not change the zoom percentage,
document coordinates or the stored sample density. Changing interface scale,
the device transform, the zoom or the theme never changes the stored pixels,
physical resolution or identity.

## Colour

- The foreground and background colours are shown as two 24-unit swatches at
  the bottom of the tool palette. Their visible mark is below the 28-unit
  minimum, so each effective hit region is expanded to 28 units and the two
  regions do not overlap. The swatch reports its colour and its swap action
  through its accessible name.
- The palette is the environment palette plus a greyscale ramp. A bitmap may
  contain other colours; the editor does not restrict the image to the
  interface palette.
- The eyedropper samples the document pixel by default and reports the stored
  colour and the colour space. A display-composited sampling mode, which
  includes the checkerboard and display transform, is a separately labelled
  choice.
- A sampled colour is converted explicitly before it is written back when the
  document's colour space differs from the sampled colour's space. The
  conversion names its source and destination profiles and is recorded in the
  document's history.
- A colour that falls outside the document's gamut is marked in the inspector
  before it is written back. The user chooses between clipping, a perceptual
  conversion and cancelling; the editor does not silently substitute a nearest
  colour.
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
- A crop or a resize is an edit with a content revision, not a new object.
- **Duplicate** creates a new object; **Export** writes a file and leaves the
  object in place.
- Undo restores pixels, not identity.
- Cancelling a stroke changes neither committed pixels nor identity.
- A display zoom or theme change does not mutate pixels, resolution or
  identity.

## Embedded bitmaps

A note may embed a bitmap using the block, inline or thumbnail profile. The
block embed carries the object's state edge and chip; the compact forms keep
the state mark and an inspection route. Opening the embed opens the bitmap
editor at the object's last zoom and selection.

## What the bitmap editor is not

- A vector drawing tool. Use Burin Draw for paths and shapes.
- A photo retoucher. The first batch does not provide curves, layers or
  filters.
- A format converter. Export uses the Burin output contract and records its
  intent.
- A place where an image is flattened into a note. The embed keeps the object.
