import copy
import json
from pathlib import Path

import pytest

from loopcraft_core.validation import DefinitionValidationError, validate_definition


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
    assert captured.value.issues[0].path == "/"


@pytest.mark.parametrize("loop_count", [0, 2])
def test_core_slice_requires_exactly_one_loop(loop_count: int) -> None:
    candidate = copy.deepcopy(load_valid())
    source_loop = copy.deepcopy(candidate["loops"][0])
    candidate["loops"] = [copy.deepcopy(source_loop) for _ in range(loop_count)]

    with pytest.raises(DefinitionValidationError) as captured:
        validate_definition(candidate)

    assert any(issue.path == "/loops" for issue in captured.value.issues)
