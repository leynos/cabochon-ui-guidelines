"""Tests for the inputs each check receives at its command-line boundary.

The checks must read the book directory, the chapter text and the contract
document they are given rather than any path fixed at import, and a contract
the loader rejects must reach the command line as a report and a non-zero exit
status rather than a traceback.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest
from layoutcheck import contract as layoutcheck_contract
from layoutcheck.chapter import check_chapter
from layoutcheck import cli as layoutcheck_cli
from linkcheck import cli as linkcheck_cli
from linkcheck.checks import run_checks
from linkcheck.contract import ContractError, load_contract
from requirementcheck import cli as requirementcheck_cli
from requirementcheck.contract import (
    ContractError as RequirementContractError,
    load_requirements,
)


def _link_document() -> dict[str, object]:
    """Return a minimal link contract naming one chapter."""
    return {
        "navigation": "README.md",
        "chapters": [{"file": "01-one.md", "part": "Orientation"}],
        "requirements": {
            "checklist": "01-one.md",
            "registry": "requirements.json",
            "id_pattern": "^(CON)-[0-9]{2}$",
        },
        "states": {
            "live": [],
            "live_owner": "01-one.md",
            "resolution": [],
            "resolution_owner": "01-one.md",
        },
        "profiles": {"names": [], "owner": "01-one.md"},
        "commands": {"record_owner": "01-one.md", "views": []},
        "resources": {"owner": "01-one.md", "consumers": []},
    }


def _write_link(tmp_path: Path, document: object) -> Path:
    """Write a link contract to a temporary path."""
    path = tmp_path / "book-contract.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def _write_book(root: Path, chapter_body: str) -> Path:
    """Write a one-chapter book whose navigation links the chapter."""
    book = root / "book"
    book.mkdir()
    (book / "README.md").write_text(
        "# Book\n\n- [One](01-one.md)\n", encoding="utf-8"
    )
    (book / "01-one.md").write_text(
        f"---\npart: Orientation\n---\n\n# One\n\n{chapter_body}\n",
        encoding="utf-8",
    )
    return book


def test_link_checks_read_the_supplied_book(tmp_path: Path) -> None:
    """A minimal book validates when the checks are given its directory."""
    contract = load_contract(_write_link(tmp_path, _link_document()))
    book = _write_book(tmp_path, "See [the book](README.md).")
    assert run_checks(contract, book) == [], (
        "the checks read the supplied book rather than the repository's"
    )


def test_link_checks_report_a_missing_checklist_without_raising(
    tmp_path: Path,
) -> None:
    """A missing checklist chapter is reported rather than read."""
    contract = load_contract(_write_link(tmp_path, _link_document()))
    book = _write_book(tmp_path, "See [the book](README.md).")
    (book / "01-one.md").unlink()
    problems = run_checks(contract, book)
    assert "manifest names missing chapter 01-one.md" in problems, (
        "the manifest reports the missing chapter"
    )


def test_link_checks_accept_a_relative_book_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A relative book directory still yields relative diagnostics."""
    contract = load_contract(_write_link(tmp_path, _link_document()))
    book = _write_book(tmp_path, "See [the book](README.md).")
    (book / "README.md").write_text(
        "# Book\n\n- [One](01-one.md#nowhere)\n", encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)
    problems = run_checks(contract, Path("book"))
    assert "book/README.md: missing anchor #nowhere in book/01-one.md" in problems, (
        "the diagnostic is relative to the supplied book"
    )


def test_link_checks_report_destinations_relative_to_the_supplied_book(
    tmp_path: Path,
) -> None:
    """A defect is named from the book directory the checks were given."""
    contract = load_contract(_write_link(tmp_path, _link_document()))
    book = _write_book(
        tmp_path,
        "See [missing](missing.md) and [anchor](README.md#absent).",
    )
    assert run_checks(contract, book) == [
        "book/01-one.md: missing link target missing.md",
        "book/01-one.md: missing anchor #absent in book/README.md",
    ], "the problems name the chapter path relative to the supplied book"


def _naming(
    section: str, key: str, value: object
) -> Callable[[dict[str, object]], None]:
    """Return a mutation that replaces one field of a named contract section."""

    def mutate(document: dict[str, object]) -> None:
        part = document[section]
        assert isinstance(part, dict), "the fixture declares the section"
        part[key] = value

    return mutate


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(
            _naming("requirements", "checklist", "99-absent.md"), id="checklist"
        ),
        pytest.param(
            _naming("states", "live_owner", "99-absent.md"), id="live-owner"
        ),
        pytest.param(
            _naming("states", "resolution_owner", "99-absent.md"),
            id="resolution-owner",
        ),
        pytest.param(_naming("profiles", "owner", "99-absent.md"), id="profile-owner"),
        pytest.param(
            _naming("commands", "record_owner", "99-absent.md"), id="command-owner"
        ),
        pytest.param(
            _naming("commands", "views", ["99-absent.md"]), id="command-view"
        ),
        pytest.param(
            _naming("resources", "owner", "99-absent.md"), id="resource-owner"
        ),
        pytest.param(
            _naming("resources", "consumers", ["99-absent.md"]),
            id="resource-consumer",
        ),
    ],
)
def test_link_contract_rejects_a_reference_outside_the_manifest(
    tmp_path: Path, mutate: Callable[[dict[str, object]], None]
) -> None:
    """A named book file the manifest does not declare is reported."""
    document = _link_document()
    mutate(document)
    with pytest.raises(ContractError) as info:
        load_contract(_write_link(tmp_path, document))
    assert "which the manifest does not declare" in str(info.value), (
        "the error names the reference the manifest does not declare"
    )


def test_link_contract_rejects_a_pattern_that_does_not_compile(
    tmp_path: Path,
) -> None:
    """An identifier pattern that is not a regular expression is reported."""
    document = _link_document()
    requirements = document["requirements"]
    assert isinstance(requirements, dict), "the fixture declares the section"
    requirements["id_pattern"] = "^(CON"
    with pytest.raises(ContractError) as info:
        load_contract(_write_link(tmp_path, document))
    assert "does not compile" in str(info.value), (
        "the error names the unusable identifier pattern"
    )


def test_link_cli_reports_a_rejected_contract(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The link command reports a rejected contract without a traceback."""
    document = _link_document()
    requirements = document["requirements"]
    assert isinstance(requirements, dict), "the fixture declares the section"
    requirements["id_pattern"] = "^(CON"
    monkeypatch.setattr(linkcheck_cli, "DATA_PATH", _write_link(tmp_path, document))
    assert linkcheck_cli.main() == 1, "a rejected contract exits non-zero"
    captured = capsys.readouterr()
    assert captured.err.startswith("link contract: "), (
        "the command reports the defect on standard error"
    )
    assert "Traceback" not in captured.err, "the defect is not raised to the interpreter"


def test_layout_chapter_check_reads_the_supplied_text() -> None:
    """Chapter 14's tables are checked from the text the caller supplies."""
    budgets = layoutcheck_contract.load_budgets(layoutcheck_contract.DATA_PATH)
    text = layoutcheck_contract.chapter_text()
    assert check_chapter(budgets, text) == [], "the committed chapter validates"
    broken = text.replace("818 × 640", "818 × 639", 1)
    assert broken != text, "the fixture changes a worked plane"
    assert any("document plane" in error for error in check_chapter(budgets, broken)), (
        "the supplied text's worked value is checked"
    )


def test_layout_chapter_check_does_not_fall_back_to_the_committed_chapter() -> None:
    """Text without the expected tables is reported, not silently replaced."""
    budgets = layoutcheck_contract.load_budgets(layoutcheck_contract.DATA_PATH)
    with pytest.raises(layoutcheck_contract.ContractError) as info:
        check_chapter(budgets, "No tables here.\n")
    assert "Bands" in str(info.value), (
        "the error names the table the supplied text lacks"
    )


def _layout_document() -> dict[str, object]:
    """Return a layout document whose panes name declared tokens."""
    return {
        "tokens": {
            "splitter": 6,
            "navigator": 210,
            "inspector": 240,
            "default_width": 1280,
            "default_height": 800,
            "document_width_min": 420,
            "document_content_height": 320,
            "document_viewport_min": 320,
            "compact_viewport_min": 240,
        },
        "profiles": {"document": ["navigator"]},
        "configurations": [
            {
                "name": "standard",
                "width": "default_width",
                "height": "default_height",
                "profile": "document",
                "left": "navigator",
                "right": "inspector",
                "expected": [818, 640],
            }
        ],
    }


@pytest.mark.parametrize("side", ["left", "right"])
def test_layout_cli_reports_a_numeric_pane(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    side: str,
) -> None:
    """A side pane given as a number is reported at the command line."""
    document = _layout_document()
    configurations = document["configurations"]
    assert isinstance(configurations, list), "the fixture declares a list"
    configuration = configurations[0]
    assert isinstance(configuration, dict), "the fixture declares one configuration"
    configuration[side] = 240
    path = tmp_path / "layout-budgets.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    monkeypatch.setattr(layoutcheck_cli, "DATA_PATH", path)
    assert layoutcheck_cli.main() == 1, "a numeric pane exits non-zero"
    captured = capsys.readouterr()
    assert captured.err.startswith("layout contract: "), (
        "the command reports the numeric pane on standard error"
    )
    assert f"configurations[0].{side} names no declared pane token: 240" in (
        captured.err
    ), "the diagnostic names the pane field"
    assert "Traceback" not in captured.err, "the defect is not raised to the interpreter"


def test_layout_cli_reports_a_rejected_contract(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The layout command reports a rejected contract without a traceback."""
    document = {
        "tokens": {"splitter": 6},
        "profiles": {},
        "configurations": [{"name": "one"}],
    }
    monkeypatch.setattr(
        layoutcheck_cli, "DATA_PATH", tmp_path / "layout-budgets.json"
    )
    (tmp_path / "layout-budgets.json").write_text(
        json.dumps(document), encoding="utf-8"
    )
    assert layoutcheck_cli.main() == 1, "a rejected contract exits non-zero"
    captured = capsys.readouterr()
    assert captured.err.startswith("layout contract: "), (
        "the command reports the defect on standard error"
    )
    assert "Traceback" not in captured.err, "the defect is not raised to the interpreter"


def test_layout_cli_reports_an_undecodable_chapter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A chapter that is not UTF-8 is reported, not raised to the interpreter."""
    chapter = tmp_path / "14-spacing-metrics.md"
    chapter.write_bytes(b"\xff\xfe# Chapter\n")
    monkeypatch.setattr(layoutcheck_contract, "CHAPTER", chapter)
    assert layoutcheck_cli.main() == 1, "an undecodable chapter exits non-zero"
    captured = capsys.readouterr()
    assert captured.err.startswith("layout chapter: "), (
        "the command reports the unreadable chapter on standard error"
    )
    assert "Traceback" not in captured.err, "the defect is not raised to the interpreter"


def test_requirement_contract_names_the_checklist_and_registry(
    tmp_path: Path,
) -> None:
    """The requirement loader reads the two file names the checks need."""
    contract = load_requirements(_write_link(tmp_path, _link_document()))
    assert contract.checklist == "01-one.md", "the checklist name is kept"
    assert contract.registry == "requirements.json", "the registry name is kept"


@pytest.mark.parametrize(
    "document",
    [
        pytest.param({"navigation": "README.md"}, id="no-requirements-section"),
        pytest.param({"requirements": {"checklist": "one.md"}}, id="no-registry"),
        pytest.param({"requirements": ["one.md"]}, id="section-not-an-object"),
    ],
)
def test_requirement_contract_rejects_a_malformed_document(
    tmp_path: Path, document: object
) -> None:
    """A document without the two declared names is reported."""
    with pytest.raises(RequirementContractError):
        load_requirements(_write_link(tmp_path, document))


def test_requirement_cli_reports_a_rejected_contract(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The requirement command reports a rejected contract without a traceback."""
    monkeypatch.setattr(
        requirementcheck_cli, "DATA_PATH", _write_link(tmp_path, {"nav": "README.md"})
    )
    assert requirementcheck_cli.main() == 1, "a rejected contract exits non-zero"
    captured = capsys.readouterr()
    assert captured.err.startswith("requirement contract: "), (
        "the command reports the defect on standard error"
    )
    assert "Traceback" not in captured.err, "the defect is not raised to the interpreter"
