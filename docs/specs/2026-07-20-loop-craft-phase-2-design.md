# Loop Craft 阶段 2 设计 Spec

> 状态：Approved
> 版本：0.1.0
> 日期：2026-07-20
> 项目仓库：Loopcraft开发
> 可安装 Skill：Loop Craft（机器名称：loop-craft）

## 1. 文档地位

本文档是阶段 2 的统一设计基线。它吸收第一阶段交接、Loop IR 架构基线、Loop 工程与写作指导，以及已确认的产品边界，但不把任何外部项目或旧交接文档当作最终权威。

权威顺序：

~~~text
批准的 Loop Craft Spec / ADR
> Active Plan
> 可重跑的测试、Trace、Receipt 和执行记录
> Resource Registry
> 旧交接声明与历史对话
~~~

本文档定义产品架构、协议边界、编译链和验收要求，不声称当前实现已经完成。

## 2. 产品身份与命名

- 研发项目显示名称：Loopcraft开发。
- Skill 展示名称：Loop Craft。
- Skill 目录名和 frontmatter name：loop-craft。
- Loopcraft Clean 不再作为产品名称；不含 Loopy 或 Loop Library 依赖是 Loop Craft 的默认边界属性。
- 未来的 Loop Craft Library Edition 是独立扩展版本，不属于当前 Loop Craft 的运行依赖。

必须区分三个对象：

1. 研发仓库：保存 Skill 源文件、Core 实现、测试、Spec、Plan 和证据记录。
2. Loop Craft Skill：可安装、可触发的完整 Skill，本身包含 Core。
3. 运行输出：Loop Craft 被调用后生成的 Evidence Package 和目标产物，例如另一个 Skill、短 Prompt 或 Runtime Artifact。

Loop Craft 是工具 Skill；它生成的 Skill 是用户目标产物。两者虽然都可能使用 Skill 目录格式，但角色不同。

## 3. 目标与范围

Loop Craft 接收三类不同来源的材料，将其统一整理为平台无关的 Behavior Contract 和 0..n 个 Loop Semantic IR，经验证与确定性编译后，分别生成证据包和目标平台产物。

目标：

- 复用三个入口的公共 Loop 判断、IR、验证、编译和交付能力；
- 保留完整 Skill 产物，不把 Skill 强行压缩成短 Prompt；
- 将 Semantic IR 作为语义权威源，避免生成物反向覆盖定义；
- 将 Evidence Package 与干净目标产物物理隔离；
- 支持 Skill、短 Prompt、Runtime 和未来标准格式等并列 Adapter；
- 支持可追溯、可重复、可解释的构建和验证；
- 让未来 Library Edition 只能通过扩展 Adapter 增加 Library 能力。

当前不实现或不纳入首条链路：

- 远程 Registry、Loop Library Catalog、发布和版本解析；
- 完整 Runtime、Scheduler、Hooks 或自动执行服务；
- 多平台 Runtime Adapter 的全集；
- 递归 Subloop、同一 Run 内并行分支和分布式状态；
- 自动覆盖 Semantic IR 的自我修改；
- 用模型自由改写代替确定性 Compiler；
- 为未来兼容提前创建无行为的空模块。

## 4. 总体架构

### 4.1 主流水线

~~~text
入口 1：从零设计 Loop
入口 2：既有 Skill 审计与 Loop 优化
入口 3：对话历史 / 已有工作流蒸馏
                ↓
入口专属抽取与澄清
                ↓
Candidate Behavior Contract
                ↓
公共 Loopability Gate
                ↓
0..n Candidate Loop Semantic IR
                ↓
Candidate Schema + Semantic Validation
                ↓
澄清、用户确认与 Review Gate
                ↓
Accepted Definition
                ↓
Compiler-time Revalidation
                ↓
Deterministic Compiler
                ↓
Final Execution IR
                ├─ Evidence Packager → Evidence Package
                └─ Adapter Router → Skill / Compact Prompt / Runtime
~~~

入口处理器和输出 Adapter 是不同概念：入口处理器负责把原始材料整理成候选定义；Adapter 负责把确认后的 Final Execution IR 投影为目标产物。

### 4.2 Core 与 Skill 的关系

Core 是 Loop Craft Skill 的内部组成部分，不是外部 Python 库或第二个产品：

~~~text
Loop Craft Skill
├─ 交互与入口层
│  ├─ From-scratch Entry
│  ├─ Skill-to-Loop Entry
│  └─ Conversation-to-Workflow Entry
└─ Loop Craft Core
   ├─ Behavior Contract / Loop IR
   ├─ Kernel（平台无关语义与编译约束）
   ├─ Validator
   ├─ Compiler
   ├─ Evidence Packager
   └─ Adapter Router 与默认 Adapters
~~~

Kernel 是 Core 内部更窄的平台无关子集；Core 仍然包含 Evidence 和 Adapter。Kernel 不依赖具体 Adapter，Adapter 只能依赖 Kernel 的公开 Contract。

### 4.3 研发仓库与 Skill 成品

~~~text
Loopcraft开发/
├─ docs/
│  ├─ specs/
│  ├─ plans/
│  ├─ records/
│  └─ references/
├─ loop-craft/
│  ├─ SKILL.md
│  ├─ agents/
│  │  └─ openai.yaml
│  ├─ references/
│  ├─ scripts/
│  │  └─ loopcraft_core/
│  │     ├─ kernel/
│  │     │  ├─ contracts/
│  │     │  ├─ schemas/
│  │     │  ├─ validator/
│  │     │  └─ compiler/
│  │     ├─ evidence/
│  │     └─ adapters/
│  └─ assets/
│     └─ templates/
└─ tests/
~~~

loop-craft 是唯一产品权威源。测试直接验证其中的脚本和资源，不维护一份外部 src 再复制进 Skill，避免双重实现和构建漂移。

Skill 成品不包含 docs、研发计划、原始对话、测试题、测试输出或无关历史。references 只保存运行时需要按需加载的说明；机器 Schema 放在 Core 的 scripts/loopcraft_core/kernel/schemas/，模板放在 assets/。

## 5. 三个输入入口

### 5.1 从零设计 Loop

当前 Loopy 的 Craft、Guided Design 和逐问访谈是迁移候选。入口需要：

- 通过用户对话确认目标、成功证据、范围、权限和停止边界；
- 形成 Candidate Behavior Contract；
- 使用公共 Loopability Gate 判断是否真的需要 Loop；
- 在确认后生成 0..n 个 Loop Semantic IR；
- 不复用 Loopy 名称、Loop Library 查找或发布通道。

如果新反馈不能改变下一步动作，应输出一次性 Workflow 或 keep_as_skill，不能为了“有 Loop”而制造循环。

### 5.2 既有 Skill 优化

当前 Phase 1 的 Skill-to-Loop Upgrade、Loopability Gate 和四类 verdict 是迁移候选。入口需要：

- 只读审计现有 Skill 的调用方式、行为合同、资源、不变量和证据；
- 区分 Observed 与 Inferred；
- 保留完整 Skill 外壳和无关用户工作；
- 判断 Loop 位于 Skill 内部、作为核心能力，还是应拆出多个独立反馈闭环；
- 只有用户批准 verdict、finding IDs 和 Loop boundaries 后才允许修改；
- 由公共 Core 生成最终目标产物。

四类判断：

| Verdict | 含义 | 默认产物 |
|---|---|---|
| keep_as_skill | 没有通过 Loopability Gate | 保持普通 Skill |
| embedded_loop | 支持型 Loop 服务于更大的阶段式 Skill | 完整父 Skill + 内部 Loop |
| loop_first_skill | Loop 是 Skill 的核心能力 | 完整 Loop-first Skill |
| split_into_loops | 多个 Loop 各自追求独立的一等反馈结果 | 父 Skill + 多个 Loop |

旧的 standalone_loop 不是现有 Skill 的默认升级结果；它已由 loop_first_skill 取代。

### 5.3 对话历史到工作流再到 Skill

该入口是新集成，参考 Workflow Skill Creator 的工作流恢复能力，但必须本地化其领域假设。

~~~text
已发生的对话 / 工作记录
→ Observed Workflow Model
→ Progressive Clarification
→ Candidate Behavior Contract
→ 公共 Loopability Gate
→ Loop Semantic IR
→ 生成目标 Skill
~~~

Workflow Model 必须区分：

- observed：材料直接支持的事实；
- inferred：由多个事实合理推断但尚未直接确认的内容；
- proposed：为完成设计而提出、等待用户确认的方案；
- missing / conflict：缺失或相互冲突的信息。

不得把工作流抽取模块变成第二套 Workflow-to-Loop 实现，也不得把 Workflow Skill Creator 的 Science Skills、固定 uv、平台路径或“所有 I/O 都必须 CLI”等假设带入 Loop Craft。

## 6. Candidate、澄清与 Review Gate

三个入口产生的材料都是 Candidate。候选先经过便宜的 Schema 和 Semantic 检查，再进行必要澄清和用户确认；用户确认后锁定为 Accepted Definition，Compiler 在生成前再次复核，复核失败则退回 Review，不生成产物。

候选字段必须保留来源分类：

~~~text
preserved / normalized / inferred / proposed
missing / conflict / ignored / unsupported
~~~

Compiler 不接受仍存在关键 missing 或未解决 conflict 的候选定义。

### Clarification Protocol

1. 先查找现有文件、历史记录、来源版本和可验证证据；
2. 梳理缺口、影响范围和不同解释；
3. 一次只询问一个会改变设计的高价值问题；
4. 问题必须携带背景、来源、缺口、影响和至少一个初步方案；
5. 不得捏造工具、权限、指标、预算、负责人、时间表或用户意图；
6. 收到回答后更新候选摘要，再决定是否仍需追问。

## 7. Loopability Gate

候选阶段只有同时满足以下条件才可以成为 Loop：

1. 每轮产生新证据或新状态；
2. 反馈能够改变下一步选择；
3. 存在可观察、可重复的进展或验收检查；
4. 每轮只执行一个有边界的动作，不静默扩大权限；
5. 成功、Clean no-op、Blocked、Approval required 和 No-progress 能区分；
6. Loop 比一次性任务或固定 Workflow 带来额外价值；
7. 下一轮状态可记录，中断、副作用和恢复有明确处理。

固定检查表、阶段式验证、“失败后理论上可以再修一次”或单纯重复动作，都不足以证明存在 Loop。

## 8. Behavior Contract 与双层 IR

### 8.1 Behavior Contract

Behavior Contract 是平台无关的行为定义，不再以 Skill 文件格式作为 Kernel 权威源。至少覆盖：

- identity、purpose、applicability；
- inputs、outputs、parameters；
- trigger、near miss 和不适用场景；
- 允许和禁止的副作用；
- 成功证据、失败行为和权限边界；
- 普通 Workflow 与 Loop 候选的关系；
- 所需能力、风险、预算和审批；
- 保留不变量和用户确认记录。

对 Loop Craft 生成的目标 Skill 而言，SKILL.md 是 Codex Skill Adapter 的投影；Loop Craft 自身的 SKILL.md 是本产品的入口源文件。两者都不得反向成为通用行为权威源。

### 8.2 Loop Semantic IR

Semantic IR 是 Loop 语义唯一权威源，由人和 Loop Craft 共同维护；平台生成物不能覆盖它。

至少包含：

~~~yaml
schema_version: "0.1"
identity: {}
purpose: {}
applicability: {}
interface: {}
cycle:
  observe: {}
  choose: {}
  act: {}
  verify: {}
  record: {}
  adapt: {}
state: {}
invariants: []
terminal_states: {}
authority: {}
risk: {}
maturity: {}
capabilities: {}
extensions: {}
~~~

### 8.3 Loop Execution IR

Execution IR 是由 Semantic IR 派生的执行计划，回答节点、跳转、条件、状态更新、Checkpoint、Retry、Resume、Rollback、终止映射和 Receipt 映射。

~~~text
Generated Execution IR
→ Typed Execution Override（可选）
→ Final Execution IR
~~~

Override 只能使用类型化白名单，不能删除成功验收、把失败映射为成功、扩大权限、绕过审批、删除强制停止、提高预算或削弱不变量。

### 8.4 条件表达语言

条件使用受限结构化表达，不运行任意代码。来源按可复现性排序：

~~~text
builtin → structured expression → tool_result → evaluator → human_decision → agent_judgment
~~~

Success 不能只依赖无约束的 agent_judgment。条件必须声明输入、输出、可复现性和失败分类。

## 9. Definition、Profile、Instance 与 Run

四层必须分开：

~~~text
Definition
→ Deployment Profile
→ Instance
→ Run
~~~

- Definition：语义和 Loop 结构；
- Deployment Profile：平台、能力绑定、适配策略和默认限制；
- Instance：目标项目、用户确认、预算和运行配置；
- Run：一次不可漂移的执行上下文。

Run 开始后锁定 Definition、Semantic IR、Execution IR、Override、Compiler、Adapter、Profile 和能力摘要。运行中不得浮动升级版本。

### 状态与并发

v0.1 对同一 Run 采用单写者模型，不支持同一 Run 内并行分支。状态更新必须经过原子 Checkpoint；Resume 前重新验证环境、权限、目标和审批有效性。

### Iteration、Retry、Resume

~~~text
Iteration = 新反馈导致的新动作
Retry     = 同一动作因临时错误重试
Resume    = 从 Checkpoint 恢复中断的 Run
~~~

三者分别记录计数、预算、Backoff、幂等性、审批有效期和副作用风险。

### 幂等性与补偿

~~~yaml
action:
  idempotency: idempotent | conditional | non_idempotent
  side_effects: none | local | external
  transaction_boundary: iteration
  compensation:
    available: true
~~~

## 10. Evaluator、结果与错误

Evaluator 的执行状态与最终 verdict 分离；working signal 与 acceptance gate 分离，避免优化目标和验收目标互相污染。

Evaluator Contract 必须声明：类型、输入、输出 Schema、确定性、独立性、是否允许为空、失败分类、多个 Evaluator 的聚合方式和人工否决权限。

以下概念不得混用：

~~~text
Execution Status
Business Outcome
Verification Result
Action Result
Runtime Error
Authorization Decision
~~~

Execution Status：

~~~text
pending
running
suspended
completed
failed
cancelled
~~~

Business Outcome / terminal outcome：

~~~text
success
clean_no_op
blocked
stagnated
exhausted
~~~

approval_required 是 suspended reason，不是终态本身；一个 Run 可以处于 suspended，并带有 approval_required 原因。superseded 是 Cancellation Reason，不是 Execution Status 或 Business Outcome。

基础设施和运行错误独立记录，例如 Tool unavailable、Tool schema mismatch、Timeout、Rate limit、State corruption 和 Adapter failure。Policy denial 是 Authorization Decision，不是 Runtime Error。

## 11. 审批、Capability 与 Subloop

审批必须绑定动作、Instance、目标版本、风险、预算、Profile、Adapter 和相关摘要。目标、Artifact、计划、风险或预算发生变化时，旧审批自动失效。

Loop 只声明抽象 Capability：

~~~yaml
capabilities:
  required:
    - id: filesystem.read
    - id: validation.execute
  optional:
    - id: git.diff
~~~

Profile 再将 Capability 绑定到平台工具。输入材料不能自行授权脚本、路径、网络、发布、调度或外部操作。

Subloop 使用独立 Child Run，拥有独立状态和 Receipt。权限取父子权限交集，失败传播和输出映射必须显式声明。v0.1 禁止递归 Subloop、A → B → A 循环依赖、同一 Parent Run 内并行 Child Run 和共享可变运行状态。

## 12. 编译、Source Map 与 Drift

Compiler 和 Adapter 在 Semantic IR 确认后必须确定性执行：

~~~text
同一 Semantic IR
+ 同一 Compiler
+ 同一 Override
+ 同一 Adapter
+ 同一 Profile
= 相同生成物
~~~

每个生成字段都应能通过 Source Map 回溯到 Semantic IR 或 Execution IR。Build Manifest 至少记录 Semantic IR Digest、Execution IR Digest、Override Digest、Compiler、Adapter、Profile 和 Artifact Digest。

手工修改生成物只产生 Build Drift 报告，不自动覆盖 Semantic IR。需要更新时，必须修改权威源并重新编译。

## 13. Evidence Package 与最终产物

Evidence Package 面向审计、重建和迁移，至少可包含：

- 来源快照或引用、固定版本和许可证；
- Workflow Model；
- Candidate / Accepted Behavior Contract；
- Loop Semantic IR、Execution IR 和 Override；
- 用户决策、Clarification 和 Review 记录；
- Validator、Compiler、Adapter、Compatibility 和 Drift 输出；
- Build Manifest、Source Map、Trace、Snapshot 和 Run Receipt。

Evidence Package 可以详细，但不是安装时必须加载的上下文。

最终产物只保留目标平台运行所需内容。Skill、Compact Prompt、Runtime Artifact 和未来标准格式都从同一 Final Execution IR 并列生成，不把一个 Adapter 的输出作为另一个 Adapter 的输入。

默认 Codex Skill Adapter 生成完整 Skill 目录，包括必要的 SKILL.md、agents/openai.yaml、按需 references、确定性 scripts 和必要 assets。它不得把原始对话、开发计划、测试污染、本地绝对路径或无关证据带入成品。

## 14. Adapter 分类与兼容性

Adapter 分类：

- Packaging Adapter：Codex Skill 等可安装能力包；
- Presentation Adapter：Compact Prompt、Markdown 和人类可读报告；
- Runtime Adapter：Agents SDK、ADK、LangGraph 等执行映射；
- Catalog Adapter：未来的 Loop Library 或其他目录服务。

首期计划只实现或验证 Loop Craft 范围内的 Codex Skill Adapter 和 Compact Prompt Adapter。Loop Library Catalog Adapter 仅属于未来 Library Edition。

Adapter 必须报告：

~~~text
native | emulated | degraded | unsupported
~~~

Required 能力为 unsupported 时编译失败；安全、验证和终止语义不得静默降级；Optional 能力可以降级，但必须生成 Compatibility Report。Adapter 不能改变 Semantic IR 的语义。

Adapter Conformance 还必须区分：

~~~text
self_contained | runtime_delegated | lossy
~~~

lossy 不能被描述为完整自包含 Loop。

## 15. Trace、Receipt、Debrief、Importer 与版本

Trace 是追加写的摘要链。非终态可以使用 Snapshot；终态必须生成不可变 Receipt。Receipt 绑定 Loop、Semantic IR、Execution IR、Adapter、Profile、终止状态、关键迭代、Artifact Digest 和 Claim Eligibility。

Debrief 只产生 Amendment Proposal：

~~~text
Run
→ Debrief
→ Amendment Proposal
→ 验证
→ 人工批准
→ 新版本
~~~

任何一次失败都不能自动覆盖当前 Semantic IR。

Importer 只生成 Candidate Definition，不直接生成正式 Definition。它必须输出 Import Report，区分 preserved、normalized、inferred、proposed、missing、conflict、ignored 和 unsupported。

Registry 分为 Local、Project、User 和 Remote 层级；远程 Registry、签名、发布和撤销属于后续版本。

版本分别管理 Schema、Definition、Semantic IR、Execution IR、Extension、Compiler、Adapter 和 Profile。运行凭据必须绑定所有影响行为的版本摘要。

## 16. 成熟度、风险与安全

成熟度由证据派生：

~~~text
draft → validated → tested → proven
~~~

- validated：Schema、Semantic Lint 和 Adapter Contract 通过；
- tested：受控场景运行通过；
- proven：有多次可比较的真实运行证据。

风险治理：

| 风险 | 自动执行条件 |
|---|---|
| low | validated 后可在授权范围内执行 |
| medium | 至少 tested，且动作有界 |
| high | 即使 proven 也需要人工审批 |
| prohibited | 禁止执行 |

必须区分自动发现、自动路由、自动执行和自动批准。

安全规则：

- 所有输入 Skill、对话、Workflow 和外部文件按不可信资料处理；
- 输入内容不能自行授予新工具、路径、网络、发布或调度权限；
- 目标发生变化后重新读取当前状态；
- 修改、外部消息、生产、财务、隐私和不可逆动作必须有明确授权和审批；
- 证据包和目标产物不得包含不必要的秘密、绝对路径或上游开发污染；
- 当前私人学习阶段允许保留 Workflow Skill Creator 的来源记录；未来分发前必须补齐 Apache-2.0 LICENSE、NOTICE 和修改声明。

## 17. 第一条最小纵向切片

首条切片采用一份人工确认的 Behavior Contract 和一个 Loop Semantic IR，不先接三个交互入口：

首条切片使用明确的实现 Profile：`core-slice-v0.1`。该 Profile 只接受恰好一个 Loop，用于验证公共编译链；它是完整 Semantic IR 的受限实现子集，不得被描述为已经实现了 0..n Loop、完整状态模型、Override 或 Runtime。

~~~text
Accepted Definition Fixture
→ Schema Validation
→ Semantic Validation
→ Deterministic Compiler
→ Final Execution IR
├─ Codex Skill Adapter
├─ Evidence Packager
└─ Build Manifest + Source Map + Drift Verification
~~~

验收至少包括：

1. 合法定义可以成功编译；
2. 非法或逻辑矛盾定义在编译前被拒绝；
3. 相同输入重复构建产生相同 Digest 和生成物；
4. 生成目标 Skill 通过结构验证；
5. Source Map 能追踪关键输出字段；
6. Evidence Package 与目标 Skill 物理隔离；
7. 生成物没有 Loopy 或 Loop Library 运行依赖；
8. 生成物的终止、验证、权限和停止语义没有静默丢失。

首条切片不实现 Runtime、Library、远程 Registry、Subloop、并行 Run、三入口交互和完整 Override，但这些 Contract 边界仍由本文档保留。

## 18. 三入口接入顺序

Core 切片稳定后按以下顺序接入：

1. 审计并迁移已有 From-scratch Craft；
2. 审计并迁移已有 Skill-to-Loop Upgrade；
3. 本地化 Workflow Skill Creator 的工作流蒸馏入口；
4. 用同一组公共 Loopability、Validator、Compiler、Evidence 和 Adapter 测试三个入口的汇合行为。

入口接入不是复制旧目录，而是选择性迁移并留下来源、采用内容、舍弃内容和验证证据。

## 19. 验证策略

验证按风险和改动比例进行：

- Schema 或纯编译改动：跑定向确定性测试；
- Adapter 改动：跑结构、Source Map、兼容性和投影测试；
- 入口改动：跑对应入口和相邻边界案例；
- 纵向切片、阶段出口和发布门槛：跑完整相关链路；
- 只有当下一项检查可能改变当前判断时才扩大范围。

Skill 行为验证使用未见任务和 fresh-context Agent；用户提供的 Skill 和工具仓库是参考资料，不是测试题。测试 Agent 不得看到预期答案、旧失败或修复意图。

最小行为场景包括：成功、Clean no-op、Blocked、Approval required、Stagnated、Exhausted、Runtime Error、Retry、Resume 和目标过期。

## 20. 旧方案迁移声明

以下旧表述不再作为当前设计的一部分：

- Loopcraft Clean 作为正式产品名称；正式产品名为 Loop Craft；
- Core 位于 Skill 外部的双重源码结构；Core 必须包含在 loop-craft；
- Skill Contract 作为 Kernel 的通用权威源；统一使用 Behavior Contract；
- standalone_loop 作为既有 Skill 升级的默认结果；使用 loop_first_skill；
- Loopy 或 Loop Library 作为 Loop Craft 的运行依赖；
- 让某一个 Adapter 生成物成为另一个 Adapter 的输入；
- 把短 Prompt、SKILL.md 或目录条目当作 Loop 的语义权威源；
- 把 approval_required 当作最终终态；它是 suspended reason。

## 21. 完成标准

阶段 2 设计在以下条件满足时视为完成：

- 三个入口的职责、来源和汇合边界明确；
- Behavior Contract、Semantic IR、Execution IR 和 Final Execution IR 的权威关系明确；
- Definition、Profile、Instance、Run 的版本锁定规则明确；
- 状态、Retry、Resume、审批、错误、Subloop、Capability 和副作用边界明确；
- Evidence Package 与最终产物隔离规则明确；
- Adapter 分类、兼容性、Conformance 和 Drift 规则明确；
- Loop Craft Skill 与未来 Library Edition 的依赖方向明确；
- 第一条最小纵向切片和比例化验证策略明确；
- Spec 自检无未处理的占位符、矛盾术语和未授权范围扩张。
