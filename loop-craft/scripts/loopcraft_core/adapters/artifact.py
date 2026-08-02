from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ArtifactResult:
    artifact_dir: Path
    artifact_digest: str
    source_map: dict[str, list[str]]
    adapter_name: str
    adapter_version: str
    profile_digest: str
    compatibility_report: dict[str, Any]
    conformance: str

    @property
    def skill_dir(self) -> Path:
        """Backward-compatible alias for existing Codex Skill consumers."""
        return self.artifact_dir
