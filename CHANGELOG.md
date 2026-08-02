# Changelog

All notable changes to this project are documented in this file.

## 0.4.0 - 2026-08-01

Dual-output Adapter release.

### Added

- A deterministic Compact Prompt Adapter that projects the same approved Final Execution IR
  into one copy-ready `PROMPT.md`, with `emulated` compatibility and
  `runtime_delegated` conformance stated explicitly.
- `--adapter codex-skill|compact-prompt` selection. One build emits one Artifact plus its
  separate, adapter-bound Evidence Package; the existing default remains `codex-skill`.
- Optional `--native-validator` support for Codex Skill builds. The Manifest binds a
  path-free Native Validation Receipt containing the current validator script digest and
  normalized result digests.
- Adapter-neutral Artifact contracts and adapter-aware read-only verification for both Skill
  and Prompt drift.

### Changed

- Evidence no longer assumes every Artifact embeds a Skill-only Final Execution IR reference;
  every Adapter now binds the compiled IR through an explicit digest contract.
- Current Codex compatibility findings must be fixed in the Adapter or template and rebuilt;
  generated Artifacts are never patched in place while retaining stale Evidence.
- Final staging promotion has a bounded retry for the observed transient Windows
  `PermissionError`; persistent permission failures still stop the build.
- Version metadata is unified at `0.4.0`.

### Boundaries

- Compact Prompt preserves the approved behavior, authority, verification, stopping and
  invariant content, but it does not supply tools, state, scheduling, or independent audit.
- Source-preserving Existing Skill upgrades remain Codex Skill builds. Runtime, multi-Loop,
  Override, Subloop, publishing, scheduling, installation automation, Release and Git tags
  remain outside this version.

## 0.3.0 - 2026-07-31

Product-path closure release.

### Added

- A Direct Definition Build route for approved JSON or prose definitions. New
  `entry-evidence-v0.2` records use `entry_type: direct_build`,
  `source_summary.kind: accepted_definition`, and `candidate_review: null`, so the build
  remains provenance-bound without claiming a Candidate Review occurred.
- Safe support for common Existing Skill packages containing a regular root `package.json`,
  a source directory whose name is not the accepted identity, and a `SKILL.md` with missing
  frontmatter. Canonical frontmatter is generated only in the new Artifact; original source
  body bytes and package files remain Manifest-bound.
- A real Conversation Distillation Demo producing a zero-Loop Skill plus separate Evidence,
  clean/drift verification, official validation, and an isolated behavior smoke check.
- Apache License 2.0 for this repository.

### Changed

- Existing Skill identity now comes from the accepted Definition. Valid conflicting,
  malformed, unterminated, or duplicate source frontmatter names stop the build instead of
  being silently normalized.
- Source package inventory keeps unknown roots, links, junctions, special files, stale
  manifests, and source/output overlap fail closed.
- Documentation now states the actual privacy boundary: raw conversations, private source
  material, development records, and absolute local paths belong in neither the Artifact nor
  Entry Evidence. Only bounded summaries, controlled source IDs, digests, and approved
  clarifications are retained.
- Version metadata is unified at `0.3.0`.

### Evaluation follow-up

- Targeted run 5 closed the RV-003 fabrication hard-fail by distinguishing values supported by
  scoped evidence from invented defaults. The remaining Direct Build provenance and mechanical
  Existing Skill package gaps were then fixed at the deterministic and Agent-interface layers.
- The historical 25/27 run is not relabelled. No expensive full-population rerun was performed;
  0.3.0 uses focused contract tests plus a separate fresh-context product-interface audit.

### Known limitations

- Builds support zero or one qualifying Loop. Multi-Loop builds, Runtime, Override, Subloop,
  Library Edition, publishing, scheduling, installation automation, GitHub Release, and tags
  remain outside the 0.3.0 product boundary.
- The platform capability vocabulary remains intentionally narrow; unsupported required
  capabilities stop the build and unsupported optional capabilities are marked degraded.

## 0.2.0 - 2026-07-27

First release with behavioral evidence. Everything before this was verified only at the
deterministic layer.

### Added

- First real end-to-end delivery through the From-scratch entry: a user goal taken through
  interview, Loopability Gate, Candidate Review, explicit approval, and a real build producing
  a clean Skill plus a separate Evidence Package. Verified with `verify` clean, a drift
  negative case exiting 1, the official Skill validator passing, and a scan confirming zero
  absolute paths or private identifiers in the artifact.
- Blind behavioral evaluation harness: isolated per-case sandboxes, task briefings and grading
  keys stored outside the sandbox tree, fresh-context runners barred from reading the
  development repo, and graders required to inspect the filesystem rather than trust the
  response.
- Three reverse guardrail cases covering situations whose correct answer is to stop — an
  out-of-root package link, cross-run state the schema cannot represent, and an approved prose
  definition missing schema-required fields.
- `stage-gate-controller` review agent: read-only, verdict-only, seven-point checklist, with
  explicit authority to block low-value repeat audits, premature abstraction, and progress
  claimed through test counts.
- CI across Linux and Windows on Python 3.12 and 3.13, including schema meta-validation, the
  official Skill validator, link resolution, a real build/verify cycle, and a negative case
  asserting that drift verification rejects a tampered artifact.
- `docs/DESIGN.md`, `docs/REAL_WORLD_EVALUATION.md`, `CONTRIBUTING.md`, `NOTICE.md`, `VERSION`,
  and a bilingual README.

### Changed

- **Loopability Gate — the Loop count may only be reduced to 0 by a named failed check.** An
  earlier fix enumerated one forbidden flattening argument; the model read it and constructed a
  rephrased exception. Enumerating prohibitions loses to paraphrase, so the default was
  inverted instead.
- Gate check 3 now recognises a target-owned acceptance judgement — a user, reviewer, or named
  role accepting or rejecting a presented draft — as an observable check, scored against the
  acceptance owner named in the authorized record rather than whoever happens to be present when
  the built Skill later runs. Only model self-confidence remains disqualified.
- Gate check 6 now states that a bounded iteration budget qualifies, including a budget of
  exactly one. A cycle known to stop after N passes is an N-bounded Loop with a minimum of 1,
  never 0.
- Gate now counts independent revision cycles **before** scoring any candidate. Without this,
  several independent cycles could each score as non-qualifying and then be merged into a single
  zero-Loop Workflow, slipping past the multi-Loop boundary by reshaping the deliverable.
- A missing material verifier is a blocked finding — explicitly never a downgrade to Workflow.
- `embedded_loop` is buildable when its single supporting Loop maps without semantic loss and
  the remaining fixed phases are preserved as workflow behavior. It was previously a verdict
  §4 could produce and §6 always rejected.
- Candidate Review raised from a relevance threshold to a blocking threshold: a question must
  also be underivable from scoped evidence. Added source precedence — an unambiguous in-scope
  document outranks a user's paraphrase, and the discrepancy travels as an explicit note instead
  of stalling the build.
- The Loop classification is no longer a `proposed` item deferred to the user. The Gate has
  already decided it.
- `keep_as_skill` must name which of the seven checks failed. A verdict that cannot point at a
  specific failed check is a defensive fallback, not a finding.

### Evaluation

| Run | Cases | Pass | Fail |
|---|---|---|---|
| 1 | 24 | 18 | 6 |
| 2 | 24 | 20 | 4 |
| 3 | 27 | 25 | 2 |

Across all three runs: zero files written before approval, and the Skill under test never
modified. Runs 1 and 2 triggered no hard-fail conditions.

**Run 3 triggered one.** RV-003 filled the schema-required `authority` field with plausible
defaults — including a prohibition its source never mentions — and presented them as settled
rather than as named gaps. This is fabrication of a security boundary. It is the single
failure in this evaluation that is over-reach rather than under-delivery, and it is unfixed
at this release.

An earlier draft of this changelog, the README, the dashboard, and the governance logs stated
all three runs were hard-fail clean. That was an extrapolation from runs 1 and 2 and it was
wrong; the independent stage-gate review caught it and it is corrected here.

### Known limitations

- Two cases still fail, both from the same root cause: mechanical and form-level gaps — a source
  package without frontmatter, a definition supplied as prose — are treated as stopping
  conditions rather than as gaps to carry forward with labelled proposed values. Behavioral and
  security gaps are handled correctly. Tracked as `R-021` and in the evaluation record.
- Grading is unstable on the boundary between a correct stop and an over-cautious stop. A single
  pass-rate delta on that boundary is signal, not measurement. Tracked as `R-022`.
- The platform capability vocabulary has four values and cannot express network or hosting
  access. Tracked as `R-017`.
- Entry Evidence has no legal `entry_type` for a direct build. Tracked as `R-020`.
- No redistribution license has been selected. Tracked as `R-014`.
