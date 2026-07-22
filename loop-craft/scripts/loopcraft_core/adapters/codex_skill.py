from __future__ import annotations

import copy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from ..canonical import canonical_json_bytes
from ..compiler import CompileResult


STOP_RULE = (
    "Stop immediately when any terminal condition is met; the terminal outcome "
    "takes precedence over every node's Next transition."
)


@dataclass(frozen=True)
class SkillArtifact:
    skill_dir: Path
    artifact_digest: str
    source_map: dict[str, list[str]]


def directory_digest(root: Path) -> str:
    if root.is_symlink():
        raise ValueError("artifact directory must not be a symlink")

    entries = list(root.rglob("*"))
    if any(path.is_symlink() for path in entries):
        raise ValueError("artifact directory must not contain symlinks")

    hasher = hashlib.sha256()
    files = sorted(
        (path.relative_to(root).as_posix(), path)
        for path in entries
        if path.is_file()
    )
    for relative_path, path in files:
        path_bytes = relative_path.encode("utf-8")
        content = path.read_bytes()
        hasher.update(len(path_bytes).to_bytes(8, "big"))
        hasher.update(path_bytes)
        hasher.update(len(content).to_bytes(8, "big"))
        hasher.update(content)
    return f"sha256:{hasher.hexdigest()}"


def _clean_trigger(use_when: str) -> str:
    trigger = use_when.strip().rstrip(".")
    prefix = "use when "
    if trigger.casefold().startswith(prefix):
        trigger = trigger[len(prefix) :].lstrip()
    return trigger.replace("<", "").replace(">", "")


def _frontmatter_description(use_when: list[str]) -> str:
    triggers = [_clean_trigger(value) for value in use_when]
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

    fallback = (
        f"Loop Craft Skill for {identity['name'].strip()}: "
        f"{execution['purpose']['outcome'].strip()}"
    )
    return (
        fallback[:64],
        ["/identity/name", "/purpose/outcome"],
    )


def _markdown_literal(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _append_list(lines: list[str], heading: str, values: list[str]) -> None:
    lines.extend([f"### {heading}", ""])
    lines.extend(f"- {_markdown_literal(value)}" for value in values)
    if not values:
        lines.append("- None.")
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
    for loop in loops:
        lines.extend(
            [
                f"### Loop: {loop['id']}",
                "",
                f"Entrypoint: `{loop['entrypoint']}`",
                "",
                "#### Nodes",
                "",
            ]
        )
        for index, node in enumerate(loop["nodes"], start=1):
            lines.extend(
                [
                    f"{index}. **{node['id']}**",
                    "   - Instruction: "
                    + _markdown_literal(node["instruction"]),
                    f"   - Next: `{node['next']}`",
                ]
            )
        lines.extend(["", STOP_RULE, "", "#### Terminal mapping", ""])
        for name in sorted(loop["terminal_mapping"]):
            condition = _markdown_literal(loop["terminal_mapping"][name])
            lines.append(f"- **{name}:** {condition}")
        lines.extend(["", "#### Invariants", ""])
        lines.extend(
            f"- {_markdown_literal(item)}" for item in loop["invariants"]
        )
        lines.append("")

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

    return adapter_map


def render_codex_skill(
    compiled: CompileResult,
    artifact_root: Path,
) -> SkillArtifact:
    execution = compiled.final_execution_ir
    identity = execution["identity"]
    skill_dir = artifact_root / identity["id"]
    references = skill_dir / "references"
    agents = skill_dir / "agents"
    references.mkdir(parents=True, exist_ok=False)
    agents.mkdir(parents=True, exist_ok=False)

    description = _frontmatter_description(
        execution["applicability"]["use_when"]
    )
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
    )
