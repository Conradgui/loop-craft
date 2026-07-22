# Core Build

Use only the two commands below. Run them from the `loop-craft` directory.

## Build an accepted definition

Require an existing, readable JSON definition that matches `scripts/loopcraft_core/kernel/schemas/accepted-definition.schema.json`. Require a new output path that does not already exist.

```powershell
python scripts/build_loop.py build <accepted-definition.json> <new-output-directory>
```

A successful build exits `0`. The output root contains sibling `artifact/` and `evidence/` directories. `artifact/` contains the generated target Skill. `evidence/` contains the accepted definition, final execution data, source map, validation report, and build manifest.

If the definition is missing, unreadable, malformed, rejected by validation, or the output path is already occupied, stop at the error. Do not guess a different input or overwrite an existing path.

## Verify an existing build

Require an existing output root created by the build command, including its sibling `artifact/` and `evidence/` directories.

```powershell
python scripts/build_loop.py verify <existing-output-directory>
```

A clean artifact reports `clean` and exits `0`. A changed artifact reports `drifted` and exits `1`. Verification is read-only: it does not repair, rebuild, or write back to either sibling directory.

If the path is missing or is not a valid build root, stop at the error instead of treating it as drift.
