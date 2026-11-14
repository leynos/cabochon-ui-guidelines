#!/usr/bin/env python3
"""Check the live-relationship state contract.

The five visible states are a projection of independent facts. This checker
holds one typed source for the legal transitions, compares it with the chapter
table and the generated figure, and runs bounded event sequences against the
projection declared in the book. Replies carry a request generation, a dispatch
epoch and a validated vector, so a stale completion or failure is rejected by
identity rather than by a pre-classified event name. Provider availability is
recorded even while authority is denied; the projection still returns Denied.

Run from the repository root with ``python3 -I tools/check-states.py``. Pass
``--self-test`` to prove that each projection, fact and reply-identity mutation
is detected.
"""

from __future__ import annotations

import copy
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "tools" / "figure-data.json").read_text(encoding="utf-8"))
FIXTURES = json.loads(
    (ROOT / "tools" / "state-fixtures.json").read_text(encoding="utf-8")
)
CHAPTER = ROOT / "book" / "08-live-relationships.md"
FIGURE = ROOT / "figures" / "fig-06-state.svg"

SVG_NS = "{http://www.w3.org/2000/svg}"
STATES = set(DATA["live_states"])
FROM_TOKENS = STATES | {"Any state", "Any state except Denied"}
TARGETS = STATES | {"Recomputed", "No change"}
EDGE_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def transition_rows() -> list[dict[str, object]]:
    return DATA["live_transitions"]


def validate_transitions(
    transitions: list[dict[str, object]],
) -> list[str]:
    """Check that the typed transition source is complete and well formed."""
    errors: list[str] = []
    seen: set[str] = set()
    for record in transitions:
        identifier = str(record.get("id", ""))
        if not EDGE_ID.match(identifier):
            errors.append(f"transition {identifier!r}: id is not kebab-case")
        if identifier in seen:
            errors.append(f"transition {identifier!r}: duplicate id")
        seen.add(identifier)
        sources = record.get("from")
        if not isinstance(sources, list) or not sources:
            errors.append(f"transition {identifier!r}: no source states")
            continue
        for source in sources:
            if source not in FROM_TOKENS:
                errors.append(
                    f"transition {identifier!r}: unknown source {source!r}"
                )
        if record.get("to") not in TARGETS:
            errors.append(
                f"transition {identifier!r}: unknown target {record.get('to')!r}"
            )
        if not str(record.get("owner", "")).strip():
            errors.append(f"transition {identifier!r}: no owner")
        if not str(record.get("event", "")).strip():
            errors.append(f"transition {identifier!r}: no event")

    targets = {record.get("to") for record in transitions}
    for state in sorted(STATES - targets):
        errors.append(f"state {state!r} is not the target of any transition")

    revocations = [
        record
        for record in transitions
        if record.get("to") == "Denied"
        and "Any state" in record.get("from", [])
    ]
    if not revocations:
        errors.append("revocation is not available from every state")
    losses = [
        record
        for record in transitions
        if record.get("to") == "Broken"
        and "Any state except Denied" in record.get("from", [])
    ]
    if not losses:
        errors.append("provider loss is not available from every state but Denied")
    absent_grants = [
        record
        for record in transitions
        if record.get("to") == "Broken"
        and "Denied" in record.get("from", [])
        and "provider is absent" in str(record.get("event", ""))
    ]
    if not absent_grants:
        errors.append("a grant issued while the provider is absent is not modelled")
    return errors


def chapter_rows() -> list[tuple[str, str, str, str]]:
    """Read the transition table under the chapter's Transitions heading."""
    text = CHAPTER.read_text(encoding="utf-8")
    match = re.search(r"^## Transitions\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if match is None:
        raise SystemExit("state contract: chapter 08 has no Transitions section")
    rows: list[tuple[str, str, str, str]] = []
    for raw in match.group(1).splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 4:
            continue
        if cells[0] in {"From", "-------"} or set(cells[0]) <= {"-"}:
            continue
        if all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        rows.append((cells[0], cells[1], cells[2], cells[3]))
    return rows


def compare_chapter(transitions: list[dict[str, object]]) -> list[str]:
    errors: list[str] = []
    declared = [
        (
            ", ".join(record["from"]),
            str(record["event"]),
            str(record["to"]),
            str(record["owner"]),
        )
        for record in transitions
    ]
    actual = chapter_rows()
    for row in sorted(set(declared) - set(actual)):
        errors.append(f"chapter 08 is missing transition {row!r}")
    for row in sorted(set(actual) - set(declared)):
        errors.append(f"chapter 08 declares unknown transition {row!r}")
    if len(actual) != len(declared):
        errors.append(
            f"chapter 08 lists {len(actual)} transitions, "
            f"the typed source has {len(declared)}"
        )
    return errors


def compare_figure(transitions: list[dict[str, object]]) -> list[str]:
    errors: list[str] = []
    if not FIGURE.exists():
        return [f"{FIGURE.name} does not exist; run make figures"]
    root = ET.parse(FIGURE).getroot()
    labels = {
        (element.text or "").strip() for element in root.iter(f"{SVG_NS}text")
    }
    for record in transitions:
        source = ", ".join(record["from"])
        for field in ("event", "to", "owner"):
            value = str(record[field])
            if value not in labels:
                errors.append(
                    f"figure does not render {field} of {record['id']!r}: {value!r}"
                )
        if source not in labels:
            errors.append(
                f"figure does not render source of {record['id']!r}: {source!r}"
            )
    return errors


def vector_at_least(
    validated: dict[str, int], known: dict[str, int]
) -> bool:
    return all(validated.get(key, -1) >= value for key, value in known.items())


def project(facts: dict[str, object]) -> str:
    """The total projection from facts, in the book's declared order."""
    if not facts["authorized"]:
        return "Denied"
    if facts["request_active"]:
        return "Refreshing"
    if facts["availability"] != "present" or not facts["accepted"]:
        return "Broken"
    fresh = (
        facts["accepted_epoch"] == facts["invalidation_epoch"]
        and vector_at_least(
            facts["accepted_validated"], facts["known_source"]
        )
    )
    return "Current" if fresh else "Stale"


NO_DATA_EVENTS = {
    "grant_revoked",
    "grant_issued",
    "provider_lost",
    "provider_recovered",
    "source_advanced",
    "refresh_requested",
}
REPLY_FIELDS = {
    "refresh_succeeded": ("generation", "epoch", "validated"),
    "refresh_failed": ("generation", "epoch"),
    "refresh_cancelled": ("generation",),
}
EVENTS = NO_DATA_EVENTS | set(REPLY_FIELDS)


def validate_step(
    scenario: str, index: int, step: dict[str, object]
) -> list[str]:
    """Check that a fixture step carries exactly the data its event needs."""
    errors: list[str] = []
    event = step.get("event")
    where = f"scenario {scenario!r} step {index + 1}"
    if event not in EVENTS:
        return [f"{where}: unknown event {event!r}"]
    expected = step.get("expected")
    if expected not in STATES:
        errors.append(f"{where}: invalid expected state {expected!r}")
    allowed = {"event", "expected"} | set(REPLY_FIELDS.get(str(event), ()))
    extra = set(step) - allowed
    if extra:
        errors.append(f"{where}: unexpected fields {sorted(extra)!r}")
    for field in REPLY_FIELDS.get(str(event), ()):
        if field not in step:
            errors.append(f"{where}: missing reply field {field!r}")
            continue
        if field == "validated":
            vector = step[field]
            if (
                not isinstance(vector, dict)
                or not vector
                or not all(
                    isinstance(key, str)
                    and isinstance(value, int)
                    and value >= 0
                    for key, value in vector.items()
                )
            ):
                errors.append(
                    f"{where}: validated vector is not a non-empty "
                    "map of names to non-negative integers"
                )
        elif (
            not isinstance(step[field], int)
            or step[field] < (1 if field == "generation" else 0)
        ):
            qualifier = "positive" if field == "generation" else "non-negative"
            errors.append(f"{where}: {field} is not a {qualifier} integer")
    return errors


def apply(
    facts: dict[str, object],
    step: dict[str, object],
    *,
    observe_provider_while_denied: bool = True,
    check_reply_identity: bool = True,
) -> None:
    """Apply one event and its reply identity to the fact set."""
    event = step["event"]
    if event == "grant_revoked":
        facts["authorized"] = False
        facts["request_active"] = False
        facts["invalidation_epoch"] += 1
    elif event == "grant_issued":
        facts["authorized"] = True
    elif event == "provider_lost":
        if observe_provider_while_denied or facts["authorized"]:
            facts["availability"] = "lost"
            facts["request_active"] = False
            facts["invalidation_epoch"] += 1
    elif event == "provider_recovered":
        if observe_provider_while_denied or facts["authorized"]:
            facts["availability"] = "present"
    elif event == "source_advanced":
        if facts["authorized"] and facts["availability"] == "present":
            for key in facts["known_source"]:
                facts["known_source"][key] += 1
            if facts["request_active"]:
                # The notification supersedes the in-flight generation. The
                # replacement request covers the vector that has just arrived.
                facts["request_generation"] += 1
                facts["request_covers"] = dict(facts["known_source"])
    elif event == "refresh_requested":
        if facts["authorized"] and facts["availability"] == "present":
            facts["request_generation"] += 1
            facts["request_active"] = True
            facts["request_covers"] = dict(facts["known_source"])
    elif event == "refresh_succeeded":
        if facts["authorized"] and facts["request_active"]:
            matching = (
                not check_reply_identity
                or (
                    step["generation"] == facts["request_generation"]
                    and step["epoch"] == facts["invalidation_epoch"]
                    and vector_at_least(
                        step["validated"], facts["known_source"]
                    )
                    and vector_at_least(
                        step["validated"], facts["request_covers"]
                    )
                )
            )
            if matching:
                facts["request_active"] = False
                facts["availability"] = "present"
                facts["accepted"] = True
                facts["accepted_validated"] = dict(step["validated"])
                facts["accepted_epoch"] = facts["invalidation_epoch"]
    elif event == "refresh_failed":
        if facts["authorized"] and facts["request_active"]:
            matching = (
                not check_reply_identity
                or (
                    step["generation"] == facts["request_generation"]
                    and step["epoch"] == facts["invalidation_epoch"]
                )
            )
            if matching:
                facts["request_active"] = False
                facts["availability"] = "uncertain"
    elif event == "refresh_cancelled":
        matching = not check_reply_identity or (
            step["generation"] == facts["request_generation"]
        )
        if facts["request_active"] and matching:
            facts["request_active"] = False
    else:
        raise SystemExit(f"state contract: unknown fixture event {event!r}")


def run_scenario(
    scenario: dict[str, object],
    *,
    observe_provider_while_denied: bool = True,
    check_reply_identity: bool = True,
) -> list[str]:
    """Run one fixture sequence and report every projection mismatch."""
    errors: list[str] = []
    facts = copy.deepcopy(FIXTURES["defaults"])
    facts.update(copy.deepcopy(scenario.get("facts", {})))
    for index, step in enumerate(scenario["events"]):
        step_errors = validate_step(str(scenario["name"]), index, step)
        if step_errors:
            errors.extend(step_errors)
            continue
        apply(
            facts,
            step,
            observe_provider_while_denied=observe_provider_while_denied,
            check_reply_identity=check_reply_identity,
        )
        actual = project(facts)
        if actual != step["expected"]:
            errors.append(
                f"scenario {scenario['name']!r} after {step['event']!r}: "
                f"projected {actual}, expected {step['expected']}"
            )
    return errors


def run_scenarios() -> list[str]:
    errors: list[str] = []
    for scenario in FIXTURES["scenarios"]:
        errors.extend(run_scenario(scenario))
    return errors


def scenario_named(name: str) -> dict[str, object]:
    for scenario in FIXTURES["scenarios"]:
        if scenario["name"] == name:
            return scenario
    raise SystemExit(f"state contract: fixture {name!r} is missing")


def check_scenario_sensitivity() -> list[str]:
    """Prove that the fixtures catch projection, fact and reply defects."""
    errors: list[str] = []
    first_load = copy.deepcopy(FIXTURES["defaults"])
    first_load["request_active"] = True

    def broken_first(facts: dict[str, object]) -> str:
        if not facts["accepted"]:
            return "Broken"
        return project(facts)

    if broken_first(first_load) == project(first_load):
        errors.append("self-test: Broken no-cache projection was not detected")

    recovered = copy.deepcopy(FIXTURES["defaults"])
    recovered["accepted"] = True
    recovered["accepted_validated"] = {"rate": 1}
    recovered["invalidation_epoch"] = 1

    def ignore_epoch(facts: dict[str, object]) -> str:
        if not facts["authorized"]:
            return "Denied"
        if facts["request_active"]:
            return "Refreshing"
        if facts["availability"] != "present" or not facts["accepted"]:
            return "Broken"
        fresh = vector_at_least(
            facts["accepted_validated"], facts["known_source"]
        )
        return "Current" if fresh else "Stale"

    if ignore_epoch(recovered) == project(recovered):
        errors.append("self-test: ignored invalidation epoch was not detected")

    provider_scenario = scenario_named("provider loss while denied is remembered")
    if run_scenario(provider_scenario):
        errors.append("self-test: provider-fact fixture does not pass")
    if not run_scenario(
        provider_scenario, observe_provider_while_denied=False
    ):
        errors.append(
            "self-test: provider facts ignored while denied were not detected"
        )

    reply_scenario = scenario_named("superseded reply is discarded")
    if run_scenario(reply_scenario):
        errors.append("self-test: reply-identity fixture does not pass")
    if not run_scenario(reply_scenario, check_reply_identity=False):
        errors.append("self-test: ignored reply identity was not detected")
    return errors


def self_test() -> int:
    failures: list[str] = []
    checks = 0

    def require(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            failures.append(message)

    transitions = copy.deepcopy(transition_rows())

    without_revocation = [
        record for record in transitions if record["id"] != "authority-revoked"
    ]
    require(
        any(
            "revocation is not available" in error
            for error in validate_transitions(without_revocation)
        ),
        "missing revocation edge was not detected",
    )

    without_absent_grant = [
        record
        for record in transitions
        if record["id"] != "grant-issued-provider-absent"
    ]
    require(
        any(
            "provider is absent is not modelled" in error
            for error in validate_transitions(without_absent_grant)
        ),
        "missing provider-absent grant edge was not detected",
    )

    wrong_owner = copy.deepcopy(transitions)
    for record in wrong_owner:
        if record["id"] == "refresh-denied":
            record["owner"] = "Host"
    require(
        any(
            "unknown transition" in error
            for error in compare_chapter(wrong_owner)
        ),
        "owner drift from the chapter table was not detected",
    )

    sensitivity = check_scenario_sensitivity()
    for label in (
        "Broken no-cache projection",
        "ignored invalidation epoch",
        "provider facts ignored while denied",
        "ignored reply identity",
    ):
        require(
            not any(label in error for error in sensitivity),
            f"{label} was not detected",
        )
    for error in sensitivity:
        if not any(
            label in error
            for label in (
                "Broken no-cache projection",
                "ignored invalidation epoch",
                "provider facts ignored while denied",
                "ignored reply identity",
            )
        ):
            require(False, error)

    missing_event = copy.deepcopy(transitions)
    missing_event[0]["event"] = "An event the figure omits"
    require(
        any(
            "figure does not render event" in error
            for error in compare_figure(missing_event)
        ),
        "figure drift from the typed source was not detected",
    )

    if failures:
        for failure in failures:
            print(f"state contract self-test: {failure}", file=sys.stderr)
        return 1
    print(f"state contract self-test detected all {checks} mutations")
    return 0


def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()
    transitions = transition_rows()
    errors = validate_transitions(transitions)
    errors.extend(compare_chapter(transitions))
    errors.extend(compare_figure(transitions))
    errors.extend(run_scenarios())
    if errors:
        for error in errors:
            print(f"state contract: {error}", file=sys.stderr)
        return 1
    print(
        f"state contract: {len(transitions)} transitions and "
        f"{len(FIXTURES['scenarios'])} event scenarios satisfy the projection"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
