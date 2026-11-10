---
title: Projects
part: The workspace
figure: fig-28-project.svg
summary: A working context of documents, objects, links and views, which owns none of them.
---

# Projects

![Project window with tree, documents and identity panel.](../figures/fig-28-project.svg)

A project is a working context. It gathers documents, objects, links, tools and
saved views so that a person can return to a piece of work. It does not own the
objects inside it, and it does not define their identity.

## The project window

The project window has three regions.

- A 260-unit project tree on the left, showing notes, data and figures.
- A flexible document list in the centre, showing the project's documents
  with their identities, details and states.
- A 280-unit identity panel on the right, explaining the selected document.

The project tree and identity panel use wider defaults than the standard panes
because they carry identity metadata; both remain above the 210-unit navigator
and 240-unit inspector minimums. They are declared variants of those roles and
inherit their row, selection and collapse behaviour. The window's status line
reports the number of documents, objects and links when the disclosure policy
permits those counts. The identity panel is read-only except for renaming and
pinning; editing belongs to the document's own instrument.

## The tree

The tree shows a working arrangement, not necessarily a directory listing. A
project may present folders, virtual collections and pinned items in one tree.

- Rows are 28 logical units high with 16-unit indentation.
- The selected row uses the selected-fill and selected-text roles.
- A document with a stale relationship carries the amber state mark; an
  unresolved link carries the oxide broken mark. Each dot is paired with a word
  in the row's accessible name and in the status line, so colour is not the
  only carrier.
- Dragging changes the working arrangement without changing object identity.
- A folder is a view over objects, not a container that owns them.

A project may be stored as a file or as a directory. The interface must not
imply that moving a document in the tree moves a file on disk unless the
project is explicitly file-backed.

## The document list

Each document row shows:

- its name, in 12-unit interface bold;
- its identity, in the 12-unit operational metadata role;
- a short detail, such as "3 embeds · updated 14:02", when disclosure permits;
- its live state chip.

A row opens the document in its instrument. A secondary action opens it in a
new window, reveals it in the tree or copies its identity. The list sorts by
name, update time or state; the sort is remembered per project. Identity,
detail and count are metadata classes and are withheld when the current grant
protects them.

## Identity and rename

The identity panel explains the difference between a document's name and its
identity.

- **Document** shows the object identity, such as `note:transition`.
- **File** shows the path, when the project is file-backed.
- **Revision** shows the current revision.
- A rename changes the name and, for a file-backed project, the path. It does
  not change the identity or break inbound links.

The panel must state this in one sentence, because it is the fact users most
often doubt. The figure's example renames a note into an archive folder and
keeps both its identity and its links.

## Views

A project remembers views, not just documents.

- Open documents and their window positions.
- Collapsed panes and their widths.
- The project tree's expansion and selection.
- The document list's sort and filter.
- Recent views, listed in the identity panel.

A view is a presentation of the working context. It must not be confused with a
saved document, and it must not be exported as one.

## Pinning

Pinning keeps an object or a view at the top of the project tree or the recent
list. A pinned item is a convenience, not a capability; unpinning never removes
the object.

## Removing and deleting

Removing a document from a project removes the working reference, not the
object. Deleting an object is a separate, destructive action with a dialog that
names the projects and notes the runtime knows and the user may inspect. It
says when the assessment may be incomplete and does not enumerate protected
references.

The project must not offer a single command that both removes and deletes
without saying which it will do.

## Empty projects

An empty project shows its name, a short explanation and three ways to begin:
**New note**, **Import**, **Open recent**. It does not show a grid of marketing
tiles, and it does not hide the menu bar.

## Portability

A project exports as a native bundle containing its documents, object
references, schemas, payloads, internal links and views. The bundle declares
its transitive data closure: which objects are included, which external
references remain references, and which unknown fields or opaque payload bytes
are preserved. It must be readable by another Cabochon installation without the
original application that created each object.

The bundle never contains capability grants, host secrets or machine-local
authorisation handles. On import the runtime reacquires authority; it does not
restore an old **Granted** badge as proof of access.

An object whose provider is absent exports as an opaque object only when its
payload bytes are actually present in the declared closure. A reference with no
payload is not an Opaque success; the bundle reports it as an external
reference or as a loss. The [embeds](32-embeds.md) chapter describes the
reference record, the stored envelope and the portable bundle.

Importing a bundle that carries an identity the installation already knows
follows the re-import policy in [Object identity](07-object-identity.md):
identical revisions are reused, older revisions require an explicit restore,
divergent revisions raise a conflict, and an explicit duplicate assigns new
identities and records the mapping. Importing the same bundle twice is
idempotent under the chosen policy.

A project bundle is a native bundle, not a conformance bundle. The
[output chapter](37-output-parity.md) defines the three export profiles.

## What a project is not

- A file manager. The host provides file access through its portal.
- A permissions boundary. Capabilities are granted per operation, not per
  project.
- An owner of objects. Deleting a project must not delete objects that are
  referenced elsewhere without an explicit, separate choice.
