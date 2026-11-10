---
title: Facet Notes
part: The workspace
figure: fig-22-notes.svg
summary: A note is a document that holds prose, live objects and links without flattening any of them.
---

# Facet Notes

![Facet Notes with a note tree and live embeds.](../figures/fig-22-notes.svg)

Facet Notes is the workspace's writing instrument. Its document is a note: a
sequence of prose blocks, embedded objects and links. The note is the
workspace, and the objects inside it remain themselves.

## Layout

Facet Notes uses a three-pane window.

- A 210-unit note tree on the left, showing the project's notes by folder.
- A flexible document plane in the centre, measuring 60 to 75 characters per
  line at the default width.
- A 220-unit relations panel on the right, showing links from and to the note.

The relations panel is a declared **relations-panel** variant. It inherits the
inspector's row, selection and collapse behaviour but not its 240-unit default,
because it carries link lists rather than property blocks. It is not a second
inspector.

Either side pane may be collapsed, and the layout is remembered per project.
The document keeps its 420-unit minimum.

## The note tree

The tree shows notes and folders, not files. A note's name is its title, and
renaming it does not change its identity.

- Rows are 28 logical units high with 16-unit indentation per depth.
- The selected row uses the selected-fill and selected-text roles.
- A note with an unresolved link carries the oxide broken mark; a note with a
  stale embed carries the amber stale mark. Each mark is paired with a word in
  the row's accessible name.
- The tree's **Add** action creates a note, not a folder, unless the user
  chooses otherwise from its menu.
- Dragging a note moves it in the tree and updates its parent, but never
  breaks an inbound link.

## The document plane

The note's title is a display-italic heading, 24 logical units, editable in
place. Below it, a metadata line records the last update, the word count and
the number of embeds when disclosure permits those classes. Those values are
supplementary metadata and may use the 11-unit metadata role; a value the user
must act on, such as a save failure time, uses the 12-unit operational floor.

Prose uses the 15- or 16-unit body role with a 1.6 line height. Paragraphs are
separated by 16 units. Headings within the note use the section voice at 18 or
20 units. Inline code and object identities use the operational mono role at
the 12-unit floor, because they carry exact, copyable information. Monospace
does not lower the floor.

When the document plane narrows, the measure shortens and the text wraps. The
note does not shrink its type below the user's requested text scale, and it
does not undo an enlargement to make a line fit. If the plane cannot show the
requested scale, the pane collapses or the window reports the feasible width,
as described in [Spacing and metrics](14-spacing-metrics.md).

The note must support:

- headings, paragraphs, lists, quotes and code blocks;
- inline links to other notes and objects;
- embedded objects as blocks, with their own state;
- a source view for the underlying Markdown, reachable from the **View**
  menu.

## Embeds in a note

An embedded object uses the **block** profile by default. It occupies the full
measure of the note and carries:

- a 4-unit state edge on its leading side, in the role of its relationship
  state;
- the object's name in 12-unit interface bold;
- its type, size and identity suffix in the 12-unit operational metadata role;
- a state chip at the trailing edge;
- a compact presentation of its content.

The state edge is the only persistent colour in the document plane. A current
embed uses the pine role, a refreshing embed the teal role, a stale embed the
amber-ink role, and a broken or denied embed the oxide role. The chip carries
the word.

A compact **inline** embed inside a text run keeps the state mark, the
accessible name and a keyboard-reachable inspection route; it does not attempt
to contain the block's full furniture. A **thumbnail** placement follows the
thumbnail rules in [Embeds](32-embeds.md). All three profiles share the same
identity and disclosure rules.

Selecting an embed shows a 2-unit oxide outline and a small action bar with
**Open**, **Change presentation** and **Inspect**. The action bar must not
obscure the object's content.

## Links and relations

A link records an object, not a file path. It survives a rename, a move and an
export.

- An internal link is drawn in the pine role with a dotted underline.
- A link to a missing object is drawn in the oxide role with a dotted underline
  and offers **Restore**, **Rebind** or **Remove reference**, named by their
  identity effect. A general **Create** does not silently replace the missing
  identity.
- The relations panel lists inbound and outbound links by name, grouped under
  **Linked from** and **Links to**, subject to the metadata disclosure policy.
- Backlinks are computed, not stored in the note's text, so that they cannot
  drift. A protected backlink is omitted rather than shown as a count.

## Saving

Facet Notes saves continuously and visibly. The title bar shows a modified
bullet while a change is pending, and the status line records the last save
time. A save failure keeps the document open, marks it modified, preserves the
draft and offers a retry.

The note distinguishes three states: the committed content, the unsaved draft
and the durable save. A pending save does not make the draft committed, and a
failed save does not discard it.

The note must never close with unsaved changes without a dialog that names the
note and offers **Save**, **Discard** and **Cancel**. **Cancel** is the safe
default, so that an accidental Return keeps the note open; **Save** remains the
primary action.

If the close follows a failed save, the dialog offers **Keep open**, **Export
copy** and **Discard**. **Keep open** is the default; **Export copy** is the
primary action, because it is the only action that both preserves the work and
lets the user leave. None of the three pretends that the save can succeed. This
recovery flow is the named safe-action exception in [Dialogs](22-dialogs.md):
**Keep open** is the action that preserves work, and it is the default, even
though it is not the affirmative button.

## What the note is not

- A file that contains rendered copies of its embeds.
- A rich-text format that hides its source.
- A place where an object can be converted to text by a single command.
- A database view. Queries belong to the project window or the Enfilade Table.

## Testing

A reviewer should rename a note, move it to another folder, reopen the project,
and confirm that every inbound link still resolves and every embed keeps its
identity and presentation. Reopening revalidates each live state against the
current source revision, provider availability and authority; it preserves a
cached **Current** label only as a label, never as a truth assertion. A note
whose source changed, provider disappeared or grant was revoked shows the
appropriate new state.
