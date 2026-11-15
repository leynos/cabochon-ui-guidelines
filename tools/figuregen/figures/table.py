"""Draw the Enfilade Table window figure.

The window shows category filters, a formula bar, a typed grid and a cell
inspector. The exported `fig_table` function returns the SVG string, drawn
from its `_COLS`, `_WIDTHS` and `_ROWS` data and the shared `figuregen.palette`
colours. `figuregen.cli` calls it to write `fig-25-table.svg` under `figures/`.
"""

from __future__ import annotations

from figuregen.canvas import line, para, rect, svg_doc, txt
from figuregen.ornaments import title_block
from figuregen.palette import F_MONO, HIGH, INK, LINE, OXIDE, PAPER, PINE2, SOFT, WHITE
from figuregen.widgets import inspector_row, pane_head, window_shell

_COLS = ["Source", "Capacity", "Output", "Share"]
_WIDTHS = [228, 130, 130, 110]
_ROWS = [
    ("Wind · Dogger Bank", "3.6 GW", "14,210", "38%"),
    ("Wind · Hornsea", "2.8 GW", "11,040", "29%"),
    ("Solar · East Anglia", "1.2 GW", "2,180", "6%"),
    ("Hydro · Norway", "0.8 GW", "4,320", "11%"),
    ("Imported · France", "2.0 GW", "6,090", "16%"),
]


def _category_counts() -> list[tuple[str, int]]:
    """Count the rows in each category, in order of first appearance."""
    source = _COLS.index("Source")
    order: list[str] = []
    counts: dict[str, int] = {}
    for row in _ROWS:
        category = row[source].split(" · ", 1)[0]
        if category not in counts:
            order.append(category)
            counts[category] = 0
        counts[category] += 1
    return [("All rows", len(_ROWS)), *[(name, counts[name]) for name in order]]


def _output_total() -> int:
    """Sum the Output column over the displayed rows."""
    output = _COLS.index("Output")
    return sum(int(row[output].replace(",", "")) for row in _ROWS)


def _categories(x: float, y: float, cat_w: float, h: float) -> str:
    """Draw the category rail."""
    body = rect(x, y + 60, cat_w, h - 86, fill=PAPER, stroke=None)
    body += pane_head(x, y + 60, cat_w, "Categories")
    cats = _category_counts()
    for index, (name, count) in enumerate(cats):
        cy = y + 100 + index * 32
        if index == 0:
            body += rect(x, cy - 18, cat_w, 28, fill=PINE2, stroke=None)
        body += txt(x + 14, cy, name, size=11, fill=WHITE if index == 0 else INK)
        body += txt(
            x + cat_w - 14,
            cy,
            str(count),
            size=10,
            fill=WHITE if index == 0 else SOFT,
            family=F_MONO,
            anchor="end",
        )
    return body


def _formula_bar(fx: float, y: float, w: float, cat_w: float) -> str:
    """Draw the formula bar."""
    body = rect(fx, y + 60, w - cat_w, 34, fill=PAPER, stroke=None)
    body += line(fx, y + 94, fx + w - cat_w, y + 94, stroke=LINE)
    body += txt(fx + 12, y + 82, "fx", size=12, fill=SOFT, family=F_MONO, weight="bold")
    body += rect(fx + 36, y + 66, w - cat_w - 48, 22, fill=WHITE, stroke=LINE)
    return body + txt(fx + 48, y + 81, "11,040", size=11, fill=INK, family=F_MONO)


def _grid_header(gx: float, gy: float) -> str:
    """Draw the grid header row."""
    body = ""
    for index, (name, width) in enumerate(zip(_COLS, _WIDTHS, strict=True)):
        cx = gx + sum(_WIDTHS[:index])
        body += rect(cx, gy, width, 30, fill=PAPER, stroke=LINE)
        if index == 0:
            body += txt(
                cx + 10,
                gy + 20,
                name,
                size=11,
                fill=SOFT,
                weight="bold",
                family=F_MONO,
                spacing=0.5,
            )
        else:
            body += txt(
                cx + width - 10,
                gy + 20,
                name,
                size=11,
                fill=SOFT,
                weight="bold",
                family=F_MONO,
                spacing=0.5,
                anchor="end",
            )
    return body


def _grid_row(gx: float, gy: float, index: int, row: tuple[str, ...]) -> str:
    """Draw one data row of the grid."""
    body = ""
    for column, (value, width) in enumerate(zip(row, _WIDTHS, strict=True)):
        cxx = gx + sum(_WIDTHS[:column])
        cyy = gy + 30 + index * 34
        selected = index == 1 and column == 2
        fill = PINE2 if selected else (HIGH if index % 2 == 0 else WHITE)
        body += rect(cxx, cyy, width, 34, fill=fill, stroke=LINE)
        if column == 0:
            body += txt(
                cxx + 12, cyy + 22, value, size=11, fill=WHITE if selected else INK
            )
        else:
            body += txt(
                cxx + width - 12,
                cyy + 22,
                value,
                size=11,
                fill=WHITE if selected else INK,
                family=F_MONO,
                anchor="end",
            )
    return body


def _grid(gx: float, gy: float) -> str:
    """Draw the grid with its selection."""
    body = _grid_header(gx, gy)
    for index, row in enumerate(_ROWS):
        body += _grid_row(gx, gy, index, row)
    range_x = gx + _WIDTHS[0]
    range_y = gy + 30
    active_x = range_x + _WIDTHS[1]
    active_y = range_y + 34
    body += line(
        active_x + 7, active_y + 8, active_x + 7, active_y + 26, stroke=WHITE, sw=1
    )
    return body + rect(
        range_x, range_y, _WIDTHS[1] + _WIDTHS[2], 68, fill="none", stroke=OXIDE, sw=2
    )


def _cell_inspector(ix: float, y: float, h: float) -> str:
    """Draw the cell inspector."""
    body = rect(ix, y + 60, 240, h - 86, fill=PAPER, stroke=None)
    body += line(ix, y + 60, ix, y + h - 26, stroke=INK)
    body += pane_head(ix, y + 60, 240, "Cell")
    body += inspector_row(ix + 14, y + 110, 212, "Address", value="C3")
    body += inspector_row(ix + 14, y + 134, 212, "Type", value="number · GWh")
    body += inspector_row(ix + 14, y + 158, 212, "Value", value="11,040")
    body += inspector_row(ix + 14, y + 182, 212, "Format", value="0,000")
    body += txt(
        ix + 14,
        y + 216,
        "VALIDATION",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=0.6,
    )
    body += txt(ix + 14, y + 240, "Number, 0–99,999", size=11, fill=INK)
    body += txt(ix + 14, y + 262, "No empty cells in this column", size=11, fill=INK)
    body += txt(
        ix + 14,
        y + 302,
        "SELECTION",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=0.6,
    )
    body += txt(ix + 14, y + 326, "B2:C3 · 4 cells", size=11, fill=INK, family=F_MONO)
    body += txt(
        ix + 14, y + 348, "2 numeric · 2 text", size=10, fill=SOFT, family=F_MONO
    )
    body += txt(ix + 14, y + 370, "Sum 25,250 GWh", size=11, fill=PINE2, family=F_MONO)
    body += txt(
        ix + 14, y + 392, "Average 12,625 GWh", size=11, fill=PINE2, family=F_MONO
    )
    return body + para(
        ix + 14,
        y + 424,
        212,
        "A typed value stays a number. The displayed format never becomes the stored value.",
        size=10,
        leading=16,
    )


def fig_table() -> str:
    """Draw Enfilade Table with categories, grid and cell inspector.

    Returns
    -------
    str
    """
    body = title_block(
        64,
        70,
        "Enfilade Table",
        "Typed cells, a visible formula bar and a selection that states its own extent. The grid is an editor, not a spreadsheet costume.",
    )
    x, y, w, h = 64, 150, 1072, 540
    body += window_shell(
        x,
        y,
        w,
        h,
        title="Enfilade Table — Generation mix",
        menu=["File", "Edit", "View", "Data", "Object", "Window", "Help"],
        status=(
            f"Output total {_output_total():,} GWh · "
            f"{len(_ROWS)} rows · {len(_COLS)} columns"
        ),
        state="Current",
    )
    cat_w = 210
    body += _categories(x, y, cat_w, h)
    body += line(x + cat_w, y + 60, x + cat_w, y + h - 26, stroke=INK)
    fx = x + cat_w
    body += _formula_bar(fx, y, w, cat_w)
    body += _grid(fx + 12, y + 104)
    body += _cell_inspector(x + w - 240, y, h)
    return svg_doc(
        1200,
        760,
        "Enfilade Table with categories, grid and cell inspector",
        "A data table with category filters, a formula bar, typed numeric cells, a selected range and a cell inspector.",
        body=body,
    )
