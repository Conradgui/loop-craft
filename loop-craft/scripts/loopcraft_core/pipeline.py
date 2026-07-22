from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import tempfile
from typing import Any

from .adapters.codex_skill import directory_digest, render_codex_skill
from .canonical import sha256_digest
from .compiler import compile_definition
from .evidence.package import package_evidence
from .validation import validate_definition


@dataclass(frozen=True)
class BuildResult:
    output_root: Path
    artifact_dir: Path
    evidence_dir: Path
    manifest: dict[str, Any]


def build_definition(definition_path: Path, output_root: Path) -> BuildResult:
    definition = json.loads(definition_path.read_text(encoding="utf-8"))
    validate_definition(definition)
    compiled = compile_definition(definition)

    if output_root.exists() or output_root.is_symlink():
        raise FileExistsError(f"Output already exists: {output_root}")
    output_root.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        dir=output_root.parent,
        prefix=f".{output_root.name}.",
    ) as temporary:
        staging_root = Path(temporary) / "output"
        artifact = render_codex_skill(compiled, staging_root / "artifact")
        evidence = package_evidence(
            definition=definition,
            compiled=compiled,
            artifact=artifact,
            evidence_dir=staging_root / "evidence",
        )
        staging_root.replace(output_root)

    return BuildResult(
        output_root,
        output_root / "artifact" / artifact.skill_dir.name,
        output_root / "evidence",
        evidence.manifest,
    )


def verify_build(output_root: Path) -> dict[str, str]:
    if output_root.is_symlink():
        raise ValueError("build output must not be a symlink")
    if not output_root.is_dir():
        raise ValueError("build output must be a directory")

    evidence_root = output_root / "evidence"
    if evidence_root.is_symlink():
        raise ValueError("evidence directory must not be a symlink")
    if not evidence_root.is_dir():
        raise ValueError("evidence directory is missing")

    expected_evidence_files = {
        "accepted-definition.json",
        "final-execution-ir.json",
        "source-map.json",
        "validation-report.json",
        "build-manifest.json",
    }
    evidence_entries = list(evidence_root.iterdir())
    if any(path.is_symlink() for path in evidence_entries):
        raise ValueError("evidence files must not be symlinks")
    if (
        {path.name for path in evidence_entries} != expected_evidence_files
        or any(not path.is_file() for path in evidence_entries)
    ):
        raise ValueError(
            "evidence directory must contain exactly the five required files"
        )

    manifest_path = evidence_root / "build-manifest.json"
    if manifest_path.is_symlink():
        raise ValueError("build manifest must not be a symlink")

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        accepted_definition = json.loads(
            (evidence_root / "accepted-definition.json").read_text(
                encoding="utf-8"
            )
        )
        execution_ir = json.loads(
            (evidence_root / "final-execution-ir.json").read_text(
                encoding="utf-8"
            )
        )
        json.loads(
            (evidence_root / "source-map.json").read_text(encoding="utf-8")
        )
        json.loads(
            (evidence_root / "validation-report.json").read_text(
                encoding="utf-8"
            )
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("evidence JSON is unavailable or invalid") from exc

    if not isinstance(manifest, dict):
        raise ValueError("evidence manifest must be an object")
    if not isinstance(accepted_definition, dict) or not isinstance(
        execution_ir, dict
    ):
        raise ValueError("evidence JSON contracts must be objects")

    required_manifest_fields = {
        "definition_digest",
        "semantic_ir_digest",
        "execution_ir_digest",
        "artifact_digest",
    }
    if not required_manifest_fields.issubset(manifest):
        raise ValueError("evidence manifest is missing digest contracts")
    try:
        semantic_payload = {
            "schema_version": accepted_definition["schema_version"],
            "profile": accepted_definition["profile"],
            "behavior_contract": accepted_definition["behavior_contract"],
            "loops": accepted_definition["loops"],
        }
    except KeyError as exc:
        raise ValueError("evidence accepted definition is incomplete") from exc
    if sha256_digest(accepted_definition) != manifest["definition_digest"]:
        raise ValueError("evidence definition digest does not match manifest")
    if sha256_digest(semantic_payload) != manifest["semantic_ir_digest"]:
        raise ValueError("evidence semantic digest does not match manifest")
    if sha256_digest(execution_ir) != manifest["execution_ir_digest"]:
        raise ValueError("evidence execution IR digest does not match manifest")
    if execution_ir.get("definition_digest") != manifest["definition_digest"]:
        raise ValueError(
            "evidence execution IR definition does not match manifest"
        )

    artifact_root = output_root / "artifact"
    if artifact_root.is_symlink():
        raise ValueError("artifact root must not be a symlink")
    if not artifact_root.is_dir():
        raise ValueError("artifact root must be a directory")

    artifact_entries = list(artifact_root.iterdir())
    if any(path.is_symlink() for path in artifact_entries):
        raise ValueError("artifact root must not contain symlinks")

    artifact_dirs = [path for path in artifact_entries if path.is_dir()]
    if len(artifact_entries) != 1 or len(artifact_dirs) != 1:
        raise ValueError("artifact root must contain exactly one artifact directory")
    if any(
        path.is_dir() and not any(path.iterdir())
        for path in artifact_dirs[0].rglob("*")
    ):
        raise ValueError("artifact directory must not contain empty directories")

    expected_digest = manifest["artifact_digest"]
    actual_digest = directory_digest(artifact_dirs[0])
    return {
        "status": "clean" if expected_digest == actual_digest else "drifted",
        "expected_artifact_digest": expected_digest,
        "actual_artifact_digest": actual_digest,
    }
