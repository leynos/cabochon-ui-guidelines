---
title: Dataframes
part: The workspace
summary: Typed cells, a visible formula bar and a grid that behaves like an editor.
---

# Dataframes

A dataframe is a typed table, not a spreadsheet costume. Its cells hold values
with declared types, its columns have names and formats, and its selection
states its own extent. The instrument that edits it should make those facts
visible.

## Layout

The dataframe editor uses a categories pane, a grid and a cell inspector.

- Categories pane: 210 units, listing saved filters with their row counts
  where the disclosure policy permits them.
- Formula bar: 34 units, directly below the menu bar, showing the selected
  cell's expression or value.
- Grid: the flexible remainder.
- Cell inspector: 240 units, showing the selected cell's address, type,
  value, format and validation.

The categories pane is optional for a small table. The formula bar and the
inspector are not: they are how the instrument explains what a cell is.

## The grid

- Header row: 30 units, with column names in 12-unit operational interface
  type, bold and letter-spaced. A column name is essential, so it uses the
  operational floor even though it sits in a metadata-shaped band.
- Body rows: 28 units minimum, 34 preferred.
- Cell padding: 12 units horizontally.
- Grid lines: 1 unit in the decorative line role; horizontal lines only when
  row density requires them.
- Alternating rows use high and white, not a tint.
- The selected cell uses the selected-fill and selected-text roles.
- The selected range uses a 2-unit oxide outline around its extent.

Numbers align to the trailing edge and use tabular figures. Text aligns to the
leading edge. Dates and times follow the locale but keep a stable, sortable
underlying value. A cell that cannot display its full value truncates at the
end and reveals the value in the inspector.

## Types and formats

A cell's type is part of the object, not a property of its display. Four
properties are independent and must not be collapsed into one "type" label.

- **Scalar type** — text, number, currency, date, time, datetime, boolean or
  reference.
- **Nullability** — whether the column admits an absent value, declared
  separately from the scalar type.
- **Semantic validation** — a business rule over the value, which may accept a
  structurally valid value and mark it.
- **Value-production mode** — stored, computed by a column expression, or
  supplied by a live reference.

- A format controls how a value is shown: `0,000`, `0.00%`, `14:02`,
  `GBP 0.00`.
- Changing a format must not change the stored value.
- A value that does not fit its column's scalar type is rejected at entry and
  leaves the previous typed value intact. It is a structural error, not a
  validation violation.
- A value that fits its type but violates a business rule is accepted, marked
  and reported. It remains readable and exportable.
- A time value carries a time of day; a datetime carries an instant and a
  declared zone or offset. A datetime without a zone is a local datetime and
  says so; it is not silently treated as UTC.
- A computed cell's value is produced by its column definition, not stored per
  cell. Editing the definition updates the column object and commits a new
  revision; it does not allocate a fresh identity for each cell result.
- A reference cell holds another object's identity and shows its name and its
  relationship state. It is **Stale** when the referenced object's source
  revision has advanced, **Broken** when the provider is unavailable and
  **Denied** when the current grant does not permit reading it. Unavailable is
  not stale, and the cell must not claim knowledge of a revision it cannot read.

## Formula bar

The formula bar shows the selected cell's expression, prefixed with `fx` in
metadata type. It is editable, and committing an expression creates a live
value with its own identity.

The formula bar must:

- show the expression, not the formatted result;
- name the sources it reads in a tooltip or in the inspector;
- reject a malformed expression with a source-located message;
- preserve the last valid result while an edit is incomplete.

The detailed behaviour of expressions belongs to
[The formula tool](30-formula.md).

## Selection

The selection is a range of cells with an anchor and an extent.

- Click selects one cell.
- Shift-click extends the range from the anchor.
- Arrow keys move the active cell; Shift with an arrow extends the range.
- Control+A selects the used range, not the entire grid.
- The status line reports the count and the aggregate of numeric cells when the
  disclosure policy permits those classes; otherwise it reports the selection
  without a count or aggregate.
- The inspector reports the range in A1 notation, the cell count and the sum
  or average where meaningful and permitted.

A selection must remain visible when the grid loses focus, drawn as an outline
rather than a fill.

## Addresses and identity

A visible address such as `B2` is a presentation address, not an identity. The
table distinguishes three things:

- a **row identity**, stable for the entity the row represents, independent of
  its current display position;
- a **column identity**, stable across reordering and renaming;
- a **cell address**, the pair of the two.

Sorting, filtering and inserting rows change display positions without changing
row or column identity. A formula or a reference that means an entity records
that identity; one that means "whatever is at B2" records positional semantics
and says so when it is created. Deleting a row leaves a recoverable broken
reference for an entity-bound expression, not a silent attachment to the next
row. A tombstone keeps the identity resolvable until the reference is repaired
or removed.

## Editing

The grid has two keyboard modes, and the same key means different things in
each. The modes are the ones defined in
[Focus and the keyboard](18-focus-keyboard.md).

- **Grid navigation.** The grid has focus but no cell is being edited. Arrow
  keys move the active cell, Tab leaves the grid for the next control, and
  Enter opens the active cell for editing.
- **Cell editing.** A cell is open for editing. Typing inserts text, Tab
  commits the edit and moves right, Enter commits and moves down, and Escape
  cancels the edit and restores the previous value.

Tab never commits and moves right while the grid is merely navigating, and it
never cycles inside the grid indefinitely. Shift+Tab leaves the grid in
navigation mode and moves left within the row in cell-editing mode. The mode is
shown in the status line, so a user can tell which behaviour Tab will have.

- Typing in navigation mode replaces the cell's content and enters cell
  editing; F2 or a double-click edits in place without replacing.
- A committed edit is one undoable transaction.
- A paste larger than the current range asks before expanding the table, and
  states how many rows and columns will be added.
- A paste that would overwrite non-empty cells is confirmed with the count and
  the range.
- A context menu opened on a cell targets that cell. Opening it does not change
  the persistent range selection, and its commands act on the context target
  unless the command is a selection command, as described in
  [Menus](10-menus.md).

## Validation

Validation rules belong to the column, not to individual cells.

- A rule is shown in the inspector with its scope and its message.
- A violated cell carries a 2-unit oxide mark in its corner and a message on
  focus.
- The table's status line reports how many cells violate a rule.
- A rule must not prevent reading or exporting the table; it marks the data,
  it does not hide it.

## Sorting and filtering

Sorting changes the view, not the stored order, unless the table declares an
ordered column. Filtering hides rows and reports how many are hidden. Both
actions are reversible and are recorded in the view, not in the object.

A filter that removes the selected row moves the selection to the nearest
visible row and says so in the status line.

## State and persistence

The dataframe keeps four independent kinds of state apart.

- **Relationship state.** A reference cell carries **Current**, **Refreshing**,
  **Stale**, **Broken** or **Denied** from
  [Live relationships](08-live-relationships.md). The table's status chip
  summarises these with the same precedence as a document.
- **Draft validity.** An incomplete or malformed expression in the formula bar
  is a draft error. The committed cell or computed column keeps its last valid
  result and reports the draft error beside the editor.
- **Persistence.** Modified, saving, saved and save failed belong to the
  document's save state, not to a relationship. A failed save does not make a
  current reference stale.
- **View state.** Sorting, filtering, column widths and category selection are
  recorded in the view and never change the object's identity or revision.

An empty table still has a type and a revision, and its status line says "0
rows" rather than implying that content failed to load. A table with no
reference columns has no relationship state to summarise.

## Large tables

A table with more than 10,000 rows must virtualize its rows and keep the header
fixed. It shows a row count in the status line only when the disclosure policy
permits that class. It must not block the interface while sorting or filtering;
a long operation shows progress and can be cancelled.

## Export

A dataframe export is a user export: CSV, TSV, Parquet or a Cabochon table
bundle. It names its encoding, its declared losses and the snapshot it read. A
plain delimited file cannot carry declared types, references or live values, so
the export states those losses rather than implying they survived. A
type-preserving export uses the table bundle or a sidecar schema. The
capability and loss table in [Enfilade Table](35-enfilade-table.md) is the
authoritative statement of what each target carries. The export does not create
the eight-artefact conformance bundle, which is a separate review command.

## What the dataframe is not

- A free-form grid where every cell may hold a different type without
  declaration.
- A presentation format. A chart or a print layout reads the dataframe; it
  does not become one.
- A file. The dataframe is an object, and it may be exported to CSV or
  Parquet without losing its identity in the project.
