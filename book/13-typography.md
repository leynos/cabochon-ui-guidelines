---
title: Typography
part: Visual language
figure: fig-08-type.svg
summary: Three voices, seven sizes and the floors that keep interface text readable.
---

# Typography

![Three typographic voices and a type scale.](../figures/fig-08-type.svg)

Cabochon uses three typographic voices. Display argues, interface explains and
metadata accounts. They do not trade places.

## The three voices

**Display** is Georgia italic, or a compatible serif with a true italic. It
appears in chapter and cover titles, plate marks, pull quotes and the titles of
studio documents. It is never used for controls, labels or running interface
text.

**Interface** is a humanist sans. It carries menus, labels, buttons, pane
heads, dialog text and short prose in panels. The reference figures use DejaVu
Sans. A platform may substitute another humanist sans with similar metrics and
must check the measured values in this chapter against the substitute.

**Metadata** is a humanist mono. It carries object identity, state words,
units, shortcuts, dimensions, timestamps and folios. The reference figures use
DejaVu Sans Mono. Monospace is a signal that a string is exact and copyable,
not a stylistic choice.

## The scale

| Voice     | Size / line height | Face               | Use                       |
| --------- | ------------------ | ------------------ | ------------------------- |
| Display   | 42–96 / 0.95       | Georgia italic     | Chapter and cover titles  |
| Title     | 24–32 / 1.1        | Georgia italic     | Tool and document titles  |
| Section   | 16–20 / 1.2        | Humanist sans bold | Pane and dialog headings  |
| Body      | 15–16 / 1.6        | Georgia or sans    | Notes and long-form prose |
| Interface | 12 / 1.35          | Humanist sans      | Controls, labels, menus   |
| Metadata  | 11 / 1.4           | Humanist mono      | Identity, state, units    |
| Folio     | 10 / 1.2           | Humanist mono      | Folios and plate marks    |

The floors are binding.

- No interface text below 12 pixels.
- Metadata may be 11 pixels only when it is non-essential, such as a
  timestamp or a count that is also available elsewhere.
- 10 pixels is reserved for folios and plate marks, which are not required
  for operation.
- A control's label must never use metadata type merely to fit.

The design book's mockups used 9- and 10-pixel labels to suggest density. At
production size those labels fail both legibility and contrast. The corrected
floors above preserve the density of the layout without shrinking the words.

## Weights and styles

- Interface text uses regular and bold only. A semibold may stand in for bold
  where the family lacks a true bold, but the two must not be mixed within one
  window.
- Display uses italic, with roman reserved for a title that must match a
  document's existing style.
- Underlining is reserved for links and for the access key in a menu label. It
  is not used for emphasis.
- Small capitals and letter-spaced capitals appear only in metadata kickers,
  at 0.06 em to 0.08 em. They are never used for sentences.

## Measure and alignment

- Long-form prose in a document plane should measure 60 to 75 characters per
  line. A notes pane narrower than 45 characters should reduce its type scale
  rather than its margins.
- Interface labels are left-aligned in left-to-right layouts and right-aligned
  in right-to-left layouts. Centred text is reserved for dialogs, empty states
  and short button labels.
- Numbers in tables use tabular figures and are right-aligned. Numbers in
  prose use the family's default figures.
- Hyphenation is permitted in long-form prose and forbidden in interface
  labels, menu items and titles.

## Truncation

Text that does not fit must be handled deliberately.

- Titles truncate in the middle, keeping the beginning and the extension.
- Menu items and button labels must not truncate; the control grows or the
  label shortens.
- Table cells truncate at the end with an ellipsis and reveal the full value
  in a tooltip and in the inspector.
- Metadata strings truncate at the end and remain copyable in full.

## Localization

The type scale must survive translation. A label that grows by 30 per cent must
not break its control; the layout should allow the label to wrap or the control
to grow. Pseudo-localization is part of the release gate, as described in
[Localization](38-localization.md).

## A test for a type choice

For any piece of text, the designer should be able to name its voice and its
row in the scale. A string that belongs to no row is a string that will drift.
The fix is to classify it, not to invent a size.
