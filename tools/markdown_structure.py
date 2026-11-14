"""Shared structural parsing for the book's Markdown checkers.

The link checker and the requirement checker must agree about which headings
create anchors and which Markdown destinations are links or images. This module
is the single implementation they import. It removes HTML comments, fenced code
blocks and, where appropriate, inline code spans before parsing, so text that a
renderer would not display cannot satisfy a structural contract.
"""

from __future__ import annotations

import re
from pathlib import Path

FENCE_OPEN_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)
EXPLICIT_ANCHOR_RE = re.compile(r"<a\s+id=[\"']([^\"']+)[\"']")
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
TARGET_RE = re.compile(
    r"(?P<image>!)?\[[^\]]*\]\(\s*(?P<target>[^)\s]+)"
    r"(?:\s+[\"'][^\"']*[\"'])?\s*\)"
)


def slug(text: str) -> str:
    """Return the anchor a common Markdown renderer gives a heading."""
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    return re.sub(r"\s+", "-", text)


def strip_fences_and_comments(text: str) -> str:
    """Remove fenced code blocks and HTML comments from Markdown.

    Inline code is deliberately kept, because a heading such as
    ``## The `rate` field`` still contributes ``rate`` to its anchor.
    """
    kept: list[str] = []
    fence_char: str | None = None
    fence_length = 0
    for line in COMMENT_RE.sub("", text).splitlines():
        match = FENCE_OPEN_RE.match(line)
        if fence_char is None:
            if match is not None:
                fence_marker = match.group(1)
                fence_char = fence_marker[0]
                fence_length = len(fence_marker)
                continue
            kept.append(line)
            continue
        if match is not None:
            fence_marker = match.group(1)
            remainder = line[match.end() :].strip()
            if (
                fence_marker[0] == fence_char
                and len(fence_marker) >= fence_length
                and not remainder
            ):
                fence_char = None
                fence_length = 0
    return "\n".join(kept)


def strip_code_and_comments(text: str) -> str:
    """Remove comments, fenced blocks and inline code spans."""
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


def targets(text: str, *, images: bool | None = None) -> list[str]:
    """Return rendered Markdown destinations, optionally only images or links."""
    found: list[str] = []
    for match in TARGET_RE.finditer(strip_code_and_comments(text)):
        is_image = match.group("image") is not None
        if images is None or images == is_image:
            found.append(match.group("target"))
    return found


def link_targets(text: str) -> list[str]:
    """Return destinations of ordinary links, excluding embedded images."""
    return targets(text, images=False)


def image_targets(text: str) -> list[str]:
    """Return destinations of embedded images only."""
    return targets(text, images=True)