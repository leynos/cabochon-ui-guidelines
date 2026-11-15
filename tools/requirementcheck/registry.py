"""Check the registry schema, its records and their ownership.

The `load_registry` and `check_records` functions validate
`tools/requirements.json` against the schema, each owner anchor and the parsed
checklist. `requirementcheck.checks` imports both.
"""

from __future__ import annotations

import json
import typing as typ

from markdown_structure import anchors

from requirementcheck.contract import PROFILE_ORDER, REQUIREMENT_RE

if typ.TYPE_CHECKING:
    from pathlib import Path


def load_registry(path: Path, problems: list[str]) -> dict[str, object]:
    """Load the registry, recording an unreadable file as a problem.

    Parameters
    ----------
    path : Path
        The JSON registry to read as UTF-8.
    problems : list[str]
        Diagnostics collected for the caller. The list is appended to in
        place and never cleared. A file that cannot be read or decoded adds
        ``"requirement registry is unreadable: <error>"``, where ``<error>``
        is the exception's message.

    Returns
    -------
    dict[str, object]
        The decoded JSON document, normally an object, or an empty
        dictionary when the file cannot be read or decoded. Later checks
        treat an empty result as a missing registry.
    """
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        problems.append(f"requirement registry is unreadable: {error}")
        return {}


def _check_record_identity(
    record: dict[str, object], seen: set[str], problems: list[str]
) -> str:
    """Check that a requirement record declares its identity."""
    identifier = str(record.get("id", "<missing>"))
    if identifier in seen:
        problems.append(f"duplicate registry identifier {identifier}")
    seen.add(identifier)
    if not REQUIREMENT_RE.fullmatch(f"**{identifier}**"):
        problems.append(f"registry identifier {identifier} is malformed")
    return identifier


def _check_record_owner(
    identifier: str,
    record: dict[str, object],
    root: Path,
    problems: list[str],
) -> tuple[str, str]:
    """Check that a requirement record names a real chapter."""
    owner = record.get("owner")
    if not isinstance(owner, dict):
        problems.append(f"{identifier}: no owner")
        return "", ""
    file_name = str(owner.get("file", ""))
    anchor = str(owner.get("anchor", ""))
    path = root / "book" / file_name
    if not path.is_file():
        problems.append(f"{identifier}: missing owner file {file_name!r}")
    elif anchor not in anchors(path):
        problems.append(f"{identifier}: missing owner anchor {file_name}#{anchor}")
    return file_name, anchor


def _check_record_metadata(
    identifier: str,
    record: dict[str, object],
    schema: tuple[list[object], list[object]],
    problems: list[str],
) -> None:
    """Check the record's force, profile and applicability predicate."""
    forces, profiles = schema
    if record.get("force") not in forces:
        problems.append(f"{identifier}: invalid force {record.get('force')!r}")
    if record.get("profile") not in profiles:
        problems.append(f"{identifier}: invalid profile {record.get('profile')!r}")
    predicate = record.get("applies_when")
    if not isinstance(predicate, str) or not predicate.strip():
        problems.append(f"{identifier}: no applicability predicate")


def _check_record_evidence(
    identifier: str,
    record: dict[str, object],
    routes: list[object],
    problems: list[str],
) -> None:
    """Check that a requirement record cites usable evidence."""
    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        problems.append(f"{identifier}: no evidence route")
        return
    for step in evidence:
        if not isinstance(step, dict):
            problems.append(f"{identifier}: evidence route is not a record")
            continue
        if step.get("route") not in routes:
            problems.append(
                f"{identifier}: invalid evidence route {step.get('route')!r}"
            )
        detail = step.get("detail")
        if not isinstance(detail, str) or not detail.strip():
            problems.append(f"{identifier}: evidence route has no detail")


def _check_checklist_owner(
    identifier: str,
    owner: tuple[str, str],
    checklist: dict[str, list[str]],
    problems: list[str],
) -> None:
    """Check that the checklist item names the registry's owner."""
    file_name, anchor = owner
    if identifier not in checklist:
        problems.append(f"registry record {identifier} has no checklist item")
        return
    expected_owner = f"{file_name}#{anchor}" if anchor else file_name
    if expected_owner not in checklist[identifier]:
        problems.append(
            f"{identifier}: checklist owner disagrees with registry "
            f"owner {expected_owner!r}"
        )


def _check_checklist_coverage(
    checklist: dict[str, list[str]], seen: set[str], problems: list[str]
) -> None:
    """Check that the checklist covers every requirement."""
    problems.extend(
        f"checklist item {identifier} has no registry record"
        for identifier in checklist
        if identifier not in seen
    )


def _check_profile_coverage(
    records: list[dict[str, object]], problems: list[str]
) -> None:
    """Check that every declared profile has requirements."""
    for profile in ("semantic", "studio"):
        rank = PROFILE_ORDER[profile]
        applicable = [
            record
            for record in records
            if record.get("force") == "must"
            and PROFILE_ORDER.get(str(record.get("profile")), -1) <= rank
        ]
        if not applicable:
            problems.append(
                f"profile {profile} inherits no applicable must requirement"
            )


def _schema_list(registry: dict[str, object], key: str) -> list[object] | None:
    """Return a registry schema list, or None when the value is not a list."""
    value = registry.get(key)
    return value if isinstance(value, list) else None


def check_records(
    registry: dict[str, object],
    checklist: dict[str, list[str]],
    root: Path,
    problems: list[str],
) -> None:
    """Check the registry schema, records, ownership and profile coverage.

    An empty registry, a missing schema list or a missing or empty
    requirements list stops the check after its message is recorded.
    Otherwise every record is checked, and the checklist and profiles are
    compared against it.

    Parameters
    ----------
    registry : dict[str, object]
        The decoded ``tools/requirements.json`` document.
    checklist : dict[str, list[str]]
        The checklist parsed by `parse_checklist`.
    root : Path
        The repository root; each owner file is resolved under
        ``root / "book"``.
    problems : list[str]
        Diagnostics collected for the caller. The list is appended to in
        place and never cleared, so several messages may be added for one
        record. Schema messages are:

        * ``"requirement registry is empty"``;
        * ``"registry schema lists are missing"``;
        * ``"registry has no requirements"``;
        * ``"registry contains a record that is not an object"``.

        Most record messages begin with the identifier, as in
        ``"CON-01: no owner"``, and report a duplicate or malformed
        identifier, a missing owner, an owner file or anchor that does not
        exist, an invalid ``force`` or ``profile``, no applicability
        predicate, a missing or invalid evidence route, or a checklist
        owner that disagrees with the registry. The checklist and profile
        coverage checks add:

        * ``"checklist item <id> has no registry record"``;
        * ``"registry record <id> has no checklist item"``;
        * ``"profile <name> inherits no applicable must requirement"``
          when ``semantic`` or ``studio`` has no applicable ``must``
          requirement.

    Returns
    -------
    None
        The function reports only through `problems` and returns nothing.
    """
    if not registry:
        problems.append("requirement registry is empty")
        return
    profiles = _schema_list(registry, "profiles")
    forces = _schema_list(registry, "forces")
    routes = _schema_list(registry, "evidence_routes")
    if profiles is None or forces is None:
        problems.append("registry schema lists are missing")
        return
    if routes is None:
        problems.append("registry schema lists are missing")
        return
    records = registry.get("requirements", [])
    if not isinstance(records, list) or not records:
        problems.append("registry has no requirements")
        return
    typed_records = [record for record in records if isinstance(record, dict)]
    if len(typed_records) != len(records):
        problems.append("registry contains a record that is not an object")
    seen: set[str] = set()
    for record in typed_records:
        identifier = _check_record_identity(record, seen, problems)
        owner = _check_record_owner(identifier, record, root, problems)
        _check_record_metadata(identifier, record, (forces, profiles), problems)
        _check_record_evidence(identifier, record, routes, problems)
        _check_checklist_owner(identifier, owner, checklist, problems)
    _check_checklist_coverage(checklist, seen, problems)
    _check_profile_coverage(typed_records, problems)
