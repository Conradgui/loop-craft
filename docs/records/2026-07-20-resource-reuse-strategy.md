# Loopcraft 资源复用与文档治理策略

> 状态：阶段 2 设计记录 v0.1  
> 日期：2026-07-20  
> 机器可读索引：[resource-registry.yaml](../references/resource-registry.yaml)
> 项目用途：当前阶段仅用于私人学习、研究和参考；若以后进入复制、分发或发布，再启用相应许可证与发布门槛。

## 1. 目的

这份记录回答四个问题：每项资源解决什么问题、哪个场景优先使用它、具体复用哪一部分、哪些内容不得进入 Loopcraft。目标不是把材料堆进上下文，而是让后续 Agent 能按模块选择最小充分参考集，并能从 Spec、Plan 和执行记录追溯每个决定。

## 2. 文档体系与权威顺序

Loopcraft 使用四类文档，各自只承担一种职责：

| 文档类型 | 回答的问题 | 可以覆盖什么 | 不可以覆盖什么 |
|---|---|---|---|
| Spec / ADR | 系统必须是什么、为什么这样设计 | 外部参考和旧基线 | 已验证事实本身 |
| Plan | 以什么顺序实现和验证 | 任务顺序与检查点 | 已批准的 Spec |
| Record | 实际做了什么、看到了什么证据 | 旧的执行状态 | Spec 或来源内容 |
| Reference Index | 哪些来源可在什么边界内复用 | 浮动链接和口头记忆 | Loopcraft 的最终决策 |

发生冲突时按以下顺序裁决：

```text
Approved Spec / ADR
> Active Plan
> Reproducible Record / Evidence
> Registered Reference
> Handoff Claim / Conversation History
```

外部项目即使质量很高，也只能影响 Spec，不能直接成为 Kernel 的隐式权威。

## 3. 主流水线与资源进入点

```text
分：三类输入入口
├─ 从零设计 Loop
├─ 既有 Skill 分析与 Loop 优化
└─ 对话历史 → 工作流蒸馏

总：统一 Kernel 流水线
Behavior Contract + 0..n Loop IR
→ Validator
→ Deterministic Compiler
→ Final Execution IR

分：两类交付
├─ Evidence Packager → 证据包
└─ Adapter Router → Skill / 短 Prompt / Runtime / 未来标准格式
```

输入阶段可以包含模型判断；Behavior Contract 和 Loop IR 经用户确认并固定摘要后，Compiler、Evidence Packager 和 Adapter 必须确定性执行。

三个入口不是相同的开发起点：

| 入口 | 当前起点 | 正确工作方式 |
|---|---|---|
| 从零设计 Loop | 当前 Loopy 已有 Craft / Guided Design 和访谈逻辑 | 审计、去 Library 耦合、改名、迁移并按新 Spec 加固，不从空白重写 |
| 既有 Skill 优化 | 当前 Phase 1 已有 Skill-to-Loop Upgrade、Loopability Gate 和四类 verdict | 独立复核、补齐可重跑证据、迁移到 Behavior Contract，不从空白重写 |
| 对话历史蒸馏 | Workflow Skill Creator 提供高质量来源，但尚未接入 Loopcraft | 本地化抽取模块，再复用公共 Loopability 和 Skill 生产模块 |

`existing_candidate` 只表示有可迁移实现，不表示已经通过阶段 2 Schema、Compiler、Adapter 或行为验收。

## 4. 三个入口如何复用资源

### 4.1 从零设计 Loop

**实现起点：** 当前 `phase1-handoff-package` 中已经存在 Craft / Guided Design 和逐问访谈路径，不重新从零构建。  
**历史主参考：** `loopy-original-readme-extract` 的目标访谈、Craft、Audit、Run 和 Debrief 逻辑。  
**工程增强：** `skill-creator-pro` 的 Behavior Contract、trigger/near miss、输入状态、副作用、成功证据和失败行为。  
**写作约束：** `skill-writing-guidelines` 的流程可预测性、可观察门槛、渐进披露和持续剪枝。  
**架构约束：** 已批准的 Loopcraft Spec，而不是 Loopy 文件结构。

复用顺序：

```text
Loopy 的成熟交互经验
→ 审计当前 Craft 实现
→ Skill Creator Pro 的行为合同
→ Loopcraft 的 Loopability Gate 和 Loop IR
```

这里的任务是选择性迁移和加固，而不是重写。仍不得轻信现有实现：必须检查它是否保留新的状态、审批、Evidence Package、确定性编译和 Adapter 边界。不得复用 Loopy 名称、Loop Library 查找/发布通道或“短 Prompt 就是 Loop 本体”的旧假设。

### 4.2 既有 Skill 优化为带 Loop 的 Skill

**实现起点：** 当前 Phase 1 已经实现 `Skill-to-Loop Upgrade`、完整 `upgrade-skill.md`、Loopability Gate 和四类 verdict，不重新从零构建。  
**独立复核责任人：** `skill-polisher`。先以 Review 模式验证现有行为合同、调用方、历史不变量、沉积层和证据边界，不能因交接文档声称完成就跳过。  
**Loop 判断：** 选择性迁移 `phase1-baseline-v1` 与 `phase1-handoff-package` 中的 Loopability Gate，以当前确认的四类结果为准：普通 Workflow、Embedded Loop、Loop-first、Multiple Loops。  
**最小原地改进：** 继续由 Skill Polisher 的 Polish/Recheck 路线负责。  
**完整重建或新身份：** 将 Behavior Contract 和保护不变量交给 `skill-creator-pro`，再生成新的 Skill-facing 产物。

这条入口必须允许“没有合适 Loop”的结论。没有反馈改变下一动作、真实验证器和停止边界时，不强塞 Loop。

### 4.3 从对话历史蒸馏工作流，再生成 Skill 和 Loop

**抽取主参考：** `workflow-skill-creator`。高保真复用它的已发生工作流总结、渐进问答、严格/灵活步骤、依赖资源、错误路径和先设计后实现门槛。  
**必须本地化：** 删除 Science Skills bundle、固定 `uv`、平台安装路径、任何 I/O 都必须新建 CLI、测试可选等领域假设。  
**统一出口：** 抽取模块只生成带 `observed / inferred / proposed` 标签的 Workflow Model 和 Candidate Behavior Contract；之后必须复用入口 4.2 的公共 Loopability Gate，不单独实现 Workflow-to-Loop 逻辑。  
**Skill 生产化：** 进入 `skill-creator-pro` 的信息层级、结构验证、质量 lint 和 fresh-context 前向测试。

Workflow Skill Creator 是生产工具来源，不是测试题、fixture 或最终输出模板。

## 5. 模块级资源所有权

| Loopcraft 模块/场景 | 首要资源 | 精确复用内容 | 辅助资源 | 禁止混入 |
|---|---|---|---|---|
| `entry/from-scratch` | Loopy README 摘录 | 访谈、Craft、Audit、有限 Run、Debrief | Creator Pro、写作指南 | Library 通道、Loopy 品牌 |
| `entry/skill-upgrade` | Skill Polisher | Review/Polish/Recheck、比例证据、living contract、不变量/沉积 | Phase 1 基线与实现 | Creator Pro 直接跳过现状审查 |
| `entry/conversation-distiller` | Workflow Skill Creator | 工作流恢复、渐进澄清、严格/灵活步骤、依赖与设计批准 | Creator Pro | Science bundle、固定 CLI/uv 假设 |
| `core/behavior-contract` | 当前批准设计 | 目的、接口、路由、普通步骤、行为边界 | Creator Pro 的合同字段 | Codex `openai.yaml` 字段 |
| `core/loopability` | Phase 1 + 当前批准设计 | 反馈、验证、状态、停止、权限判断 | Loopy discover/audit | Library 查重依赖 |
| `core/semantic-ir` | Phase 2 Spec | Loop 语义、不变量、权限、Evaluator、Outcome | 02 基线作为问题清单 | 外部 Skill 的文件格式 |
| `compiler` | Phase 2 Spec | 双层 IR、版本锁、确定性编译、Source Map | 02 基线 | 模型自由改写、Loopy 运行逻辑 |
| `evidence-packager` | Phase 2 Spec | 来源、决策、验证、Build Manifest、Trace/Receipt | Creator Pro、Polisher | 平台产物目录 |
| `adapter/codex-skill` | Skill Creator Pro | 最小完整 Skill、资源层级、metadata、validator、quality lint | 官方 Creator 仅作兼容底线 | Kernel 内部证据和开发记录 |
| `adapter/compact-prompt` | Loopy 原始行为 | 紧凑调用表达 | 02 基线的投影模型 | 宣称自包含完整 Loop |
| `adapter/runtime` | Phase 2 Spec | Capability Binding、状态和执行图映射 | 平台官方规范 | 修改 Semantic IR |
| `adapter/future-standard` | Phase 2 Spec | Core/Extension/Vendor 映射、Compatibility Report | 写作指南的平台翻译原则 | 直接替换权威 Definition |
| `adapter/library-catalog` | Loopy/Loop Library 历史 | Catalog、查找、版本与发布集成 | Library Edition Spec | Loopcraft Clean / Kernel |
| Skill 写作审查 | Skill Writing Guidelines | 十二原则、证据边界、仓库工程 | Creator Pro lint | 把启发式当行为证据 |
| 既有发布漂移 | Skill Polisher | source/repository/published/installed 分层 | Creator Pro release gate | 用本地 clean 推断已发布 |
| 新 Skill 首次发布 | Skill Creator Pro | identity、license、CI、fresh clone、installer 验证 | 写作指南仓库工程 | 未授权远端写操作 |

## 6. 两类交付的隔离规则

### Evidence Package

证据包保存来源快照或引用、Workflow Model、Behavior Contract、Loop IR、决策、验证输出、Compatibility Report、Build Manifest、Source Map、许可证和后续 Run Receipt。它面向审计、重建和迁移，可以详细，但不得成为安装时必须加载的上下文负担。

### Final Artifact Set

最终产物只保留目标平台运行所需内容。Skill、短 Prompt、Runtime Artifact 或未来标准格式都从同一 Final Execution IR 独立生成，不以另一 Adapter 的产物为输入。

“干净”表示不含原始对话、开发笔记、测试污染、本地绝对路径、上游 `vendor/` 快照和无关证据；不表示删除运行必需脚本、参考文件或许可证义务。若复制 Apache-2.0 或 MIT 代码，产物仍须保留适用的 License、NOTICE、版权和修改声明。

## 7. 精确文件与条件加载索引

| 资源 | 只在什么场景读取 | 精确文件或章节 | 复用目标 |
|---|---|---|---|
| Loop 工程与写作指导 | 需要恢复某项架构决定的理由或比较旧方案时 | “定义/部署/实例/运行”“条件表达语言”“Subloop”“状态、Retry/Resume”“Evaluator”“错误/审批”“工具契约”“可重复编译”“Importer/Conformance”相关章节 | 决策历史和问题清单，不复制结论 |
| 01 Phase 1 基线 | 实现或验收 Skill-to-Loop 入口时 | §7 Skill Contract 提取、§8 Loopability Gate、§9 四类输出、§12 测试设计、§13 验收标准 | 恢复原始需求，再按当前术语迁移 |
| 02 Phase 2 基线 | 编写对应 Kernel/Compiler/Adapter Spec 时 | §5 双层 IR、§6 Override、§7 扩展、§8 四层运行模型、§14-17 Adapter/审计、§18-33 各协议 | 作为章节覆盖清单，不直接实现字段 |
| Loopy README 摘录 | 从零入口、短 Prompt Adapter、Library Edition 边界 | “What Loopy does”“Discover”“Run and improve”“完整闭环”“Loopy 与 Loop Library 的流转逻辑” | 复用交互与产品历史，隔离 Library 依赖 |
| Phase 1 handoff | 独立复核、选择性迁移 Phase 1 | `loopy/SKILL.md`、`loopy/references/upgrade-skill.md`、`docs/IMPLEMENTATION-HANDOFF.md`、`docs/TESTING-HANDOFF.md` | 审计实现与声明；前两者是代码/行为候选，后两者是待验证交接证据 |
| Workflow Skill Creator | 第三入口从已发生对话恢复工作流 | `SKILL.md` Phase 1 Rounds 1-4、Brainstorming Completion Criteria、Phase 2 Skill Design；只有确认需要确定性 CLI 时才读 `references/cli_script_template.py` | 高保真本地化工作流蒸馏，不默认采用 Phase 3 的领域假设 |
| Skill Polisher | 既有 Skill review、最小改进、recheck 或发布漂移 | `SKILL.md` Process 1-6；修改时读 `references/polish-and-recheck.md`；发布副本不一致时读 `references/release-drift.md` | 现状证据、最小改动、稳定 finding 和漂移审计 |
| Skill Creator Pro | 新 Skill、完整重建、Skill Adapter 或首次发布 | `SKILL.md` Steps 1-8；Skill 产物用 `scripts/init_skill.py`、`quick_validate.py`、`quality_lint.py`；复杂集合设计读 `references/predictable-skill-design.md`；仅发布时读 `references/release-engineering.md` | 新 Skill 的行为合同、最小结构、机械验证、前向测试与发布门槛 |
| Skill Writing Guidelines | 写/审 Spec、Skill 或仓库结构时的横切检查 | `skills/skill-writing-guidelines/SKILL.md` §§1-6；归因时读 `references/evidence-boundary.md`；写作细则读 `GUIDELINES.md`；发布结构读 `REPOSITORY_ENGINEERING.zh.md` | 检查职责、门槛、渐进披露、证据比例和仓库边界 |
| Official Codex Skill Creator | Creator Pro 与当前 Codex harness 发生兼容疑问时 | Installed `SKILL.md` 的 Anatomy、Progressive Disclosure、frontmatter、`openai.yaml` 和 validator 约束 | 只裁决平台兼容，不拥有创建流程 |

## 8. 每项资源的使用决策

### Loop 工程与写作指导

用作研究笔记、决策演化和外部阅读线索。它包含多个阶段的对话和后来已被修正的建议，因此不得作为最终 Schema 或验收权威；正式 Spec 应提炼结论，而不是复制整份对话。

### 01 Phase 1 基线

保留原始范围、Loopability Gate 和测试分类。`standalone_loop`、普遍性的 `Skill Contract` 等旧决定必须通过当前 Spec 显式迁移，不能让旧术语重新进入实现。

### 02 Phase 2 基线

用作完整问题清单和双层 IR 种子。Terminal/Error、Approval、Subloop、Override、Behavior Contract 和多 Adapter 输出采用当前逐段批准结果；最终阶段 2 Spec 将取代它的架构权威地位。

### Loopy 原始 README 与当前交接包

原始 README 提供行为历史；当前交接包提供 Phase 1 实现证据。两者都只做选择性迁移：前者不能带入 Library 耦合，后者必须先经过独立验收，不能按目录整体复制。

### Workflow Skill Creator

只拥有“已完成工作流的恢复和抽象”。本地副本与上游固定提交内容一致，但缺少随目录保存的 Apache LICENSE。由于当前项目明确只用于私人学习和参考，这不是当前阻塞项；保留来源与许可证记录即可。只有以后把代码或修改版复制进可分发 `vendor/`、成品或公开仓库时，才必须补齐许可证、Google 版权、来源版本和修改声明。它不拥有从零创建、Loopability 或最终 Skill 生产化。

### Skill Polisher

只拥有既有 Skill 生命周期。它提供现状审查、证据边界、最小补丁和 release drift；当工作变成新身份或完整重建时，必须交给 Skill Creator Pro。

### Skill Creator Pro

作为新 Skill 创建与首次发布的主工具，替代官方 Skill Creator 的主流程地位。它只进入 Skill-facing 入口和 Adapter，不能定义 Kernel。官方 Skill Creator 仅保留为当前 Codex 格式和 validator 的兼容底线。

### Matt Pocock Inspired Skill Writing

作为横切写作和仓库工程参考，负责检查流程可预测性、职责所有权、门槛、渐进披露和重复沉积。其十二条结构是独立归纳，不得归因成 Matt Pocock 的官方框架，也不能代替实际行为测试。

## 9. 实践时的最小参考加载协议

每个实施任务按以下顺序开始：

1. 读取当前模块对应的已批准 Spec 和 ADR。
2. 读取 Active Plan 中当前任务、文件边界和验收命令。
3. 在资源注册表中查找该模块，只加载“首要资源”和必要辅助资源。
4. 在执行记录中写下资源 ID、固定 revision/hash、实际采用部分和主动舍弃部分。
5. 复制代码或模板前检查许可证和修改声明；只借鉴思想时记录为 inspiration。
6. 先写能失败的确定性测试或结构检查，再实现最小功能。
7. 完成后记录原始命令、输出摘要、差异、未执行检查和残余风险。

这个协议防止两类浪费：把所有资源一次性塞进上下文，以及让多个高质量项目重复拥有同一职责。

## 10. 验证与测试资源规则

- 用户提供的 Skill 和仓库是工具或参考来源，不是端到端测试题。
- Schema、Compiler、Source Map、Capability Binding 和 Adapter Contract 使用确定性 fixtures。
- Skill 行为测试使用另外设计的未见任务；开发中只用 fresh-context Agent 验证逻辑边界。
- Fresh-context Agent 只收到任务局部输入、待测产物和必要环境，不收到预期答案、旧失败或开发意图。
- 测试通过只能支持其覆盖范围内的声明；结构校验不能冒充行为验证。

## 11. 来源漂移与更新规则

- 所有远程资源固定 commit；实践中不得直接使用浮动 `main` 作为可复现输入。
- 本地文件通过 SHA-256 识别。摘要变化后先生成 Reference Drift Record，再决定是否升级索引。
- 更新外部资源不得自动修改 Spec、Plan 或实现；必须先做影响分析。
- 资源升级需要记录新增能力、破坏性变化、许可证变化、受影响模块和需要重跑的验证。
- 当前 handoff 在新仓库完成隔离前保持只读。

## 12. 当前已冻结的资源决策

1. 从零设计 Loop 已有 Loopy Craft 实现候选，工作方式是审计、解耦、迁移和加固，不从空白重写。
2. 既有 Skill 优化已有 Phase 1 实现候选，工作方式是独立复核、补证和迁移，不从空白重写。
3. `Skill Creator Pro` 是新 Skill 创建、重建、验证和首次发布的首要来源。
4. `Skill Polisher` 是既有 Skill 审查、最小改进和 release drift 的首要来源。
5. `Workflow Skill Creator` 是第三入口工作流蒸馏的首要来源。
6. Matt 指南是横切写作参考，不拥有执行流程。
7. `Behavior Contract + 0..n Loop IR` 是 Kernel 的通用 Definition，不以 Skill 格式为中心。
8. Evidence Packager 与 Adapter Router 并列；证据包和干净产物物理隔离、摘要关联。
9. Loopcraft Clean 不包含 Loopy 或 Loop Library 运行依赖；Library Edition 以后通过 Catalog Adapter 增量加入。

## 13. 已知证据缺口与处理动作

| 缺口 | 当前影响 | 处理动作 |
|---|---|---|
| Phase 1 测试只有汇总，没有 fixtures 和原始输出 | 不能独立宣称完成 | 新仓库中重建确定性 fixtures 和可重跑命令 |
| Workflow Skill Creator 本地摘录缺少 LICENSE | 对当前私人学习和参考不构成阻塞；尚不能据此准备公开分发包 | 当前保留来源/许可证记录；只有 vendoring、分发或发布前再补齐 LICENSE、NOTICE 和修改声明 |
| 外部三个仓库尚未进入本地 vendor | 当前只能按固定远程 commit 引用 | Spec 确认后列出复制清单并征得用户确认再执行 |
| 阶段 2 最终 Spec 已写入并批准 | 当前设计已有统一书面权威 | 后续实现必须以 `docs/specs/2026-07-20-loop-craft-phase-2-design.md` 为准，变更需追加 ADR 或修订记录 |
| 独立 Loopcraft Git 仓库与远程已建立 | `origin` 为 `https://github.com/Conradgui/loop-craft.git`，`main` 与隔离实现分支分别承载治理和实现 | 实现工作只在获批的隔离 worktree 分支推进，已审查提交持续同步远程，并在记录中绑定实际提交与验证证据 |

完成标准：未来 Agent 可以仅凭本记录和注册表，为任一模块找到唯一主参考、固定来源版本、允许复用内容、禁止边界以及需要留下的证据。
