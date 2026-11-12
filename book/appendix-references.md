---
title: References
part: Appendices
summary: The design traditions, primary documents and Cabochon sources behind this book.
---

# References

This book is a synthesis, not a survey. The works below supplied particular
habits of thought; none of them is a template for Cabochon, and several
disagree with it.

## Cabochon sources

- **Cabochon repository.** <https://github.com/leynos/cabochon>. The
  philosophy, the component boundaries and the first-batch scope.
- **Cabochon design book.** The visual study held alongside this repository as
  `cabochon-design-book`. Its palette, metrics and document-centred layout are
  the starting point for the production values in this book.
- **Cabochon component documentation.** Clerestory, Lapidary, Burin,
  Escutcheon, Enfilade, Mullion and cabochon-portal. The contracts in
  [The ecosystem map](03-ecosystem-map.md) summarize them.

## Contract basis

Every normative platform dependency in this book names the document and
revision it was written against. A dependency without a basis is a claim, not a
contract.

| Repository                      | Revision      | Document and section                                      | Status                         | Conflict owner  |
| ------------------------------- | ------------- | --------------------------------------------------------- | ------------------------------ | --------------- |
| `leynos/cabochon`               | `de40019`     | `docs/cabochon-design.md` §§2.2, 7.1, 8.1–8.10, 9.2       | Authoritative platform design  | Platform design |
| `leynos/cabochon`               | `de40019`     | `docs/execplans/1-0-1-clerestory-application-contract.md` | Approved substrate plan        | Programme       |
| `leynos/cabochon`               | `de40019`     | `docs/execplans/1-0-2-escutcheon-resource-format.md`      | Approved substrate plan        | Programme       |
| `leynos/cabochon`               | `de40019`     | `docs/execplans/1-0-3-lapidary-scene-contract.md`         | Approved substrate plan        | Programme       |
| `leynos/cabochon`               | `de40019`     | `docs/execplans/1-0-4-burin-output-contract.md`           | Approved substrate plan        | Programme       |
| `leynos/cabochon`               | `de40019`     | `docs/adrs/adr-0001`–`adr-0008`                           | Accepted decisions             | Architecture    |
| `leynos/cabochon-ui-guidelines` | this revision | `book/`                                                   | Normative for user experience  | This book       |
| Local visual study              | unversioned   | `cabochon-design-book`                                    | Reference only, not a contract | This book       |

The revision is the commit the book was checked against, not a promise that the
platform will not move. When a platform document changes, the change is
reconciled in the authoritative programme documentation first, and this book
follows. A genuine scope change is never made silently in user-experience prose.

## Conformance profiles and delivery phases

A conformance profile names the capabilities a surface must provide. A delivery
phase names what the programme is building now. They are different axes, and
the book keeps them apart.

- **Substrate conformance.** Clerestory, Lapidary, Burin and Escutcheon. A
  substrate-only surface draws, exports and is accessible without Enfilade,
  semantic object identity or a capability grant. The
  [hello-window](36-hello-window.md) fixture is the reference.
- **Semantic workspace conformance.** Adds Enfilade, live relationships, the
  capability broker and the workspace instruments. It requires the substrate
  profile and the semantic contracts in
  [Live relationships](08-live-relationships.md).
- **Studio conformance.** Adds the studio tools and their heavier output
  requirements. It requires the semantic workspace profile and the studio
  contracts in [The studio and the contracts](33-burin-draw.md).

Membership is cumulative, and the table below is the single declaration of it.
An "Adds" entry is required by that profile; an "Inherits" entry is required
because the profile it inherits from already requires it.

| Capability or instrument                | Substrate | Semantic workspace | Studio   |
| --------------------------------------- | --------- | ------------------ | -------- |
| Clerestory, Lapidary, Burin, Escutcheon | Adds      | Inherits           | Inherits |
| Enfilade, capability broker             | —         | Adds               | Inherits |
| Live relationships                      | —         | Adds               | Inherits |
| Facet Notes                             | —         | Adds               | Inherits |
| Dataframe editor                        | —         | Adds               | Inherits |
| Diagram editor                          | —         | Adds               | Inherits |
| Bitmap editor                           | —         | Adds               | Inherits |
| Formula tool                            | —         | Adds               | Inherits |
| Inspector and project window            | —         | Adds               | Inherits |
| Burin Draw                              | —         | —                  | Adds     |
| Cabochon Press                          | —         | —                  | Adds     |
| Enfilade Table                          | —         | —                  | Adds     |
| SVG vector encoding for diagram export  | —         | Adds               | Inherits |
| PDF/X and print production profiles     | —         | —                  | Adds     |

The studio profile does not repeat the workspace instruments. They remain
required because studio conformance requires semantic workspace conformance.
Enfilade Table is a studio tool, so it appears only in the studio row.

An instrument's required export encodings must be a subset of its resolved
profile's capabilities. The diagram editor claims semantic workspace
conformance, so SVG is a semantic workspace capability; the studio profile
inherits it rather than owning it. PDF/X is a studio production capability
because it depends on the print profiles that only the studio tools claim.

The **first batch** is a delivery phase, not a profile. It names the work the
programme is doing now. The studio guidance in this book is strict and
prospective: it states what a studio instrument must do when it is built, and
it does not claim that the first release is a desktop-publishing package. Where
the platform design's initial proving ground limits document types, that limit
belongs to the delivery phase and is reconciled in the programme documentation,
not overridden here.

## Document-oriented environments

- **Étoilé mockups, Jesse 2007.**
  <https://etoileos.com/etoile/mockups/jesse-2007/>. The clearest demonstration
  that a desktop can be organized around documents, objects and live
  relationships rather than around applications and files. The composure of its
  surfaces and the prominence of the document plane informed
  [The document at the centre](06-document-centre.md).
- **GEM and FreeMiNT.** Digital Research's GEM supplied the rectangle as the
  basic unit of interface behaviour and the idea of a small, predictable
  desktop. FreeMiNT's continuation of that environment is a reminder that
  compactness is a design choice, not a limitation.
  <https://freemint.github.io/>

## Platform guidelines

- **KDE Human Interface Guidelines.** <https://develop.kde.org/hig/>. Clear,
  practical guidance on controls, dialogs and keyboard access, written for a
  free-software desktop.
- **Haiku Human Interface Guidelines.** <https://www.haiku-os.org/docs/HIG/>.
  A compact, opinionated guide with a strong sense of place. Its treatment of
  windows, menus and direct manipulation is a useful counterweight to guideline
  documents that grow without limit.
- **GNOME Human Interface Guidelines.** <https://developer.gnome.org/hig/>.
  Modern guidance on accessibility, adaptive layout and restrained motion.
- **Apple Human Interface Guidelines, 2005 edition.** The pre-mobile edition
  is a model of explaining a visual language through worked examples rather
  than abstractions. Its emphasis on clarity, directness and feedback survives
  the change of platform.
- **NeXTSTEP User Interface Guidelines.** Addison-Wesley, 1993. The source of
  many habits this book retains: the inspector, the document-centred window,
  the sheet, and a small number of strong visual conventions applied
  consistently.
- **Windows Interface Guidelines for Software Design.** Microsoft Press, 1995.
  The most complete published account of the classic desktop vocabulary. Its
  menu order, dialog conventions and state marks are widely understood and are
  used here where they help.
- **Newton 2.0 User Interface Guidelines.** Apple, 1996. A study in designing
  for a small surface without shrinking the interaction. Its rules for targets,
  handwriting and progressive disclosure remain instructive.
- **Zen of Palm.** PalmSource, 2001. A short argument for doing a few things
  well on a constrained device. Its discipline informs
  [The first batch](04-first-batch.md) and the anti-patterns throughout this
  book.
- **IRIX Interactive User Interface Guidelines.** Silicon Graphics, 1995. A
  guide from a workstation culture that valued density, colour and direct
  manipulation. It is a reminder that a professional interface need not be
  austere.
- **CDE Style Guide and Certification Checklist.** The Open Group, 1996. A
  formal, testable style guide. Its checklist format informed
  [the conformance checklist](40-checklist.md), even where its visual language
  did not.

## Standards and technical references

- **WCAG 2.2.** <https://www.w3.org/TR/WCAG22/>. The contrast ratios, target
  sizes, reflow and motion requirements in [Accessibility](39-accessibility.md)
  follow this specification.
- **WAI-ARIA Authoring Practices.** <https://www.w3.org/WAI/ARIA/apg/>. Role
  and state vocabulary for custom controls.
- **Unicode Standard Annex #9, Unicode Bidirectional Algorithm.**
  <https://www.unicode.org/reports/tr9/>. The basis for the direction rules in
  [Localization](38-localization.md).
- **PDF 1.7 and PDF/X-4.** The output intents and preflight rules in
  [Cabochon Press](34-cabochon-press.md) assume these specifications. PDF/X
  conformance is claimed only by an output profile that validates the chosen
  level; other output is described as PDF with a declared colour intent and is
  not called PDF/X.

## A note on borrowing

A guideline is not a style. The documents above agree on very little beyond the
value of consistency, legibility and a visible response to the user's action.
Cabochon borrows habits, not appearances. Where this book states a number, it
is a decision for the first small world, made to be tested and revised, not an
appeal to authority.
