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

- A failed atomic mutation leaves every object at its previous committed
  revision; no successful subset is exposed.
- A failed refresh keeps the last accepted value when authority permits its
  display, labelled **Broken**. It keeps an unauthorised value only in
  protected storage.
- A failed save keeps the document open, modified and with its draft intact; it
  never closes the window.
- A failed import leaves the existing document untouched and reports the
  objects that could not be read.

An application must never replace a value with an empty value because it could
not read the source. It must also never retain a value whose authority has
ended. The [live relationship states](08-live-relationships.md) exist to make
preservation expressible; redaction takes precedence over preservation.

## Wording

- Use the active voice with an explicit actor where known: "Cabochon could not
  refresh the table", not "The table could not be refreshed". The second
  sentence is passive, even though the contrasted "The table refresh failed" is
  grammatically active; the latter names no actor and is less helpful.
- Name the object and, where several similar objects exist and disclosure
  permits, its identity suffix.
- Avoid internal error codes as the primary message. A code may appear in a
  details block, copyable for support.
- Avoid "invalid", "illegal" and "bad" as descriptions of user input. Say what
  the field expects.
- Do not use exclamation marks.
- Do not apologize. An apology takes space without helping the user decide.

## Retry and recovery

A retry must be safe. An operation with an uncertain outcome is not repeated
blindly: the runtime first resolves the original outcome or reuses an
idempotent operation identity. If repeating the operation could duplicate a
change, the interface offers **Review** instead of **Retry**, and shows what
would happen.

- A transient network failure offers **Retry**.
- A permission failure offers **Request access** or **Open settings**, not
  **Retry**.
- A malformed object offers **Edit source**, not **Retry**.
- A conflict offers **Compare** and **Choose**, not **Overwrite**.

## Atomic operations, batches and partial failure

An **atomic semantic transaction** commits its whole declared mutation set or
none of it. It never leaves a successful subset visible. If a participating
provider cannot support atomic preparation and commit, the runtime rejects the
operation before mutation. Injecting a denial, a conflict, a provider crash or
a restart at any transaction boundary leaves the observable semantic state at
the old committed set or the new committed set.

Choosing a compatible subset before invocation is not partial success. The
interface shows the chosen subset and then transacts it atomically.

A **batch of independent transactions** is a different operation. It identifies
its commit units before execution and reports each unit separately. Partial
results in a batch are expected and are never described as partial success of
an atomic transaction.

An **import with explicit partial mode** is a batch. It states its commit
units, its recovery behaviour and its undo grouping, and it is distinct from an
all-or-nothing import. A partially imported document says which objects are
absent; it does not pretend the import was complete.

## Degraded mode

When a provider is missing, an object may still be readable as bytes.
Resolution, authority and cached availability remain separate. When current
authority permits it, the interface says **Opaque**, preserves the object and
offers **Export original**. It does not pretend the object is editable, it does
not delete it to tidy the document, and it does not offer export when authority
withholds it.

When the runtime loses a tool registry, the affected commands become
unavailable with a reason. The document continues to open, render, print and
export using the last known presentations.

When the display renderer fails entirely, the failure is not disguised as a
working window. The application keeps the last committed document model, shows
a bounded fallback surface with reachable diagnostics, disables mutations whose
visible target cannot be validated, and redacts any retained pixel or thumbnail
that would disclose information whose authority has ended. The
[output chapter](37-output-parity.md) defines the retained-pixel and hit-region
rules.

## Diagnostics

A diagnostic surface is available from **Help**, from the affected object's
context menu and from the command palette. It shows, subject to the metadata
disclosure policy:

- the object's identity and revision;
- the provider and its version;
- the capability that was requested and its outcome;
- the last successful and last failed operation, with timestamps;
- a copyable diagnostic bundle that contains no document content unless the
  user chooses to include it.

An opt-in diagnostic-content setting can include public metadata and public
content. It cannot override a denial or reveal a protected metadata class.
Diagnostics must never be the primary error message. They are the place a
support conversation begins, not the place a user is left.

## Logging

Errors are recorded with enough context to reproduce them and without recording
document content by default. A log entry carries the object identity, the
operation, the outcome and the provider version when disclosure permits. It
does not carry the value that was read, and it does not carry a protected
identity, revision, count or timestamp. A log is one of the output surfaces
covered by the authorisation matrix: it is not exempt because it is not visible.

## Testing

A reviewer should be able to produce each failure state on demand and observe
four things: a plain sentence, the preserved value, a safe recovery action and
a diagnostic record. The [checklist](40-checklist.md) lists the failures that
must be exercised before release.
