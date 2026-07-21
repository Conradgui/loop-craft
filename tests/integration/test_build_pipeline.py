import json
from pathlib import Path

import pytest

from loopcraft_core.pipeline import build_definition


FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "accepted-definition.valid.json"
)


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
