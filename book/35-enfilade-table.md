---
title: Enfilade Table
part: The studio and the contracts
figure: fig-25-table.svg
summary: The dense table instrument for large typed data, references and validation at scale.
---

# Enfilade Table

![Enfilade Table with categories, grid and cell inspector.](../figures/fig-25-table.svg)

Enfilade Table is the studio's dense data instrument. It edits large typed
tables, their validation rules and their references to other objects. The
workspace dataframe editor edits a single embedded dataframe; Enfilade Table is
where a dataset with many rows, several categories and cross-table references
is examined and maintained.

## Layout

- Categories panel: 200 pixels, listing saved filters with row counts.
- Formula bar: 34 pixels, showing the selected cell's expression.
- Grid: the flexible remainder.
- Cell inspector: 250 pixels, showing address, type, value, format,
  validation and selection aggregates.
- Status line: aggregate, row count and column count.

The categories panel is the instrument's navigator. It lists **All rows** and
each saved category, with the selected category filled in pine 2.

## The grid at scale

- Header row: 30 pixels, with column names in 10-pixel metadata.
- Body rows: 28 pixels minimum, 34 preferred.
- Column widths are draggable and remembered per view.
- The grid virtualizes rows and columns; a 100,000-row table remains
  scrollable at interactive speed.
- Frozen columns keep the key column visible while scrolling horizontally.
- Numbers are right-aligned with tabular figures; text is left-aligned.
- The selected cell uses pine 2; the selected range uses a 2-pixel oxide
  outline; the active cell keeps a white caret.

## Types

The studio table supports the workspace types plus:

- **reference**, holding another object's identity;
- **enum**, holding one of a declared set of values;
- **computed**, holding a live formula with its own identity;
- **blob**, holding opaque bytes with a declared media type.

A computed column is a provider-owned object. Editing its expression edits the
column's definition, not each cell. A reference column resolves names through
the provider and shows **Denied** or **Unavailable** without revealing the
referenced value.

## Validation at scale

Validation is declared per column and may depend on other columns.

- The inspector lists every rule that applies to the selected cell, with its
  scope and message.
- A violated cell carries a 2-pixel oxide corner mark.
- The status line reports the number of violating rows in the current
  category.
- The categories panel can create a **Violations** category, which is a view,
  not a stored filter on the object.
- Validation never blocks reading, sorting, filtering or exporting. It marks
  the data and reports it.

## References and joins

A reference cell shows the referenced object's name and its state. A join
between two tables is a computed view, not a mutation of either table.

- Creating a join declares its key columns and its output columns.
- The join is previewed before it is saved.
- A broken reference appears in the **Broken references** category and offers
  **Repair** or **Clear**.
- Deleting a referenced object warns and lists the tables that reference it.

## Categories

A category is a saved filter with a name and a count. It is stored in the view,
not in the table object.

- Creating a category from the current filter is one command.
- A category may be pinned to the top of the panel.
- A category that matches no rows says so and offers to edit its filter.
- The **All rows** category is always present and cannot be deleted.

## Formula bar and computed columns

The formula bar edits the selected cell or the selected computed column's
definition, depending on the selection.

- The bar shows the expression, not the formatted result.
- A computed column's expression names its sources in the inspector.
- A malformed expression is reported at its location and does not change the
  column.
- A computed column that becomes stale keeps its last value and reports its
  state.

## Import and export

- Import accepts CSV, TSV, Parquet and a Cabochon table bundle.
- Import previews the inferred types, the delimiter and the encoding before
  committing.
- A failed row is reported with its line number and does not abort the
  imported rows unless the user chooses all-or-nothing.
- Export writes the table's values and its declared types, not its formatted
  display.
- The export manifest records the table's identity, revision and any computed
  columns that were evaluated.

## What Enfilade Table is not

- A spreadsheet with free-form cells and implicit types.
- A database administration console.
- A charting tool. Charts read the table and present it elsewhere.
- A place where a reference is copied as a string. References keep identity.

## Testing

A reviewer should build a table with a reference column, break the reference,
create a violations category, repair the reference and confirm that the table's
identity, revision and exported types are unchanged by the view operations.
