# Contributing to Loop Craft

This project has an unusual property: **most of the product is prose.** The Python is a
deterministic build chain that can be unit-tested; the actual user-facing behavior — routing,
classification, when to ask, when to stop — lives in `loop-craft/SKILL.md` and
`loop-craft/references/*.md`.

That changes how you contribute. A green test suite proves nothing about a prompt change.

## Before you start

Read [`AGENTS.md`](AGENTS.md). It is the project's operating contract and it takes precedence
over this file. Then read [`docs/DESIGN.md`](docs/DESIGN.md) for the architecture and
[`docs/project-management/decision-log.md`](docs/project-management/decision-log.md) for why
things are the way they are — several obvious-looking simplifications were tried and
reverted, and the reasons are recorded.

## Setup

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
```

Requires Python 3.12+ and `jsonschema`. On a non-UTF-8 locale (common on Windows), set
`PYTHONUTF8=1` before running the official Skill validator — generated Skills may contain
non-ASCII text and the upstream validator reads files without an explicit encoding.

## The one rule that matters most

> **Does a user now do something they could not do before?**

If the answer is only "there is a new schema, module, test, or governance record", the change
is not a product milestone and must not be described as one. This project previously spent
several days growing test counts while the end-to-end user path stayed at zero. The whole
governance apparatus exists to prevent a repeat.

## Which change needs which evidence

| You changed | Required evidence |
|---|---|
| Python under `loop-craft/scripts/` | `pytest -q`, plus a real `build` + `verify` if the build chain is touched |
| A JSON schema | Meta-validation, plus regression on both the 0-Loop and 1-Loop fixtures |
| One entry reference only | Targeted behavioral cases for that entry |
| **A shared file** — the Gate, Candidate Review, or a schema | **Full behavioral evaluation.** All three entries change at once. |
| Docs, dashboard, comments | Minimal static checks only. Do not run the suite. |

The last row is a real rule, not laziness. See the budget section.

### Behavioral evaluation

Prompt changes are verified by running blind cases through fresh-context agents and grading
against a hidden oracle. The isolation rules are not optional:

- one sandbox per case, materials placed at their declared paths;
- the oracle and the task briefing live **outside** the sandbox tree;
- the runner may read the Skill directory and its own sandbox — **not** the parent repo,
  which contains tests, fixtures, and development docs that leak expected answers;
- the runner is never told it is being tested, never sees another case, never sees a rubric;
- grading inspects the filesystem, not the model's self-report. "I stopped for approval" is
  checked against whether the output directory is actually empty.

Method and results: [`docs/REAL_WORLD_EVALUATION.md`](docs/REAL_WORLD_EVALUATION.md).

### Relaxing a stopping condition

If your change makes the Skill stop *less* often, you must add a case whose correct answer is
to stop, **before** making the change. Otherwise the evaluation cannot tell the difference
between fixing over-blocking and creating over-building. This has already bitten once and is
recorded as `R-023`.

## Test and review budget

```text
test/review tokens : development tokens  ≤  1 : 2.5
```

This is a **ceiling, not a target**. The default budget is zero. Increased development effort
does not earn a test allowance that must be spent.

Before writing or running anything, answer: *which real failure does this catch, and would the
result change what ships?* If you cannot answer, do not run it.

Do not re-run passing tests because a milestone was reached. Do not add tests to approach the
ratio. Do not harden a component no entry calls yet.

## Task layering

Every task belongs to exactly one layer:

- **mainline** — directly increases user capability. Only one active at a time.
- **validation** — verifies a risk in the mainline work just completed. Never runs standalone.
- **support** — dashboard, docs, governance. Never blocks or preempts mainline, and never
  counts toward product progress.
- **not_now** — Runtime, Override, Subloop, Library Edition, publishing, multi-platform.

## Changing the Skill's prose

- `references/loopability-gate.md` is the **single owner** of the seven checks. Entries link
  to it. Never restate or locally amend the Gate inside an entry.
- Keep the boundary honest. If a capability is unsupported, say so plainly rather than
  approximating it.
- Do not weaken the anti-fabrication rules to make a case pass. "The Skill may invent a
  verifier when one is missing" is never the right fix; a missing verifier is a blocked
  finding.
- Enumerating forbidden arguments one at a time tends to fail — a rephrased version gets
  through. Prefer inverting the default: state what *is* permitted and treat everything else
  as not granted.

## Commits and records

- Commit messages: `feat:`, `fix:`, `test:`, `docs:`, `chore:`.
- Any architecture decision, trade-off, or rejected alternative goes in `decision-log.md`
  with the evidence that settled it.
- `progress-log.md` records **executed actions and observed evidence only.** Planned steps,
  expected outputs, and template text are not progress.
- Update `dashboard/status.json` in the same batch as the change it reflects. `delivered` may
  only list capabilities that actually exist and are reachable from a user entry.
- Platform `429`/`403`/quota failures are not product defects. Retry or route around them;
  never write them into governance records.

## Pull requests

State what a user can now do, which evidence you ran, what you deliberately did not run and
why, and any boundary that is still unsupported. CI runs the suite, schema meta-validation,
the official Skill validator, link checking, a real build/verify, and a drift negative case
on Linux and Windows across Python 3.12 and 3.13.

CI does not cover behavioral evaluation. If you touched prose, say so and attach results.

## Security reports

Do not open a public Issue for a suspected vulnerability, authority-boundary bypass, sensitive
Evidence leak or approval/stop-condition bypass. Follow [SECURITY.md](SECURITY.md) and use the
private GitHub reporting form. Public Bug reports must use synthetic or redacted inputs and must
not contain credentials, personal data, raw private conversations or unrelated local paths.

Participation in Issues and Pull Requests is also governed by the
[Code of Conduct](CODE_OF_CONDUCT.md).
