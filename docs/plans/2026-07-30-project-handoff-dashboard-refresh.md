# Loop Craft 接力型双基线看板更新实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Do not dispatch subagents for this support task.

**Goal:** 把现有看板更新为可追溯的接力型双基线看板，准确区分 Git 已提交能力、工作区候选成果、真实用户能力和未关闭风险。

**Architecture:** `dashboard/status.json` 继续作为实时看板的状态投影；`dashboard/index.html` 只增加双基线与接力记录的渲染；`dashboard/triage.html` 继续作为静态决策看板，但其内容改为当前接力事实和优先级。执行记录保存证据来源、修改范围和验证结果，不创建第二套项目事实源。

**Tech Stack:** 静态 HTML、CSS、原生 JavaScript、JSON、PowerShell、Git 只读检查。

**执行状态（2026-07-30）：** 已完成。计划中的 `11 modified + 9 untracked` 是接手时快照；加入本次支持文件后，最终校准为 `12 modified + 14 untracked`。

---

## 文件结构

- Modify: `dashboard/status.json`
  - 负责实时状态数据；
  - 增加 `handoff` 与 `baselines`；
  - 校准顶层状态、用户能力、风险、Gate 和下一步。
- Modify: `dashboard/index.html`
  - 渲染 `handoff` 与 `baselines`；
  - 保留五秒轮询和现有响应式布局。
- Modify: `dashboard/triage.html`
  - 作为静态接力与决策看板；
  - 呈现版本保护、对话时间线、双基线和三档任务。
- Create: `docs/records/2026-07-30-project-handoff-dashboard-refresh.md`
  - 记录对话 ID、修改前矛盾、实际修改和验证证据。
- Existing design: `docs/specs/2026-07-30-project-handoff-dashboard-refresh-design.md`
  - 本计划的批准规格，不在实施中改写。

### Task 1: 校准实时状态数据

**Files:**
- Modify: `dashboard/status.json`

- [x] **Step 1: 更新顶层状态和产品指标**

把顶层状态改为以下事实：

```text
overall:
  已提交基线稳定；Claude Code 候选成果尚未进入版本库

milestone:
  M1 · 三入口真实用户链路
  progress: 60
  progress_label: From-scratch 1 / 1；其余入口 0 / 2

metrics:
  已提交基线: 255438f · 2026-07-23
  工作区候选: 11 modified + 9 untracked
  真实 Demo: From-scratch 1 / 1
  其余入口 Demo: 0 / 2
  阶段出口: DRIFT · 不放行
```

顶层摘要必须同时说明：

- Core、Packaging、Entry Evidence 和三入口骨架已提交；
- From-scratch 已有真实 Demo；
- Existing Skill 与 Conversation 仍无真实调用证据；
- 五轮行为验证已经执行，fabrication hard-fail 已关闭；
- 当前最高优先事实是候选成果未提交，不把看板更新算作产品能力增长。

- [x] **Step 2: 增加接力与双基线数据**

增加以下结构：

```json
{
  "handoff": {
    "label": "Codex → Claude Code → Codex",
    "records": [
      {
        "agent": "Codex",
        "id": "019f7ad2-237d-77d2-b4c7-275dbc40feca",
        "period": "2026-07-19 — 2026-07-26",
        "role": "产品边界、Core、三入口、Packaging、Entry Evidence 与首版看板"
      },
      {
        "agent": "Claude Code",
        "id": "35f026ff-2073-47ea-ac55-52ab462c33b4",
        "period": "2026-07-26",
        "role": "真实 Demo、五轮盲测、规则修复、治理文档、CI 与管控 Agent"
      },
      {
        "agent": "Claude Code",
        "id": "581ebf20-443a-49b8-992b-bff6afadebfe",
        "period": "2026-07-29",
        "role": "恢复接管记录并生成 triage.html"
      },
      {
        "agent": "Codex",
        "id": "current",
        "period": "2026-07-30",
        "role": "核对对话、Git 与治理记录，校准双基线看板"
      }
    ]
  },
  "baselines": [
    {
      "kind": "committed",
      "title": "已提交基线",
      "value": "255438f · 2026-07-23",
      "state": "ready",
      "detail": "确定性 Core、三入口骨架、共享 Gate、Packaging、Entry Evidence 与 build/verify 可从 Git 恢复。"
    },
    {
      "kind": "workspace",
      "title": "工作区候选",
      "value": "11 modified + 9 untracked",
      "state": "blocked",
      "detail": "五轮验证后的规则修复、双语 README、DESIGN、评估报告、CI、管控 Agent 与看板尚未进入版本库。"
    }
  ]
}
```

不在状态文件中写本地绝对会话路径，只保存会话 ID 和角色。

- [x] **Step 3: 重写问题、任务分层和下一步**

Problem Ledger 至少包含：

```text
P0-01 工作区候选尚无版本保护          active
P0-02 Existing Skill / Conversation 无真实 Demo active
P1-01 RV-003 direct-build provenance   active
P1-02 LC-009 source inventory 可达性    active
P1-03 远端 CI 尚未首跑                 active
P1-04 LICENSE 尚未决定                  active
P2-01 fabrication hard-fail             ready
P2-02 三入口共享 Gate / Evidence        ready
```

`work_lanes` 必须满足：

```text
mainline:
  active 仅一项：保护并复核当前工作区候选

validation:
  看板 JSON / HTML 最小验证
  后续 LC-009 放松修复必须绑定 RV-001 安全护栏

support:
  许可证决策
  远端 CI 首跑
  风险登记与实测结果对齐

not_now:
  Runtime / Override / Subloop / Library Edition / 多 Loop / 发布调度
```

`next_steps` 改为：

```text
N1 保护并复核工作区候选       active
N2 选择下一条真实 Demo 入口    queued
N3 修复 RV-003 direct-build   queued
N4 重新设计 LC-009 可达性      queued
N5 LICENSE 与远端 CI          queued
```

不得保留“N6 24 例盲测尚未执行”。

- [x] **Step 4: 对齐风险、Gate、已交付和 Activity**

明确以下状态：

- R-024 fabrication hard-fail 已关闭；
- R-020/RV-003 路由与 provenance 仍开放；
- R-021/R-025/LC-009 仍开放；
- G4 测试预算历史违规保留；
- 阶段出口仍为 DRIFT；
- CI 只完成本地工作流文件和离线演练，未远端运行；
- `delivered` 只能把工作区候选写成“候选已存在，未提交”，不能标成远端交付完成；
- Activity 加入 2026-07-30 的“对话与双基线核对完成”，但不提高产品完成度。

- [x] **Step 5: 严格解析 JSON**

Run:

```powershell
Get-Content -Raw -LiteralPath 'dashboard\status.json' | ConvertFrom-Json -Depth 100 | Out-Null
```

Expected: 退出码 `0`，无解析错误。

### Task 2: 最小同步实时 HTML 看板

**Files:**
- Modify: `dashboard/index.html`

- [x] **Step 1: 增加双基线区域**

在 Milestone 与 Product signal 之间增加：

```html
<section class="section" aria-labelledby="baselines-title">
  <div class="section-head">
    <h2 id="baselines-title">Two baselines</h2>
    <small>committed ≠ workspace</small>
  </div>
  <div class="baseline-grid" id="baselines"></div>
</section>
```

新增 `.baseline-grid`、`.baseline-card`、`.baseline-value` 样式。桌面为两列，`max-width: 620px` 时变一列。

- [x] **Step 2: 增加接力记录区域**

在 Activity 前增加：

```html
<section class="section" aria-labelledby="handoff-title">
  <div class="section-head">
    <h2 id="handoff-title">Handoff trail</h2>
    <small id="handoff-label">conversation provenance</small>
  </div>
  <div class="handoff-list" id="handoff"></div>
</section>
```

每条记录显示 Agent、会话 ID、时间与角色。会话 ID 使用普通文本，不生成本地文件链接。

- [x] **Step 3: 扩展渲染函数**

在 `render(data)` 中加入：

```javascript
state("baselines").innerHTML = data.baselines.map(item =>
  `<article class="baseline-card ${safe(item.state)}">
    <div class="metric-label">${safe(item.title)}</div>
    <div class="baseline-value">${safe(item.value)}</div>
    <p>${safe(item.detail)}</p>
  </article>`
).join("");

state("handoff-label").textContent = data.handoff.label;
state("handoff").innerHTML = data.handoff.records.map(item =>
  `<div class="handoff-item">
    <strong>${safe(item.agent)}</strong>
    <code>${safe(item.id)}</code>
    <span>${safe(item.period)} · ${safe(item.role)}</span>
  </div>`
).join("");
```

继续使用现有 `safe()` 入口，不新增依赖。

- [x] **Step 4: 修正侧栏产品说明**

把旧说明替换为：

```text
已提交基线证明 Core 与三入口骨架可恢复；工作区候选包含真实 Demo、行为验证和治理补强，但尚未进入版本库。From-scratch 已真实走通，另外两条入口仍缺真实调用证据。
```

保留 Refresh 与五秒轮询说明。

### Task 3: 更新静态分诊看板

**Files:**
- Modify: `dashboard/triage.html`

- [x] **Step 1: 更新顶部结论**

标题改为：

```text
Loop Craft 接力与决策看板
```

顶部结论必须包含：

```text
已提交基线稳定，工作区候选尚未进入版本库。
From-scratch 已真实走通；Existing Skill 与 Conversation 仍缺真实 Demo。
当前支持任务不会提高产品完成度。
```

- [x] **Step 2: 增加接力时间线**

时间线按以下顺序呈现：

```text
2026-07-19 — 07-26 · Codex 019f7ad2...
产品边界 → Core → 三入口 → Packaging → Entry Evidence → 实时看板

2026-07-26 · Claude Code 35f026ff...
真实 Demo → 五轮验证 → 规则修复 → 管控 Agent → 文档 / CI

2026-07-29 · Claude Code 581ebf20...
恢复接管记录 → 生成静态分诊看板

2026-07-30 · Codex current
核对对话、Git 和治理记录 → 建立双基线状态
```

- [x] **Step 3: 增加双基线对照**

对照内容与 `status.json.baselines` 一致，并在工作区候选上显示最高优先标签：

```text
先保护和复核，再决定提交边界；本次不自动提交或推送。
```

- [x] **Step 4: 重排三档问题**

“值得讨论”保留四项：

1. 下一条真实 Demo 先做 Existing Skill 还是 Conversation；
2. capability 词表扩展还是长期边界；
3. LICENSE 选择；
4. 工作区候选如何拆分为可审阅提交。

“需要重复验证”只保留三类：

1. LC-009 与 RV-001 的相反方向；
2. 放松类修复的反向护栏；
3. 正确停机与过度停机的评分稳定性。

“简要记录”包括：

- fabrication hard-fail 已关闭；
- 远端 CI 未首跑；
- validator 在 Windows 非 UTF-8 locale 下需 `PYTHONUTF8=1`；
- 源包不是事务快照；
- 多 Loop、Runtime 与 Library Edition 不在当前队列。

- [x] **Step 5: 更新阶段出口**

阶段出口使用：

```text
DRIFT · 不放行
```

理由限定为：

- 候选成果未提交；
- Existing Skill / Conversation 无真实 Demo；
- R-020/R-021 仍开放；
- LICENSE 未定；
- 远端 CI 未验证；
- 历史测试预算违规和状态记录不一致仍需保留为治理教训。

不得把支持性看板更新表述成解除 DRIFT 的证据。

### Task 4: 记录执行证据

**Files:**
- Create: `docs/records/2026-07-30-project-handoff-dashboard-refresh.md`

- [x] **Step 1: 写入记录头部和来源**

记录必须包含：

```text
Codex main: 019f7ad2-237d-77d2-b4c7-275dbc40feca
Codex test support: 019f9a0d-faf6-7243-a3e9-affe03ab6cb8
Claude Code takeover: 35f026ff-2073-47ea-ac55-52ab462c33b4
Claude Code recovery/dashboard: 581ebf20-443a-49b8-992b-bff6afadebfe
Excluded recovery attempt: bd5fb767-fe9b-4567-b3a0-a52e7636594c
Git baseline: 255438f
```

- [x] **Step 2: 记录修改前矛盾**

逐条记录：

- `4 / 5` 与三项 ready Gate 不一致；
- N6 与五轮 Activity 不一致；
- R-024 OPEN 与第五轮 hard-fail 归零不一致；
- Demo `1 / 1` 没有入口范围；
- 未提交候选未进入顶层状态。

- [x] **Step 3: 记录实际修改与未修改范围**

列出三份看板文件的实际变化，并明确：

- 未修改 Skill、Schema、Core、Adapter 和测试；
- 未移动、删除、安装、提交或推送；
- 看板更新不增加用户可执行能力。

### Task 5: 最小验证与收口

**Files:**
- Verify: `dashboard/status.json`
- Verify: `dashboard/index.html`
- Verify: `dashboard/triage.html`
- Update: `docs/records/2026-07-30-project-handoff-dashboard-refresh.md`

- [x] **Step 1: 检查字段引用**

Run:

```powershell
$status = Get-Content -Raw -LiteralPath 'dashboard\status.json' | ConvertFrom-Json -Depth 100
$html = Get-Content -Raw -LiteralPath 'dashboard\index.html'
@('baselines','handoff') | ForEach-Object {
  if (-not $status.psobject.Properties.Name.Contains($_)) { throw "missing status field: $_" }
  if ($html -notmatch ('id="' + $_ + '"')) { throw "missing html target: $_" }
}
```

Expected: 退出码 `0`。

- [x] **Step 2: 检查静态文件无外部资源依赖**

Run:

```powershell
rg -n 'https?://|<script[^>]+src=|<link[^>]+href=' dashboard/index.html dashboard/triage.html
```

Expected: 不出现外部 CSS、JavaScript、字体或图片依赖；文字中的本地服务 URL 可保留。

- [x] **Step 3: 启动或复用本地看板服务**

先检查 `127.0.0.1:4173`：

```powershell
try {
  (Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:4173/' -TimeoutSec 2).StatusCode
} catch {
  'not-running'
}
```

如果未运行，使用工作区现有 Python 启动静态服务：

```powershell
Start-Process -WindowStyle Hidden -FilePath python -ArgumentList '-m','http.server','4173','--directory','dashboard'
```

Expected: 首页和 `/triage.html` 返回 HTTP `200`。

- [x] **Step 4: 浏览器检查桌面和窄屏**

检查：

- `index.html` 双基线为两列，窄屏为一列；
- Handoff trail 可读，无横向溢出；
- `triage.html` 接力时间线、双基线、三档问题和阶段出口完整；
- 页面无 JavaScript 控制台错误；
- status.json 五秒刷新后内容仍存在。

- [x] **Step 5: 检查差异边界**

Run:

```powershell
git diff --check
git diff --name-only
git status --short
```

Expected:

- `git diff --check` 不报告本次引入的空白错误；
- 本次新增修改只涉及计划、规格、三份看板文件和执行记录；
- 既有未提交文件仍被保留；
- 不运行 Python 测试和盲测。

- [x] **Step 6: 回写验证结果**

在执行记录中写入：

- JSON 解析结果；
- HTTP 状态；
- 桌面与窄屏检查结果；
- `git diff --check` 结果；
- 未执行 Python 测试的理由；
- 当前仍未提交、未推送。

本任务不创建 Git commit；候选提交边界由后续独立任务决定。
