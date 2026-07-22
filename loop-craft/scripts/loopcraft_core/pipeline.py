from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import tempfile
from typing import Any

from .adapters.codex_skill import (
    directory_digest,
    render_codex_skill,
    validate_compatibility_contract,
)
from .adapters.source_skill import (
    is_link_or_junction,
    load_reviewed_manifest,
    validate_source_manifest,
)
from .canonical import sha256_digest
from .compiler import compile_definition
from .evidence.entry import load_entry_evidence, validate_entry_evidence
from .evidence.package import package_evidence
from .validation import validate_definition


DIGEST_CONTRACT = re.compile(r"sha256:[0-9a-f]{64}")


@dataclass(frozen=True)
class BuildResult:
    output_root: Path
    artifact_dir: Path
    evidence_dir: Path
    manifest: dict[str, Any]


def _ensure_source_output_separate(
    source_skill_dir: Path,
    output_root: Path,
) -> None:
    source = source_skill_dir.resolve()
    output = output_root.resolve()
    if source == output or source in output.parents or output in source.parents:
        raise ValueError("source Skill and build output must not overlap")


def build_definition(
    definition_path: Path,
    output_root: Path,
    *,
    source_skill_dir: Path | None = None,
    package_manifest_path: Path | None = None,
    entry_evidence_path: Path | None = None,
) -> BuildResult:
    if (source_skill_dir is None) != (package_manifest_path is None):
        raise ValueError(
            "source Skill and package manifest must be provided together"
        )
    definition = json.loads(definition_path.read_text(encoding="utf-8"))
    validate_definition(definition)
    compiled = compile_definition(definition)

    entry_evidence: dict[str, Any] | None = None
    if entry_evidence_path is not None:
        entry_evidence = load_entry_evidence(entry_evidence_path, definition)

    source_manifest: dict[str, Any] | None = None
    if source_skill_dir is not None and package_manifest_path is not None:
        if definition["profile"] != "skill-package-v0.1" or len(
            definition["loops"]
        ) != 1:
            raise ValueError(
                "source Skill builds require skill-package-v0.1 with exactly one Loop"
            )
        _ensure_source_output_separate(source_skill_dir, output_root)
        source_manifest = load_reviewed_manifest(
            source_skill_dir,
            package_manifest_path,
        )

    if output_root.exists() or is_link_or_junction(output_root):
        raise FileExistsError(f"Output already exists: {output_root}")
    output_root.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        dir=output_root.parent,
        prefix=f".{output_root.name}.",
    ) as temporary:
        staging_root = Path(temporary) / "output"
        artifact = render_codex_skill(
            compiled,
            staging_root / "artifact",
            source_skill_dir=source_skill_dir,
            source_manifest=source_manifest,
        )
        evidence = package_evidence(
            definition=definition,
            compiled=compiled,
            artifact=artifact,
            evidence_dir=staging_root / "evidence",
            source_manifest=source_manifest,
            entry_evidence=entry_evidence,
        )
        staging_root.replace(output_root)

    return BuildResult(
        output_root,
        output_root / "artifact" / artifact.skill_dir.name,
        output_root / "evidence",
        evidence.manifest,
    )


def verify_build(output_root: Path) -> dict[str, str]:
    if is_link_or_junction(output_root):
        raise ValueError("build output must not be a link or junction")
    if not output_root.is_dir():
        raise ValueError("build output must be a directory")

    evidence_root = output_root / "evidence"
    if is_link_or_junction(evidence_root):
        raise ValueError("evidence directory must not be a link or junction")
    if not evidence_root.is_dir():
        raise ValueError("evidence directory is missing")

    base_evidence_files = {
        "accepted-definition.json",
        "final-execution-ir.json",
        "source-map.json",
        "validation-report.json",
        "build-manifest.json",
    }
    evidence_entries = list(evidence_root.iterdir())
    if any(is_link_or_junction(path) for path in evidence_entries):
        raise ValueError("evidence files must not be links or junctions")
    if any(not path.is_file() for path in evidence_entries):
        raise ValueError("evidence directory may contain only regular files")

    manifest_path = evidence_root / "build-manifest.json"
    if is_link_or_junction(manifest_path):
        raise ValueError("build manifest must not be a link or junction")

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
        source_map = json.loads(
            (evidence_root / "source-map.json").read_text(encoding="utf-8")
        )
        validation_report = json.loads(
            (evidence_root / "validation-report.json").read_text(
                encoding="utf-8"
            )
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("evidence JSON is unavailable or invalid") from exc

    if not isinstance(manifest, dict):
        raise ValueError("evidence manifest must be an object")
    if "compatibility_report" not in manifest or "conformance" not in manifest:
        raise ValueError("evidence manifest is missing adapter contracts")
    source_binding_fields = {
        "source_package_manifest_digest",
        "source_skill_digest",
    }
    entry_binding_fields = {"entry_evidence_digest", "entry_type"}
    binding_specs = (
        (
            "source package",
            source_binding_fields,
            "source-package-manifest.json",
        ),
        (
            "entry evidence",
            entry_binding_fields,
            "entry-evidence.json",
        ),
    )
    expected_evidence_files = set(base_evidence_files)
    bound_contracts: set[str] = set()
    for label, fields, filename in binding_specs:
        present = fields & set(manifest)
        if present and present != fields:
            raise ValueError(f"evidence {label} binding is incomplete")
        if present:
            bound_contracts.add(label)
            expected_evidence_files.add(filename)
    if {path.name for path in evidence_entries} != expected_evidence_files:
        raise ValueError(
            "evidence directory files do not match manifest bindings"
        )
    bound_source = "source package" in bound_contracts
    bound_entry = "entry evidence" in bound_contracts
    if not isinstance(accepted_definition, dict) or not isinstance(
        execution_ir, dict
    ):
        raise ValueError("evidence JSON contracts must be objects")
    if (
        not isinstance(source_map, dict)
        or not source_map
        or any(
            not isinstance(artifact_path, str)
            or not artifact_path
            or not isinstance(source_pointers, list)
            or not source_pointers
            or any(not isinstance(pointer, str) for pointer in source_pointers)
            for artifact_path, source_pointers in source_map.items()
        )
    ):
        raise ValueError("evidence source map contract is invalid")
    if not isinstance(validation_report, dict) or (
        validation_report.get("schema_validation") != "passed"
        or validation_report.get("semantic_validation") != "passed"
        or validation_report.get("accepted_definition") is not True
    ):
        raise ValueError("evidence validation report does not record success")

    required_manifest_fields = (
        "definition_digest",
        "semantic_ir_digest",
        "execution_ir_digest",
        "source_map_digest",
        "validation_report_digest",
        "artifact_digest",
    )
    if not set(required_manifest_fields).issubset(manifest):
        raise ValueError("evidence manifest is missing digest contracts")
    for field in required_manifest_fields:
        value = manifest[field]
        if not isinstance(value, str) or DIGEST_CONTRACT.fullmatch(value) is None:
            raise ValueError(f"evidence manifest {field} digest contract is invalid")
    if bound_source:
        for field in source_binding_fields:
            value = manifest[field]
            if (
                not isinstance(value, str)
                or DIGEST_CONTRACT.fullmatch(value) is None
            ):
                raise ValueError(
                    f"evidence manifest {field} digest contract is invalid"
                )
        try:
            source_manifest = json.loads(
                (evidence_root / "source-package-manifest.json").read_text(
                    encoding="utf-8"
                )
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError("evidence source package manifest is invalid") from exc
        validate_source_manifest(source_manifest)
        if sha256_digest(source_manifest) != manifest[
            "source_package_manifest_digest"
        ]:
            raise ValueError(
                "evidence source package manifest digest does not match"
            )
        if (
            source_manifest["source_skill_digest"]
            != manifest["source_skill_digest"]
        ):
            raise ValueError("evidence source Skill digest does not match")
    if bound_entry:
        entry_digest = manifest["entry_evidence_digest"]
        if (
            not isinstance(entry_digest, str)
            or DIGEST_CONTRACT.fullmatch(entry_digest) is None
        ):
            raise ValueError(
                "evidence manifest entry_evidence_digest contract is invalid"
            )
        if manifest["entry_type"] not in {
            "from_scratch",
            "existing_skill",
            "conversation",
        }:
            raise ValueError("evidence manifest entry_type contract is invalid")
        try:
            entry_evidence = json.loads(
                (evidence_root / "entry-evidence.json").read_text(
                    encoding="utf-8"
                )
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError("evidence entry evidence is invalid") from exc
        if not isinstance(entry_evidence, dict):
            raise ValueError("evidence entry evidence must be an object")
        validate_entry_evidence(entry_evidence, accepted_definition)
        if sha256_digest(entry_evidence) != entry_digest:
            raise ValueError("evidence entry evidence digest does not match")
        if entry_evidence["entry_type"] != manifest["entry_type"]:
            raise ValueError("evidence entry type does not match manifest")
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
    if sha256_digest(source_map) != manifest["source_map_digest"]:
        raise ValueError("evidence source map digest does not match manifest")
    if (
        sha256_digest(validation_report)
        != manifest["validation_report_digest"]
    ):
        raise ValueError(
            "evidence validation report digest does not match manifest"
        )
    if execution_ir.get("definition_digest") != manifest["definition_digest"]:
        raise ValueError(
            "evidence execution IR definition does not match manifest"
        )
    validate_compatibility_contract(
        execution_ir,
        manifest["compatibility_report"],
        manifest["conformance"],
    )

    artifact_root = output_root / "artifact"
    if is_link_or_junction(artifact_root):
        raise ValueError("artifact root must not be a link or junction")
    if not artifact_root.is_dir():
        raise ValueError("artifact root must be a directory")

    artifact_entries = list(artifact_root.iterdir())
    if any(is_link_or_junction(path) for path in artifact_entries):
        raise ValueError("artifact root must not contain links or junctions")

    artifact_dirs = [path for path in artifact_entries if path.is_dir()]
    if len(artifact_entries) != 1 or len(artifact_dirs) != 1:
        raise ValueError("artifact root must contain exactly one artifact directory")
    if not any(artifact_dirs[0].iterdir()):
        raise ValueError("artifact directory must not be empty")
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
