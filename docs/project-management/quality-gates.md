# Loop Craft 质量门槛

> 基线日期：2026-07-20
> 使用方式：按顺序记录 `OPEN / 部分完成 / 待执行验证 / 待质量审查 / 质量阻塞 / 已验证（子任务） / PASS / FAIL / WAIVED`；子任务状态只覆盖列出的范围；没有命令输出、测试结果或明确审查结论时不得写 `PASS`。

| Gate | 对应风险 | 必须满足 | 证据 | 当前状态 |
|---|---|---|---|---|
| G-01 执行前置 | R-005 | 获得 Git 初始化、隔离 branch/worktree、目录命名及依赖环境的批准；确认 Python、pytest、jsonschema 版本；不擅自安装、复制或移动资源。 | 用户已确认整份操作清单：保留 ASCII 路径 `C:\Users\Administrator\Documents\loopcraft`、项目显示名“Loopcraft开发”、创建隔离 worktree、使用现有依赖且不安装。`main` 跟踪 `origin/main`；feature worktree 已创建并跟踪 `origin/feature/core-vertical-slice`；版本已确认 | PASS（仅执行前置门槛） |
| G-02 输入契约与范围 | R-001、R-002 | 在代码/Schema/证据中明确首条切片是 Accepted Definition 的受限子集；首条切片明确一个 Loop，或实现并测试空/多 Loop；不得宣称完整 Semantic IR、Runtime 或三入口已完成。 | G-02-T1 至 G-02-T4 已验证；Task 4 编译前复用 schema → canonical → semantic validation，并验证 Compiler/Source Map 子范围；Adapter 及后续范围仍未完成 | 部分验证（Task 1-4 已验证；后续范围 OPEN） |
| G-03 编译与 Source Map | R-002、R-003 | 重复构建产生相同 IR、artifact 和摘要；每个关键生成字段、当前 Profile 的 Loop 和元数据都有可回溯映射；Manifest 明确 Semantic IR、Execution IR、Override/no-override、Compiler、Adapter、Profile、Artifact 摘要。 | Task 4 的 Compiler/语义 Source Map 子范围已验证；Adapter、Manifest、artifact 摘要和两次独立构建仍无执行证据 | 部分完成（Compiler 子范围；其余待执行） |
| G-04 产物与证据隔离 | R-003、R-004 | artifact 与 evidence 为兄弟目录；证据绑定 artifact digest；Adapter/Evidence 任一中途失败不留下可被误用的部分输出；漂移验证不修改 artifact。 | Plan 勘误 `1b7fb10` 已要求 Task 6 digest 覆盖完整 core subset，并将 Task 8 预期修正为 4；尚无实现/执行证据 | 待执行验证 |
| G-05 阶段出口 | R-001..R-005 | 完整相关测试、官方 Skill 结构校验、两次独立构建、clean/drift 验证、禁用词/依赖残留扫描全部有原始输出；执行记录只在全部通过后创建。 | `docs/records/2026-07-20-core-vertical-slice-execution.md` 及 build evidence | OPEN |

### G-02-T1 子门槛

| 子门槛 | 范围 | 证据 | 状态 |
|---|---|---|---|
| Task 1：确定性序列化测试基础 | canonical JSON 字节序列、SHA-256、NaN 拒绝及测试 harness；不包含 Schema、Compiler、Adapter、Evidence 或 Runtime | `8d811db`（含 `ab9116c`、`d95e4e3`）；独立运行 `python -m pytest tests/unit/test_canonical.py -q`：`4 passed in 0.02s`；隔离 worktree clean | 已验证（子任务） |

Task 1 的“已验证”不改变全局 G-02、G-03、G-04 或 G-05 的状态；后续任务必须分别提供命令和原始输出。

### G-02-T2 子门槛

| 子门槛 | 范围 | 证据 | 状态 |
|---|---|---|---|
| Task 2：Accepted Definition Schema 与基础语义校验 | Profile/单 Loop Schema、缺失字段、0/2 Loop 负例、canonical/identifier/text/JSON Pointer 边界和基础 authority 语义校验 | `a65f3b2`（基线 `8d811db`）；规格/代码质量复审均 Approved；全量 `21 passed in 0.14s`；定向 `21 passed in 0.13s`；Schema check 与 `git diff --check` 通过 | 已验证（子任务） |

Task 2 的“已验证”不覆盖 Task 3、Compiler、Adapter、Evidence、Pipeline 或阶段出口。保留 Minor：非法输入的原始 jsonschema `error.message` 可能受键插入顺序影响，当前延后且不阻塞有效定义确定性验收。

### G-02-T3 子门槛

| 子门槛 | 范围 | 证据 | 状态 |
|---|---|---|---|
| Task 3：Semantic Validation | 三组 authority 两两交叉检查、schema → canonical → semantic 顺序及 surrogate + authority overlap 错误边界；当前单 Loop Profile 不实现 `duplicate_loop_id` | `5299f81` + `2da604d`；规格/代码质量复审均 `Approved`，无 Critical/Important；全量与 validation + canonical 定向回归均为 `25 passed`；Schema check 与 `git diff --check` 通过 | 已验证（子任务） |

Task 3 的“已验证”只覆盖当前 `core-slice-v0.1` 的语义校验与 canonical 边界；不覆盖 Compiler、Adapter、Evidence、Pipeline、完整 Semantic IR 或阶段出口。质量复审 Agent 未能在其 PATH 环境运行 pytest，测试证据来自主控在 feature worktree 的独立执行。

### G-02-T4 子门槛

| 子门槛 | 范围 | 证据 | 状态 |
|---|---|---|---|
| Task 4：Deterministic Compiler 与语义 Source Map | 递归字典键重排确定性、输入 `deepcopy` 隔离、invalid definition 先验证、Final Execution IR 核心字段投影和 Source Map 完整性；`compiler_version` 为生成元数据且不伪造语义映射 | `61e9bbc`；规格/代码质量审查均 `Approved`，无 Critical/Important；compiler 定向 `5 passed`、validation + canonical + compiler 组合 `30 passed`、全量 `30 passed`；Schema check 与 `git diff --check` 通过；feature worktree clean | 已验证（子任务） |

Task 4 的“已验证”只覆盖 Compiler 与当前 `core-slice-v0.1` 的语义 Source Map。R-009 为不阻塞的 Minor；Adapter、Evidence、Manifest、重复构建、Runtime、Pipeline 和阶段出口仍未验证，因此全局 G-02 仍为部分验证，G-03、G-04、G-05 不提前关闭。

### Plan 勘误基线

`main` 提交 `1b7fb10` 已更新后续验收：Task 3 在单 Loop Profile 下删除 duplicate 检查；Task 4/5 强化确定性、完整投影/Source Map 与 quoted safe frontmatter；Task 6 digest 覆盖完整 core subset；Task 8 预期为 4。这里只记录计划门槛，不代表这些任务已实现。

## 不作为当前门槛的范围

Runtime、Scheduler、Hooks、递归/并行 Subloop、远程 Registry、Library Edition、三入口交互和完整 Override 是 Spec/Plan 明确的后续范围；它们在本切片中应保持未实现且不得被产品 Skill 宣称支持。
