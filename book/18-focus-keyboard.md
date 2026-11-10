---
title: Focus and keyboard
part: Interaction
figure: fig-20-focus.svg
summary: A visible focus ring, a reading-order tab path and the keys that must work everywhere.
---

# Focus and keyboard

![Focus ring, tab order and keyboard map.](../figures/fig-20-focus.svg)

The keyboard must reach everything. A Cabochon surface that can only be
operated with a pointer is incomplete, and a focus ring that disappears to make
a screenshot look calmer is a defect.

## The focus ring

- Colour: oxide `#8A302F`.
- Width: 3 pixels.
- Offset: 3 pixels outside the control's edge.
- Shape: follows the control's shape, square for a square control.
- Visibility: drawn for every focus source, including a pointer click.

The ring is drawn outside the control so that it never changes the layout. It
must remain visible on paper, high, control and dark grounds. Only one control
in a window carries the ring.

## Tab order

Focus moves in reading order: left to right, top to bottom within the writing
direction of the interface.

A typical document window orders its stops as follows.

1. The navigator tree.
2. The document body.
3. The first embed or object in the document.
4. The inspector fields.
5. The status line actions.

A composite control is one tab stop. Arrow keys move within it: between the
items of a list, the cells of a grid, the options of a radio group or the tabs
of a tab bar. Tab moves out of the composite to the next stop.

## Keys that must work

| Key             | Action                                   |
| --------------- | ---------------------------------------- |
| Tab / Shift+Tab | Move between groups and controls         |
| Arrow keys      | Move within a tree, list or grid         |
| Enter           | Activate the focused control             |
| Space           | Toggle a checkbox or press a button      |
| Escape          | Dismiss a menu, popover, sheet or dialog |
| F6              | Cycle between panes                      |
| F1              | Open help for the focused object         |
| Control+Q       | Quit the application                     |

Instruments may add keys, but they may not rebind these. A shortcut must appear
beside its command in the menu and be searchable in the command palette; a
shortcut that exists only in documentation is a secret.

## Focus memory

A window that loses focus remembers its last focused control. When the window
returns, that control receives the ring again. The remembered control is shown
with a muted ring while the window is inactive, so that the user can see where
focus will land.

A pane that is collapsed and reopened restores the focus of its last active
control, provided that control still exists. If it does not, focus moves to the
pane head.

## Trapping and escaping

Focus is trapped only in a modal dialog. Every other surface must allow the
user to leave with Tab, Shift+Tab or Escape.

A popover that contains a text field must close on Escape without submitting. A
command palette must close on Escape and return focus to the control that
opened it. A modal dialog must return focus to the control that opened it when
it closes, whether the user confirmed or cancelled.

## Access keys

Menu labels may carry an access key, shown with an underline. Access keys are
activated with Alt and are localized with the interface. They are a convenience
for pointer-averse users, not a substitute for the full keyboard path.

## Focus and selection

Focus and selection are different. Focus says where the keyboard will act;
selection says what the next command will affect. A focused row is not
necessarily selected, and a selected row may be outside the focus.

The interface must show both. A selected row in an inactive pane keeps its
fill; a focused row in an active pane carries the ring. A command that acts on
the selection must remain enabled while the document has focus, even if the
selection was made in another pane.

## Testing

A reviewer can test keyboard access without a pointer: open the application,
press Tab repeatedly, and confirm that every control is reachable, that the
ring is always visible, that no control traps focus outside a modal dialog, and
that Escape returns the user to the document.
