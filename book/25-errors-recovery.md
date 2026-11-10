---
title: Errors and recovery
part: Interaction
summary: Errors that say what happened, what survived and what the user can do next.
---

# Errors and recovery

An error is a statement about the work, not about the user. It says what
happened, what survived and what can be done next. It never scolds, never
blames and never presents a raw failure as the whole message.

## The anatomy of an error

Every error surface carries four parts.

1. **What happened.** One sentence in plain language.
2. **What survived.** The object, value or document that is still intact.
3. **Why.** The cause, in terms the user can act on.
4. **What next.** A primary recovery action and a way to dismiss.

An error that omits the second part is unsafe, because the user cannot tell
whether their work is gone. An error that omits the fourth part is a dead end.

## Inline first

Most errors belong beside the thing that failed.

- A field validation error appears below the field and is associated with it
  for assistive technology.
- A failed embed appears in place, inside its placeholder, with its state
  word and a retry action.
- A failed save appears in the status line and in the document header, and the
  document keeps its modified mark.
- A failed export appears in the export surface, with the path that was
  attempted and the reason.

A dialog is reserved for a failure that blocks the current task and needs a
decision. A failure that can be retried without a decision must not open one.

## Preserving work

The first duty of an error path is to preserve the last committed state.

- A failed mutation leaves the object at its previous revision.
- A failed refresh keeps the last successful value, labelled **Stale** or
  **Broken**.
- A failed save keeps the document open and modified; it never closes the
  window.
- A failed import leaves the existing document untouched and reports the
  objects that could not be read.

An application must never replace a value with an empty value because it could
not read the source. The [live relationship states](08-live-relationships.md)
exist to make preservation expressible.

## Wording

- Use the active voice: "The table could not be refreshed", not "The table
  refresh failed".
- Name the object and, where several similar objects exist, its identity
  suffix.
- Avoid internal error codes as the primary message. A code may appear in a
  details block, copyable for support.
- Avoid "invalid", "illegal" and "bad" as descriptions of user input. Say what
  the field expects.
- Do not use exclamation marks.
- Do not apologize. An apology takes space without helping the user decide.

## Retry and recovery

A retry must be safe. If repeating the operation could duplicate a change, the
interface offers **Review** instead of **Retry**, and shows what would happen.

- A transient network failure offers **Retry**.
- A permission failure offers **Request access** or **Open settings**, not
  **Retry**.
- A malformed object offers **Edit source** or **Export original**, not
  **Retry**.
- A conflict offers **Compare** and **Choose**, not **Overwrite**.

## Partial failure

An operation that affects several objects may partly succeed. The report must
say which objects succeeded and which did not, and must not describe the whole
operation as failed.

- The successful objects keep their new revision.
- The failed objects keep their previous revision.
- The report lists both sets and offers a retry for the failed subset.
- The document remains usable throughout.

## Degraded mode

When a provider is missing, an object may still be readable as bytes. The
interface says **Opaque**, preserves the object and offers **Export original**.
It does not pretend the object is editable, and it does not delete it to tidy
the document.

When the runtime loses a tool registry, the affected commands become
unavailable with a reason. The document continues to open, render, print and
export using the last known presentations.

## Diagnostics

A diagnostic surface is available from **Help**, from the affected object's
context menu and from the command palette. It shows:

- the object's identity and revision;
- the provider and its version;
- the capability that was requested and its outcome;
- the last successful and last failed operation, with timestamps;
- a copyable diagnostic bundle that contains no document content unless the
  user chooses to include it.

Diagnostics must never be the primary error message. They are the place a
support conversation begins, not the place a user is left.

## Logging

Errors are recorded with enough context to reproduce them and without recording
document content by default. A log entry carries the object identity, the
operation, the outcome and the provider version. It does not carry the value
that was read.

## Testing

A reviewer should be able to produce each failure state on demand and observe
four things: a plain sentence, the preserved value, a safe recovery action and
a diagnostic record. The [checklist](40-checklist.md) lists the failures that
must be exercised before release.
