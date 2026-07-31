import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from loopcraft_core.canonical import canonical_json_bytes, sha256_digest
from loopcraft_core.pipeline import verify_build


ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "loop-craft" / "scripts" / "build_loop.py"
FIXTURES = ROOT / "tests" / "fixtures"
ZERO_LOOP = FIXTURES / "accepted-definition.zero-loop.json"
SOURCE_DEFINITION = FIXTURES / "accepted-definition.source-upgrade.json"
SOURCE_SKILL = FIXTURES / "source-skill" / "existing-skill"
MECHANICAL_SOURCE = FIXTURES / "source-skill" / "mechanical-package"


def run_cli(*arguments: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *(str(item) for item in arguments)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_zero_loop_build_renders_a_complete_ordinary_skill(tmp_path: Path) -> None:
    output = tmp_path / "zero-loop-build"

    result = run_cli("build", ZERO_LOOP, output)

    assert result.returncode == 0, result.stderr
    skill_text = (output / "artifact" / "release-checklist" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "### Steps" in skill_text
    assert "### Success evidence" in skill_text
    assert "### Failure or stop" in skill_text
    assert "### Loop:" not in skill_text
    assert verify_build(output)["status"] == "clean"
    assert len(list((output / "evidence").iterdir())) == 5


def test_inventory_source_build_preserves_resources_and_binds_evidence(
    tmp_path: Path,
) -> None:
    source_before = snapshot(SOURCE_SKILL)
    manifest_path = tmp_path / "source-package-manifest.json"
    output = tmp_path / "source-build"

    inventory = run_cli("inventory", SOURCE_SKILL, manifest_path)
    assert inventory.returncode == 0, inventory.stderr
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert [entry["path"] for entry in manifest["entries"]] == sorted(
        source_before
    )
    assert all(not Path(entry["path"]).is_absolute() for entry in manifest["entries"])
    actions = {entry["path"]: entry["action"] for entry in manifest["entries"]}
    assert actions["SKILL.md"] == "overlay"
    assert actions["references/final-execution-ir.json"] == "generated"
    assert actions["assets/template.txt"] == "preserve"

    build = run_cli(
        "build",
        SOURCE_DEFINITION,
        output,
        "--source-skill",
        SOURCE_SKILL,
        "--package-manifest",
        manifest_path,
    )
    assert build.returncode == 0, build.stderr
    assert snapshot(SOURCE_SKILL) == source_before

    artifact = output / "artifact" / "existing-skill"
    for relative_path in (
        "agents/openai.yaml",
        "references/operating.md",
        "scripts/helper.py",
        "assets/template.txt",
        "LICENSE",
    ):
        assert (artifact / relative_path).read_bytes() == source_before[relative_path]
    skill_bytes = (artifact / "SKILL.md").read_bytes()
    assert skill_bytes.startswith(source_before["SKILL.md"])
    assert b"## Feedback Loop" in skill_bytes
    skill_text = skill_bytes.decode("utf-8")
    assert '"publish_target"' in skill_text
    assert '"edit_unrelated_files"' in skill_text
    assert '"filesystem.read"' in skill_text
    assert (artifact / "references/final-execution-ir.json").read_bytes() != (
        source_before["references/final-execution-ir.json"]
    )

    evidence = output / "evidence"
    assert len(list(evidence.iterdir())) == 6
    evidence_manifest = json.loads(
        (evidence / "source-package-manifest.json").read_text(encoding="utf-8")
    )
    build_manifest = json.loads(
        (evidence / "build-manifest.json").read_text(encoding="utf-8")
    )
    source_map = json.loads(
        (evidence / "source-map.json").read_text(encoding="utf-8")
    )
    assert evidence_manifest == manifest
    assert build_manifest["source_package_manifest_digest"] == sha256_digest(manifest)
    assert build_manifest["source_skill_digest"] == manifest["source_skill_digest"]
    assert build_manifest["compatibility_report"] == {
        "schema_version": "codex-compatibility-v0.1",
        "platform": "codex",
        "overall": "native",
        "required": [
            {"capability": "filesystem.read", "status": "native"},
            {"capability": "filesystem.write", "status": "native"},
        ],
        "optional": [
            {"capability": "validation.execute", "status": "native"}
        ],
    }
    assert build_manifest["conformance"] == "self_contained"
    asset_index = next(
        index
        for index, entry in enumerate(manifest["entries"])
        if entry["path"] == "assets/template.txt"
    )
    assert source_map["assets/template.txt#source"] == [
        f"/source-package-manifest/entries/{asset_index}"
    ]
    assert source_map["SKILL.md#feedback-loop/invariants"] == [
        "/loops/0/invariants"
    ]
    assert verify_build(output)["status"] == "clean"


def test_common_mechanical_package_gets_canonical_frontmatter_without_source_edits(
    tmp_path: Path,
) -> None:
    source_before = snapshot(MECHANICAL_SOURCE)
    manifest_path = tmp_path / "mechanical-manifest.json"
    output = tmp_path / "mechanical-build"

    inventory = run_cli("inventory", MECHANICAL_SOURCE, manifest_path)
    assert inventory.returncode == 0, inventory.stderr
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    actions = {entry["path"]: entry["action"] for entry in manifest["entries"]}
    assert actions == {"SKILL.md": "overlay", "package.json": "preserve"}

    build = run_cli(
        "build",
        SOURCE_DEFINITION,
        output,
        "--source-skill",
        MECHANICAL_SOURCE,
        "--package-manifest",
        manifest_path,
    )

    assert build.returncode == 0, build.stderr
    assert snapshot(MECHANICAL_SOURCE) == source_before
    artifact = output / "artifact" / "existing-skill"
    assert (artifact / "package.json").read_bytes() == source_before["package.json"]
    expected_prefix = (
        "---\n"
        "name: existing-skill\n"
        'description: "Use when an existing result needs evidence-driven repair"\n'
        "---\n\n"
    ).encode("utf-8")
    assert (artifact / "SKILL.md").read_bytes().startswith(
        expected_prefix + source_before["SKILL.md"]
    )

    source_map = json.loads(
        (output / "evidence" / "source-map.json").read_text(encoding="utf-8")
    )
    skill_index = next(
        index
        for index, entry in enumerate(manifest["entries"])
        if entry["path"] == "SKILL.md"
    )
    assert source_map["SKILL.md#source-body"] == [
        f"/source-package-manifest/entries/{skill_index}"
    ]
    assert source_map["SKILL.md#generated-frontmatter/name"] == ["/identity/id"]
    assert source_map["SKILL.md#generated-frontmatter/description"] == [
        "/applicability/use_when/0"
    ]
    assert verify_build(output)["status"] == "clean"


def test_source_build_rejects_valid_but_conflicting_frontmatter_name(
    tmp_path: Path,
) -> None:
    conflicting = tmp_path / "renamed-source-directory"
    shutil.copytree(SOURCE_SKILL, conflicting)
    skill_path = conflicting / "SKILL.md"
    original_body = skill_path.read_text(encoding="utf-8").split("---\n", 2)[2]
    skill_path.write_text(
        "---\nname: conflicting-name\n"
        "description: Use when the package name conflicts.\n---\n"
        + original_body,
        encoding="utf-8",
    )
    manifest_path = tmp_path / "conflicting-manifest.json"
    output = tmp_path / "conflicting-build"
    assert run_cli("inventory", conflicting, manifest_path).returncode == 0

    build = run_cli(
        "build",
        SOURCE_DEFINITION,
        output,
        "--source-skill",
        conflicting,
        "--package-manifest",
        manifest_path,
    )

    assert build.returncode != 0
    assert "frontmatter name must match definition identity.id" in build.stderr
    assert not output.exists()


def test_package_json_does_not_weaken_out_of_root_link_guard(
    tmp_path: Path,
) -> None:
    source = tmp_path / "linked-mechanical-package"
    shutil.copytree(MECHANICAL_SOURCE, source)
    outside = tmp_path / "outside.txt"
    outside.write_text("private", encoding="utf-8")
    try:
        os.symlink(outside, source / "outside-link.txt")
    except OSError as exc:
        pytest.skip(f"links unavailable: {exc}")

    inventory = run_cli("inventory", source, tmp_path / "linked-manifest.json")

    assert inventory.returncode != 0
    assert "links or junctions" in inventory.stderr


def test_source_build_rejects_a_stale_reviewed_manifest(tmp_path: Path) -> None:
    manifest_path = tmp_path / "source-package-manifest.json"
    assert run_cli("inventory", SOURCE_SKILL, manifest_path).returncode == 0
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["entries"][0]["digest"] = "sha256:" + "0" * 64
    manifest_path.write_bytes(canonical_json_bytes(manifest) + b"\n")
    output = tmp_path / "stale-build"

    result = run_cli(
        "build",
        SOURCE_DEFINITION,
        output,
        "--source-skill",
        SOURCE_SKILL,
        "--package-manifest",
        manifest_path,
    )

    assert result.returncode != 0
    assert "stale" in result.stderr
    assert not output.exists()


def test_source_build_rejects_unpaired_source_options(tmp_path: Path) -> None:
    result = run_cli(
        "build",
        SOURCE_DEFINITION,
        tmp_path / "unpaired-build",
        "--source-skill",
        SOURCE_SKILL,
    )

    assert result.returncode != 0
    assert "provided together" in result.stderr


def test_required_unsupported_capability_stops_before_output(tmp_path: Path) -> None:
    definition = json.loads(ZERO_LOOP.read_text(encoding="utf-8"))
    definition["behavior_contract"]["capabilities"]["required"].append(
        "network.write"
    )
    definition_path = tmp_path / "unsupported-required.json"
    definition_path.write_text(json.dumps(definition), encoding="utf-8")
    output = tmp_path / "unsupported-required-build"

    result = run_cli("build", definition_path, output)

    assert result.returncode != 0
    assert "unsupported required Codex capability" in result.stderr
    assert not output.exists()


def test_optional_unsupported_capability_is_degraded_and_verifiable(
    tmp_path: Path,
) -> None:
    definition = json.loads(ZERO_LOOP.read_text(encoding="utf-8"))
    definition["behavior_contract"]["capabilities"]["optional"] = [
        "network.observe"
    ]
    definition_path = tmp_path / "unsupported-optional.json"
    definition_path.write_text(json.dumps(definition), encoding="utf-8")
    output = tmp_path / "unsupported-optional-build"

    result = run_cli("build", definition_path, output)

    assert result.returncode == 0, result.stderr
    manifest = json.loads(
        (output / "evidence" / "build-manifest.json").read_text(
            encoding="utf-8"
        )
    )
    report = manifest["compatibility_report"]
    assert report["overall"] == "degraded"
    assert report["optional"] == [
        {"capability": "network.observe", "status": "unsupported"}
    ]
    assert manifest["conformance"] == "self_contained"
    assert verify_build(output)["status"] == "clean"


def test_inventory_rejects_an_unknown_root(tmp_path: Path) -> None:
    unknown = tmp_path / "unknown-skill"
    unknown.mkdir()
    (unknown / "SKILL.md").write_text("---\nname: unknown-skill\n---\n", encoding="utf-8")
    (unknown / "README.md").write_text("not a standard root", encoding="utf-8")
    unknown_result = run_cli("inventory", unknown, tmp_path / "unknown.json")
    assert unknown_result.returncode != 0
    assert "unknown" in unknown_result.stderr


def test_inventory_manifest_cannot_be_written_inside_source_skill(
    tmp_path: Path,
) -> None:
    source_before = snapshot(SOURCE_SKILL)
    manifest_path = SOURCE_SKILL / "references" / "reviewed-manifest.json"

    result = run_cli("inventory", SOURCE_SKILL, manifest_path)

    assert result.returncode != 0
    assert "outside the source Skill" in result.stderr
    assert snapshot(SOURCE_SKILL) == source_before
    assert not manifest_path.exists()
