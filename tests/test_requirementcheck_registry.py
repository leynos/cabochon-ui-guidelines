"""Tests for the requirement registry loader's failure contract.

`load_registry` records every unreadable or unparsable registry as one
diagnostic and returns an empty mapping, so a caller sees a missing registry
rather than an exception. That contract must hold for a file that cannot be
read, a file that is not valid UTF-8 and a file that is not valid JSON.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from requirementcheck.registry import load_registry

UNREADABLE = "requirement registry is unreadable: "


def test_missing_file_is_recorded(tmp_path: Path) -> None:
    """A registry that does not exist is reported, not raised."""
    problems: list[str] = []

    assert load_registry(tmp_path / "absent.json", problems) == {}
    assert len(problems) == 1
    assert problems[0].startswith(UNREADABLE)


def test_invalid_utf8_is_recorded(tmp_path: Path) -> None:
    """Bytes that are not UTF-8 are reported like any other unreadable file."""
    path = tmp_path / "registry.json"
    path.write_bytes(b'{"id": "\xff\xfe"}')
    problems: list[str] = []

    assert load_registry(path, problems) == {}
    assert len(problems) == 1
    assert problems[0].startswith(UNREADABLE)


def test_invalid_json_is_recorded(tmp_path: Path) -> None:
    """A file that is not JSON is reported, not raised."""
    path = tmp_path / "registry.json"
    path.write_text("{not json}", encoding="utf-8")
    problems: list[str] = []

    assert load_registry(path, problems) == {}
    assert len(problems) == 1
    assert problems[0].startswith(UNREADABLE)


def test_valid_registry_returns_its_document(tmp_path: Path) -> None:
    """A readable registry returns its document and records nothing."""
    path = tmp_path / "registry.json"
    path.write_text('{"requirements": []}', encoding="utf-8")
    problems: list[str] = []

    assert load_registry(path, problems) == {"requirements": []}
    assert problems == []


@pytest.mark.parametrize("payload", [b"", b"\xf0\x28\x8c\x28"])
def test_decoding_failures_are_all_reported(tmp_path: Path, payload: bytes) -> None:
    """Each undecodable payload earns exactly one diagnostic."""
    path = tmp_path / "registry.json"
    path.write_bytes(payload)
    problems: list[str] = []

    assert load_registry(path, problems) == {}
    assert len(problems) == 1