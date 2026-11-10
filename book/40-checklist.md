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
- [ ] The conformance export produces the full bundle: PDF, print PDF, raster,
      thumbnail, accessibility, clipboard, hit map and manifest. An ordinary
      user export produces only the file the user asked for and its manifest
      entry.
- [ ] The manifest records identities, revisions, presentations and any
      substitutions, and declares which identity fields apply to the scene.
- [ ] A substrate-only scene needs no semantic object identity, revision or
      capability grant to draw or to be accessible.
- [ ] The application survives `en-XA` and `ar-XB`.

## Window and structure

- [ ] Title bar 31, menu bar 29, tool strip 30, status line 26, in logical
      units.
- [ ] The window has one document plane and no decorative gradient.
- [ ] Menus follow File, Edit, View, instrument, Window, Help, omitting any menu
      with no commands.
- [ ] Ellipses mark commands that request further information before acting;
      immediate commands have none.
- [ ] The status line reports something true; it does not say **Ready**.
- [ ] Every window declares its role, activation, modality and attachment
      independently, and its furniture matches the role.
- [ ] Exactly one decoration profile is active, and it names one owner for
      window controls, move and resize gestures and shadows.
- [ ] A window shows at most one title and one set of window controls.
- [ ] A secondary window is a declared role, not an undeclared copy of the
      document plane.

## Layout

- [ ] Spacing uses the 4-unit grid: 4, 8, 12, 16 within a pane and 24, 32,
      48, 64 between structures.
- [ ] Pane padding is 16 units.
- [ ] The navigator is at least 210 units and the inspector at least 240.
- [ ] The document plane is at least 420 units and remains the flexible
      element.
- [ ] No more than two side panes are open beside the document.
- [ ] Splitters are 6 units visible with an 8-unit hit region that does not
      reduce either pane.
- [ ] Panes collapse and restore without losing their state.
- [ ] The window declares a layout profile, a requested width and a feasible
      width, and the compact profile applies below the supported floor.
- [ ] Every component role and variant used is declared in the catalogue, and
      no control invents a height.

## Type and colour

- [ ] Essential interface text is at least 12 units; supplementary metadata is
      11; folios are 10.
- [ ] Body text is 15 or 16 units with 1.6 leading.
- [ ] Display and titles use Georgia italic; interface text uses the humanist
      sans; metadata uses the humanist mono.
- [ ] Body text meets 4.5:1; large text and essential icons meet 3:1.
- [ ] Decorative teal never carries text; the refresh text role is the only
      teal-family colour used for words.
- [ ] Every semantic role resolves in every supported theme, and the dark theme
      meets the same ratios as the light theme.
- [ ] Colour is never the only carrier of a state.
- [ ] Radii do not exceed 2 units.
- [ ] There is at most one offset shadow, with no blur.

## Objects and state

- [ ] Every object has a stable, unique, opaque and copyable identity.
- [ ] Semantic object, presentation definition, presentation instance and scene
      node identities are distinct, and a hit or accessible node names its
      instance.
- [ ] Duplicate, derive and export are distinct operations, with the declared
      shallow or deep closure.
- [ ] Every mutation has an operation identity; retrying it is idempotent and
      does not duplicate effects.
- [ ] An atomic transaction commits all of its effects or none; independent
      batch work and partial import are explicit, separately labelled modes.
- [ ] Embed resolution renders as **Resolved**, **Opaque**, **Unavailable** or
      **Malformed**, and only a resolved embed carries a live state.
- [ ] Resolution, current authority and cached-result availability are treated
      as independent facts; an unresolved embed gains no export right.
- [ ] Live relationships render as **Current**, **Refreshing**, **Stale**,
      **Broken** or **Denied**.
- [ ] Every transition in the state table is witnessed, and no other transition
      occurs.
- [ ] Revocation, expiry and provider loss act from every reachable state
      without an intervening refresh, and a late reply cannot reverse them.
- [ ] A state is visible in the object, the inspector and the status line.
- [ ] A stale object keeps its last good value and says it is stale.
- [ ] A denied object reveals its value or protected metadata in no text,
      tooltip, preview, thumbnail, accessible name, search result, backlink,
      diagnostic or manifest.
- [ ] A mixed-state document reports the most severe child state without
      hiding a less severe one, using the declared precedence.
- [ ] Persistence, draft validity, resolution and relationship freshness are
      separate facts with separate carriers.
- [ ] A presentation edit changes its container, not the source object, and is
      undone in the container's history.
- [ ] Names, identities, revisions, counts, timestamps, source chips,
      backlinks, search results, diagnostics and manifests each obey the
      metadata disclosure policy.
- [ ] A portable bundle carries reconstructable data and never a capability
      grant, host secret or machine-local handle; import reacquires authority.

## Controls and keyboard

- [ ] Every interactive object is reachable by keyboard in a logical order,
      except a disabled control that leaves the tab order with its reason
      reachable elsewhere.
- [ ] The focus ring uses the theme's focus role, 3 units at 3 units offset,
      and keeps the control's allocated border.
- [ ] Focus returns through the focus-return chain: invoker, surviving logical
      context, then a safe fallback.
- [ ] Effective targets are at least 28 units; the splitter, scrollbar and
      other declared exceptions are valid only with their alternatives, and a
      dialog's primary action is 36.
- [ ] Focus toggling changes neither layout bounds nor the command target.
- [ ] Accessible bounds describe the semantic region and are not required to
      equal the hit map.
- [ ] Every icon-only button has an accessible name.
- [ ] A drag interaction has a keyboard alternative.
- [ ] Every composite declares its input modes, how Tab leaves it and how
      Escape returns to navigation.
- [ ] Enter and Space activate only the focused control in navigation mode;
      text editing and composition take them first.
- [ ] A pressed control responds within one refresh interval, no more than
      16.7 milliseconds at 60 hertz.
- [ ] The command palette opens with Control+K, completes inside its query
      field only, and announces its results.
- [ ] A command record declares one semantic identity across menus, palette,
      toolbar and context menus, with an invocation context captured at
      invocation.

## Feedback and failure

- [ ] An error says what happened, what was preserved and what to do next.
- [ ] A recoverable error is shown inline before it is shown in a dialog.
- [ ] A destructive action names its object and offers Cancel as the default.
- [ ] An operation longer than 200 milliseconds announces itself, and one that
      finishes says so once.
- [ ] A cancel action is acknowledged within 200 milliseconds, suppresses
      publication immediately, and any cleanup continues in a separate
      **Cancelling** state.
- [ ] Timing is measured from the accepted action to the first frame showing
      the new state, and each background operation is bounded by its own
      trigger.
- [ ] Progress is visible and does not block unrelated work.
- [ ] A dialog declares modality, presentation and purpose separately, and a
      sheet does not bypass the purpose's decision rules.
- [ ] A failed export leaves the previous output intact.
- [ ] A partial export is marked as partial.
- [ ] Diagnostics are reachable from Help.

## Output

- [ ] Display, PDF, print, raster, thumbnail, clipboard, accessibility, hit
      map and manifest agree with the scene within the declared tolerances for
      their declared intent, not across unrelated intents.
- [ ] Application chrome, guides, grids and selection handles are excluded from
      document output, while intended state marks remain.
- [ ] Every artefact and its manifest identify one accepted snapshot.
- [ ] The bundle is staged and published as a unit; a failure leaves the
      previous published bundle intact.
- [ ] Text remains text in PDF and in the accessibility tree.
- [ ] Fonts are embedded; a permitted substitution is still embedded where the
      chosen profile requires it, and is recorded in the manifest.
- [ ] A colour outside the target's gamut is reported before export.
- [ ] The hit map describes the same instances that were drawn.
- [ ] A preflight override changes only a waivable policy outcome; it never
      grants authority or makes structurally invalid output conformant.
- [ ] A PDF/X claim is made only by a profile that validates the chosen level.

## Localization and access

- [ ] Every resource key exists in every shipped locale.
- [ ] Both pseudo-locales build and export without clipping or overlap.
- [ ] Panes, menus, icons and focus order mirror for right-to-left locales.
- [ ] Numbers, dates and currency use the locale's formats.
- [ ] The accessibility tree exposes roles, names, states, accessible bounds
      and order.
- [ ] A screen-reader user can complete the primary task.
- [ ] At 200 per cent interface scale, every control is reachable and no
      control or text overlaps; the compact profile applies where needed.
- [ ] Narrowing a pane or enlarging text never shrinks text below the user's
      requested scale.
- [ ] Reduced motion makes finite transitions effectively immediate, keeps
      activity indicators static, and never speeds an infinite animation up.

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
