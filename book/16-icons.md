---
title: Icons
part: Visual language
figure: fig-11-icons.svg
summary: A monochrome line vocabulary, three sizes and four states.
---

# Icons

![Icon grid, sizes and states.](../figures/fig-11-icons.svg)

Cabochon icons are monochrome line drawings. They are drawn on a 24-pixel grid
with a 2-pixel stroke, square caps and joins, and no fills except where a shape
must read as solid at small size, such as the selection arrow.

These rules govern interface icons. An image inside a document, a diagram's own
symbols and a bitmap's content are authored material, not interface icons, and
the environment does not redraw them in the icon style.

Colour is reserved for state. A default icon inherits the ink of its text. An
active icon uses oxide. A stale icon uses amber ink and is always accompanied
by a label. A disabled icon uses line and is removed from the focus order.

## Sizes

| Size | Use                                                       |
| ---- | --------------------------------------------------------- |
| 16   | Inline with metadata, table rows, tree leaves, tool strip |
| 20   | Compact controls and dense pane heads                     |
| 24   | Primary actions and standalone icon buttons               |

The stroke scales with the size: 1.25 pixels at 16, 1.5 at 20 and 2 at 24, so
that the optical weight stays constant. Icons are drawn at the target size, not
scaled from a single bitmap.

## The first vocabulary

The first batch uses fourteen core glyphs: select, text, rectangle, ellipse,
pen, line, table, formula, link, lock, warning, check, refresh and gear. Each
has one meaning across every instrument.

The fourteen are a core subset, not the whole available vocabulary. The studio
instruments register further glyphs in the same shared set: hand, brush,
eraser, eyedropper, crop, zoom and the remaining canvas tools named in
[Bitmaps](29-bitmaps.md) and [Burin Draw](33-burin-draw.md). A registered glyph
follows the same grid, stroke and state rules as a core glyph, and it is
declared once so that two instruments cannot draw the same concept twice.

- **Link** means a live relationship to another object.
- **Lock** means a denied or protected capability.
- **Warning** means a problem that needs attention but does not block work.
- **Check** means a completed or valid state.
- **Refresh** means a manual or in-progress refresh.

An instrument that needs a new concept should propose a glyph to the shared
vocabulary rather than drawing a private variant of an existing one.

## Drawing rules

- Keep the glyph inside a 20-pixel live area within the 24-pixel box, leaving
  2 pixels of optical margin.
- Use one stroke weight throughout a glyph. Do not mix a 1-pixel detail with a
  2-pixel outline.
- Prefer open shapes. A closed shape with a fill reads as a state, not a tool.
- Avoid text inside icons. The only exception is the letter T for the text
  tool, and it must be drawn as a path, not as live text.
- Draw at the final size and check the 16-pixel version before accepting the
  24-pixel one.

## States

Every icon has four states, and every state must be distinguishable without
colour.

| State    | Colour    | Additional cue                               |
| -------- | --------- | -------------------------------------------- |
| Default  | Ink       | None                                         |
| Active   | Oxide     | Pressed or selected background               |
| Stale    | Amber ink | A word beside the icon                       |
| Disabled | Line      | No pressed state; reason in tooltip and name |

Hover is a background change, not an icon colour change. A hovered icon keeps
its default ink and gains the control plane's hover fill.

An icon-only button that leaves the tab order is not thereby silent. It shows
no pressed state, but it still shows a non-activating explanatory tooltip on
hover, and its accessible name carries the same reason. The reason is the
single applicability reason from the command record, so the tool strip, the
menu and the palette explain the same unavailability in the same words. An icon
is never enabled merely so that its reason can be discovered.

## Icons with labels

An icon may stand alone only when its meaning is in the shared vocabulary and
its tooltip names it. A command that is new, rare or destructive must carry a
text label. The label sits 8 units from the glyph, aligned to the text baseline
on the reading side.

In a tool strip, a labelled button widens to fit the label; it does not shrink
the glyph or truncate the word.

## Mirroring

Each icon declares whether it mirrors in a right-to-left interface. Directional
icons — arrows, playback controls, indentation marks — mirror. Object icons — a
document, a pen, a bitmap — do not. The declaration belongs to the icon's
metadata, not to a global transform, so mirroring the interface never reverses
a glyph that depicts an object. The metadata is part of the icon resource, and
[Localization](38-localization.md) states the direction rules it follows.

## Accessibility

- An icon that carries meaning must have an accessible name.
- A decorative icon beside a text label is hidden from assistive technology.
- An icon button must report its state, not only its name, and must be
  operable with Enter and Space.
- The 28-unit target requirement applies to every icon button, regardless of
  glyph size.

## Testing an icon

Show the glyph at 16 pixels, in monochrome, to a person who has not seen it
before. If they cannot guess its meaning and the tooltip must explain it every
time, the glyph is either wrong or premature. Replace it with a labelled button
until a better drawing exists.
