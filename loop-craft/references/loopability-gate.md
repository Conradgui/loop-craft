# Loopability Gate

This file is the single owner of the Loopability Gate used by From-scratch Design, Existing Skill Upgrade, and Conversation Distillation. Entry references recover source-specific evidence and map the result, but they must not redefine this gate.

## Apply all seven checks

A candidate qualifies as a Loop only when all are true:

1. A pass produces fresh evidence or changed state.
2. That feedback can change the next selected action.
3. An observable, repeatable check judges progress or acceptance.
4. Each pass takes one bounded action without widening authority.
5. Success, clean no-op, blocked, approval-required, and no-progress states are distinguishable when relevant.
6. Iteration adds value beyond a one-shot or fixed staged workflow.
7. State needed by the next pass can be recorded, with explicit recovery or handoff after interruption or side effects.

A missing material verifier or evidence source is a blocked finding. Never substitute model confidence, invent a return edge, or treat a multi-step checklist as recurrence.

## 0 qualifying Loops

Preserve the behavior as a Workflow. After Candidate Review and explicit approval, an entry that supports ordinary Skill creation may build the approved 0-loop Workflow with profile `skill-package-v0.1`, including `workflow.steps`, `success_evidence`, and `failure_or_stop`.

This classification does not force every entry to build an artifact. In particular, Existing Skill Upgrade retains the `keep_as_skill` Assessment verdict rather than manufacturing a meaningless zero-Loop replacement.

## Exactly 1 qualifying Loop

Preserve the candidate as one bounded Loop. After Candidate Review and explicit approval, a compatible 1-loop definition may build with the same `skill-package-v0.1` profile. Entry-specific compatibility rules still apply: a From-scratch or Conversation candidate can use the ordinary packaging route, while an Existing Skill upgrade uses the reviewed source-preserving overlay.

## More than 1 qualifying Loop or semantic loss

Return **Assessment only** with the unsupported boundary. Do not compress independent Loops, discard behavior, or call the Core when the approved contract cannot be represented without semantic loss.
