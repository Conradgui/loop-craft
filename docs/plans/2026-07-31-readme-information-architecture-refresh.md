# README Information Architecture Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the half-finished implementation-first bilingual README with a product-first, Loop-centered explanation that restores the approved 分—总—分 architecture and gives first-time Agent users a friendly path to installation and invocation.

**Architecture:** Both language editions share one factual and structural contract: three primary entries converge on the shared Loop pipeline, whose Final Execution IR feeds Evidence Packager and Adjuster in parallel. Skill is the current solid-edge output; Compact Prompt, Runtime, future Loop-standard formats, and other adapters remain explicitly planned or future paths.

**Tech Stack:** GitHub-flavored Markdown, Mermaid, JSON status projection, PowerShell/Python static checks.

---

## File map

- Modify `README.md`: canonical English product narrative, architecture, quick start, capability status, and developer entry.
- Modify `README.zh.md`: structurally equivalent Chinese narrative with idiomatic explanations and examples.
- Modify `dashboard/status.json`: support-layer record of the README refresh without changing 0.3.0 product completion.
- Update this plan's checkboxes as each task completes.

Runtime Skill files, schemas, tests, version metadata, `docs/DESIGN.md`, and release facts are unchanged.

### Task 1: Rewrite the bilingual product narrative

**Files:**
- Modify: `README.md`
- Modify: `README.zh.md`
- Reference: `docs/specs/2026-07-31-readme-information-architecture-refresh.md`

- [x] **Step 1: Replace the English README with the approved information architecture**

Use this exact heading order:

```text
# Loop Craft
## See Loop Craft in one minute
## Choose your starting point
## Quick start
## What you get
## How Loop Craft decides
## Why the result is trustworthy
## Works today
## Evolution paths
## For developers
## References and independence
## License
```

Required content:

- approved Loop-centered hero copy from the design spec;
- the approved Mermaid graph with three primary entries, Direct Build as an expert shortcut,
  the shared middle, parallel Evidence Packager/Adjuster outputs, solid Skill, and dotted future outputs;
- one plain-language paragraph immediately after the graph explaining `分—总—分` and why Evidence is not an Adjuster input;
- the four-row starting-point table and four copy-ready invocation prompts;
- Codex `$skill-installer` and manual-copy installation paths without claiming an unverified installer command;
- clean Artifact and separate Evidence output tree;
- concise seven-check Gate and 0/1/multi-Loop classification;
- source, approval, deterministic-build, and read-only-verify boundaries;
- separate current and future capability lists;
- developer build commands, repository map, and links to design/evaluation/decision/risk documents.

- [x] **Step 2: Replace the Chinese README with the same factual contract**

Use this exact heading order:

```text
# Loop Craft
## 一分钟看懂 Loop Craft
## 选择你的起点
## 快速开始
## 你会得到什么
## Loop Craft 如何判断
## 为什么这个结果值得信任
## 当前可用
## 演进方向
## 面向开发者
## 参考来源与独立性
## 许可证
```

Keep the same Mermaid node IDs, edges, status labels, links, tables, output files, and
capability boundaries as the English edition. Use the approved Chinese hero and idiomatic
Chinese invocation examples. Explain technical terms on first use instead of translating
English sentence order mechanically.

- [x] **Step 3: Run the bilingual structure and local-link contract check**

Run an inline Python checker that asserts:

```text
English H2 count = 11
Chinese H2 count = 11
Both contain ENTRY, CORE, EP, AR, S, P, and F Mermaid node IDs
Both contain solid AR --> S
Both contain dotted planned Compact Prompt and future-adapter edges
Neither describes Compact Prompt, Runtime, or future-standard compatibility as implemented
Every relative Markdown link in both files resolves from its README directory
```

Expected: exit 0 with `README contract: PASS` and `missing links: 0`.

- [x] **Step 4: Review the diff for product truth and readability**

Confirm the first screen explains Loop before Compiler, the main graph can be restated as
three entries → shared Core → Evidence/Adjuster split, Direct Build is not called a fourth
discovery entry, and no current capability carries a distracting `Available in 0.3.0` label.

- [x] **Step 5: Commit the bilingual README rewrite**

```text
git add README.md README.zh.md docs/plans/2026-07-31-readme-information-architecture-refresh.md
git commit -m "docs: rebuild Loop Craft README experience"
```

### Task 2: Synchronize the live status projection

**Files:**
- Modify: `dashboard/status.json`
- Modify: `docs/plans/2026-07-31-readme-information-architecture-refresh.md`

- [x] **Step 1: Record the support-layer README refresh**

Keep overall product status `PASS · 0.3.0 封板` and milestone progress `100`. Update
`updated_at`, add a completed support item for the product-model README, and prepend one
activity entry stating:

```text
中英文 README 已恢复三入口 → 统一 Core → Evidence / Adjuster 双出口的分—总—分产品模型；
Skill 保持当前实线输出，Compact Prompt、Runtime 与未来标准格式继续明确标为演进方向。
```

Do not increase product completion or remove existing risks.

- [x] **Step 2: Run documentation-only verification**

Run:

```text
git diff --check
dashboard/status.json JSON parse
bilingual README structure/link contract from Task 1
Markdown fence balance for both README files
scan for private absolute paths
scan for stale current/future capability claims
```

Expected: every command exits 0. Do not run pytest because no runtime contract changed.

- [x] **Step 3: Mark this plan complete and commit the status projection**

```text
git add dashboard/status.json docs/plans/2026-07-31-readme-information-architecture-refresh.md
git commit -m "docs: record README architecture refresh"
```

### Task 3: Review and integrate the documentation branch

**Files:**
- Review only: branch diff against `main`

- [x] **Step 1: Run final branch checks**

Confirm branch status is clean, commits contain only the approved documentation/support
files, local README links resolve, dashboard JSON parses, and the `loop-craft/` tree hash is
unchanged from `main`.

- [ ] **Step 2: Integrate without rewriting product history**

Fast-forward `main` only when it still points to the design commit or is an ancestor of the
documentation branch. Push only after local/remote equality and the final documentation
checks pass. The README-only change does not create a Release or Tag.
