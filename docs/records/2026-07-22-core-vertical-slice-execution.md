# Core Vertical Slice Execution Record

- Date: 2026-07-22
- Scope: Accepted Definition -> target Skill + Evidence, plus drift verification.
- Tested code SHA: `d9bfab2e297f6d0ebf0e64df5d1b39f8f1d7ccd8`.
- Precondition refs: `main=ebc5ec0dae1311b767a1e7ecaeb719329039b2f7`; feature based on `30ca5a32f929ec806bc49faa85052e3ce19b501e` plus seven local commits, including five contract-fix commits.
- Runtime: Python `3.13.13`; existing repository dependencies only.

## Commands and Results

1. Worktree gate: `git status --porcelain=v1` produced no output; `build/final-20260722-a` and `build/final-20260722-b` did not exist.
2. `python -m pytest -q` -> `110 passed in 6.04s` (exit 0).
3. `python loop-craft/scripts/build_loop.py build tests/fixtures/accepted-definition.valid.json build/final-20260722-a` -> artifact and Evidence created (exit 0).
4. The same build command for `build/final-20260722-b` -> artifact and Evidence created (exit 0).
5. Official `quick_validate.py loop-craft` -> `Skill is valid!` (exit 0).
6. Official `quick_validate.py build/final-20260722-a/artifact/skill-polish-loop` -> `Skill is valid!` (exit 0).
7. `build_loop.py verify` on both outputs -> `status: clean`; expected and actual artifact digest were `sha256:23ac2315e146fcb6b278b004fed44e9a4473425147449b348ffefee21939f357` (exit 0).
8. Python snapshot mapping each relative POSIX path to `SHA-256(file raw bytes)` -> 8 files per output; paths and all file digests matched; `byte_identical=True`.
9. `rg -n -i "loopy|loop library" loop-craft build/final-20260722-a/artifact` -> no matches.
10. `git diff --check` -> no output; the worktree was clean before this record update.

## Determinism Snapshot

| Relative path | SHA-256 raw bytes |
|---|---|
| `artifact/skill-polish-loop/SKILL.md` | `e2e6998b83c277c2713b2acd1ce5fa1d13917aac881ad7df97e5d1c1bf974046` |
| `artifact/skill-polish-loop/agents/openai.yaml` | `fcee5a2c65728c960349712ff60ad4c9a61f2f2cb877a14cb1d47c8dbba4959a` |
| `artifact/skill-polish-loop/references/final-execution-ir.json` | `46a740c1a29df99f460b2a8a74238f6a6e4888ee4a2923ca9f62fae9df403b7e` |
| `evidence/accepted-definition.json` | `3ef1a896b03d56d539277eeeba7912827085e6dd0bf4c5c41a34412ff301abf6` |
| `evidence/build-manifest.json` | `cd00fbd18019b396b6731bf2f9ac1335c25c876c45b7baf3424ea7535df877e6` |
| `evidence/final-execution-ir.json` | `46a740c1a29df99f460b2a8a74238f6a6e4888ee4a2923ca9f62fae9df403b7e` |
| `evidence/source-map.json` | `5e2228ea045c13767f0657c95567660a61b2d5724107da1c94335fdfee49f6dd` |
| `evidence/validation-report.json` | `97ba620e9fc2676bd78d49e4d07dbb1ec09fbe086e3a6bb780fb4f82d01b64f1` |

## Manifest Snapshot

- Definition and semantic IR: `sha256:a8242601fb199672b7fe2f2cd4cb5a6ef442c915d4f47a938bd94ed6f64e58e9`.
- Execution IR: `sha256:60ab47f1a8e89b42cd929093b9905091d5561f5f5adb0e0b3772b6a40a58687d`.
- Source Map: `sha256:8b6f57d2c6616fd4bb642d78e1b8bdb1a8dd6f21e2d400528d36c45e5b307bdc`.
- Validation Report: `sha256:63a93bc9c2118af7bf4952e6fa703067f0c68868eb0efbf6cc04c2004b8eab24`.
- Artifact: `sha256:23ac2315e146fcb6b278b004fed44e9a4473425147449b348ffefee21939f357`.
- Override mode: `none`; Adapter: `codex-skill@0.1.0`; Compiler: `0.1.0`.

## Evidence Paths

- Product Skill: `loop-craft/SKILL.md`
- Generated target Skill: `build/final-20260722-a/artifact/skill-polish-loop/SKILL.md`
- Generated metadata: `build/final-20260722-a/artifact/skill-polish-loop/agents/openai.yaml`
- Evidence Package: `build/final-20260722-a/evidence/`
- Independent comparison build: `build/final-20260722-b/`

The ignored `build/` paths are reproducible local evidence, not tracked repository artifacts. This record preserves the tested SHA, commands, digests, and comparison result required to reproduce the gate.

## Review Result

- Final specification review: `Approved`.
- Final global code-quality review: `Approved`; no Critical or Important remained in the final contract-fix scope. Existing deferred Minor items R-007, R-009, R-010, and R-011, plus the R-012 P2 residual, remain tracked.
- Skill Creator Pro authoring principles were applied. The official validator is the compatibility floor; Creator Pro `quality_lint.py` was not available and is not reported as passed.

## Boundary

This record closes only the deterministic Core vertical slice: Accepted Definition -> validated target Skill + Evidence Package + drift verification. It does not claim the three input entries, Runtime, Override, Subloop execution, Library Edition, publication, scheduling, or the deferred real forward behavioral experiment are implemented.
