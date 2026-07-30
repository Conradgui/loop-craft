# Loop Craft 接力型双基线看板更新设计

> 状态：已批准并实施
> 日期：2026-07-30
> 任务层级：`support`
> 目标：让现有 HTML 看板同时准确呈现对话接力来源、已提交基线、未提交候选状态、真实用户能力和下一步主线。

## 1. 为什么要更新

当前看板不是单纯过期，而是把三类不同事实混在同一层：

1. Git 已提交、可从 `HEAD` 重建的能力；
2. Claude Code 已完成但仍停留在工作区的候选成果；
3. 盲测、管控裁决与治理记录中的阶段性结论。

这导致同一看板内出现互相冲突的状态：

- 总进度写为 `4 / 5 gates`，但 Gate 列表只有三项 `ready`；
- `N6` 仍写 24 例盲测待执行，Activity 已记录五轮结果；
- R-024 在风险登记中仍为 OPEN，而第五轮已关闭 fabrication hard-fail；
- `Demo 1 / 1` 没有说明只覆盖 From-scratch，容易被理解成三入口都完成真实验证；
- Claude Code 当轮成果尚未提交这一最高优先事实没有进入实时主看板。

本次更新只修复状态表达和接力可追溯性，不修改 Loop Craft 产品逻辑、Schema、Compiler、Adapter 或测试。

## 2. 对话与证据来源

看板中的交接事实按以下来源排序：

1. **仓库命令事实**：当前 `HEAD`、工作区状态、文件是否真实存在；
2. **可复核执行记录**：构建输出、verify、测试结果、独立管控裁决；
3. **Codex 主开发记录**：线程 `019f7ad2-237d-77d2-b4c7-275dbc40feca`；
4. **Claude Code 接管主会话**：会话 `35f026ff-2073-47ea-ac55-52ab462c33b4`；
5. **Claude Code 恢复与看板会话**：会话 `581ebf20-443a-49b8-992b-bff6afadebfe`；
6. **历史治理文档**：只在其内容没有被更晚的命令事实或实测结果推翻时采用。

Codex 的测试包修正任务 `019f9a0d-faf6-7243-a3e9-affe03ab6cb8` 只作为测试支持记录，不计为主仓库开发里程碑。Claude Code 会话 `bd5fb767-fe9b-4567-b3a0-a52e7636594c` 是一次后续恢复尝试，其输出包含与仓库不符的技术栈判断，不作为项目事实源。

## 3. 双基线模型

看板必须把项目状态分成两条清晰基线。

### 3.1 已提交基线

- 当前 `HEAD`：`255438f`；
- 最后提交日期：2026-07-23；
- 已提交能力：确定性 Core、三入口 Walking Skeleton、共享 Loopability Gate、Packaging、Entry Evidence、build / verify 和既有测试；
- 这条基线是版本库可以直接恢复的能力。

### 3.2 工作区候选

- 11 个已跟踪文件被修改；
- 9 个新增文件尚未跟踪；
- 主要内容：五轮盲测后的规则修复、双语 README、DESIGN、REAL_WORLD_EVALUATION、CONTRIBUTING、CI、管控 Agent、版本与归属文件、分诊看板；
- 这些内容可以作为当前候选事实，但不能写成“已经进入版本库”或“远端已生效”。

看板不得用一个总进度百分比掩盖两条基线的差异。里程碑仍可保留，但必须同时显示“版本保护状态”。

## 4. 用户能力口径

### 4.1 已可用

- 用户可直接调用 Loop Craft 的 From-scratch 路径；
- 已有一次真实需求完成访谈、Gate、Candidate Review、批准、构建和交付；
- 真实 Demo 产出可调用 Skill 与独立 Evidence；
- 确定性 build、clean verify 与 drift 检测已有证据；
- 三入口共享 Gate、Candidate Review、Compiler、Evidence 和 Adapter 路径已接通。

### 4.2 仍不可用或未证实

- Existing Skill Upgrade 尚无真实用户 Demo；
- Conversation Distillation 尚无真实用户 Demo；
- direct build 无合法 Entry Evidence 来源类型，RV-003 仍有路由和 provenance 失真；
- 真实 Skill 包的 inventory 可达性仍受 LC-009 限制；
- 网络、托管平台和更细粒度 Git 能力无法由当前 capability 词表准确表达；
- 多 Loop、Runtime、Override、Subloop、Library Edition、发布与调度仍属于 `not_now`；
- CI 尚未在远端运行；
- 仓库尚无明确 LICENSE。

看板中的 Demo 指标改为“From-scratch 真实 Demo 1 / 1；其余入口 0 / 2”，不再使用含糊的单个 `1 / 1`。

## 5. 文件职责与修改范围

### `dashboard/triage.html`

作为“接力与决策看板”，保留当前静态、自适应布局，更新为：

- 顶部显示版本保护警报；
- 增加 Codex → Claude Code → 当前 Codex 的接力时间线；
- 增加已提交基线 / 工作区候选的双栏对照；
- 重新整理值得讨论、需要重复验证、简要记录三档；
- 删除已经过期或自相矛盾的数字；
- 明确当前推荐主线是先保护和复核现有候选，再决定 Existing Skill / Conversation 的真实 Demo 顺序；
- 不引入框架、构建工具或外部依赖。

### `dashboard/status.json`

继续作为实时状态事实投影，更新：

- `updated_at`、`overall`、`milestone` 和产品指标；
- Problem Ledger 的事实、行动和完成条件；
- `work_lanes`，确保一次只有一个 `mainline` active；
- `delivered`，区分已提交能力和未提交候选；
- `next_steps`，移除“盲测尚未执行”等过时内容；
- `risks`、`phase_gates`、`known_limits` 和 Activity；
- 增加轻量的 `handoff` 与 `baselines` 数据，供实时看板显示接力来源和双基线。

### `dashboard/index.html`

只做最小同步：

- 渲染 `handoff` 与 `baselines`；
- 把侧栏的旧英文说明改为当前真实产品边界；
- 保持五秒轮询、现有配色和响应式布局；
- 不进行视觉重做或组件拆分。

### 项目记录

新增一份执行记录，记录：

- 本次使用的对话 ID；
- 修改前识别出的看板矛盾；
- 实际修改文件；
- 静态和浏览器验证结果；
- 未修改的产品逻辑及剩余风险。

建议位置：`docs/records/2026-07-30-project-handoff-dashboard-refresh.md`。

## 6. 状态裁决

更新后的顶层状态使用以下结论：

- **产品状态**：From-scratch 端到端路径可用；另外两个入口尚未获得真实调用证据；
- **工程状态**：已提交 Core 基线稳定，候选规则和交付文档尚未进入版本库；
- **质量状态**：五轮行为验证已执行，fabrication hard-fail 已关闭，剩余两个结构性缺口需要 Schema / Python 级修改；
- **发布状态**：不放行；原因是未提交候选、远端 CI 未验证、LICENSE 未定和阶段裁决仍为 DRIFT。

现有 `DRIFT` 裁决不因看板更新而自动撤销。看板更新只是修正状态投影，不是新的阶段出口审查。

## 7. 下一步排序

更新后只允许一个 active 主线：

1. **主线 active**：保护并复核当前未提交候选，形成可审阅的提交边界；本次任务不自动提交或推送；
2. **validation attached**：只做看板 JSON、页面渲染和现有链接的最小检查；
3. **support**：许可证决策、远端 CI 首跑、治理记录一致性；
4. **not_now**：LC-009、R-020/RV-003 的 Schema/Python 修复，以及 Runtime、Library Edition、多 Loop 等扩展。

候选被保护后，产品主线应优先补 Existing Skill Upgrade 或 Conversation Distillation 的真实 Demo，而不是继续进行大规模盲测。两个入口的具体先后顺序属于下一项产品决策，不在本次支持任务中替用户决定。

## 8. 验证边界

本次修改是 HTML、JSON 与记录更新，默认不运行 Python 全量测试。最小验证为：

1. `dashboard/status.json` 可被严格解析；
2. `index.html` 引用的所有状态字段均存在；
3. `triage.html` 可独立打开，无外部资源依赖；
4. 本地服务下 `index.html` 和 `triage.html` 桌面宽度无明显溢出；
5. 窄屏布局仍可读；
6. `git diff --check` 不报告本次修改引入的空白错误；
7. 修改范围不包含产品 Skill、Schema、Python Core 或测试。

不重复运行 24/27 例盲测，也不因为支持性看板更新重跑 160 项测试。

## 9. 明确不做

- 不提交或推送当前工作区成果；
- 不修改、移动或删除既有未提交文件；
- 不修复 LC-009、R-020/RV-003；
- 不选择许可证；
- 不宣称 CI 已远端生效；
- 不把看板更新计入产品完成度；
- 不重做看板视觉风格；
- 不把测试通过率当作唯一产品指标。
