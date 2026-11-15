"""Extract the destinations a Markdown renderer would follow.

The link checker and the requirement checker must agree about which Markdown
destinations are links or images. This module builds on
:mod:`markdown_structure`'s cleaning, which removes fences, comments and code
spans, and parses the inline, reference and shortcut destinations that remain.
It imports `strip_code_and_comments` from `markdown_structure`; the dependency
is one-way, so there is no circular import.
"""

from __future__ import annotations

import re
import string

from markdown_structure import strip_code_and_comments

_ESCAPABLE = frozenset(string.punctuation)
_ESCAPED_CHAR = "\ue000"
_LITERAL_BACKSLASH = "\ue001"

TARGET_RE = re.compile(
    r"(?P<image>!)?\[[^\]]*\]\(\s*"
    r"(?P<target><[^>\n]*>|(?:[^()\s]|\([^()\s]*\))+)"
    r"(?:\s+[\"'][^\"']*[\"'])?\s*\)"
)
REF_DEF_RE = re.compile(
    r"^ {0,3}\[(?P<label>[^\]]+)\]:\s*(?P<target><[^>\n]*>|\S+)", re.MULTILINE
)
REF_LINK_RE = re.compile(r"(?P<image>!)?\[(?P<text>[^\]]*)\]\[(?P<label>[^\]]*)\]")
SHORTCUT_RE = re.compile(r"(?P<image>!)?\[(?P<label>[^\]]+)\](?![\[(:])")


def _neutralise_escapes(text: str) -> str:
    """Return text with CommonMark backslash escapes made inert.

    A run of backslashes before an escapable character renders as half as many
    literal backslashes, and an odd run makes the character after it literal
    punctuation that can neither open nor close a delimiter. Each is replaced
    with a placeholder so the patterns above cannot read it as syntax.

    Parameters
    ----------
    text : str
        The cleaned Markdown source to prepare.

    Returns
    -------
    str
        The same text with every backslash run resolved.
    """
    out: list[str] = []
    index = 0
    while index < len(text):
        if text[index] != "\\":
            out.append(text[index])
            index += 1
            continue
        end = index
        while end < len(text) and text[end] == "\\":
            end += 1
        run = end - index
        out.append(_LITERAL_BACKSLASH * (run // 2))
        if run % 2:
            if end < len(text) and text[end] in _ESCAPABLE:
                out.append(_ESCAPED_CHAR)
                end += 1
            else:
                out.append(_LITERAL_BACKSLASH)
        index = end
    return "".join(out)


def _unwrap_target(target: str) -> str:
    """Return a destination without the angle brackets CommonMark permits."""
    if target.startswith("<") and target.endswith(">"):
        return target[1:-1]
    return target


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
    """Return rendered Markdown destinations, optionally only images or links.

    Fenced blocks, comments and code spans are removed first, so a
    destination inside them is ignored. Inline destinations are reported
    first, followed by reference links and shortcut references whose label
    has a definition in the text; the angle brackets CommonMark permits
    around a destination are removed. A destination may contain one level of
    balanced parentheses. A backslash before punctuation makes that character
    literal text, and a backslash before a backslash makes the pair a literal
    backslash, so only an odd run of backslashes can escape the delimiter that
    follows it.

    Parameters
    ----------
    text : str
        The Markdown source to scan.
    images : bool | None, optional
        ``True`` keeps only embedded images, ``False`` keeps only ordinary
        links, and ``None`` (the default) keeps both.

    Returns
    -------
    list[str]
        The destinations in source order: inline ones first, then
        ``[text][label]`` references, then shortcut ``[label]`` references.
        Duplicates are retained.
    """
    clean = _neutralise_escapes(strip_code_and_comments(text))
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
    """Return destinations of ordinary links, excluding embedded images.

    Parameters
    ----------
    text : str
        The Markdown source to scan.

    Returns
    -------
    list[str]
        The result of `targets` with ``images`` set to ``False``.
    """
    return targets(text, images=False)


def image_targets(text: str) -> list[str]:
    """Return destinations of embedded images only.

    Parameters
    ----------
    text : str
        The Markdown source to scan.

    Returns
    -------
    list[str]
        The result of `targets` with ``images`` set to ``True``.
    """
    return targets(text, images=True)
