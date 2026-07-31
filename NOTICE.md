# Notice

Loop Craft is an independent project. Its Core, Compiler, Evidence Packager, and Codex Skill
Adapter are original to this repository.

## Design references

The following projects were studied and selectively localized. Each is a **design
reference**, not a runtime dependency, not a vendored copy, and not a test fixture. What was
adopted, what was deliberately excluded, and why is recorded per source in
[`docs/references/resource-registry.yaml`](docs/references/resource-registry.yaml).

| Source | License recorded in registry | Localized here as |
|---|---|---|
| [Conradgui/loopy](https://github.com/Conradgui/loopy) (handoff package) | MIT | Interview shape, Loopability reasoning, four architecture verdicts, crafted-loop preflight |
| Workflow Skill Creator | Apache-2.0 | Observed-workflow recovery, progressive clarification, explicit-approval flow |
| [Conradgui/skill-polisher](https://github.com/Conradgui/skill-polisher) | MIT | Read-only inventory, preserved invariants, minimal approved modification, full-package recheck |
| [Conradgui/skill-creator-pro](https://github.com/Conradgui/skill-creator-pro) | Apache-2.0 | Behavior contract first, minimal complete directory, deferred metadata generation, structural validation |
| [Conradgui/matt-pocock-inspired-skill-writing](https://github.com/Conradgui/matt-pocock-inspired-skill-writing) | MIT | Cross-cutting skill-writing constraints |
| Official Codex `skill-creator` | See upstream | Format compatibility baseline only; `quick_validate.py` is invoked, never modified |

Upstream attribution and license requirements remain with their respective owners. No
endorsement by OpenAI, Anthropic, or any listed author is implied.

## What is not borrowed

The deterministic build chain — canonical serialization, the accepted-definition and
entry-evidence schemas, the Final Execution IR, Source Map, Build Manifest, dual-binding
Evidence Package, and read-only drift verification — is this project's own work.

## Repository license status

The original Loop Craft work in this repository is distributed under the Apache License,
Version 2.0; see [`LICENSE`](LICENSE). That license does not relicense the independent
upstream projects listed above. Their own licenses, notices, and attribution requirements
continue to apply to their respective material.

The listed sources were used as design references rather than vendored runtime dependencies.
If future changes copy upstream code or assets into this repository, the contributor must add
the applicable upstream license and modification notices before distribution.
