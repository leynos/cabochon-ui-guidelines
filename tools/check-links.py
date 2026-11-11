#!/usr/bin/env python3
"""Check the book's links and its structural contract.

The mechanical checks cover relative paths, real heading anchors and the
relationship between a chapter's declared figure and the figure it embeds. The
semantic checks cover the contents graph, requirement identifiers, state and
profile ownership, and the command and resource relationships. They are
structural: they do not parse prose or assert whole paragraphs.

Run from the repository root with ``python3 -I tools/check-links.py``. Pass
``--self-test`` to apply negative mutations to a temporary copy and confirm
that each check detects the defect it claims to prevent.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOK = ROOT / "book"
FIGURES = ROOT / "figures"
CONTRACT = json.loads((ROOT / "tools" / "book-contract.json").read_text(encoding="utf-8"))

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
FRONT_FIGURE_RE = re.compile(r"^figure:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)
FRONT_PART_RE = re.compile(r"^part:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)
EXPLICIT_ANCHOR_RE = re.compile(r"<a\s+id=[\"']([^\"']+)[\"']")
REQUIREMENT_RE = re.compile(r"\*\*([A-Z]{3}-[0-9]{2})\*\*")
OWNER_RE = re.compile(r"Owner:\s*\[[^\]]*\]\(([^)]+)\)")


def slug(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    return re.sub(r"\s+", "-", text)


def anchors(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    found = {slug(heading) for heading in HEADING_RE.findall(text)}
    found.update(EXPLICIT_ANCHOR_RE.findall(text))
    return found


def link_targets(text: str) -> list[str]:
    targets: list[str] = []
    for raw in LINK_RE.findall(text):
        target = raw.strip().split(" ", 1)[0]
        targets.append(target)
    return targets


def check_links(chapters: list[Path], problems: list[str]) -> None:
    for chapter in chapters:
        text = chapter.read_text(encoding="utf-8")
        for target in link_targets(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_part, _, fragment = target.partition("#")
            path = (chapter.parent / path_part).resolve()
            if not path.exists():
                problems.append(
                    f"{chapter.relative_to(ROOT)}: missing link target {target}"
                )
                continue
            if fragment and path.suffix == ".md":
                if fragment not in anchors(path):
                    problems.append(
                        f"{chapter.relative_to(ROOT)}: missing anchor "
                        f"#{fragment} in {path.relative_to(ROOT)}"
                    )


def check_front_figure(chapters: list[Path], problems: list[str]) -> None:
    for chapter in chapters:
        text = chapter.read_text(encoding="utf-8")
        declared = FRONT_FIGURE_RE.findall(text)
        if not declared:
            continue
        figure = declared[0]
        if not (FIGURES / figure).exists():
            problems.append(f"{chapter.relative_to(ROOT)}: missing figure {figure}")
        if f"../figures/{figure}" not in text:
            problems.append(
                f"{chapter.relative_to(ROOT)}: declared figure {figure} "
                "is not embedded in the body"
            )


def check_manifest(chapters: list[Path], problems: list[str]) -> None:
    entries = CONTRACT["chapters"]
    declared = {entry["file"] for entry in entries}
    navigation_name = CONTRACT["navigation"]
    present = {path.name for path in chapters if path.name != navigation_name}
    for name in sorted(declared - present):
        problems.append(f"manifest names missing chapter {name}")
    for name in sorted(present - declared):
        problems.append(f"chapter {name} is absent from the manifest")

    navigation = BOOK / CONTRACT["navigation"]
    nav_text = navigation.read_text(encoding="utf-8")
    for entry in entries:
        name = entry["file"]
        if f"]({name})" not in nav_text and f"]({name}#" not in nav_text:
            problems.append(f"navigation does not link chapter {name}")
        path = BOOK / name
        if not path.exists():
            continue
        part = FRONT_PART_RE.findall(path.read_text(encoding="utf-8"))
        if not part:
            problems.append(f"{name}: missing part in front matter")
        elif part[0] != entry["part"]:
            problems.append(
                f"{name}: part {part[0]!r} disagrees with manifest "
                f"{entry['part']!r}"
            )


def check_requirements(problems: list[str]) -> None:
    spec = CONTRACT["requirements"]
    checklist = BOOK / spec["checklist"]
    text = checklist.read_text(encoding="utf-8")
    pattern = re.compile(spec["id_pattern"])
    seen: set[str] = set()
    for block in text.split("- [ ] ")[1:]:
        ids = REQUIREMENT_RE.findall(block)
        if not ids:
            problems.append("checklist item has no requirement identifier")
            continue
        identifier = ids[0]
        if not pattern.match(identifier):
            problems.append(f"requirement {identifier} does not match the pattern")
        if identifier in seen:
            problems.append(f"duplicate requirement identifier {identifier}")
        seen.add(identifier)
        owners = OWNER_RE.findall(block)
        if not owners:
            problems.append(f"requirement {identifier} names no owner")
        for owner in owners:
            path_part, _, fragment = owner.partition("#")
            path = (checklist.parent / path_part).resolve()
            if not path.exists():
                problems.append(
                    f"requirement {identifier}: missing owner {owner}"
                )
            elif fragment and fragment not in anchors(path):
                problems.append(
                    f"requirement {identifier}: missing owner anchor {owner}"
                )


def check_states(problems: list[str]) -> None:
    spec = CONTRACT["states"]
    for group, owner_key in (
        ("live", "live_owner"),
        ("resolution", "resolution_owner"),
    ):
        owner = BOOK / spec[owner_key]
        text = owner.read_text(encoding="utf-8")
        for state in spec[group]:
            if state not in text:
                problems.append(
                    f"{owner.name}: {group} state {state!r} is not declared"
                )


def check_profiles(problems: list[str]) -> None:
    spec = CONTRACT["profiles"]
    owner = BOOK / spec["owner"]
    text = owner.read_text(encoding="utf-8")
    for name in spec["names"]:
        if name not in text:
            problems.append(f"{owner.name}: profile {name!r} is not declared")


def check_commands(problems: list[str]) -> None:
    spec = CONTRACT["commands"]
    owner = BOOK / spec["record_owner"]
    if not owner.exists():
        problems.append(f"command record owner {owner.name} is missing")
        return
    for view in spec["views"]:
        path = BOOK / view
        if not path.exists():
            problems.append(f"command view {view} is missing")
            continue
        if f"]({owner.name})" not in path.read_text(encoding="utf-8"):
            problems.append(f"{view}: does not reference the command record owner")


def check_resources(problems: list[str]) -> None:
    spec = CONTRACT["resources"]
    owner = BOOK / spec["owner"]
    if not owner.exists():
        problems.append(f"resource owner {owner.name} is missing")
        return
    for consumer in spec["consumers"]:
        path = BOOK / consumer
        if not path.exists():
            problems.append(f"resource consumer {consumer} is missing")
            continue
        if f"]({owner.name})" not in path.read_text(encoding="utf-8"):
            problems.append(f"{consumer}: does not reference the resource owner")


def run_checks() -> list[str]:
    problems: list[str] = []
    chapters = sorted(BOOK.glob("*.md"))
    if not chapters:
        problems.append("no chapters found under book/")
        return problems
    check_links(chapters, problems)
    check_front_figure(chapters, problems)
    check_manifest(chapters, problems)
    check_requirements(problems)
    check_states(problems)
    check_profiles(problems)
    check_commands(problems)
    check_resources(problems)
    return problems


def self_test() -> int:
    """Apply one mutation per check and confirm the checker rejects it."""
    mutations = {
        "orphan chapter": lambda book: (book / "99-orphan.md").write_text(
            "---\ntitle: Orphan\npart: Breadth\n---\n\n# Orphan\n", encoding="utf-8"
        ),
        "broken anchor": lambda book: (book / "01-purpose.md").write_text(
            (book / "01-purpose.md").read_text(encoding="utf-8")
            + "\n[broken](02-cabochon-character.md#no-such-heading)\n",
            encoding="utf-8",
        ),
        "mismatched figure": lambda book: (book / "02-cabochon-character.md").write_text(
            (book / "02-cabochon-character.md")
            .read_text(encoding="utf-8")
            .replace("fig-02-small-world.svg", "fig-01-map.svg", 1),
            encoding="utf-8",
        ),
        "missing requirement owner": lambda book: (book / "40-checklist.md").write_text(
            (book / "40-checklist.md")
            .read_text(encoding="utf-8")
            .replace("Owner: [Ecosystem map](03-ecosystem-map.md).", "", 1),
            encoding="utf-8",
        ),
        "missing state": lambda book: (book / "08-live-relationships.md").write_text(
            (book / "08-live-relationships.md")
            .read_text(encoding="utf-8")
            .replace("Refreshing", "Updating"),
            encoding="utf-8",
        ),
        "missing profile": lambda book: (book / "appendix-references.md").write_text(
            (book / "appendix-references.md")
            .read_text(encoding="utf-8")
            .replace("substrate", "foundation"),
            encoding="utf-8",
        ),
        "missing command relation": lambda book: (book / "23-command-palette.md").write_text(
            (book / "23-command-palette.md")
            .read_text(encoding="utf-8")
            .replace("](10-menus.md)", "](11-toolbars-status.md)"),
            encoding="utf-8",
        ),
        "missing resource relation": lambda book: (book / "16-icons.md").write_text(
            (book / "16-icons.md")
            .read_text(encoding="utf-8")
            .replace("](38-localization.md)", "](13-typography.md)"),
            encoding="utf-8",
        ),
    }
    failures: list[str] = []
    for label, mutate in mutations.items():
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "repo"
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(".git", "build"))
            mutate(copy / "book")
            result = subprocess.run(
                [sys.executable, "-I", str(copy / "tools" / "check-links.py")],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                failures.append(f"self-test: {label} was not detected")
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print(f"links: self-test detected all {len(mutations)} mutations")
    return 0


def main() -> int:
    if "--self-test" in sys.argv[1:]:
        return self_test()
    problems = run_checks()
    if problems:
        for problem in problems:
            print(f"error: {problem}", file=sys.stderr)
        return 1
    chapters = len(list(BOOK.glob("*.md")))
    figures = len(list(FIGURES.glob("*.svg")))
    print(f"links: ok ({chapters} chapters, {figures} figures)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
