---
title: Purpose
part: Orientation
summary: What this book is for, who it serves and how far its authority runs.
---

# Purpose

Cabochon needs a user interface that matches its ambition without imitating a
large desktop. The ambition is a document environment in which objects keep
their identity across applications, and in which tools appear where they are
useful rather than in a global bazaar. The risk is that each application
invents its own idea of a window, a menu, a selection or a saved file, and the
environment dissolves into a collection of unrelated programs.

This book exists to prevent that. It states the common furniture, the common
measurements and the common habits for the first Cabochon small world. It is a
manual for people building that world: application developers, interaction
designers, iconographers and reviewers.

## Scope

The book covers three kinds of software.

- **Contracts.** The reference applications and shared formats that prove the
  substrate: `hello-window`, `escutcheon-check`, the Lapidary scene contract
  and the Burin output contract.
- **Workspace instruments.** Facet Notes, the dataframe editor, the diagram
  editor, the bitmap editor, the formula tool, the inspector and the project
  window.
- **Studio tools.** Burin Draw, Cabochon Press and Enfilade Table, which
  exercise the same furniture under heavier demands.

The book does not specify a compositor, a GPU renderer, a final widget toolkit
or a replacement for any existing desktop. Those decisions belong to later
evidence. It also does not describe organization-only administration, fleet
management or compliance features, none of which are part of the first small
world.

## Authority

Three sources govern a Cabochon interface, in descending order.

1. **Platform contracts.** Clerestory, Lapidary, Burin and Escutcheon define
   what an application can rely on. A guideline cannot require behaviour that a
   contract does not provide.
2. **This book.** It interprets the contracts for the first batch and fixes
   the shared visual and interaction language.
3. **Local judgement.** An application may add a control or a panel that its
   own work requires, provided the addition uses the shared furniture and does
   not contradict a rule.

Guidance marked **must** is a release condition. Guidance marked **should** is
the expected choice, open to a documented exception. Guidance marked **may** is
an option that costs nothing to omit.

## Why a book rather than a component library

A component library can enforce geometry. It cannot explain why a pane head is
28 pixels, why a stale relationship is amber rather than red, or why a
destructive action requires a sentence rather than a second button. The first
batch is small enough that shared understanding matters more than a shared
binary. The book is the contract between teams until the components catch up.

The book is also a test instrument. Each chapter states observable behaviour,
so a reviewer can compare a running application with the text and reach a
verdict without reading source code.

## How the chapters fit together

The first part establishes the character and the map. The second explains the
document model that every later chapter assumes. The third to fifth parts
supply the structural, visual and interaction vocabulary. The sixth and seventh
apply that vocabulary to concrete instruments. The final part extends it to
localization and accessibility, and closes with a checklist.

A reader building a single application should read Parts I to V in order, then
the chapter for the instrument at hand. A reader reviewing an application
should start with the [checklist](40-checklist.md) and follow the links
backwards.

## A note on tone

Cabochon's design book describes a clean, practical and liberal environment.
Those words carry obligations. *Clean* means that every visible element earns
its place. *Practical* means that the common task is short and the rare task is
possible. *Liberal* means that the user's documents, formats and choices
outrank the environment's preferences.

The chapters that follow turn those obligations into pixels, states and
keyboard paths.
