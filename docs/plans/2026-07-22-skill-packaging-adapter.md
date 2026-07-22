# Skill Packaging Adapter Walking Skeleton

## Objective

Deliver complete Codex Skill packages for two currently blocked cases:

1. an approved zero-Loop workflow that should remain an ordinary Skill;
2. an approved one-Loop upgrade that must preserve an existing Skill package.

## Input Contract

- Keep `core-slice-v0.1` unchanged at exactly one Loop.
- Add `skill-package-v0.1` with zero or one Loop.
- A zero-Loop definition requires `workflow.steps`, `success_evidence`, and
  `failure_or_stop` in the Behavior Contract.
- An existing package build requires a reviewed source-package manifest whose
  relative paths, actions, and file digests still match the source Skill.

## Packaging Behavior

- New zero-Loop Skill: deterministically generate `SKILL.md`, Codex metadata,
  and the Final Execution IR reference from the accepted definition.
- Existing one-Loop Skill: preserve the source package byte-for-byte, overlay
  a deterministic feedback-loop section in `SKILL.md`, and replace only the
  generated Final Execution IR reference.
- Inventory actions are `preserve`, `overlay`, or `generated`; unresolved or
  unknown root entries stop before build.
- Accept only standard Skill package roots and regular in-root files. Reject
  links, path escape, source/output overlap, stale digests, and collisions.

## Evidence

- Write `source-package-manifest.json` only for source-package builds.
- Bind its digest in `build-manifest.json`.
- Extend `verify` to validate the optional manifest and its digest.
- Keep source absolute paths out of Final IR, Evidence, and artifacts.

## Focused Verification

- Build and validate one zero-Loop ordinary Skill.
- Inventory, build, and validate one existing Skill containing metadata,
  references, scripts, assets, and license material.
- Confirm source bytes are unchanged, approved resources are preserved, and a
  stale manifest or link is rejected.
- Do not run unrelated full-suite or forward behavioral tests in this stage.
