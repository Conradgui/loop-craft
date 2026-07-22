import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from loopcraft_core.pipeline import build_definition


FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "accepted-definition.valid.json"
)
ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "loop-craft" / "scripts" / "build_loop.py"


def run_cli(*arguments: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *(str(item) for item in arguments)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture
def cli_build(tmp_path: Path) -> tuple[Path, subprocess.CompletedProcess[str]]:
    output = tmp_path / "cli-build"
    result = run_cli("build", FIXTURE, output)
    assert result.returncode == 0, result.stderr
    return output, result


def file_snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_pipeline_builds_identical_outputs(tmp_path: Path) -> None:
    first = build_definition(FIXTURE, tmp_path / "first")
    second = build_definition(FIXTURE, tmp_path / "second")

    assert first.manifest == second.manifest
    assert file_snapshot(first.output_root) == file_snapshot(second.output_root)
    assert first.artifact_dir.parent.name == "artifact"
    assert first.evidence_dir.name == "evidence"


def test_invalid_input_leaves_no_partial_output(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.json"
    invalid.write_text(
        json.dumps({"schema_version": "0.1.0"}), encoding="utf-8"
    )
    output = tmp_path / "failed-build"

    with pytest.raises(ValueError):
        build_definition(invalid, output)

    assert not output.exists()


def test_adapter_failure_cleans_staging_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import loopcraft_core.pipeline as pipeline

    def fail_adapter(*args: object, **kwargs: object) -> None:
        raise RuntimeError("adapter failed")

    monkeypatch.setattr(pipeline, "render_codex_skill", fail_adapter)
    output = tmp_path / "adapter-failure"

    with pytest.raises(RuntimeError, match="adapter failed"):
        pipeline.build_definition(FIXTURE, output)

    assert not output.exists()


@pytest.mark.parametrize("fail_at_write", [2, 3, 4, 5])
def test_evidence_failure_cleans_partial_staging_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    fail_at_write: int,
) -> None:
    import loopcraft_core.evidence.package as evidence_package

    original_write_json = evidence_package._write_json
    write_count = 0

    def fail_after_partial_write(path: Path, value: object) -> None:
        nonlocal write_count
        write_count += 1
        original_write_json(path, value)
        if write_count == fail_at_write:
            raise RuntimeError("evidence write failed")

    monkeypatch.setattr(evidence_package, "_write_json", fail_after_partial_write)
    output = tmp_path / "evidence-failure"

    with pytest.raises(RuntimeError, match="evidence write failed"):
        build_definition(FIXTURE, output)

    assert not output.exists()
    assert not list(tmp_path.glob(f".{output.name}.*"))


def test_existing_output_is_rejected_without_modification(
    tmp_path: Path,
) -> None:
    output = tmp_path / "existing-output"
    output.mkdir()
    existing_file = output / "keep.txt"
    existing_file.write_bytes(b"preserve me")
    before = file_snapshot(output)

    with pytest.raises(FileExistsError):
        build_definition(FIXTURE, output)

    assert file_snapshot(output) == before
    assert not list(tmp_path.glob(f".{output.name}.*"))


def test_dangling_output_symlink_is_treated_as_occupied(tmp_path: Path) -> None:
    target = tmp_path / "missing-target"
    output = tmp_path / "occupied-link"
    os.symlink(target, output, target_is_directory=True)

    with pytest.raises(FileExistsError):
        build_definition(FIXTURE, output)

    assert output.is_symlink()
    assert not target.exists()


def test_cli_build_returns_zero_and_prints_output_paths(
    cli_build: tuple[Path, subprocess.CompletedProcess[str]],
) -> None:
    output, result = cli_build

    assert "Artifact:" in result.stdout
    assert "Evidence:" in result.stdout
    assert len(list((output / "artifact").iterdir())) == 1
    assert (output / "evidence" / "build-manifest.json").is_file()


def test_cli_verify_clean_returns_zero_and_json(
    cli_build: tuple[Path, subprocess.CompletedProcess[str]],
) -> None:
    output, _ = cli_build

    result = run_cli("verify", output)

    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["status"] == "clean"
    assert report["expected_artifact_digest"] == (
        report["actual_artifact_digest"]
    )


def test_cli_verify_drift_returns_one_without_rewriting_artifact(
    cli_build: tuple[Path, subprocess.CompletedProcess[str]],
) -> None:
    output, _ = cli_build
    artifact_dir = next((output / "artifact").iterdir())
    skill_file = artifact_dir / "SKILL.md"
    edited_content = skill_file.read_bytes() + b"manual edit\n"
    skill_file.write_bytes(edited_content)

    result = run_cli("verify", output)

    assert result.returncode == 1, result.stderr
    report = json.loads(result.stdout)
    assert report["status"] == "drifted"
    assert report["expected_artifact_digest"] != (
        report["actual_artifact_digest"]
    )
    assert skill_file.read_bytes() == edited_content
