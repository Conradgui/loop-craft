from __future__ import annotations

from collections.abc import Iterator
import json
from pathlib import Path
import re
from typing import Any

from jsonschema import Draft202012Validator

from ..adapters.source_skill import is_link_or_junction
from ..canonical import canonical_json_bytes, sha256_digest


SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "kernel"
    / "schemas"
    / "entry-evidence.schema.json"
)
ENTRY_SUMMARY_KINDS = {
    "from_scratch": "design_interview",
    "existing_skill": "skill_assessment",
    "conversation": "workflow_model",
}
LOCAL_ABSOLUTE_PATH = re.compile(
    r"(?i)(?:"
    r"(?<![a-z0-9])[a-z]:[\\/]"
    r"|\\\\(?:\?\\)?[^\\/\s]+[\\/][^\\/\s]+"
    r"|(?<![:/])//[^/\s]+/[^/\s]+"
    r"|(?<![a-z0-9/\]])/(?![\s/])"
    r"|(?<![a-z0-9])file:(?://)?/"
    r")"
)


class EntryEvidenceValidationError(ValueError):
    pass


def _iter_strings(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _iter_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_strings(child)


def validate_entry_evidence(
    entry_evidence: dict[str, Any],
    definition: dict[str, Any],
) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema).iter_errors(entry_evidence),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    if errors:
        summary = "; ".join(error.message for error in errors)
        raise EntryEvidenceValidationError(f"entry evidence schema: {summary}")

    try:
        canonical_json_bytes(entry_evidence)
    except ValueError as exc:
        raise EntryEvidenceValidationError(
            f"entry evidence is not canonical JSON: {exc}"
        ) from exc

    expected_kind = ENTRY_SUMMARY_KINDS[entry_evidence["entry_type"]]
    if entry_evidence["source_summary"]["kind"] != expected_kind:
        raise EntryEvidenceValidationError(
            "entry evidence source summary kind does not match entry type"
        )

    classifications = {
        0: "zero_loop_workflow",
        1: "one_loop_bounded_loop",
    }
    loop_count = len(definition.get("loops", []))
    if loop_count not in classifications:
        raise EntryEvidenceValidationError(
            "accepted definition Loop count must be zero or one"
        )
    expected_classification = classifications[loop_count]
    if (
        entry_evidence["candidate_review"]["classification"]
        != expected_classification
    ):
        raise EntryEvidenceValidationError(
            "entry evidence classification does not match accepted definition"
        )

    if entry_evidence["definition_digest"] != sha256_digest(definition):
        raise EntryEvidenceValidationError(
            "entry evidence definition digest does not match accepted definition"
        )

    if any(
        LOCAL_ABSOLUTE_PATH.search(value)
        for value in _iter_strings(entry_evidence)
    ):
        raise EntryEvidenceValidationError(
            "entry evidence must not contain an absolute local path"
        )


def load_entry_evidence(
    path: Path,
    definition: dict[str, Any],
) -> dict[str, Any]:
    if is_link_or_junction(path) or not path.is_file():
        raise ValueError("entry evidence must be a regular file")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("entry evidence is unavailable or invalid") from exc
    if not isinstance(value, dict):
        raise EntryEvidenceValidationError("entry evidence must be an object")
    validate_entry_evidence(value, definition)
    return value
