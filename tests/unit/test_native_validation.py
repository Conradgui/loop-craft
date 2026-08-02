import json
from pathlib import Path

import pytest

from loopcraft_core.native_validation import run_native_validation


def write_validator(path: Path, *, exit_code: int) -> None:
    path.write_text(
        "\n".join(
            [
                "import sys",
                "print('Skill is valid!' if "
                f"{exit_code} == 0 else 'Skill is invalid!', "
                f"file=sys.stdout if {exit_code} == 0 else sys.stderr)",
                f"raise SystemExit({exit_code})",
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_returns_path_free_receipt_for_passing_validator(
    tmp_path: Path,
) -> None:
    skill_dir = tmp_path / "skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("valid", encoding="utf-8")
    validator = tmp_path / "quick_validate.py"
    write_validator(validator, exit_code=0)

    receipt = run_native_validation(skill_dir, validator)

    assert receipt["schema_version"] == "native-validation-v0.1"
    assert receipt["validator"] == "codex-skill-creator/quick_validate.py"
    assert receipt["validator_digest"].startswith("sha256:")
    assert receipt["stdout_digest"].startswith("sha256:")
    assert receipt["stderr_digest"].startswith("sha256:")
    assert receipt["exit_code"] == 0
    assert receipt["status"] == "passed"
    serialized = json.dumps(receipt, sort_keys=True)
    assert str(tmp_path) not in serialized


def test_rejects_failing_validator(tmp_path: Path) -> None:
    skill_dir = tmp_path / "skill"
    skill_dir.mkdir()
    validator = tmp_path / "quick_validate.py"
    write_validator(validator, exit_code=1)

    with pytest.raises(ValueError, match="Codex native validator failed"):
        run_native_validation(skill_dir, validator)


def test_rejects_unavailable_validator(tmp_path: Path) -> None:
    skill_dir = tmp_path / "skill"
    skill_dir.mkdir()

    with pytest.raises(
        ValueError,
        match="Codex native validator is unavailable",
    ):
        run_native_validation(skill_dir, tmp_path / "missing.py")
