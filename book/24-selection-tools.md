---
title: Selection and tools
part: Interaction
summary: Selection as the address for work, and tools that appear only where they apply.
---

# Selection and tools

Selection is more than a highlight. It is the address that tells a tool what to
act on, what to read and what to change. In Cabochon, a tool is offered because
the selection declares that it can be used, not because a global menu lists
every service in the environment.

## What a selection declares

A selection carries four things.

- **The selected objects**, by identity.
- **Their types and selectors**, which describe what can be addressed within
  them.
- **The capabilities** the application currently holds for those objects.
- **The extent**, such as a range of cells, a span of text or a set of diagram
  elements.

When a command is invoked, it captures a command context: the window, the
document, the selected object identifiers, any local text selection, the extent
and the expected revisions. Asynchronous work revalidates that context at
commit rather than retargeting itself to whatever happens to be selected when
it finishes.

The inspector shows the identity, the presentation, the authority and the
extent. The status line shows a short summary, such as "12 rows selected" or "3
objects · 2 providers", subject to the metadata disclosure policy.

## Selector-based applicability

A tool declares the selectors it can read or invoke. When the selection exposes
a compatible selector and the application holds the required capability, the
tool becomes available at the point of use.

- The formula tool appears for a numeric cell, a currency value or an
  addressable note entity.
- A diagram tool appears for diagram elements, not for prose.
- A currency presentation appears for a currency object, not for a bitmap.

An incompatible selection must not show the tool greyed in a global menu. It
must not show it at all, because a menu of unavailable services teaches the
user that the environment is broken.

## Three kinds of tool

Tools differ in what they promise, and the interface must not give them one
generic result shape.

- A **canvas tool** changes what a pointer gesture does: select, pan, draw,
  paint, erase, sample. It is modal only within its canvas and has a declared
  commit boundary.
- A **read-only inspection** reveals information without changing content. It
  may stay open while the user looks elsewhere.
- A **transactional contextual operation**, such as the formula tool, computes
  a result and commits one object change. It has explicit primary and cancel
  actions and one atomic commit.

The formula tool's **Insert live value** and **Cancel** belong to the
transactional operation. A selection or brush tool does not acquire them merely
because it is also contextual.

## Point of use

A transactional contextual operation appears beside the selection it can act
on: a small popover, a trailing button in the selection's row, or an item in
the selection's context menu.

- The popover is anchored to the selection, not to the pointer.
- It names the sources it will read and the grants it will use.
- It shows the result before the user commits, where the result is cheap to
  compute.
- It offers its declared primary action and **Cancel** as the way out.
- It closes on Escape and returns focus through the declared focus-return
  chain.

A tool that needs more space than a popover uses a pane or a sheet, and the
same rules apply.

## One active tool

An instrument has at most one active canvas tool at a time. The active tool is
shown in the tool strip, named in the status line and reflected in the pointer
cursor.

Each canvas tool declares its commit boundary in the instrument contract. The
boundary is deterministic and identical whether the tool is switched by
pointer, shortcut or focus change.

- A **selection or pan** tool creates no content mutation when its gesture
  ends. It may update the selection or view state.
- A **drawing or painting** tool commits its stroke or shape as one undoable
  transaction when the gesture ends, or cancels it when the gesture is
  abandoned.
- Switching away from a tool with an uncommitted operation applies that tool's
  declared boundary: it commits, cancels or asks, and the rule is the same in
  every case.
- Escape cancels the active tool's pending operation and returns to the select
  tool.
- A tool that cannot complete because the object changed must say so and keep
  the object's last committed state.
- A committed tool session is undoable as one transaction, not as a series of
  invisible steps.

## Selection and document focus

A command acts on the selection even when the document itself does not have
focus, provided the selection belongs to the active window. This rule lets a
user select a range, move to the inspector, adjust a property and return
without losing the selection.

The rule has one exception: when focus is in an editable text field, the text
editing commands — Cut, Copy, Paste, Delete, Select all and Undo — act on that
field's text before they act on the document selection. A command that is
document-scoped says so, and its invocation context names the document.

A selection in an inactive window is remembered but not acted on. Its fill
becomes an outline, as described in [Palette](12-palette.md).

## Multi-selection

- Shift-click extends a selection; Control-click toggles an item.
- A drag on empty canvas draws a marquee; a drag on an object moves it.
- A multi-selection shows its count in the status line and its shared
  properties in the inspector.
- A command that applies to only some selected objects offers a compatible
  subset only as an explicit pre-invocation choice, with the chosen subset
  listed. Once invoked, the edit commits for that whole subset or for none of
  it.
- A command with no compatible object is unavailable, and the reason is
  discoverable without activation.
- A mixed property reads **Mixed** and is not silently normalized.

## Selection extent

The extent must be visible whenever a command could act on more than one thing.
Selection is interaction decoration: it changes the drawn outline, fill or
handles, never the saved appearance of the object.

- Text selection uses the system's text selection colour and shows its handles
  on touch.
- Cell selection uses the selected-cell fill role for the anchor and a 2-unit
  oxide outline for the range.
- Object selection uses a 2-unit oxide outline with 8-unit square corner
  handles. The handles are within the object's visual bounds and do not alter
  its geometry.
- A selection that crosses several objects shows one outline around the group
  and a separate outline around each member.

A compact handle's visible mark may be smaller than the minimum pointer target.
Its effective hit region is expanded within the object's bounds, and where
handles would overlap, the instrument declares a deterministic resolution: a
priority order plus a modifier or keyboard alternative. The final clipped hit
region, not the glyph, is the target that must satisfy the applicable policy.

## Denied selections

A selection may be visible while its content is denied. The outline remains and
the word **Denied** appears without the value. The object's name, identity and
count are shown only when the metadata disclosure policy permits those classes;
otherwise the label is a non-disclosing placeholder. A command that would read
the value is unavailable, and the reason names the capability rather than
blaming the user.

## Testing

A reviewer selects an object, observes which tools appear, invokes one, cancels
it, invokes it again and undoes the result. The reviewer records identity,
committed content, revision and view state separately, using the operation
table in [Object identity](07-object-identity.md):

- cancellation preserves identity and committed content;
- the committed invocation changes the intended content under the same
  identity;
- undo restores the prior content without allocating a new object;
- view-only operations do not change the content revision;
- a stale writer remains detectably stale after an intervening edit and undo.

The test does not require an arithmetic revision increment. Revision values are
opaque.
