# Loop Craft 决策日志

> 基线日期：2026-07-20
> 维护规则：只追加已确认决策、可复核证据和明确的未决项；本日志不覆盖 Spec、Plan 或生产代码。

## 权威与范围

- `docs/specs/2026-07-20-loop-craft-phase-2-design.md`：状态为 `Approved`，版本 `0.1.0`。它是阶段 2 的架构、协议边界和验收权威源。
- `docs/plans/2026-07-20-loop-craft-core-vertical-slice.md`：按当前任务授权，作为 Core 首条纵向切片的已批准 Active Plan，执行顺序受 Spec 约束。计划文件自身未声明独立版本或批准字段，因此不把计划文本中的“Expected”当作已发生证据。
- `docs/records/2026-07-20-resource-reuse-strategy.md` 与 `docs/references/resource-registry.yaml`：资源复用边界和来源索引；外部资料不得取代批准的 Spec。

## 已确认决策

### D-001 首条切片范围

首条切片只覆盖人工确认的 Accepted Definition 到 Schema/Semantic Validation、Deterministic Compiler、Final Execution IR、Codex Skill Adapter、Evidence Package、Build Manifest、Source Map 和 Drift Verification。三个交互入口、Runtime、Override、Subloop、Registry、Library Edition、发布和多平台 Adapter 明确不在本计划内。

证据：Spec §17、Plan §Scope / §Spec Coverage Boundary。

### D-002 产品源码边界

生产代码必须位于可安装 `loop-craft` Skill 的 `scripts/loopcraft_core` 下，测试直接导入该目录；不建立一份独立 `src` 再复制，以避免双重实现和构建漂移。

证据：Spec §4.3、Plan §File Map / Ownership。

### D-003 Git 与环境是执行前置门槛

Plan 要求在实施前先列出并获得批准：初始化 Git、是否重命名目录、隔离 branch/worktree、确认 Python/pytest/jsonschema 环境。首次基线检查时 `git status --short` 返回 `fatal: not a git repository`；后续已创建基线提交 `effd60b35d1ff438a75d6827d779011d433099f0`（短 SHA：`effd60b`，`docs: establish Loop Craft project baseline`）。当前仍在 `main`，尚无额外隔离 branch/worktree。Python `3.13.13`、pytest `9.0.3`、jsonschema `4.26.0` 已核对；安装/复制外部资源仍保持待批准状态。

### D-004 资源记录中的过时陈述

资源复用记录 §13 第 237 行此前称“阶段 2 最终 Spec 尚未写入”，现已更新为“阶段 2 最终 Spec 已写入并批准”；此前陈述已成为 `stale`，本 Agent 不修改原记录，后续以批准 Spec 为准。第 238 行的 Git 未初始化陈述因后续 `git init` 也已过时，实际状态以进度日志中的命令证据为准。

## 未决项

- 是否完成隔离分支/worktree，以及是否将当前目录更名；基线 commit `effd60b` 已创建，但隔离工作区仍未完成。
- Accepted Definition 的受限子集边界已写入修订后的 Spec/Plan；仍需 Schema、fixture、产品 Skill 和执行记录的测试证据，见 `risk-register.md` 的 `R-001`。
- 五项 P1 质量门槛关闭前，不得把计划中的 Expected 或模板结果写成执行完成。
