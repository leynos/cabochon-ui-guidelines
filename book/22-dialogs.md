---
title: Dialogs
part: Interaction
figure: fig-19-dialog.svg
summary: Modality, presentation and purpose stated separately, with a safe way out of each.
---

# Dialogs

![Destructive confirmation dialog.](../figures/fig-19-dialog.svg)

A dialog interrupts the user's work, so it must earn the interruption. It asks
one question, names the object concerned and offers a clear way out. It is not
a place to arrange the application, explain the product or collect unrelated
settings.

## Three separate properties

Every interrupting surface declares three properties independently. Confusing
them is how a sheet acquires a dialog's restrictions without earning them, or a
dialog escapes its own rules by changing shape.

**Modality** says what the surface blocks.

- **None.** The user may work elsewhere while the surface is open.
- **Document.** The containing document is inert; other documents remain usable.
- **Application.** The whole application is inert.

**Presentation** says how the surface is drawn.

- **Inline.** A region inside the document or pane.
- **Popover.** A small surface anchored to a control or a selection.
- **Sheet.** A document-modal surface attached to its window.
- **Window.** A separate window with its own title bar.
- **Host portal.** A surface owned by the host, such as a file or print dialog.

**Purpose** says what the surface is for.

- **Information.** It reports something and needs acknowledgement.
- **Input.** It collects values before an operation.
- **Confirmation.** It asks whether to proceed with a named action.
- **Recovery.** It resolves a failure and preserves work.

A sheet is the host presentation of a document-modal dialog. It does not bypass
the rules for its purpose merely because it is attached to a window. A separate
window with the same purpose follows the same transaction and default rules.

## When to interrupt

Use an interrupting surface when all three statements hold.

1. The decision cannot be deferred.
2. The decision needs information that the document does not show.
3. Proceeding without the decision would lose work or authority.

When any statement fails, use an inline message, a popover, a pane or the
status line instead. A routine, reversible operation must not interrupt.

An information surface that only reports a completed operation belongs in the
status line or the document, not in a dialog. A recovery surface is justified
when the failure blocks the current task and the user must choose how to
preserve work.

## Anatomy

A Cabochon dialog has five parts.

- A title bar naming the question, such as **Replace the embedded table?**
- A sentence or short paragraph explaining the consequence.
- An identity block naming the affected object, with its type, revision and
  identity suffix.
- Optional choices, such as **Keep a copy in this note**.
- Actions at the bottom, on the trailing edge: a safe action, an optional
  alternative such as **Discard**, and the confirming action. Three actions is
  the practical maximum; a fourth question belongs in a different surface.

The dialog uses the overlay plane and the offset shadow. Its width is between
420 and 560 units; a dialog that needs more should become a sheet or a pane.
The dialog reflows and scrolls when text is enlarged or a translation grows. It
does not hold a fixed height that clips its content.

## Wording

- The title asks one question, in sentence case, ending with a question mark
  when it is a question.
- The body names the object and states the consequence in plain language.
- The confirming button uses the specific verb: **Replace**, **Delete**,
  **Discard**, **Remove embed**.
- The safe button is **Cancel**, not **No**, **Dismiss** or **Close**.
- A destructive consequence is stated once, in the body. It is not repeated in
  three places.

## Defaults and focus

The default action is scoped to the purpose and the destructive risk.

- A **destructive confirmation** starts with focus on its safe action. The
  destructive button is never the Return default. It remains reachable by Tab
  and activatable by Enter or Space when it has focus, so that a deliberate
  choice is still possible.
- A **non-destructive confirmation** may start with focus on its primary action
  when it confirms an action the user has just requested. Escape still cancels
  without side effects.
- An **information** surface starts with focus on its dismiss action.
- An **input** surface starts with focus on its first field, not on a button.
- A **recovery** surface starts with focus on the action that preserves work.
  The failed-save flow in [Facet Notes](26-facet-notes.md) is the named
  exception: **Keep open** is the default because it preserves the draft, even
  though it is not the affirmative button.

The focus ring is drawn on the focused button, as described in
[Focus and keyboard](18-focus-keyboard.md).

Four properties are commonly conflated and are kept apart here. The **default
action** is what Return invokes. The **initially focused control** is where the
focus ring starts. The **presentation** is whether the surface is a sheet, a
modal dialog or a non-modal panel. **Cancellability** is whether Escape can
abandon the transaction. A destructive confirmation may be a cancellable sheet
that starts focus on its safe action while making the destructive action
reachable but not the Return default. Changing one property never implies
another, and the invocation context — which command opened the surface and on
what selection — decides all four together.

## Behaviour

- Escape follows the surface's declared safe exit. It cancels without
  committing a draft change and returns focus through the focus-return chain.
- Enter and Return are the same activation event. It activates the focused
  control when that control is activatable, including a deliberately focused
  destructive button. It activates the default action only when focus is not on
  an activatable control and not in a text field or composition. The routing
  table in [Focus and keyboard](18-focus-keyboard.md) is authoritative.
- Tab cycles within a modal surface; focus does not escape to the document
  behind.
- The document behind a document-modal surface is inert and visibly dimmed, but
  remains readable.
- Closing the surface returns focus through the focus-return chain in
  [Focus and keyboard](18-focus-keyboard.md).
- A dialog must not open another dialog. If a second question is required, the
  first dialog closes and the second takes its place, or the questions are
  combined.
- A dialog must not be resizable unless it contains a scrollable list of
  objects selected by the user.

## Destructive actions

A destructive action removes, replaces or overwrites something the user can
see. The dialog must state:

- what will be removed or replaced;
- what will remain;
- whether the action can be undone;
- the object's identity, where more than one similar object exists.

The dialog must not use a red heading for a non-destructive action, and must
not use a neutral button for a destructive one. Colour supports the verb; it
does not replace it.

## Progress and long operations

A dialog must not remain open while a long operation runs behind it. Close the
dialog, show progress in the status line and the document, and report the
outcome once. If the operation fails, the failure appears in the document with
a recovery action, not in a second dialog stacked on the first.

## Sheets and host dialogs

Where the host supports sheets, a document-modal dialog attaches to its window
as a sheet. Where it does not, the dialog is centred over the window. In hosted
mode, file, print and portal dialogs belong to the host and must not be
imitated by the application.

A sheet's modality is document, not application. It does not block another
document, and it does not change the transaction semantics of the operation it
confirms.

## Testing

A reviewer should be able to cancel every surface with Escape, confirm that its
modality matches its focus and inertness behaviour, and return through the
focus-return chain. A destructive confirmation starts on its safe action; a
non-destructive confirmation may start on its primary action; a recovery
surface starts on the action that preserves work. Presenting the same question
as a sheet or a separate window must not change what is committed.

A dialog that fails any of these tests is not ready.
