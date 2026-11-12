---
title: Palette
part: Visual language
figure: fig-07-palette.svg
summary: Paper, ink, pine, oxide and amber, with the semantic role pairs that govern each theme.
---

# Palette

![The material palette in light and dark.](../figures/fig-07-palette.svg)

Cabochon's palette is small, warm and material. It describes paper, ink,
polished stone and a few signal colours. Nothing in it is decorative: each
colour has a role, and every role has a contrast requirement.

## The light palette

| Token     | Value   | Role                                    |
| --------- | ------- | --------------------------------------- |
| Paper     | #F1EEE5 | Window ground and document surroundings |
| High      | #FAF8F2 | Raised pane, document plane, overlay    |
| Ink       | #17201C | Primary text and keylines               |
| Soft      | #59625D | Secondary text and metadata             |
| Pine      | #173F35 | Window edge, strong structure           |
| Pine 2    | #285E50 | Selection and primary button            |
| Teal      | #678E86 | Decoration and refresh motion only      |
| Teal ink  | #456A62 | Refresh text and small marks            |
| Oxide     | #8A302F | Authority, focus, destructive emphasis  |
| Amber     | #B8792E | Large marks and icons only              |
| Amber ink | #8A5B24 | Stale text at body size                 |
| Line      | #AAA99F | Hairlines and separators                |

## Semantic roles

A role names a job, not a colour. An interface uses roles, and a theme resolves
each role to a value. The light theme resolves them as follows.

| Role               | Light value | Contrast against its ground |
| ------------------ | ----------- | --------------------------- |
| Ground             | #F1EEE5     | —                           |
| Surface            | #FAF8F2     | —                           |
| Control fill       | #E4E3DD     | 1.21 against surface        |
| Overlay            | #FAF8F2     | —                           |
| Text primary       | #17201C     | 14.37 paper, 15.70 surface  |
| Text muted         | #59625D     | 5.44 paper, 5.94 surface    |
| Essential border   | #6E6A5E     | 4.66 paper, 5.09 surface    |
| Decorative line    | #AAA99F     | 2.04 paper, 2.23 surface    |
| Selected fill      | #285E50     | —                           |
| Selected text      | #FFFFFF     | 7.48 on selected fill       |
| Row fill           | #FAF8F2     | —                           |
| Alternate row fill | #FFFFFF     | —                           |
| Inactive selection | #285E50     | outline, with text primary  |
| Primary fill       | #285E50     | —                           |
| Primary text       | #FFFFFF     | 7.48 on primary fill        |
| Destructive fill   | #8A302F     | —                           |
| Destructive text   | #FFFFFF     | 8.25 on destructive fill    |
| Focus              | #8A302F     | 7.11 paper, 6.42 control    |
| Refresh mark       | #678E86     | 3.13 paper, non-text only   |
| Refresh text       | #456A62     | 5.19 paper, 5.66 surface    |
| Stale mark         | #B8792E     | 3.11 paper, non-text only   |
| Stale text         | #8A5B24     | 5.02 paper, 5.49 surface    |
| Denied and broken  | #8A302F     | 7.11 paper, 7.77 surface    |
| Disabled fill      | #E4E3DD     | —                           |
| Disabled text      | #59625D     | exempt from text contrast   |

The rules that follow from the table are absolute.

- Teal is a wash, a rule or a moving indicator. It never carries text. Teal ink
  carries refresh text and small marks.
- Amber is a large mark, an icon or a rule. It never carries text at any size.
  Amber ink carries stale text at body size.
- Line is a decorative separator. It never identifies a control, a field or a
  state on its own. The essential border role does that job.
- No colour may be the only carrier of meaning. Every state also has a word,
  a shape or a position.

## Contrast

Contrast is measured against the two light grounds, paper and high. The
following ratios are the production reference.

| Colour    | On paper | On high | Permitted use                         |
| --------- | -------- | ------- | ------------------------------------- |
| Ink       | 14.37    | 15.70   | Any text and keyline                  |
| Soft      | 5.44     | 5.94    | Secondary text at 12 units and above  |
| Pine      | 10.06    | 10.99   | Text and structure                    |
| Pine 2    | 6.45     | 7.04    | Text on high; selection fills         |
| Teal      | 3.13     | 3.42    | Decoration and motion, never text     |
| Teal ink  | 5.19     | 5.66    | Text and small marks                  |
| Oxide     | 7.11     | 7.77    | Text, focus ring, destructive accents |
| Amber     | 3.11     | 3.40    | Marks, icons and rules only           |
| Amber ink | 5.02     | 5.49    | Body-size stale text                  |
| Line      | 2.04     | 2.23    | Hairlines, never text                 |

Two further combinations are permitted: ink on amber at 4.61 and ink on line at
7.05. Both are used for compact labels on filled marks, and neither may be
inverted.

Amber's 3.11 ratio does not qualify it for text. WCAG's large-text exception is
defined in points, not in logical units: 18 points, or 14 points bold. An
18-unit label is not large text. Amber therefore carries no text, and amber ink
carries the same meaning at every size.

## Selection

Selection is one idea with three representations, because the thing selected
differs. The vocabulary is fixed; the representation follows the object.

| Selected thing | Representation                                     |
| -------------- | -------------------------------------------------- |
| Text           | The system text-selection colour behind the glyphs |
| Cell or row    | Selected fill with selected text                   |
| Canvas object  | A non-destructive outline and handles              |

A selected row in a tree and a selected cell in a table use the selected fill
with selected text. A selected canvas object is marked by an outline and
handles in interface space, as [Selection and tools](24-selection-tools.md)
specifies; selection never changes the object's own fill, stroke or colour. The
outline is interaction decoration, not saved appearance, so it is absent from
every export.

A secondary selection, such as an inactive pane's remembered selection, uses
the inactive-selection role: an outline with a text-primary label. It must
remain visible without competing with the active selection. The outline is the
inactive-selection role; it is never a tint, and it is never the active fill at
reduced opacity. There is no second policy for this state.

## Focus

The focus ring is oxide, 3 units wide, offset 3 units from the control's edge.
Oxide is strong enough to be seen on every light ground and distinct from
selection. The ring must never be omitted for pointer users: a control that is
focused by any means wears the ring.

The ring is evaluated against the surfaces actually adjacent to it, not against
the control's fill alone. Where the ring crosses from a control onto a pane of
similar luminance, it carries a one-unit inner keyline in the ground role so
that the indicator remains visible on both sides. The dark theme resolves focus
to its own value; a light-theme hex literal is never reused on a dark surface.

## Dark theme

The dark theme is a translation, not an inversion. It resolves the same roles.

| Role               | Dark value | Contrast against its ground |
| ------------------ | ---------- | --------------------------- |
| Ground             | #121816    | —                           |
| Surface            | #1B2420    | —                           |
| Control fill       | #26312C    | 1.18 against surface        |
| Overlay            | #1B2420    | —                           |
| Text primary       | #EDE9DE    | 14.82 ground, 13.12 surface |
| Text muted         | #A9B1AB    | 8.19 ground, 7.25 surface   |
| Essential border   | #74847B    | 4.56 ground, 4.04 surface   |
| Decorative line    | #3A453F    | 1.59 surface, non-text only |
| Selected fill      | #7FB3A3    | —                           |
| Selected text      | #121816    | 7.60 on selected fill       |
| Row fill           | #1B2420    | —                           |
| Alternate row fill | #202A25    | —                           |
| Inactive selection | #7FB3A3    | outline, with text primary  |
| Primary fill       | #7FB3A3    | —                           |
| Primary text       | #121816    | 7.60 on primary fill        |
| Destructive fill   | #D98C86    | —                           |
| Destructive text   | #121816    | 6.89 on destructive fill    |
| Focus              | #E0B36A    | 9.27 ground, 8.20 surface   |
| Refresh mark       | #6FA79C    | 5.82 surface, non-text only |
| Refresh text       | #8FC4B8    | 8.15 surface                |
| Stale mark         | #E0B36A    | 8.20 surface, non-text only |
| Stale text         | #E0B36A    | 8.20 surface                |
| Denied and broken  | #D98C86    | 6.10 surface                |
| Disabled fill      | #26312C    | —                           |
| Disabled text      | #6E7A73    | exempt from text contrast   |

The dark theme keeps the same roles and the same restraint. It does not
introduce new hues, and it does not use pure black or pure white. Contrast must
meet the same thresholds; a colour that passes on paper does not automatically
pass on the dark ground.

A role that has no dark value is a defect, not an invitation to reuse the light
value. The dark keyline is deliberately faint because it is decorative; the
essential border is a separate role with its own value.

## Tints and washes

A tint is a colour at low opacity over paper or high. Cabochon permits three.

- Oxide at 6 per cent for an error region behind a message.
- Amber at 8 per cent for a stale region.
- Teal at 8 per cent for a refreshing region.

An inactive selection is an outline, not a tint, so no tint is declared for it.

A tint must never be the only indication of a state, and a tinted region must
still meet text contrast against its own background. Contrast is computed for
the composited pair, not for the accent in isolation.

## Scope of the palette

The palette governs four scopes, and a rule states which one it addresses.

- **Cabochon chrome.** Window frames, panes, controls, menus, status lines and
  overlays. The closed role set in this chapter applies without exception.
- **Cabochon-authored document furniture.** Rulers, guides, selection handles,
  grid lines and other aids the environment draws over a document. These use
  interface roles, are drawn in interface space and never print.
- **User-authored content.** A document's own colours, a diagram's declared
  theme and a bitmap's samples. These are preserved within the target's gamut
  and are not coerced into an interface role.
- **Editorial artwork.** The book's own cover and illustrative figures. These
  are not production interface examples and are labelled as such where they
  appear.

An interface role is never used to recolour authored content, and a content
colour never becomes a state signal. A rule that does not name its scope is a
chrome rule by default.

## Choosing a new colour

The palette is closed for the first batch. An instrument that believes it needs
another colour should first check whether it needs another *role*. If it
genuinely does, the role, its light and dark values and its contrast ratios
belong in this chapter and in the generator before the colour appears in an
interface.
