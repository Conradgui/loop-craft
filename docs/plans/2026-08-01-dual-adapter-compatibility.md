# Dual Adapter Compatibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a real Compact Prompt output beside the existing Codex Skill output, bind either artifact to truthful Evidence, and validate Skill output against the current Codex native validator without allowing post-build mutation.

**Architecture:** Keep the existing Compiler and Final Execution IR unchanged. Introduce an adapter-neutral artifact result, route one selected adapter per build, and let Evidence bind the selected adapter plus an optional native-validation receipt. Compact Prompt preserves all current 0/1-Loop behavior semantics in one copy-ready paragraph while declaring runtime execution as delegated.

**Tech Stack:** Python 3.12+, dataclasses, argparse, subprocess, jsonschema, pytest, Markdown, JSON Evidence manifests.

---

## File map

- Create `loop-craft/scripts/loopcraft_core/adapters/artifact.py`: adapter-neutral artifact result.
- Create `loop-craft/scripts/loopcraft_core/adapters/compact_prompt.py`: deterministic Prompt projection and compatibility contract.
- Create `loop-craft/scripts/loopcraft_core/native_validation.py`: current Codex validator runner and receipt.
- Modify `loop-craft/scripts/loopcraft_core/adapters/codex_skill.py`: return the common artifact result while retaining `skill_dir` compatibility.
- Modify `loop-craft/scripts/loopcraft_core/pipeline.py`: select one adapter, run optional native validation, and dispatch verify by adapter.
- Modify `loop-craft/scripts/loopcraft_core/evidence/package.py`: bind adapter-owned metadata and optional validator receipt.
- Modify `loop-craft/scripts/build_loop.py`: expose `--adapter` and `--native-validator`.
- Create `tests/unit/test_compact_prompt_adapter.py`: Prompt semantics, determinism, compatibility and future-IR failure.
- Create `tests/unit/test_native_validation.py`: native validator pass/fail/unavailable behavior.
- Modify `tests/unit/test_codex_skill_adapter.py`: common artifact compatibility assertion.
- Modify `tests/unit/test_evidence_package.py`: adapter-neutral and receipt bindings.
- Modify `tests/integration/test_build_pipeline.py`: end-to-end selection, Evidence and drift behavior.
- Modify `loop-craft/references/core-build.md`: user-facing commands and current-native validation requirement.
- Modify `loop-craft/SKILL.md`: dual-output boundary and delivery choice.
- Modify `docs/DESIGN.md`, `README.md`, `README.zh.md`, `CHANGELOG.md`, `VERSION`, `pyproject.toml`, `dashboard/status.json`: truthful 0.4.0 product state.
- Modify GitHub repository metadata after local verification: Description and Topics only; no Release or Git version Tag.

### Task 1: Introduce the adapter-neutral artifact result

**Files:**
- Create: `loop-craft/scripts/loopcraft_core/adapters/artifact.py`
- Modify: `loop-craft/scripts/loopcraft_core/adapters/codex_skill.py`
- Modify: `loop-craft/scripts/loopcraft_core/evidence/package.py`
- Test: `tests/unit/test_codex_skill_adapter.py`
- Test: `tests/unit/test_evidence_package.py`

- [ ] **Step 1: Write the failing compatibility assertions**

Add assertions showing that the current Codex renderer exposes common metadata without changing its existing `skill_dir` consumer:

```python
assert result.artifact_dir == result.skill_dir
assert result.adapter_name == "codex-skill"
assert result.adapter_version == "0.1.0"
assert result.profile_digest.startswith("sha256:")
```

- [ ] **Step 2: Run the focused tests and observe failure**

Run:

```powershell
pytest tests/unit/test_codex_skill_adapter.py tests/unit/test_evidence_package.py -q
```

Expected: failure because `SkillArtifact` has no adapter-neutral fields.

- [ ] **Step 3: Add the common result and migrate Codex rendering**

Create:

```python
@dataclass(frozen=True)
class ArtifactResult:
    artifact_dir: Path
    artifact_digest: str
    source_map: dict[str, list[str]]
    adapter_name: str
    adapter_version: str
    profile_digest: str
    compatibility_report: dict[str, Any]
    conformance: str

    @property
    def skill_dir(self) -> Path:
        return self.artifact_dir
```

Return `ArtifactResult` from both Codex rendering branches with adapter name `codex-skill`, the existing source/non-source adapter version, and the existing Codex profile digest. Change Evidence type annotations to the common result without changing Manifest values.

- [ ] **Step 4: Run focused tests and confirm compatibility**

Run the same pytest command. Expected: all selected tests pass and existing Skill snapshots remain unchanged.

- [ ] **Step 5: Commit the common contract**

```powershell
git add loop-craft/scripts/loopcraft_core/adapters/artifact.py loop-craft/scripts/loopcraft_core/adapters/codex_skill.py loop-craft/scripts/loopcraft_core/evidence/package.py tests/unit/test_codex_skill_adapter.py tests/unit/test_evidence_package.py
git commit -m "refactor: generalize adapter artifact contract"
```

### Task 2: Implement the deterministic Compact Prompt Adapter

**Files:**
- Create: `loop-craft/scripts/loopcraft_core/adapters/compact_prompt.py`
- Create: `tests/unit/test_compact_prompt_adapter.py`

- [ ] **Step 1: Write failing 0-loop and 1-loop projection tests**

Load `accepted-definition.zero-loop.json` and `accepted-definition.valid.json`, compile each, render it, and assert:

```python
assert sorted(file_snapshot(result.artifact_dir)) == ["PROMPT.md"]
assert result.adapter_name == "compact-prompt"
assert result.conformance == "runtime_delegated"
assert result.compatibility_report["overall"] == "emulated"
```

For 1-loop, assert every node instruction, terminal mapping value, invariant, approval-required item and forbidden item appears in `PROMPT.md`. For 0-loop, assert every workflow step, success evidence item and failure/stop item appears.

- [ ] **Step 2: Write failing determinism and future-field tests**

Render equivalent definitions with reversed mapping insertion order and assert identical file bytes and digest. Construct a copied `CompileResult` whose Final Execution IR contains `runtime_binding`, then assert:

```python
with pytest.raises(ValueError, match="unsupported Final Execution IR field"):
    render_compact_prompt(changed, tmp_path)
```

- [ ] **Step 3: Run the new tests and observe import failure**

Run:

```powershell
pytest tests/unit/test_compact_prompt_adapter.py -q
```

Expected: collection fails because `compact_prompt.py` does not exist.

- [ ] **Step 4: Implement the minimal renderer**

Implement strict known-field validation and a stable labelled paragraph:

```python
SUPPORTED_EXECUTION_FIELDS = {
    "schema_version", "compiler_version", "input_profile", "definition_digest",
    "identity", "purpose", "applicability", "interface", "authority",
    "capabilities", "workflow", "loops",
}
CONFORMANCE = "runtime_delegated"

def render_compact_prompt(compiled: CompileResult, artifact_root: Path) -> ArtifactResult:
    execution = compiled.final_execution_ir
    unknown = set(execution) - SUPPORTED_EXECUTION_FIELDS
    if unknown:
        raise ValueError("unsupported Final Execution IR field: " + ", ".join(sorted(unknown)))
    artifact_dir = artifact_root / execution["identity"]["id"]
    artifact_dir.mkdir(parents=True, exist_ok=False)
    prompt = _render_prompt(execution)
    text = f"# {execution['identity']['name']}\n\n{execution['identity']['description']}\n\nPrompt:\n> {prompt}\n"
    (artifact_dir / "PROMPT.md").write_text(text, encoding="utf-8", newline="\n")
    compatibility_report = calculate_compatibility_report(execution)
    return ArtifactResult(
        artifact_dir=artifact_dir,
        artifact_digest=directory_digest(artifact_dir),
        source_map=_prompt_source_map(compiled),
        adapter_name="compact-prompt",
        adapter_version="0.1.0",
        profile_digest=sha256_digest(
            {"platform": "presentation", "profile_version": "0.1.0"}
        ),
        compatibility_report=compatibility_report,
        conformance=CONFORMANCE,
    )
```

Use stable clause order: trigger/goal, inputs/outputs, allowed/forbidden/approval, required/optional capabilities, workflow or observe→choose→act→verify→record→adapt, terminal states and invariants. Use JSON string literals where needed so arbitrary accepted text cannot break Markdown structure.

- [ ] **Step 5: Add the Prompt compatibility report and Source Map**

Required capabilities receive `emulated`; optional capabilities receive `emulated`; overall is `emulated`. Include the limitation that tools and state must be supplied by the receiving Agent. Map `PROMPT.md#prompt` to the exact IR pointers consumed by the paragraph and `PROMPT.md#summary` to identity/purpose pointers.

- [ ] **Step 6: Run Prompt tests**

Run the new test file. Expected: all Prompt adapter tests pass.

- [ ] **Step 7: Commit the Prompt adapter**

```powershell
git add loop-craft/scripts/loopcraft_core/adapters/compact_prompt.py tests/unit/test_compact_prompt_adapter.py
git commit -m "feat: add compact prompt adapter"
```

### Task 3: Route one selected adapter through CLI and Pipeline

**Files:**
- Modify: `loop-craft/scripts/build_loop.py`
- Modify: `loop-craft/scripts/loopcraft_core/pipeline.py`
- Modify: `tests/integration/test_build_pipeline.py`

- [ ] **Step 1: Write failing integration tests**

Add tests for default Skill behavior, explicit Prompt output, and rejected source-preserving Prompt:

```python
result = build_definition(definition_path, output, adapter_name="compact-prompt")
assert result.artifact_dir.name == "deterministic-repair-loop"
assert (result.artifact_dir / "PROMPT.md").is_file()
assert not (result.artifact_dir / "SKILL.md").exists()

with pytest.raises(ValueError, match="compact-prompt.*source Skill"):
    build_definition(
        definition_path,
        tmp_path / "rejected-output",
        adapter_name="compact-prompt",
        source_skill_dir=source,
        package_manifest_path=manifest,
    )
```

- [ ] **Step 2: Run the integration tests and observe signature failure**

Run:

```powershell
pytest tests/integration/test_build_pipeline.py -q
```

Expected: failure because `build_definition` has no adapter selector.

- [ ] **Step 3: Add router dispatch and CLI choices**

Add `adapter_name: str = "codex-skill"` to `build_definition`; reject unknown names before creating output. Dispatch only:

```python
if adapter_name == "codex-skill":
    artifact = render_codex_skill(
        compiled,
        staging_root / "artifact",
        source_skill_dir=source_skill_dir,
        source_manifest=source_manifest,
    )
elif adapter_name == "compact-prompt":
    if source_skill_dir is not None:
        raise ValueError("compact-prompt does not support source Skill packaging")
    artifact = render_compact_prompt(compiled, staging_root / "artifact")
else:
    raise ValueError(f"unsupported adapter: {adapter_name}")
```

Add argparse `choices=("codex-skill", "compact-prompt")` and default `codex-skill`.

- [ ] **Step 4: Run CLI and pipeline tests**

Run integration tests plus existing CLI tests. Expected: default tests remain green and explicit Prompt build passes.

- [ ] **Step 5: Commit routing**

```powershell
git add loop-craft/scripts/build_loop.py loop-craft/scripts/loopcraft_core/pipeline.py tests/integration/test_build_pipeline.py
git commit -m "feat: route selectable build adapters"
```

### Task 4: Make Evidence and Verify adapter-aware

**Files:**
- Modify: `loop-craft/scripts/loopcraft_core/evidence/package.py`
- Modify: `loop-craft/scripts/loopcraft_core/pipeline.py`
- Modify: `tests/unit/test_evidence_package.py`
- Modify: `tests/integration/test_build_pipeline.py`

- [ ] **Step 1: Write failing Manifest and drift tests**

Assert a Prompt build Manifest contains:

```python
assert manifest["adapter"] == "compact-prompt"
assert manifest["adapter_version"] == "0.1.0"
assert manifest["conformance"] == "runtime_delegated"
assert verify_build(output)["status"] == "clean"
```

Modify `PROMPT.md` and assert verify returns `drifted`. Also assert Codex Skill Manifest values remain unchanged.

- [ ] **Step 2: Observe the hard-coded Codex failure**

Run Evidence and pipeline tests. Expected: Prompt Manifest incorrectly reports Codex or verify calls the Codex-only compatibility validator.

- [ ] **Step 3: Bind adapter-owned metadata**

Replace hard-coded Manifest fields with `artifact.adapter_name`, `artifact.adapter_version`, and `artifact.profile_digest`. Keep compatibility report, conformance, source map and digest from the selected result.

- [ ] **Step 4: Dispatch compatibility verification**

In `verify_build`, select the contract validator from `manifest["adapter"]`. Reject unknown adapters. Codex uses its existing contract; Compact Prompt recalculates its emulated/runtime-delegated report from Evidence IR.

- [ ] **Step 5: Run Evidence and integration tests**

Expected: clean/drift works independently for Skill and Prompt.

- [ ] **Step 6: Commit adapter-aware Evidence**

```powershell
git add loop-craft/scripts/loopcraft_core/evidence/package.py loop-craft/scripts/loopcraft_core/pipeline.py tests/unit/test_evidence_package.py tests/integration/test_build_pipeline.py
git commit -m "feat: bind evidence to selected adapter"
```

### Task 5: Add current Codex native-validation receipts

**Files:**
- Create: `loop-craft/scripts/loopcraft_core/native_validation.py`
- Modify: `loop-craft/scripts/build_loop.py`
- Modify: `loop-craft/scripts/loopcraft_core/pipeline.py`
- Modify: `loop-craft/scripts/loopcraft_core/evidence/package.py`
- Create: `tests/unit/test_native_validation.py`
- Modify: `tests/integration/test_build_pipeline.py`

- [ ] **Step 1: Write failing validator runner tests**

Create fixture scripts that exit 0 and 1. Assert pass returns a receipt containing a SHA-256 script digest and no absolute path; failure raises `ValueError("Codex native validator failed")`; missing path raises `ValueError("Codex native validator is unavailable")`.

- [ ] **Step 2: Run the runner tests and observe import failure**

Run:

```powershell
pytest tests/unit/test_native_validation.py -q
```

Expected: module import failure.

- [ ] **Step 3: Implement the read-only runner**

Use the active interpreter and UTF-8 mode:

```python
completed = subprocess.run(
    [sys.executable, str(validator_path), str(skill_dir)],
    capture_output=True,
    text=True,
    encoding="utf-8",
    env={**os.environ, "PYTHONUTF8": "1"},
    check=False,
)
```

Normalize the receipt to schema version, validator name, validator digest and `status: passed`; do not retain the local path or environment.

- [ ] **Step 4: Add optional low-level CLI injection and strict user-path semantics**

Add `--native-validator <path>` for `codex-skill`. Reject it with `compact-prompt`. When supplied, run it after rendering and before Evidence packaging; bind `native-validation.json`, `native_validation_digest` and `native_validator_digest`. Omitting it keeps the low-level historical command available but makes no current-native claim. The Loop Craft user workflow in Task 6 must always supply the current built-in validator and stop if it is unavailable.

- [ ] **Step 5: Verify receipt and drift contracts**

Teach `verify_build` to require `native-validation.json` exactly when its two Manifest binding fields exist, validate its shape/digests, and reject partial bindings or extra files.

- [ ] **Step 6: Run unit and integration tests**

Expected: pass/fail/unavailable and receipt tampering are all observable; default historical builds still pass.

- [ ] **Step 7: Run the current official validator once**

Run the current installed Skill Creator validator against a generated Skill using its actual script path. Expected output includes `Skill is valid!`; record the script digest in the build Evidence.

- [ ] **Step 8: Commit native validation**

```powershell
git add loop-craft/scripts/loopcraft_core/native_validation.py loop-craft/scripts/build_loop.py loop-craft/scripts/loopcraft_core/pipeline.py loop-craft/scripts/loopcraft_core/evidence/package.py tests/unit/test_native_validation.py tests/integration/test_build_pipeline.py
git commit -m "feat: bind Codex native validation receipts"
```

### Task 6: Connect the Agent-facing dual-output workflow

**Files:**
- Modify: `loop-craft/SKILL.md`
- Modify: `loop-craft/references/core-build.md`
- Modify: `tests/integration/test_loop_craft_skill.py`

- [ ] **Step 1: Write failing interface assertions**

Assert the runtime Skill states that one build chooses `codex-skill` or `compact-prompt`, source-preserving Existing Skill always uses Codex Skill, and current native validation is required before delivering a Skill claim.

- [ ] **Step 2: Run interface tests and observe missing route text**

Run:

```powershell
pytest tests/integration/test_loop_craft_skill.py -q
```

Expected: new assertions fail.

- [ ] **Step 3: Update the runtime instructions**

Add commands for both adapters. In the Codex Skill path, locate the currently available built-in `skill-creator` resource, pass its `quick_validate.py` through `--native-validator`, and stop if unavailable. State that Compact Prompt is copy-ready but runtime-delegated and has no source-preserving Existing Skill route.

- [ ] **Step 4: Encode Adapter maintenance review**

State that when the Codex adapter/spec changes or a release candidate is prepared, run Skill Creator PRO@`eb23656e56ea3555599a6c5278a8b5834dc56b6d` quality lint and current built-in Skill Creator review. Apply findings to Adapter/template source, rebuild, and never patch a generated Artifact in place.

- [ ] **Step 5: Run interface tests and current native validator**

Expected: interface assertions and official validation both pass.

- [ ] **Step 6: Commit the user path**

```powershell
git add loop-craft/SKILL.md loop-craft/references/core-build.md tests/integration/test_loop_craft_skill.py
git commit -m "docs: connect dual adapter user workflow"
```

### Task 7: Verify the product slice and update release facts

**Files:**
- Modify: `docs/DESIGN.md`
- Modify: `README.md`
- Modify: `README.zh.md`
- Modify: `CHANGELOG.md`
- Modify: `VERSION`
- Modify: `pyproject.toml`
- Modify: `dashboard/status.json`

- [ ] **Step 1: Run focused tests before documentation claims**

Run the new Prompt, native-validation, Evidence, pipeline and Skill-interface tests. Expected: all pass.

- [ ] **Step 2: Run the existing full suite once because shared contracts changed**

Run:

```powershell
pytest -q
python -m compileall -q loop-craft/scripts tests
```

Expected: all tests pass and compileall exits 0.

- [ ] **Step 3: Perform two minimal real builds**

Build the same accepted definition once with `codex-skill` plus the current native validator and once with `compact-prompt`; run `verify` on both. Expected: both report `clean`, Skill passes native validation, and Prompt contains no Evidence files.

- [ ] **Step 4: Update version and product documentation**

Set repository version to `0.4.0`. Update both README architecture diagrams so Skill and Compact Prompt are solid current outputs. Reduce Runtime/future standards to a concise compatibility direction. Document one-build/one-output commands, Prompt runtime delegation, Skill native validation, and separate Evidence.

- [ ] **Step 5: Update the live dashboard**

Mark 2/2 adapters delivered only after the two real builds pass. Preserve Runtime, Override, Subloop, multi-Loop and publishing under `not_now`. Record exact tests and build/verify evidence without using test count as the product result.

- [ ] **Step 6: Run proportional documentation checks**

Parse dashboard JSON, check local README links, compare English/Chinese headings and capability claims, validate Mermaid fences, and run `git diff --check`.

- [ ] **Step 7: Commit the 0.4.0 product state**

```powershell
git add docs/DESIGN.md README.md README.zh.md CHANGELOG.md VERSION pyproject.toml dashboard/status.json
git commit -m "docs: publish dual adapter product model"
```

### Task 8: Integrate main and synchronize GitHub

**Files:**
- Git branch history
- GitHub repository `Conradgui/loop-craft` metadata

- [ ] **Step 1: Run completion verification from the final branch head**

Run the full suite only if files changed after Task 7's full run; otherwise reuse that result and rerun only JSON/link/diff checks. Confirm the worktree contains no unrelated staged files.

- [ ] **Step 2: Merge the implementation branch into local main**

Use a non-destructive fast-forward or regular merge that preserves the existing main history. Keep the pre-existing `README.zh.md` line-ending-only workspace state out of commits unless its content is intentionally changed by Task 7.

- [ ] **Step 3: Push main and inspect remote CI**

Push `main` to `origin`, then inspect the resulting GitHub Actions run. Do not create a GitHub Release or Git version Tag.

- [ ] **Step 4: Update repository discovery metadata**

Set a concise bilingual-aware Description and add Topics such as `agent-skills`, `ai-agents`, `codex`, `feedback-loop`, `prompt-engineering`, `skill-engineering`, `workflow-automation`, `evidence`, and `deterministic-build`. Keep GitHub Topics distinct from Git Tags.

- [ ] **Step 5: Report the exact final state**

Report commit, remote branch, CI URL/status, two real build results, current GitHub Description/Topics, and any remaining non-blocking boundary. Update dashboard only if remote CI changes the release judgment.
