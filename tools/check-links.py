#!/usr/bin/env python3
"""Check the book's links and its structural contract.

Links, images and headings are parsed from Markdown after HTML comments, fenced
code blocks and inline code spans have been removed. Local fragments are checked
against the current file as well as other files, and duplicate headings receive
the same numeric suffixes a Markdown renderer assigns. The semantic checks cover
the contents graph, requirement identifiers, state and profile ownership, and
the command and resource relationships. They are structural: they do not parse
prose or assert whole paragraphs.

Run from the repository root with ``python3 -I tools/check-links.py``. Pass
``--self-test`` to require a clean baseline, prove each mutation actually
changed its target, and assert the expected diagnostic for every defect.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from markdown_structure import (  # noqa: E402
    anchors,
    image_targets,
    slug,
    strip_code_and_comments,
    targets,
)

ROOT = Path(__file__).resolve().parent.parent
BOOK = ROOT / "book"
FIGURES = ROOT / "figures"
CONTRACT = json.loads((ROOT / "tools" / "book-contract.json").read_text(encoding="utf-8"))

FRONT_FIGURE_RE = re.compile(r"^figure:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)
FRONT_PART_RE = re.compile(r"^part:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)
REQUIREMENT_RE = re.compile(r"\*\*([A-Z]{3}-[0-9]{2})\*\*")
OWNER_RE = re.compile(r"Owner:\s*\[[^\]]*\]\(([^)]+)\)")


def check_links(chapters: list[Path], problems: list[str]) -> None:
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
        if f"../figures/{figure}" not in image_targets(text):
            problems.append(
                f"{chapter.relative_to(ROOT)}: declared figure {figure} "
                "is not embedded as an image in the body"
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
        if not pattern.fullmatch(identifier):
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


def first_cells(text: str) -> set[str]:
    cells: set[str] = set()
    for line in strip_code_and_comments(text).splitlines():
        if line.startswith("|"):
            parts = [part.strip().strip("*").strip() for part in line.strip("|").split("|")]
            if parts and parts[0] and not set(parts[0]) <= {"-", ":"}:
                cells.add(parts[0])
    return cells


def section(text: str, heading: str) -> str:
    kept: list[str] = []
    active = False
    for line in text.splitlines():
        if line.startswith("## "):
            active = slug(line[3:]) == heading
            continue
        if active:
            kept.append(line)
    return "\n".join(kept)


def check_states(problems: list[str]) -> None:
    spec = CONTRACT["states"]
    for group, owner_key, heading in (
        ("live", "live_owner", "the-five-states"),
        (
            "resolution",
            "resolution_owner",
            "resolution-authority-and-cache-are-independent",
        ),
    ):
        owner = BOOK / spec[owner_key]
        text = owner.read_text(encoding="utf-8")
        cells = first_cells(section(text, heading))
        for state in spec[group]:
            if state not in cells:
                problems.append(
                    f"{owner.name}: {group} state {state!r} is not declared "
                    "in its state table"
                )


def check_profiles(problems: list[str]) -> None:
    spec = CONTRACT["profiles"]
    owner = BOOK / spec["owner"]
    text = strip_code_and_comments(owner.read_text(encoding="utf-8"))
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


def run_checker(root: Path) -> tuple[int, str]:
    script = root / "tools" / "check-links.py"
    result = subprocess.run(
        [sys.executable, "-I", str(script)],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stdout + result.stderr


def fresh_copy(tmp: str) -> Path:
    copy = Path(tmp) / "repo"
    shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(".git", "build"))
    return copy


def replace(path: Path, old: str, new: str, count: int = -1) -> bool:
    text = path.read_text(encoding="utf-8")
    changed = text.replace(old, new, count)
    if changed == text:
        return False
    path.write_text(changed, encoding="utf-8")
    return True


def append(path: Path, addition: str) -> bool:
    text = path.read_text(encoding="utf-8")
    path.write_text(text + addition, encoding="utf-8")
    return True


def self_test() -> int:
    """Require a clean baseline and the expected diagnostic per mutation."""
    failures: list[str] = []
    counts = {"detecting": 0, "passing": 0}

    with tempfile.TemporaryDirectory() as tmp:
        baseline_root = fresh_copy(tmp)
        code, output = run_checker(baseline_root)
        if code != 0:
            failures.append(f"baseline is not clean: {output.strip()[:300]}")

    def mutate(
        label: str,
        edit,
        expected: str | None,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = fresh_copy(tmp)
            if not edit(root):
                failures.append(f"self-test: {label} mutation did not apply")
                return
            code, output = run_checker(root)
            if "Traceback" in output:
                failures.append(f"self-test: {label} crashed: {output.strip()[:300]}")
                return
            if expected is None:
                if code != 0:
                    failures.append(
                        f"self-test: {label} should pass, got {output.strip()[:300]}"
                    )
                else:
                    counts["passing"] += 1
                return
            if code == 0:
                failures.append(f"self-test: {label} was not detected")
            elif expected not in output:
                failures.append(
                    f"self-test: {label} expected {expected!r}, "
                    f"got {output.strip()[:300]}"
                )
            else:
                counts["detecting"] += 1

    mutate(
        "orphan chapter",
        lambda root: (
            root / "book" / "99-orphan.md"
        ).write_text(
            "---\ntitle: Orphan\npart: Breadth\n---\n\n# Orphan\n",
            encoding="utf-8",
        )
        or True,
        "chapter 99-orphan.md is absent from the manifest",
    )
    mutate(
        "broken cross-file anchor",
        lambda root: append(
            root / "book" / "01-purpose.md",
            "\n[broken](02-cabochon-character.md#no-such-heading)\n",
        ),
        "missing anchor #no-such-heading",
    )
    mutate(
        "broken same-file anchor",
        lambda root: append(
            root / "book" / "01-purpose.md",
            "\n[broken](#no-such-local-anchor)\n",
        ),
        "missing anchor #no-such-local-anchor in book/01-purpose.md",
    )
    mutate(
        "anchor in a comment",
        lambda root: append(
            root / "book" / "01-purpose.md",
            "\n<!-- [ignored](01-purpose.md#no-such-heading) -->\n",
        ),
        None,
    )
    mutate(
        "heading inside a comment",
        lambda root: append(
            root / "book" / "01-purpose.md",
            "\n<!--\n## Comment-only heading\n-->\n\n"
            "[broken](#comment-only-heading)\n",
        ),
        "missing anchor #comment-only-heading in book/01-purpose.md",
    )
    mutate(
        "heading inside fenced code",
        lambda root: append(
            root / "book" / "01-purpose.md",
            "\n```\n## Fenced heading\n```\n\n"
            "[broken](#fenced-heading)\n",
        ),
        "missing anchor #fenced-heading in book/01-purpose.md",
    )
    mutate(
        "duplicate heading suffix",
        lambda root: append(
            root / "book" / "01-purpose.md",
            "\n## Scope\n\n[duplicate](#scope-1)\n",
        ),
        None,
    )
    mutate(
        "mismatched figure",
        lambda root: replace(
            root / "book" / "02-cabochon-character.md",
            "fig-02-small-world.svg",
            "fig-01-map.svg",
            1,
        ),
        "declared figure fig-01-map.svg is not embedded as an image in the body",
    )
    mutate(
        "hyperlink instead of an image",
        lambda root: replace(
            root / "book" / "02-cabochon-character.md",
            "![",
            "[",
            1,
        ),
        "declared figure fig-02-small-world.svg is not embedded as an image "
        "in the body",
    )
    mutate(
        "figure mentioned only in a comment",
        lambda root: (
            replace(
                root / "book" / "02-cabochon-character.md",
                "![",
                "<!-- ![",
                1,
            )
            and append(
                root / "book" / "02-cabochon-character.md",
                "\n-->\n",
            )
        ),
        "is not embedded as an image in the body",
    )
    mutate(
        "missing requirement owner",
        lambda root: replace(
            root / "book" / "40-checklist.md",
            "Owner: [Ecosystem map](03-ecosystem-map.md#the-substrate-components).",
            "",
            1,
        ),
        "requirement CON-01 names no owner",
    )
    mutate(
        "missing state",
        lambda root: replace(
            root / "book" / "08-live-relationships.md",
            "| Refreshing |",
            "| Updating   |",
            1,
        ),
        "state 'Refreshing' is not declared",
    )
    mutate(
        "state mentioned only in a comment",
        lambda root: (
            replace(
                root / "book" / "08-live-relationships.md",
                "| Refreshing |",
                "| Updating   |",
                1,
            )
            and append(
                root / "book" / "08-live-relationships.md",
                "\n<!-- Refreshing -->\n",
            )
        ),
        "state 'Refreshing' is not declared",
    )
    mutate(
        "missing profile",
        lambda root: replace(
            root / "book" / "appendix-references.md",
            "substrate",
            "foundation",
        ),
        "profile 'substrate' is not declared",
    )
    mutate(
        "missing command relation",
        lambda root: replace(
            root / "book" / "23-command-palette.md",
            "](10-menus.md)",
            "](11-toolbars-status.md)",
            1,
        ),
        "does not reference the command record owner",
    )
    mutate(
        "missing resource relation",
        lambda root: replace(
            root / "book" / "16-icons.md",
            "](38-localization.md)",
            "](13-typography.md)",
            1,
        ),
        "does not reference the resource owner",
    )

    with tempfile.TemporaryDirectory() as tmp:
        root = fresh_copy(tmp)
        append(root / "book" / "01-purpose.md", "\n[broken](#no-such-heading)\n")
        no_op = replace(
            root / "book" / "01-purpose.md",
            "text that is not present",
            "replacement",
        )
        if no_op:
            failures.append("self-test: no-op mutation was reported as applied")
        code, output = run_checker(root)
        if code == 0 or "missing anchor #no-such-heading" not in output:
            failures.append("self-test: unrelated failing baseline was not reported")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print(
        "links: self-test passed a clean baseline, "
        f"{counts['detecting']} detecting mutations and "
        f"{counts['passing']} passing mutations"
    )
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