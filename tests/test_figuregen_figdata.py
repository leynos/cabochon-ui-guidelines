"""Tests for the figure catalogue loader and its contract errors.

`figuregen.figdata` must parse and validate ``tools/figure-data.json`` only
when a caller asks it to, and it must report an unreadable or malformed
contract as `ContractError` rather than leaking the underlying exception.
"""

from __future__ import annotations

import subprocess  # ruff: ignore[suspicious-subprocess-import]
import sys
from pathlib import Path

import pytest
from figuregen.figdata import (
    DATA_PATH,
    Catalogue,
    ContractError,
    load_catalogue,
    load_document,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS = REPO_ROOT / "tools"

SECTIONS = ("live_states", "live_transitions", "resolution_states", "figures")

_IMPORT_PROBE = """\
import sys

def _audit(event: str, arguments: tuple[object, ...]) -> None:
    if event != "open" or not arguments:
        return
    target = arguments[0]
    if not isinstance(target, str):
        return
    if target.endswith(".py") or "__pycache__" in target:
        return
    raise RuntimeError(f"import opened {target}")

sys.path.insert(0, sys.argv[1])
sys.addaudithook(_audit)
import figuregen.figdata
import figuregen.ornaments.chips
"""


def _valid_document() -> dict[str, object]:
    """Return a structurally valid contract document.

    Returns
    -------
    dict[str, object]
        A document whose four catalogue sections are present and empty.
    """
    return {
        "live_states": {},
        "live_transitions": [],
        "resolution_states": {},
        "figures": {},
    }


@pytest.mark.parametrize(
    ("content", "reason"),
    [
        pytest.param(None, "cannot read", id="missing-file"),
        pytest.param(b"\xff\xfe\xfd", "cannot decode", id="invalid-utf-8"),
        pytest.param(b'{"live_states": ', "cannot parse", id="invalid-json"),
    ],
)
def test_load_document_reports_an_unusable_contract(
    tmp_path: Path, content: bytes | None, reason: str
) -> None:
    """An unreadable, undecodable or unparsable file raises ContractError."""
    path = tmp_path / "figure-data.json"
    if content is not None:
        path.write_bytes(content)
    with pytest.raises(ContractError) as error:
        load_document(path)
    message = str(error.value)
    assert str(path) in message, "the error message must name the contract path"
    assert reason in message, "the error message must name the underlying failure"


@pytest.mark.parametrize("section", SECTIONS)
def test_from_document_requires_each_section(section: str) -> None:
    """A document without one of the four catalogue sections is rejected."""
    document = _valid_document()
    del document[section]
    with pytest.raises(ContractError) as error:
        Catalogue.from_document(document)
    assert section in str(error.value), (
        "the error message must name the missing section"
    )


@pytest.mark.parametrize(
    ("section", "wrong_type"),
    [
        pytest.param("live_states", [], id="live-states-array"),
        pytest.param("live_transitions", {}, id="live-transitions-object"),
        pytest.param("resolution_states", "states", id="resolution-states-string"),
        pytest.param("figures", [], id="figures-array"),
    ],
)
def test_from_document_rejects_a_wrong_section_type(
    section: str, wrong_type: object
) -> None:
    """A section whose declared type is wrong is rejected."""
    document = _valid_document()
    document[section] = wrong_type
    with pytest.raises(ContractError) as error:
        Catalogue.from_document(document)
    assert section in str(error.value), "the error message must name the bad section"


def test_from_document_rejects_a_non_string_state_value() -> None:
    """A state record holding a non-string field is rejected."""
    document = _valid_document()
    document["live_states"] = {"Current": {"id": 1}}
    with pytest.raises(ContractError) as error:
        Catalogue.from_document(document)
    assert "live_states.Current" in str(error.value), (
        "the error message must name the offending state record"
    )


def test_from_document_accepts_the_real_contract() -> None:
    """The committed contract yields its four catalogue sections unchanged."""
    document = load_document(DATA_PATH)
    catalogue = Catalogue.from_document(document)
    assert catalogue.live_states == document["live_states"], (
        "live_states must match the contract document"
    )
    assert catalogue.live_transitions == document["live_transitions"], (
        "live_transitions must match the contract document"
    )
    assert catalogue.resolution_states == document["resolution_states"], (
        "resolution_states must match the contract document"
    )
    assert catalogue.figure_specs == document["figures"], (
        "figure_specs must match the figures section"
    )
    assert catalogue.states.live is catalogue.live_states, (
        "the state tables must expose the live state records"
    )
    assert catalogue.states.resolution is catalogue.resolution_states, (
        "the state tables must expose the resolution state records"
    )
    assert load_catalogue(DATA_PATH) == catalogue, (
        "load_catalogue must return the same catalogue as from_document"
    )


def test_importing_the_modules_reads_no_contract() -> None:
    """Importing figdata and the chips performs no non-source file reads."""
    result = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
        [sys.executable, "-I", "-c", _IMPORT_PROBE, str(TOOLS)],
        capture_output=True,
        text=True,
        check=False,
        timeout=20,
    )
    assert result.returncode == 0, (
        f"importing figuregen read a file outside the import machinery: {result.stderr}"
    )
