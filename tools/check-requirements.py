#!/usr/bin/env python3
"""Check the structured requirement registry against the checklist.

The registry is the structured record of every checklist requirement. Each
record names an owning file and heading anchor, its force, its conformance
profile, the predicate under which it applies and at least one evidence route.
The checklist is a projection of that registry, so this checker proves set
equality, ownership and coverage rather than parsing the book's prose.

Run from the repository root with ``python3 -I tools/check-requirements.py``.
Pass ``--self-test`` to apply mutations to a temporary copy and confirm that
each check detects the defect it claims to prevent, that the baseline passes
and that a wording-only edit still passes.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOK = ROOT / "book"

REQUIREMENT_RE = re.compile(r"\*\*([A-Z]{3}-[0-9]{2})\*\*")
OWNER_RE = re.compile(r"Owner:\s*\[[^\]]*\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)
EXPLICIT_ANCHOR_RE = re.compile(r"<a\s+id=[\"']([^\"']+)[\"']")

PROFILE_ORDER = {"substrate": 0, "semantic": 1, "studio": 2}


def slug(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    return re.sub(r"\s+", "-", text)


def anchors(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    found = {slug(heading) for heading in HEADING_RE.findall(text)}
    found.update(EXPLICIT_ANCHOR_RE.findall(text))
    return found


def parse_checklist(path: Path, problems: list[str]) -> dict[str, list[str]]:
    items: dict[str, list[str]] = {}
    text = path.read_text(encoding="utf-8")
    for block in text.split("- [ ] ")[1:]:
        match = REQUIREMENT_RE.match(block)
        if not match:
            problems.append("checklist item has no requirement identifier")
            continue
        identifier = match.group(1)
        if identifier in items:
            problems.append(f"duplicate checklist identifier {identifier}")
        items[identifier] = OWNER_RE.findall(block)
    return items


def load_registry(path: Path, problems: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        problems.append(f"requirement registry is unreadable: {error}")
        return {}


def check_records(
    registry: dict, checklist: dict[str, list[str]], problems: list[str]
) -> None:
    profiles = registry.get("profiles", [])
    forces = registry.get("forces", [])
    routes = registry.get("evidence_routes", [])
    if not all(isinstance(value, list) for value in (profiles, forces, routes)):
        problems.append("registry schema lists are missing")
        return

    seen: set[str] = set()
    records = registry.get("requirements", [])
    if not isinstance(records, list):
        problems.append("registry requirements is not a list")
        return

    for record in records:
        identifier = record.get("id", "<missing>")
        if identifier in seen:
            problems.append(f"duplicate registry identifier {identifier}")
        seen.add(identifier)

        if not REQUIREMENT_RE.fullmatch(f"**{identifier}**"):
            problems.append(f"registry identifier {identifier} is malformed")

        owner = record.get("owner", {})
        file_name = owner.get("file", "")
        anchor = owner.get("anchor", "")
        path = BOOK / file_name
        if not path.is_file():
            problems.append(f"{identifier}: missing owner file {file_name!r}")
        elif anchor not in anchors(path):
            problems.append(
                f"{identifier}: missing owner anchor {file_name}#{anchor}"
            )

        if record.get("force") not in forces:
            problems.append(f"{identifier}: invalid force {record.get('force')!r}")
        if record.get("profile") not in profiles:
            problems.append(
                f"{identifier}: invalid profile {record.get('profile')!r}"
            )
        predicate = record.get("applies_when")
        if not isinstance(predicate, str) or not predicate.strip():
            problems.append(f"{identifier}: no applicability predicate")

        evidence = record.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            problems.append(f"{identifier}: no evidence route")
        else:
            for step in evidence:
                if step.get("route") not in routes:
                    problems.append(
                        f"{identifier}: invalid evidence route "
                        f"{step.get('route')!r}"
                    )
                if not str(step.get("detail", "")).strip():
                    problems.append(f"{identifier}: evidence route has no detail")

        if identifier not in checklist:
            problems.append(f"registry record {identifier} has no checklist item")
        else:
            owner_files = {
                owner.partition("#")[0] for owner in checklist[identifier]
            }
            if file_name not in owner_files:
                problems.append(
                    f"{identifier}: checklist owner disagrees with registry "
                    f"owner {file_name!r}"
                )

    for identifier in checklist:
        if identifier not in seen:
            problems.append(f"checklist item {identifier} has no registry record")

    for profile in ("semantic", "studio"):
        rank = PROFILE_ORDER[profile]
        applicable = [
            record
            for record in records
            if record.get("force") == "must"
            and PROFILE_ORDER.get(record.get("profile"), -1) <= rank
        ]
        if not applicable:
            problems.append(
                f"profile {profile} inherits no applicable must requirement"
            )


def run(root: Path) -> list[str]:
    contract = json.loads((root / "tools" / "book-contract.json").read_text())
    spec = contract["requirements"]
    problems: list[str] = []
    checklist = parse_checklist(root / "book" / spec["checklist"], problems)
    registry = load_registry(root / "tools" / spec["registry"], problems)
    if registry:
        check_records(registry, checklist, problems)
    return problems


def self_test() -> None:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "repo"
        root.mkdir()
        shutil.copytree(ROOT / "book", root / "book")
        (root / "tools").mkdir()
        for name in ("book-contract.json", "requirements.json"):
            shutil.copy(ROOT / "tools" / name, root / "tools" / name)

        baseline = run(root)
        if baseline:
            failures.append(f"baseline is not clean: {baseline[:3]}")

        def mutate(name: str, edit, expected: str) -> None:
            target = root / "tools" / "requirements.json"
            original = target.read_text()
            data = json.loads(original)
            edit(data)
            target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
            problems = run(root)
            if expected not in "\n".join(problems):
                failures.append(f"{name}: expected {expected!r}, got {problems[:3]}")
            target.write_text(original)

        def edit_checklist(name: str, edit, expected: str) -> None:
            target = root / "book" / "40-checklist.md"
            original = target.read_text()
            changed = edit(original)
            if changed == original:
                failures.append(f"{name}: mutation did not apply")
                return
            target.write_text(changed)
            problems = run(root)
            if expected not in "\n".join(problems):
                failures.append(f"{name}: expected {expected!r}, got {problems[:3]}")
            target.write_text(original)

        mutate(
            "duplicate record",
            lambda data: data["requirements"].append(
                dict(data["requirements"][0])
            ),
            "duplicate registry identifier CON-01",
        )
        mutate(
            "missing owner file",
            lambda data: data["requirements"][0]["owner"].update(
                {"file": "41-missing.md"}
            ),
            "missing owner file '41-missing.md'",
        )
        mutate(
            "missing owner anchor",
            lambda data: data["requirements"][0]["owner"].update(
                {"anchor": "no-such-heading"}
            ),
            "missing owner anchor 03-ecosystem-map.md#no-such-heading",
        )
        mutate(
            "missing evidence",
            lambda data: data["requirements"][0].update({"evidence": []}),
            "CON-01: no evidence route",
        )
        mutate(
            "missing predicate",
            lambda data: data["requirements"][0].update({"applies_when": ""}),
            "CON-01: no applicability predicate",
        )
        mutate(
            "mismatched checklist owner",
            lambda data: data["requirements"][0]["owner"].update(
                {"file": "01-purpose.md", "anchor": "scope"}
            ),
            "CON-01: checklist owner disagrees with registry owner '01-purpose.md'",
        )

        def remove_item(text: str) -> str:
            start = text.index("- [ ] **DOC-04**")
            candidates = [
                index
                for marker in ("- [ ] ", "\n## ")
                if (index := text.find(marker, start + 10)) != -1
            ]
            end = min(candidates) if candidates else len(text)
            return text[:start] + text[end:]

        edit_checklist(
            "removed checklist entry",
            remove_item,
            "registry record DOC-04 has no checklist item",
        )

        def wording_only(text: str) -> str:
            return text.replace(
                "The application loads menus, labels, icons and shortcuts",
                "The application loads its menus, labels, icons and shortcuts",
            )

        target = root / "book" / "40-checklist.md"
        original = target.read_text()
        target.write_text(wording_only(original))
        if run(root):
            failures.append("wording-only edit was rejected")
        target.write_text(original)

    if failures:
        print("\n".join(f"self-test: {failure}" for failure in failures))
        raise SystemExit(1)
    print("self-test: 8 mutations detected, baseline and wording-only edit pass")


def main() -> None:
    if "--self-test" in sys.argv:
        self_test()
        return
    problems = run(ROOT)
    if problems:
        print("\n".join(problems))
        raise SystemExit(1)
    print("requirements: registry and checklist agree")


if __name__ == "__main__":
    main()
