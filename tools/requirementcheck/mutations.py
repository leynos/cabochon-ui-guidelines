"""Describe the self-test mutations and their required diagnostics."""

from __future__ import annotations

import json
import shutil
import typing as typ

from requirementcheck.checks import run
from requirementcheck.contract import ROOT

if typ.TYPE_CHECKING:
    import collections.abc as cabc
    from pathlib import Path


def _fresh_repository(temporary: Path) -> Path:
    """Copy the book and registry tools into a disposable repository."""
    root = temporary / "repo"
    root.mkdir()
    shutil.copytree(ROOT / "book", root / "book")
    (root / "tools").mkdir()
    for name in ("book-contract.json", "requirements.json"):
        shutil.copy(ROOT / "tools" / name, root / "tools" / name)
    return root


def _registry_cases() -> list[tuple[str, cabc.Callable[..., None], str]]:
    """Return every registry mutation with the diagnostic it must provoke."""
    return [
        (
            "duplicate record",
            lambda data: data["requirements"].append(dict(data["requirements"][0])),
            "duplicate registry identifier CON-01",
        ),
        (
            "missing owner file",
            lambda data: data["requirements"][0]["owner"].update({
                "file": "41-missing.md"
            }),
            "missing owner file '41-missing.md'",
        ),
        (
            "missing owner anchor",
            lambda data: data["requirements"][0]["owner"].update({
                "anchor": "no-such-heading"
            }),
            "missing owner anchor 03-ecosystem-map.md#no-such-heading",
        ),
        (
            "missing evidence",
            lambda data: data["requirements"][0].update({"evidence": []}),
            "CON-01: no evidence route",
        ),
        (
            "missing predicate",
            lambda data: data["requirements"][0].update({"applies_when": ""}),
            "CON-01: no applicability predicate",
        ),
        (
            "empty registry",
            lambda data: data.clear(),
            "requirement registry is empty",
        ),
        (
            "mismatched checklist owner",
            lambda data: data["requirements"][0]["owner"].update({
                "file": "01-purpose.md",
                "anchor": "scope",
            }),
            (
                "CON-01: checklist owner disagrees with registry owner "
                "'01-purpose.md#scope'"
            ),
        ),
    ]


def _remove_doc_04(text: str) -> str:
    """Delete the DOC-04 checklist item from the checklist text."""
    start = text.index("- [ ] **DOC-04**")
    candidates = [
        index
        for marker in ("- [ ] ", "\n## ")
        if (index := text.find(marker, start + 10)) != -1
    ]
    end = min(candidates) if candidates else len(text)
    return text[:start] + text[end:]


def _renumber_owner(text: str) -> str:
    """Point the CON-01 checklist owner at the file heading, not its section."""
    return text.replace(
        "03-ecosystem-map.md#the-substrate-components",
        "03-ecosystem-map.md#ecosystem-map",
        1,
    )


def _checklist_cases() -> list[tuple[str, cabc.Callable[[str], str], str]]:
    """Return every checklist mutation with the diagnostic it must provoke."""
    return [
        (
            "same-file wrong anchor",
            _renumber_owner,
            (
                "CON-01: checklist owner disagrees with registry owner "
                "'03-ecosystem-map.md#the-substrate-components'"
            ),
        ),
        (
            "removed checklist entry",
            _remove_doc_04,
            "registry record DOC-04 has no checklist item",
        ),
    ]


def _run_registry_case(
    root: Path, name: str, edit: cabc.Callable[..., None], expected: str
) -> tuple[str | None, bool]:
    """Apply one registry mutation and report its failure and detection."""
    target = root / "tools" / "requirements.json"
    original = target.read_text(encoding="utf-8")
    data = json.loads(original)
    edit(data)
    target.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    problems = run(root)
    target.write_text(original, encoding="utf-8")
    if expected in "\n".join(problems):
        return None, True
    return f"{name}: expected {expected!r}, got {problems[:3]}", False


def _run_checklist_case(
    root: Path, name: str, edit: cabc.Callable[[str], str], expected: str
) -> tuple[str | None, bool]:
    """Apply one checklist mutation and report its failure and detection."""
    target = root / "book" / "40-checklist.md"
    original = target.read_text(encoding="utf-8")
    changed = edit(original)
    if changed == original:
        return f"{name}: mutation did not apply", False
    target.write_text(changed, encoding="utf-8")
    problems = run(root)
    target.write_text(original, encoding="utf-8")
    if expected in "\n".join(problems):
        return None, True
    return f"{name}: expected {expected!r}, got {problems[:3]}", False


def _tally(failures: list[str], outcome: tuple[str | None, bool]) -> int:
    """Record one mutation outcome and return its detection count."""
    failure, detected = outcome
    if failure is not None:
        failures.append(failure)
    return int(detected)


def _owner_copy_case(root: Path) -> tuple[str | None, bool]:
    """Rename a heading in the copied book and require the copy's own anchors."""
    owner_copy = root / "book" / "03-ecosystem-map.md"
    original = owner_copy.read_text(encoding="utf-8")
    changed = original.replace(
        "## The substrate components",
        "## The renamed substrate components",
        1,
    )
    if changed == original:
        return "copied owner mutation did not apply", False
    owner_copy.write_text(changed, encoding="utf-8")
    problems = run(root)
    owner_copy.write_text(original, encoding="utf-8")
    expected = (
        "CON-01: missing owner anchor 03-ecosystem-map.md#the-substrate-components"
    )
    if any(expected in problem for problem in problems):
        return None, True
    return (
        (
            "copied owner anchor mutation was resolved against the real "
            f"repository: {problems[:3]}"
        ),
        False,
    )


def _apply_wording(text: str) -> str:
    """Reword one checklist item without changing its meaning."""
    return text.replace(
        "The application loads menus, labels, icons and shortcuts",
        "The application loads its menus, labels, icons and shortcuts",
    )


def _benign_edit_failures(root: Path) -> list[str]:
    """Return failures for benign checklist edits that must still pass."""
    target = root / "book" / "40-checklist.md"
    original = target.read_text(encoding="utf-8")
    failures: list[str] = []
    target.write_text(_apply_wording(original), encoding="utf-8")
    if run(root):
        failures.append("wording-only edit was rejected")
    target.write_text(
        original + "\n<!--\n- [ ] **ZZZ-99** — Comment-only item.\n-->\n",
        encoding="utf-8",
    )
    if run(root):
        failures.append("checklist item inside a comment was rejected")
    target.write_text(original, encoding="utf-8")
    return failures
