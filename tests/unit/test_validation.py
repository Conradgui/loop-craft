import copy
import json
from pathlib import Path

import pytest

from loopcraft_core.validation import (
    DefinitionValidationError,
    _json_pointer,
    validate_definition,
)


FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "accepted-definition.valid.json"
)


def load_valid() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_valid_definition_passes_validation() -> None:
    validate_definition(load_valid())


def test_missing_behavior_contract_is_rejected() -> None:
    candidate = copy.deepcopy(load_valid())
    candidate.pop("behavior_contract")

    with pytest.raises(DefinitionValidationError) as captured:
        validate_definition(candidate)

    assert captured.value.issues[0].code == "schema"
    assert captured.value.issues[0].path == ""


def test_json_pointer_escapes_reference_tokens() -> None:
    assert _json_pointer(["a/b", "c~d", 0]) == "/a~1b/c~0d/0"


def test_unpaired_surrogate_is_reported_as_non_canonical_json() -> None:
    candidate = copy.deepcopy(load_valid())
    candidate["behavior_contract"]["identity"]["description"] = "\ud800"

    with pytest.raises(DefinitionValidationError) as captured:
        validate_definition(candidate)

    assert captured.value.issues[0].code == "non_canonical_json"
    assert captured.value.issues[0].path == ""
    assert "JSON compliant" in captured.value.issues[0].message


@pytest.mark.parametrize(
    "path",
    [
        ("behavior_contract", "identity", "id"),
        ("behavior_contract", "identity", "version"),
        ("loops", 0, "id"),
    ],
)
def test_identifiers_reject_trailing_newline(path: tuple[object, ...]) -> None:
    candidate = copy.deepcopy(load_valid())
    parent = candidate
    for key in path[:-1]:
        parent = parent[key]  # type: ignore[index]
    field = path[-1]
    parent[field] = f"{parent[field]}\n"  # type: ignore[index]

    with pytest.raises(DefinitionValidationError):
        validate_definition(candidate)


@pytest.mark.parametrize(
    "path",
    [
        ("behavior_contract", "identity", "name"),
        ("behavior_contract", "interface", "inputs", 0),
        ("behavior_contract", "authority", "allowed", 0),
        ("behavior_contract", "capabilities", "required", 0),
        ("behavior_contract", "capabilities", "optional", 0),
        ("loops", 0, "cycle", "observe"),
    ],
)
def test_free_text_rejects_whitespace_only(path: tuple[object, ...]) -> None:
    candidate = copy.deepcopy(load_valid())
    parent = candidate
    for key in path[:-1]:
        parent = parent[key]  # type: ignore[index]
    parent[path[-1]] = " \t\n"  # type: ignore[index]

    with pytest.raises(DefinitionValidationError):
        validate_definition(candidate)


def test_identity_id_accepts_64_characters() -> None:
    candidate = copy.deepcopy(load_valid())
    candidate["behavior_contract"]["identity"]["id"] = "a" * 64

    validate_definition(candidate)


def test_identity_id_rejects_65_characters() -> None:
    candidate = copy.deepcopy(load_valid())
    candidate["behavior_contract"]["identity"]["id"] = "a" * 65

    with pytest.raises(DefinitionValidationError):
        validate_definition(candidate)


@pytest.mark.parametrize("loop_count", [0, 2])
def test_core_slice_requires_exactly_one_loop(loop_count: int) -> None:
    candidate = copy.deepcopy(load_valid())
    source_loop = copy.deepcopy(candidate["loops"][0])
    candidate["loops"] = [copy.deepcopy(source_loop) for _ in range(loop_count)]

    with pytest.raises(DefinitionValidationError) as captured:
        validate_definition(candidate)

    assert any(issue.path == "/loops" for issue in captured.value.issues)
