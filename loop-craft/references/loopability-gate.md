# Loopability Gate

This file is the single owner of the Loopability Gate used by From-scratch Design, Existing Skill Upgrade, and Conversation Distillation. Entry references recover source-specific evidence and map the result, but they must not redefine this gate.

## Count independent cycles first

Before scoring any candidate, count the independent revision cycles in the recovered
model. Cycles are independent when they have different owners or reviewers, different
scope, or different acceptance targets.

When two or more independent cycles are present, classify the result as multi-Loop
unsupported, return **Assessment only**, and stop. Do not score the seven checks per
candidate in order to reach a buildable shape, and do not make a clarification question
a precondition for returning that assessment.

Thin evidence inside an individual cycle is not grounds for re-counting several
independent cycles as one staged Workflow. The response to thin evidence is an
assessment plus the named evidence gap — never a reshaped deliverable that happens to
fit the at-most-one-Loop boundary.

## Apply all seven checks

A candidate qualifies as a Loop only when all are true:

1. A pass produces fresh evidence or changed state.
2. That feedback can change the next selected action.
3. An observable, repeatable check judges progress or acceptance. A target-owned
   acceptance judgement — a user, reviewer, or named role accepting or rejecting a
   presented draft — is such a check when the design states when the draft is presented
   and what ends the cycle. Only model self-confidence is disqualified. Score this check
   against the acceptance owner named in the authorized record, not against whoever
   happens to be available when the built Skill later runs.
4. Each pass takes one bounded action without widening authority.
5. Success, clean no-op, blocked, approval-required, and no-progress states are distinguishable when relevant.
6. Iteration adds value beyond a one-shot or fixed staged workflow. A bounded iteration
   budget qualifies, including a budget of exactly one. Count the passes the design
   actually admits: a cycle known to stop after N passes is an N-bounded Loop with a
   minimum of 1, never 0. This check asks whether an *additional* pass would add value;
   it never removes the pass that already exists. Anchor the count on the decision being
   revised, not on the item flowing through it.
7. State needed by the next pass can be recorded, with explicit recovery or handoff after interruption or side effects.

A missing material verifier or evidence source is a blocked finding — never a downgrade
to Workflow. Never substitute model confidence, invent a return edge, or treat a
multi-step checklist as recurrence.

Conversely, a correction round already present in the authorized record — a boundary
case raised, a rule revised, the revision folded back into the process — is an observed
return edge, not an invented one. Encode it as the Loop's verify-to-adapt edge; do not
flatten it into a static Workflow step merely because it happened once or at design time.

Two further flattening arguments are closed. A source stating that the observed round is
the final or the only round sets the iteration budget to 1; it does not reduce the Loop
count to 0. And the acceptance owner named in the authorized record remains the Loop's
verifier: that this owner is not present when the built Skill later runs is a blocked
finding at most, never grounds for re-classifying the candidate as a 0-loop Workflow.

The Loop count may only be reduced to 0 by a named failed check from the seven above.
Any other reason for reaching 0 is a flattening argument this gate does not grant.

## 0 qualifying Loops

Preserve the behavior as a Workflow. After Candidate Review and explicit approval, an entry that supports ordinary Skill creation may build the approved 0-loop Workflow with profile `skill-package-v0.1`, including `workflow.steps`, `success_evidence`, and `failure_or_stop`.

This classification does not force every entry to build an artifact. In particular, Existing Skill Upgrade retains the `keep_as_skill` Assessment verdict rather than manufacturing a meaningless zero-Loop replacement.

Before returning `keep_as_skill`, name which of the seven checks the candidate failed and
why the user's requested change does not supply it. A verdict that cannot point at a
specific failed check is a defensive fallback, not a finding.

## Exactly 1 qualifying Loop

Preserve the candidate as one bounded Loop. After Candidate Review and explicit approval, a compatible 1-loop definition may build with the same `skill-package-v0.1` profile. Entry-specific compatibility rules still apply: a From-scratch or Conversation candidate can use the ordinary packaging route, while an Existing Skill upgrade uses the reviewed source-preserving overlay.

## More than 1 qualifying Loop or semantic loss

Return **Assessment only** with the unsupported boundary. Do not compress independent Loops, discard behavior, or call the Core when the approved contract cannot be represented without semantic loss.
