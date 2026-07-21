from pathlib import Path

from loopcraft_core.pipeline import build_definition, verify_build


FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "accepted-definition.valid.json"
)


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
