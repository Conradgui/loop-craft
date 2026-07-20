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

Plan 要求在实施前先列出并获得批准：初始化 Git、目录命名、隔离 branch/worktree、确认 Python/pytest/jsonschema 环境。用户已明确批准整份操作清单：保留本地 ASCII 路径 `C:\Users\Administrator\Documents\loopcraft`，项目显示名使用“Loopcraft开发”，创建隔离 worktree，并使用现有依赖而不安装新依赖。基线提交 `effd60b` 已由治理更新提交 `5a38ec7` 承接；`main` 跟踪 `origin/main`，远程 `origin` 为 `https://github.com/Conradgui/loop-craft.git`。`feature/core-vertical-slice` worktree 创建于 `C:\Users\Administrator\Documents\loopcraft\.worktrees\core-vertical-slice`，初始 HEAD 为 `5a38ec7`，当前跟踪 `origin/feature/core-vertical-slice`。Python `3.13.13`、pytest `9.0.3`、jsonschema `4.26.0` 已核对。G-01 因此满足；该结论只表示执行前置门槛通过，不表示任何实现或测试通过。

### D-004 资源记录中的过时陈述

资源复用记录 §13 第 237 行此前称“阶段 2 最终 Spec 尚未写入”，现已更新为“阶段 2 最终 Spec 已写入并批准”；此前陈述已成为 `stale`，本 Agent 不修改原记录，后续以批准 Spec 为准。第 238 行已记录 `effd60b` 和“尚未创建远程仓库”；远程已在本次复核中确认并推送 `main`，该部分陈述也已过时，实际状态以本日志和命令证据为准。

### D-005 Task 1 验证边界

Task 1（确定性序列化测试基础）已在 `feature/core-vertical-slice` 分支通过独立定向验证：提交链包含 `ab9116c`、`d95e4e3`、`8d811db`，`python -m pytest tests/unit/test_canonical.py -q` 输出 `4 passed in 0.02s`，worktree clean。该决策只确认 canonical serialization/harness 的当前子范围，不扩大为 Schema、Compiler、Adapter、Evidence 或阶段出口已完成；规格审查通过和代码质量审查 `Approved` 作为当前里程碑审查结论记录，后续任务仍需独立证据。

## 未决项

- Accepted Definition 的受限子集边界已写入修订后的 Spec/Plan；仍需 Schema、fixture、产品 Skill 和执行记录的测试证据，见 `risk-register.md` 的 `R-001`。
- 五项 P1 质量门槛关闭前，不得把计划中的 Expected 或模板结果写成执行完成。
