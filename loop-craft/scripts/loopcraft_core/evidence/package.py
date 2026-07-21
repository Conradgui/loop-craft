from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..adapters.codex_skill import SkillArtifact
from ..canonical import canonical_json_bytes, sha256_digest
from ..compiler import CompileResult


@dataclass(frozen=True)
class EvidenceResult:
    evidence_dir: Path
    manifest: dict[str, Any]


def _write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_json_bytes(value) + b"\n")


def package_evidence(
    *,
    definition: dict[str, Any],
    compiled: CompileResult,
    artifact: SkillArtifact,
    evidence_dir: Path,
) -> EvidenceResult:
    evidence_dir.mkdir(parents=True, exist_ok=False)
    manifest = {
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
        "override_mode": "none",
        "override_digest": None,
        "compiler_version": compiled.final_execution_ir["compiler_version"],
        "adapter": "codex-skill",
        "adapter_version": "0.1.0",
        "profile_digest": sha256_digest(
            {"platform": "codex", "profile_version": "0.1.0"}
        ),
        "artifact_digest": artifact.artifact_digest,
    }
    validation_report = {
        "schema_validation": "passed",
        "semantic_validation": "passed",
        "accepted_definition": True,
    }

    _write_json(evidence_dir / "accepted-definition.json", definition)
    _write_json(
        evidence_dir / "final-execution-ir.json",
        compiled.final_execution_ir,
    )
    _write_json(evidence_dir / "source-map.json", artifact.source_map)
    _write_json(evidence_dir / "validation-report.json", validation_report)
    _write_json(evidence_dir / "build-manifest.json", manifest)
    return EvidenceResult(evidence_dir, manifest)
