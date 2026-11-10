---
title: Menus
part: Structure
figure: fig-14-menus.svg
summary: Menu order, wording, shortcuts, state marks and the context-menu subset.
---

# Menus

![A menu bar with an open File menu.](../figures/fig-14-menus.svg)

The menu bar is Cabochon's complete command surface. Every command that changes
a document must be reachable from it. The command palette and the tool strip
are accelerators, not substitutes.

## Order

Menus appear in a fixed order, with instrument-specific menus inserted before
**Window**.

1. **File** — new, open, save, export, print, close.
2. **Edit** — undo, redo, cut, copy, paste, selection, find.
3. **View** — zoom, panes, presentation, appearance.
4. *Instrument menus* — **Insert**, **Format**, **Data**, **Page**, **Object**
   or similar, in the order the instrument's work flows.
5. **Window** — window list, new window, detached panes.
6. **Help** — documentation, keyboard reference, about, diagnostics.

The list gives each menu's internal order and its usual contents. An
application omits the items and menus it does not implement: one with no
editable document omits **Edit**, and one with a single window omits
**Window**. A menu that would be empty is never drawn.

An instrument must not rename **File** or **Edit**, and must not move **Help**
away from the end. A user who learns one Cabochon application should find the
same anchors in the next.

## Wording

Menu items are verb phrases in sentence case: **Save a copy**, **Insert
reference**, **Refresh now**. A noun-only item is acceptable only when it names
a toggle or a property, such as **Rulers** or **Dark appearance**.

Rules for wording:

- Use the same verb everywhere for the same operation. If the toolbar says
  **Export**, the menu says **Export**.
- Use an ellipsis when the command opens a dialog that requires more input.
- Do not use an ellipsis for a command that acts immediately.
- Do not add "…" to a command that opens a sheet the user can cancel without
  consequence; the ellipsis marks a request for information, not a warning.
- Prefer the specific verb to the generic one: **Insert reference** beats
  **Insert**, and **Export plate** beats **Export**.

## Shortcuts

A shortcut is displayed right-aligned in the menu item, using the platform's
modifier names. Cabochon uses Control as the primary modifier on Linux, with
Alt for menu access and Shift for extension.

- A shortcut must be discoverable from the menu; the command palette displays
  the same string.
- A shortcut must remain stable across applications for the same operation:
  Control-S saves, Control-Z undoes, Control-F finds.
- An application-specific shortcut must not shadow a platform or accessibility
  shortcut.
- Single-letter shortcuts without a modifier are reserved for tools inside a
  canvas, and must be shown in the tool's tooltip.

## State marks

A menu item may show one of three marks.

- A **check** marks a toggle that is on.
- A **bullet** marks the selected option in a radio group.
- A **dash** marks a mixed state, such as a selection whose members disagree.

The mark occupies a 16-pixel column at the left of the item. Icons do not
appear in menus; the mark column is reserved for state, and mixing icons with
checks makes the state unreadable.

## Grouping and order within a menu

Items are grouped by purpose, with a one-pixel separator between groups. The
usual order is: create and open; save and export; share and print; destructive
items last. A destructive item is separated from the group above it and is
never placed next to a frequently used command.

Disablement is for a command that applies to this object but is temporarily
unavailable, such as **Paste** with an empty clipboard or **Undo** at the start
of history. It remains visible with a reason available on hover and to
accessibility clients.

Absence is for a command that cannot apply to this object at all, such as
**Format cell** on a note. A command that can never act on the current object
must not be shown greyed; it is left out of the menu, the tool strip and the
context menu. The distinction is between "not now" and "not here".

## Context menus

A context menu is a subset of the menu bar, not a parallel command system. It
may contain only commands that apply to the object under the pointer, plus
**Inspect** and **Copy identity** where relevant.

Context menus must:

- open on the keyboard's context-menu key as well as the secondary button;
- close on Escape without changing the document;
- place the most specific command first;
- never contain a command that has no effect on the current selection.

## Menu behaviour

- Pressing Alt focuses the menu bar. Arrow keys move between menus; Down opens
  one.
- Typing a letter jumps to the next item beginning with that letter.
- Escape closes the open menu and returns focus to the document.
- Opening a menu must not change the selection.
- A menu that would extend beyond the window flips or scrolls rather than
  clipping its last items.
- Menus must be reachable and operable with a screen reader, including their
  state marks and shortcuts.

## The More menu

When the window is too narrow for the full menu bar, whole menus move into a
final **More** menu in their original order. Individual items must not be
plucked out of their menus, because a menu's grouping carries meaning. The
**More** menu uses the same typography and marks as the menu bar.
