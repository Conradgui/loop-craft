from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "loop-craft"


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
