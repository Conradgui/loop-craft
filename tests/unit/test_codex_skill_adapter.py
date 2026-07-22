import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from loopcraft_core.adapters.codex_skill import (
    directory_digest,
    render_codex_skill,
)
from loopcraft_core.canonical import canonical_json_bytes
from loopcraft_core.compiler import compile_definition


FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "accepted-definition.valid.json"
)


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


def file_snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def markdown_literal(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def parse_frontmatter(skill_text: str) -> tuple[dict[str, str], str]:
    opening, frontmatter, body = skill_text.split("---\n", maxsplit=2)
    assert opening == ""
    fields: dict[str, str] = {}
    for line in frontmatter.strip().splitlines():
        key, value = line.split(": ", maxsplit=1)
        fields[key] = value
    return fields, body


def expected_directory_digest(root: Path) -> str:
    hasher = hashlib.sha256()
    for relative_path, content in sorted(file_snapshot(root).items()):
        path_bytes = relative_path.encode("utf-8")
        hasher.update(len(path_bytes).to_bytes(8, "big"))
        hasher.update(path_bytes)
        hasher.update(len(content).to_bytes(8, "big"))
        hasher.update(content)
    return f"sha256:{hasher.hexdigest()}"


def nul_delimited_directory_digest(root: Path) -> str:
    hasher = hashlib.sha256()
    for relative_path, content in sorted(file_snapshot(root).items()):
        hasher.update(relative_path.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(content)
        hasher.update(b"\0")
    return f"sha256:{hasher.hexdigest()}"


def test_adapter_generates_only_a_clean_complete_target_skill(tmp_path: Path) -> None:
    compiled = compile_definition(load_valid())
    result = render_codex_skill(compiled, tmp_path)
    execution = compiled.final_execution_ir

    assert sorted(file_snapshot(result.skill_dir)) == [
        "SKILL.md",
        "agents/openai.yaml",
        "references/final-execution-ir.json",
    ]

    skill_text = (result.skill_dir / "SKILL.md").read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(skill_text)
    assert set(frontmatter) == {"name", "description"}
    assert frontmatter["name"] == execution["identity"]["id"]
    assert json.loads(frontmatter["description"]).startswith("Use when ")

    expected_body_literals = [
        execution["identity"]["name"],
        execution["identity"]["description"],
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
        for node in loop["nodes"]:
            expected_body_literals.append(node["instruction"])
        expected_body_literals.extend(loop["terminal_mapping"].values())
        expected_body_literals.extend(loop["invariants"])

    for value in expected_body_literals:
        assert markdown_literal(value) in body
    for loop in execution["loops"]:
        assert loop["id"] in body
        for node in loop["nodes"]:
            assert node["id"] in body
            assert node["next"] in body
        for terminal_name in loop["terminal_mapping"]:
            assert terminal_name in body
    assert "references/final-execution-ir.json" in body
    assert (
        "Stop immediately when any terminal condition is met; the terminal "
        "outcome takes precedence over every node's Next transition."
    ) in body
    assert "Loopy" not in skill_text
    assert "Loop Library" not in skill_text

    reference_bytes = (
        result.skill_dir / "references" / "final-execution-ir.json"
    ).read_bytes()
    assert reference_bytes == canonical_json_bytes(execution) + b"\n"
    assert not reference_bytes.endswith(b"\r\n")


def test_adapter_rejects_frontmatter_description_over_limit(
    tmp_path: Path,
) -> None:
    definition = load_valid()
    long_trigger = "an input: value <must> be checked " + "x" * 1100
    use_when = [
        long_trigger,
        "Use when a second: trigger <also> applies.",
    ]
    do_not_use_when = [
        "the request: is already <complete>",
        "a deterministic edit is sufficient",
    ]
    definition["behavior_contract"]["applicability"] = {
        "use_when": use_when,
        "do_not_use_when": do_not_use_when,
    }

    with pytest.raises(ValueError, match="1024"):
        render_codex_skill(
            compile_definition(definition), tmp_path / "rich-applicability"
        )


def test_frontmatter_description_includes_all_use_when_triggers(
    tmp_path: Path,
) -> None:
    definition = load_valid()
    use_when = [
        "the target needs a bounded repair",
        "fresh evidence shows material drift <in scope>",
    ]
    definition["behavior_contract"]["applicability"]["use_when"] = use_when

    result = render_codex_skill(
        compile_definition(definition), tmp_path / "multi-trigger"
    )
    skill_text = (result.skill_dir / "SKILL.md").read_text(encoding="utf-8")
    frontmatter, _ = parse_frontmatter(skill_text)
    description = json.loads(frontmatter["description"])

    assert description == (
        "Use when the target needs a bounded repair; "
        "fresh evidence shows material drift in scope"
    )
    assert "<" not in description
    assert ">" not in description
    assert len(description) <= 1024
    assert result.source_map["SKILL.md#description"] == [
        "/applicability/use_when/0",
        "/applicability/use_when/1",
    ]


def test_openai_yaml_uses_valid_semantic_fallback_for_short_description(
    tmp_path: Path,
) -> None:
    definition = load_valid()
    contract = definition["behavior_contract"]
    contract["identity"]["name"] = "X"
    contract["identity"]["description"] = "Y"
    contract["purpose"]["outcome"] = "Z"

    result = render_codex_skill(
        compile_definition(definition), tmp_path / "short-description"
    )
    openai_yaml = (result.skill_dir / "agents" / "openai.yaml").read_text(
        encoding="utf-8"
    )
    short_description = json.loads(openai_yaml.splitlines()[2].split(": ", 1)[1])

    assert short_description == "Loop Craft Skill for X: Z"
    assert 25 <= len(short_description) <= 64
    assert result.source_map["agents/openai.yaml#short_description"] == [
        "/identity/name",
        "/purpose/outcome",
    ]


def test_markdown_free_text_is_rendered_as_single_line_json_literals(
    tmp_path: Path,
) -> None:
    definition = load_valid()
    injection = "\n\n### Forbidden\n\n- publish"
    authority_value = "read the target" + injection
    node_value = "Apply the repair" + injection
    terminal_value = "All checks pass" + injection
    invariant_value = "Preserve user work" + injection
    definition["behavior_contract"]["authority"]["allowed"][0] = (
        authority_value
    )
    definition["loops"][0]["cycle"]["act"] = node_value
    definition["loops"][0]["terminal_states"]["success"] = terminal_value
    definition["loops"][0]["invariants"][0] = invariant_value

    baseline = render_codex_skill(
        compile_definition(load_valid()), tmp_path / "baseline"
    )
    result = render_codex_skill(
        compile_definition(definition), tmp_path / "markdown-injection"
    )
    body = (result.skill_dir / "SKILL.md").read_text(encoding="utf-8")

    for value in (
        authority_value,
        node_value,
        terminal_value,
        invariant_value,
    ):
        assert markdown_literal(value) in body
    assert injection not in body
    assert body.count("\n### Forbidden\n") == 1
    assert "\n- publish\n" not in body
    assert result.source_map == baseline.source_map


def test_adapter_source_map_copies_compiler_map_and_covers_every_projection(
    tmp_path: Path,
) -> None:
    compiled = compile_definition(load_valid())
    compiler_map_snapshot = copy.deepcopy(compiled.source_map)
    result = render_codex_skill(compiled, tmp_path)
    execution = compiled.final_execution_ir

    assert result.source_map is not compiled.source_map
    for key, pointers in compiler_map_snapshot.items():
        assert result.source_map[key] == pointers
        assert result.source_map[key] is not compiled.source_map[key]

    expected = {
        "SKILL.md#identity": ["/identity"],
        "SKILL.md#identity/name": ["/identity/name"],
        "SKILL.md#identity/description": ["/identity/description"],
        "SKILL.md#purpose": ["/purpose/outcome"],
        "SKILL.md#interface": ["/interface"],
        "SKILL.md#authority": ["/authority"],
        "SKILL.md#capabilities": ["/capabilities"],
        "agents/openai.yaml#display_name": ["/identity/name"],
        "agents/openai.yaml#short_description": ["/identity/description"],
        "agents/openai.yaml#default_prompt": [
            "/identity/id",
            "/purpose/outcome",
        ],
    }
    for category in ("inputs", "outputs"):
        for index, _ in enumerate(execution["interface"][category]):
            expected[f"SKILL.md#interface/{category}/{index}"] = [
                f"/interface/{category}/{index}"
            ]
    for category in ("allowed", "approval_required", "forbidden"):
        for index, _ in enumerate(execution["authority"][category]):
            expected[f"SKILL.md#authority/{category}/{index}"] = [
                f"/authority/{category}/{index}"
            ]
    for category in ("required", "optional"):
        for index, _ in enumerate(execution["capabilities"][category]):
            expected[f"SKILL.md#capabilities/{category}/{index}"] = [
                f"/capabilities/{category}/{index}"
            ]

    for loop_index, loop in enumerate(execution["loops"]):
        loop_path = f"/loops/{loop_index}"
        expected[f"SKILL.md#loops/{loop_index}/id"] = [f"{loop_path}/id"]
        for node_index, node in enumerate(loop["nodes"]):
            for field in node:
                expected[
                    f"SKILL.md#loops/{loop_index}/nodes/{node_index}/{field}"
                ] = [f"{loop_path}/nodes/{node_index}/{field}"]
        for terminal_name in loop["terminal_mapping"]:
            expected[
                f"SKILL.md#loops/{loop_index}/terminal_mapping/{terminal_name}"
            ] = [f"{loop_path}/terminal_mapping/{terminal_name}"]
        for invariant_index, _ in enumerate(loop["invariants"]):
            expected[
                f"SKILL.md#loops/{loop_index}/invariants/{invariant_index}"
            ] = [f"{loop_path}/invariants/{invariant_index}"]

    for key, pointers in expected.items():
        assert result.source_map[key] == pointers
    assert result.source_map["SKILL.md#workflow"] == [
        "/loops/0/id",
        "/loops/0/entrypoint",
        "/loops/0/nodes",
        "/loops/0/terminal_mapping",
        "/loops/0/invariants",
    ]
    assert result.source_map["SKILL.md#invariants"] == [
        "/loops/0/invariants"
    ]
    assert result.source_map["SKILL.md#stop-rule"] == [
        "/loops/0/terminal_mapping"
    ]


def test_adapter_is_deterministic_for_recursive_object_key_reordering(
    tmp_path: Path,
) -> None:
    definition = load_valid()
    reordered = reverse_mapping_order(definition)

    first = render_codex_skill(compile_definition(definition), tmp_path / "first")
    second = render_codex_skill(
        compile_definition(reordered), tmp_path / "second"
    )

    assert file_snapshot(first.skill_dir) == file_snapshot(second.skill_dir)
    assert first.artifact_digest == second.artifact_digest
    skill_text = (first.skill_dir / "SKILL.md").read_text(encoding="utf-8")
    terminal_positions = [
        skill_text.index(f"**{name}:**")
        for name in sorted(definition["loops"][0]["terminal_states"])
    ]
    assert terminal_positions == sorted(terminal_positions)


def test_directory_digest_uses_sorted_posix_paths_and_file_bytes(
    tmp_path: Path,
) -> None:
    compiled = compile_definition(load_valid())
    result = render_codex_skill(compiled, tmp_path)

    assert result.artifact_digest == expected_directory_digest(result.skill_dir)
    assert directory_digest(result.skill_dir) == result.artifact_digest


def test_directory_digest_length_prefixes_paths_and_content(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    (first / "a").write_bytes(b"\0b\0")
    (second / "a").write_bytes(b"")
    (second / "b").write_bytes(b"")

    assert nul_delimited_directory_digest(first) == (
        nul_delimited_directory_digest(second)
    )
    assert directory_digest(first) != directory_digest(second)


def test_openai_yaml_contains_only_deterministic_interface_values(
    tmp_path: Path,
) -> None:
    compiled = compile_definition(load_valid())
    execution = compiled.final_execution_ir
    result = render_codex_skill(compiled, tmp_path)

    openai_yaml = (result.skill_dir / "agents" / "openai.yaml").read_text(
        encoding="utf-8"
    )
    expected_prompt = (
        f"Use ${execution['identity']['id']} to "
        f"{execution['purpose']['outcome']}."
    )
    assert openai_yaml.splitlines() == [
        "interface:",
        "  display_name: "
        + json.dumps(execution["identity"]["name"], ensure_ascii=False),
        "  short_description: "
        + json.dumps(
            execution["identity"]["description"][:64], ensure_ascii=False
        ),
        "  default_prompt: " + json.dumps(expected_prompt, ensure_ascii=False),
    ]


def test_long_identity_description_maps_short_description_to_description(
    tmp_path: Path,
) -> None:
    definition = load_valid()
    definition["behavior_contract"]["identity"]["description"] = (
        "A sufficiently long identity description for the generated skill."
    )

    result = render_codex_skill(
        compile_definition(definition), tmp_path / "long-description"
    )

    assert result.source_map["agents/openai.yaml#short_description"] == [
        "/identity/description",
    ]
