from __future__ import annotations

import argparse
import json
from pathlib import Path

from loopcraft_core.pipeline import build_definition, verify_build
from loopcraft_core.adapters.source_skill import write_source_manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build and verify Loop artifacts."
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    build = subcommands.add_parser("build")
    build.add_argument("definition", type=Path)
    build.add_argument("output", type=Path)
    build.add_argument("--source-skill", type=Path)
    build.add_argument("--package-manifest", type=Path)

    inventory = subcommands.add_parser("inventory")
    inventory.add_argument("source_skill_dir", type=Path)
    inventory.add_argument("new_manifest", type=Path)

    verify = subcommands.add_parser("verify")
    verify.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.command == "build" and (
        (args.source_skill is None) != (args.package_manifest is None)
    ):
        parser.error(
            "--source-skill and --package-manifest must be provided together"
        )
    return args


def main() -> int:
    args = parse_args()
    if args.command == "build":
        result = build_definition(
            args.definition,
            args.output,
            source_skill_dir=args.source_skill,
            package_manifest_path=args.package_manifest,
        )
        print(f"Artifact: {result.artifact_dir}")
        print(f"Evidence: {result.evidence_dir}")
        return 0

    if args.command == "inventory":
        manifest = write_source_manifest(
            args.source_skill_dir,
            args.new_manifest,
        )
        print(f"Manifest: {args.new_manifest}")
        print(f"Source digest: {manifest['source_skill_digest']}")
        return 0

    report = verify_build(args.output)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "clean" else 1


if __name__ == "__main__":
    raise SystemExit(main())
