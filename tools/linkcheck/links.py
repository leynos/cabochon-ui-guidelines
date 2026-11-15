"""Check every local link, front-matter figure and manifest entry.

The `check_links`, `check_front_figure` and `check_manifest` functions validate
link targets, anchors and chapter metadata across `book/*.md`.
`linkcheck.checks` imports all three.
"""

from __future__ import annotations

import typing as typ

if typ.TYPE_CHECKING:
    from pathlib import Path


from markdown_structure import anchors, image_targets, link_targets, targets

from linkcheck.contract import (
    BOOK,
    CONTRACT,
    FIGURES,
    FRONT_FIGURE_RE,
    FRONT_PART_RE,
    ROOT,
)


def check_links(chapters: list[Path], problems: list[str]) -> None:
    """Check that every local link target and fragment resolves."""
    for chapter in chapters:
        text = chapter.read_text(encoding="utf-8")
        for target in targets(text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            if target.startswith("#"):
                path = chapter
                fragment = target[1:]
            else:
                path_part, _, fragment = target.partition("#")
                path = (chapter.parent / path_part).resolve()
                if not path.exists():
                    problems.append(
                        f"{chapter.relative_to(ROOT)}: missing link target {target}"
                    )
                    continue
            if not fragment or path.suffix != ".md":
                continue
            if fragment not in anchors(path):
                problems.append(
                    f"{chapter.relative_to(ROOT)}: missing anchor "
                    f"#{fragment} in {path.relative_to(ROOT)}"
                )


def check_front_figure(chapters: list[Path], problems: list[str]) -> None:
    """Check that each declared front-matter figure exists and is embedded."""
    for chapter in chapters:
        text = chapter.read_text(encoding="utf-8")
        declared = FRONT_FIGURE_RE.findall(text)
        if not declared:
            continue
        figure = declared[0]
        if not (FIGURES / figure).exists():
            problems.append(f"{chapter.relative_to(ROOT)}: missing figure {figure}")
        if f"../figures/{figure}" not in image_targets(text):
            problems.append(
                f"{chapter.relative_to(ROOT)}: declared figure {figure} "
                "is not embedded as an image in the body"
            )


def check_manifest(chapters: list[Path], problems: list[str]) -> None:
    """Check that the manifest, the chapters and their parts agree."""
    entries = CONTRACT["chapters"]
    declared = {entry["file"] for entry in entries}
    navigation_name = CONTRACT["navigation"]
    present = {path.name for path in chapters if path.name != navigation_name}
    problems.extend(
        f"manifest names missing chapter {name}" for name in sorted(declared - present)
    )
    problems.extend(
        f"chapter {name} is absent from the manifest"
        for name in sorted(present - declared)
    )

    navigation = BOOK / CONTRACT["navigation"]
    nav_text = navigation.read_text(encoding="utf-8")
    nav_paths = {target.partition("#")[0] for target in link_targets(nav_text)}
    for entry in entries:
        name = entry["file"]
        if name not in nav_paths:
            problems.append(f"navigation does not link chapter {name}")
        path = BOOK / name
        if not path.exists():
            continue
        part = FRONT_PART_RE.findall(path.read_text(encoding="utf-8"))
        if not part:
            problems.append(f"{name}: missing part in front matter")
        elif part[0] != entry["part"]:
            problems.append(
                f"{name}: part {part[0]!r} disagrees with manifest {entry['part']!r}"
            )
