# Loop Craft 0.4.0 Open-Source Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish the already validated Loop Craft 0.4.0 product slice as a reproducible, governable GitHub Release with a stable Skill archive and protected main branch.

**Architecture:** Repository contracts are enforced by one deterministic integration test, then consumed by the existing GitHub Actions matrix. A feature PR proves the repository changes before merge; the merged commit is the only source for the release archive, tag and checksums. GitHub settings are applied after the release so protection cannot block the release integration itself.

**Tech Stack:** Markdown, GitHub Issue Forms YAML, GitHub Actions YAML, Python 3.12+, pytest, git, GitHub CLI and REST API.

---

### Task 1: Pin the release CI supply chain

**Files:**
- Create: `tests/integration/test_repository_release_contract.py`
- Modify: `.github/workflows/validate.yml`

- [ ] **Step 1: Write the failing CI contract test**

Add assertions that the workflow contains read-only contents permission, `workflow_dispatch`, immutable Action SHAs with readable version comments, and the pinned Skill Creator PRO revision:

```python
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "validate.yml"


def test_release_workflow_pins_every_external_checkout() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "permissions:\n  contents: read" in text
    assert "workflow_dispatch:" in text
    assert "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1" in text
    assert "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0" in text
    assert "ref: eb23656e56ea3555599a6c5278a8b5834dc56b6d" in text
```

- [ ] **Step 2: Run the test and verify RED**

Run: `python -m pytest tests/integration/test_repository_release_contract.py -q`

Expected: failure because the workflow still uses floating Action majors and no Skill Creator PRO `ref`.

- [ ] **Step 3: Make the workflow deterministic**

Add:

```yaml
on:
  push:
  pull_request:
  workflow_dispatch:

permissions:
  contents: read
```

Replace both checkout calls and setup-python with the immutable SHAs in Step 1. Add
`ref: eb23656e56ea3555599a6c5278a8b5834dc56b6d` to the external repository checkout.

- [ ] **Step 4: Run the targeted test and verify GREEN**

Run: `python -m pytest tests/integration/test_repository_release_contract.py -q`

Expected: `1 passed`.

- [ ] **Step 5: Commit**

```text
git add .github/workflows/validate.yml tests/integration/test_repository_release_contract.py
git commit -m "ci: pin release validation dependencies"
```

### Task 2: Add the minimum open-source governance surface

**Files:**
- Create: `SECURITY.md`
- Create: `CODE_OF_CONDUCT.md`
- Create: `.github/ISSUE_TEMPLATE/bug_report.yml`
- Create: `.github/ISSUE_TEMPLATE/feature_request.yml`
- Create: `.github/ISSUE_TEMPLATE/config.yml`
- Create: `.github/pull_request_template.md`
- Modify: `tests/integration/test_repository_release_contract.py`

- [ ] **Step 1: Extend the contract test and verify RED**

Assert every file exists and assert the security policy points to
`https://github.com/Conradgui/loop-craft/security/advisories/new`. Assert the Bug form requests
Loop Craft version, entry route, selected Adapter, reproduction, expected/actual behavior and
Evidence redaction. Assert the PR template requests user impact, validation and boundaries.

Run: `python -m pytest tests/integration/test_repository_release_contract.py -q`

Expected: failure listing the missing community files.

- [ ] **Step 2: Add `SECURITY.md` and `CODE_OF_CONDUCT.md`**

Security must support 0.4.x, direct vulnerabilities to private reporting, forbid posting raw
conversations/Evidence/secrets in public Issues, state that Loop Craft can read/write local
files only under approved scope, and give a best-effort acknowledgement target without a
guaranteed remediation SLA. Conduct reports use the same private channel when confidentiality
is needed because no public maintainer email exists.

- [ ] **Step 3: Add structured Issue and PR templates**

Use GitHub Issue Forms with required acknowledgements for redaction and scope. Disable blank
Issues and add Security plus Discussions-independent documentation contact links. The PR
template must distinguish checks run from checks deliberately not run.

- [ ] **Step 4: Run the targeted test and static YAML load**

Run:

```text
python -m pytest tests/integration/test_repository_release_contract.py -q
python -c "import pathlib,yaml; [yaml.safe_load(p.read_text(encoding='utf-8')) for p in pathlib.Path('.github/ISSUE_TEMPLATE').glob('*.yml')]; print('issue forms yaml ok')"
```

Expected: contract passes and all three Issue Form YAML files parse.

- [ ] **Step 5: Commit**

```text
git add SECURITY.md CODE_OF_CONDUCT.md .github tests/integration/test_repository_release_contract.py
git commit -m "docs: add open-source governance contracts"
```

### Task 3: Make the stable release path discoverable

**Files:**
- Modify: `README.md`
- Modify: `README.zh.md`
- Modify: `CONTRIBUTING.md`
- Modify: `CHANGELOG.md`
- Modify: `tests/integration/test_repository_release_contract.py`

- [ ] **Step 1: Extend the contract test and verify RED**

Require both READMEs to link to `tree/v0.4.0/loop-craft`, Security, Issues, Pull Requests,
Contributing and Code of Conduct. Require CONTRIBUTING to direct suspected vulnerabilities to
SECURITY instead of public Issues.

- [ ] **Step 2: Update user and contributor navigation**

Keep `main` documentation links for living docs, but change the default installer prompt to
the immutable `v0.4.0/loop-craft` path. Add a compact Community section to both READMEs and a
Security section to CONTRIBUTING. Record governance and stable-install changes under 0.4.0 in
CHANGELOG without claiming the GitHub Release exists yet.

- [ ] **Step 3: Run the targeted contract and local-link checks**

Run the contract test plus the existing Markdown link checker logic over root, docs and
`loop-craft/`. Expected: 0 broken local links.

- [ ] **Step 4: Commit**

```text
git add README.md README.zh.md CONTRIBUTING.md CHANGELOG.md tests/integration/test_repository_release_contract.py
git commit -m "docs: expose stable release and community paths"
```

### Task 4: Project the release candidate truthfully

**Files:**
- Modify: `dashboard/status.json`
- Create: `docs/records/2026-08-01-v0.4.0-open-source-release.md`

- [ ] **Step 1: Update the dashboard to RELEASE CANDIDATE**

Keep product completion at 100%, add a separate release-readiness milestone/lane stating that
repository contracts are local-complete while PR CI, main CI, Release and branch protection are
pending. Do not reduce the delivered product capability or claim the external actions occurred.

- [ ] **Step 2: Create the execution record**

Record the immutable revisions, intended GitHub settings, local validation commands and blank
fields for observed PR/main run IDs and Release URL. Blank fields must be labeled pending, not
fabricated.

- [ ] **Step 3: Validate and commit**

Parse `dashboard/status.json`, run `git diff --check`, then commit:

```text
git add dashboard/status.json docs/records/2026-08-01-v0.4.0-open-source-release.md
git commit -m "docs: stage 0.4.0 open-source release"
```

### Task 5: Run the complete local release gate

**Files:** none unless a verification failure reveals an in-scope defect.

- [ ] **Step 1: Run deterministic checks**

Run `python -m compileall -q loop-craft/scripts tests`, schema meta-validation, dashboard JSON,
root/docs/Skill local links, current Codex `quick_validate.py`, and Skill Creator PRO quality
lint at the pinned revision.

- [ ] **Step 2: Run the complete test suite**

Run: `python -m pytest -q`

Expected: 191 tests pass after adding the repository contract test.

- [ ] **Step 3: Run same-definition dual builds**

Build the valid fixture with `codex-skill` plus the current native validator and with
`compact-prompt`; run `verify` on both. Expected: both `clean`, Skill has the native receipt,
Prompt does not.

- [ ] **Step 4: Review scope**

Confirm `git status --short` is clean, inspect `main..HEAD`, and confirm no Core/Adapter/Schema
behavior file changed.

### Task 6: Publish through a ready PR and merge

**Files:** no new repository files.

- [ ] **Step 1: Push the release branch**

Push `codex/oss-release-readiness` with upstream tracking.

- [ ] **Step 2: Open a ready-for-review PR**

Title: `Prepare Loop Craft 0.4.0 for formal open-source release`.

Body must cover supply-chain pinning, stable install path, governance contracts, local evidence,
no Core behavior changes and deferred non-goals. This PR is ready, not draft, because the user
explicitly requested completion through GitHub.

- [ ] **Step 3: Wait for PR CI and merge**

Require all four matrix jobs to succeed. Merge without force-push, then wait for the merge
commit's `main` push workflow to succeed 4/4. Stop if either run fails.

### Task 7: Create the immutable release and GitHub protections

**Files:** temporary release assets only; no generated archive enters Git.

- [ ] **Step 1: Build release assets from the verified merge commit**

Use `git archive` to create `loop-craft-v0.4.0.zip` containing only `loop-craft/` under a
versioned prefix. Write its lowercase SHA-256 line to `SHA256SUMS.txt`, then independently
recompute and compare the digest.

- [ ] **Step 2: Create Tag and Release**

Create annotated `v0.4.0` at the verified merge commit. Create a non-draft, non-prerelease
GitHub Release with bounded claims, install instructions, CI run link, explicit limitations and
both assets. Stop instead of overwriting if Tag or Release already exists.

- [ ] **Step 3: Apply repository settings**

Enable private vulnerability reporting, disable the unused Wiki, and protect `main` with strict
required checks for the four matrix job names. Enforce protection for administrators, disallow
force pushes and deletion, require conversation resolution, and do not require an impossible
self-approval.

- [ ] **Step 4: Read back every external fact**

Verify Tag target, Release assets/digests, Private Vulnerability Reporting status, Wiki disabled,
Community Profile, branch protection and `origin/main`.

### Task 8: Close through the protected branch and hand off

**Files:**
- Modify: `dashboard/status.json`
- Modify: `docs/records/2026-08-01-v0.4.0-open-source-release.md`

- [ ] **Step 1: Create a closure branch and record only observed remote results**

Create `codex/oss-release-closure` from the protected `main`. Write actual PR URL, PR and main CI
run IDs, verified release commit, Release URL, archive digest, GitHub settings results and any
non-blocking residual into the record and dashboard.

- [ ] **Step 2: Run support-only checks and commit**

Parse dashboard JSON, verify Markdown links and run `git diff --check`. Commit on the closure
branch with:

```text
git commit -m "docs: record 0.4.0 open-source release [skip ci]"
```

- [ ] **Step 3: Push closure facts through a second PR**

Push the closure branch, open a ready PR, wait for its four required checks and merge through the
new protection rule. Wait for the resulting `main` run, confirm local HEAD equals `origin/main`,
and keep `v0.4.0` on the earlier verified product commit.
