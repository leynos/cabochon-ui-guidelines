"""Tests for loading the figure, state and layout contract documents.

The loaders must report a document that cannot be read, decoded or parsed as a
typed contract error rather than a `SystemExit` or a traceback, must reject a
declared value the checks could not use, and importing a contract module must
not read any contract document.
"""

from __future__ import annotations

import json
import subprocess
import sys
import typing as typ
from collections.abc import Callable
from pathlib import Path

import pytest
from figurecheck import contract as figurecheck_contract
from layoutcheck import contract as layoutcheck_contract
from linkcheck import contract as linkcheck_contract
from requirementcheck import contract as requirementcheck_contract
from statecheck import contract as statecheck_contract

CONTRACT_MODULES = (
    statecheck_contract,
    figurecheck_contract,
    linkcheck_contract,
    layoutcheck_contract,
    requirementcheck_contract,
)
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
import layoutcheck.budget
import layoutcheck.chapter
import layoutcheck.cli
import layoutcheck.contract
import layoutcheck.selftest
import linkcheck.checks
import linkcheck.cli
import linkcheck.contract
import linkcheck.links
import linkcheck.requirements
import linkcheck.selftest
import requirementcheck.checks
import requirementcheck.cli
import requirementcheck.contract
import requirementcheck.selftest
import statecheck.cli
import statecheck.contract
import statecheck.selftest
print("clean")
"""


@pytest.fixture(
    params=CONTRACT_MODULES,
    ids=["statecheck", "figurecheck", "linkcheck", "layoutcheck", "requirementcheck"],
)
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


def _layout_configuration() -> dict[str, object]:
    """Return one well-formed worked configuration."""
    return {
        "name": "standard",
        "width": "default_width",
        "height": "default_height",
        "profile": "document",
        "left": "navigator",
        "right": "inspector",
        "expected": [818, 640],
    }


def _layout_document() -> dict[str, object]:
    """Return a minimal layout budget document the loader accepts."""
    return {
        "tokens": {
            "title": 31,
            "menu": 29,
            "status": 26,
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
        "profiles": {"document": ["title", "menu", "status"]},
        "configurations": [_layout_configuration()],
    }


def _write_layout(tmp_path: Path, document: object) -> Path:
    """Write a layout budget document to a temporary path."""
    path = tmp_path / "layout-budgets.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def test_layout_budgets_accept_a_valid_document(tmp_path: Path) -> None:
    """A document whose references all resolve loads unchanged."""
    document = _layout_document()
    budgets = layoutcheck_contract.load_budgets(_write_layout(tmp_path, document))
    assert budgets.configurations == document["configurations"], (
        "the valid configuration survives validation"
    )
    assert budgets.profiles == document["profiles"], "the valid profiles survive"
    assert budgets.tokens == document["tokens"], "the valid tokens survive"


def _configuration(document: dict[str, object]) -> dict[str, object]:
    """Return the document's first configuration for mutation."""
    configurations = document["configurations"]
    assert isinstance(configurations, list), "the fixture declares a list"
    first = configurations[0]
    assert isinstance(first, dict), "the fixture declares one configuration"
    return first


def _replace(**changes: object) -> Callable[[dict[str, object]], None]:
    """Return a mutation that replaces named configuration fields."""

    def mutate(document: dict[str, object]) -> None:
        """Apply the changes to the document's configuration."""
        _configuration(document).update(changes)

    return mutate


def _remove(field: str) -> Callable[[dict[str, object]], None]:
    """Return a mutation that removes one configuration field."""

    def mutate(document: dict[str, object]) -> None:
        """Delete the field from the document's configuration."""
        del _configuration(document)[field]

    return mutate


def _set_profile_bands(bands: list[str]) -> Callable[[dict[str, object]], None]:
    """Return a mutation that replaces the declared profile's bands."""

    def mutate(document: dict[str, object]) -> None:
        """Set the document profile's bands."""
        document["profiles"] = {"document": bands}

    return mutate


def _drop_token(name: str) -> Callable[[dict[str, object]], None]:
    """Return a mutation that removes one declared token."""

    def mutate(document: dict[str, object]) -> None:
        """Delete the named token from the document."""
        tokens = document["tokens"]
        assert isinstance(tokens, dict), "the fixture declares a token table"
        del tokens[name]

    return mutate


def _set_token(name: str, value: object) -> Callable[[dict[str, object]], None]:
    """Return a mutation that replaces one declared token's value."""

    def mutate(document: dict[str, object]) -> None:
        """Set the named token's value in the document."""
        tokens = document["tokens"]
        assert isinstance(tokens, dict), "the fixture declares a token table"
        tokens[name] = value

    return mutate


def _configurations(value: object) -> Callable[[dict[str, object]], None]:
    """Return a mutation that replaces the configurations array."""

    def mutate(document: dict[str, object]) -> None:
        """Replace the document's configurations array."""
        document["configurations"] = value

    return mutate


@pytest.mark.parametrize(
    ("mutate", "reason"),
    [
        pytest.param(_remove("height"), "configurations[0] lacks ['height']", id="missing-field"),
        pytest.param(
            _replace(width="absent"),
            "configurations[0].width names no declared token: 'absent'",
            id="unknown-width-token",
        ),
        pytest.param(
            _replace(left=7.5),
            "configurations[0].left names no declared pane token: 7.5",
            id="fractional-pane",
        ),
        pytest.param(
            _replace(right=240),
            "configurations[0].right names no declared pane token: 240",
            id="numeric-pane",
        ),
        pytest.param(
            _replace(profile="absent"),
            "configurations[0].profile names no declared profile: 'absent'",
            id="unknown-profile",
        ),
        pytest.param(
            _replace(expected=[818]),
            "configurations[0].expected is not a pair of plane sizes",
            id="short-expected",
        ),
        pytest.param(
            _replace(expected="818 x 640"),
            "configurations[0].expected is not a pair of plane sizes",
            id="text-expected",
        ),
        pytest.param(
            _replace(expected=["absent", 640]),
            "configurations[0].expected names no declared token: 'absent'",
            id="unknown-expected-token",
        ),
        pytest.param(
            _replace(compact="yes"),
            "configurations[0].compact is not a boolean",
            id="text-compact",
        ),
        pytest.param(
            _replace(name=""),
            "configurations[0].name is not a non-empty string",
            id="blank-name",
        ),
        pytest.param(_configurations(["one"]), "configurations[0] is not a JSON object", id="not-an-object"),
        pytest.param(
            _set_profile_bands(["title", "ghost"]),
            "profile 'document' names undeclared tokens ['ghost']",
            id="unknown-profile-band",
        ),
        pytest.param(_drop_token("splitter"), "layout budgets declare no ['splitter']", id="missing-token"),
        pytest.param(
            _set_token("document_width_min", True),
            "layout budgets declare a non-integer token",
            id="boolean-token",
        ),
    ],
)
def test_layout_budgets_reject_an_unusable_document(
    tmp_path: Path, mutate: Callable[[dict[str, object]], None], reason: str
) -> None:
    """A value the checks could not use is reported as a contract error."""
    document = _layout_document()
    mutate(document)
    with pytest.raises(layoutcheck_contract.ContractError) as info:
        layoutcheck_contract.load_budgets(_write_layout(tmp_path, document))
    assert reason in str(info.value), "the error names the unusable declaration"


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
