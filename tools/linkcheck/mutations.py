"""Describe the self-test mutations and their required diagnostics.

The `_mutation_cases` function returns each deliberate defect and the message
it must provoke, with `replace` and `append` as the edit helpers.
`linkcheck.selftest` imports these cases.
"""

from __future__ import annotations

import typing as typ

if typ.TYPE_CHECKING:
    import collections.abc as cabc
    from pathlib import Path


def replace(path: Path, old: str, new: str, count: int = -1) -> bool:
    """Replace text in a file and report whether the file changed."""
    text = path.read_text(encoding="utf-8")
    changed = text.replace(old, new, count)
    if changed == text:
        return False
    path.write_text(changed, encoding="utf-8")
    return True


def append(path: Path, addition: str) -> bool:
    """Append text to a file, reporting the mutation as applied."""
    text = path.read_text(encoding="utf-8")
    path.write_text(text + addition, encoding="utf-8")
    return True


def _write(root: Path, relative: str, text: str) -> bool:
    """Write text to a repository-relative path and report it as applied."""
    (root / relative).write_text(text, encoding="utf-8")
    return True


def _comment_out_figure(root: Path) -> bool:
    """Move the chapter's first embedded image into an HTML comment."""
    chapter = root / "book" / "02-cabochon-character.md"
    return replace(chapter, "![", "<!-- ![", 1) and append(chapter, "\n-->\n")


def _state_in_comment(root: Path) -> bool:
    """Rename a live-state table row and leave the old name in a comment."""
    chapter = root / "book" / "08-live-relationships.md"
    return replace(chapter, "| Refreshing |", "| Updating   |", 1) and append(
        chapter, "\n<!-- Refreshing -->\n"
    )


def _part_only_in_fence(root: Path) -> bool:
    """Move a chapter's part field from front matter into a fenced example."""
    chapter = root / "book" / "01-purpose.md"
    return replace(chapter, "part: Orientation\n", "", 1) and append(
        chapter, "\n```yaml\npart: Orientation\n```\n"
    )


def _image_reference_command_link(root: Path) -> bool:
    """Replace the command owner link with an image reference to the same file."""
    chapter = root / "book" / "23-command-palette.md"
    return replace(
        chapter,
        "[Menus](10-menus.md)",
        "![Menus][menus]\n\n[menus]: 10-menus.md\n",
        1,
    )


def _fenced_state_heading(root: Path) -> bool:
    """Insert a fenced level-two heading between a state heading and its table."""
    chapter = root / "book" / "08-live-relationships.md"
    return replace(
        chapter,
        "## The five states\n\n",
        "## The five states\n\n```markdown\n## Example\n```\n\n",
        1,
    )


def _mutation_cases() -> list[tuple[str, cabc.Callable[[Path], bool], str | None]]:
    """Return every self-test mutation with the diagnostic it must provoke."""
    purpose = "book/01-purpose.md"
    return [
        (
            "orphan chapter",
            lambda root: _write(
                root,
                "book/99-orphan.md",
                "---\ntitle: Orphan\npart: Breadth\n---\n\n# Orphan\n",
            ),
            "chapter 99-orphan.md is absent from the manifest",
        ),
        (
            "broken cross-file anchor",
            lambda root: append(
                root / purpose,
                "\n[broken](02-cabochon-character.md#no-such-heading)\n",
            ),
            "missing anchor #no-such-heading",
        ),
        (
            "broken same-file anchor",
            lambda root: append(root / purpose, "\n[broken](#no-such-local-anchor)\n"),
            "missing anchor #no-such-local-anchor in book/01-purpose.md",
        ),
        (
            "anchor in a comment",
            lambda root: append(
                root / purpose,
                "\n<!-- [ignored](01-purpose.md#no-such-heading) -->\n",
            ),
            None,
        ),
        (
            "heading inside a comment",
            lambda root: append(
                root / purpose,
                "\n<!--\n## Comment-only heading\n-->\n\n"
                "[broken](#comment-only-heading)\n",
            ),
            "missing anchor #comment-only-heading in book/01-purpose.md",
        ),
        (
            "heading inside fenced code",
            lambda root: append(
                root / purpose,
                "\n```\n## Fenced heading\n```\n\n[broken](#fenced-heading)\n",
            ),
            "missing anchor #fenced-heading in book/01-purpose.md",
        ),
        (
            "duplicate heading suffix",
            lambda root: append(
                root / purpose, "\n## Scope\n\n[duplicate](#scope-1)\n"
            ),
            None,
        ),
        (
            "mismatched figure",
            lambda root: replace(
                root / "book" / "02-cabochon-character.md",
                "fig-02-small-world.svg",
                "fig-01-map.svg",
                1,
            ),
            "declared figure fig-01-map.svg is not embedded as an image in the body",
        ),
        (
            "hyperlink instead of an image",
            lambda root: replace(
                root / "book" / "02-cabochon-character.md", "![", "[", 1
            ),
            (
                "declared figure fig-02-small-world.svg is not embedded as an "
                "image in the body"
            ),
        ),
        (
            "figure mentioned only in a comment",
            _comment_out_figure,
            "is not embedded as an image in the body",
        ),
        (
            "missing requirement owner",
            lambda root: replace(
                root / "book" / "40-checklist.md",
                "Owner: [Ecosystem map](03-ecosystem-map.md#the-substrate-components).",
                "",
                1,
            ),
            "requirement CON-01 names no owner",
        ),
        (
            "missing state",
            lambda root: replace(
                root / "book" / "08-live-relationships.md",
                "| Refreshing |",
                "| Updating   |",
                1,
            ),
            "state 'Refreshing' is not declared",
        ),
        (
            "state mentioned only in a comment",
            _state_in_comment,
            "state 'Refreshing' is not declared",
        ),
        (
            "missing profile",
            lambda root: replace(
                root / "book" / "appendix-references.md", "substrate", "foundation"
            ),
            "profile 'substrate' is not declared",
        ),
        (
            "missing command relation",
            lambda root: replace(
                root / "book" / "23-command-palette.md",
                "](10-menus.md)",
                "](11-toolbars-status.md)",
                1,
            ),
            "does not reference the command record owner",
        ),
        (
            "missing resource relation",
            lambda root: replace(
                root / "book" / "16-icons.md",
                "](38-localization.md)",
                "](13-typography.md)",
                1,
            ),
            "does not reference the resource owner",
        ),
        (
            "reference-style broken link",
            lambda root: append(
                root / purpose,
                "\n[ref]: 02-cabochon-character.md#no-such-heading\n\n[broken][ref]\n",
            ),
            "missing anchor #no-such-heading",
        ),
        (
            "link inside a multi-line code span",
            lambda root: append(
                root / purpose,
                "\n`example\n[ignored](01-purpose.md#no-such-heading)\nend`\n",
            ),
            None,
        ),
        (
            "comment delimiter inside a fence",
            lambda root: append(
                root / purpose,
                "\n```\n<!-- example\n```\n## Visible heading\n-->\n\n"
                "[broken](#after-fence)\n",
            ),
            "missing anchor #after-fence",
        ),
        (
            "owner link with a fragment",
            lambda root: replace(
                root / "book" / "23-command-palette.md",
                "](10-menus.md)",
                "](10-menus.md#command-records)",
                1,
            ),
            None,
        ),
        (
            "checklist item only in a comment",
            lambda root: append(
                root / "book" / "40-checklist.md",
                "\n<!--\n- [ ] **ZZZ-99** — Comment-only item.\n-->\n",
            ),
            None,
        ),
        (
            "escaped bracket is literal text",
            lambda root: append(
                root / "book" / "01-purpose.md",
                "\nEscaped \\[example](missing.md) is literal text.\n",
            ),
            None,
        ),
        (
            "parenthesised destination is not truncated",
            lambda root: append(
                root / "book" / "01-purpose.md",
                "\n[paren](no-such-file(v2).md)\n",
            ),
            "missing link target no-such-file(v2).md",
        ),
        (
            "angle-bracket destinations",
            lambda root: append(
                root / purpose,
                "\n[angle](<01-purpose.md>) and [ref]\n\n[ref]: <01-purpose.md>\n",
            ),
            None,
        ),
        (
            "comment delimiter inside a code span",
            lambda root: append(
                root / purpose,
                "\n[ok](#the-rate-field)\n\nA literal `<!--` in a span.\n\n"
                "## The `rate` field\n",
            ),
            None,
        ),
        (
            "duplicate reference definition",
            lambda root: append(
                root / purpose,
                "\n[dup]: 01-purpose.md\n[dup]: no-such-file.md\n\n[broken][dup]\n",
            ),
            None,
        ),
        (
            "image reference is not an ordinary link",
            _image_reference_command_link,
            "does not reference the command record owner",
        ),
        (
            "figure field inside a fenced example",
            lambda root: append(
                root / purpose, "\n```yaml\nfigure: fig-absent.svg\n```\n"
            ),
            None,
        ),
        (
            "part field only in a fenced example",
            _part_only_in_fence,
            "missing part in front matter",
        ),
        (
            "navigation destination with a leading ./",
            lambda root: replace(
                root / "book" / "README.md",
                "](01-purpose.md)",
                "](./01-purpose.md)",
                1,
            ),
            None,
        ),
        (
            "checked checklist item is validated",
            lambda root: append(
                root / "book" / "40-checklist.md",
                "\n- [x] **CON-01** — A checked duplicate. Owner: "
                "[Ecosystem map](03-ecosystem-map.md#the-substrate-components).\n",
            ),
            "duplicate requirement identifier CON-01",
        ),
        (
            "state heading inside a fenced example",
            _fenced_state_heading,
            None,
        ),
        (
            "owner link with a leading ./",
            lambda root: replace(
                root / "book" / "23-command-palette.md",
                "](10-menus.md)",
                "](./10-menus.md)",
                1,
            ),
            None,
        ),
        (
            "owner link inside a code span",
            lambda root: append(
                root / "book" / "40-checklist.md",
                "\n- [ ] **CON-99** — A demonstration. "
                "`Owner: [Ecosystem map]"
                "(03-ecosystem-map.md#the-substrate-components)`\n",
            ),
            "requirement CON-99 names no owner",
        ),
        (
            "owner outside a checklist item",
            lambda root: append(
                root / "book" / "40-checklist.md",
                "\nA closing paragraph outside the list. "
                "Owner: [Gone](../figures/fig-01-map.svg#no-such-anchor).\n",
            ),
            None,
        ),
        (
            "indented owner inside an item is read",
            lambda root: replace(
                root / "book" / "40-checklist.md",
                "from Escutcheon resources. Owner: "
                "[Ecosystem map](03-ecosystem-map.md#the-substrate-components).",
                "from Escutcheon resources. Owner: "
                "[Ecosystem map](03-ecosystem-map.md#the-substrate-components).\n"
                "      Owner: [Gone](../figures/fig-01-map.svg#no-such-anchor).",
                1,
            ),
            "missing owner anchor ../figures/fig-01-map.svg#no-such-anchor",
        ),
    ]
