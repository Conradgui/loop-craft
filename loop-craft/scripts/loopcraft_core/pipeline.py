from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import tempfile
from typing import Any

from .adapters.codex_skill import directory_digest, render_codex_skill
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
    manifest_path = output_root / "evidence" / "build-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    artifact_root = output_root / "artifact"
    if artifact_root.is_symlink():
        raise ValueError("artifact root must not be a symlink")

    artifact_entries = (
        list(artifact_root.iterdir()) if artifact_root.is_dir() else []
    )
    if any(path.is_symlink() for path in artifact_entries):
        raise ValueError("artifact root must not contain symlinks")

    artifact_dirs = [path for path in artifact_entries if path.is_dir()]
    if len(artifact_entries) != 1 or len(artifact_dirs) != 1:
        raise ValueError("artifact root must contain exactly one artifact directory")

    expected_digest = manifest["artifact_digest"]
    actual_digest = directory_digest(artifact_dirs[0])
    return {
        "status": "clean" if expected_digest == actual_digest else "drifted",
        "expected_artifact_digest": expected_digest,
        "actual_artifact_digest": actual_digest,
    }
