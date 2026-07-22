from __future__ import annotations

import copy
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from ..canonical import canonical_json_bytes
from ..compiler import CompileResult
from .source_skill import (
    directory_digest,
    file_bytes_digest,
    is_link_or_junction,
    source_frontmatter_name,
    validate_source_manifest,
)


STOP_RULE = (
    "Stop immediately when any terminal condition is met; the terminal outcome "
    "takes precedence over every node's Next transition."
)
SUPPORTED_CAPABILITIES = {
    "filesystem.read",
    "filesystem.write",
    "validation.execute",
    "git.diff",
}
CONFORMANCE = "self_contained"


@dataclass(frozen=True)
class SkillArtifact:
    skill_dir: Path
    artifact_digest: str
    source_map: dict[str, list[str]]
    compatibility_report: dict[str, Any]
    conformance: str


def calculate_compatibility_report(
    execution: dict[str, Any],
) -> dict[str, Any]:
    capabilities = execution["capabilities"]
    unsupported_required = [
        capability
        for capability in capabilities["required"]
        if capability not in SUPPORTED_CAPABILITIES
    ]
    if unsupported_required:
        raise ValueError(
            "unsupported required Codex capability: "
            + ", ".join(unsupported_required)
        )

    required = [
        {"capability": capability, "status": "native"}
        for capability in capabilities["required"]
    ]
    optional = [
        {
            "capability": capability,
            "status": (
                "native"
                if capability in SUPPORTED_CAPABILITIES
                else "unsupported"
            ),
        }
        for capability in capabilities["optional"]
    ]
    overall = (
        "degraded"
        if any(item["status"] == "unsupported" for item in optional)
        else "native"
    )
    return {
        "schema_version": "codex-compatibility-v0.1",
        "platform": "codex",
        "overall": overall,
        "required": required,
        "optional": optional,
    }


def validate_compatibility_contract(
    execution: dict[str, Any],
    compatibility_report: Any,
    conformance: Any,
) -> None:
    if conformance != CONFORMANCE:
        raise ValueError("adapter conformance contract is invalid")
    expected = calculate_compatibility_report(execution)
    if compatibility_report != expected:
        raise ValueError("adapter compatibility report is invalid")


def _clean_trigger(use_when: str) -> str:
    trigger = use_when.strip().rstrip(".")
    prefix = "use when "
    if trigger.casefold().startswith(prefix):
        trigger = trigger[len(prefix) :].lstrip()
    return trigger.replace("<", "").replace(">", "").strip()


def _frontmatter_description(use_when: list[str]) -> str:
    triggers = [_clean_trigger(value) for value in use_when]
    if any(not trigger for trigger in triggers):
        raise ValueError("frontmatter trigger is empty after cleaning")
    prefix = "Use when "
    separator = "; "
    description = prefix + separator.join(triggers)
    if len(description) > 1024:
        raise ValueError(
            "frontmatter description exceeds the 1024-character limit"
        )
    return description


def _short_description_projection(
    execution: dict[str, Any],
) -> tuple[str, list[str]]:
    identity = execution["identity"]
    description = identity["description"].strip()
    if len(description) >= 25:
        return description[:64], ["/identity/description"]

    prefix = "Loop Craft Skill for "
    separator = ": "
    name = identity["name"].strip()
    outcome = execution["purpose"]["outcome"].strip()
    content_budget = 64 - len(prefix) - len(separator)
    name_budget = min(len(name), (content_budget + 1) // 2)
    outcome_budget = min(len(outcome), content_budget - name_budget)
    remaining = content_budget - name_budget - outcome_budget
    name_budget += min(remaining, len(name) - name_budget)
    remaining = content_budget - name_budget - outcome_budget
    outcome_budget += min(remaining, len(outcome) - outcome_budget)
    fallback = (
        f"{prefix}{name[:name_budget]}{separator}{outcome[:outcome_budget]}"
    )
    return (
        fallback,
        ["/identity/name", "/purpose/outcome"],
    )


def _markdown_literal(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _append_list(
    lines: list[str],
    heading: str,
    values: list[str],
    *,
    level: int = 3,
) -> None:
    lines.extend([f"{'#' * level} {heading}", ""])
    lines.extend(f"- {_markdown_literal(value)}" for value in values)
    if not values:
        lines.append("- None.")
    lines.append("")


def _append_loop(lines: list[str], loop: dict[str, Any], heading: str) -> None:
    lines.extend(
        [
            f"{heading} Loop: {loop['id']}",
            "",
            f"Entrypoint: `{loop['entrypoint']}`",
            "",
            f"{heading}# Nodes",
            "",
        ]
    )
    for index, node in enumerate(loop["nodes"], start=1):
        lines.extend(
            [
                f"{index}. **{node['id']}**",
                "   - Instruction: " + _markdown_literal(node["instruction"]),
                f"   - Next: `{node['next']}`",
            ]
        )
    lines.extend(["", STOP_RULE, "", f"{heading}# Terminal mapping", ""])
    for name in sorted(loop["terminal_mapping"]):
        condition = _markdown_literal(loop["terminal_mapping"][name])
        lines.append(f"- **{name}:** {condition}")
    lines.extend(["", f"{heading}# Invariants", ""])
    lines.extend(f"- {_markdown_literal(item)}" for item in loop["invariants"])
    lines.append("")


def _skill_body(execution: dict[str, Any]) -> str:
    identity = execution["identity"]
    purpose = execution["purpose"]
    applicability = execution["applicability"]
    interface = execution["interface"]
    authority = execution["authority"]
    capabilities = execution["capabilities"]
    loops = execution["loops"]

    lines = [
        f"# {_markdown_literal(identity['name'])}",
        "",
        _markdown_literal(identity["description"]),
        "",
        "## Purpose",
        "",
        _markdown_literal(purpose["outcome"]),
        "",
        "## Applicability",
        "",
    ]
    _append_list(lines, "Use when", applicability["use_when"])
    _append_list(lines, "Do not use when", applicability["do_not_use_when"])

    lines.extend(["## Interface", ""])
    _append_list(lines, "Inputs", interface["inputs"])
    _append_list(lines, "Outputs", interface["outputs"])

    lines.extend(["## Workflow", ""])
    if "workflow" in execution:
        workflow = execution["workflow"]
        lines.extend(["### Steps", ""])
        lines.extend(
            f"{index}. {_markdown_literal(step)}"
            for index, step in enumerate(workflow["steps"], start=1)
        )
        lines.append("")
        _append_list(lines, "Success evidence", workflow["success_evidence"])
        _append_list(lines, "Failure or stop", workflow["failure_or_stop"])

    for loop in loops:
        _append_loop(lines, loop, "###")

    lines.extend(["## Authority", ""])
    _append_list(lines, "Allowed", authority["allowed"])
    _append_list(lines, "Approval required", authority["approval_required"])
    _append_list(lines, "Forbidden", authority["forbidden"])

    lines.extend(["## Capabilities", ""])
    _append_list(lines, "Required", capabilities["required"])
    _append_list(lines, "Optional", capabilities["optional"])
    lines.extend(
        [
            "Read `references/final-execution-ir.json` for exact machine-readable execution details.",
            "",
        ]
    )
    return "\n".join(lines)


def _adapter_source_map(compiled: CompileResult) -> dict[str, list[str]]:
    execution = compiled.final_execution_ir
    applicability = execution["applicability"]
    adapter_map = copy.deepcopy(compiled.source_map)
    adapter_map.update(
        {
            "SKILL.md#name": ["/identity/id"],
            "SKILL.md#description": [
                f"/applicability/use_when/{index}"
                for index, _ in enumerate(applicability["use_when"])
            ],
            "SKILL.md#identity": ["/identity"],
            "SKILL.md#identity/name": ["/identity/name"],
            "SKILL.md#identity/description": ["/identity/description"],
            "SKILL.md#purpose": ["/purpose/outcome"],
            "SKILL.md#applicability": [
                *[
                    f"/applicability/use_when/{index}"
                    for index, _ in enumerate(applicability["use_when"])
                ],
                *[
                    f"/applicability/do_not_use_when/{index}"
                    for index, _ in enumerate(applicability["do_not_use_when"])
                ],
            ],
            "SKILL.md#interface": ["/interface"],
            "SKILL.md#workflow": [
                f"/loops/{index}/{field}"
                for index, _ in enumerate(execution["loops"])
                for field in (
                    "id",
                    "entrypoint",
                    "nodes",
                    "terminal_mapping",
                    "invariants",
                )
            ],
            "SKILL.md#authority": ["/authority"],
            "SKILL.md#capabilities": ["/capabilities"],
            "SKILL.md#invariants": [
                f"/loops/{index}/invariants"
                for index, _ in enumerate(execution["loops"])
            ],
            "SKILL.md#stop-rule": [
                f"/loops/{index}/terminal_mapping"
                for index, _ in enumerate(execution["loops"])
            ],
            "agents/openai.yaml#display_name": ["/identity/name"],
            "agents/openai.yaml#short_description": (
                _short_description_projection(execution)[1]
            ),
            "agents/openai.yaml#default_prompt": [
                "/identity/id",
                "/purpose/outcome",
            ],
            "references/final-execution-ir.json": [""],
        }
    )

    for category in ("use_when", "do_not_use_when"):
        for index, _ in enumerate(applicability[category]):
            artifact_path = f"SKILL.md#applicability/{category}/{index}"
            adapter_map[artifact_path] = [
                f"/applicability/{category}/{index}"
            ]

    for category in ("inputs", "outputs"):
        for index, _ in enumerate(execution["interface"][category]):
            artifact_path = f"SKILL.md#interface/{category}/{index}"
            adapter_map[artifact_path] = [f"/interface/{category}/{index}"]

    for category in ("allowed", "approval_required", "forbidden"):
        for index, _ in enumerate(execution["authority"][category]):
            artifact_path = f"SKILL.md#authority/{category}/{index}"
            adapter_map[artifact_path] = [f"/authority/{category}/{index}"]

    for category in ("required", "optional"):
        for index, _ in enumerate(execution["capabilities"][category]):
            artifact_path = f"SKILL.md#capabilities/{category}/{index}"
            adapter_map[artifact_path] = [
                f"/capabilities/{category}/{index}"
            ]

    for loop_index, loop in enumerate(execution["loops"]):
        loop_path = f"/loops/{loop_index}"
        adapter_map[f"SKILL.md#loops/{loop_index}/id"] = [f"{loop_path}/id"]
        adapter_map[f"SKILL.md#loops/{loop_index}/entrypoint"] = [
            f"{loop_path}/entrypoint"
        ]
        for node_index, _ in enumerate(loop["nodes"]):
            for field in ("id", "instruction", "next"):
                artifact_path = (
                    f"SKILL.md#loops/{loop_index}/nodes/{node_index}/{field}"
                )
                adapter_map[artifact_path] = [
                    f"{loop_path}/nodes/{node_index}/{field}"
                ]
        for name in sorted(loop["terminal_mapping"]):
            artifact_path = (
                f"SKILL.md#loops/{loop_index}/terminal_mapping/{name}"
            )
            adapter_map[artifact_path] = [
                f"{loop_path}/terminal_mapping/{name}"
            ]
        for invariant_index, _ in enumerate(loop["invariants"]):
            artifact_path = (
                f"SKILL.md#loops/{loop_index}/invariants/{invariant_index}"
            )
            adapter_map[artifact_path] = [
                f"{loop_path}/invariants/{invariant_index}"
            ]

    workflow_sources = adapter_map["SKILL.md#workflow"]
    if "workflow" in execution:
        for category in ("steps", "success_evidence", "failure_or_stop"):
            for index, _ in enumerate(execution["workflow"][category]):
                pointer = f"/workflow/{category}/{index}"
                workflow_sources.append(pointer)
                adapter_map[f"SKILL.md#workflow/{category}/{index}"] = [
                    pointer
                ]
    for empty_when_no_loop in ("SKILL.md#invariants", "SKILL.md#stop-rule"):
        if not adapter_map[empty_when_no_loop]:
            adapter_map.pop(empty_when_no_loop)

    return adapter_map


def _source_adapter_map(
    compiled: CompileResult,
    source_manifest: dict[str, Any],
) -> dict[str, list[str]]:
    source_map = copy.deepcopy(compiled.source_map)
    for index, entry in enumerate(source_manifest["entries"]):
        source_pointer = f"/source-package-manifest/entries/{index}"
        if entry["action"] == "preserve":
            source_map[f"{entry['path']}#source"] = [source_pointer]
        elif entry["action"] == "overlay":
            source_map["SKILL.md#source"] = [source_pointer]
        else:
            source_map[entry["path"]] = [""]
    source_map["references/final-execution-ir.json"] = [""]

    loop = compiled.final_execution_ir["loops"][0]
    loop_path = "/loops/0"
    source_map["SKILL.md#feedback-loop"] = [
        f"{loop_path}/{field}"
        for field in (
            "id",
            "entrypoint",
            "nodes",
            "terminal_mapping",
            "invariants",
        )
    ]
    source_map["SKILL.md#feedback-loop/purpose"] = ["/purpose/outcome"]
    source_map["SKILL.md#feedback-loop/interface"] = ["/interface"]
    for category in ("inputs", "outputs"):
        for index, _ in enumerate(compiled.final_execution_ir["interface"][category]):
            source_map[
                f"SKILL.md#feedback-loop/interface/{category}/{index}"
            ] = [f"/interface/{category}/{index}"]
    source_map["SKILL.md#feedback-loop/authority"] = ["/authority"]
    for category in ("allowed", "approval_required", "forbidden"):
        for index, _ in enumerate(compiled.final_execution_ir["authority"][category]):
            source_map[
                f"SKILL.md#feedback-loop/authority/{category}/{index}"
            ] = [f"/authority/{category}/{index}"]
    source_map["SKILL.md#feedback-loop/capabilities"] = ["/capabilities"]
    for category in ("required", "optional"):
        for index, _ in enumerate(compiled.final_execution_ir["capabilities"][category]):
            source_map[
                f"SKILL.md#feedback-loop/capabilities/{category}/{index}"
            ] = [f"/capabilities/{category}/{index}"]
    for node_index, node in enumerate(loop["nodes"]):
        for field in node:
            source_map[
                f"SKILL.md#feedback-loop/nodes/{node_index}/{field}"
            ] = [f"{loop_path}/nodes/{node_index}/{field}"]
    source_map["SKILL.md#feedback-loop/terminal-mapping"] = [
        f"{loop_path}/terminal_mapping"
    ]
    source_map["SKILL.md#feedback-loop/invariants"] = [
        f"{loop_path}/invariants"
    ]
    source_map["SKILL.md#feedback-loop/stop-rule"] = [
        f"{loop_path}/terminal_mapping"
    ]
    return source_map


def _render_source_skill(
    compiled: CompileResult,
    artifact_root: Path,
    source_skill_dir: Path,
    source_manifest: dict[str, Any],
    compatibility_report: dict[str, Any],
) -> SkillArtifact:
    validate_source_manifest(source_manifest)
    execution = compiled.final_execution_ir
    identity_id = execution["identity"]["id"]
    if source_skill_dir.name != identity_id:
        raise ValueError("source Skill directory name must match definition identity.id")
    if source_frontmatter_name(source_skill_dir / "SKILL.md") != identity_id:
        raise ValueError("source SKILL.md frontmatter name must match definition identity.id")

    skill_dir = artifact_root / identity_id
    skill_dir.mkdir(parents=True, exist_ok=False)
    for entry in source_manifest["entries"]:
        if entry["action"] == "generated":
            continue
        source_path = source_skill_dir / Path(entry["path"])
        if is_link_or_junction(source_path):
            raise ValueError(f"source package entry became a link: {entry['path']}")
        if not source_path.is_file():
            raise ValueError(f"source package entry is not a regular file: {entry['path']}")
        source_bytes = source_path.read_bytes()
        if file_bytes_digest(source_bytes) != entry["digest"]:
            raise ValueError(f"source package entry changed after review: {entry['path']}")
        target_path = skill_dir / Path(entry["path"])
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(source_bytes)

    loop_lines = [
        "## Feedback Loop",
        "",
        "### Purpose",
        "",
        _markdown_literal(execution["purpose"]["outcome"]),
        "",
        "### Interface",
        "",
    ]
    _append_list(loop_lines, "Inputs", execution["interface"]["inputs"], level=4)
    _append_list(loop_lines, "Outputs", execution["interface"]["outputs"], level=4)
    loop_lines.extend(["### Authority", ""])
    _append_list(loop_lines, "Allowed", execution["authority"]["allowed"], level=4)
    _append_list(
        loop_lines,
        "Approval required",
        execution["authority"]["approval_required"],
        level=4,
    )
    _append_list(loop_lines, "Forbidden", execution["authority"]["forbidden"], level=4)
    loop_lines.extend(["### Capabilities", ""])
    _append_list(
        loop_lines,
        "Required",
        execution["capabilities"]["required"],
        level=4,
    )
    _append_list(
        loop_lines,
        "Optional",
        execution["capabilities"]["optional"],
        level=4,
    )
    _append_loop(loop_lines, execution["loops"][0], "###")
    source_skill_bytes = (skill_dir / "SKILL.md").read_bytes()
    separator = b"\n" if source_skill_bytes.endswith(b"\n") else b"\n\n"
    skill_bytes = (
        source_skill_bytes
        + separator
        + "\n".join(loop_lines).encode("utf-8")
    )
    if len(skill_bytes.decode("utf-8").splitlines()) > 500:
        raise ValueError("generated SKILL.md exceeds the 500-line limit")
    (skill_dir / "SKILL.md").write_bytes(skill_bytes)

    execution_ir_path = skill_dir / "references" / "final-execution-ir.json"
    execution_ir_path.parent.mkdir(parents=True, exist_ok=True)
    execution_ir_path.write_bytes(canonical_json_bytes(execution) + b"\n")
    return SkillArtifact(
        skill_dir=skill_dir,
        artifact_digest=directory_digest(skill_dir),
        source_map=_source_adapter_map(compiled, source_manifest),
        compatibility_report=compatibility_report,
        conformance=CONFORMANCE,
    )
def render_codex_skill(
    compiled: CompileResult,
    artifact_root: Path,
    *,
    source_skill_dir: Path | None = None,
    source_manifest: dict[str, Any] | None = None,
) -> SkillArtifact:
    compatibility_report = calculate_compatibility_report(
        compiled.final_execution_ir
    )
    if (source_skill_dir is None) != (source_manifest is None):
        raise ValueError(
            "source Skill and source package manifest must be provided together"
        )
    if source_skill_dir is not None and source_manifest is not None:
        return _render_source_skill(
            compiled,
            artifact_root,
            source_skill_dir,
            source_manifest,
            compatibility_report,
        )

    execution = compiled.final_execution_ir
    identity = execution["identity"]
    skill_dir = artifact_root / identity["id"]
    references = skill_dir / "references"
    agents = skill_dir / "agents"
    description = _frontmatter_description(
        execution["applicability"]["use_when"]
    )
    references.mkdir(parents=True, exist_ok=False)
    agents.mkdir(parents=True, exist_ok=False)

    skill_text = "\n".join(
        [
            "---",
            f"name: {identity['id']}",
            "description: " + json.dumps(description, ensure_ascii=False),
            "---",
            "",
            _skill_body(execution),
        ]
    )
    if len(skill_text.splitlines()) > 500:
        raise ValueError("generated SKILL.md exceeds the 500-line limit")
    (skill_dir / "SKILL.md").write_bytes(skill_text.encode("utf-8"))

    default_prompt = (
        f"Use ${identity['id']} to {execution['purpose']['outcome']}."
    )
    openai_yaml = "\n".join(
        [
            "interface:",
            "  display_name: "
            + json.dumps(identity["name"], ensure_ascii=False),
            "  short_description: "
            + json.dumps(
                _short_description_projection(execution)[0],
                ensure_ascii=False,
            ),
            "  default_prompt: "
            + json.dumps(default_prompt, ensure_ascii=False),
            "",
        ]
    )
    (agents / "openai.yaml").write_bytes(openai_yaml.encode("utf-8"))
    (references / "final-execution-ir.json").write_bytes(
        canonical_json_bytes(execution) + b"\n"
    )

    return SkillArtifact(
        skill_dir=skill_dir,
        artifact_digest=directory_digest(skill_dir),
        source_map=_adapter_source_map(compiled),
        compatibility_report=compatibility_report,
        conformance=CONFORMANCE,
    )
