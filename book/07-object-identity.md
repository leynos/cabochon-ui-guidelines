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

A revision records a change to an object's content. It is not part of the
identity, and it is not a user-visible version number in the manner of a
document-management system. It is an opaque concurrency token: the interface
compares it for equality and ancestry, and never computes with it or asserts
that it increments by one.

The interface rules are:

- A stale revision must never overwrite a newer one silently. The user sees a
  conflict and chooses.
- Undo restores content, not identity. Undoing an edit must not create a new
  object.
- An object's history may be inspectable, but history is not the default view.

## Operation effects

Identity, committed content, revision and view state are separate effects. The
following table is the reference for every instrument.

| Operation                        | Semantic identity                             | Content and history effect                                     | View and container effect                                            |
| -------------------------------- | --------------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------------- |
| Edit existing content            | Preserved                                     | Commit under the platform revision and transaction policy      | Reflect the accepted revision in authorised presentations            |
| Cancel a draft or tool operation | Preserved                                     | No committed content mutation                                  | Discard or retain the draft according to the declared editing policy |
| Undo committed content           | Preserved                                     | Restore content through the declared undo and revision policy  | Update relevant views without reallocating the object                |
| Change one embed's presentation  | Source identity preserved                     | Source content unchanged                                       | Change the containing document's reference record and history        |
| Zoom, sort or filter a view      | Preserved                                     | Source content unchanged unless a distinct command edits it    | Change the declared view state                                       |
| Duplicate a graph                | New identities in the declared copied closure | Copy content under the documented sharing and remapping policy | Preserve or remap links as declared                                  |
| Export a presentation            | Original identity preserved                   | No source mutation                                             | Produce a declared output with explicitly stated losses              |
| Export a portable bundle         | Included identities preserved                 | No source mutation                                             | Preserve the declared data closure; omit runtime authority           |

Cancelling an edit changes neither committed content nor identity. An edit
keeps identity and commits a new content revision. Undo restores the prior
committed content under the same identity; it is not a second edit that
allocates a new object. Reference repair, sorting, filtering and changing a
category are different operations and are tested separately.

## Presentation identity

A presentation is a way of showing an object. Three things are distinct:

- a **presentation definition**, which has its own identity and describes a
  reusable view;
- a **presentation instance**, which is the placement of an object with one
  definition in one document, including its placement, clipping and scene nodes;
- a **scene or control node**, which is one drawn or interactive rectangle in a
  resolved scene.

A document stores the semantic object identity, the presentation definition
identity and its own presentation-instance record. Reopening restores the
instance, not a rendered copy.

Editing a presentation instance changes the containing document's reference
record and belongs to that document's history. It does not change the source
object, and it does not change a second embed of the same object in the same or
another document. Changing the shared presentation definition is a separate
operation with its own authority and conflict rules.

A presentation that is no longer available falls back to a declared placeholder
and reports the problem; it does not silently substitute a different view.

## Duplicate, derive, export

The operations are distinct and must be labelled distinctly.

| Operation               | Result                                                                                                                                                                                                    |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Duplicate               | A new identity with copied content. By default the target's owned closure is copied and its internal links are remapped; references to independently owned objects remain references to the same objects. |
| Duplicate with contents | A new identity for the whole declared closure, including referenced objects, with every internal link remapped. External references remain external.                                                      |
| Derive                  | A new identity with a declared relationship to the source, such as a variant or a computed view.                                                                                                          |
| Export                  | A file in another format. The object remains where it was.                                                                                                                                                |

A duplicate of a document may contain shared objects, cycles, nested live
relationships and internal links. The command therefore states its closure
before it runs: which objects receive new identities, which links are remapped
and which references stay shared. The default is the document's owned closure;
a reference to an independently owned object is not copied merely because it is
reachable.

An exported file is not a duplicate. Restoring a bundle into an installation
that already knows an identity follows the re-import policy:

- an identical revision is reused;
- an older revision is accepted only through the platform's explicit restore or
  conflict path;
- a divergent revision raises a conflict and never silently overwrites live
  content;
- an explicit duplicate assigns new identities and records the mapping.

The importer never infers sameness from a display suffix and never restores a
runtime grant from a bundle.

A menu that offers "Save a copy" for a live object is ambiguous: it could mean
duplicate, derive or export. Cabochon menus should use the precise verb. Menu
commands and their ellipsis policy are defined once in [Menus](10-menus.md).

## Identity in the interface

Identity should be visible where it matters and absent where it does not.

- The inspector shows the object's type, identity and revision in a metadata
  block.
- The title bar shows the object's name.
- The status line may show a short identity suffix when several similar
  objects are open.
- The document body does not print identity unless the document is a technical
  record that requires it.

A display suffix is a short string derived from the identity, such as `8f3a` in
`obj:8f3a`, chosen for recognition in status lines, inspector metadata, menus
and errors. It is display only: it is not the identity, it is never parsed to
recover one, and it may be regenerated or lengthened when two objects collide.
Changing or regenerating a suffix must not change the identity or break a link.
A command that copies identity always copies the full value.

A user should never need to understand identity to use the environment. They
should be able to rely on it without seeing it.

## Failure and identity

When an object cannot be loaded, its identity must survive. A placeholder that
says "Unavailable" still refers to the original object, so that a later
provider update can restore it. Replacing an unavailable object with an empty
object of the same type destroys the link and is forbidden. Restoring a
recoverable identity and creating a replacement are different actions, and the
recovery command says which it will do.

The same rule applies to deletion. Deleting an object that is referenced
elsewhere must warn. The warning lists the references the runtime knows and the
user may inspect, and says when that assessment may be incomplete. It does not
invent a global list it cannot establish and does not reveal references that
the metadata disclosure policy protects. An orphaned placeholder is
recoverable; a silently deleted object is not.

Identity disclosure is not content disclosure. The inspector, diagnostics,
search results, backlinks and manifests show an identity, name, revision or
count only when the current grant permits that metadata class, as described in
[Live relationships](08-live-relationships.md).

## What identity is not

Identity is not authority. Knowing an object's identity does not grant the
right to read or change it. Selector invocation still requires a capability
scoped to the operation, as described in
[Live relationships](08-live-relationships.md) and
[Selection and tools](24-selection-tools.md).

Identity is also not presentation. A beautifully rendered card is not more real
than an inline value. Both are views, and both defer to the object.
