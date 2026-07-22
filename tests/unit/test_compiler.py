import json
from pathlib import Path
from typing import Any

import pytest

from loopcraft_core.canonical import canonical_json_bytes, sha256_digest
from loopcraft_core.compiler import compile_definition
from loopcraft_core.validation import DefinitionValidationError


FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "accepted-definition.valid.json"
)
ZERO_LOOP_FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "accepted-definition.zero-loop.json"
)
CYCLE_ORDER = ("observe", "choose", "act", "verify", "record", "adapt")


def load_valid() -> dict[str, Any]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def reverse_mapping_order(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: reverse_mapping_order(item)
            for key, item in reversed(tuple(value.items()))
        }
    if isinstance(value, list):
        return [reverse_mapping_order(item) for item in value]
    return value


def test_compiler_is_canonically_deterministic_for_equivalent_definitions() -> None:
    definition = load_valid()
    reordered_definition = reverse_mapping_order(definition)

    first = compile_definition(definition)
    second = compile_definition(reordered_definition)

    assert canonical_json_bytes(first.final_execution_ir) == canonical_json_bytes(
        second.final_execution_ir
    )
    assert sha256_digest(first.final_execution_ir) == sha256_digest(
        second.final_execution_ir
    )
    assert first.final_execution_ir["definition_digest"] == second.final_execution_ir[
        "definition_digest"
    ]
    assert canonical_json_bytes(first.source_map) == canonical_json_bytes(
        second.source_map
    )


def test_compiler_maps_cycle_in_fixed_order() -> None:
    result = compile_definition(load_valid())
    nodes = result.final_execution_ir["loops"][0]["nodes"]

    assert [node["id"] for node in nodes] == list(CYCLE_ORDER)
    assert [node["next"] for node in nodes] == [
        "choose",
        "act",
        "verify",
        "record",
        "adapt",
        "observe",
    ]


def test_source_map_covers_all_critical_core_slice_fields() -> None:
    result = compile_definition(load_valid())
    source_map = result.source_map

    assert source_map["/schema_version"] == ["/schema_version"]
    assert source_map["/input_profile"] == ["/profile"]
    assert source_map["/definition_digest"] == [""]
    for field in (
        "identity",
        "purpose",
        "applicability",
        "interface",
        "authority",
        "capabilities",
    ):
        assert source_map[f"/{field}"] == [f"/behavior_contract/{field}"]

    assert source_map["/loops/0/id"] == ["/loops/0/id"]
    assert source_map["/loops/0/entrypoint"] == ["/loops/0/cycle/observe"]
    for node_index, node_id in enumerate(CYCLE_ORDER):
        next_id = CYCLE_ORDER[(node_index + 1) % len(CYCLE_ORDER)]
        output_path = f"/loops/0/nodes/{node_index}"
        assert source_map[f"{output_path}/id"] == [
            f"/loops/0/cycle/{node_id}"
        ]
        assert source_map[f"{output_path}/instruction"] == [
            f"/loops/0/cycle/{node_id}"
        ]
        assert source_map[f"{output_path}/next"] == [
            f"/loops/0/cycle/{next_id}"
        ]

    assert source_map["/loops/0/terminal_mapping"] == [
        "/loops/0/terminal_states"
    ]
    assert source_map["/loops/0/invariants"] == ["/loops/0/invariants"]
    assert "/compiler_version" not in source_map


def test_compiler_result_does_not_alias_the_input_definition() -> None:
    definition = load_valid()
    result = compile_definition(definition)
    original_ir_bytes = canonical_json_bytes(result.final_execution_ir)
    original_ir_digest = sha256_digest(result.final_execution_ir)
    original_source_map_bytes = canonical_json_bytes(result.source_map)
    original_definition_digest = result.final_execution_ir["definition_digest"]

    definition["behavior_contract"]["identity"]["name"] = "Changed"
    definition["behavior_contract"]["capabilities"]["required"].append(
        "network.write"
    )
    definition["loops"][0]["terminal_states"]["success"] = "Changed"
    definition["loops"][0]["invariants"].append("Changed")

    assert canonical_json_bytes(result.final_execution_ir) == original_ir_bytes
    assert canonical_json_bytes(result.source_map) == original_source_map_bytes
    assert result.final_execution_ir["definition_digest"] == original_definition_digest
    assert sha256_digest(result.final_execution_ir) == original_ir_digest


def test_compiler_validates_before_projecting_the_definition() -> None:
    definition = load_valid()
    definition.pop("behavior_contract")

    with pytest.raises(DefinitionValidationError):
        compile_definition(definition)


def test_compiler_projects_optional_workflow_without_synthesizing_a_loop() -> None:
    definition = json.loads(ZERO_LOOP_FIXTURE.read_text(encoding="utf-8"))

    result = compile_definition(definition)

    assert result.final_execution_ir["workflow"] == definition[
        "behavior_contract"
    ]["workflow"]
    assert result.final_execution_ir["loops"] == []
    assert result.source_map["/workflow/steps/0"] == [
        "/behavior_contract/workflow/steps/0"
    ]
