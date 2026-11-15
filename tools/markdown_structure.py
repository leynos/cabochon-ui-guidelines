"""Shared structural parsing for the book's Markdown checkers.

The link checker and the requirement checker must agree about which headings
create anchors and which Markdown destinations are links or images. This module
is the single implementation they import. It removes HTML comments, fenced code
blocks and, where appropriate, code spans before parsing, so text that a
renderer would not display cannot satisfy a structural contract.

Comments and fences are scanned together: a comment delimiter inside a fenced
example is literal text, while a fence marker inside a comment is not a fence.
Inline code is masked while those scans run, so a literal comment delimiter
inside a code span cannot hide the rest of a chapter; the spans are restored
afterwards because headings keep their inline code.
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
    r"(?P<image>!)?\[[^\]]*\]\(\s*(?P<target><[^>\n]*>|[^)\s]+)"
    r"(?:\s+[\"'][^\"']*[\"'])?\s*\)"
)
REF_DEF_RE = re.compile(
    r"^ {0,3}\[(?P<label>[^\]]+)\]:\s*(?P<target><[^>\n]*>|\S+)", re.MULTILINE
)
REF_LINK_RE = re.compile(r"(?P<image>!)?\[(?P<text>[^\]]*)\]\[(?P<label>[^\]]*)\]")
SHORTCUT_RE = re.compile(r"(?P<image>!)?\[(?P<label>[^\]]+)\](?![\[(:])")
CHECKLIST_ITEM_RE = re.compile(r"^ {0,3}- \[[ xX]\] ", re.MULTILINE)
CODE_PLACEHOLDER_RE = re.compile(r"\x00([0-9]+)\x00")


def slug(text: str) -> str:
    """Return the anchor a common Markdown renderer gives a heading."""
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    return re.sub(r"\s+", "-", text)


def _unwrap_target(target: str) -> str:
    """Return a destination without the angle brackets CommonMark permits."""
    if target.startswith("<") and target.endswith(">"):
        return target[1:-1]
    return target


def _placeholder(index: int) -> str:
    """Return the masked-code token that stands in for a code span."""
    return f"\x00{index}\x00"


def _earliest(candidate: int, *others: int) -> bool:
    """Return whether a non-negative index precedes every other index."""
    if candidate < 0:
        return False
    return all(other < 0 or candidate < other for other in others)


def _scan_fence_line(
    text: str, position: int, fence: tuple[str, int] | None, kept: list[str]
) -> tuple[int, tuple[str, int] | None, bool]:
    """Consume one whole line when it opens, continues or closes a fence."""
    end = text.find("\n", position)
    end = len(text) if end == -1 else end + 1
    line = text[position:end]
    marker = FENCE_OPEN_RE.match(line)
    if fence is not None:
        if marker is not None and _closes_fence(
            marker.group(1), line[marker.end() :], fence[0], fence[1]
        ):
            fence = None
        kept.append(line)
        return end, fence, True
    if marker is None:
        return position, None, False
    kept.append(line)
    return end, (marker.group(1)[0], len(marker.group(1))), True


def _scan_comment(text: str, position: int, kept: list[str]) -> tuple[int, bool]:
    """Consume text inside an HTML comment that the scan has entered."""
    end = text.find("-->", position)
    if end == -1:
        kept.append(text[position:])
        return len(text), True
    kept.append(text[position : end + 3])
    return end + 3, False


def _scan_inline(
    text: str, position: int, kept: list[str], spans: list[str]
) -> tuple[int, bool]:
    """Consume ordinary text up to the next comment, code span or line end."""
    comment = text.find("<!--", position)
    span = INLINE_CODE_RE.search(text, position)
    span_start = span.start() if span is not None else -1
    newline = text.find("\n", position)
    if span is not None and _earliest(span_start, comment, newline):
        kept.extend((text[position:span_start], _placeholder(len(spans))))
        spans.append(span.group(0))
        return span.end(), False
    if _earliest(comment, newline, span_start):
        kept.extend((text[position:comment], "<!--"))
        return comment + 4, True
    end = len(text) if newline == -1 else newline + 1
    kept.append(text[position:end])
    return end, False


def _mask_code_spans(text: str) -> tuple[str, list[str]]:
    """Replace code spans outside fences and comments with placeholders."""
    kept: list[str] = []
    spans: list[str] = []
    fence: tuple[str, int] | None = None
    in_comment = False
    position = 0
    while position < len(text):
        starts_line = position == 0 or text[position - 1] == "\n"
        if starts_line and not in_comment:
            position, fence, consumed = _scan_fence_line(text, position, fence, kept)
            if consumed:
                continue
        if in_comment:
            position, in_comment = _scan_comment(text, position, kept)
            continue
        position, in_comment = _scan_inline(text, position, kept, spans)
    return "".join(kept), spans


def _restore_code_spans(text: str, spans: list[str]) -> str:
    """Put the masked code spans back into the scanned text."""

    def restore(match: re.Match[str]) -> str:
        """Return the original code span behind one placeholder."""
        return spans[int(match.group(1))]

    return CODE_PLACEHOLDER_RE.sub(restore, text)


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
    ``## The `rate` field`` still contributes ``rate`` to its anchor. Code
    spans are masked while comments and fences are located, so a literal
    comment delimiter inside a span is not treated as a comment. Comment
    delimiters inside a fence remain literal, and a fence marker inside a
    comment does not open or close a fence.
    """
    masked, spans = _mask_code_spans(text)
    kept: list[str] = []
    fence_char: str | None = None
    fence_length = 0
    in_comment = False
    for raw_line in masked.splitlines():
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
    return _restore_code_spans("\n".join(kept), spans)


def strip_code_and_comments(text: str) -> str:
    """Remove comments, fenced blocks and code spans, including multi-line ones."""
    return INLINE_CODE_RE.sub("", strip_fences_and_comments(text))


def checklist_items(text: str) -> list[str]:
    """Split text into task-list item bodies, checked or unchecked."""
    return CHECKLIST_ITEM_RE.split(text)[1:]


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
    """Collect the first definition of each reference label in a chapter."""
    definitions: dict[str, str] = {}
    for match in REF_DEF_RE.finditer(text):
        label = _normalise_label(match.group("label"))
        definitions.setdefault(label, _unwrap_target(match.group("target")))
    return definitions


def _wanted(*, is_image: bool, images: bool | None) -> bool:
    """Return whether a destination of this kind belongs in the result."""
    return images is None or images == is_image


def _inside_span(position: int, spans: list[tuple[int, int]]) -> bool:
    """Return whether a position lies inside one of the given spans."""
    return any(start <= position < end for start, end in spans)


def _reference_targets(
    text: str, definitions: dict[str, str], *, images: bool | None
) -> list[str]:
    """Collect the reference targets used in a chapter."""
    found: list[str] = []
    consumed: list[tuple[int, int]] = []
    for match in REF_LINK_RE.finditer(text):
        consumed.append(match.span())
        label = match.group("label") or match.group("text")
        target = definitions.get(_normalise_label(label))
        is_image = match.group("image") is not None
        if target is not None and _wanted(is_image=is_image, images=images):
            found.append(target)
    for match in SHORTCUT_RE.finditer(text):
        if _inside_span(match.start(), consumed):
            continue
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
            found.append(_unwrap_target(match.group("target")))
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
