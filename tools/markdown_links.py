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

_PUNCTUATION = tuple(sorted(string.punctuation))
_ESCAPABLE = frozenset(_PUNCTUATION)
_STANDIN_WIDTH = len(_PUNCTUATION) + 1
_PRIVATE_USE_RANGES = ((0xE000, 0xF900), (0xF0000, 0xFFFFE), (0x100000, 0x10FFFE))

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


def _standin_base(text: str) -> int:
    """Return a private-use base whose stand-ins do not occur in ``text``.

    The stand-ins occupy a run of ``_STANDIN_WIDTH`` consecutive private-use
    code points, so any character in that run inside the source would be read
    back as a stand-in. The first run the source does not use is returned.

    Parameters
    ----------
    text : str
        The text that will be scanned after the stand-ins are substituted.

    Returns
    -------
    int
        The code point the run starts at.

    Raises
    ------
    ValueError
        If every private-use run is too crowded to hold the stand-ins.
    """
    used = sorted({ord(char) for char in text})
    for start, end in _PRIVATE_USE_RANGES:
        base = start
        for code in used:
            if code < base:
                continue
            if code - base >= _STANDIN_WIDTH:
                break
            base = code + 1
        if base + _STANDIN_WIDTH <= end:
            return base
    raise ValueError("no private-use range is free for escape stand-ins")


def _placeholder(char: str, base: int) -> str:
    """Return the stand-in that keeps an escaped character out of the syntax."""
    return chr(base + _PUNCTUATION.index(char) + 1)


def _restore(text: str, base: int) -> str:
    """Return text with each stand-in turned back into the character it holds."""
    out: list[str] = []
    for char in text:
        code = ord(char) - base
        if code == 0:
            out.append("\\")
        elif 0 < code <= len(_PUNCTUATION):
            out.append(_PUNCTUATION[code - 1])
        else:
            out.append(char)
    return "".join(out)


def _neutralise_escapes(text: str, base: int) -> str:
    """Return text with CommonMark backslash escapes made inert.

    A run of backslashes before an escapable character renders as half as many
    literal backslashes, and an odd run makes the character after it literal
    punctuation that can neither open nor close a delimiter. Each is replaced
    with a distinct stand-in drawn from the ``base`` run, which `_restore`
    turns back into the character it stood for, so a destination keeps the text
    the renderer would follow.

    Parameters
    ----------
    text : str
        The cleaned Markdown source to prepare.
    base : int
        The start of the private-use run `_standin_base` found free.

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
        out.append(chr(base) * (run // 2))
        if run % 2:
            if end < len(text) and text[end] in _ESCAPABLE:
                out.append(_placeholder(text[end], base))
                end += 1
            else:
                out.append(chr(base))
        index = end
    return "".join(out)


def _unwrap_target(target: str, base: int) -> str:
    """Return a destination without its angle brackets and stand-ins."""
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    return _restore(target, base)


def _normalise_label(label: str, base: int) -> str:
    """Normalise a reference label for comparison."""
    return re.sub(r"\s+", " ", _restore(label, base).strip()).casefold()


def _reference_definitions(text: str, base: int) -> dict[str, str]:
    """Collect the first definition of each reference label in a chapter."""
    definitions: dict[str, str] = {}
    for match in REF_DEF_RE.finditer(text):
        label = _normalise_label(match.group("label"), base)
        definitions.setdefault(label, _unwrap_target(match.group("target"), base))
    return definitions


def _wanted(*, is_image: bool, images: bool | None) -> bool:
    """Return whether a destination of this kind belongs in the result."""
    return images is None or images == is_image


def _inside_span(position: int, spans: list[tuple[int, int]]) -> bool:
    """Return whether a position lies inside one of the given spans."""
    return any(start <= position < end for start, end in spans)


def _reference_targets(
    text: str, definitions: dict[str, str], base: int, *, images: bool | None
) -> list[str]:
    """Collect the reference targets used in a chapter."""
    found: list[str] = []
    consumed: list[tuple[int, int]] = []
    for match in REF_LINK_RE.finditer(text):
        consumed.append(match.span())
        label = match.group("label") or match.group("text")
        target = definitions.get(_normalise_label(label, base))
        is_image = match.group("image") is not None
        if target is not None and _wanted(is_image=is_image, images=images):
            found.append(target)
    for match in SHORTCUT_RE.finditer(text):
        if _inside_span(match.start(), consumed):
            continue
        target = definitions.get(_normalise_label(match.group("label"), base))
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
    follows it. A reported destination holds those literal characters, not the
    stand-ins used while the text is scanned, and two labels that differ only
    in escaped punctuation resolve to their own definitions. The stand-ins come
    from a private-use run the source does not use, so a literal private-use
    character in a destination or a label is reported unchanged.

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
    source = strip_code_and_comments(text)
    base = _standin_base(source)
    clean = _neutralise_escapes(source, base)
    found: list[str] = []
    for match in TARGET_RE.finditer(clean):
        is_image = match.group("image") is not None
        if _wanted(is_image=is_image, images=images):
            found.append(_unwrap_target(match.group("target"), base))
    definitions = _reference_definitions(clean, base)
    if definitions:
        found.extend(_reference_targets(clean, definitions, base, images=images))
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
