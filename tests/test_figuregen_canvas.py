"""Tests for the canvas text wrapping the figure generator shares.

`wrap_words` decides where a paragraph breaks, so a line must stay within the
declared width unless a single word cannot, and wrapping must never split or
lose a word.
"""

from __future__ import annotations

import pytest
from figuregen.canvas import wrap_words

SENTENCE = "The quick brown fox jumps over the lazy dog"


def test_no_line_exceeds_the_declared_width() -> None:
    """Every line fits the limit, because no word in the sample is too long."""
    lines = wrap_words(SENTENCE, 12)
    assert lines, "the sentence wraps to at least one line"
    assert all(len(line) <= 12 for line in lines), "no line overruns the limit"


def test_wrapping_neither_splits_nor_loses_a_word() -> None:
    """Joining the lines reproduces the sentence's own words in order."""
    assert " ".join(wrap_words(SENTENCE, 12)).split() == SENTENCE.split(), (
        "every word survives whole and in its original order"
    )


def test_a_word_longer_than_the_limit_is_kept_whole() -> None:
    """The single line that must overrun keeps its word unsplit."""
    assert wrap_words("supercalifragilistic a", 5) == [
        "supercalifragilistic",
        "a",
    ], "an over-long word is neither split nor dropped"


@pytest.mark.parametrize("value", ["", "   ", "\n"], ids=["empty", "spaces", "newline"])
def test_text_without_words_wraps_to_nothing(value: str) -> None:
    """Text that holds no word produces no line."""
    assert wrap_words(value, 10) == [], "no line is emitted for empty text"