# Candidate Review Gate

Use this gate immediately before a Candidate from any Loop Craft entry becomes an accepted definition.

## Resolve only material gaps

First inspect the scoped evidence again. Ask one question only when its answer can change the behavior, authority, verification, stopping rule, or deliverable. Include:

- what is already known;
- what remains missing or conflicting;
- why it matters;
- the current proposed interpretation.

Never ask a blank question and never fabricate an answer.

## 0-loop Workflow packet

For a Candidate with no qualifying Loop, show:

- ordered Workflow steps;
- success evidence and its observable acceptance rule;
- failure or stop behavior, including blocked and handoff conditions.

Do not invent a feedback cycle for a fixed staged Workflow.

## 1-loop bounded Loop packet

For a Candidate with exactly one qualifying Loop, show:

- the Observe → Choose → Act → Verify → Record → Adapt cycle;
- fresh feedback and the acceptance rule;
- terminal states and state / recovery behavior.

## Shared review fields

Show these fields for both packet types:

1. Outcome and use conditions, including the source entry and provenance boundary.
2. Inputs and outputs.
3. Authority: allowed, approval-required, and forbidden actions.
4. Invariants that the Workflow or Loop must preserve.
5. Success, stop, and handoff conditions.
6. Inferred or proposed facts that still depend on user judgment.
7. Current boundary, including unsupported Loop count or semantic loss, no Runtime, no installation, no publication, no scheduling, and no Library Edition coupling.
8. Approval scope: writing the accepted definition and building the local artifact plus Evidence only.

State whether the Candidate is ready, blocked by a named gap, or classified as a 0-loop Workflow or 1-loop bounded Loop. Ask for approval or one specific correction.

## Lock acceptance

After clear approval:

- apply only the approved corrections;
- remove candidate-only provenance labels from the accepted JSON;
- validate against the current accepted-definition schema through the real build command;
- if validation fails, return to this Review Gate with the concrete issue and do not generate an artifact.

Approval applies only to writing the definition and building the local artifact plus Evidence. It does not authorize running, installing, publishing, scheduling, external messaging, or other consequential actions.
