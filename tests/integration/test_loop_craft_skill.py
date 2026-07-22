import json
from pathlib import Path
import re
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


def markdown_section(text: str, heading: str) -> str:
    match = re.search(
        rf"^##+ {re.escape(heading)}\s*$\n(?P<body>.*?)(?=^##+ |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match is not None, f"missing Markdown section: {heading}"
    return match.group("body")


def test_product_skill_routes_supported_entries_and_requires_acceptance() -> None:
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    for reference in (
        "references/from-scratch.md",
        "references/upgrade-skill.md",
        "references/from-conversation.md",
        "references/loopability-gate.md",
        "references/core-build.md",
    ):
        assert f"]({reference})" in text
        assert (SKILL / reference).is_file()
    assert "explicit approval" in text
    assert "Candidate Behavior Contract" in text
    assert "accepted definition" in text
    assert "conversation history" not in text
    assert "Loop Library" not in text
    assert "Loopy" not in text


def test_entries_use_one_shared_loopability_gate_contract() -> None:
    references = SKILL / "references"
    gate_path = references / "loopability-gate.md"
    assert gate_path.is_file()

    gate_text = gate_path.read_text(encoding="utf-8")
    gate_rules = re.findall(r"^\d+\. .+$", gate_text, flags=re.MULTILINE)
    assert len(gate_rules) == 7

    for entry_name in (
        "from-scratch.md",
        "upgrade-skill.md",
        "from-conversation.md",
    ):
        entry_text = (references / entry_name).read_text(encoding="utf-8")
        assert "[loopability-gate.md](loopability-gate.md)" in entry_text
        assert not any(rule in entry_text for rule in gate_rules)

    zero_loop = markdown_section(gate_text, "0 qualifying Loops")
    one_loop = markdown_section(gate_text, "Exactly 1 qualifying Loop")
    unsupported = markdown_section(
        gate_text, "More than 1 qualifying Loop or semantic loss"
    )
    assert "skill-package-v0.1" in zero_loop
    assert "skill-package-v0.1" in one_loop
    assert "Assessment only" in unsupported


def test_from_scratch_routes_approved_workflows_and_loops_through_packaging() -> None:
    text = (SKILL / "references" / "from-scratch.md").read_text(
        encoding="utf-8"
    )

    assert "core-slice-v0.1" not in text
    assert "0-loop Workflow" in text
    assert "1-loop bounded Loop" in text
    assert "skill-package-v0.1" in text
    assert "Candidate Review" in text
    assert "explicit approval" in text


def test_candidate_review_distinguishes_workflow_and_loop_packets() -> None:
    text = (SKILL / "references" / "candidate-review.md").read_text(
        encoding="utf-8"
    )
    workflow_packet = markdown_section(text, "0-loop Workflow packet")
    loop_packet = markdown_section(text, "1-loop bounded Loop packet")
    shared_packet = markdown_section(text, "Shared review fields")

    for field in ("steps", "success evidence", "failure or stop"):
        assert field in workflow_packet.lower()
    for cycle_step in ("Observe", "Choose", "Act", "Verify", "Record", "Adapt"):
        assert cycle_step in loop_packet
    for field in ("authority", "invariants", "boundary", "approval"):
        assert field in shared_packet.lower()


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
