---
title: hello-window
part: The studio and the contracts
figure: fig-27-hello-window.svg
summary: The smallest application that proves the whole contract, complete on purpose.
---

# hello-window

![hello-window reference application.](../figures/fig-27-hello-window.svg)

`hello-window` is the smallest application that proves the Cabochon application
contract. It is small on purpose and complete on purpose: every requirement the
environment makes of an application is present, and nothing else is.

It is not a demo. It is the program that fails loudly when a contract regresses.

## The window

`hello-window` has one window, three menus and one fixed document.

- **File** contains **Export**, **Print** and **Quit**.
- **View** contains **Command palette**, **Zoom** and **Appearance**.
- **Help** contains **About** and **Diagnostics**.
- The document plane holds a greeting, a short explanation and two buttons:
  **Export** as the primary action and **About** as the secondary.
- The status line reports the document and the last export time.

The document is read-only and there is only one window, so the menu bar omits
**Edit** and **Window**: every command that would live there, such as **Undo**,
**Cut** or **Copy**, has nothing to act on. It also omits **New**, **Open** and
**Save**, which have nothing to act on either. Each omission is recorded here
as a deliberate fixture-surface exemption, so that the reference application is
not mistaken for a contract violation, and so that a reviewer can tell an
applicability rule from a hard-coded command list.

`hello-window` does **not** omit **Print**. The fixed document is printable,
and the print target is proved both by the export bundle and by the command,
which opens the print surface with its declared intent and reports the result.
The earlier exemption would have implied that printable content could be
declared unprintable, and that is not a contract the environment can test.

The **Command palette** command is present because the palette is a universal
command surface. Its absence from a menu would make it undiscoverable by a user
who does not know Control+K. **Print** and **Export** are distinct records:
**Print** opens the print surface, and **Export** writes the file or bundle the
user asks for. Neither stands in for the other.

Every menu, string, icon and shortcut is loaded from Escutcheon resources. The
application must not hard-code a menu or a label. Changing the resource bundle
must change the interface without recompiling the application.

## What it proves

The reference application exercises five contracts.

1. **Resources.** Menus, strings, icons and shortcuts load from Escutcheon,
   including a pseudo-localized bundle.
2. **Scene.** One Lapidary scene describes the document, its text, its
   controls, their scene-node identities and their hit regions.
3. **Output.** Burin renders that scene to display, PDF, print, raster,
   thumbnail, clipboard, accessibility, hit-testing and manifest targets.
4. **Access.** Every control has a role, a name, a state and a position in the
   focus order.
5. **Locale.** The application runs under `en-XA` and `ar-XB` without layout
   breaks, clipped labels or reversed reading order.

A contract test that omits any of these is incomplete, because each one is a
promise the rest of the environment depends on.

## The export bundle

**Export** writes a bundle with eight artefacts:

| Artefact             | Content                                      |
| -------------------- | -------------------------------------------- |
| `content.pdf`        | Screen-oriented vector output                |
| `content-print.pdf`  | Print-oriented output with intent and bleed  |
| `content.png`        | Raster at the declared scale                 |
| `thumbnail.png`      | Small raster for lists and previews          |
| `accessibility.json` | Roles, names, states and bounds              |
| `clipboard/`         | Text and geometry for the clipboard          |
| `hit-map.json`       | Hit regions keyed by scene node              |
| `export.json`        | Manifest of intents, tolerances and versions |

All eight come from the same scene. Geometry, text placement, clipping and
metadata must agree within the tolerances in
[Output parity](37-output-parity.md). The accessibility and hit-map outputs
must describe the same nodes that were drawn.

The eight artefacts form a **conformance bundle**, not the shape of every user
export. They are produced by the review command that proves the contract, and
they all read one accepted snapshot: the scene revision, the presentation
intents, the authority decision and the renderer version. A user who exports
one PNG or one PDF receives that file and its manifest entry, not the other
seven artefacts. The conformance bundle is staged and published as a unit, so
an interrupted review never pairs new content with an old manifest.

## Identity in a substrate-only scene

`hello-window` proves that the substrate works without the semantic plane. It
therefore distinguishes four identifiers that other chapters also use.

- **Semantic object identity.** An Enfilade object such as `note:transition`.
  `hello-window` has none.
- **Presentation definition.** A reusable description of how an object is
  drawn. `hello-window` has none.
- **Presentation instance.** One placement of a definition in a scene. The
  greeting, the explanation and the two buttons are instances.
- **Scene or control node.** The Lapidary node that carries geometry, hit
  region and accessible role. Every visible element is one.

A hit result identifies a scene node and may name the presentation instance and
the semantic object through the integration boundary. It must not require a
semantic revision or a capability grant for a rectangle or a button. Two
instances of one semantic object therefore return distinct instances with a
shared optional semantic reference.

The manifest records which identity fields apply to the scene. A substrate-only
scene carries scene and node identifiers, instance identifiers and the scene
revision. Semantic object identities, object revisions and authority references
appear only when the Enfilade bridge supplies them, and their absence is
declared rather than inferred. An optional semantic annotation survives a scene
round trip without ever becoming rendering authority.

## What it must not do

- Draw directly to the screen outside Lapidary.
- Build a PDF through a second layout path.
- Hard-code a string that belongs in a resource.
- Omit the status line, the menu bar or the accessibility tree because the
  application is small.
- Require an Enfilade provider, a semantic revision or a capability grant to
  draw a rectangle or a button.
- Add features that the contract does not require. The point of the
  application is that its surface is entirely explained by the contract.

## Using it as a review instrument

A reviewer can compare a new application with `hello-window` and ask:

- Does the new application load its menus from resources?
- Does it render through a Lapidary scene, and can that scene be extracted?
- Does its export bundle contain the same eight artefacts?
- Does its accessibility tree describe every control?
- Does it survive `en-XA` and `ar-XB`?

A negative answer is a contract defect, not a stylistic preference.

## Relationship to the guidelines

`hello-window` follows every rule in this book that applies to it: the window
bands, the menu order, the control sizes, the focus ring, the state chip and
the status line. Where a rule assumes an editable document or several windows,
this chapter records the exemption: the fixed read-only document and the single
window are the reason the corresponding commands and menus are absent. It is
the reference for the smallest complete surface, and therefore the first place
a new developer should look.
