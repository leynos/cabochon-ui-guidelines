---
title: Accessibility
part: Breadth
figure: fig-32-accessibility.svg
summary: The accessibility tree is another output of the same scene, not a reconstruction.
---

# Accessibility

![Accessibility tree and focus order.](../figures/fig-32-accessibility.svg)

Accessibility is not a feature added to a finished interface. It is a property
of the scene. The scene carries semantic annotations, and the same annotations
produce the accessible tree and the hit map; the pixels are a projection of the
same scene. If a name is missing from the annotation, it is missing from every
target that needs it.

## Semantic nodes and drawing primitives

The accessible tree is not a one-to-one copy of the drawing primitives. Four
kinds of scene content are treated differently.

- **Semantic nodes** carry a role, a name, a state and a position in the
  logical reading order. A control, a document, a menu and a diagram element
  are semantic nodes.
- **Decorative geometry** carries no role and is absent from the tree. A
  keyline, a background plane and an ornamental rule are decorative.
- **Static text** is exposed as text content within its parent, not as an
  independent tab stop.
- **Composite-managed descendants** belong to one composite node. A tree item,
  a grid cell or a menu item is exposed through the composite's own navigation,
  not as a separate top-level stop.

The tree must not omit a control because the control is drawn by a custom
widget. A custom widget declares its role, its name, its actions, its state and
its managed descendants like any other composite.

## The tree

The accessibility tree mirrors the visible structure's meaning.

- A window has a name and a role.
- A menu bar has a name and contains menus, which contain items.
- A tree has a name, a selected item and an item count when the disclosure
  policy permits that class.
- A document has a name and contains groups.
- A control has a role, a name, a state, its actions and bounds.
- A status line has a name and its current text.

The tree also exposes actions and relationships, not only text. An icon button
whose glyph has no text still exposes its action name. A diagram exposes nodes,
edges and their relationships. An embed exposes its state and its inspection
action. A static picture that carries meaning is a semantic node with a name
and a description; a purely decorative picture is absent.

## Names

- Every control has a name. An icon-only button takes its name from its
  accessible label, not from its glyph.
- A name describes the action or the content, not the appearance: **Export as
  PDF**, not **Blue button**.
- A group has a name when it groups related controls.
- A name is translated with the rest of the interface.
- A name is unique within its group, so that a screen reader's list of
  controls is usable.
- Placeholder text is not a name. A field with a placeholder and no label is
  unlabelled.

## Roles and states

- Roles use the platform's accessibility vocabulary: button, check box, radio
  button, text field, tree, tree item, tab, dialog, status.
- States are exposed, not implied by colour: selected, checked, expanded,
  busy, invalid, read-only, unavailable.
- A live relationship exposes its state as **Current**, **Refreshing**,
  **Stale**, **Broken** or **Denied**, matching the visible chip.
- A progress indicator exposes its value and whether it is indeterminate.
- A validation error is associated with the field it describes.

A state that exists only as a colour is invisible to a screen reader and to a
colour-blind user. The state chip, the icon and the text carry it together.

## Focus and keyboard

- Every interactive object is reachable by keyboard in a logical order, except
  a disabled control that leaves the tab order. Its reason remains reachable
  through its help text, its mirrored menu item or the command palette, as
  described in [Controls](19-controls.md).
- The focus ring uses the theme's focus role: 3 units at 3 units offset. The
  ring is drawn outside the control and keeps the control's allocated border,
  so focus changes neither the layout bounds nor the command target.
- The ring is evaluated against the surfaces actually adjacent to it, which a
  3-unit offset may make the window ground rather than the control. Where the
  adjacent surfaces cannot both meet 3:1, the ring gains a one-unit inner
  keyline in the contrasting role, as
  [Planes and borders](15-planes-borders.md) requires.
- Focus is never trapped except in a modal dialog, and a modal dialog returns
  focus through the focus-return chain in
  [Focus and the keyboard](18-focus-keyboard.md).
- Focus is never moved without a reason, such as opening a dialog or
  revealing a pane.
- Access keys are declared in resources and shown in menus.
- The command palette is reachable by keyboard and announces its results.
- A skipped focusable object is a defect, even if it is reachable by pointer.
  A disabled one is not skipped; it is excluded by policy and explained.

Keyboard behaviour depends on the input mode, as defined in
[Focus and the keyboard](18-focus-keyboard.md). In navigation mode, Enter or
Space activates the focused control. In text-editing and composition modes,
those keys belong to the text or the composition first. Every composite
declares how Tab leaves it and how Escape returns to navigation, so no control
traps the keyboard without an exit. A destructive dialog's safe default is not
a guarantee that its focused destructive button is unreachable: deliberate
activation of that button remains possible.

## Targets and pointer

The target minimum applies to the **effective hit region**, not to the visible
glyph and not to an area average. A target is at least 28 by 28 units in both
dimensions; 32 is preferred, and a dialog's primary action is 36.

- A small glyph may sit inside a larger target; the target, not the glyph,
  determines the hit region.
- Adjacent targets have at least 8 units between their effective hit regions.
- A composite control's internal geometry is declared, as in
  [Spacing and metrics](14-spacing-metrics.md); its parts are not independent
  targets, and the composite as a whole is one stop. A swatch palette is such a
  composite: 24-unit swatches, a 4-unit internal gap and a 28-unit effective
  cell, with the palette keeping the 8-unit independent-control gap around it.
- The splitter's 8-unit hit edge spans the full pane boundary, which is a
  larger continuous target than a 28-unit square. It is a declared exception
  and it is not the only way to resize.
- The scrollbar is a declared exception only where a wheel, keyboard and
  drag-anywhere alternative is always present.
- Selection and path handles are a declared compact-target exception. Their
  visible mark is 8 units, their hit region is 20 units clipped to the object's
  bounds, and an object smaller than 20 units uses its own bounds. The fixed
  picking order, Tab cycling and numeric inspector fields in
  [Selection and tools](24-selection-tools.md) are the alternative route; a
  handle that cannot meet the pointer minimum is still reachable and operable
  from the keyboard and from the property fields.
- A drag interaction has a keyboard alternative.
- A context menu is reachable from the keyboard.
- Clipping is declared. When an expanded hit region is clipped by its
  container, the clipped region is the target that must satisfy the policy, and
  the instrument provides a deterministic resolution where two clipped regions
  overlap.

## Contrast and colour

- Body text meets 4.5:1 against its background.
- Large text is text at 18 points or 14 points bold. At the baseline scale of
  96 dots per inch, one point is exactly 4/3 logical units, so 18 points is 24
  units and 14 points bold is 18⅔ units. The conversion is applied before the
  threshold, with no downward rounding: an 18-unit bold label is 13.5 points
  and is not large text, and a 19-unit bold label clears the threshold. An
  18-unit regular label is not large text and is held to 4.5:1.
- Essential icons and boundaries that identify a control meet 3:1.
- Focus indicators meet 3:1 against each adjacent surface.
- The semantic roles are the ones in [Palette](12-palette.md): text, muted
  text, essential border, selected fill and text, primary fill and text,
  destructive fill and text, focus, refresh mark and text, stale, denied and
  disabled. Each resolves in every supported theme.
- Decorative teal never carries text. The refresh **text** role is the readable
  tint, and it is the only teal-family colour used for words.
- Colour is never the only carrier of meaning; every state also has a mark, a
  label or a shape.
- The dark theme meets the same ratios as the light theme, measured after tint
  compositing rather than against an accent in isolation.

## Motion and timing

- Motion respects the reduced-motion setting and collapses to 0.01
  milliseconds.
- No content flashes more than three times per second.
- A timed action can be extended or disabled.
- An animation never delays the availability of a control.
- A progress state is announced, not only drawn.

## Zoom and reflow

- Essential interface text does not fall below 12 units at the user's chosen
  text scale. The operational floor and the 11-unit metadata allowance are
  defined in [Typography](13-typography.md).
- At 200 per cent interface scale, panes may collapse, but every control
  remains reachable, no control overlaps another and no text is clipped. The
  compact layout profile applies below the requested width, as described in
  [Spacing and metrics](14-spacing-metrics.md).
- Narrowing a pane does not undo the user's requested text enlargement. Text
  wraps and rows grow; it is not shrunk to fit.
- Chrome and prose reflow rather than clipping, and neither scrolls
  horizontally. A data grid, a canvas, a page and the document plane may scroll
  horizontally, as [Spacing and metrics](14-spacing-metrics.md) permits.
- At the supported floor of 512 by 384 logical units, the compact profile
  keeps every control reachable and the document plane scrolls rather than
  shrinking below its declared minimum.
- A high-contrast theme replaces the palette rather than tinting it.

## The accessibility output

The `accessibility.json` artefact in the export bundle contains the tree:
roles, names, states, bounds and order. It is generated from the same scene as
the pixels.

Each accessible node carries its scene-node identity. When two placements of
one semantic object appear in the scene, they are two nodes with distinct
identities and the same optional semantic reference; collapsing them into one
node would make one placement unreachable. A semantic object identity is
present only when the Enfilade bridge supplies it, and it never substitutes for
the node identity. A substrate-only scene, such as
[hello-window](36-hello-window.md), is fully accessible without any semantic
object identity at all.

Each node reports **accessible bounds**, which are the bounds of the semantic
region the node represents, after the same transform as the visual bounds. They
are not the hit region and are not required to equal it. The five bounds are
defined in [Spacing and metrics](14-spacing-metrics.md): layout, visual,
focus-decoration, effective hit region and accessible. A declared hit expansion
or a focus ring outside the control changes the hit or decoration bounds, not
the accessible bounds.

A test compares the tree with the scene and fails when:

- a drawn control has no role;
- a named control has no accessible name;
- a state is visible but not exposed;
- the order disagrees with the focus order;
- accessible bounds do not correspond to the chosen semantic region after the
  same transform;
- the hit map does not equal the declared expansion and clipping of the visual
  target;
- toggling focus changes the layout bounds or the command target.

## Live assistive technology

The exported `accessibility.json` proves that a snapshot can be described. It
does not prove that a native assistive-technology client can use the running
application, and the book does not treat it as such proof.

Three dimensions of an object are independent, and a test must name the one it
asserts.

| Dimension           | Question                                      | Values                                   |
| ------------------- | --------------------------------------------- | ---------------------------------------- |
| Resolution          | Did a provider load the bytes?                | Resolved, Opaque, Unavailable, Malformed |
| Semantic projection | Can the loaded provider describe the content? | Full, bounded fallback, not declared     |
| Authorization       | May this client read the content now?         | Permitted, Denied                        |

They vary independently. A **Resolved** object can use the bounded fallback
without becoming Opaque. An **Opaque** object has no provider at all, so its
semantic projection is absent by definition. A **Denied** object keeps whatever
resolution and projection it already had, and reports the denial as its live
state.

- The native adapter exposes actions, not only names: activate, focus, set
  value, expand, collapse, select, scroll and show menu, as the role allows.
- A logical row that is outside the visible viewport is still reachable. A
  virtualized grid or tree reports its logical child count where the disclosure
  policy permits that class, and materializes a row when a client asks for it;
  the client does not have to scroll the visible area to discover content. When
  the count is withheld, it reports that further items exist without a number.
- Coalescing applies to redundant application announcements and intermediate
  frames. Typing, caret movement and selection changes remain observable
  through the adapter's native text, caret and selection notifications, which
  the application must not suppress. Duplicate application-level announcements
  for the same settled change are removed; the required native notification is
  not.
- Focus changes, selection changes, busy state and validation results each
  produce one application announcement per settled change, not one per
  intermediate frame. A selection change still reaches the native selection
  notification even when its application announcement is coalesced.
- Semantic projection is a provider contract, not a condition of resolution. An
  installed provider must declare whether it supplies the projection. A
  provider that declares it and then fails at run time uses the bounded
  fallback: the object's name, identity where disclosure permits, its role, the
  actions the provider can still support and the action that retries or
  configures it. The tree labels the description as bounded; it does not
  present it as the provider's full semantics. The object stays **Resolved**,
  remains drawable and exportable, and the failure is written to diagnostics.
- A provider that supplies no projection, or a fallback that is only partial,
  is never relabelled **Opaque**. Opaque stays reserved for intact bytes with
  no installed provider, as [Embeds](32-embeds.md) defines it.
- Authorization is checked separately. A denied read never changes resolution,
  identity or the underlying bytes.

The exported tree and the live adapter read the same scene-associated
annotations, so an exported name and a spoken name cannot drift apart.

## Testing

Accessibility is tested at four levels.

1. **Automated.** The tree is checked against the scene for roles, names,
   states and bounds.
2. **Keyboard.** A reviewer completes the primary task without a pointer.
3. **Screen reader.** A reviewer completes the primary task with a screen
   reader and confirms that every change is announced.
4. **Visual.** A reviewer checks the focus ring, the contrast and the state
   marks at 100 and 200 per cent zoom.

A pass at the first level does not imply a pass at the others. The automated
check proves the tree exists; the manual checks prove it is usable.

At the native-adapter level, typing, caret movement and selection changes must
remain observable while duplicate application-level announcements are
suppressed. A resolved provider whose semantic adapter fails must use the
declared bounded fallback without changing the object's identity, its
resolution state or its eligibility for export.

## What accessibility is not

- An alternative interface maintained separately.
- A checklist completed after release.
- A reason to remove keyboard shortcuts or compact layouts.
- A synonym for colour contrast alone.
