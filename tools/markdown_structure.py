"""Shared structural parsing for the book's Markdown checkers.

The link checker and the requirement checker must agree about which headings
create anchors and which Markdown destinations are links or images. This module
is the single implementation they import. It removes HTML comments, fenced code
blocks and, where appropriate, code spans before parsing, so text that a
renderer would not display cannot satisfy a structural contract.

Comments and fences are scanned together: a comment delimiter inside a fenced
example is literal text, while a fence marker inside a comment is not a fence.
"""

from __future__ import annotations

import re
import typing as typ

if typ.TYPE_CHECKING:
    from pathlib import Path

FENCE_OPEN_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)
EXPLICIT_ANCHOR_RE = re.compile(r"<a\s+id=[\"']([^\"']+)[\"']")
INLINE_CODE_RE = re.compile(r"(?<!`)(`+)(?!`)(.*?)(?<!`)\1(?!`)", re.DOTALL)
TARGET_RE = re.compile(
    r"(?P<image>!)?\[[^\]]*\]\(\s*(?P<target>[^)\s]+)"
    r"(?:\s+[\"'][^\"']*[\"'])?\s*\)"
)
REF_DEF_RE = re.compile(
    r"^ {0,3}\[(?P<label>[^\]]+)\]:\s*(?P<target>\S+)", re.MULTILINE
)
REF_LINK_RE = re.compile(r"(?P<image>!)?\[(?P<text>[^\]]*)\]\[(?P<label>[^\]]*)\]")
SHORTCUT_RE = re.compile(r"(?P<image>!)?\[(?P<label>[^\]]+)\](?![\[(:])")


def slug(text: str) -> str:
    """Return the anchor a common Markdown renderer gives a heading."""
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    return re.sub(r"\s+", "-", text)


def _remove_comments(line: str, *, in_comment: bool) -> tuple[str, bool]:
    """Remove HTML comments from one line, carrying an open comment forward."""
    if in_comment:
        end = line.find("-->")
        if end == -1:
            return "", True
        line = line[end + 3 :]
    kept: list[str] = []
    while True:
        start = line.find("<!--")
        if start == -1:
            kept.append(line)
            return "".join(kept), False
        kept.append(line[:start])
        end = line.find("-->", start + 4)
        if end == -1:
            return "".join(kept), True
        line = line[end + 3 :]


def _closes_fence(
    marker: str, remainder: str, fence_char: str, fence_length: int
) -> bool:
    """Return whether a fence marker line closes the fence that is open."""
    if marker[0] != fence_char:
        return False
    return len(marker) >= fence_length and not remainder.strip()


def strip_fences_and_comments(text: str) -> str:
    """Remove fenced code blocks and HTML comments from Markdown.

    Inline code is deliberately kept, because a heading such as
    ``## The `rate` field`` still contributes ``rate`` to its anchor. Comment
    delimiters inside a fence remain literal, and a fence marker inside a
    comment does not open or close a fence.
    """
    kept: list[str] = []
    fence_char: str | None = None
    fence_length = 0
    in_comment = False
    for raw_line in text.splitlines():
        if fence_char is not None:
            match = FENCE_OPEN_RE.match(raw_line)
            if match is None:
                continue
            if _closes_fence(
                match.group(1), raw_line[match.end() :], fence_char, fence_length
            ):
                fence_char = None
                fence_length = 0
            continue
        line, in_comment = _remove_comments(raw_line, in_comment=in_comment)
        match = FENCE_OPEN_RE.match(line)
        if match is not None:
            marker = match.group(1)
            fence_char = marker[0]
            fence_length = len(marker)
            continue
        kept.append(line)
    return "\n".join(kept)


def strip_code_and_comments(text: str) -> str:
    """Remove comments, fenced blocks and code spans, including multi-line ones."""
    return INLINE_CODE_RE.sub("", strip_fences_and_comments(text))


def anchors(path: Path) -> set[str]:
    """Return every anchor a renderer would expose for the Markdown file."""
    text = path.read_text(encoding="utf-8")
    visible = strip_fences_and_comments(text)
    found: set[str] = set()
    seen: dict[str, int] = {}
    for heading in HEADING_RE.findall(visible):
        base = slug(heading)
        count = seen.get(base, 0)
        found.add(base if count == 0 else f"{base}-{count}")
        seen[base] = count + 1
    found.update(EXPLICIT_ANCHOR_RE.findall(strip_code_and_comments(text)))
    return found


def _normalise_label(label: str) -> str:
    """Normalise a reference label for comparison."""
    return re.sub(r"\s+", " ", label.strip()).casefold()


def _reference_definitions(text: str) -> dict[str, str]:
    """Collect the reference definitions declared in a chapter."""
    return {
        _normalise_label(match.group("label")): match.group("target")
        for match in REF_DEF_RE.finditer(text)
    }


def _wanted(*, is_image: bool, images: bool | None) -> bool:
    """Return whether a destination of this kind belongs in the result."""
    return images is None or images == is_image


def _reference_targets(
    text: str, definitions: dict[str, str], *, images: bool | None
) -> list[str]:
    """Collect the reference targets used in a chapter."""
    found: list[str] = []
    for match in REF_LINK_RE.finditer(text):
        label = match.group("label") or match.group("text")
        target = definitions.get(_normalise_label(label))
        is_image = match.group("image") is not None
        if target is not None and _wanted(is_image=is_image, images=images):
            found.append(target)
    for match in SHORTCUT_RE.finditer(text):
        target = definitions.get(_normalise_label(match.group("label")))
        is_image = match.group("image") is not None
        if target is not None and _wanted(is_image=is_image, images=images):
            found.append(target)
    return found


def targets(text: str, *, images: bool | None = None) -> list[str]:
    """Return rendered Markdown destinations, optionally only images or links."""
    clean = strip_code_and_comments(text)
    found: list[str] = []
    for match in TARGET_RE.finditer(clean):
        is_image = match.group("image") is not None
        if _wanted(is_image=is_image, images=images):
            found.append(match.group("target"))
    definitions = _reference_definitions(clean)
    if definitions:
        found.extend(_reference_targets(clean, definitions, images=images))
    return found


def link_targets(text: str) -> list[str]:
    """Return destinations of ordinary links, excluding embedded images."""
    return targets(text, images=False)


def image_targets(text: str) -> list[str]:
    """Return destinations of embedded images only."""
    return targets(text, images=True)
