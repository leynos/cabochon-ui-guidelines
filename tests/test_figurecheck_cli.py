"""Tests for the figure-check command line.

The `figurecheck.cli.main` function must dispatch between the contract checks
and the mutation self-test, print help on demand and reject an unknown or
abbreviated option rather than silently running a check.
"""

from __future__ import annotations

import sys

import pytest
from figurecheck import cli


def _run(monkeypatch: pytest.MonkeyPatch, *arguments: str) -> int:
    """Invoke the command line with the given arguments."""
    monkeypatch.setattr(sys, "argv", ["check-figures", *arguments])
    return cli.main()


def test_plain_run_checks_every_figure(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A bare invocation runs the contract checks and reports success."""
    assert _run(monkeypatch) == 0, "a bare run reports success"
    assert "figures satisfy" in capsys.readouterr().out, (
        "the success line reports that the figures satisfy the contract"
    )


def test_self_test_runs_the_mutations(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The self-test option selects the mutation self-test."""
    assert _run(monkeypatch, "--self-test") == 0, "the self-test reports success"
    assert "detected all" in capsys.readouterr().out, (
        "the self-test line reports that every mutation was detected"
    )


def test_help_prints_usage_and_exits(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The help option prints usage and exits successfully."""
    with pytest.raises(SystemExit) as exit_info:
        _run(monkeypatch, "--help")
    assert exit_info.value.code == 0, "help exits successfully"
    assert "--self-test" in capsys.readouterr().out, (
        "the usage lists the self-test option"
    )


def test_unknown_option_is_rejected(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """An abbreviated or unknown option exits with the usage error status."""
    with pytest.raises(SystemExit) as exit_info:
        _run(monkeypatch, "--self-tes")
    assert exit_info.value.code == 2, "an unknown option exits with the usage status"
    assert "unrecognized arguments" in capsys.readouterr().err, (
        "the error names the rejected argument"
    )
