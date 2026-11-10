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

The inspector shows the identity, the presentation, the authority and the
extent. The status line shows a short summary, such as "12 rows selected" or "3
objects · 2 providers".

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

## Point of use

A contextual tool appears beside the selection it can act on: a small popover,
a trailing button in the selection's row, or an item in the selection's context
menu.

- The popover is anchored to the selection, not to the pointer.
- It names the sources it will read and the grants it will use.
- It shows the result before the user commits, where the result is cheap to
  compute.
- It offers **Insert live value** as a primary action and **Cancel** as the
  way out.
- It closes on Escape and returns focus to the document.

A tool that needs more space than a popover uses a pane or a sheet, and the
same rules apply.

## One active tool

An instrument has at most one active tool at a time. The active tool is shown
in the tool strip, named in the status line and reflected in the pointer cursor.

- Switching tools commits or cancels the current tool's pending operation; it
  never leaves a half-finished edit behind.
- Escape cancels the active tool and returns to the select tool.
- A tool that cannot complete because the object changed must say so and keep
  the object's last committed state.
- A tool session must be undoable as one transaction, not as a series of
  invisible steps.

## Selection and document focus

A command acts on the selection even when the document itself does not have
focus, provided the selection belongs to the active window. This rule lets a
user select a range, move to the inspector, adjust a property and return
without losing the selection.

A selection in an inactive window is remembered but not acted on. Its fill
becomes an outline, as described in [Palette](12-palette.md).

## Multi-selection

- Shift-click extends a selection; Control-click toggles an item.
- A drag on empty canvas draws a marquee; a drag on an object moves it.
- A multi-selection shows its count in the status line and its shared
  properties in the inspector.
- A command that applies to only some selected objects is either disabled with
  a reason or applied to the compatible subset, and the choice is stated before
  it runs.
- A mixed property reads **Mixed** and is not silently normalized.

## Selection extent

The extent must be visible whenever a command could act on more than one thing.

- Text selection uses the system's text selection colour and shows its
  handles on touch.
- Cell selection uses the pine-2 fill for the anchor and a 2-pixel oxide
  outline for the range.
- Object selection uses a 2-pixel oxide outline with 8-pixel square corner
  handles.
- A selection that crosses several objects shows one outline around the group
  and a separate outline around each member.

## Denied selections

A selection may be visible while its content is denied. The outline remains,
the label names the object and the word **Denied** appears without the value. A
command that would read the value is unavailable, and the reason names the
capability rather than blaming the user.

## Testing

A reviewer should be able to select an object, observe which tools appear,
invoke one, cancel it, invoke it again, undo the result and confirm that the
object's identity and revision changed exactly once.
