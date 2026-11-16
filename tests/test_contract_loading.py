"""Tests for loading the figure and state contract documents.

The loaders must report a document that cannot be read, decoded or parsed as a
typed contract error rather than a `SystemExit` or a traceback, and importing a
contract module must not read any contract document.
"""

from __future__ import annotations

import subprocess
import sys
import typing as typ
from pathlib import Path

import pytest
from figurecheck import contract as figurecheck_contract
from statecheck import contract as statecheck_contract

CONTRACT_MODULES = (statecheck_contract, figurecheck_contract)
TOOLS = Path(__file__).resolve().parent.parent / "tools"

_AUDIT_SCRIPT = """
import sys


def _is_import_path(path):
    return path.endswith(".py") or path.endswith(".pyc") or "__pycache__" in path


def _audit(event, arguments):
    if event != "open":
        return
    target = arguments[0]
    if isinstance(target, str) and not _is_import_path(target):
        raise RuntimeError(f"unexpected file read: {target}")


sys.addaudithook(_audit)
sys.path.insert(0, sys.argv[1])
import figurecheck.cli
import figurecheck.contract
import figurecheck.selftest
import figuregen.cli
import figuregen.figdata
import statecheck.cli
import statecheck.contract
import statecheck.selftest
print("clean")
"""


@pytest.fixture(params=CONTRACT_MODULES, ids=["statecheck", "figurecheck"])
def contract_module(request: pytest.FixtureRequest) -> typ.Any:
    """Return one package's contract module under test."""
    return request.param


def test_missing_document_raises_contract_error(
    contract_module: typ.Any, tmp_path: Path
) -> None:
    """A missing document raises the module's typed contract error."""
    path = tmp_path / "missing.json"
    with pytest.raises(contract_module.ContractError) as info:
        contract_module.load_document(path)
    assert str(path) in str(info.value), "the error names the missing document"


@pytest.mark.parametrize(
    ("name", "content"),
    [
        ("invalid-utf8", b"\xff\xfe\x00"),
        ("invalid-json", b'{"live_states": '),
    ],
)
def test_bad_document_raises_contract_error(
    contract_module: typ.Any, tmp_path: Path, name: str, content: bytes
) -> None:
    """A document that cannot be decoded or parsed raises a contract error."""
    path = tmp_path / f"{name}.json"
    path.write_bytes(content)
    with pytest.raises(contract_module.ContractError) as info:
        contract_module.load_document(path)
    assert str(path) in str(info.value), "the error names the unreadable document"


def _state(**overrides: object) -> dict[str, object]:
    """Return one well-formed state record for a hand-built contract."""
    state: dict[str, object] = {
        "id": "denied",
        "word": "Denied",
        "cue": "padlock and word",
        "mark": "lock",
        "role": "oxide",
        "colour": "#8A302F",
    }
    state.update(overrides)
    return state


def _document(*states: dict[str, object]) -> dict[str, object]:
    """Return a minimal contract that declares the given live states."""
    return {
        "live_states": {str(state["word"]): state for state in states},
        "resolution_states": {},
        "palette_roles": {"oxide": "#8A302F"},
    }


def test_state_records_read_the_real_contract() -> None:
    """The real figure document validates into one record per identity."""
    data = figurecheck_contract.load_document(figurecheck_contract.DATA_PATH)
    records, messages = figurecheck_contract.state_records(data)
    assert messages == [], "the committed contract validates without a defect"
    assert records["current"] == {
        "id": "current",
        "word": "CURRENT",
        "mark": "dot",
        "role": "pine2",
        "colour": "#285E50",
    }, "the current state keeps its declared identity, mark and colour"
    assert set(records) == {
        "current",
        "refreshing",
        "stale",
        "broken",
        "denied",
        "resolved",
        "opaque",
        "unavailable",
        "malformed",
    }, "every declared live and resolution state earns one record"


@pytest.mark.parametrize(
    ("declared", "expected"),
    [
        (
            (_state(), _state(word="Denied again")),
            "duplicate state identity 'denied'",
        ),
        (
            (_state(mark="sparkle"),),
            "state 'DENIED' has unknown mark 'sparkle'",
        ),
        (
            (_state(role="ghost"),),
            "state 'DENIED' names unknown role 'ghost'",
        ),
        (
            (_state(colour="#000000"),),
            "state 'DENIED' colour #000000 disagrees with role 'oxide'",
        ),
    ],
    ids=["duplicate-identity", "unknown-mark", "unknown-role", "colour"],
)
def test_state_records_report_each_defect(
    declared: tuple[dict[str, object], ...], expected: str
) -> None:
    """Every malformed state record is reported with the existing wording."""
    records, messages = figurecheck_contract.state_records(_document(*declared))
    assert messages == [expected], "the defect is reported with its declared wording"
    assert len(records) == 1, "the well-formed state still earns its record"


def test_state_records_omit_a_state_with_a_missing_field() -> None:
    """A state that omits a required field does not enter the mapping."""
    records, messages = figurecheck_contract.state_records(_document(_state(cue="")))
    assert records == {}, "a state with a blank field yields no record"
    assert messages == ["state 'Denied' lacks ['cue']"], (
        "the blank field is named in the diagnostic"
    )


@pytest.mark.parametrize(
    "declared",
    [
        _state(cue=None),
        {key: value for key, value in _state().items() if key != "cue"},
        _state(cue=7),
    ],
    ids=["null", "absent", "not-text"],
)
def test_state_records_omit_a_state_whose_field_is_not_text(
    declared: dict[str, object],
) -> None:
    """A null, absent or non-text field leaves the state out of the mapping."""
    records, messages = figurecheck_contract.state_records(_document(declared))
    assert records == {}, "a state without a declared text field yields no record"
    assert messages == ["state 'Denied' lacks ['cue']"], (
        "the unusable field is named in the diagnostic"
    )


@pytest.mark.parametrize(
    ("record", "expected"),
    [
        pytest.param("one", "scenario 0 is not a JSON object", id="not-an-object"),
        pytest.param({"events": []}, "scenario 0 declares no name", id="no-name"),
        pytest.param(
            {"name": "one", "events": "none"},
            "scenario 0 declares no events array",
            id="events-not-an-array",
        ),
        pytest.param(
            {"name": "one", "events": [1]},
            "scenario 0 declares no events array",
            id="event-not-an-object",
        ),
        pytest.param(
            {"name": "one", "events": [], "facts": []},
            "scenario 0 declares malformed facts",
            id="facts-not-an-object",
        ),
    ],
)
def test_scenarios_reject_a_malformed_record(
    record: object, expected: str
) -> None:
    """A fixture sequence that does not declare its shape is reported by position."""
    with pytest.raises(statecheck_contract.ContractError) as info:
        statecheck_contract.scenarios({"scenarios": [record]})
    assert str(info.value) == expected, "the defect is reported with its position"


def test_scenarios_name_the_offending_position() -> None:
    """The reported position is the malformed record's index, not the first one."""
    fixtures = {"scenarios": [{"name": "one", "events": []}, {"name": 2}]}
    with pytest.raises(statecheck_contract.ContractError) as info:
        statecheck_contract.scenarios(fixtures)
    assert str(info.value) == "scenario 1 declares no name", (
        "the position counts every preceding record"
    )


def test_scenarios_read_the_real_fixtures() -> None:
    """Every committed scenario validates and is returned unchanged."""
    fixtures = statecheck_contract.load_document(statecheck_contract.FIXTURES_PATH)
    declared = statecheck_contract.scenarios(fixtures)
    assert declared == fixtures["scenarios"], "the committed fixtures validate"
    assert declared, "the fixtures declare at least one scenario"


def test_importing_contract_modules_reads_no_document() -> None:
    """Importing the contract modules performs no file read but source loads."""
    result = subprocess.run(
        [sys.executable, "-I", "-c", _AUDIT_SCRIPT, str(TOOLS)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "clean", (
        "importing the contract modules opened no data file"
    )
