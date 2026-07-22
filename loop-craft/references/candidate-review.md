# Candidate Review Gate

Use this gate immediately before a Candidate from any Loop Craft entry becomes an accepted definition.

## Resolve only material gaps

First inspect the scoped evidence again. Ask one question only when its answer can change the behavior, authority, verification, stopping rule, or deliverable. Include:

- what is already known;
- what remains missing or conflicting;
- why it matters;
- the current proposed interpretation.

Never ask a blank question and never fabricate an answer.

## Present the review packet

Show a compact review with these sections:

1. Outcome and use conditions, including the source entry and provenance boundary.
2. Inputs and outputs.
3. Observe → Choose → Act → Verify → Record → Adapt.
4. Success and stop conditions.
5. Allowed, approval-required, and forbidden actions.
6. Invariants.
7. Inferred or proposed facts that still depend on user judgment.
8. Current boundary: one Loop, no Runtime, no installation, no publication, no scheduling, and no Library Edition coupling.

State whether the Candidate is ready, blocked by a named gap, or better represented as a one-shot Workflow. Ask for approval or one specific correction.

## Lock acceptance

After clear approval:

- apply only the approved corrections;
- remove candidate-only provenance labels from the accepted JSON;
- validate against the current accepted-definition schema through the real build command;
- if validation fails, return to this Review Gate with the concrete issue and do not generate an artifact.

Approval applies only to writing the definition and building the local artifact plus Evidence. It does not authorize running, installing, publishing, scheduling, external messaging, or other consequential actions.
