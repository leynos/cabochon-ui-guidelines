"""Check every local link, front-matter figure and manifest entry.

The `check_links`, `check_front_figure` and `check_manifest` functions validate
link targets, anchors and chapter metadata across `book/*.md`.
`linkcheck.checks` imports all three.
"""

from __future__ import annotations

import typing as typ

if typ.TYPE_CHECKING:
    from pathlib import Path


from markdown_links import image_targets, link_targets, targets
from markdown_structure import anchors

from linkcheck.contract import (
    FRONT_FIGURE_RE,
    FRONT_MATTER_RE,
    FRONT_PART_RE,
    Contract,
    resolved_destination,
)


def _front_matter(text: str) -> str:
    """Return the leading front-matter block, or an empty string."""
    match = FRONT_MATTER_RE.match(text)
    return match.group(1) if match else ""


def check_links(chapters: list[Path], book: Path, problems: list[str]) -> None:
    """Check that every local link target and fragment resolves.

    Parameters
    ----------
    chapters : list[Path]
        The chapter files to check.
    book : Path
        The book directory the chapters belong to.
    problems : list[str]
        The accumulated problems, extended in place.
    """
    root = book.parent
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
                        f"{chapter.relative_to(root)}: missing link target {target}"
                    )
                    continue
            if not fragment or path.suffix != ".md":
                continue
            if fragment not in anchors(path):
                problems.append(
                    f"{chapter.relative_to(root)}: missing anchor "
                    f"#{fragment} in {path.relative_to(root)}"
                )


def check_front_figure(chapters: list[Path], book: Path, problems: list[str]) -> None:
    """Check that each declared front-matter figure exists and is embedded.

    Parameters
    ----------
    chapters : list[Path]
        The chapter files to check.
    book : Path
        The book directory the chapters belong to.
    problems : list[str]
        The accumulated problems, extended in place.
    """
    root = book.parent
    figures = root / "figures"
    for chapter in chapters:
        text = chapter.read_text(encoding="utf-8")
        declared = FRONT_FIGURE_RE.findall(_front_matter(text))
        if not declared:
            continue
        figure = declared[0]
        if not (figures / figure).exists():
            problems.append(f"{chapter.relative_to(root)}: missing figure {figure}")
        if f"../figures/{figure}" not in image_targets(text):
            problems.append(
                f"{chapter.relative_to(root)}: declared figure {figure} "
                "is not embedded as an image in the body"
            )


def check_manifest(
    chapters: list[Path], book: Path, contract: Contract, problems: list[str]
) -> None:
    """Check that the manifest, the chapters and their parts agree.

    Parameters
    ----------
    chapters : list[Path]
        The chapter files to check.
    book : Path
        The book directory the manifest and chapters live in.
    contract : Contract
        The loaded link contract.
    problems : list[str]
        The accumulated problems, extended in place.
    """
    entries = contract.chapters
    declared = {entry["file"] for entry in entries}
    navigation_name = contract.navigation
    present = {path.name for path in chapters if path.name != navigation_name}
    problems.extend(
        f"manifest names missing chapter {name}" for name in sorted(declared - present)
    )
    problems.extend(
        f"chapter {name} is absent from the manifest"
        for name in sorted(present - declared)
    )

    navigation = book / contract.navigation
    nav_text = navigation.read_text(encoding="utf-8")
    nav_paths = {
        resolved
        for target in link_targets(nav_text)
        if (resolved := resolved_destination(book, target)) is not None
    }
    for entry in entries:
        name = entry["file"]
        if (book / name).resolve() not in nav_paths:
            problems.append(f"navigation does not link chapter {name}")
        path = book / name
        if not path.exists():
            continue
        part = FRONT_PART_RE.findall(_front_matter(path.read_text(encoding="utf-8")))
        if not part:
            problems.append(f"{name}: missing part in front matter")
        elif part[0] != entry["part"]:
            problems.append(
                f"{name}: part {part[0]!r} disagrees with manifest {entry['part']!r}"
            )
