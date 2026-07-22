from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..adapters.codex_skill import SkillArtifact, directory_digest
from ..adapters.source_skill import validate_source_manifest
from ..canonical import canonical_json_bytes, sha256_digest
from ..compiler import CompileResult
from .entry import validate_entry_evidence


@dataclass(frozen=True)
class EvidenceResult:
    evidence_dir: Path
    manifest: dict[str, Any]


def _write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_json_bytes(value) + b"\n")


def _validate_inputs(
    *,
    definition: dict[str, Any],
    compiled: CompileResult,
    artifact: SkillArtifact,
    evidence_dir: Path,
) -> None:
    execution_ir = compiled.final_execution_ir
    if execution_ir.get("definition_digest") != sha256_digest(definition):
        raise ValueError("definition does not match compiled execution IR")

    artifact_dir = artifact.skill_dir.resolve()
    resolved_evidence_dir = evidence_dir.resolve()
    if (
        resolved_evidence_dir == artifact_dir
        or resolved_evidence_dir in artifact_dir.parents
        or artifact_dir in resolved_evidence_dir.parents
    ):
        raise ValueError(
            "evidence directory must be physically separate from artifact"
        )

    execution_ir_path = (
        artifact.skill_dir / "references" / "final-execution-ir.json"
    )
    try:
        artifact_execution_ir = execution_ir_path.read_bytes()
    except OSError as exc:
        raise ValueError(
            "artifact execution IR reference is unavailable"
        ) from exc
    if artifact_execution_ir != canonical_json_bytes(execution_ir) + b"\n":
        raise ValueError(
            "artifact execution IR does not match compiled execution IR"
        )

    current_artifact_digest = directory_digest(artifact.skill_dir)
    if current_artifact_digest != artifact.artifact_digest:
        raise ValueError(
            "artifact digest does not match current artifact contents"
        )


def package_evidence(
    *,
    definition: dict[str, Any],
    compiled: CompileResult,
    artifact: SkillArtifact,
    evidence_dir: Path,
    source_manifest: dict[str, Any] | None = None,
    entry_evidence: dict[str, Any] | None = None,
) -> EvidenceResult:
    _validate_inputs(
        definition=definition,
        compiled=compiled,
        artifact=artifact,
        evidence_dir=evidence_dir,
    )
    if source_manifest is not None:
        validate_source_manifest(source_manifest)
    if entry_evidence is not None:
        validate_entry_evidence(entry_evidence, definition)
    evidence_dir.mkdir(parents=True, exist_ok=False)
    validation_report = {
        "schema_validation": "passed",
        "semantic_validation": "passed",
        "accepted_definition": True,
    }
    manifest: dict[str, Any] = {
        "schema_version": "0.1.0",
        "definition_digest": sha256_digest(definition),
        "semantic_ir_digest": sha256_digest(
            {
                "schema_version": definition["schema_version"],
                "profile": definition["profile"],
                "behavior_contract": definition["behavior_contract"],
                "loops": definition["loops"],
            }
        ),
        "execution_ir_digest": sha256_digest(compiled.final_execution_ir),
        "source_map_digest": sha256_digest(artifact.source_map),
        "validation_report_digest": sha256_digest(validation_report),
        "override_mode": "none",
        "override_digest": None,
        "compiler_version": compiled.final_execution_ir["compiler_version"],
        "adapter": "codex-skill",
        "adapter_version": "0.2.0" if source_manifest is not None else "0.1.0",
        "profile_digest": sha256_digest(
            {"platform": "codex", "profile_version": "0.1.0"}
        ),
        "compatibility_report": artifact.compatibility_report,
        "conformance": artifact.conformance,
        "artifact_digest": artifact.artifact_digest,
    }
    if source_manifest is not None:
        manifest["source_package_manifest_digest"] = sha256_digest(
            source_manifest
        )
        manifest["source_skill_digest"] = source_manifest[
            "source_skill_digest"
        ]
    if entry_evidence is not None:
        manifest["entry_evidence_digest"] = sha256_digest(entry_evidence)
        manifest["entry_type"] = entry_evidence["entry_type"]

    _write_json(evidence_dir / "accepted-definition.json", definition)
    _write_json(
        evidence_dir / "final-execution-ir.json",
        compiled.final_execution_ir,
    )
    _write_json(evidence_dir / "source-map.json", artifact.source_map)
    _write_json(evidence_dir / "validation-report.json", validation_report)
    if source_manifest is not None:
        _write_json(
            evidence_dir / "source-package-manifest.json",
            source_manifest,
        )
    if entry_evidence is not None:
        _write_json(evidence_dir / "entry-evidence.json", entry_evidence)
    _write_json(evidence_dir / "build-manifest.json", manifest)
    return EvidenceResult(evidence_dir, manifest)
