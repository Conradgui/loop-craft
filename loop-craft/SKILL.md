---
name: loop-craft
description: Use when a user wants to design one bounded feedback loop from a goal and build it into an Agent Skill, when an accepted Loop Craft JSON definition must be built, or when an existing Loop Craft build must be checked for artifact drift.
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

## Accepted definition build or drift verification

Read [references/core-build.md](references/core-build.md) before running a command.

- Build only from an accepted JSON definition into a new output directory.
- Verify only an existing build produced by the build command.
- Stop when an input is missing, invalid, the wrong kind, or outside the selected operation. Do not guess a replacement input or alter an existing build during verification.

## Current boundary

This version supports the From-scratch single-Loop Demo, accepted-definition builds, and drift verification. It does not yet expose Skill Upgrade, Conversation Distillation, multiple Loops, Runtime, or Library Edition. State that boundary when it affects the request instead of silently approximating support.
