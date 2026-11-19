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


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (r"[x](file\_name.md)", ["file_name.md"]),
        (r"[x](a\.b.md)", ["a.b.md"]),
        (r"[x](a\\b.md)", [r"a\b.md"]),
    ],
    ids=["escaped-underscore", "escaped-dot", "literal-backslash"],
)
def test_destination_keeps_the_characters_its_escapes_make_literal(
    source: str, expected: list[str]
) -> None:
    """An escaped character reaches the caller as itself, not as a stand-in."""
    assert targets(source) == expected, "the destination holds the literal character"


def test_escaped_labels_resolve_separately() -> None:
    """Labels that differ only in escaped punctuation keep their own targets."""
    text = "[one\\_x]: one.md\n[one\\.x]: two.md\n\n[use][one\\.x]\n"
    assert link_targets(text) == ["two.md"], (
        "each escaped label resolves to its own definition"
    )


def test_an_escaped_label_does_not_merge_with_its_unscaped_spelling() -> None:
    """CommonMark matches labels by source spelling, before escapes resolve."""
    text = "[foo!]: one.md\n[foo\\!]: two.md\n\n[a][foo!]\n[b][foo\\!]\n"
    assert link_targets(text) == ["one.md", "two.md"], (
        "the escaped and unescaped labels name different definitions"
    )


@pytest.mark.parametrize(
    "code", [0xE000, 0xE001, 0xE020, 0xE100, 0xE121], ids=lambda code: f"{code:04X}"
)
def test_a_literal_private_use_character_survives(code: int) -> None:
    """A private-use character in a destination is not read as a stand-in."""
    char = chr(code)
    source = f"[x](a{char}b.md)"
    assert targets(source) == [f"a{char}b.md"], (
        "the destination keeps the character the source declares"
    )


def test_a_literal_private_use_label_is_not_confused_with_punctuation() -> None:
    """A label holding a private-use character keeps its own definition."""
    literal = chr(0xE000)
    text = f"[one{literal}x]: one.md\n[one!x]: two.md\n\n[use][one{literal}x]\n"
    assert link_targets(text) == ["one.md"], (
        "the literal character does not resolve to the escaped punctuation label"
    )


def test_angle_bracket_destination_loses_its_brackets() -> None:
    """The angle brackets CommonMark permits around a destination are removed."""
    assert targets("[angle](<01-purpose.md>)") == ["01-purpose.md"], (
        "the reported destination omits the angle brackets"
    )

def test_labels_that_differ_in_backslash_run_length_stay_distinct() -> None:
    """The stand-ins record each backslash, so the source spelling is kept."""
    text = "[a\\qb]: one.md\n[a\\\\qb]: two.md\n\n[u1][a\\qb]\n[u2][a\\\\qb]\n"
    assert link_targets(text) == ["one.md", "two.md"], (
        "one backslash and two resolve to their own definitions"
    )
