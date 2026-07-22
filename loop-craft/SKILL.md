---
name: loop-craft
description: Use when a user wants to design one bounded feedback loop from a goal, assess or upgrade an existing Agent Skill with feedback loops, build an accepted Loop Craft JSON definition, or check an existing Loop Craft build for artifact drift.
---

# Loop Craft

Route the request into one of the supported paths below. Keep the interview and review conversational; use the deterministic Core only after the definition is accepted.

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
- Build only when the approved design passes the current Core compatibility gate. Otherwise return the Assessment without compressing the design into the single-Loop profile.
- The deliverable remains a complete discoverable Skill, not a standalone Loop fragment.

## Accepted definition build or drift verification

Read [references/core-build.md](references/core-build.md) before running a command.

- Build only from an accepted JSON definition into a new output directory.
- Verify only an existing build produced by the build command.
- Stop when an input is missing, invalid, the wrong kind, or outside the selected operation. Do not guess a replacement input or alter an existing build during verification.

## Current boundary

This version supports From-scratch single-Loop design, existing-Skill assessment with a narrowly gated single-Loop upgrade, accepted-definition builds, and drift verification. Conversation Distillation and multi-Loop builds are not yet supported. State that boundary when it affects the request instead of silently approximating support.
