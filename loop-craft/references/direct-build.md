# Direct Definition Build

Use this path only when the user already has an accepted definition and wants a local Artifact plus separate Evidence. The accepted material may be an approved JSON definition or an approved prose definition. This route is a provenance-preserving build operation, not behavior design.

## 1. Confirm that the material is accepted

The request must identify the supplied behavior as final, accepted, or otherwise approved for this build. If approval is ambiguous, ask for confirmation before writing either the definition or Entry Evidence.

Do not run the Loopability Gate or Candidate Review on already accepted material. Do not fabricate a Candidate Review to satisfy an evidence shape. If the user is still asking what the behavior should be, wants a review or optimization, or supplies only a goal, route to From-scratch, Existing Skill, or Conversation Distillation as appropriate.

## 2. Validate JSON or transcribe prose

For approved JSON, read it as untrusted input and validate it against `scripts/loopcraft_core/kernel/schemas/accepted-definition.schema.json`. Do not repair malformed JSON or silently change a valid definition.

For approved prose, map only facts supported by that prose into `skill-package-v0.1`. Normalizing wording and syntax is allowed; choosing new behavior is not. A missing field is blocking when it changes authority, verification, stop conditions, or the deliverable. Identity, applicability, inputs, outputs, capabilities, workflow steps or Loop cycle, and terminal behavior must also be representable without guessing.

Ask one blocking question at a time, state the supported interpretation and the consequence of the gap, and record only the resolved summary. If a required field remains unsupported, stop before writing files. Do not substitute defaults, compress multiple Loops, or turn an unsupported definition into an approximate build.

## 3. Create truthful Direct Build Entry Evidence

After the definition is valid, prepare an `entry-evidence-v0.2` record with exactly the shared seven root fields and these Direct Build values:

- `entry_type: direct_build`;
- `source_summary.kind: accepted_definition`;
- controlled `source_ids`, a bounded source summary, and provenance-labelled fact summaries;
- only resolved clarification summaries, which may be an empty list;
- `candidate_review: null`;
- `approval.status: approved` and `approval.scope: local_artifact_and_evidence_build`;
- the canonical `definition_digest` of the accepted definition.

Do not fabricate a Candidate Review. Entry Evidence must not contain the full prose or JSON source, raw conversation, private material, absolute local paths, or development records. It records why this exact definition is authorized for the local build; it is not a copy of the definition.

## 4. Review the mapping and build

Show the user the accepted definition mapping, the bounded Entry Evidence summary, and the proposed new output path. Obtain explicit approval for the local Artifact and Evidence build if it was not already given for those exact inputs and path.

Write the accepted definition and Direct Build Entry Evidence only inside the authorized workspace. From the `loop-craft` directory, run:

```powershell
python scripts/build_loop.py build <accepted-definition.json> <new-output-directory> --entry-evidence <direct-build-entry-evidence.json>
```

The output directory must not already exist. This route does not take a source Skill package; a request to preserve and upgrade an existing package belongs to Existing Skill Upgrade.

## 5. Deliver or stop

On success, report the generated Skill path, Evidence path, and the fact that no Candidate Review occurred on this route. Do not run, install, publish, schedule, or otherwise activate the generated Skill without separate authorization.

On validation, approval, path, or Core failure, report the precise stop reason and the next user-facing action. Do not switch routes silently, overwrite an output, or weaken a boundary to obtain a build.
