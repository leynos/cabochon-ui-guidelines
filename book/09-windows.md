---
title: Windows
part: Structure
figure: fig-13-window.svg
summary: Window anatomy, the measured bands and the rules for size, state and host adaptation.
---

# Windows

![Window anatomy with labelled metrics.](../figures/fig-13-window.svg)

A Cabochon window is assembled from a fixed set of horizontal bands. The bands
give every application the same rhythm and make a window recognisable before
its contents are read.

## The bands

The metrics below are production values in logical units at 100 per cent
interface scale.

| Band        | Height | Contents                                           |
| ----------- | ------ | -------------------------------------------------- |
| Masthead    | 44 lu  | Instrument name and primary command; optional.     |
| Title bar   | 31 lu  | Title, object state, window controls.              |
| Menu bar    | 29 lu  | Top-level menus, right-aligned status if required. |
| Tool strip  | 30 lu  | Frequent commands, grouped and separated.          |
| Document    | Fill   | The document plane and its panes.                  |
| Status line | 26 lu  | Message, progress and state chip.                  |

The bands are stacked without gaps. A one-unit rule in the decorative line role
separates the window from its work surface and the document plane from the
chrome. The status line grows to 28 units when it carries an action, as
described in [Toolbars and status](11-toolbars-status.md).

## Title bar

The title bar carries the document's name at its leading edge. It may also
carry a small state chip when the document has a live relationship that is not
**Current**. The chip sits between the title and the window controls and must
not displace them.

Rules for the title bar:

- The title must be the document's name, not the application's name. When no
  document is open, it may name the instrument.
- The title must truncate in the middle, preserving the beginning and the
  extension, rather than at the end.
- Window controls are minimize, maximize and close, in that order, with a
  16-unit glyph inside a 28-unit target inset one unit from the band, when the
  application owns the window controls.
- A modified document appends a single bullet, not the word "modified".
- Double-clicking the title bar must perform the host's configured action.

The title bar described here is the application's internal **document header**.
It is not the same object as a host-drawn title bar, and the two may both show
the document's name. Which one carries the window controls is decided by the
decoration profile, not by the header.

## Menu bar

The menu bar follows the ordering rules in [Menus](10-menus.md). It must remain
visible at every window size; an application must not collapse its menus into a
hamburger button. When the window is too narrow, whole menus move into a final
**More** menu in their original order. Individual items are never plucked out
of their menus, because a menu's grouping carries meaning.

## Tool strip

The tool strip is optional. It holds commands that the user invokes repeatedly
and that benefit from a visible, one-click target. It is not a place for every
command, and it must not grow beyond one row.

A tool strip button is 30 units square with a 16-unit glyph. Related buttons
are grouped with an 8-unit gap and separated from the next group by a one-unit
vertical rule with 8 units of space on each side. The strip must carry a text
label for any command whose icon is not universally understood.

## Document area

The document area holds the instrument's panes. It must not be inset by a frame
of its own; the window's keyline is the only border. A document that needs a
visible page, such as a print layout, draws that page inside the area with its
own margin and shadow.

## Status line

The status line is always present in a document window. Its zones, their
contents and their rules are owned by
[Toolbars and status](11-toolbars-status.md); this chapter does not restate
them. A window that places a status line must use that layout.

## Four independent properties

A window has four properties that vary independently. They are not one state
list, and an instrument must not derive one from another.

| Property   | Values                                             |
| ---------- | -------------------------------------------------- |
| Activation | Active, Inactive                                   |
| Modality   | None, Document, Application                        |
| Attachment | Primary, Detached, Sheet, Host portal              |
| Role       | Document, Tool, Inspector, Palette, Utility, Alert |

- **Activation** says only which window receives input. An inactive window
  keeps readable content and keeps its selection visible as an outline.
- **Modality** says which other windows the window blocks while it is open. It
  is declared when the window is created and cannot be inferred from its
  appearance.
- **Attachment** says what the window is attached to. A detached inspector is
  a window in its own right but keeps the layout it was torn from; a sheet is
  attached to one window; a host portal is presented by the host.
- **Role** says what the window is for, and therefore which furniture is
  permitted. A **Tool** window keeps its tool options and no document title; a
  **Utility** window carries no live document relationship of its own.

Modality, attachment and role are reported in the window's accessible name and
in the instrument's window list. A window that is inactive is not thereby
modal, and a modal window is not thereby detached.

An inactive window must not dim its content below readable contrast. The
distinction between active and inactive is carried by the document header, the
window-control strip and the focus ring, not by a veil over the document.

## Permitted window roles

Cabochon does not forbid secondary windows. It forbids secondary windows that
duplicate the document's own plane without declaring a role.

| Role      | May contain                                          | Furniture permitted     |
| --------- | ---------------------------------------------------- | ----------------------- |
| Document  | A document and its panes                             | Full band set           |
| Tool      | Options for the active canvas tool                   | Head, options, close    |
| Inspector | Object properties for one or more objects            | Head, scrolling content |
| Palette   | Commands, search, or a colour set                    | Field, list             |
| Utility   | Transient environment work, such as a transfer queue | Head, list, status      |
| Alert     | One message and its responses                        | Message, buttons        |

Each role has a maximum of one open window per document, except **Utility** and
**Alert**. Opening a second window of the same role for the same document
focuses the existing one or replaces its content, and says which it did.

## Size and position

- A window requests its initial size from its layout profile, as defined in
  [Spacing and metrics](14-spacing-metrics.md). At the supported floor of 512
  by 384 logical units the compact profile applies.
- The minimum size must be declared per instrument, and must never be smaller
  than the sum of its pane minimums plus the chrome. The compact profile is the
  only layout that may go below that sum, and it is declared per instrument.
- A window that receives less than its requested width shows the feasible
  width, not a squeezed copy of the requested layout.
- The environment restores the last size and position per document, not per
  application.
- A window restored onto a display that no longer exists must be moved onto
  the nearest available display rather than opened off-screen.
- Persisted geometry is clamped to the requested-width interval when it is
  restored, so a saved size that exceeds the current display opens at the
  largest feasible width and says so in the status line once.

## Decoration profiles

Exactly one profile is active for a window, and it names the owner of each
decorative element. An instrument must not mix ownership within one window.

| Profile          | Window controls | Move and resize | Shadow      | Document header |
| ---------------- | --------------- | --------------- | ----------- | --------------- |
| Server-decorated | Host            | Host            | Host        | Hidden          |
| Client-decorated | Application     | Application     | Application | Drawn           |
| Undecorated      | Application     | Application     | Application | Drawn           |

- **Server-decorated.** The host draws the frame and the controls. The
  application hides its own window controls and its document header; the
  document's name is still available through the window's accessible name and
  the document's own pane head.
- **Client-decorated.** The application draws the document header and the
  window controls, and is responsible for move and resize gestures and for its
  own shadow. This is the default when the host offers no server decoration.
- **Undecorated.** The application draws the document header and controls but
  presents no shadow, for example when the window is embedded in another
  surface. It must not leave the user without a way to move or close the window.

The document header and a host title bar are different objects. A
client-decorated window has a document header and no host title bar; a
server-decorated window has a host title bar and no document header. If a host
insists on drawing a title bar for a client-decorated window, the application
hides its document header rather than show two. Two titles for one document is
a configuration error, and the instrument reports it rather than negotiating
silently.

The test is observable: under a server-decorated host, under a client-decorated
host, and undecorated, each window shows exactly one set of window controls and
at most one title, and no window has two close buttons.
