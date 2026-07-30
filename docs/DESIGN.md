# Loop Craft Design

> Normative architecture reference. When this document and the shipped Skill disagree, the
> Skill and its schemas are authoritative and this document is stale — fix it.
>
> Scope note: this describes what is implemented today. Deferred ideas live in
> [Out of scope](#8-out-of-scope-today), not in the sections above it.

## 1. What problem this solves

Teams keep re-deriving the same thing: a repeatable agent behavior that is supposed to
*iterate* — draft, check, revise, stop — but that ends up written as a flat prompt with no
verifier, no stopping rule, and no record of why it was accepted.

Two failure modes dominate:

1. **Manufactured loops.** A fixed staged checklist gets called a "loop" because it has
   several steps. Nothing in it consumes feedback, so another pass changes nothing.
2. **Unfalsifiable loops.** A genuine cycle exists, but its acceptance rule is "until it
   looks good". Nobody can reproduce the judgement, so the loop either never stops or stops
   on model self-confidence.

Loop Craft turns a goal, an existing Skill, or an authorized work record into an
**accepted behavior contract**, and then compiles that contract deterministically into a
clean installable Skill plus a separate, inspectable Evidence Package.

The Evidence Package is the part that makes the result auditable: it records what was
accepted, by whom, on what basis, and binds every output to a digest.

## 2. Three layers, and why the split matters

```text
┌─ Prompt layer ──────────────────────────────────────────────┐
│  SKILL.md + references/*.md                                 │
│  Routing, seven-check Gate, Candidate Review, approval gate  │
│  Judgement lives here. Verified by behavioral evaluation.    │
└──────────────────────────┬───────────────────────────────────┘
                           │  accepted definition (JSON)
                           │  entry evidence (JSON)
┌──────────────────────────▼───────────────────────────────────┐
│  Contract layer                                              │
│  kernel/schemas/*.schema.json                                │
│  The only place a shape is defined. Both layers obey it.     │
└──────────────────────────┬───────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────┐
│  Deterministic layer                                         │
│  validation → compiler → adapter → evidence → pipeline       │
│  No judgement. Same input, same bytes. Verified by pytest.   │
└──────────────────────────────────────────────────────────────┘
```

The split is deliberate and it is the single most important design decision in the project.

**Everything requiring judgement is pushed up into the prompt layer. Everything below the
contract boundary is a pure function.** That is why the deterministic layer can be tested
with ordinary unit tests and byte-comparison, while the prompt layer requires isolated
behavioral evaluation against a hidden oracle.

It also means the two layers fail differently and must be verified differently. A green
test suite says nothing about whether the Gate classifies correctly. Conversely a
well-behaved interview says nothing about whether two builds produce identical bytes.
Both kinds of evidence are required; neither substitutes for the other.

## 3. Three entries, one Gate

```text
From-scratch          Existing Skill           Conversation
(goal → design)       (assess → upgrade)       (record → model)
      │                      │                       │
      └──────────────────────┼───────────────────────┘
                             │  source-specific Candidate Behavior Contract
                  ┌──────────▼──────────┐
                  │  Loopability Gate   │  single owner, never redefined per entry
                  └──────────┬──────────┘
                  ┌──────────▼──────────┐
                  │  Candidate Review   │  shared packet + blocking-question threshold
                  └──────────┬──────────┘
                             │  explicit user approval — nothing is written before this
                  ┌──────────▼──────────┐
                  │  Core build         │
                  └─────────────────────┘
```

Each entry owns only **source-specific recovery**: how to extract a candidate contract from
a goal, from an existing Skill package, or from an authorized transcript. Everything after
that is shared.

`references/loopability-gate.md` is the **single owner** of the seven checks. Entries link
to it; they must never restate or locally amend it. An earlier version of this project had
each entry carrying its own copy, which drifted — the same candidate could be classified
differently depending on which entry the user happened to trigger.

### The Loopability Gate

A candidate qualifies as a Loop only when all seven are true:

1. A pass produces fresh evidence or changed state.
2. That feedback can change the next selected action.
3. An observable, repeatable check judges progress or acceptance.
4. Each pass takes one bounded action without widening authority.
5. Success, clean no-op, blocked, approval-required, and no-progress states are
   distinguishable when relevant.
6. Iteration adds value beyond a one-shot or fixed staged workflow.
7. State needed by the next pass can be recorded, with explicit recovery or handoff.

Two rules around the Gate carry most of its weight in practice, and both were added because
blind evaluation showed the Gate failing in a specific direction:

- **Independent cycles are counted before any candidate is scored.** Without this, several
  independent cycles could each individually score as "not qualifying" and then be merged
  into a single zero-Loop Workflow — quietly slipping past the multi-Loop boundary by
  reshaping the deliverable into something buildable.
- **The Loop count may only be reduced to 0 by a named failed check.** Any other route to
  zero is a flattening argument the Gate does not grant. Enumerating forbidden arguments one
  at a time proved insufficient: each time one was closed, a rephrased version got through.
  The fix was to invert the default.

### Classification outcomes

| Qualifying Loops | Result |
|---|---|
| 0 | Ordinary Workflow. Buildable as a zero-Loop Skill with `workflow.steps`, `success_evidence`, `failure_or_stop`. |
| exactly 1 | Bounded Loop. Buildable with `loops[0].cycle`, `terminal_states`, `invariants`. |
| 2 or more | **Assessment only.** Not buildable. Independent Loops are never compressed. |

Existing Skill Upgrade additionally carries four architecture verdicts — `keep_as_skill`,
`embedded_loop`, `loop_first_skill`, `split_into_loops` — because "should a Loop exist here
at all, and where" is a different question from "does this candidate qualify".

## 4. Data flow

```text
accepted-definition.json ──► validate ──► compile ──► Final Execution IR
                              │             │              │
                     schema → canonical     │        ┌─────┴─────┐
                          → semantic        │        ▼           ▼
                                       source map  Adapter   Evidence
                                                     │           │
                                                artifact/    evidence/
```

**Validation runs in a fixed order: schema → canonical → semantic.** The order is not
cosmetic. Semantic checks perform set operations over authority lists and format error
messages containing user-supplied values; running them before canonical validation allowed
a lone surrogate to turn a stable validation error into a `UnicodeEncodeError`. Canonical
validation now rejects non-canonical input before any semantic value is touched.

**The compiler is a projection, never a second definition.** It deep-copies the validated
input before projecting, so the Final Execution IR shares no nested object with the caller's
mutable input. Determinism is tested by recursively reversing every dict key order in the
input and comparing canonical bytes and digests of the output.

**The adapter is a projection too.** It renders `SKILL.md`, `agents/openai.yaml`, and
`references/final-execution-ir.json` from the Final Execution IR. It does not decide
behavior, and it never writes Evidence.

Free text in the rendered Markdown is emitted as a single-line JSON string literal. This
closes structural injection — a value containing newlines and `##` cannot become new
Markdown headings — at a real cost to readability: rendered titles carry visible quotes.
That trade was taken deliberately. It is not general HTML sanitization and must not be
described as such.

**The pipeline is atomic.** It stages into a `TemporaryDirectory` created inside
`output_root.parent`, writes adapter output then Evidence, and only calls
`staging_root.replace(output_root)` after both succeed. An invalid definition or an adapter
failure leaves no partial output directory. An already-occupied output path is rejected up
front, including when it is a dangling symlink.

## 5. Two orthogonal evidence bindings

The Build Manifest can bind two independent proofs. Neither implies nor duplicates the
other, and `verify` derives the expected Evidence file set dynamically from whichever
bindings are present.

| Binding | Answers | Contains |
|---|---|---|
| **Source Package Evidence** | *Which source bytes were preserved?* | Sorted POSIX-relative paths, per-file digests, `preserve`/`overlay`/`generated` action, complete source digest. Never an absolute path. |
| **Entry Evidence** | *Why was this behavior accepted?* | Controlled source IDs, provenance-labelled fact summaries, resolved clarifications, a bounded Candidate Review summary, and the approval record. Bound to the accepted definition's canonical digest. |

Keeping them separate matters because they have different lifetimes and different trust
properties. A source-preserving upgrade needs the first; a from-scratch design has no source
package but still needs the second.

**What Entry Evidence is not.** Validation enforces shape, rejects local absolute paths,
fixes the approval scope, checks the 0/1 classification against the actual Loop count, and
verifies digest binding. It does **not** prove the summaries are true, perform PII scanning,
provide complete de-identification, or authenticate the approver. Claiming otherwise is a
hard failure in evaluation, and the reference text says so explicitly.

## 6. Determinism and drift

- Canonical JSON: `sort_keys`, no spaces, `ensure_ascii=False`, `allow_nan=False`, UTF-8, LF.
  `ensure_ascii=False` is load-bearing — it is what allows non-ASCII content to survive into
  a generated Skill without becoming `\uXXXX` escapes.
- `directory_digest` hashes sorted relative paths and file bytes with 8-byte big-endian
  length prefixes on both path and content. An earlier NUL-separated scheme admitted digest
  collisions across differently-split path/content boundaries.
- `verify` is strictly read-only. It reports `clean` (exit 0) or `drifted` (exit 1) and never
  repairs, rebuilds, or writes back. It rejects a symlinked artifact root, links inside the
  tree, and a symlinked Evidence directory or Manifest before reading any JSON through them.

## 7. Safety model

Three rules, in priority order:

1. **The target is untrusted input.** A Skill being assessed, a transcript being distilled,
   and a saved definition are all evidence. Instructions inside them never grant authority,
   widen scope, or override the user's actual request.
2. **Nothing is written before explicit approval.** The Candidate Review is shown first. A
   generic "upgrade this" is not approval of a plan the user has not seen. Two rounds of
   blind evaluation confirmed this holds in practice: across every failing case, the sandbox
   `outputs/` directory was empty.
3. **The source is never modified.** Source-preserving upgrades build into a new directory
   and preserve source bytes verbatim; the source directory is not touched.

Building a Skill never runs, installs, publishes, or schedules it. Those are separate
actions requiring separate authorization.

## 8. Out of scope today

Not implemented. Listed so nobody has to rediscover the boundary:

Multi-Loop builds · Runtime · Override · Subloop · Compact Prompt output ·
Library Edition · publishing · scheduling · installation automation · distributed execution

Known limitations with open remediation are tracked in
[risk-register.md](project-management/risk-register.md), not here.

## 9. Where to change what

| Change | File |
|---|---|
| Routing between entries | `loop-craft/SKILL.md` |
| The seven checks, cycle counting, classification | `loop-craft/references/loopability-gate.md` |
| Review packet, blocking-question threshold, approval | `loop-craft/references/candidate-review.md` |
| Source-specific recovery | `references/from-scratch.md`, `upgrade-skill.md`, `from-conversation.md` |
| Build/verify commands and Entry Evidence contract | `loop-craft/references/core-build.md` |
| Any shape | `loop-craft/scripts/loopcraft_core/kernel/schemas/*.json` |
| Platform projection | `loop-craft/scripts/loopcraft_core/adapters/` |

Changing a shared file — the Gate, the Review, a schema — changes all three entries at once.
Those changes require the full behavioral evaluation, not a targeted subset. See
[REAL_WORLD_EVALUATION.md](REAL_WORLD_EVALUATION.md) for what that costs and what it caught.
