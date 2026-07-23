# Loop Craft

Loop Craft is a Codex Skill for turning a goal, an existing Skill, or an authorized conversation record into an accepted bounded workflow or feedback Loop. It produces a clean target Skill and a separate, inspectable Evidence Package.

This repository is the development project `Loopcraft开发`. The installable product is the `loop-craft` Skill inside this repository; its Core, Compiler, Evidence Packager, and Codex Skill Adapter are bundled inside that Skill.

## Current Status

The current product slice supports:

- From-scratch design with one shared seven-item Loopability Gate;
- Existing Skill assessment with `keep_as_skill`, `embedded_loop`, `loop_first_skill`, and `split_into_loops` decisions;
- Authorized conversation distillation into an observed Workflow Model;
- Ordinary zero-Loop Skill packaging and compatible one-Loop packaging;
- Source-preserving one-Loop upgrade for reviewed existing Skill packages;
- Manifest-bound Entry Evidence for source summaries, clarifications, Candidate Review, and approval;
- deterministic build, separate Artifact/Evidence output, and read-only drift verification.

The current profiles support zero or one Loop. Multi-Loop builds, Runtime, Compact Prompt, Library Edition, publishing, scheduling, installation automation, and distributed execution are not implemented in this slice.

## Install

The runtime Skill is the `loop-craft/` directory. For local development, point Codex at this repository or copy that directory into the active Skill directory. Validate the installed directory with the platform Skill validator.

The repository does not currently declare a redistribution license. Treat it as development material until the project owner chooses and adds a license and any required notices.

## Use

Invoke the Skill for one of these requests:

```text
Use $loop-craft to design a bounded feedback Loop from this goal.
Use $loop-craft to assess this existing Skill and decide whether a Loop belongs in it.
Use $loop-craft to distill this authorized conversation into a reusable Skill.
```

The Skill asks only material clarification questions, presents a Candidate Review, and requires explicit approval before writing an accepted definition or building an output.

## Build And Verify

Run commands from `loop-craft/` with Python and `jsonschema` available:

```powershell
python scripts/build_loop.py build <accepted-definition.json> <new-output-directory> --entry-evidence <approved-entry-evidence.json>
python scripts/build_loop.py verify <existing-output-directory>
```

Existing Skill upgrades additionally use a reviewed source package manifest. See [core-build.md](loop-craft/references/core-build.md) for the exact inventory and source-preserving command.

The output root contains sibling `artifact/` and `evidence/` directories. The Artifact is the clean target Skill. Evidence contains accepted inputs, IRs, source maps, validation, manifests, and optional Entry/Source Package bindings. Raw conversations, private source material, development records, and absolute local paths do not belong in the Artifact.

## Architecture

```text
From-scratch       Existing Skill       Conversation Distiller
       \                |                       /
        source-specific Candidate Behavior Contract
                         |
              shared Loopability Gate
                         |
                 Candidate Review + approval
                         |
              Accepted Definition / Entry Evidence
                         |
                Compiler → Final Execution IR
                    /                    \
          Evidence Packager       Codex Skill Adapter
                    |                    |
              Evidence Package      target Skill
```

The Semantic/Execution contracts are the authority. An Adapter is a projection, not a replacement definition. Source Package Evidence proves preserved source bytes; Entry Evidence records the structured reason and approval for the behavior. These bindings are independent.

## Repository Map

```text
docs/                 specs, plans, records, references, project governance
loop-craft/           installable Skill, references, Core scripts, schemas
tests/                focused unit and integration tests
dashboard/            live project status at http://127.0.0.1:4173/
```

Important project records:

- [Phase 2 Spec](docs/specs/2026-07-20-loop-craft-phase-2-design.md)
- [Resource Registry](docs/references/resource-registry.yaml)
- [Decision Log](docs/project-management/decision-log.md)
- [Risk Register](docs/project-management/risk-register.md)
- [Live Dashboard](http://127.0.0.1:4173/)

## Reference Boundaries

Loop Craft selectively localizes mechanisms from the supplied Loopy handoff, Workflow Skill Creator, Skill Polisher, Skill Creator Pro, and Skill writing guidelines. The registry records what each source owns, what was adopted, and what was deliberately excluded. These projects are design references, not runtime dependencies or test fixtures.

## License Status

No repository license has been selected or added yet. This is an explicit delivery limitation, not an implicit permission to redistribute the repository or derivative material. Upstream attribution and license requirements remain recorded in the resource registry.
