import json
import os
from pathlib import Path
from typing import Any

import pytest

from loopcraft_core.canonical import sha256_digest
from loopcraft_core.evidence.entry import (
    EntryEvidenceValidationError,
    load_entry_evidence,
    validate_entry_evidence,
)


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
ENTRY_FIXTURE = FIXTURES / "entry-evidence.valid.json"
ONE_LOOP_DEFINITION = FIXTURES / "accepted-definition.valid.json"
ZERO_LOOP_DEFINITION = FIXTURES / "accepted-definition.zero-loop.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def valid_entry() -> dict[str, Any]:
    return load_json(ENTRY_FIXTURE)


@pytest.mark.parametrize(
    ("entry_type", "summary_kind"),
    [
        ("from_scratch", "design_interview"),
        ("existing_skill", "skill_assessment"),
        ("conversation", "workflow_model"),
    ],
)
def test_accepts_each_entry_type_with_its_source_summary_kind(
    entry_type: str,
    summary_kind: str,
) -> None:
    definition = load_json(ONE_LOOP_DEFINITION)
    evidence = valid_entry()
    evidence["entry_type"] = entry_type
    evidence["source_summary"]["kind"] = summary_kind

    validate_entry_evidence(evidence, definition)


def test_accepts_zero_loop_classification_and_empty_clarifications() -> None:
    definition = load_json(ZERO_LOOP_DEFINITION)
    evidence = valid_entry()
    evidence["definition_digest"] = sha256_digest(definition)
    evidence["clarifications"] = []
    evidence["candidate_review"]["classification"] = "zero_loop_workflow"
    evidence["candidate_review"]["summary"] = (
        "The reviewed zero-Loop Workflow may cite https://example.com/path."
    )

    validate_entry_evidence(evidence, definition)


def test_rejects_definition_outside_the_supported_loop_count() -> None:
    definition = load_json(ONE_LOOP_DEFINITION)
    definition["loops"].append(definition["loops"][0])
    evidence = valid_entry()
    evidence["definition_digest"] = sha256_digest(definition)

    with pytest.raises(EntryEvidenceValidationError, match="Loop count"):
        validate_entry_evidence(evidence, definition)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda item: item.update({"raw_conversation": "private"}), "schema"),
        (
            lambda item: item["source_summary"].update(
                {"raw_payload": {"messages": []}}
            ),
            "schema",
        ),
        (
            lambda item: item["approval"].update({"approved_by": "user"}),
            "schema",
        ),
        (
            lambda item: item["source_summary"].update(
                {"kind": "workflow_model"}
            ),
            "source summary kind",
        ),
        (
            lambda item: item["candidate_review"].update(
                {"classification": "zero_loop_workflow"}
            ),
            "classification",
        ),
        (
            lambda item: item.update({"definition_digest": "sha256:bad"}),
            "schema",
        ),
        (
            lambda item: item.update(
                {"definition_digest": "sha256:" + "0" * 64}
            ),
            "definition digest",
        ),
    ],
)
def test_rejects_shape_and_definition_binding_risks(
    mutate: Any,
    message: str,
) -> None:
    definition = load_json(ONE_LOOP_DEFINITION)
    evidence = valid_entry()
    mutate(evidence)

    with pytest.raises(EntryEvidenceValidationError, match=message):
        validate_entry_evidence(evidence, definition)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda item: item["clarifications"].append(
            {
                "question_summary": " ",
                "answer_summary": "Resolved answer",
                "resolution": "resolved",
            }
        ),
        lambda item: item["clarifications"].append(
            {
                "question_summary": "Material question",
                "answer_summary": "Resolved answer",
                "resolution": "pending",
            }
        ),
        lambda item: item["source_summary"].update({"source_ids": []}),
        lambda item: item["source_summary"].update({"summary": ""}),
        lambda item: item["source_summary"].update({"facts": []}),
        lambda item: item["approval"].update({"status": "pending"}),
        lambda item: item["approval"].update({"scope": "publish"}),
    ],
)
def test_rejects_empty_unresolved_or_unapproved_records(mutate: Any) -> None:
    definition = load_json(ONE_LOOP_DEFINITION)
    evidence = valid_entry()
    mutate(evidence)

    with pytest.raises(EntryEvidenceValidationError, match="schema"):
        validate_entry_evidence(evidence, definition)


@pytest.mark.parametrize(
    "unsafe_value",
    [
        r"C:\Users\Conrad\private.txt",
        "C:/Users/Conrad/private.txt",
        "/home/conrad/private.txt",
        "path:/home/conrad/private.txt",
        r"\\server\share\private.txt",
        "//server/share/private.txt",
    ],
)
def test_rejects_absolute_local_paths_anywhere_in_the_record(
    unsafe_value: str,
) -> None:
    definition = load_json(ONE_LOOP_DEFINITION)
    evidence = valid_entry()
    evidence["source_summary"]["facts"][0]["summary"] = (
        f"source={unsafe_value}"
    )

    with pytest.raises(EntryEvidenceValidationError, match="absolute local path"):
        validate_entry_evidence(evidence, definition)


def test_accepts_https_url_with_ipv6_host() -> None:
    definition = load_json(ONE_LOOP_DEFINITION)
    evidence = valid_entry()
    evidence["source_summary"]["facts"][0]["summary"] = (
        "source=https://[2001:db8::1]/path"
    )

    validate_entry_evidence(evidence, definition)


def test_loader_rejects_link_or_junction_without_reading_target(
    tmp_path: Path,
) -> None:
    target = tmp_path / "entry-evidence.json"
    target.write_text(ENTRY_FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
    link = tmp_path / "entry-link.json"
    try:
        os.symlink(target, link)
    except OSError as exc:
        pytest.skip(f"links unavailable: {exc}")

    with pytest.raises(ValueError, match="regular file"):
        load_entry_evidence(link, load_json(ONE_LOOP_DEFINITION))


def test_loader_returns_an_independent_validated_record() -> None:
    definition = load_json(ONE_LOOP_DEFINITION)

    loaded = load_entry_evidence(ENTRY_FIXTURE, definition)

    assert loaded == valid_entry()
    assert loaded is not valid_entry()
