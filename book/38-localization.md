---
title: Localization
part: Breadth
figure: fig-31-localization.svg
summary: Pseudo-locales as a gate, resources as complete sentences and direction as a layout property.
---

# Localization

![Pseudo-localized left-to-right and right-to-left windows.](../figures/fig-31-localization.svg)

Localization is not a coat applied after the interface is finished. An
interface that only works in English is an interface with untested layout,
untranslated resources and unexamined assumptions about direction.

Cabochon treats localization as a gate, run with the same rigour as contrast
and output parity.

## The two pseudo-locales

Every application ships with two pseudo-locale builds.

- **`en-XA`** expands every string with accented characters and pads it by at
  least 35 per cent. It reveals clipped labels, fixed-width buttons and
  single-line fields that cannot grow.
- **`ar-XB`** mirrors the layout right-to-left and substitutes right-to-left
  text. It reveals panes, icons, reading order and hit regions that assume
  left-to-right.

Both builds run the full export bundle. A screenshot of the main window is not
a localization test.

## Resources

- Every user-visible string is a resource keyed by meaning, not by its English
  text.
- A resource is a complete sentence or a complete label, never a fragment that
  is concatenated at run time.
- Placeholders are named and typed, and a translation may reorder them.
- Plural forms use the locale's plural rules, not an `if` on the count.
- Accelerator keys are declared separately from the label, so that a
  translation can choose a different letter.
- A missing resource is a build failure, not a fallback to English.

The last rule matters. A silent fallback hides untranslated surfaces until a
user finds them. A missing key must fail the pseudo-locale gate.

## Expansion and layout

Text grows when it is translated. The layout must absorb the growth.

- Menu items and button labels do not truncate; the control grows or the label
  wraps. Table cells and metadata truncate at the end with an ellipsis and a
  tooltip. No label may overlap its neighbour.
- Buttons and fields have a minimum size, not a fixed size derived from
  English text.
- A menu bar that cannot fit its menus moves whole menus into **More**. A tool
  strip that cannot fit its commands moves a whole group into its overflow
  menu. Neither shrinks a target below 28 units.
- A dialog that grows beyond the window reflows or scrolls; it does not clip.
  Its title and its action row stay fixed, and its body scrolls. A button row
  that no longer fits wraps onto a second row rather than shrinking its
  buttons. A dialog never grows wider than the window's feasible width, and it
  never hides its primary action below the fold.
- A status line may shorten its message but must keep its state and its
  object count.

The 35 per cent expansion is a floor, not a target. German and Finnish often
exceed it; the pseudo-locale is designed to fail early.

## Direction

Direction is a property of the interface, not of each widget.

- Panes mirror: the navigator moves to the right, the inspector to the left.
- Menu bars mirror, and menu items align to the reading edge.
- Icons that depict direction, such as arrows and playback controls, mirror.
  Icons that depict objects, such as a document or a pen, do not.
- Text alignment follows the direction of the text, which may differ from the
  direction of the interface.
- Hit regions and focus order mirror with the layout.
- Scrollbars move to the reading edge's far side.
- Position is described with leading and trailing edges, not left and right,
  except where a rule is deliberately absolute.

A document's content keeps its own direction. An Arabic note inside an English
interface is right-to-left; an English quotation inside an Arabic interface is
left-to-right. The interface direction is the frame, not a claim about every
string.

## Numbers, dates and units

Values are formatted by locale, never assembled from pieces.

- Numbers use the locale's grouping and decimal separators.
- Dates use a named format such as a short date, not a hand-built pattern.
- Currency uses the currency's own minor units and the locale's placement.
- Units are converted only when the user asks; the stored value keeps its
  unit.
- Sorting uses the locale's collation for text and numeric order for numbers.
- A right-to-left locale may still use Western digits where that is the
  locale's convention. The locale decides.

## Fonts

- The interface font stack includes a humanist sans with broad coverage and a
  fallback chain.
- A missing glyph is reported in the pseudo-locale gate rather than displayed
  as a blank box in production.
- Metadata and interface text may use different fonts, but both must cover the
  shipped locales.
- A translated string must not change the type scale or the line height.

## Testing

A localization gate passes when:

- every resource key exists in every shipped locale;
- both pseudo-locales build and export without clipping or overlap;
- the focus order and hit regions match the mirrored layout;
- dates, numbers and currency render in the locale's format;
- the accessibility tree exposes translated names, not resource keys;
- no string is concatenated from fragments.

The gate runs in continuous integration and produces a report naming the
window, the widget and the overflowing string. A screenshot is evidence, not
the gate.

## What localization is not

- Translating the menus and leaving the dialogs in English.
- Reversing the layout without reversing the reading order.
- Assuming that a longer string can be truncated silently.
- Treating a locale as a language. A locale includes direction, collation,
  formats and conventions.
