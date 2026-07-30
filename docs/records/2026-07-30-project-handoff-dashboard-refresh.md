# 2026-07-30 Loop Craft 接力型双基线看板执行记录

## 任务目标

根据 Codex、Claude Code 本地会话、Git 状态和项目治理记录，更新现有 HTML 看板，使其准确区分：

- 已提交、可从 Git 恢复的能力；
- 已完成但仍停留在工作区的候选成果；
- 已形成真实用户证据的入口；
- 仍只有骨架或盲测证据的入口；
- 历史裁决、开放风险和后续主线。

本任务属于 `support`，不增加 Loop Craft 的用户可执行能力。

## 对话来源

| 来源 | ID | 采用范围 |
|---|---|---|
| Codex 主开发 | `019f7ad2-237d-77d2-b4c7-275dbc40feca` | 产品边界、Core、三入口、Packaging、Entry Evidence、首版看板和盲测设计 |
| Codex 测试支持 | `019f9a0d-faf6-7243-a3e9-affe03ab6cb8` | Blind Forward Test Dataset 修正；不计主仓库产品里程碑 |
| Claude Code 接管 | `35f026ff-2073-47ea-ac55-52ab462c33b4` | 真实 Demo、五轮验证、规则修复、治理文档、CI 和管控 Agent |
| Claude Code 恢复/看板 | `581ebf20-443a-49b8-992b-bff6afadebfe` | 恢复接管记录并生成原 `triage.html` |
| 排除的恢复尝试 | `bd5fb767-fe9b-4567-b3a0-a52e7636594c` | 输出包含与仓库不符的 TypeScript/React/LangChain 技术栈，不作为项目事实源 |

Git 已提交基线：`255438f`。

## 修改前发现的状态矛盾

1. 顶层里程碑写 `4 / 5 gates`，Gate 列表实际只有三项 `ready`。
2. `N6` 写 24 例盲测尚未执行，Activity 已记录五轮结果。
3. 风险登记把 R-024 fabrication hard-fail 标成 OPEN，第五轮实测已经归零。
4. Demo 指标写成 `1 / 1`，没有说明只覆盖 From-scratch；Existing Skill 与 Conversation 的真实调用证据仍为 `0 / 2`。
5. Claude Code 当轮 11 个修改文件和 9 个新增文件尚未提交，但这一最高优先版本风险没有进入实时主看板。
6. CI 文件已存在并完成本地离线演练，但从未进入版本库或在远端运行。

## 实际修改

### `dashboard/status.json`

- 重写顶层状态、里程碑、指标、问题清单、任务分层、风险、Gate 和 Activity；
- 增加 `handoff`，保存接力会话 ID 与角色；
- 增加 `baselines`，明确已提交基线与工作区候选；
- 将 Demo 指标拆为 From-scratch `1 / 1` 和其余入口 `0 / 2`；
- 将 fabrication hard-fail 标为已关闭；
- 保留 RV-003 路由/provenance、LC-009、LICENSE、远端 CI 和 DRIFT。

### `dashboard/index.html`

- 增加双基线区域；
- 增加 Handoff trail；
- 支持四层 `work_lanes`；
- 修正候选成果的状态显示；
- 更新侧栏产品说明；
- 保留五秒轮询、原生 JavaScript 和响应式布局。

### `dashboard/triage.html`

- 保留静态、无依赖、深浅色自适应的原有定位；
- 增加 Codex → Claude Code → Codex 接力时间线；
- 增加双基线对照；
- 重排值得讨论、需要重复验证和简要记录三档；
- 明确阶段出口仍为 `DRIFT · 不放行`；
- 删除“1/1 代表三入口”“CI 已生效”等容易误读的表达。

## 明确未修改

- 未修改 `loop-craft/SKILL.md` 或任何产品 reference；
- 未修改 Schema、Compiler、Evidence、Adapter、Pipeline 或 Python 测试；
- 未移动或删除用户既有成果；
- 未安装依赖；
- 未创建 Git commit；
- 未推送远端；
- 未选择许可证；
- 未把看板更新计入产品完成度。

## 验证记录

### 状态与静态文件

- `dashboard/status.json` 已通过 `ConvertFrom-Json -Depth 100` 严格解析；
- `status.json` 与 `index.html` 均存在 `baselines`、`handoff` 数据/挂载点；
- `index.html` 与 `triage.html` 未引用外部 CSS、JavaScript、字体或图片；
- 本地服务返回：`/` 为 HTTP `200`、`/triage.html` 为 HTTP `200`、`/status.json` 为 HTTP `200`；
- 浏览器实际读取到了更新后的 `12 modified + 14 untracked`，证明实时 JSON 已成功加载，而不是只显示 HTML 占位内容。

### Codex 侧边栏浏览器

使用 Codex 内置侧边栏浏览器检查，不安装 Playwright 或其他依赖。

`dashboard/index.html`：

- 1440 × 900：双基线两列，主区和侧栏并列，页面级横向溢出为 `false`；
- 390 × 844：双基线改为单列，侧栏下沉，页面级横向溢出为 `false`；
- Handoff trail 渲染 4 条记录；
- 浏览器控制台 warning/error 为 0。

`dashboard/triage.html`：

- 1440 × 900：双基线两列，接力时间线 4 条，`DRIFT` 结论存在；
- 390 × 844：双基线改为单列，页面级横向溢出为 `false`；
- 外部 script 与 stylesheet 数量均为 0；
- 浏览器控制台 warning/error 为 0。

验证结束后，实时看板保留在 Codex 侧边栏浏览器：`http://127.0.0.1:4173/`。

### Git 边界

- 接手并开始本次支持任务前，Claude Code 候选为 `11 modified + 9 untracked`；
- 加入本次看板、规格、计划和执行记录后，当前为 `12 modified + 14 untracked`；
- 未移动、删除、提交或推送任何用户成果；
- 最终执行 `git diff --check`，未出现空白错误；计划与规格文件也没有未完成 checkbox 或行尾空格；
- 不运行 Python 测试或盲测：本次只修改状态投影、HTML 和记录，没有改变产品行为合同，重复产品测试不会改变交付判断。

## 后续版本保护授权

看板刷新完成后，项目所有者在同一接力会话中明确要求“先把目前这个版本提交”。因此，“未创建 Git commit”只描述前一项看板支持任务的原始边界，不再限制后续独立的本地版本保护动作。

提交前重新核对全部变更路径，并确认：

- `.claude/` 与 `.codex/` 各只有一个项目级 `stage-gate-controller` 配置，没有本地会话日志；
- 敏感信息模式扫描无命中；
- `python -m pytest -q`：`160 passed`；
- `compileall`、两份 JSON Schema、dashboard JSON 与本地 Markdown 引用检查通过；
- 本次仅提交本地 `main`，不推送远端；
- 看板同步改为“本地 HEAD 已保护、origin/main 仍为 255438f、提交后工作区 clean”。
