import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import pytest

from loopcraft_core.canonical import canonical_json_bytes, sha256_digest
from loopcraft_core.pipeline import verify_build


ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "loop-craft" / "scripts" / "build_loop.py"
FIXTURES = ROOT / "tests" / "fixtures"
DEFINITION = FIXTURES / "accepted-definition.valid.json"
SOURCE_DEFINITION = FIXTURES / "accepted-definition.source-upgrade.json"
ENTRY_EVIDENCE = FIXTURES / "entry-evidence.valid.json"
SOURCE_SKILL = FIXTURES / "source-skill" / "existing-skill"


def run_cli(*arguments: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *(str(item) for item in arguments)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_entry(path: Path, definition_path: Path, *, existing: bool = False) -> None:
    value = load_json(ENTRY_EVIDENCE)
    value["definition_digest"] = sha256_digest(load_json(definition_path))
    if existing:
        value["entry_type"] = "existing_skill"
        value["source_summary"]["kind"] = "skill_assessment"
        value["source_summary"]["facts"] = [
            {
                "provenance": "observed",
                "summary": "The reviewed Skill package contains one defining Loop.",
            }
        ]
    path.write_bytes(canonical_json_bytes(value) + b"\n")


def build_with_entry(tmp_path: Path) -> Path:
    output = tmp_path / "entry-build"
    result = run_cli(
        "build",
        DEFINITION,
        output,
        "--entry-evidence",
        ENTRY_EVIDENCE,
    )
    assert result.returncode == 0, result.stderr
    return output


def test_build_binds_canonical_entry_evidence_and_keeps_it_out_of_artifact(
    tmp_path: Path,
) -> None:
    output = build_with_entry(tmp_path)
    evidence = output / "evidence"
    entry = load_json(evidence / "entry-evidence.json")
    manifest = load_json(evidence / "build-manifest.json")

    assert (evidence / "entry-evidence.json").read_bytes() == (
        canonical_json_bytes(load_json(ENTRY_EVIDENCE)) + b"\n"
    )
    assert manifest["entry_evidence_digest"] == sha256_digest(entry)
    assert manifest["entry_type"] == "from_scratch"
    assert verify_build(output)["status"] == "clean"
    artifact = next((output / "artifact").iterdir())
    assert not list(artifact.rglob("entry-evidence.json"))


@pytest.mark.parametrize(
    "mutation",
    ["tampered_entry", "missing_entry", "incomplete_manifest"],
)
def test_verify_rejects_broken_entry_evidence_binding(
    tmp_path: Path,
    mutation: str,
) -> None:
    output = build_with_entry(tmp_path)
    evidence = output / "evidence"
    entry_path = evidence / "entry-evidence.json"
    manifest_path = evidence / "build-manifest.json"

    if mutation == "tampered_entry":
        entry = load_json(entry_path)
        entry["source_summary"]["summary"] = "Tampered after build."
        entry_path.write_bytes(canonical_json_bytes(entry) + b"\n")
    elif mutation == "missing_entry":
        entry_path.unlink()
    else:
        manifest = load_json(manifest_path)
        del manifest["entry_type"]
        manifest_path.write_bytes(canonical_json_bytes(manifest) + b"\n")

    with pytest.raises(ValueError):
        verify_build(output)


def test_invalid_entry_evidence_stops_before_output_creation(tmp_path: Path) -> None:
    invalid = load_json(ENTRY_EVIDENCE)
    invalid["definition_digest"] = "sha256:" + "0" * 64
    invalid_path = tmp_path / "invalid-entry.json"
    invalid_path.write_bytes(canonical_json_bytes(invalid) + b"\n")
    output = tmp_path / "invalid-entry-build"

    result = run_cli(
        "build",
        DEFINITION,
        output,
        "--entry-evidence",
        invalid_path,
    )

    assert result.returncode != 0
    assert "definition digest" in result.stderr
    assert not output.exists()


def test_source_package_and_entry_evidence_bind_independently(
    tmp_path: Path,
) -> None:
    package_manifest = tmp_path / "source-package-manifest.json"
    entry_path = tmp_path / "existing-skill-entry.json"
    output = tmp_path / "source-entry-build"
    write_entry(entry_path, SOURCE_DEFINITION, existing=True)
    inventory = run_cli("inventory", SOURCE_SKILL, package_manifest)
    assert inventory.returncode == 0, inventory.stderr

    result = run_cli(
        "build",
        SOURCE_DEFINITION,
        output,
        "--source-skill",
        SOURCE_SKILL,
        "--package-manifest",
        package_manifest,
        "--entry-evidence",
        entry_path,
    )

    assert result.returncode == 0, result.stderr
    evidence_names = {path.name for path in (output / "evidence").iterdir()}
    assert {
        "accepted-definition.json",
        "final-execution-ir.json",
        "source-map.json",
        "validation-report.json",
        "build-manifest.json",
        "source-package-manifest.json",
        "entry-evidence.json",
    } == evidence_names
    manifest = load_json(output / "evidence" / "build-manifest.json")
    assert manifest["source_package_manifest_digest"] == sha256_digest(
        load_json(package_manifest)
    )
    assert manifest["entry_evidence_digest"] == sha256_digest(
        load_json(entry_path)
    )
    assert manifest["entry_type"] == "existing_skill"
    assert verify_build(output)["status"] == "clean"


def test_build_without_entry_evidence_remains_verifiable(tmp_path: Path) -> None:
    output = tmp_path / "historical-compatible-build"

    result = run_cli("build", DEFINITION, output)

    assert result.returncode == 0, result.stderr
    manifest = load_json(output / "evidence" / "build-manifest.json")
    assert "entry_evidence_digest" not in manifest
    assert "entry_type" not in manifest
    assert not (output / "evidence" / "entry-evidence.json").exists()
    assert verify_build(output)["status"] == "clean"
