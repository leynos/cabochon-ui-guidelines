"""Prove that each mutation provokes the diagnostic it claims."""

from __future__ import annotations

import shutil

# The self-test re-runs the checker itself under an isolated interpreter. The
# argument vector is built from local paths, so no shell or untrusted input
# reaches the process.
import subprocess  # ruff: ignore[suspicious-subprocess-import]
import sys
import tempfile
import typing as typ
from pathlib import Path

from linkcheck.contract import ROOT
from linkcheck.mutations import _mutation_cases, append, replace

if typ.TYPE_CHECKING:
    import collections.abc as cabc


def run_checker(root: Path) -> tuple[int, str]:
    """Run the checker in ``root`` as an isolated subprocess and capture output."""
    script = root / "tools" / "check-links.py"
    # The argument vector is built here from the running interpreter and a
    # path inside a freshly copied worktree; no shell or untrusted input is
    # involved, so the generic subprocess warning does not apply.
    result = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
        [sys.executable, "-I", str(script)],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stdout + result.stderr


def fresh_copy(tmp: str) -> Path:
    """Copy the repository into a temporary directory for mutation testing."""
    copy = Path(tmp) / "repo"
    shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(".git", "build"))
    return copy


def _baseline_failures() -> list[str]:
    """Return a failure when the unmutated copy does not pass cleanly."""
    with tempfile.TemporaryDirectory() as tmp:
        code, output = run_checker(fresh_copy(tmp))
    if code == 0:
        return []
    return [f"baseline is not clean: {output.strip()[:300]}"]


def _judge_mutation(
    label: str, code: int, output: str, expected: str | None
) -> str | None:
    """Return the failure description for one mutation outcome, if any."""
    if expected is None:
        if code != 0:
            return f"self-test: {label} should pass, got {output.strip()[:300]}"
        return None
    if code == 0:
        return f"self-test: {label} was not detected"
    if expected not in output:
        return f"self-test: {label} expected {expected!r}, got {output.strip()[:300]}"
    return None


def _run_mutation(
    label: str, edit: cabc.Callable[[Path], bool], expected: str | None
) -> tuple[str | None, str | None]:
    """Apply one mutation in a fresh copy and classify its outcome."""
    with tempfile.TemporaryDirectory() as tmp:
        root = fresh_copy(tmp)
        if not edit(root):
            return f"self-test: {label} mutation did not apply", None
        code, output = run_checker(root)
    if "Traceback" in output:
        return f"self-test: {label} crashed: {output.strip()[:300]}", None
    failure = _judge_mutation(label, code, output, expected)
    if failure is not None:
        return failure, None
    return None, "passing" if expected is None else "detecting"


def _unrelated_failure_check() -> list[str]:
    """Check that an unrelated failing baseline is still reported."""
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = fresh_copy(tmp)
        append(root / "book" / "01-purpose.md", "\n[broken](#no-such-heading)\n")
        no_op = replace(
            root / "book" / "01-purpose.md",
            "text that is not present",
            "replacement",
        )
        code, output = run_checker(root)
    if no_op:
        failures.append("self-test: no-op mutation was reported as applied")
    if code == 0 or "missing anchor #no-such-heading" not in output:
        failures.append("self-test: unrelated failing baseline was not reported")
    return failures


def self_test() -> int:
    """Require a clean baseline and the expected diagnostic per mutation."""
    failures = _baseline_failures() + _unrelated_failure_check()
    counts = {"detecting": 0, "passing": 0}
    for label, edit, expected in _mutation_cases():
        failure, kind = _run_mutation(label, edit, expected)
        if failure is not None:
            failures.append(failure)
        if kind is not None:
            counts[kind] += 1
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
