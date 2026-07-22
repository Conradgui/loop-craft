# Shared Entry Gate and From-Scratch Packaging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make all three Loop Craft entries use one seven-item Loopability Gate and route approved From-scratch zero-Loop and one-Loop candidates through the existing Skill Packaging profile without claiming that every entry produces the same artifact form.

**Architecture:** Add one runtime reference as the sole Gate owner. Keep entry references responsible for source-specific extraction, classification, and mapping: From-scratch and Conversation zero-Loop candidates may produce ordinary Skills, Existing Skill `keep_as_skill` remains Assessment only, and approved Existing Skill one-Loop upgrades use the source-preserving overlay. Reuse the shared Gate, Review, Compiler, and Adapter contracts while keeping the existing Compiler and Codex Skill Adapter unchanged.

**Tech Stack:** Markdown Agent Skill contracts, existing Python packaging pipeline, pytest static integration checks.

---

### Task 1: Lock the shared behavior contract

**Files:**
- Create: `loop-craft/references/loopability-gate.md`
- Modify: `loop-craft/references/from-scratch.md`
- Modify: `loop-craft/references/upgrade-skill.md`
- Modify: `loop-craft/references/from-conversation.md`
- Modify: `loop-craft/references/candidate-review.md`
- Modify: `loop-craft/SKILL.md`
- Modify: `tests/integration/test_loop_craft_skill.py`

- [x] Add failing assertions that all three entries link to the same Gate owner, From-scratch supports approved zero-Loop Workflow packaging, and the Candidate Review distinguishes Workflow from Loop review.
- [x] Run `python -m pytest tests/integration/test_loop_craft_skill.py -q` and confirm the new assertions fail for the missing shared contract.
- [x] Add the exact seven-item Gate and its 0 / 1 / more-than-1 classification to `loopability-gate.md`.
- [x] Replace entry-local Gate definitions with direct links to the shared owner.
- [x] Route From-scratch zero-Loop Workflow and one-Loop candidates through `skill-package-v0.1` after the shared approval gate.
- [x] Keep Existing Skill `keep_as_skill` at Assessment only; do not manufacture a zero-Loop upgrade merely to make entry outputs uniform.
- [x] Keep unsupported multi-Loop candidates at assessment without semantic compression.
- [x] Run the same integration test and confirm it passes.

### Task 2: Close the module without broad testing

**Files:**
- Modify: `docs/project-management/decision-log.md`
- Modify: `docs/project-management/progress-log.md`
- Do not modify: `dashboard/status.json` (the controller updates it only after independent review)

- [x] Record the single-owner Gate decision and exact scope boundary.
- [x] Leave the dashboard unchanged for the controller to update after independent review.
- [x] Run `tests/integration/test_loop_craft_skill.py` plus one existing real zero-Loop Packaging build test; Packaging Python is unchanged, so do not run all nine adapter tests.
- [x] Run `git diff --check` and self-review the scoped contract changes.
- [x] Leave independent quality review to the controller's assigned reviewer; do not duplicate multiple reviewer rounds in this implementation task.
