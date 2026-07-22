# Entry Evidence Binding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bind the three entries' approved source summary, clarifications, Candidate Review, and user approval into deterministic Evidence without placing raw source material in the generated Skill.

**Architecture:** Accept one reviewed `entry-evidence.json` as an optional build input. Validate its exact structure and accepted-definition binding, copy it into Evidence, bind its digest and entry type in Build Manifest, and let `verify` derive the allowed Evidence file set from independent Manifest bindings. The caller supplies summaries rather than raw source; validation does not prove that free-text summaries are true or fully de-identified.

**Tech Stack:** Python 3.12+, JSON Schema Draft 2020-12, existing canonical JSON and pytest infrastructure.

---

### Task 1: Define and validate Entry Evidence

**Files:**
- Create: `loop-craft/scripts/loopcraft_core/kernel/schemas/entry-evidence.schema.json`
- Create: `loop-craft/scripts/loopcraft_core/evidence/entry.py`
- Create: `tests/fixtures/entry-evidence.valid.json`
- Create or modify: focused Entry Evidence tests under `tests/unit/`

- [x] Write a focused risk matrix for the three entry types, accepted-definition digest and Loop-count consistency, exact object shape, resolved non-empty clarifications, links/junctions, and absolute local path rejection.
- [x] Add schema version `entry-evidence-v0.1` with `entry_type` values `from_scratch`, `existing_skill`, and `conversation`.
- [x] Use exactly seven root fields: `schema_version`, `entry_type`, `definition_digest`, `source_summary`, `clarifications`, `candidate_review`, and `approval`.
- [x] Define `source_summary` as `kind` (`design_interview`, `skill_assessment`, or `workflow_model`), a non-empty safe `source_ids` list, a bounded `summary`, and provenance-labelled `facts`; require entry type and summary kind to match.
- [x] Allow `clarifications: []`; each present record contains only bounded `question_summary`, `answer_summary`, and `resolution: resolved`.
- [x] Define Candidate Review as a bounded `summary` plus classification `zero_loop_workflow` or `one_loop_bounded_loop`, and require the classification to match the accepted definition's 0/1 Loop count.
- [x] Keep approval to `status: approved` and fixed `scope: local_artifact_and_evidence_build`; do not add identity or time fields. The root definition digest binds the record to the approved definition but is not identity authentication.
- [x] Reject extra/raw source payload fields, absolute Windows/POSIX/UNC paths, malformed digests, unapproved records, and definition digest mismatch. State explicitly that structural validation cannot prove summary truth or complete de-identification; do not add PII scanning.

### Task 2: Bind Entry Evidence through build and verify

**Files:**
- Modify: `loop-craft/scripts/build_loop.py`
- Modify: `loop-craft/scripts/loopcraft_core/pipeline.py`
- Modify: `loop-craft/scripts/loopcraft_core/evidence/package.py`
- Modify: focused pipeline/evidence tests under `tests/integration/` and `tests/unit/`

- [x] Add focused failing tests for `build --entry-evidence`, Manifest `entry_evidence_digest` and `entry_type`, clean verify, tampered/missing Evidence, source-package plus entry-evidence composition, and backward compatibility.
- [x] Load and validate the reviewed input before output creation; never write it into Artifact.
- [x] Write canonical `entry-evidence.json` into Evidence and bind its digest plus entry type in Build Manifest.
- [x] Treat source-package and entry-evidence as orthogonal contracts: source binding proves which source package bytes were preserved; entry binding records why the behavior was accepted. Neither duplicates or requires the other.
- [x] In `verify`, require each binding's complete Manifest field group and derive `expected files = base union source binding file union entry binding file`; do not add hard-coded 5/6/7-file branches.
- [x] Keep builds without Entry Evidence backward compatible.

### Task 3: Connect the Skill contract and close the module

**Files:**
- Modify: `loop-craft/SKILL.md`
- Modify: `loop-craft/references/from-scratch.md`
- Modify: `loop-craft/references/upgrade-skill.md`
- Modify: `loop-craft/references/from-conversation.md`
- Modify: `loop-craft/references/core-build.md`
- Modify: `tests/integration/test_loop_craft_skill.py`
- Modify: `docs/project-management/decision-log.md`
- Modify: `docs/project-management/progress-log.md`
- Controller-only after approval: `dashboard/status.json`

- [x] Route all three approved entry builds through `--entry-evidence`; remove the Conversation-only `manifest-unbound` supplemental route.
- [x] State that raw conversations, absolute paths, private source material, and development records never enter Artifact or Entry Evidence.
- [x] Run only Entry Evidence unit/integration tests, the entry Skill contract test, one source+entry composition build, official Skill validator, and `git diff --check`.
- [x] Request one independent quality review. Dashboard update remains controller-only after approval.

## Explicit Non-goals

- Do not capture raw conversations or copy source documents.
- Do not add Runtime, multi-Loop, Compact Prompt, Library Edition, publication, or installation behavior.
- Do not make Entry Evidence mandatory for historical accepted-definition-only builds.
- Do not repair the five unrelated drift error-message assertions in this module.
