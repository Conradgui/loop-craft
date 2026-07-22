---
name: loop-craft
description: Use when an accepted Loop Craft JSON definition must be built into a target Agent Skill or an existing build must be checked for artifact drift.
---

# Loop Craft

Use the deterministic Core to build an accepted Behavior Contract into a target Agent Skill with separate evidence, or to verify an existing build for artifact drift.

## Core workflow

Read [references/core-build.md](references/core-build.md) before running a command.

- Build only from an accepted JSON definition into a new output directory.
- Verify only an existing build produced by the build command.
- Stop immediately when an input is missing, invalid, the wrong kind, or outside these two operations. Do not guess a replacement input or alter an existing build during verification.
