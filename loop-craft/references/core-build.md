# Core Build

Use only the commands below. Run them from the `loop-craft` directory.

The runtime must provide Python and jsonschema; if either dependency is missing, stop and do not guess or install it.

## Build an accepted definition

Require an existing, readable JSON definition that matches `scripts/loopcraft_core/kernel/schemas/accepted-definition.schema.json`. Require a new output path that does not already exist.

```powershell
python scripts/build_loop.py build <accepted-definition.json> <new-output-directory>
```

A successful build exits `0`. The output root contains sibling `artifact/` and `evidence/` directories. `artifact/` contains the generated target Skill. `evidence/` contains the accepted definition, final execution data, source map, validation report, and build manifest. The `skill-package-v0.1` profile accepts either an approved ordinary Workflow with zero Loops or one approved Loop. A zero-Loop definition must include `behavior_contract.workflow.steps`, `success_evidence`, and `failure_or_stop`.

If the definition is missing, unreadable, malformed, rejected by validation, or the output path is already occupied, stop at the error. Do not guess a different input or overwrite an existing path.

## Inventory and preserve an existing Skill

First write a new, reviewable source-package manifest:

```powershell
python scripts/build_loop.py inventory <source-skill-directory> <new-manifest.json>
```

Review the manifest before approval. It records only sorted POSIX-relative paths, the `preserve`, `overlay`, or `generated` action, file digests, and the complete source Skill digest. It never records an absolute source path. Unknown root entries, links, a missing `SKILL.md`, or an occupied manifest path stop inventory.

After the one-Loop upgrade and manifest are both approved, build into a new directory:

```powershell
python scripts/build_loop.py build <accepted-definition.json> <new-output-directory> --source-skill <source-skill-directory> --package-manifest <reviewed-manifest.json>
```

`--source-skill` and `--package-manifest` must be supplied together. This route accepts only `skill-package-v0.1` with exactly one Loop. The source directory name and safely parsed `SKILL.md` frontmatter name must both equal `behavior_contract.identity.id`. The build re-inventories the source and stops if anything differs from the reviewed manifest, if source and output overlap, or if the resulting `SKILL.md` exceeds 500 lines.

The source is never modified. The new artifact preserves source-owned metadata, references, scripts, assets, and license material byte-for-byte; appends the approved `## Feedback Loop` section to `SKILL.md`; and generates `references/final-execution-ir.json`. Its Evidence directory contains a sixth file, `source-package-manifest.json`, whose manifest and source digests are bound by `build-manifest.json`.

## Verify an existing build

Require an existing output root created by the build command, including its sibling `artifact/` and `evidence/` directories.

```powershell
python scripts/build_loop.py verify <existing-output-directory>
```

A clean artifact reports `clean` and exits `0`. A changed artifact reports `drifted` and exits `1`. Verification accepts either the five-file generated package or the six-file source-bound package and does not need the original source directory. Verification is read-only: it does not repair, rebuild, or write back to either sibling directory.

If the path is missing or is not a valid build root, stop at the error instead of treating it as drift.
