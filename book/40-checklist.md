---
title: Conformance checklist
part: Breadth
summary: A scoped projection of the book's requirements, with stable identifiers and owning rules.
---

# Conformance checklist

This checklist is a projection of the book's normative rules, not a second
specification. Each item carries a stable identifier and names the rule that
owns it. The item inherits that rule's force, exceptions and conformance
profile, and it adds no behaviour of its own.

- An item is **applicable** when its owning rule's predicate is true for the
  surface under review.
- An item is **not applicable** only when that predicate is false, and the
  reviewer records the reason. A false predicate is not a waiver.
- A **must** item that does not hold blocks sign-off. A **should** item may be
  departed from only with a recorded reason.
- Changing a rule's wording does not change its identifier. Changing its
  meaning requires a new identifier and a review of every item that cites it.

A surface is ready when every applicable **must** holds and every departure
from an applicable **should** is deliberate and recorded. A checked box is a
claim that the reviewer has seen the behaviour, not that the code appears to
implement it.

The machine-readable form of this projection is `tools/requirements.json`. Each
record names the identifier, the owning file and heading anchor, the force, the
conformance profile, the predicate under which the requirement applies and at
least one evidence route. The checklist item is a view of that record, not a
second definition. `make requirements` proves that the two sets agree, that
every owner and anchor exists and that every requirement has an evidence route.
Removing a checklist entry therefore fails coverage rather than silently
shrinking the checklist.

## Contract

- [ ] **CON-01** — The application loads menus, labels, icons and shortcuts
      from Escutcheon resources. Owner: [Ecosystem map](03-ecosystem-map.md#the-substrate-components).
- [ ] **CON-02** — One Lapidary scene describes the document, its controls and
      its hit regions. Owner: [Ecosystem map](03-ecosystem-map.md#the-substrate-components).
- [ ] **CON-03** — The scene is exportable and can be compared with the
      display. Owner: [Output parity](37-output-parity.md#targets-artefacts-and-encodings).
- [ ] **CON-04** — A conformance export produces the full bundle: PDF, print
      PDF, raster, thumbnail, accessibility, clipboard, hit map and manifest.
      An ordinary user export produces only the file the user asked for and
      its manifest entry. Owner: [Output parity](37-output-parity.md#targets-artefacts-and-encodings).
- [ ] **CON-05** — The manifest records identities, revisions, presentations
      and any substitutions, and declares which identity fields apply to the
      scene. Owner: [Output parity](37-output-parity.md#the-manifest).
- [ ] **CON-06** — A substrate-only scene needs no semantic object identity,
      revision or capability grant to draw or to be accessible. Owner:
      [Hello window](36-hello-window.md#identity-in-a-substrate-only-scene).
- [ ] **CON-07** — The application survives `en-XA` and `ar-XB`. Owner:
      [Localization](38-localization.md#the-two-pseudo-locales).

## Window and structure

- [ ] **WIN-01** — When a title bar, menu bar, tool strip or status line is
      present, it uses its declared band height: 31, 29, 30 and 26 logical
      units respectively. A band is a baseline height and grows with its
      content. Owner: [Windows](09-windows.md#the-bands), [Spacing and metrics](14-spacing-metrics.md).
- [ ] **WIN-02** — The window has one document plane and no decorative
      gradient. Owner: [The document at the centre](06-document-centre.md#the-document-plane).
- [ ] **WIN-03** — Menus follow File, Edit, View, instrument, Window, Help,
      omitting any menu with no commands. Owner: [Menus](10-menus.md#order).
- [ ] **WIN-04** — Ellipses mark commands that request further information
      before acting; immediate commands have none. Owner: [Menus](10-menus.md#wording).
- [ ] **WIN-05** — The status line reports something true; it does not say
      **Ready**. Owner: [Toolbars and status](11-toolbars-status.md#the-status-line).
- [ ] **WIN-06** — Every window declares its role, activation, modality and
      attachment independently, and its furniture matches the role. Owner:
      [Windows](09-windows.md#four-independent-properties).
- [ ] **WIN-07** — Exactly one decoration profile is active, and it names one
      owner for window controls, move and resize gestures and shadows. Owner:
      [Windows](09-windows.md#decoration-profiles).
- [ ] **WIN-08** — A window shows at most one title and one set of window
      controls. Owner: [Windows](09-windows.md#decoration-profiles).
- [ ] **WIN-09** — A secondary window is a declared role, not an undeclared
      copy of the document plane. Owner: [Windows](09-windows.md#permitted-window-roles).
- [ ] **WIN-10** — A status line's zones follow the owning layout: progress
      occupies the zone that layout assigns it, and the line does not restate
      a different placement. Owner: [Toolbars and status](11-toolbars-status.md#the-status-line).

## Layout

- [ ] **LAY-01** — Spacing uses the 4-unit grid: 4, 8, 12, 16 within a pane
      and 24, 32, 48, 64 between structures. Owner:
      [Spacing and metrics](14-spacing-metrics.md#the-scale).
- [ ] **LAY-02** — Pane padding is 16 units. Owner:
      [Spacing and metrics](14-spacing-metrics.md#pane-padding).
- [ ] **LAY-03** — The navigator is at least 210 units and the inspector at
      least 240, unless a declared variant states a different default. Owner:
      [Panes](20-panes.md#the-three-pane-window).
- [ ] **LAY-04** — The document plane is at least 420 units and remains the
      flexible element. Owner: [Panes](20-panes.md#the-three-pane-window).
- [ ] **LAY-05** — No more than two side panes are open beside the document.
      Owner: [Panes](20-panes.md#the-three-pane-window).
- [ ] **LAY-06** — Splitters are 6 units visible with an 8-unit hit region
      that does not reduce either pane. Owner: [Panes](20-panes.md#splitters).
- [ ] **LAY-07** — Panes collapse and restore without losing their state.
      Owner: [Panes](20-panes.md#collapse-and-restore).
- [ ] **LAY-08** — The window declares a layout profile, a requested width and
      a feasible width. The compact profile applies at or above the supported
      floor when the expanded layout cannot fit; below the floor the
      application still keeps every control reachable by scrolling. Owner:
      [Spacing and metrics](14-spacing-metrics.md#layout-profiles).
- [ ] **LAY-09** — Every component role and variant used is declared in the
      catalogue, and no control invents a height. Owner:
      [Spacing and metrics](14-spacing-metrics.md#component-roles-and-variants).
- [ ] **LAY-10** — A splitter's resize cursor and arrow axis follow its
      orientation. Owner: [Panes](20-panes.md#splitters).

## Type and colour

- [ ] **TYP-01** — Essential interface text is at least 12 units;
      non-essential supplementary metadata is 11; folios are 10. Owner:
      [Typography](13-typography.md#the-scale).
- [ ] **TYP-02** — Body text is 15 or 16 units with 1.6 leading. Owner:
      [Typography](13-typography.md#the-scale).
- [ ] **TYP-03** — Display and titles use Georgia italic; interface text uses
      the humanist sans; metadata uses the humanist mono. Owner:
      [Typography](13-typography.md#the-three-voices).
- [ ] **TYP-04** — Body text meets 4.5:1; large text and essential icons meet
      3:1. Legibility and contrast are separate tests. Owner:
      [Palette](12-palette.md#contrast), [Typography](13-typography.md).
- [ ] **TYP-05** — Decorative teal never carries text; the refresh text role
      is the only teal-family colour used for words. Owner:
      [Palette](12-palette.md#semantic-roles).
- [ ] **TYP-06** — Every semantic role resolves in every supported theme, and
      the dark theme meets the same ratios as the light theme. Owner:
      [Palette](12-palette.md#dark-theme).
- [ ] **TYP-07** — Colour is never the only carrier of a state. Owner:
      [Palette](12-palette.md#semantic-roles).
- [ ] **TYP-08** — Radii do not exceed 2 units on chrome. Owner:
      [Planes and borders](15-planes-borders.md#radii).
- [ ] **TYP-09** — Each application-owned overlay casts at most one offset
      shadow, with no blur; a host-decorated window's shadow belongs to the
      host, and a page-proof surface is the declared physical-page exception.
      Owner: [Planes and borders](15-planes-borders.md#shadow).
- [ ] **TYP-10** — Interface style governs chrome and Cabochon-authored
      furniture; user-authored content and editorial artwork keep their own
      appearance. Owner: [Palette](12-palette.md#scope-of-the-palette).

## Objects and state

- [ ] **OBJ-01** — Every object has a stable, unique, opaque and copyable
      identity. Owner: [Object identity](07-object-identity.md#what-identity-means).
- [ ] **OBJ-02** — Semantic object, presentation definition, presentation
      instance and scene node identities are distinct, and a hit or accessible
      node names its instance. Owner: [Object identity](07-object-identity.md#presentation-identity).
- [ ] **OBJ-03** — Duplicate, derive and export are distinct operations, with
      the declared shallow or deep closure. Owner:
      [Object identity](07-object-identity.md#duplicate-derive-export).
- [ ] **OBJ-04** — Every mutation has an operation identity; retrying it is
      idempotent and does not duplicate effects. Owner:
      [Errors and recovery](25-errors-recovery.md#retry-and-recovery).
- [ ] **OBJ-05** — An atomic transaction commits all of its effects or none;
      independent batch work and partial import are explicit, separately
      labelled modes. Owner:
      [Errors and recovery](25-errors-recovery.md#atomic-operations-batches-and-partial-failure).
- [ ] **OBJ-06** — Embed resolution renders as **Resolved**, **Opaque**,
      **Unavailable** or **Malformed**, and only a resolved embed carries a
      live state. Owner: [Embeds](32-embeds.md#resolution-authority-and-cache-are-independent).
- [ ] **OBJ-07** — Resolution, current authority and cached-result
      availability are treated as independent facts; an unresolved embed
      gains no export right. Owner: [Embeds](32-embeds.md#resolution-authority-and-cache-are-independent).
- [ ] **OBJ-08** — Live relationships render as **Current**, **Refreshing**,
      **Stale**, **Broken** or **Denied**. Owner:
      [Live relationships](08-live-relationships.md#the-five-states).
- [ ] **OBJ-09** — Every transition in the state table is witnessed, and no
      other transition occurs. Owner:
      [Live relationships](08-live-relationships.md#transitions).
- [ ] **OBJ-10** — Revocation, expiry and provider loss act from every
      reachable state without an intervening refresh, and a late reply cannot
      reverse them. Owner: [Live relationships](08-live-relationships.md#authority-and-availability-are-events-in-their-own-right).
- [ ] **OBJ-11** — A state is visible in the object, the inspector and the
      status line. Owner: [Live relationships](08-live-relationships.md#the-five-states).
- [ ] **OBJ-12** — A stale object keeps its last good value and says it is
      stale. Owner: [Live relationships](08-live-relationships.md#stale).
- [ ] **OBJ-13** — A denied object reveals its value or protected metadata in
      no text, tooltip, preview, thumbnail, accessible name, search result,
      backlink, diagnostic or manifest. Owner:
      [Live relationships](08-live-relationships.md#broken-and-denied).
- [ ] **OBJ-14** — A mixed-state summary protects the most severe child state;
      a milder summary may not replace or hide it, and a less severe state is
      omitted only when the declared precedence permits. Owner:
      [Live relationships](08-live-relationships.md#aggregating-child-states).
- [ ] **OBJ-15** — Persistence, draft validity, resolution and relationship
      freshness are separate facts with separate carriers. Owner:
      [Live relationships](08-live-relationships.md#recoverability-is-a-transition-not-a-state).
- [ ] **OBJ-16** — A presentation edit changes its container, not the source
      object, and is undone in the container's history. Owner:
      [Object identity](07-object-identity.md#presentation-identity).
- [ ] **OBJ-17** — Names, identities, revisions, counts, timestamps, source
      chips, backlinks, search results, diagnostics and manifests each obey
      the metadata disclosure policy. Owner:
      [Live relationships](08-live-relationships.md#metadata-disclosure).
- [ ] **OBJ-18** — A portable bundle carries reconstructable data and never a
      capability grant, host secret or machine-local handle; import reacquires
      authority. Owner: [Object identity](07-object-identity.md#duplicate-derive-export).

## Controls and keyboard

- [ ] **CTL-01** — Every interactive object is reachable by keyboard in a
      logical order, except a disabled control that leaves the tab order with
      its reason reachable elsewhere. Owner:
      [Focus and the keyboard](18-focus-keyboard.md#tab-order).
- [ ] **CTL-02** — The focus ring uses the theme's focus role, 3 units at 3
      units offset, and keeps the control's allocated border. Owner:
      [Focus and the keyboard](18-focus-keyboard.md#the-focus-ring).
- [ ] **CTL-03** — Focus returns through the focus-return chain: invoker,
      surviving logical context, then a safe fallback. Owner:
      [Focus and the keyboard](18-focus-keyboard.md#focus-memory-and-the-focus-return-chain).
- [ ] **CTL-04** — Effective targets are at least 28 units; the splitter,
      scrollbar and other declared exceptions are valid only with their
      alternatives, and a dialog's primary action is 36. Owner:
      [Controls](19-controls.md#sizes-and-spacing).
- [ ] **CTL-05** — Focus toggling changes neither layout bounds nor the
      command target. Owner: [Spacing and metrics](14-spacing-metrics.md#bounds).
- [ ] **CTL-06** — Accessible bounds describe the semantic region and are not
      required to equal the hit map. Owner:
      [Accessibility](39-accessibility.md#targets-and-pointer).
- [ ] **CTL-07** — Every icon-only button has an accessible name. Owner:
      [Icons](16-icons.md#accessibility).
- [ ] **CTL-08** — A drag interaction has a keyboard alternative. Owner:
      [Controls](19-controls.md#sliders-and-steppers).
- [ ] **CTL-09** — Every composite declares its input modes, how Tab leaves it
      and how Escape returns to navigation. Owner:
      [Focus and the keyboard](18-focus-keyboard.md#input-modes-and-routing).
- [ ] **CTL-10** — Enter and Space activate only the focused control in
      navigation mode; text editing and composition take them first. Owner:
      [Focus and the keyboard](18-focus-keyboard.md#input-modes-and-routing).
- [ ] **CTL-11** — A pressed control responds within one refresh interval, no
      more than 16.7 milliseconds at 60 hertz. Owner:
      [Motion](17-motion.md#timing-events).
- [ ] **CTL-12** — The command palette opens with Control+K, completes inside
      its query field only, and announces its results. Owner:
      [Command palette](23-command-palette.md#opening-and-closing).
- [ ] **CTL-13** — A command record declares one semantic identity across
      menus, palette, toolbar and context menus, with an invocation context
      captured at invocation. Owner: [Menus](10-menus.md#command-records).
- [ ] **CTL-14** — A canvas tool commits or cancels by its declared per-tool
      rule; a selection or pan tool creates no content mutation. Owner:
      [Selection and tools](24-selection-tools.md#one-active-tool).

## Feedback and failure

- [ ] **FBK-01** — An error says what happened, what was preserved and what to
      do next. Owner: [Errors and recovery](25-errors-recovery.md#the-anatomy-of-an-error).
- [ ] **FBK-02** — A recoverable error is shown inline before it is shown in a
      dialog. Owner: [Errors and recovery](25-errors-recovery.md#inline-first).
- [ ] **FBK-03** — A destructive action names its object and offers Cancel as
      the default. Owner: [Dialogs](22-dialogs.md#defaults-and-focus).
- [ ] **FBK-04** — An operation longer than 200 milliseconds announces itself,
      and one that finishes says so once. Owner: [Motion](17-motion.md#timing-events).
- [ ] **FBK-05** — A cancel action is acknowledged within 200 milliseconds,
      suppresses publication immediately, and any cleanup continues in a
      separate **Cancelling** state. Owner: [Motion](17-motion.md#cancellation).
- [ ] **FBK-06** — Timing is measured from the accepted action to the first
      frame showing the new state, and each background operation is bounded by
      its own trigger. Owner: [Motion](17-motion.md#timing-events).
- [ ] **FBK-07** — Progress is visible and does not block unrelated work.
      Owner: [Toolbars and status](11-toolbars-status.md#progress).
- [ ] **FBK-08** — A dialog declares modality, presentation and purpose
      separately, and a sheet does not bypass the purpose's decision rules.
      Owner: [Dialogs](22-dialogs.md#three-separate-properties).
- [ ] **FBK-09** — A failed export leaves the previous output intact. Owner:
      [Output parity](37-output-parity.md#failure-behaviour).
- [ ] **FBK-10** — A partial export is marked as partial. Owner:
      [Output parity](37-output-parity.md#failure-behaviour).
- [ ] **FBK-11** — Diagnostics are reachable from Help. Owner:
      [Menus](10-menus.md#order).

## Output

- [ ] **OUT-01** — Display, PDF, print, raster, thumbnail, clipboard,
      accessibility, hit map and manifest agree with the scene within the
      declared tolerances for their declared intent, not across unrelated
      intents. Owner: [Output parity](37-output-parity.md#targets-artefacts-and-encodings).
- [ ] **OUT-02** — Application chrome, guides, grids and selection handles are
      excluded from document output, while intended state marks remain. Owner:
      [Output parity](37-output-parity.md#participation-policy).
- [ ] **OUT-03** — Every artefact and its manifest identify one accepted
      snapshot. Owner: [Output parity](37-output-parity.md#the-snapshot).
- [ ] **OUT-04** — The bundle is staged and published as a unit; a failure
      leaves the previous published bundle intact. Owner:
      [Output parity](37-output-parity.md#failure-behaviour).
- [ ] **OUT-05** — Text remains text in PDF and in the accessibility tree.
      Owner: [Output parity](37-output-parity.md#text).
- [ ] **OUT-06** — Fonts are embedded; a permitted substitution is still
      embedded where the chosen profile requires it, and is recorded in the
      manifest. Owner: [Output parity](37-output-parity.md#what-must-agree).
- [ ] **OUT-07** — A colour outside the target's gamut is reported before
      export. Owner: [Output parity](37-output-parity.md#colour).
- [ ] **OUT-08** — The hit map describes the same instances that were drawn.
      Owner: [Output parity](37-output-parity.md#hit-regions).
- [ ] **OUT-09** — A preflight override changes only a waivable policy
      outcome; it never grants authority or makes structurally invalid output
      conformant. Owner: [Cabochon Press](34-cabochon-press.md#preflight).
- [ ] **OUT-10** — A PDF/X claim is made only by a profile that validates the
      chosen level. Owner: [Output parity](37-output-parity.md#export-profiles).

## Localization and access

- [ ] **LOC-01** — Every resource key exists in every shipped locale. Owner:
      [Localization](38-localization.md#resources).
- [ ] **LOC-02** — Both pseudo-locales build and export without clipping or
      overlap. Owner: [Localization](38-localization.md#testing).
- [ ] **LOC-03** — Panes, menus and focus order mirror for right-to-left
      locales; directional icons mirror and object icons do not, by per-icon
      metadata rather than a global flip. Owner:
      [Localization](38-localization.md#direction), [Icons](16-icons.md).
- [ ] **LOC-04** — Numbers, dates and currency use the locale's formats.
      Owner: [Localization](38-localization.md#numbers-dates-and-units).
- [ ] **LOC-05** — The accessibility tree exposes roles, names, states,
      accessible bounds and order. Owner:
      [Accessibility](39-accessibility.md#the-tree).
- [ ] **LOC-06** — A screen-reader user can complete the primary task. Owner:
      [Accessibility](39-accessibility.md#testing).
- [ ] **LOC-07** — At 200 per cent interface scale, every control is reachable
      and no control or text overlaps; the compact profile applies where
      needed. Owner: [Accessibility](39-accessibility.md#zoom-and-reflow).
- [ ] **LOC-08** — Narrowing a pane or enlarging text never shrinks text below
      the user's requested scale. Owner: [Accessibility](39-accessibility.md#zoom-and-reflow).
- [ ] **LOC-09** — Reduced motion makes finite transitions effectively
      immediate, keeps activity indicators static, and never speeds an
      infinite animation up. Owner: [Motion](17-motion.md#reduced-motion).

## Documentation and review

- [ ] **DOC-01** — The application's window, menus and shortcuts match the
      book or record an approved departure. Owner:
      [Purpose](01-purpose.md#scope).
- [ ] **DOC-02** — A figure that contradicts the book has been corrected in
      the generator. Owner: [README](README.md#building-the-book).
- [ ] **DOC-03** — The export bundle and its manifest are attached to the
      review. Owner: [Output parity](37-output-parity.md#the-manifest).
- [ ] **DOC-04** — The reviewer has read the proof sheet and the application
      at 100 and 200 per cent zoom. Owner: [README](README.md#building-the-book).

## Sign-off

A reviewer records:

- the build and scene versions;
- the locales tested;
- the export targets tested;
- every item marked not applicable, with the false predicate that made it so;
- every departure from a **should**, with its reason;
- every **must** that does not hold, which blocks sign-off.

A checklist with an unexplained failure is not a pass. The purpose of the list
is to make the decision visible, not to produce a green tick.
