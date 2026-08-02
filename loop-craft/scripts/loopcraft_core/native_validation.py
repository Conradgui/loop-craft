from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
from typing import Any
import re

from .adapters.source_skill import file_bytes_digest, is_link_or_junction


DIGEST_CONTRACT = re.compile(r"sha256:[0-9a-f]{64}")


def validate_native_validation_receipt(value: Any) -> None:
    if not isinstance(value, dict) or set(value) != {
        "schema_version",
        "validator",
        "validator_digest",
        "stdout_digest",
        "stderr_digest",
        "exit_code",
        "status",
    }:
        raise ValueError("native validation receipt contract is invalid")
    if (
        value["schema_version"] != "native-validation-v0.1"
        or value["validator"]
        != "codex-skill-creator/quick_validate.py"
        or value["exit_code"] != 0
        or value["status"] != "passed"
    ):
        raise ValueError("native validation receipt contract is invalid")
    for field in ("validator_digest", "stdout_digest", "stderr_digest"):
        if (
            not isinstance(value[field], str)
            or DIGEST_CONTRACT.fullmatch(value[field]) is None
        ):
            raise ValueError("native validation receipt contract is invalid")


def run_native_validation(
    skill_dir: Path,
    validator_path: Path,
) -> dict[str, Any]:
    if (
        is_link_or_junction(validator_path)
        or not validator_path.is_file()
    ):
        raise ValueError("Codex native validator is unavailable")
    if is_link_or_junction(skill_dir) or not skill_dir.is_dir():
        raise ValueError("Codex Skill artifact is unavailable")

    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    completed = subprocess.run(
        [sys.executable, str(validator_path), str(skill_dir)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=environment,
        check=False,
    )
    if completed.returncode != 0:
        raise ValueError("Codex native validator failed")

    return {
        "schema_version": "native-validation-v0.1",
        "validator": "codex-skill-creator/quick_validate.py",
        "validator_digest": file_bytes_digest(validator_path.read_bytes()),
        "stdout_digest": file_bytes_digest(completed.stdout.encode("utf-8")),
        "stderr_digest": file_bytes_digest(completed.stderr.encode("utf-8")),
        "exit_code": completed.returncode,
        "status": "passed",
    }
