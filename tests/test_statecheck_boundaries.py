"""Tests for the inputs the state check receives at its command line.

The chapter and figure paths reach the readers as parameters, and a chapter or
figure that cannot be read or parsed must be reported as a handled diagnostic
with exit status 1 rather than raised to the interpreter.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from statecheck import cli as statecheck_cli
from statecheck import contract as statecheck_contract
from statecheck.transitions import chapter_rows


@pytest.fixture(autouse=True)
def _plain_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    """Run the command as a plain invocation rather than a self-test."""
    monkeypatch.setattr(sys, "argv", ["check-states"])


def _run(capsys: pytest.CaptureFixture[str]) -> tuple[int, str]:
    """Run the command and return its status with its standard error."""
    status = statecheck_cli.main()
    return status, capsys.readouterr().err


def test_a_missing_chapter_is_reported(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A chapter that does not exist is reported, not raised."""
    monkeypatch.setattr(statecheck_contract, "CHAPTER", tmp_path / "08-absent.md")

    status, err = _run(capsys)

    assert status == 1, "an unreadable chapter exits non-zero"
    assert err.startswith("state contract: "), (
        "the command reports the chapter on standard error"
    )
    assert "08-absent.md" in err, "the diagnostic names the missing chapter"
    assert "Traceback" not in err, "the defect is not raised to the interpreter"


def test_an_undecodable_chapter_is_reported(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A chapter that is not UTF-8 is reported, not raised."""
    chapter = tmp_path / "08-live-relationships.md"
    chapter.write_bytes(b"\xff\xfe## Transitions\n")
    monkeypatch.setattr(statecheck_contract, "CHAPTER", chapter)

    status, err = _run(capsys)

    assert status == 1, "an undecodable chapter exits non-zero"
    assert err.startswith("state contract: "), (
        "the command reports the chapter on standard error"
    )
    assert "Traceback" not in err, "the defect is not raised to the interpreter"


def test_a_missing_figure_is_reported(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A figure that has not been generated is reported as a diagnostic."""
    monkeypatch.setattr(statecheck_contract, "FIGURE", tmp_path / "fig-absent.svg")

    status, err = _run(capsys)

    assert status == 1, "a missing figure exits non-zero"
    assert "fig-absent.svg does not exist; run make figures" in err, (
        "the diagnostic names the figure and the target that generates it"
    )
    assert "Traceback" not in err, "the absent figure is not raised"


def test_a_malformed_figure_is_reported(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A figure that is not well-formed XML is reported, not raised."""
    figure = tmp_path / "fig-06-state.svg"
    figure.write_text("<svg><g></svg>", encoding="utf-8")
    monkeypatch.setattr(statecheck_contract, "FIGURE", figure)

    status, err = _run(capsys)

    assert status == 1, "a malformed figure exits non-zero"
    assert err.startswith("state contract: "), (
        "the command reports the parse failure on standard error"
    )
    assert "Traceback" not in err, "the parse failure is not raised"


def test_a_non_string_event_is_reported(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A fixture step whose event is not a string is a diagnostic, not a raise."""
    document = json.loads(
        statecheck_contract.FIXTURES_PATH.read_text(encoding="utf-8")
    )
    document["scenarios"][0]["events"][0]["event"] = ["refresh_requested"]
    fixtures = tmp_path / "state-fixtures.json"
    fixtures.write_text(json.dumps(document), encoding="utf-8")
    monkeypatch.setattr(statecheck_contract, "FIXTURES_PATH", fixtures)

    status, err = _run(capsys)

    assert status == 1, "a malformed fixture event exits non-zero"
    assert "unknown event ['refresh_requested']" in err, (
        "the diagnostic names the event it cannot read"
    )
    assert "Traceback" not in err, "the malformed fixture is not raised"


def test_chapter_rows_ignore_a_fenced_example(tmp_path: Path) -> None:
    """A fenced sample that spells the heading cannot stand in for the section."""
    chapter = tmp_path / "08-live-relationships.md"
    chapter.write_text(
        "# Live relationships\n\n"
        "```markdown\n"
        "## Transitions\n\n"
        "| From | Event | To | Owner |\n"
        "| --- | --- | --- | --- |\n"
        "| Sample | sample | Sample | chapter-08 |\n"
        "```\n\n"
        "## Transitions\n\n"
        "| From | Event | To | Owner |\n"
        "| --- | --- | --- | --- |\n"
        "| Broken | refresh_requested | Refreshing | chapter-08 |\n",
        encoding="utf-8",
    )

    assert chapter_rows(chapter) == [
        ("Broken", "refresh_requested", "Refreshing", "chapter-08")
    ], "the real section's row is read rather than the fenced sample"
