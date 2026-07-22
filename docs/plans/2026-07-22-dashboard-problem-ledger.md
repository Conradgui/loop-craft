# Dashboard Problem Ledger Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the existing live dashboard show the reviewed problems, ordered resolution path, and traceable completion gates.

**Architecture:** Keep `dashboard/status.json` as the state source and `dashboard/index.html` as the renderer. Add only the `issues`, `phase_gates`, and `known_limits` projections needed by the approved design.

**Tech Stack:** Static HTML, CSS, JavaScript, and JSON.

---

### Task 1: Add the problem ledger projection

**Files:**
- Modify: `dashboard/index.html`
- Modify: `dashboard/status.json`

- [x] Add a responsive Problem Ledger section that renders priority, fact, action, and done condition.
- [x] Render explicit phase-gate progress and known limits from `status.json`.
- [x] Replace overstated or stale dashboard claims with the reviewed current state.

### Task 2: Perform the minimum dashboard check

**Files:**
- Verify: `dashboard/index.html`
- Verify: `dashboard/status.json`

- [x] Parse `status.json` with PowerShell `ConvertFrom-Json`.
- [x] Request `http://127.0.0.1:4173/status.json` and confirm the new state is served.
- [x] Check the dashboard HTML references `issues`, `phase_gates`, and `known_limits`.
- [x] Confirm `git diff --check` passes.
