---
title: Spacing and metrics
part: Visual language
figure: fig-09-spacing.svg
summary: The logical unit, the four-unit grid, layout budgets and the target sizes beneath every control.
---

# Spacing and metrics

![Spacing scale and measured tool strip.](../figures/fig-09-spacing.svg)

Cabochon measures in a four-unit grid. The grid keeps unrelated instruments in
rhythm and makes a layout review a matter of arithmetic rather than taste.

## The logical unit

The book measures interface geometry in **logical units** (lu). One logical
unit is one device-independent interface unit. At the baseline profile it maps
to one physical pixel at 96 dots per inch and 100 per cent interface scale. The
baseline exists for arithmetic; it is not a claim about a particular display.

Five scales compose, and they are named separately.

| Scale           | What it changes                             | Who owns it              |
| --------------- | ------------------------------------------- | ------------------------ |
| Device scale    | logical units to physical pixels            | the host and the display |
| Interface scale | chrome, spacing and pointer targets         | the user's UI scale      |
| Text scale      | type size and line height                   | the user's font scale    |
| Document zoom   | the document plane's projection             | the instrument's view    |
| Sample scale    | raster resolution and bitmap sample mapping | the export or the object |

The rules that follow from the distinction are binding.

- Interface geometry in this book is expressed in logical units. A rule that
  says 28 units means 28 logical units before device scale, not 28 physical
  pixels on every display.
- Interface scale multiplies chrome, spacing and target minima. It does not
  change a document's physical size.
- Text scale multiplies type size and line height. It never reduces a target
  below its minimum; the control grows or the layout reflows.
- Document zoom multiplies document-space geometry inside the document plane.
  It never changes chrome, target minima or hit slop.
- Raster sampling is an output transform. A thumbnail or a bitmap's stored
  samples are not an interface scale.
- A bitmap at 100 per cent document zoom maps one stored sample to one logical
  unit at the current interface scale. That is the sample-exact mapping; every
  other zoom uses the declared filtered or nearest-neighbour sampling in
  [Bitmaps](29-bitmaps.md).
- Parity tolerances in [Output parity](37-output-parity.md) are logical units
  converted through the declared transforms, never hard-coded device pixels.

A figure caption or an older note that says "pixel" means the baseline logical
unit. Normative prose uses the logical unit.

## The scale

| Step | Use                                                           |
| ---- | ------------------------------------------------------------- |
| 4    | Hairline breathing room                                       |
| 8    | Icon-to-label gap, gap between related controls, chip padding |
| 12   | Gap between groups inside a pane                              |
| 16   | Pane padding, standard block gap                              |
| 24   | Separation between sections                                   |
| 32   | Separation between major regions                              |
| 48   | Page margin in a document plane                               |
| 64   | Outer margin in a studio or presentation surface              |

Use 4, 8, 12 and 16 for rhythm inside a pane; use 24, 32, 48 and 64 for
structure between regions. A value outside the scale is a defect unless it is a
measured component dimension, such as a 26-unit status line.

## Pane padding

Every pane uses 16 units of padding on all sides. A pane head adds its own
28-unit band above the content and aligns its title with the same 16-unit
inset. A list row may reduce its horizontal padding to 12 units when it carries
a leading icon, but the inset from the pane edge remains 12 or 16, never 10.

## Box model

A layout review is only arithmetic when the box model is stated.

- A pane's declared width includes its padding and its border. A 240-unit
  inspector is 240 units from its leading edge to its trailing edge.
- A splitter occupies its own 6-unit column between panes. Its 8-unit hit
  region extends one unit into each neighbour; that extension is hit-only and
  does not reduce either pane's layout width.
- Horizontal bands are separate rows. A one-unit rule between two regions
  belongs to neither region's height.
- A collapsed pane keeps its head and a 42-unit handle. The handle replaces the
  pane's width; it is not added to it.
- Overlays, focus decorations and hit slop are outside layout. They never
  change the space a control occupies.

## Component roles and variants

Shared dimensions are role minimums and defaults, not a single frozen number
for every instrument.

| Role or variant    | Minimum   | Default | Inherits                     |
| ------------------ | --------- | ------- | ---------------------------- |
| Masthead           | —         | 44      | studio surfaces only         |
| Title bar          | 31        | 31      | window role                  |
| Menu bar           | 29        | 29      | window role                  |
| Tool strip         | 30        | 30      | one row, never two           |
| Tool button        | 28        | 30      | tool-strip target rules      |
| Studio tool button | 28        | 32      | tool button, larger glyph    |
| Window control     | 28        | 28      | 16-unit glyph                |
| Pane head          | 28        | 28      | pane role                    |
| Tree and list row  | 28        | 28      | composite row geometry       |
| Formula bar        | 34        | 34      | document instruments         |
| Status line        | 26        | 26      | 28 when it carries an action |
| Navigator          | 210       | 210     | three-pane document window   |
| Page navigator     | 150       | 150     | navigator, page instruments  |
| Notes tree         | 210       | 210     | navigator                    |
| Project tree       | 210       | 260     | navigator, identity metadata |
| Rail               | 126       | 126     | persistent category list     |
| Inspector          | 240       | 240     | three-pane document window   |
| Relations panel    | 220       | 220     | inspector, link lists        |
| Identity panel     | 240       | 280     | inspector, identity metadata |
| Splitter           | 6 visible | 8 hit   | layout column                |
| Selection handle   | 8 visible | 8       | expanded hit region          |
| Dialog button      | 32        | 36      | primary action 36            |

A variant is a declared role with its own default, not a local escape hatch. It
inherits the row, selection, collapse and target behaviour of the role it
names. An instrument may not redefine a shared value; it may declare a variant
here before using it.

The primary-action floor is 36 units everywhere, in a dialog or not. A labelled
toolbar button keeps the 30-unit height and widens to fit its label; it never
shrinks the glyph or truncates the word.

## Targets

The target is the region that accepts a pointer, not the glyph drawn inside it.

| Target         | Minimum | Preferred | Primary |
| -------------- | ------- | --------- | ------- |
| Any control    | 28 lu   | 32 lu     | 36 lu   |
| Tool strip     | 28 lu   | 30 lu     | —       |
| Menu item      | 28 lu   | 30 lu     | —       |
| Window control | 28 lu   | 28 lu     | —       |
| Dialog action  | 32 lu   | 36 lu     | 36 lu   |

A 16-unit icon may sit inside a 28-unit target; the target is the contract. Hit
slop may extend 4 units beyond a drawn glyph, but it must not overlap a
neighbouring target.

### Glyph, control, hit region and clipping

Four rectangles are distinct, and a test must name the one it measures.

- The **glyph** is what is drawn.
- The **visible control** is the drawn surface: fill, border and label.
- The **hit region** is the visible control plus any declared hit slop, before
  clipping.
- The **clipping container** is the nearest ancestor that clips. The **effective
  target** is the hit region that remains after every ancestor's clipping and
  transform.

A target is compliant when its effective target meets the applicable minimum. A
tall thin rectangle does not satisfy a square minimum by area, and a target
does not become compliant before its parent clips it.

Compact components declare their strategy rather than an unstated exception.

- **Scrollbar.** The track is 12 units wide. Its hit region is the full track,
  and its effective target is a continuous drag surface whose length is the
  pane's height. It is a declared essential-geometry exception, valid only
  because a wheel, keyboard and drag-anywhere alternative is always available.
- **Selection and path handles.** The visible mark is 8 units. Its hit region
  expands to 20 units within the object's bounds, and overlapping handles are
  resolved by the priority order and modifier or keyboard alternative declared
  in [Selection and tools](24-selection-tools.md).
- **Slider thumb.** The visible thumb is 8 units. Its effective target is
  28 units around the thumb, clipped to the slider's container.
- **Swatches.** A 24-unit swatch has a 28-unit effective target and a 4-unit
  gap from its neighbours.
- **Status-line actions.** An action region is 28 units high. A status line that
  carries an action grows to 28 units; otherwise it is 26. A cancel action is
  never clipped to the 26-unit band.

## Target spacing

Spacing applies between independent controls. Composite widgets are exempt
because their internal selection geometry is not a set of independent targets.

- Independent controls keep at least 8 units between their effective targets,
  and groups are separated by 12 or 16 units.
- A menu, tree, grid, tab bar or canvas declares its own internal geometry:
  contiguous rows or cells, a deterministic owner at every shared boundary, and
  a keyboard route to every internal target.
- The boundary between two adjacent grid cells or menu items belongs to exactly
  one target. The rule is declared, not left to hit-test order.
- Changing a row height or a spacing token must not silently invalidate either
  contract. The composite contract is tested against its own declaration, and
  the independent-control contract against the 8-unit rule.

An external group of controls placed inside a dense pane still satisfies the
independent-control rule. The dense rows inside a table do not, because they
are one composite.

## Bounds

Five bounds are named so that focus, hit-testing and accessibility do not
accidentally demand equality.

| Bound                   | Definition                                                     |
| ----------------------- | -------------------------------------------------------------- |
| Layout bounds           | The space the control occupies, including its allocated border |
| Visual bounds           | The painted surface, including a border if one is drawn        |
| Focus-decoration bounds | The ring and offset, drawn outside layout and never clipped    |
| Effective hit region    | The hit region after ancestor clipping and transform           |
| Accessible bounds       | The chosen semantic region after the same transform            |

Focus toggling changes none of layout, visual, hit or accessible bounds. A
control allocates its border in every state; focus adds a decoration outside
it. The accessibility adapter reports the accessible bounds of the semantic
region it exposes, and that region need not equal the hit region: a merged
group, a virtualised row or an expanded target legitimately differs. The test
compares each bound with its own contract, never one with another.

## Density

Density is a property of the pane, not an excuse to shrink the target. A dense
table may use 28-unit rows and 12-unit operational text; it may not use 20-unit
rows or 9-unit labels. Where an instrument needs to show more, it should use a
larger window, a collapsible pane or a zoom control.

## Layout profiles

A layout budget is derived from the components actually present. Three profiles
are declared.

- **Document.** Title bar, menu bar, optional tool strip and status line.
- **Studio.** Masthead, title bar, menu bar, tool strip and status line.
- **Page.** The studio profile applied to a page instrument, with a page
  navigator and a preflight pane.

The band totals follow from the table, not from a remembered number.

| Profile            | Bands                  | Total |
| ------------------ | ---------------------- | ----- |
| Document, no strip | 31 + 29 + 26           | 86    |
| Document           | 31 + 29 + 30 + 26      | 116   |
| Studio, no strip   | 44 + 31 + 29 + 26      | 130   |
| Studio             | 44 + 31 + 29 + 30 + 26 | 160   |

The studio figure of 130 units is the four bands without a tool strip. Adding a
tool strip adds exactly 30 units, and removing the masthead removes exactly 44.

A vertical budget is the sum of the bands present plus the document plane's
minimum height of 320 units. A horizontal budget is the document minimum or the
sum of the expanded panes and splitter columns, whichever is greater.

| Configuration                    | Width                         |
| -------------------------------- | ----------------------------- |
| Navigator + document + inspector | 210 + 6 + 420 + 6 + 240 = 882 |
| Inspector collapsed              | 210 + 6 + 420 + 6 + 42 = 684  |
| Both side panes collapsed        | 42 + 6 + 420 + 6 + 42 = 516   |

At the default 1280 by 800 window with both side panes and the studio bands,
the document plane is 914 by 640 units before any optional tool strip, about 57
per cent of the window. The binding test is that the document plane remains the
largest region and at least 420 units wide.

### Requested and feasible width

A pane stores two widths: the width the user requested and the width currently
feasible in the window. The displayed width is the requested width clamped to
the interval between the pane's minimum and the space remaining after the other
panes and the document minimum. When the window grows again, the pane returns
to its requested width; it does not inherit the temporary clamp.

### The last-resort configuration

Below the computed minimum, the instrument enters a declared compact profile
rather than clipping a control.

- Both side panes collapse to 28-unit edge strips.
- The tool strip and the masthead are hidden; the menu bar and status line
  remain.
- The document plane keeps a 420-unit width and may scroll horizontally. Prose
  reflows instead of scrolling; a grid, a canvas and a page may scroll.
- The supported logical viewport floor is 512 by 384 units. A narrower or
  shorter window is outside the supported set, and the application must still
  keep every control reachable by scrolling rather than clipping it.

At 200 per cent interface scale a 1024 by 768 physical display provides about
512 by 384 logical units, so the compact profile is the profile that makes the
accessibility requirement feasible. It is not a degraded mode to be avoided; it
is the declared answer.

## Alignment

- Labels align to the text baseline of their control, not to the control's
  vertical centre.
- Icons align to the optical centre of their target. A glyph with a heavy
  top, such as a triangle, sits 1 unit lower than its geometric centre.
- Numbers in a column share a trailing edge.
- Pane heads across a window share a baseline, even when their bands differ in
  height by a unit.

## Window sizes

The minimum window size is computed from the configuration, not stated as one
number. The default window is 1280 by 800. A preferred document plane is at
least 900 by 600 units. A window must remain usable at 1024 by 768, the floor
for the first batch, where the document plane remains at least 420 units wide.

## Checking a layout

A reviewer can check a layout with five measurements: the pane padding, the row
height, the gap between groups, the effective target of the smallest control
and the allocated width of every pane. If those are on scale and the budget
arithmetic closes, the rest of the layout is usually sound. The figure's
measured tool strip shows the method: every dimension is drawn and labelled, so
a disagreement is visible rather than argued.
