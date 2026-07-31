# Loop Craft 0.3.0 Fresh-Context Product Interface Audit

## Role

You are a fresh Codex Agent with no knowledge of the Loop Craft development project. Audit only
the installed Skill in your current working directory. Read `SKILL.md` and only the references
it routes you to. Do not read the parent directory, any development repository, tests, fixtures,
plans, dashboard, prior conversations, or evaluation oracle.

This is a read-only reasoning audit. Do not run Core commands, do not create or modify any file,
do not execute a real user project, and do not install, publish, or schedule anything. Your
output is only a structured trace of what you would do.

## Product question

Can an Agent that receives this Skill cold determine the correct route, legal inputs, module
owner, output, next consumer, approval or stop boundary, and user-facing next step without hidden
project knowledge or asking the user to manufacture internal JSON?

## Neutral route requests

Trace all six independently:

1. **from_scratch** — “Use Loop Craft to turn my goal into a local Skill. I know the outcome but
   have not designed the workflow yet.”
2. **existing_skill** — “Assess this complete existing Agent Skill and, if one bounded feedback
   Loop fits without semantic loss, prepare an upgraded local Skill while preserving its package.”
3. **conversation** — “Distill this authorized completed conversation into a reusable local Skill;
   it may honestly be a one-shot Workflow.”
4. **direct_build** — “This JSON or prose Definition is already approved. Build it locally with
   separate evidence; do not redesign it.”
5. **verify** — “Check this existing Loop Craft build for drift without repairing or rebuilding it.”
6. **multi_loop_refusal** — “This process has two independent feedback cycles. Package both into
   the current Loop Craft output.”

Do not invent concrete user answers or files. When a route needs a real input, approval, evidence,
or path, state what must be requested and stop at that boundary.

## Required trace

For every route, follow only instructions reachable from the installed Skill and report:

- why Router selects that owner;
- each module step's `input`, `owner`, `output`, `next_consumer`,
  `approval_or_stop`, `boundary`, and `user_facing_next_step`;
- which fields can be transcribed from scoped evidence and which require a user answer;
- what may be written before and after approval;
- terminal state for success, approval-required, blocked, unsupported, clean, or drifted;
- whether Artifact, Evidence, and raw source remain separated.

## Four hard gates

Set the overall verdict to PASS only when all are true:

1. **interfaces_connected** — every output is a legal downstream input; no orphan state or hidden
   conversion exists;
2. **boundaries_rigorous** — source scope, authority, privacy, Loop count, package/link boundary,
   approval, and stops have explicit owners;
3. **handoffs_fluent** — the user is not asked twice, is not asked to hand-author internal JSON,
   and receives a clear next action at every stop;
4. **usable_cold** — a fresh Agent can reach delivery or the correct stop using only the installed
   Skill.

If any route fails any gate, return DRIFT and name the smallest concrete interface gap. Do not
give implementation advice beyond identifying that gap.
