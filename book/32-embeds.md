---
title: Embeds
part: The workspace
figure: fig-29-embed.svg
summary: The reference record, the provider and the four ways resolution can end.
---

# Embeds

![Embed envelope and provider.](../figures/fig-29-embed.svg)

An embed is a promise. The document owns a presentation; the object keeps its
identity, its provider and its state. The promise holds when the provider is
present, and it must remain intelligible when the provider is not.

## Three records, not one

The word **envelope** covers three different records. Keeping them apart is
what makes an embed portable without making it leak authority.

- A **reference record** is what the containing document stores: the object's
  identity, the presentation definition chosen for this placement, the provider
  hint, and the document-owned placement and revision.
- A **stored object envelope** is what the runtime keeps for the object itself:
  its type and schema metadata, its payload location, its revisions and its
  relationships. The provider validates the payload and produces revisions.
- A **portable bundle** is an export: the declared transitive closure of
  reference records, object envelopes, schemas, payloads and internal links,
  with unknown fields and opaque payload bytes preserved where the encoding
  permits.

A reference record is not a copy of the object. A portable bundle is not a
backup of the runtime's authority. Capability grants, host secrets and
machine-local authorisation handles never travel in a bundle. On import the
runtime reacquires authority; it does not restore an old **Granted** badge as
proof of access.

The document does not store a rendered copy as its primary content. A cached
rendering may exist for speed, but it is a cache, clearly replaceable from the
object.

## The provider

The provider owns the payload, its validation and its revisions. It resolves an
identity to the data the presentation needs. The runtime's capability broker
owns authority: it issues, scopes, delegates and revokes the grants an embed
needs. A provider is untrusted until the broker grants the relevant capability,
and a provider response cannot widen a grant. The document asks the runtime to
resolve the embed; it does not reach the provider directly.

The interface consequence is that an embed can fail independently of the
document. The document remains open, printable and exportable while one embed
is unavailable, subject to the authorisation rules below.

## Resolution, authority and cache are independent

Resolution asks whether this machine can turn the reference into a
presentation. It does not ask whether the payload may be disclosed, and it does
not ask whether an authorised cached value exists. Those are three independent
facts.

| Resolution  | Meaning                                        | What remains                             | Mark           |
| ----------- | ---------------------------------------------- | ---------------------------------------- | -------------- |
| Resolved    | A provider loaded the object                   | The presentation and its live state      | Filled dot     |
| Opaque      | The bytes are intact; no provider is installed | An authorised preview or a placeholder   | Hatched square |
| Unavailable | The provider exists but cannot load the object | Name or placeholder, identity, retry     | Dashed square  |
| Malformed   | The provider rejected the payload              | Name or placeholder, identity, diagnosis | Crossed square |

Each resolution state carries its own shape mark as well as its word, so the
four remain distinguishable without colour.

Only a **Resolved** embed carries one of the five live states from
[Live relationships](08-live-relationships.md). An Opaque, Unavailable or
Malformed embed has no live state and shows its resolution state instead. Stale
and Denied are properties of a resolved relationship, not alternative
resolution states.

Removing, crashing or reinstalling a provider changes resolution and
availability. It does not change whether the payload may be disclosed. An
unresolved embed that is not authorised shows a non-disclosing placeholder and
offers no preview, no **Export original**, no clipboard copy and no diagnostic
bytes. **Export original** is offered only when the current grant permits
exporting the original bytes.

Opaque is not a failure of the document. When export is authorised, it is a
promise kept: the content is preserved even though this machine cannot render
it. The placeholder must say so and offer **Export original**. When export is
not authorised, the placeholder says that the content exists but may not be
shown.

## Inserting an embed

Insertion is one atomic action with one undo step. The user chooses an object
from the project, the clipboard or a provider's picker, chooses one of the
available presentations in the same surface, and confirms once. The runtime
creates the reference record, resolves the presentation and establishes the
delegated grant, or none of these happens. The embed appears with its
resolution state and, once resolved, its live state; the document is marked
modified.

If the provider cannot resolve the object, the embed is still inserted in its
resolution state. The reference is never silently discarded because a provider
is missing.

The flow must not insert a rendered image by default. If the user wants an
image, **Export** and **Insert image** are separate commands.

## Presentations

A presentation definition is chosen per embed. Changing it changes the
containing document's reference record, not the source object, and is undoable
in that document's history. It does not change a second embed of the same
object, and it does not change the source object's content revision.

- A presentation that is unavailable is greyed with a reason.
- A presentation that would exceed the document's width offers a compact
  variant rather than clipping.
- A presentation may be changed from the embed's action bar or the
  inspector.
- The document remembers the presentation across reopen and export.

Each placement is a presentation instance with its own scene and control nodes.
Two instances of one object share the semantic identity but not their
placement, clipping or interaction identifiers. A hit or accessibility result
identifies the instance and maps to the semantic object through the integration
boundary.

## Form factors

An embed has one of three presentation profiles. All three carry the same
semantic guarantees and the same disclosure rules; they differ in how much
furniture fits.

| Profile   | Use                                       | Furniture                                                    |
| --------- | ----------------------------------------- | ------------------------------------------------------------ |
| Block     | A full-measure object in a note or report | State edge, name, metadata line, state chip, action bar      |
| Inline    | A short reference inside a text run       | State mark, accessible name, inspection route                |
| Thumbnail | A list, preview or page placement         | State mark when large enough, list-row state, manifest entry |

A block is the default for notes and reports. An inline mark cannot contain the
block's furniture; it keeps the state mark, the object's accessible name and a
keyboard-reachable inspection route that exposes the name, identity, state and
actions in a popover or the inspector. A thumbnail at least 48 units on its
shorter side carries a shape mark; a smaller thumbnail carries the state in its
list row and in the manifest.

An inspection opened from an inline mark or a thumbnail is a **pinned read-only
inspection** in the sense of [Selection and tools](24-selection-tools.md). It
does not dismiss the surface that opened it, it keeps the captured context
visible on return, and it closes on Escape without committing. Opening it does
not change the document selection.

The host application must not add its own private chrome around the embed. A
dataframe embedded in a note and a dataframe embedded in a report should be
recognisably the same object in the same envelope.

## Printing and export

An embed prints through its chosen presentation, using the shared Burin target.
Every artefact that includes the embed is produced from one accepted snapshot
with one authorised scene, as described in
[Output parity](37-output-parity.md). If the provider is unavailable at print
time, the last cached presentation may print only when current authority
permits that use; it carries a visible state mark, and the preflight report
names the unresolved embeds.

The export manifest records each embed's identity, provider, presentation,
accepted revision and state. It must not claim that an unresolved embed was
rendered from live data, and it must not name a protected object whose metadata
the disclosure policy withholds.

## Removing an embed

Removing an embed removes the reference from the document. It does not delete
the object. The confirmation, if any, says exactly that.

Deleting the object is a separate action. If the object is referenced
elsewhere, the deletion dialog lists the references the runtime knows and the
user may inspect, and requires an explicit choice. It does not claim a complete
global list when the runtime cannot establish one; it says that the assessment
may be incomplete.

## Missing and unavailable links

An unavailable reference offers recovery actions whose names state their
identity effect:

- **Restore** reconnects the original identity when the runtime can recover it.
- **Rebind** links the reference to an explicitly chosen existing object and
  records the new identity.
- **Remove reference** removes the reference and leaves the object untouched.

A general **Create** action must not silently replace an unavailable identity
with a new object. If creating a replacement is offered, it is labelled as such
and records the new identity and the rebinding.

On reopen, the document preserves the reference, presentation and dependencies
and revalidates the live status. It does not preserve a cached **Current** or
**Granted** label as a truth assertion.

## Accessibility

An embed exposes semantic nodes for:

- its accessible name, from the object's name when the disclosure policy
  permits, or a non-disclosing label otherwise;
- its role, from the object's type;
- its state, as a described status;
- its content, through the presentation's semantic projection;
- an action to open the object and an action to inspect it.

Accessibility is mandatory for supported content. Where a provider cannot
supply a semantic projection, the embed exposes a bounded fallback: its name or
placeholder, its type, its state, a plain-language description of what is
unavailable and the actions that remain. Raw source may be an additional view;
it is not the only successful accessibility path.

A denied embed must not expose the protected value, its protected metadata, a
count or a revision through an accessible name or description.

## What an embed is not

- A screenshot.
- A copy of the object's data.
- A link that breaks when a file moves.
- A reason to close the document when a provider fails.
- A promise that can be silently converted into a picture.
