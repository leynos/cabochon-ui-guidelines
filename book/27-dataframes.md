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

- Categories pane: 210 pixels, listing saved filters with their row counts.
- Formula bar: 34 pixels, directly below the menu bar, showing the selected
  cell's expression or value.
- Grid: the flexible remainder.
- Cell inspector: 240 pixels, showing the selected cell's address, type,
  value, format and validation.

The categories pane is optional for a small table. The formula bar and the
inspector are not: they are how the instrument explains what a cell is.

## The grid

- Header row: 30 pixels, with column names in 11-pixel metadata, bold and
  letter-spaced.
- Body rows: 28 pixels minimum, 34 preferred.
- Cell padding: 12 pixels horizontally.
- Grid lines: 1 pixel in line; horizontal lines only when row density
  requires them.
- Alternating rows use high and white, not a tint.
- The selected cell uses the pine-2 fill with white text.
- The selected range uses a 2-pixel oxide outline around its extent.

Numbers are right-aligned and use tabular figures. Text is left-aligned. Dates
and times follow the locale but keep a stable, sortable underlying value. A
cell that cannot display its full value truncates at the end and reveals the
value in the inspector.

## Types and formats

A cell's type is part of the object, not a property of its display.

- Supported scalar types in the first batch: text, number, currency, date,
  boolean and reference.
- A format controls how a value is shown: `0,000`, `0.00%`, `14:02`,
  `GBP 0.00`.
- Changing a format must not change the stored value.
- A value that does not fit its column's type is a validation error, not a
  silent conversion.
- A reference cell holds another object's identity and shows its name; it
  becomes stale when the referenced object is unavailable.

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
- The status line reports the count and the aggregate of numeric cells.
- The inspector reports the range in A1 notation, the cell count and the sum
  or average where meaningful.

A selection must remain visible when the grid loses focus, drawn as an outline
rather than a fill.

## Editing

- Typing replaces the cell's content; F2 or a double-click edits in place.
- Enter commits and moves down; Tab commits and moves right.
- Escape cancels the edit and restores the previous value.
- A committed edit is one undoable transaction.
- A paste larger than the current range asks before expanding the table, and
  states how many rows and columns will be added.
- A paste that would overwrite non-empty cells is confirmed with the count and
  the range.

## Validation

Validation rules belong to the column, not to individual cells.

- A rule is shown in the inspector with its scope and its message.
- A violated cell carries a 2-pixel oxide mark in its corner and a message on
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

## Large tables

A table with more than 10,000 rows must virtualize its rows, keep the header
fixed and show a row count in the status line. It must not block the interface
while sorting or filtering; a long operation shows progress and can be
cancelled.

## What the dataframe is not

- A free-form grid where every cell may hold a different type without
  declaration.
- A presentation format. A chart or a print layout reads the dataframe; it
  does not become one.
- A file. The dataframe is an object, and it may be exported to CSV or
  Parquet without losing its identity in the project.
