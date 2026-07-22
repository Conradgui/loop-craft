# Core Build

Use only the commands below. Run them from the `loop-craft` directory.

The runtime must provide Python and jsonschema; if either dependency is missing, stop and do not guess or install it.

## Build an accepted definition

Require an existing, readable JSON definition that matches `scripts/loopcraft_core/kernel/schemas/accepted-definition.schema.json`. Require a new output path that does not already exist.

```powershell
python scripts/build_loop.py build <accepted-definition.json> <new-output-directory>
```

A successful build exits `0`. The output root contains sibling `artifact/` and `evidence/` directories. `artifact/` contains the generated target Skill. `evidence/` contains the accepted definition, final execution data, source map, validation report, and build manifest. The `skill-package-v0.1` profile accepts either an approved ordinary Workflow with zero Loops or one approved Loop. A zero-Loop definition must include `behavior_contract.workflow.steps`, `success_evidence`, and `failure_or_stop`.

Historical or direct accepted-definition builds may omit Entry Evidence. Every build produced by the From-scratch, Existing Skill, or Conversation entry after Candidate approval must provide the reviewed record:

```powershell
python scripts/build_loop.py build <accepted-definition.json> <new-output-directory> --entry-evidence <reviewed-entry-evidence.json>
```

The `entry-evidence-v0.1` contract has exactly seven root fields: `schema_version`, `entry_type`, `definition_digest`, `source_summary`, `clarifications`, `candidate_review`, and `approval`. `entry_type` is `from_scratch`, `existing_skill`, or `conversation`; it maps respectively to `source_summary.kind` `design_interview`, `skill_assessment`, or `workflow_model`. `source_summary` also contains non-empty controlled `source_ids`, a bounded summary, and non-empty provenance-labelled fact summaries. `clarifications` may be empty; each present item contains only a non-empty question summary, answer summary, and `resolution: resolved`.

`candidate_review.classification` is `zero_loop_workflow` or `one_loop_bounded_loop` and must match the accepted definition's Loop count. `approval` contains only `status: approved` and `scope: local_artifact_and_evidence_build`. The root `definition_digest` must exactly equal the accepted definition's canonical digest. The canonical record is written only to `evidence/entry-evidence.json`; its digest and entry type are bound in `build-manifest.json`, and it never enters Artifact.

The caller must supply structured summaries and controlled source IDs, never raw conversation, absolute paths, private source material, raw Skill payloads, or development records. Validation enforces shape, local absolute-path rejection, approval scope, classification, and digest binding; it does not prove summary truth, perform PII scanning, or provide identity authentication. Entry Evidence is an approved input summary, not a second intermediate representation or an automatically extracted record.

If the definition is missing, unreadable, malformed, rejected by validation, or the output path is already occupied, stop at the error. Do not guess a different input or overwrite an existing path.

## Inventory and preserve an existing Skill

First write a new, reviewable source-package manifest:

```powershell
python scripts/build_loop.py inventory <source-skill-directory> <new-manifest.json>
```

Review the manifest before approval. It records only sorted POSIX-relative paths, the `preserve`, `overlay`, or `generated` action, file digests, and the complete source Skill digest. It never records an absolute source path. Unknown root entries, links, a missing `SKILL.md`, or an occupied manifest path stop inventory.

After the one-Loop upgrade and manifest are both approved, build into a new directory:

```powershell
python scripts/build_loop.py build <accepted-definition.json> <new-output-directory> --source-skill <source-skill-directory> --package-manifest <reviewed-manifest.json> --entry-evidence <reviewed-entry-evidence.json>
```

`--source-skill` and `--package-manifest` must be supplied together. This route accepts only `skill-package-v0.1` with exactly one Loop. The source directory name and safely parsed `SKILL.md` frontmatter name must both equal `behavior_contract.identity.id`. The build re-inventories the source and stops if anything differs from the reviewed manifest, if source and output overlap, or if the resulting `SKILL.md` exceeds 500 lines.

The source is never modified. The new artifact preserves source-owned metadata, references, scripts, assets, and license material byte-for-byte; appends the approved `## Feedback Loop` section to `SKILL.md`; and generates `references/final-execution-ir.json`. The source-package manifest proves which source bytes were preserved; Entry Evidence records why the behavior was accepted. They are independent Manifest bindings and neither duplicates nor requires the other outside this approved-entry command.

## Verify an existing build

Require an existing output root created by the build command, including its sibling `artifact/` and `evidence/` directories.

```powershell
python scripts/build_loop.py verify <existing-output-directory>
```

A clean artifact reports `clean` and exits `0`. A changed artifact reports `drifted` and exits `1`. Verification derives the expected Evidence files from the independent source-package and Entry Evidence bindings in `build-manifest.json`; it does not need the original source directory or Entry Evidence input path. Verification checks the Entry Evidence shape, canonical digest, entry type, definition binding, and classification. Verification is read-only: it does not repair, rebuild, or write back to either sibling directory.

If the path is missing or is not a valid build root, stop at the error instead of treating it as drift.
