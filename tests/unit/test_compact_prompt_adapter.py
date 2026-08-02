import copy
import json
from pathlib import Path
from typing import Any

import pytest

from loopcraft_core.adapters.compact_prompt import render_compact_prompt
from loopcraft_core.canonical import sha256_digest
from loopcraft_core.compiler import CompileResult, compile_definition


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def load_fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def file_snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def reverse_mapping_order(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: reverse_mapping_order(item)
            for key, item in reversed(tuple(value.items()))
        }
    if isinstance(value, list):
        return [reverse_mapping_order(item) for item in value]
    return value


def assert_common_contract(result: Any, execution: dict[str, Any]) -> str:
    assert file_snapshot(result.artifact_dir).keys() == {"PROMPT.md"}
    assert result.adapter_name == "compact-prompt"
    assert result.adapter_version == "0.1.0"
    assert result.profile_digest.startswith("sha256:")
    assert result.execution_ir_digest == sha256_digest(execution)
    assert result.conformance == "runtime_delegated"
    assert result.compatibility_report["overall"] == "emulated"
    assert result.source_map["PROMPT.md#prompt"]
    return (result.artifact_dir / "PROMPT.md").read_text(encoding="utf-8")


def test_renders_one_loop_without_dropping_behavior_boundaries(
    tmp_path: Path,
) -> None:
    compiled = compile_definition(
        load_fixture("accepted-definition.valid.json")
    )

    result = render_compact_prompt(compiled, tmp_path)
    execution = compiled.final_execution_ir
    text = assert_common_contract(result, execution)

    expected = [
        execution["purpose"]["outcome"],
        *execution["applicability"]["use_when"],
        *execution["applicability"]["do_not_use_when"],
        *execution["interface"]["inputs"],
        *execution["interface"]["outputs"],
        *execution["authority"]["allowed"],
        *execution["authority"]["approval_required"],
        *execution["authority"]["forbidden"],
        *execution["capabilities"]["required"],
        *execution["capabilities"]["optional"],
    ]
    for loop in execution["loops"]:
        expected.extend(node["instruction"] for node in loop["nodes"])
        expected.extend(loop["terminal_mapping"].values())
        expected.extend(loop["invariants"])

    for value in expected:
        assert value in text
    assert "Inputs: skill_path" in text
    assert '["skill_path"]' not in text
    prompt_line = text.split("Prompt:\n> ", maxsplit=1)[1]
    assert prompt_line.rstrip().endswith("environment.")
    assert not prompt_line.rstrip().endswith("environment..")


def test_renders_zero_loop_workflow_without_inventing_a_loop(
    tmp_path: Path,
) -> None:
    compiled = compile_definition(
        load_fixture("accepted-definition.zero-loop.json")
    )

    result = render_compact_prompt(compiled, tmp_path)
    execution = compiled.final_execution_ir
    text = assert_common_contract(result, execution)
    workflow = execution["workflow"]

    for value in (
        *workflow["steps"],
        *workflow["success_evidence"],
        *workflow["failure_or_stop"],
    ):
        assert value in text
    assert "observe → choose → act → verify → record → adapt" not in text


def test_is_deterministic_for_equivalent_definitions(tmp_path: Path) -> None:
    definition = load_fixture("accepted-definition.valid.json")
    first = render_compact_prompt(
        compile_definition(definition),
        tmp_path / "first",
    )
    second = render_compact_prompt(
        compile_definition(reverse_mapping_order(definition)),
        tmp_path / "second",
    )

    assert file_snapshot(first.artifact_dir) == file_snapshot(
        second.artifact_dir
    )
    assert first.artifact_digest == second.artifact_digest
    assert first.source_map == second.source_map


def test_rejects_unknown_future_execution_fields(tmp_path: Path) -> None:
    compiled = compile_definition(
        load_fixture("accepted-definition.valid.json")
    )
    changed_execution = copy.deepcopy(compiled.final_execution_ir)
    changed_execution["runtime_binding"] = {"provider": "future"}
    changed = CompileResult(changed_execution, compiled.source_map)

    with pytest.raises(
        ValueError,
        match="unsupported Final Execution IR field: runtime_binding",
    ):
        render_compact_prompt(changed, tmp_path)
