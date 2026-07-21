import json
from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any

import pytest

from loopcraft_core.adapters.codex_skill import render_codex_skill
from loopcraft_core.canonical import canonical_json_bytes, sha256_digest
from loopcraft_core.compiler import compile_definition
from loopcraft_core.evidence.package import package_evidence


FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "accepted-definition.valid.json"
)


def load_valid() -> dict[str, Any]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_evidence_package_is_separate_and_binds_the_complete_build(
    tmp_path: Path,
) -> None:
    definition = load_valid()
    compiled = compile_definition(definition)
    artifact = render_codex_skill(compiled, tmp_path / "artifact")
    evidence_dir = tmp_path / "evidence"

    result = package_evidence(
        definition=definition,
        compiled=compiled,
        artifact=artifact,
        evidence_dir=evidence_dir,
    )

    assert result.evidence_dir == evidence_dir
    assert result.evidence_dir != artifact.skill_dir
    assert result.evidence_dir not in artifact.skill_dir.parents
    assert artifact.skill_dir not in result.evidence_dir.parents

    semantic_ir = {
        "schema_version": definition["schema_version"],
        "profile": definition["profile"],
        "behavior_contract": definition["behavior_contract"],
        "loops": definition["loops"],
    }
    expected_manifest = {
        "schema_version": "0.1.0",
        "definition_digest": sha256_digest(definition),
        "semantic_ir_digest": sha256_digest(semantic_ir),
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
    assert result.manifest == expected_manifest
    assert result.manifest["definition_digest"] == (
        compiled.final_execution_ir["definition_digest"]
    )

    expected_files = {
        "accepted-definition.json": definition,
        "final-execution-ir.json": compiled.final_execution_ir,
        "source-map.json": artifact.source_map,
        "validation-report.json": {
            "schema_validation": "passed",
            "semantic_validation": "passed",
            "accepted_definition": True,
        },
        "build-manifest.json": expected_manifest,
    }
    assert {path.name for path in result.evidence_dir.iterdir()} == set(
        expected_files
    )
    for filename, value in expected_files.items():
        assert (result.evidence_dir / filename).read_bytes() == (
            canonical_json_bytes(value) + b"\n"
        )


def test_evidence_result_is_frozen(tmp_path: Path) -> None:
    definition = load_valid()
    compiled = compile_definition(definition)
    artifact = render_codex_skill(compiled, tmp_path / "artifact")
    result = package_evidence(
        definition=definition,
        compiled=compiled,
        artifact=artifact,
        evidence_dir=tmp_path / "evidence",
    )

    with pytest.raises(FrozenInstanceError):
        result.evidence_dir = tmp_path / "other"
