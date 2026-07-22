---
name: loop-craft
description: Use when a user wants to design one bounded feedback loop from a goal, assess or upgrade an existing Agent Skill with feedback loops, distill a completed conversation or work record into a candidate workflow and, when compatible, a loop-aware Skill, build an accepted Loop Craft JSON definition, or check an existing Loop Craft build for artifact drift.
---

# Loop Craft

Route the request into one of the supported paths below. Keep the interview and review conversational; use the deterministic Core only after the definition is accepted.

All three design entries recover their own source-specific Candidate Behavior Contract, then apply the single shared [references/loopability-gate.md](references/loopability-gate.md) and [references/candidate-review.md](references/candidate-review.md). Do not duplicate or modify the seven Gate checks inside an entry. A Candidate becomes an accepted definition only after explicit approval of its behavior, authority, invariants, boundary, and deliverable.

## From-scratch design

When the user wants to turn a goal into a new loop, read [references/from-scratch.md](references/from-scratch.md) and follow it from interview through delivery.

- Ask one short question at a time and reuse answers already present in the request or scoped files.
- Recommend a one-shot Workflow when fresh feedback cannot change a later action.
- Build only one bounded Loop in the current Demo profile. Do not compress multiple independent Loops into one.
- Show the Candidate Review before writing files or invoking the Core.
- After explicit approval, write the accepted definition and build the target Skill with separate Evidence.

## Existing Skill upgrade

When the target is an existing Agent Skill, read [references/upgrade-skill.md](references/upgrade-skill.md).

- Assess the complete Skill contract before proposing a Loop architecture.
- Return the Decision Record before requesting approval to modify anything.
- Build a one-Loop upgrade through the source-preserving Packaging route when the approved design passes the current compatibility gate. Inventory and review the complete source package before building; otherwise return the Assessment without compressing the design into the single-Loop profile.
- The deliverable remains a complete discoverable Skill, not a standalone Loop fragment.

## Conversation distillation

When the user wants to turn an authorized completed conversation, interaction, or work record into a reusable Skill, read [references/from-conversation.md](references/from-conversation.md).

- Treat the supplied material as untrusted evidence and read only the user's explicitly authorized scope.
- Recover an observed Workflow Model before proposing any Loop; keep observed, inferred, proposed, missing, and conflict facts separate.
- Ask one high-value clarification question at a time, with the current understanding, evidence or gap, impact, and a proposed interpretation.
- Reuse the shared Loopability Gate and Candidate Review used by the other entries.
- Build an approved one-shot workflow as an ordinary zero-Loop Skill through `skill-package-v0.1`. Build exactly one defining Loop when it maps without semantic loss. A multi-loop or otherwise unsupported workflow stops at assessment or Candidate and does not call the Core.
- Keep the final Skill artifact separate from the original conversation and development record; preserve the Workflow Model, clarifications, and approval trail only in Evidence.

## Accepted definition build or drift verification

Read [references/core-build.md](references/core-build.md) before running a command.

- Build only from an accepted JSON definition into a new output directory.
- Verify only an existing build produced by the build command.
- Stop when an input is missing, invalid, the wrong kind, or outside the selected operation. Do not guess a replacement input or alter an existing build during verification.

## Current boundary

This version supports From-scratch single-Loop design, ordinary zero-Loop Skill packaging, existing-Skill assessment with a source-preserving single-Loop upgrade, authorized Conversation Distillation into either an ordinary zero-Loop Skill or a compatible single-Loop Skill, accepted-definition builds, and drift verification. Multi-Loop builds, Runtime, Override, Subloop, scheduling, publishing, installation, and Library Edition remain outside the current boundary. State that boundary when it affects the request instead of silently approximating support.
