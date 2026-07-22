import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "loop-craft"
FIXTURE = ROOT / "tests" / "fixtures" / "accepted-definition.valid.json"

EXPECTED_SHORT_DESCRIPTION = "Design, upgrade, and package bounded agent workflows"
EXPECTED_DEFAULT_PROMPT = (
    "Use $loop-craft to design, distill, or upgrade a workflow and package "
    "the approved result as a Skill with separate evidence."
)
EXPECTED_OPENAI_YAML = (
    "interface:\n"
    '  display_name: "Loop Craft"\n'
    f'  short_description: "{EXPECTED_SHORT_DESCRIPTION}"\n'
    f'  default_prompt: "{EXPECTED_DEFAULT_PROMPT}"\n'
)
BUILD_COMMAND = (
    "python scripts/build_loop.py build <accepted-definition.json> "
    "<new-output-directory>"
)
VERIFY_COMMAND = "python scripts/build_loop.py verify <existing-output-directory>"


def test_loop_craft_contains_core_and_no_dev_docs() -> None:
    assert (SKILL / "SKILL.md").is_file()
    assert (SKILL / "agents" / "openai.yaml").is_file()
    assert (SKILL / "references" / "core-build.md").is_file()
    assert (SKILL / "scripts" / "build_loop.py").is_file()
    assert (SKILL / "scripts" / "loopcraft_core").is_dir()
    assert not (SKILL / "README.md").exists()
    assert not (SKILL / "tests").exists()


def test_product_skill_does_not_claim_unimplemented_entries() -> None:
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert "accepted Behavior Contract" in text
    assert "conversation history" not in text
    assert "Loop Library" not in text
    assert "Loopy" not in text


def test_product_skill_metadata_matches_contract() -> None:
    metadata = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")

    assert metadata == EXPECTED_OPENAI_YAML
    assert 25 <= len(EXPECTED_SHORT_DESCRIPTION) <= 64
    assert '  display_name: "Loop Craft"\n' in metadata
    assert "$loop-craft" in metadata


def test_product_skill_links_to_core_build_reference() -> None:
    skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    relative_reference = Path("references/core-build.md")

    assert f"({relative_reference.as_posix()})" in skill_text
    assert (SKILL / relative_reference).resolve().is_file()


def test_core_build_reference_documents_exact_cli_commands() -> None:
    reference = (SKILL / "references" / "core-build.md").read_text(
        encoding="utf-8"
    )

    assert BUILD_COMMAND in reference
    assert VERIFY_COMMAND in reference
    assert (
        "The runtime must provide Python and jsonschema; if either dependency "
        "is missing, stop and do not guess or install it."
    ) in reference


def test_product_skill_runs_build_clean_and_drift_verify_from_skill_directory(
    tmp_path: Path,
) -> None:
    output = tmp_path / "core-build"
    build = subprocess.run(
        [
            sys.executable,
            "scripts/build_loop.py",
            "build",
            str(FIXTURE),
            str(output),
        ],
        cwd=SKILL,
        capture_output=True,
        text=True,
        check=False,
    )

    assert build.returncode == 0, build.stderr
    assert (output / "artifact").is_dir()
    assert (output / "evidence").is_dir()

    verify = subprocess.run(
        [sys.executable, "scripts/build_loop.py", "verify", str(output)],
        cwd=SKILL,
        capture_output=True,
        text=True,
        check=False,
    )

    assert verify.returncode == 0, verify.stderr
    assert json.loads(verify.stdout)["status"] == "clean"

    artifact_entries = list((output / "artifact").iterdir())
    assert len(artifact_entries) == 1
    generated_skill = artifact_entries[0]
    assert generated_skill.is_dir()
    skill_file = generated_skill / "SKILL.md"
    edited_content = skill_file.read_bytes() + b"manual edit\n"
    skill_file.write_bytes(edited_content)

    drift = subprocess.run(
        [sys.executable, "scripts/build_loop.py", "verify", str(output)],
        cwd=SKILL,
        capture_output=True,
        text=True,
        check=False,
    )

    assert drift.returncode == 1, drift.stderr
    assert json.loads(drift.stdout)["status"] == "drifted"
    assert skill_file.read_bytes() == edited_content
