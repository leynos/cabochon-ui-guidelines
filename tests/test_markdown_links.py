"""Tests for the link and image destinations extracted from Markdown.

The extraction must follow CommonMark's backslash rule: punctuation after an
odd run of backslashes is literal text, while an even run leaves literal
backslashes and lets the next delimiter act. A destination may also contain one
level of balanced parentheses.
"""

from __future__ import annotations

import pytest
from markdown_links import image_targets, link_targets, targets


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("[label](missing.md)", ["missing.md"]),
        (r"\[label](missing.md)", []),
        (r"\\[label](missing.md)", ["missing.md"]),
        (r"\\\[label](missing.md)", []),
    ],
    ids=["plain", "escaped", "even-run", "odd-run"],
)
def test_backslash_parity_decides_whether_a_link_opens(
    source: str, expected: list[str]
) -> None:
    """Only an odd run of backslashes leaves the bracket literal."""
    assert link_targets(source) == expected, "the bracket's escape parity is honoured"


@pytest.mark.parametrize(
    ("source", "links", "images"),
    [
        ("![shot](a.png)", [], ["a.png"]),
        (r"\![shot](a.png)", ["a.png"], []),
        (r"\\![shot](a.png)", [], ["a.png"]),
        (r"\\\![shot](a.png)", ["a.png"], []),
    ],
    ids=["image", "escaped-bang", "even-run", "odd-run"],
)
def test_backslash_parity_decides_whether_a_bang_is_an_image(
    source: str, links: list[str], images: list[str]
) -> None:
    """An escaped bang leaves a link, and an even run keeps the image."""
    assert link_targets(source) == links, "the bang's escape parity decides links"
    assert image_targets(source) == images, "the bang's escape parity decides images"


def test_parenthesised_destination_is_kept_whole() -> None:
    """One level of balanced parentheses stays inside the destination."""
    assert targets("[paren](no-such-file(v2).md)") == ["no-such-file(v2).md"], (
        "the destination is captured whole rather than truncated"
    )


def test_angle_bracket_destination_loses_its_brackets() -> None:
    """The angle brackets CommonMark permits around a destination are removed."""
    assert targets("[angle](<01-purpose.md>)") == ["01-purpose.md"], (
        "the reported destination omits the angle brackets"
    )