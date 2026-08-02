from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..canonical import sha256_digest
from ..compiler import CompileResult
from .artifact import ArtifactResult
from .source_skill import directory_digest


ADAPTER_NAME = "compact-prompt"
ADAPTER_VERSION = "0.1.0"
CONFORMANCE = "runtime_delegated"
SUPPORTED_EXECUTION_FIELDS = {
    "schema_version",
    "compiler_version",
    "input_profile",
    "definition_digest",
    "identity",
    "purpose",
    "applicability",
    "interface",
    "authority",
    "capabilities",
    "workflow",
    "loops",
}


def _literal(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def calculate_compatibility_report(
    execution: dict[str, Any],
) -> dict[str, Any]:
    capabilities = execution["capabilities"]
    return {
        "schema_version": "compact-prompt-compatibility-v0.1",
        "platform": "presentation",
        "overall": "emulated",
        "required": [
            {"capability": capability, "status": "emulated"}
            for capability in capabilities["required"]
        ],
        "optional": [
            {"capability": capability, "status": "emulated"}
            for capability in capabilities["optional"]
        ],
        "limitations": [
            "Tools, state, and execution must be supplied by the receiving Agent."
        ],
    }


def validate_compatibility_contract(
    execution: dict[str, Any],
    compatibility_report: Any,
    conformance: Any,
) -> None:
    if conformance != CONFORMANCE:
        raise ValueError("compact Prompt conformance contract is invalid")
    if compatibility_report != calculate_compatibility_report(execution):
        raise ValueError("compact Prompt compatibility report is invalid")


def _render_prompt(execution: dict[str, Any]) -> str:
    applicability = execution["applicability"]
    interface = execution["interface"]
    authority = execution["authority"]
    capabilities = execution["capabilities"]
    clauses = [
        "Use when " + _literal(applicability["use_when"]),
        "Do not use when " + _literal(applicability["do_not_use_when"]),
        "Goal: " + execution["purpose"]["outcome"],
        "Inputs: " + _literal(interface["inputs"]),
        "Outputs: " + _literal(interface["outputs"]),
        "Allowed actions: " + _literal(authority["allowed"]),
        "Ask for approval before: "
        + _literal(authority["approval_required"]),
        "Forbidden actions: " + _literal(authority["forbidden"]),
        "Required Agent capabilities: "
        + _literal(capabilities["required"]),
        "Optional Agent capabilities: "
        + _literal(capabilities["optional"]),
    ]

    workflow = execution.get("workflow")
    if workflow is not None:
        clauses.extend(
            [
                "Steps: " + _literal(workflow["steps"]),
                "Success evidence: "
                + _literal(workflow["success_evidence"]),
                "Failure or stop: "
                + _literal(workflow["failure_or_stop"]),
            ]
        )

    for loop in execution["loops"]:
        cycle = [
            {"phase": node["id"], "instruction": node["instruction"]}
            for node in loop["nodes"]
        ]
        clauses.extend(
            [
                f"Loop {loop['id']}: " + _literal(cycle),
                "Terminal conditions: "
                + _literal(loop["terminal_mapping"]),
                "Invariants: " + _literal(loop["invariants"]),
            ]
        )

    clauses.append(
        "The receiving Agent must supply the named tools, state, and execution environment."
    )
    return "; ".join(clauses) + "."


def _prompt_source_map(
    compiled: CompileResult,
) -> dict[str, list[str]]:
    summary_sources = [
        *compiled.source_map["/identity"],
        *compiled.source_map["/purpose"],
    ]
    prompt_sources = sorted(
        {
            pointer
            for source_pointers in compiled.source_map.values()
            for pointer in source_pointers
        }
    )
    return {
        "PROMPT.md#summary": list(dict.fromkeys(summary_sources)),
        "PROMPT.md#prompt": prompt_sources,
    }


def render_compact_prompt(
    compiled: CompileResult,
    artifact_root: Path,
) -> ArtifactResult:
    execution = compiled.final_execution_ir
    unknown = set(execution) - SUPPORTED_EXECUTION_FIELDS
    if unknown:
        raise ValueError(
            "unsupported Final Execution IR field: "
            + ", ".join(sorted(unknown))
        )

    identity = execution["identity"]
    artifact_dir = artifact_root / identity["id"]
    artifact_dir.mkdir(parents=True, exist_ok=False)
    prompt = _render_prompt(execution)
    text = "\n".join(
        [
            f"# {identity['name']}",
            "",
            identity["description"],
            "",
            "Prompt:",
            f"> {prompt}",
            "",
        ]
    )
    (artifact_dir / "PROMPT.md").write_text(
        text,
        encoding="utf-8",
        newline="\n",
    )
    compatibility_report = calculate_compatibility_report(execution)
    return ArtifactResult(
        artifact_dir=artifact_dir,
        artifact_digest=directory_digest(artifact_dir),
        source_map=_prompt_source_map(compiled),
        adapter_name=ADAPTER_NAME,
        adapter_version=ADAPTER_VERSION,
        profile_digest=sha256_digest(
            {"platform": "presentation", "profile_version": "0.1.0"}
        ),
        compatibility_report=compatibility_report,
        conformance=CONFORMANCE,
    )
