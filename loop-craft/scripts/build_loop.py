from __future__ import annotations

import argparse
from pathlib import Path

from loopcraft_core.pipeline import build_definition


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a Loop Skill and Evidence Package."
    )
    parser.add_argument("definition", type=Path)
    parser.add_argument("output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = build_definition(args.definition, args.output)
    print(f"Artifact: {result.artifact_dir}")
    print(f"Evidence: {result.evidence_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
