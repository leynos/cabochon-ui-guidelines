---
title: Inspector
part: Interaction
figure: fig-17-inspector.svg
summary: Identity, presentation, state and authority, in that order, read-mostly by default.
---

# Inspector

![Object inspector.](../figures/fig-17-inspector.svg)

The inspector explains the object under the selection. It answers four
questions in a fixed order: what the object is, how it is being shown, what
state its relationships are in and what the application is allowed to do with
it.

The inspector describes. It does not become a second application, and it does
not become the place where every property is edited.

## Structure

The inspector is 240 logical units wide by default and uses the pane plane. Its
head carries the word **Inspector** and, where useful, the selected object's
type.

The body is divided into four blocks.

1. **Identity.** Object identity, provider, revision and parent.
2. **Presentation.** Every presentation of the object, with the current one
   selected.
3. **State.** The live relationship state and its last successful update.
4. **Authority.** The capabilities that allow read, write, share and export.

A fifth block for instrument-specific properties may follow, but it must not
push identity below the fold.

## Identity block

The identity block shows:

- the object's display name, in 18-unit display italic;
- its type and a short identity suffix, in the operational metadata role at the
  12-unit floor;
- its provider;
- its revision;
- its parent object or document.

Each value is selectable and copyable. A command copies the full identity, not
the displayed suffix. The inspector must never show a file path in place of an
identity.

Identity, name, revision and provider are metadata classes. They are shown only
when the current grant's disclosure policy permits that class. A denied object
may therefore show a non-disclosing placeholder in place of any of them, as
described in [Live relationships](08-live-relationships.md).

## Presentation block

Every presentation instance relevant to the object is listed, with the current
one marked. The list distinguishes the shared presentation definition from the
placement in this document.

Choosing another presentation for this placement changes the containing
document's reference record and its undo history. It does not change the source
object and does not change a second embed of the same object. Changing the
shared definition is a separate operation.

- The list names the presentation and its context: **In note**, **Dataframe**,
  **Print**.
- A presentation that is unavailable is shown greyed with a reason.
- The block does not offer to convert, flatten or export unless the object
  genuinely supports that operation.

## Authority block

The authority block lists the capabilities relevant to the selection and
whether the runtime's capability broker granted, denied or has not been asked
for each.

- Granted appears in the pine role.
- Denied appears in the oxide role and names the capability in plain language.
- Not requested appears in the soft-text role.

A denied capability must not reveal the protected value anywhere in the
inspector, including in a tooltip, a count, a revision number or a timestamp
that could leak activity. The block states the broker's decision; it does not
offer to widen a grant.

## State block

The state block shows the live relationship state using the vocabulary of
[Live relationships](08-live-relationships.md). It includes the last successful
refresh time in the operational metadata role and the action that can restore
the relationship.

The state block is the one place where the inspector may show a provider's
diagnostic text. It must be a sentence, not a stack trace, and it must be
paired with a user action. Diagnostic text is subject to the same metadata
disclosure policy as the rest of the inspector.

## Read-mostly by default

The inspector may edit a property, but editing happens through the same
transaction as the document. It must not maintain a parallel copy of the object
or a private undo stack.

The rule has four consequences.

- A property change made in the inspector is undoable with the document's undo.
- The inspector shows the object's committed revision and, separately, any
  draft that has not been committed.
- A failed save preserves both the unsaved draft and the committed identity;
  it does not present the draft as committed.
- A conflict in the inspector is resolved with the same conflict surface as a
  conflict in the document.

An inspector edit that spans several objects is one atomic semantic
transaction. It commits every declared mutation or none of them; it never
leaves a successful subset visible. If the runtime cannot make the
participating providers atomic, it rejects the edit before mutation. Choosing a
compatible subset of objects is a separate step that happens before invocation
and is shown to the user; it is not partial success.

## Editing text in the inspector

An inspector value that accepts text is an editable control, and it owns the
text-editing commands while it has focus. Cut, Copy, Paste, Delete, Select all
and Undo act on the field's text selection before they act on the document
selection. The rule is the one stated in
[Selection and tools](24-selection-tools.md), applied here.

- A command that is document-scoped says so in its label and in its accessible
  name, and its invocation context names the document rather than the field.
- Leaving the field commits or cancels according to the field's declared
  behaviour; it does not silently leave a draft that the document's undo cannot
  reach.
- A field that shows a read-only value still allows selection and copying, and
  its Copy command copies the value, not the object identity.
- A context menu opened inside a field targets the field's text selection. It
  does not retarget the document selection, and it does not offer commands that
  are ineffective on the field.

## Bounds and accessibility

The inspector reports the same five bounds as every other control, defined in
[Spacing and metrics](14-spacing-metrics.md): layout, visual, focus-decoration,
effective hit region and accessible.

- The accessible bounds of a value are the bounds of the semantic region that
  carries it, after the same transform as the visual bounds. They are not the
  hit region, and they are not required to equal it.
- A value that is clipped by the pane reports its unclipped semantic bounds
  only when the assistive technology can scroll it into view; otherwise it
  reports the visible region and its accessible name carries the full value.
- A focus ring drawn outside the control does not enlarge the accessible
  bounds, and toggling focus changes neither the layout bounds nor the command
  target.
- A block that reflows under enlargement reports the bounds of its reflowed
  region, not the bounds it had at the default width.

## What the inspector is not

- A second copy of the document.
- A raw diagnostic console.
- A place to edit every property at once.
- A marketing surface for unused features.
- A substitute for a focused editor.

## Empty and multiple selections

With no selection, the inspector shows the document's identity and state. With
multiple objects selected, it shows the shared properties and a count, and
every property that differs reads **Mixed**. The count is a metadata class and
is withheld when the disclosure policy protects it.

Editing a mixed property applies the new value to every selected object through
one atomic transaction, and the inspector says so before the change is
committed. The whole declared set commits or none of it does. An explicitly
independent batch is a different command and names its commit units in advance.

## Width and scrolling

The inspector scrolls vertically, never horizontally. A metadata or value field
truncates at the end and reveals the full value in a tooltip and through a
keyboard-reachable expansion. An essential field label does not truncate: it
wraps, or the block reflows. Truncation never removes the only route to the
value.

A user may widen the inspector by dragging the splitter, up to 360 logical
units; beyond that, the content should move to a dedicated pane. The requested
width is remembered separately from the width currently feasible in the window,
as described in [Panes](20-panes.md).
