"""Tests for the layout checker's self-test baseline gate.

The self-test only proves anything when the unmodified baseline passes, and
its probes read the committed chapter by row position. A failing baseline must
therefore be reported and stop the run before any probe executes.
"""

from __future__ import annotations

import pytest
from layoutcheck import contract as layoutcheck_contract
from layoutcheck import selftest as layoutcheck_selftest


def test_self_test_stops_before_the_probes_when_the_baseline_fails(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A failing baseline is reported without running a mutation probe."""
    budgets = layoutcheck_contract.load_budgets(layoutcheck_contract.DATA_PATH)
    called: list[str] = []

    def probe(_budgets: object) -> str | None:
        """Record that a probe ran and report no failure."""
        called.append("probe")
        return None

    monkeypatch.setattr(layoutcheck_selftest, "PROBES", (probe,))
    status = layoutcheck_selftest.self_test(["worked table row 'standard' fails"], budgets)
    assert status == 1, "a failing baseline fails the self-test"
    assert called == [], "no probe runs while the baseline fails"
    captured = capsys.readouterr()
    assert "baseline budgets did not pass" in captured.err, (
        "the baseline failure is named on standard error"
    )
    assert "worked table row 'standard' fails" in captured.err, (
        "the baseline diagnostic is reported"
    )


def test_self_test_runs_the_probes_when_the_baseline_passes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A passing baseline runs every probe and reports the count."""
    budgets = layoutcheck_contract.load_budgets(layoutcheck_contract.DATA_PATH)
    called: list[str] = []

    def probe(_budgets: object) -> str | None:
        """Record that a probe ran and report no failure."""
        called.append("probe")
        return None

    monkeypatch.setattr(layoutcheck_selftest, "PROBES", (probe,))
    assert layoutcheck_selftest.self_test([], budgets) == 0, (
        "a passing baseline and silent probe succeed"
    )
    assert called == ["probe"], "the probe runs once"