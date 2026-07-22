from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any

from ..canonical import canonical_json_bytes


MANIFEST_SCHEMA_VERSION = "source-skill-package-v0.1"
ALLOWED_ROOT_DIRECTORIES = {"agents", "references", "scripts", "assets"}
ALLOWED_ROOT_FILES = {
    "SKILL.md",
    "license.txt",
    "LICENSE",
    "NOTICE",
    "NOTICE.md",
}
DIGEST_CONTRACT = re.compile(r"sha256:[0-9a-f]{64}")
SKILL_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def _file_digest(path: Path) -> str:
    return file_bytes_digest(path.read_bytes())


def file_bytes_digest(content: bytes) -> str:
    return f"sha256:{hashlib.sha256(content).hexdigest()}"


def is_link_or_junction(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or bool(is_junction and is_junction())


def directory_digest(root: Path) -> str:
    if is_link_or_junction(root) or not root.is_dir():
        raise ValueError("artifact directory must be a real, non-symlink directory")
    descendants = list(root.rglob("*"))
    if any(is_link_or_junction(path) for path in descendants):
        raise ValueError("artifact directory must not contain links or junctions")
    hasher = hashlib.sha256()
    files = sorted(
        (
            (path.relative_to(root).as_posix(), path)
            for path in descendants
            if path.is_file()
        ),
        key=lambda item: item[0],
    )
    for relative_path, path in files:
        path_bytes = relative_path.encode("utf-8")
        content = path.read_bytes()
        hasher.update(len(path_bytes).to_bytes(8, "big"))
        hasher.update(path_bytes)
        hasher.update(len(content).to_bytes(8, "big"))
        hasher.update(content)
    return f"sha256:{hasher.hexdigest()}"


def _validated_files(source_skill_dir: Path) -> list[tuple[str, Path]]:
    if is_link_or_junction(source_skill_dir) or not source_skill_dir.is_dir():
        raise ValueError("source Skill must be a real, non-symlink directory")

    root_entries = list(source_skill_dir.iterdir())
    if any(is_link_or_junction(path) for path in root_entries):
        raise ValueError("source Skill must not contain links or junctions")
    for path in root_entries:
        if path.name in ALLOWED_ROOT_DIRECTORIES:
            if not path.is_dir():
                raise ValueError(f"standard Skill root must be a directory: {path.name}")
        elif path.name in ALLOWED_ROOT_FILES:
            if not path.is_file():
                raise ValueError(f"standard Skill root must be a file: {path.name}")
        else:
            raise ValueError(f"unknown source Skill root entry: {path.name}")

    skill_path = source_skill_dir / "SKILL.md"
    if is_link_or_junction(skill_path) or not skill_path.is_file():
        raise ValueError("source Skill must contain a regular SKILL.md")

    descendants = list(source_skill_dir.rglob("*"))
    if any(is_link_or_junction(path) for path in descendants):
        raise ValueError("source Skill must not contain links or junctions")
    if any(not path.is_file() and not path.is_dir() for path in descendants):
        raise ValueError("source Skill may contain only regular files and directories")

    return sorted(
        (
            (path.relative_to(source_skill_dir).as_posix(), path)
            for path in descendants
            if path.is_file()
        ),
        key=lambda item: item[0],
    )


def _action_for(relative_path: str) -> str:
    if relative_path == "SKILL.md":
        return "overlay"
    if relative_path == "references/final-execution-ir.json":
        return "generated"
    return "preserve"


def inventory_source_skill(source_skill_dir: Path) -> dict[str, Any]:
    files = _validated_files(source_skill_dir)
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "source_skill_digest": directory_digest(source_skill_dir),
        "entries": [
            {
                "path": relative_path,
                "action": _action_for(relative_path),
                "digest": _file_digest(path),
            }
            for relative_path, path in files
        ],
    }


def validate_source_manifest(manifest: Any) -> dict[str, Any]:
    if not isinstance(manifest, dict) or set(manifest) != {
        "schema_version",
        "source_skill_digest",
        "entries",
    }:
        raise ValueError("source package manifest has an invalid object contract")
    if manifest["schema_version"] != MANIFEST_SCHEMA_VERSION:
        raise ValueError("source package manifest schema version is unsupported")
    source_digest = manifest["source_skill_digest"]
    if not isinstance(source_digest, str) or not DIGEST_CONTRACT.fullmatch(
        source_digest
    ):
        raise ValueError("source package manifest source digest is invalid")
    entries = manifest["entries"]
    if not isinstance(entries, list) or not entries:
        raise ValueError("source package manifest entries must be non-empty")

    paths: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"path", "action", "digest"}:
            raise ValueError("source package manifest entry contract is invalid")
        relative_path = entry["path"]
        if not isinstance(relative_path, str) or not relative_path:
            raise ValueError("source package manifest path is invalid")
        pure_path = PurePosixPath(relative_path)
        if (
            pure_path.is_absolute()
            or "\\" in relative_path
            or relative_path != pure_path.as_posix()
            or any(part in {"", ".", ".."} for part in pure_path.parts)
        ):
            raise ValueError("source package manifest paths must be POSIX relative paths")
        root_name = pure_path.parts[0]
        if root_name in ALLOWED_ROOT_DIRECTORIES:
            if len(pure_path.parts) < 2:
                raise ValueError("source package manifest may include files only")
        elif root_name not in ALLOWED_ROOT_FILES or len(pure_path.parts) != 1:
            raise ValueError(
                f"source package manifest path uses an unknown root: {relative_path}"
            )
        if entry["action"] != _action_for(relative_path):
            raise ValueError(f"source package manifest action is invalid: {relative_path}")
        digest = entry["digest"]
        if not isinstance(digest, str) or not DIGEST_CONTRACT.fullmatch(digest):
            raise ValueError(f"source package manifest digest is invalid: {relative_path}")
        paths.append(relative_path)

    if paths != sorted(paths) or len(paths) != len(set(paths)):
        raise ValueError("source package manifest entries must be uniquely sorted")
    if "SKILL.md" not in paths:
        raise ValueError("source package manifest must include SKILL.md")
    return manifest


def load_reviewed_manifest(
    source_skill_dir: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    if is_link_or_junction(manifest_path) or not manifest_path.is_file():
        raise ValueError("source package manifest must be a regular file")
    try:
        reviewed = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("source package manifest is unavailable or invalid") from exc
    validate_source_manifest(reviewed)
    current = inventory_source_skill(source_skill_dir)
    if canonical_json_bytes(reviewed) != canonical_json_bytes(current):
        raise ValueError("source package manifest is stale or does not match the source Skill")
    return reviewed


def write_source_manifest(
    source_skill_dir: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    source = source_skill_dir.resolve()
    manifest = manifest_path.resolve()
    if manifest == source or source in manifest.parents:
        raise ValueError("source package manifest must be outside the source Skill")
    if manifest_path.exists() or is_link_or_junction(manifest_path):
        raise FileExistsError(f"Manifest already exists: {manifest_path}")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = inventory_source_skill(source_skill_dir)
    manifest_path.write_bytes(canonical_json_bytes(manifest) + b"\n")
    return manifest


def source_frontmatter_name(skill_path: Path) -> str:
    try:
        lines = skill_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise ValueError("source SKILL.md must be readable UTF-8") from exc
    if not lines or lines[0].strip() != "---":
        raise ValueError("source SKILL.md frontmatter is missing")
    try:
        end = next(
            index
            for index in range(1, len(lines))
            if lines[index].strip() == "---"
        )
    except StopIteration as exc:
        raise ValueError("source SKILL.md frontmatter is unterminated") from exc

    names: list[str] = []
    for line in lines[1:end]:
        if not line.startswith("name:"):
            continue
        raw = line.removeprefix("name:").strip()
        if raw.startswith('"'):
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError("source SKILL.md frontmatter name is unsafe") from exc
        else:
            value = raw
        if not isinstance(value, str) or SKILL_ID.fullmatch(value) is None:
            raise ValueError("source SKILL.md frontmatter name is unsafe")
        names.append(value)
    if len(names) != 1:
        raise ValueError("source SKILL.md must have exactly one safely parseable name")
    return names[0]
