"""Tests for the code-span recognition the structural checkers share.

A backtick that follows an odd run of backslashes is literal text and cannot
open a code span, so two escaped backticks around a link leave that link
visible. A genuine span still hides its content, and a backslash inside one is
content rather than an escape.
"""

from __future__ import annotations

import pytest
from markdown_links import link_targets
from markdown_structure import strip_code_and_comments, strip_fences_and_comments


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (r"\`[broken](missing.md)\`", ["missing.md"]),
        (r"\`[a](b.md)\` and \`[c](d.md)\`", ["b.md", "d.md"]),
        (r"`[hidden](missing.md)`", []),
        (r"\``[hidden](missing.md)`", []),
    ],
    ids=["escaped-pair", "two-escaped-pairs", "genuine-span", "escaped-run"],
)
def test_escaped_backticks_neither_open_nor_hide_a_link(
    source: str, expected: list[str]
) -> None:
    """An escaped backtick is literal, while a genuine pair still hides text."""
    assert link_targets(source) == expected, "the span's backtick escapes are honoured"


def test_a_removed_span_keeps_the_text_around_it() -> None:
    """Only the span disappears; the prose on either side survives."""
    assert strip_code_and_comments(r"see `rate` here") == "see  here", (
        "the span is removed whole"
    )


def test_a_backslash_inside_a_span_is_content() -> None:
    """A backslash before the closing backtick does not escape it."""
    assert strip_code_and_comments(r"`a\`") == "", (
        "the span closes before the backslash"
    )
    assert strip_fences_and_comments(r"`a\` b") == r"`a\` b", (
        "the span is restored unchanged for callers that keep inline code"
    )


def test_a_multi_line_span_is_removed_whole() -> None:
    """Recognition matches a closing run on a later line."""
    assert strip_code_and_comments("`one\ntwo` tail") == " tail", (
        "the whole span is removed"
    )


@pytest.mark.parametrize(
    "source",
    [
        "````\ninside\n```\nstill inside\n````\n\nafter\n",
        "```\ninside\n``` extra\nstill inside\n```\n\nafter\n",
        "```\ninside\n~~~~\nstill inside\n```\n\nafter\n",
        "```\ninside\n````\n\nafter\n",
    ],
    ids=["shorter", "trailing-text", "other-marker", "longer"],
)
def test_only_a_permitted_fence_line_closes_a_fence(source: str) -> None:
    """A shorter, differently marked or trailing-text fence line leaves it open."""
    assert strip_fences_and_comments(source) == "\nafter", (
        "everything before the permitted closing fence is removed"
    )
