---
title: Conformance checklist
part: Breadth
summary: The questions a reviewer asks before a Cabochon surface is called ready.
---

# Conformance checklist

This checklist is the short form of the book. It is written for a reviewer with
the application in front of them and the guidelines beside them.

A surface is ready when every **must** holds and every departure from a
**should** is deliberate and recorded. A checked box is a claim that the
reviewer has seen the behaviour, not that the code appears to implement it.

## Contract

- [ ] The application loads menus, labels, icons and shortcuts from
      Escutcheon resources.
- [ ] One Lapidary scene describes the document, its controls and its hit
      regions.
- [ ] The scene is exportable and can be compared with the display.
- [ ] Export produces the full bundle: PDF, print PDF, raster, thumbnail,
      accessibility, clipboard, hit map and manifest.
- [ ] The manifest records identities, revisions, presentations and any
      substitutions.
- [ ] The application survives `en-XA` and `ar-XB`.

## Window and structure

- [ ] Title bar 31, menu bar 29, tool strip 30, status line 26.
- [ ] The window has one document plane and no decorative gradient.
- [ ] Menus follow File, Edit, View, instrument, Window, Help, omitting any menu
      with no commands.
- [ ] Ellipses mark commands that request further information before acting;
      immediate commands have none.
- [ ] The status line reports something true; it does not say **Ready**.
- [ ] Secondary windows are sheets or dialogs, not free-floating copies of the
      main window.

## Layout

- [ ] Spacing uses the 4-pixel grid: 4, 8, 12, 16 within a pane and 24, 32,
      48, 64 between structures.
- [ ] Pane padding is 16 pixels.
- [ ] The navigator is at least 210 pixels and the inspector at least 240.
- [ ] The document plane is at least 420 pixels and remains the flexible
      element.
- [ ] No more than two side panes are open beside the document.
- [ ] Splitters are 6 pixels visible with an 8-pixel hit region.
- [ ] Panes collapse and restore without losing their state.

## Type and colour

- [ ] Interface text is at least 12 pixels; metadata is 11; folios are 10.
- [ ] Body text is 15 or 16 pixels with 1.6 leading.
- [ ] Display and titles use Georgia italic; interface text uses the humanist
      sans; metadata uses the humanist mono.
- [ ] Body text meets 4.5:1; large text and essential icons meet 3:1.
- [ ] Teal is never used for text that carries meaning.
- [ ] The dark theme meets the same contrast ratios as the light theme.
- [ ] Colour is never the only carrier of a state.
- [ ] Radii do not exceed 2 pixels.
- [ ] There is at most one offset shadow, with no blur.

## Objects and state

- [ ] Every object has a stable, unique, opaque and copyable identity.
- [ ] Duplicate, derive and export are distinct operations.
- [ ] Embed resolution renders as **Resolved**, **Opaque**, **Unavailable** or
      **Malformed**, and only a resolved embed carries a live state.
- [ ] Live relationships render as **Current**, **Refreshing**, **Stale**,
      **Broken** or **Denied**.
- [ ] Every transition in the state table is witnessed, and no other transition
      occurs.
- [ ] A state is visible in the object, the inspector and the status line.
- [ ] A stale object keeps its last good value and says it is stale.
- [ ] A denied object reveals its value in no text, tooltip, preview, thumbnail,
      accessibility label or diagnostic.

## Controls and keyboard

- [ ] Every interactive object is reachable by keyboard in a logical order.
- [ ] The focus ring is 3 pixels of oxide at 3 pixels offset.
- [ ] Focus returns to the opener when a dialog closes.
- [ ] Targets are at least 28 pixels; a dialog's primary action is 36.
- [ ] Every icon-only button has an accessible name.
- [ ] A drag interaction has a keyboard alternative.
- [ ] The command palette opens with Control+K and announces its results.

## Feedback and failure

- [ ] An error says what happened, what was preserved and what to do next.
- [ ] A recoverable error is shown inline before it is shown in a dialog.
- [ ] A destructive action names its object and offers Cancel as the default.
- [ ] Progress is visible and does not block unrelated work.
- [ ] A failed export leaves the previous output intact.
- [ ] A partial export is marked as partial.
- [ ] Diagnostics are reachable from Help.

## Output

- [ ] Display, PDF, print, raster, thumbnail, clipboard, accessibility and hit
      map agree within the declared tolerances.
- [ ] Text remains text in PDF and in the accessibility tree.
- [ ] Guides, grids and selection handles never print.
- [ ] Fonts are embedded or a substitution is recorded.
- [ ] A colour outside the target's gamut is reported before export.
- [ ] The hit map describes the objects that were drawn.

## Localization and access

- [ ] Every resource key exists in every shipped locale.
- [ ] Both pseudo-locales build and export without clipping or overlap.
- [ ] Panes, menus, icons and focus order mirror for right-to-left locales.
- [ ] Numbers, dates and currency use the locale's formats.
- [ ] The accessibility tree exposes roles, names, states, bounds and order.
- [ ] A screen-reader user can complete the primary task.
- [ ] The interface remains usable at 200 per cent zoom.
- [ ] Reduced motion collapses animation to 0.01 milliseconds.

## Documentation and review

- [ ] The application's window, menus and shortcuts match the book or record
      an approved departure.
- [ ] A figure that contradicts the book has been corrected in the generator.
- [ ] The export bundle and its manifest are attached to the review.
- [ ] The reviewer has read the proof sheet and the application at 100 and 200
      per cent zoom.

## Sign-off

A reviewer records:

- the build and scene versions;
- the locales tested;
- the export targets tested;
- every departure from a **should**, with its reason;
- every **must** that does not hold, which blocks sign-off.

A checklist with an unexplained failure is not a pass. The purpose of the list
is to make the decision visible, not to produce a green tick.
