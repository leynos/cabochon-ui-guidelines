#!/usr/bin/env python3
"""Check relative links, figure references and chapter numbering in the book."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOK = ROOT / "book"
FIGURES = ROOT / "figures"

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
FRONT_FIGURE_RE = re.compile(r"^figure:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)


def main() -> int:
    problems: list[str] = []
    chapters = sorted(BOOK.glob("*.md"))
    if not chapters:
        problems.append("no chapters found under book/")

    for chapter in chapters:
        text = chapter.read_text(encoding="utf-8")
        for target in LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path = (chapter.parent / target.split("#", 1)[0]).resolve()
            if not path.exists():
                problems.append(f"{chapter.relative_to(ROOT)}: missing link target {target}")

        for figure in FRONT_FIGURE_RE.findall(text):
            if not (FIGURES / figure).exists():
                problems.append(f"{chapter.relative_to(ROOT)}: missing figure {figure}")

    figures = sorted(FIGURES.glob("*.svg"))
    if not figures:
        problems.append("no SVG figures found under figures/")

    expected = 40
    numbered = [p for p in chapters if re.match(r"^\d{2}-", p.name)]
    if len(numbered) != expected:
        problems.append(f"expected {expected} numbered chapters, found {len(numbered)}")
    seen: set[int] = set()
    for chapter in numbered:
        number = int(chapter.name[:2])
        if number in seen:
            problems.append(f"duplicate chapter number {number:02d}")
        seen.add(number)
    missing = sorted(set(range(1, expected + 1)) - seen)
    if missing:
        problems.append("missing chapter numbers: " + ", ".join(f"{n:02d}" for n in missing))

    if problems:
        for problem in problems:
            fail(problem)
        return 1

    print(f"links: ok ({len(chapters)} chapters, {len(figures)} figures)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
