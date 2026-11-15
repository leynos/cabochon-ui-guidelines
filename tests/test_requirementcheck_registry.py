"""Tests for the requirement registry loader's failure contract.

`load_registry` records every unreadable or unparsable registry as one
diagnostic and returns an empty mapping, so a caller sees a missing registry
rather than an exception. That contract must hold for a file that cannot be
read, a file that is not valid UTF-8 and a file that is not valid JSON.
"""

from __future__ import annotations

import typing as typ

import pytest
from requirementcheck.registry import load_registry

if typ.TYPE_CHECKING:
    from pathlib import Path

UNREADABLE = "requirement registry is unreadable: "


def test_missing_file_is_recorded(tmp_path: Path) -> None:
    """A registry that does not exist is reported, not raised."""
    problems: list[str] = []

    assert load_registry(tmp_path / "absent.json", problems) == {}, (
        "a missing registry yields no mapping"
    )
    assert len(problems) == 1, "a missing registry earns exactly one diagnostic"
    assert problems[0].startswith(UNREADABLE), "the diagnostic names the registry"


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param(b"", id="empty"),
        pytest.param(b"{not json}", id="invalid-json"),
        pytest.param(b'{"id": "\xff\xfe"}', id="invalid-utf8"),
        pytest.param(b"\xf0\x28\x8c\x28", id="malformed-utf8"),
    ],
)
def test_unreadable_payloads_are_recorded(tmp_path: Path, payload: bytes) -> None:
    """Each unreadable payload earns one diagnostic and an empty mapping.

    Empty input and invalid JSON fail while parsing; the two malformed byte
    sequences fail while decoding UTF-8. Both paths record a single
    ``UNREADABLE`` diagnostic rather than raising.
    """
    path = tmp_path / "registry.json"
    path.write_bytes(payload)
    problems: list[str] = []

    assert load_registry(path, problems) == {}, (
        "an unreadable registry yields no mapping"
    )
    assert len(problems) == 1, "an unreadable registry earns exactly one diagnostic"
    assert problems[0].startswith(UNREADABLE), "the diagnostic names the registry"


def test_valid_registry_returns_its_document(tmp_path: Path) -> None:
    """A readable registry returns its document and records nothing."""
    path = tmp_path / "registry.json"
    path.write_text('{"requirements": []}', encoding="utf-8")
    problems: list[str] = []

    assert load_registry(path, problems) == {"requirements": []}, (
        "a readable registry yields its document"
    )
    assert problems == [], "a readable registry records no diagnostic"
