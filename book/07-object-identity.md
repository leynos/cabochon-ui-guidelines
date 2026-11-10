---
title: Object identity
part: The document world
summary: Stable identity, revisions, presentations and the difference between duplicate and export.
---

# Object identity

Every persisted Cabochon object has an identity that does not depend on the
application showing it, the file containing it or the place it was first
created. Identity is the foundation of the environment; if it is ambiguous,
every later promise about embeds, tools and live relationships becomes
unreliable.

## What identity means

An object identity is a stable reference with four properties.

- **Stable.** It survives save, reopen, rename, move and export.
- **Unique.** Two objects never share an identity, even across projects.
- **Opaque.** It is not a file path, a row number or a title, and applications
  must not parse it.
- **Copyable.** A user can copy it for support, scripting or inspection.

An object may also carry a human-readable name. The name is a label; the
identity is the truth. Renaming an object must not break a link to it, and two
objects may share a name without becoming the same object.

## Revisions

A revision records a change to an object's content. It is not a user-visible
version number in the manner of a document-management system; it is the basis
for conflict detection and undo.

The interface rules are:

- A stale revision must never overwrite a newer one silently. The user sees a
  conflict and chooses.
- Undo restores content, not identity. Undoing an edit must not create a new
  object.
- An object's history may be inspectable, but history is not the default view.

## Presentation identity

A presentation is a way of showing an object. It has its own identity so that a
document can remember *which* view of the object it contains — the compact
currency row, the detailed card, the chart — without confusing that choice with
the object itself.

This distinction appears in the interface as follows.

- Changing a presentation must not change the object.
- A document that embeds an object stores the object identity and the
  presentation choice.
- Reopening a document restores the presentation, not a rendered copy.
- A presentation that is no longer available falls back to a declared
  placeholder and reports the problem; it does not silently substitute a
  different view.

## Duplicate, derive, export

The three operations are distinct and must be labelled distinctly.

| Operation | Result                                                                                           |
| --------- | ------------------------------------------------------------------------------------------------ |
| Duplicate | A new object with a new identity and the same content.                                           |
| Derive    | A new identity with a declared relationship to the source, such as a variant or a computed view. |
| Export    | A file in another format. The object remains where it was.                                       |

A menu that offers "Save a copy" for a live object is ambiguous: it could mean
duplicate, derive or export. Cabochon menus should use the precise verb.

## Identity in the interface

Identity should be visible where it matters and absent where it does not.

- The inspector shows the object's type, identity and revision in a metadata
  block.
- The title bar shows the object's name.
- The status line may show a short identity suffix when several similar
  objects are open.
- The document body does not print identity unless the document is a technical
  record that requires it.

A user should never need to understand identity to use the environment. They
should be able to rely on it without seeing it.

## Failure and identity

When an object cannot be loaded, its identity must survive. A placeholder that
says "Unavailable" still refers to the original object, so that a later
provider update can restore it. Replacing an unavailable object with an empty
object of the same type destroys the link and is forbidden.

The same rule applies to deletion. Deleting an object that is referenced
elsewhere must warn, and the warning must name the references. An orphaned
placeholder is recoverable; a silently deleted object is not.

## What identity is not

Identity is not authority. Knowing an object's identity does not grant the
right to read or change it. Selector invocation still requires a capability
scoped to the operation, as described in
[Live relationships](08-live-relationships.md) and
[Selection and tools](24-selection-tools.md).

Identity is also not presentation. A beautifully rendered card is not more real
than an inline value. Both are views, and both defer to the object.
