"""Tests for the chapter table and worked-cell parsers.

Only a table a renderer would display may stand in for the chapter's table, so
a fenced example or a commented-out draft is ignored. A worked cell states at
most one total, so an intermediate equality cannot slip past the sum check
unread.
"""

from __future__ import annotations

import pytest
from layoutcheck.tables import (
    MalformedCellError,
    addends,
    stated_total,
    table_with,
)


def test_table_with_ignores_a_fenced_example_table() -> None:
    """A fenced example table does not stand in for the rendered one."""
    source = (
        "```markdown\n"
        "| Bands | Values   | Total |\n"
        "| ----- | -------- | ----- |\n"
        "| demo  | 1 + 1    | 2     |\n"
        "```\n"
        "\n"
        "| Bands | Values   | Total |\n"
        "| ----- | -------- | ----- |\n"
        "| real  | 44 + 116 | 160   |\n"
    )
    assert table_with(source, "Bands") == [["real", "44 + 116", "160"]], (
        "the rendered table is read rather than the fenced example"
    )


def test_table_with_ignores_a_commented_table() -> None:
    """A table inside an HTML comment is not read."""
    source = (
        "<!--\n"
        "| Bands | Values   | Total |\n"
        "| ----- | -------- | ----- |\n"
        "| draft | 1 + 1    | 2     |\n"
        "-->\n"
        "\n"
        "| Bands | Values   | Total |\n"
        "| ----- | -------- | ----- |\n"
        "| real  | 44 + 116 | 160   |\n"
    )
    assert table_with(source, "Bands") == [["real", "44 + 116", "160"]], (
        "the commented table is ignored"
    )


def test_a_worked_cell_states_at_most_one_total() -> None:
    """An intermediate equality is rejected rather than read past."""
    with pytest.raises(MalformedCellError) as info:
        addends("44 + 116 = 999 = 160")
    assert "states more than one total" in str(info.value), (
        "the defect names the second equals sign"
    )
    with pytest.raises(MalformedCellError):
        stated_total("44 + 116 = 999 = 160")


def test_a_single_total_is_still_read() -> None:
    """One total, or none, is accepted as before."""
    assert addends("44 + 116 = 160") == [44, 116], "the addends precede the total"
    assert stated_total("44 + 116 = 160") == 160, "the stated total is read"
    assert stated_total("160") == 160, "a bare integer supplies its own total"