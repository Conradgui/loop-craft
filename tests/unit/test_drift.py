import json
import os
from pathlib import Path
import shutil

import pytest

from loopcraft_core.pipeline import build_definition, verify_build


FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "accepted-definition.valid.json"
)


def file_snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def test_verify_build_reports_drift_without_changing_artifact(
    tmp_path: Path,
) -> None:
    result = build_definition(FIXTURE, tmp_path / "build")
    skill_file = result.artifact_dir / "SKILL.md"
    edited_content = skill_file.read_bytes() + b"manual edit\n"
    skill_file.write_bytes(edited_content)

    verification = verify_build(result.output_root)

    assert verification["status"] == "drifted"
    assert verification["expected_artifact_digest"] != (
        verification["actual_artifact_digest"]
    )
    assert skill_file.read_bytes() == edited_content


@pytest.mark.parametrize(
    "missing_file",
    [
        "accepted-definition.json",
        "final-execution-ir.json",
        "source-map.json",
        "validation-report.json",
        "build-manifest.json",
    ],
)
def test_verify_build_rejects_each_missing_evidence_file_without_reading_manifest(
    tmp_path: Path,
    missing_file: str,
) -> None:
    result = build_definition(FIXTURE, tmp_path / "build")
    (result.evidence_dir / missing_file).unlink()

    with pytest.raises(ValueError, match="evidence"):
        verify_build(result.output_root)


def test_verify_build_rejects_empty_artifact_directory_without_changes(
    tmp_path: Path,
) -> None:
    result = build_definition(FIXTURE, tmp_path / "build")
    empty_dir = result.artifact_dir / "empty"
    empty_dir.mkdir()
    artifact_before = file_snapshot(result.artifact_dir)

    with pytest.raises(ValueError, match="empty"):
        verify_build(result.output_root)

    assert empty_dir.is_dir()
    assert file_snapshot(result.artifact_dir) == artifact_before


def test_verify_build_rejects_evidence_digest_mismatch_without_changes(
    tmp_path: Path,
) -> None:
    result = build_definition(FIXTURE, tmp_path / "build")
    definition_path = result.evidence_dir / "accepted-definition.json"
    definition = json.loads(definition_path.read_text(encoding="utf-8"))
    definition["profile"] = "tampered-profile"
    definition_path.write_text(json.dumps(definition), encoding="utf-8")
    artifact_before = file_snapshot(result.artifact_dir)
    evidence_before = file_snapshot(result.evidence_dir)

    with pytest.raises(ValueError, match="digest"):
        verify_build(result.output_root)

    assert file_snapshot(result.artifact_dir) == artifact_before
    assert file_snapshot(result.evidence_dir) == evidence_before


def test_verify_build_rejects_symlinked_skill_directory_without_changes(
    tmp_path: Path,
) -> None:
    baseline = build_definition(FIXTURE, tmp_path / "baseline")
    external_skill = shutil.copytree(
        baseline.artifact_dir,
        tmp_path / "external-skill",
    )
    output = tmp_path / "symlinked-skill-build"
    artifact_root = output / "artifact"
    artifact_root.mkdir(parents=True)
    evidence_dir = shutil.copytree(baseline.evidence_dir, output / "evidence")
    skill_link = artifact_root / baseline.artifact_dir.name
    os.symlink(external_skill, skill_link, target_is_directory=True)
    artifact_before = file_snapshot(external_skill)
    evidence_before = file_snapshot(evidence_dir)

    with pytest.raises(ValueError, match="symlink"):
        verify_build(output)

    assert skill_link.is_symlink()
    assert file_snapshot(external_skill) == artifact_before
    assert file_snapshot(evidence_dir) == evidence_before


def test_verify_build_rejects_symlinked_artifact_file_without_changes(
    tmp_path: Path,
) -> None:
    baseline = build_definition(FIXTURE, tmp_path / "baseline")
    output = tmp_path / "symlinked-file-build"
    artifact_dir = shutil.copytree(
        baseline.artifact_dir,
        output / "artifact" / baseline.artifact_dir.name,
        ignore=shutil.ignore_patterns("SKILL.md"),
    )
    evidence_dir = shutil.copytree(baseline.evidence_dir, output / "evidence")
    external_skill_file = tmp_path / "external-SKILL.md"
    external_skill_file.write_bytes(
        (baseline.artifact_dir / "SKILL.md").read_bytes()
    )
    skill_link = artifact_dir / "SKILL.md"
    os.symlink(external_skill_file, skill_link)
    artifact_before = file_snapshot(artifact_dir)
    evidence_before = file_snapshot(evidence_dir)

    with pytest.raises(ValueError, match="symlink"):
        verify_build(output)

    assert skill_link.is_symlink()
    assert file_snapshot(artifact_dir) == artifact_before
    assert file_snapshot(evidence_dir) == evidence_before


def test_verify_build_rejects_extra_artifact_root_file_without_changes(
    tmp_path: Path,
) -> None:
    result = build_definition(FIXTURE, tmp_path / "build")
    artifact_root = result.output_root / "artifact"
    extra_file = artifact_root / "EXTRA.txt"
    extra_file.write_text("unexpected", encoding="utf-8")
    artifact_before = file_snapshot(artifact_root)
    evidence_before = file_snapshot(result.evidence_dir)

    with pytest.raises(ValueError, match="exactly one artifact directory"):
        verify_build(result.output_root)

    assert file_snapshot(artifact_root) == artifact_before
    assert file_snapshot(result.evidence_dir) == evidence_before


def test_verify_build_rejects_symlinked_output_root_without_changes(
    tmp_path: Path,
) -> None:
    baseline = build_definition(FIXTURE, tmp_path / "baseline")
    output_link = tmp_path / "output-link"
    os.symlink(baseline.output_root, output_link, target_is_directory=True)
    baseline_before = file_snapshot(baseline.output_root)

    with pytest.raises(ValueError, match="symlink"):
        verify_build(output_link)

    assert output_link.is_symlink()
    assert file_snapshot(baseline.output_root) == baseline_before


def test_verify_build_rejects_symlinked_evidence_directory_without_changes(
    tmp_path: Path,
) -> None:
    baseline = build_definition(FIXTURE, tmp_path / "baseline")
    output = tmp_path / "symlinked-evidence-build"
    artifact_dir = shutil.copytree(
        baseline.artifact_dir,
        output / "artifact" / baseline.artifact_dir.name,
    )
    evidence_link = output / "evidence"
    os.symlink(baseline.evidence_dir, evidence_link, target_is_directory=True)
    artifact_before = file_snapshot(artifact_dir)
    evidence_before = file_snapshot(baseline.evidence_dir)

    with pytest.raises(ValueError, match="symlink"):
        verify_build(output)

    assert evidence_link.is_symlink()
    assert file_snapshot(artifact_dir) == artifact_before
    assert file_snapshot(baseline.evidence_dir) == evidence_before


def test_verify_build_rejects_symlinked_manifest_without_changes(
    tmp_path: Path,
) -> None:
    baseline = build_definition(FIXTURE, tmp_path / "baseline")
    output = tmp_path / "symlinked-manifest-build"
    artifact_dir = shutil.copytree(
        baseline.artifact_dir,
        output / "artifact" / baseline.artifact_dir.name,
    )
    evidence_dir = shutil.copytree(
        baseline.evidence_dir,
        output / "evidence",
        ignore=shutil.ignore_patterns("build-manifest.json"),
    )
    manifest_link = evidence_dir / "build-manifest.json"
    os.symlink(
        baseline.evidence_dir / "build-manifest.json",
        manifest_link,
    )
    artifact_before = file_snapshot(artifact_dir)
    evidence_before = file_snapshot(baseline.evidence_dir)

    with pytest.raises(ValueError, match="symlink"):
        verify_build(output)

    assert manifest_link.is_symlink()
    assert file_snapshot(artifact_dir) == artifact_before
    assert file_snapshot(baseline.evidence_dir) == evidence_before
