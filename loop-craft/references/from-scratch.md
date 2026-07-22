# From-Scratch Loop Design

Use this path when the user has a goal but no accepted Loop Craft definition. The user should not need to understand or write the JSON schema.

## 1. Recover existing answers

Read the request and only the files or history the user placed in scope. Extract already-known facts before asking anything. Never invent a schedule, metric, tool, budget, owner, permission, or output location.

Track each candidate fact as one of:

- `preserved`: copied without semantic change from user-provided material;
- `normalized`: wording changed without changing meaning;
- `inferred`: supported by the material but not directly stated;
- `proposed`: a design choice awaiting approval;
- `missing`: required and not yet known;
- `conflict`: two scoped sources disagree.

## 2. Interview one question at a time

Start with the highest-value unanswered question. Use everyday language.

1. What are you trying to accomplish?
2. What would a successful result look like?
3. When should this be used?
4. What may it inspect or change, and what is off-limits?
5. What fresh evidence can show whether the last action helped?
6. When must it stop or ask for help?

Do not ask all six when the answer is already known. Each question must include the current understanding and why the missing answer changes the design. Stop asking when remaining uncertainty would not materially change the loop.

## 3. Classify with the shared Loopability Gate

Apply [loopability-gate.md](loopability-gate.md) to the recovered goal. Do not redefine the Gate in this entry.

Preserve a result with no qualifying Loop as a 0-loop Workflow. Preserve exactly one qualifying cycle as a 1-loop bounded Loop. If the result contains multiple independent qualifying Loops or cannot be represented without semantic loss, return the assessment and unsupported boundary without calling the Core.

## 4. Draft the Candidate Behavior Contract

Map the answers to `scripts/loopcraft_core/kernel/schemas/accepted-definition.schema.json` using profile `skill-package-v0.1`.

For both forms include:

- `identity`: stable kebab-case id, readable name, version `0.1.0`, concise description;
- `purpose.outcome`: the user-visible result;
- `applicability`: use and non-use conditions;
- `interface`: named inputs and outputs;
- `authority`: allowed, approval-required, and forbidden actions;
- `capabilities`: required and optional capabilities grounded in known tools.

For a 0-loop Workflow, set `loops` to an empty list and include:

- `workflow.steps`: the bounded ordered behavior;
- `workflow.success_evidence`: observable acceptance evidence;
- `workflow.failure_or_stop`: failure, blocked, approval, and handoff behavior.

Map every must-preserve constraint for a 0-loop Workflow into an existing field: use `authority` for action boundaries, `workflow.steps` for required behavior, or `workflow.failure_or_stop` for stop and handoff constraints. Do not add an `invariants` field to a 0-loop definition.

For a 1-loop bounded Loop, include the same shared fields plus:

- `loops[0].cycle`: observe, choose, act, verify, record, adapt;
- `loops[0].terminal_states`: success, clean no-op, blocked, stagnated, exhausted;
- `loops[0].invariants`: facts and boundaries that every pass must preserve.

Only a 1-loop definition writes `loops[0].invariants`. Do not add unsupported fields or a second Loop.

## 5. Review before writing

Use the shared Candidate Review in [candidate-review.md](candidate-review.md). Resolve material missing or conflict items, then show the packet for the selected 0-loop Workflow or 1-loop bounded Loop. Do not write the accepted definition or create an output directory until the user gives explicit approval.

## 6. Build after approval

Ask for or propose paths inside the authorized workspace for:

- the accepted definition JSON;
- a reviewed Entry Evidence JSON containing only safe source IDs and structured summaries;
- a new output directory that does not exist.

Write the approved `skill-package-v0.1` definition as UTF-8 JSON. Write the reviewed `entry-evidence-v0.1` record described in [core-build.md](core-build.md), with `entry_type: from_scratch` and `source_summary.kind: design_interview`. Both an approved 0-loop Workflow and an approved 1-loop bounded Loop use the same build command from the `loop-craft` directory:

```powershell
python scripts/build_loop.py build <accepted-definition.json> <new-output-directory> --entry-evidence <reviewed-entry-evidence.json>
```

On success, report the generated Skill path and Evidence path. Entry Evidence contains no raw interview, absolute paths, private source material, or development record. Do not run the generated Loop, install it, publish it, or enable a schedule unless the user separately asks and authorizes that action.
