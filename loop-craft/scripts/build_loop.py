from __future__ import annotations

import argparse
import json
from pathlib import Path

from loopcraft_core.pipeline import build_definition, verify_build


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build and verify Loop artifacts."
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    build = subcommands.add_parser("build")
    build.add_argument("definition", type=Path)
    build.add_argument("output", type=Path)

    verify = subcommands.add_parser("verify")
    verify.add_argument("output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "build":
        result = build_definition(args.definition, args.output)
        print(f"Artifact: {result.artifact_dir}")
        print(f"Evidence: {result.evidence_dir}")
        return 0

    report = verify_build(args.output)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "clean" else 1


if __name__ == "__main__":
    raise SystemExit(main())
