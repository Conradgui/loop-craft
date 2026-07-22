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

## 3. Decide whether a Loop adds value

Require all of the following:

- each pass observes fresh evidence or state;
- that evidence can change the next action;
- verification is observable and repeatable;
- one pass makes one bounded action;
- success, clean no-op, blocked, stagnated, and exhausted can be distinguished;
- the next pass can resume from recorded state.

If feedback cannot change a later action, return a one-shot Workflow and do not call the Core. If the goal contains multiple independent first-class feedback outcomes, explain that the current Demo profile cannot build them without distortion and stop before acceptance.

## 4. Draft the current single-Loop definition

Map the answers to `scripts/loopcraft_core/kernel/schemas/accepted-definition.schema.json`:

- `identity`: stable kebab-case id, readable name, version `0.1.0`, concise description;
- `purpose.outcome`: the user-visible result;
- `applicability`: use and non-use conditions;
- `interface`: named inputs and outputs;
- `authority`: allowed, approval-required, and forbidden actions;
- `capabilities`: required and optional capabilities grounded in known tools;
- `loops[0].cycle`: observe, choose, act, verify, record, adapt;
- `loops[0].terminal_states`: success, clean no-op, blocked, stagnated, exhausted;
- `loops[0].invariants`: facts and boundaries that every pass must preserve.

Use profile `core-slice-v0.1`. Do not add unsupported fields or a second Loop.

## 5. Review before writing

Read [candidate-review.md](candidate-review.md). Resolve material missing or conflict items, then show the compact review packet. Do not write the accepted definition or create an output directory until the user approves the candidate.

## 6. Build after approval

Ask for or propose paths inside the authorized workspace for:

- the accepted definition JSON;
- a new output directory that does not exist.

Write the approved definition as UTF-8 JSON. From the `loop-craft` directory run:

```powershell
python scripts/build_loop.py build <accepted-definition.json> <new-output-directory>
```

On success, report the generated Skill path and Evidence path. Do not run the generated Loop, install it, publish it, or enable a schedule unless the user separately asks and authorizes that action.
