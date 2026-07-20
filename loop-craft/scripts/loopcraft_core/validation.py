from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from loopcraft_core.canonical import canonical_json_bytes


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    path: str
    message: str


class DefinitionValidationError(ValueError):
    def __init__(self, issues: tuple[ValidationIssue, ...]) -> None:
        self.issues = issues
        summary = "; ".join(
            f"{issue.code} {issue.path}: {issue.message}" for issue in issues
        )
        super().__init__(summary)


SCHEMA_PATH = (
    Path(__file__).resolve().parent
    / "kernel"
    / "schemas"
    / "accepted-definition.schema.json"
)


def _json_pointer(parts: list[Any]) -> str:
    if not parts:
        return ""
    escaped = [str(part).replace("~", "~0").replace("/", "~1") for part in parts]
    return "/" + "/".join(escaped)


def schema_issues(definition: dict[str, Any]) -> tuple[ValidationIssue, ...]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema).iter_errors(definition),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    return tuple(
        ValidationIssue(
            code="schema",
            path=_json_pointer(list(error.absolute_path)),
            message=error.message,
        )
        for error in errors
    )


def validate_definition(definition: dict[str, Any]) -> None:
    issues = schema_issues(definition)
    if issues:
        raise DefinitionValidationError(issues)
    try:
        canonical_json_bytes(definition)
    except ValueError as exc:
        raise DefinitionValidationError(
            (
                ValidationIssue(
                    code="non_canonical_json",
                    path="",
                    message=str(exc),
                ),
            )
        ) from exc
