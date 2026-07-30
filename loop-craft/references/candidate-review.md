# Candidate Review Gate

Use this gate immediately before a Candidate from any Loop Craft entry becomes an accepted definition.

## Resolve only blocking gaps

First inspect the scoped evidence again. Ask one question only when **both** are true:
its answer can change the behavior, authority, verification, stopping rule, or
deliverable; **and** that answer cannot be derived from the scoped evidence, so the
Candidate packet cannot be shown without it. Include:

- what is already known;
- what remains missing or conflicting;
- why it matters;
- the current proposed interpretation.

**Source precedence.** When the user's paraphrase and an unambiguous in-scope
authoritative source disagree, follow the source, continue, and carry the discrepancy as
one explicit note in the Review packet, the delivered Skill, and Entry Evidence.
Escalate to a blocking question only when the source itself is ambiguous or two
same-rank sources conflict.

**Everything else travels in the packet.** Anything that does not block showing the
Candidate is carried into the packet as `proposed` or `missing` under shared review
field 5 and settled by the approval decision. Never queue several questions as
prerequisites to the packet, and never label a non-blocking item a material gap in order
to defer delivery.

Never ask a blank question and never fabricate an answer.

## 0-loop Workflow packet

For a Candidate with no qualifying Loop, show:

- ordered Workflow steps;
- success evidence and its observable acceptance rule;
- failure or stop behavior, including blocked and handoff conditions;
- every must-preserve constraint and its concrete location in `authority`, `workflow.steps`, or `workflow.failure_or_stop`.

Do not invent a feedback cycle or an `invariants` field for a fixed staged Workflow.

## 1-loop bounded Loop packet

For a Candidate with exactly one qualifying Loop, show:

- the Observe → Choose → Act → Verify → Record → Adapt cycle;
- fresh feedback and the acceptance rule;
- terminal states and state / recovery behavior;
- `loops[0].invariants` that every pass must preserve.

## Shared review fields

Show these fields for both packet types:

1. Outcome and use conditions, including the source entry and provenance boundary.
2. Inputs and outputs.
3. Authority: allowed, approval-required, and forbidden actions.
4. Success, stop, and handoff conditions.
5. Inferred or proposed facts that still depend on user judgment. The Loop
   classification itself is never one of them: the Gate has already decided it. State it
   as decided, then ask for approval or one specific correction.

   A schema-required field belongs here when **no scoped evidence supports its value** —
   not merely when the source material lacks the exact wording. Scoped evidence includes the
   source material, the authorization the user stated, and the environment facts they
   supplied. Deriving a value from any of these is transcription, and transcription is never
   fabrication: state the value and cite where it came from. This rule adds no new blocking
   category; the threshold above still governs when to ask.

   Fabrication is supplying a value **no scoped evidence supports** and presenting it as
   settled. The two that must never be fabricated are the **authority** boundary (allowed,
   approval-required, forbidden) and the **acceptance evidence** — they define what the built
   Skill may do and how anyone will know it worked. When neither the source nor the stated
   authorization establishes them, name each as a gap and get the user's answer. Writing an
   unsourced value into field 3 or field 4 does not discharge this: a field can be shown and
   still rest on nothing. A plausible default here is more dangerous than an obvious
   omission, because it survives review unnoticed.

   Note the distinction in scope. Authorization granted to *you* — which directories you may
   read and write while building — is not by itself the authority of the *Skill you are
   building*. Derive the latter from evidence about the Skill's own behavior.
6. Current boundary, including unsupported Loop count or semantic loss, no Runtime, no installation, no publication, no scheduling, and no Library Edition coupling.
7. Approval scope: writing the accepted definition and building the local artifact plus Evidence only.

State whether the Candidate is ready, blocked by a named gap, or classified as a 0-loop Workflow or 1-loop bounded Loop. Ask for approval or one specific correction.

Name each field-5 item so the user can confirm or correct it individually in the same round.
**A single blanket approval never settles an authority boundary or an acceptance rule that no
scoped evidence supports.** If the user approves the packet without answering those, they
remain unanswered; ask again rather than treating silence as assent.

This applies only to values nothing supports. A value derived from scoped evidence is settled
by the packet approval like any other field — do not re-ask for confirmation of something the
user already told you.

## Lock acceptance

After clear approval:

- apply only the approved corrections;
- remove candidate-only provenance labels from the accepted JSON;
- validate against the current accepted-definition schema through the real build command;
- if validation fails, return to this Review Gate with the concrete issue and do not generate an artifact.

Approval applies only to writing the definition and building the local artifact plus Evidence. It does not authorize running, installing, publishing, scheduling, external messaging, or other consequential actions.
