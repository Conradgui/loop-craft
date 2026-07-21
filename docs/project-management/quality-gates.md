# Loop Craft 质量门槛

> 基线日期：2026-07-20
> 使用方式：按顺序记录 `OPEN / 部分完成 / 待执行验证 / 待质量审查 / 质量阻塞 / 已验证（子任务） / PASS / FAIL / WAIVED`；子任务状态只覆盖列出的范围；没有命令输出、测试结果或明确审查结论时不得写 `PASS`。

| Gate | 对应风险 | 必须满足 | 证据 | 当前状态 |
|---|---|---|---|---|
| G-01 执行前置 | R-005 | 获得 Git 初始化、隔离 branch/worktree、目录命名及依赖环境的批准；确认 Python、pytest、jsonschema 版本；不擅自安装、复制或移动资源。 | 用户已确认整份操作清单：保留 ASCII 路径 `C:\Users\Administrator\Documents\loopcraft`、项目显示名“Loopcraft开发”、创建隔离 worktree、使用现有依赖且不安装。`main` 跟踪 `origin/main`；feature worktree 已创建并跟踪 `origin/feature/core-vertical-slice`；版本已确认 | PASS（仅执行前置门槛） |
| G-02 输入契约与范围 | R-001、R-002 | 在代码/Schema/证据中明确首条切片是 Accepted Definition 的受限子集；首条切片明确一个 Loop，或实现并测试空/多 Loop；不得宣称完整 Semantic IR、Runtime 或三入口已完成。 | G-02-T1 至 G-02-T5 已验证；Task 5 只投影干净目标 Skill，并明确排除 Evidence、Runtime、Library 与后续范围 | 部分验证（Task 1-5 已验证；后续范围 OPEN） |
| G-03 编译与 Source Map | R-002、R-003 | 重复构建产生相同 IR、artifact 和摘要；每个关键生成字段、当前 Profile 的 Loop 和元数据都有可回溯映射；Manifest 明确 Semantic IR、Execution IR、Override/no-override、Compiler、Adapter、Profile、Artifact 摘要。 | Task 4 Compiler、Task 5 Adapter、Task 6 Manifest、Task 7 deterministic dual-build 与 Task 8 clean/drift 摘要核对子范围已验证 | 部分完成（Compiler + Adapter + Manifest + 双构建 + drift 子范围） |
| G-04 产物与证据隔离 | R-003、R-004 | artifact 与 evidence 为兄弟目录；证据绑定 artifact digest；Adapter/Evidence 任一中途失败不留下可被误用的部分输出；漂移验证不修改 artifact。 | Task 6 已验证隔离/摘要绑定/写入前拒绝；Task 7 已验证 staging 与部分失败路径；Task 8 已验证非破坏性 drift、唯一 artifact 根条目及直接 symlink 读取边界。普通已有输出、Evidence 写入中途失败、强杀与非本地 FS 仍无证据 | 部分完成（Task 6-8 子范围；不得关闭） |
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

### G-02-T5 子门槛

| 子门槛 | 范围 | 证据 | 状态 |
|---|---|---|---|
| Task 5：Codex Skill Adapter | Final Execution IR 到干净目标 Skill 的确定性投影；单行 JSON literal Markdown 边界；8-byte big-endian 长度前缀目录摘要；coarse/fine Adapter Source Map；terminal stop precedence；不包含 Evidence、Runtime 或 Library | `db4e4b2` + `c282fc6`；规格/代码质量复审均 `Approved`，无 Critical/Important；主控 fresh Python 3.13 定向 `8 passed`、全量 `38 passed`，静态检查通过；feature worktree clean | 已验证（子任务） |

官方 validator 的证据边界：主控在修复前的 rich fixture 上独立确认 `quick_validate.py` 输出 `Skill is valid!`；修复后的 hardened injection fixture validator 只有实现 Agent 的结果，因此不登记为主控独立验证。Task 5 的“已验证”以 fresh 定向/全量测试、静态检查和两项复审为依据；R-010 的 HTML rendering Minor 不阻塞当前 Markdown Adapter。

Task 5 的“已验证”不关闭全局 G-02，也不提前关闭 G-03、G-04 或 G-05。Evidence Package、Build Manifest、跨目录隔离、双构建、drift 验证、Runtime、Library 和阶段出口仍需后续任务证据。

### Task 6 子门槛

| 子门槛 | 范围 | 证据 | 状态 |
|---|---|---|---|
| Task 6：Evidence Package 与 Build Manifest | artifact/Evidence 物理隔离；五份 canonical JSON + LF；definition、完整 semantic subset、Execution IR、Profile、Adapter、artifact digest 与 no-override Manifest 绑定；四类 `mkdir` 前拒绝 | `826f285` + `475b2a4`；规格/代码质量复审均 `Approved`，无规格偏差、Critical 或 Important；主控 fresh Python 3.13 定向 `6 passed`、全量 `44 passed`；`git diff --check` 通过；feature worktree clean | 已验证（子任务） |

Task 6 的“已验证”只确认 Evidence/Manifest 生成与写入前输入边界。R-011 为不阻塞的浅可变 Source Map Minor；Pipeline 原子提交、写入中途失败、双构建、drift 和阶段出口仍未验证，因此 G-04 不关闭，G-05 保持 `OPEN`。

### Task 7 子门槛

| 子门槛 | 范围 | 证据 | 状态 |
|---|---|---|---|
| Task 7：End-to-End Pipeline 与薄 CLI | output parent 内 staging；Adapter → Evidence → final replace；双构建相同；非法定义/Adapter 失败无正式 output；dangling symlink 占用保护；CLI 仅两个位置参数 | `8253c24` + `6d295ab`；规格/代码质量复审均 `Approved`，无 Critical/Important；主控 fresh integration `4 passed`、全量 `48 passed`；真实 CLI 退出 0 并生成 artifact 3/Evidence 5 文件；`git diff --check` 通过；两个 worktree clean | 已验证（子任务） |

Task 7 的 symlink Minor 已由回归测试和 `exists() or is_symlink()` 修复关闭。R-012 在 Task 7 快照中保留测试权限、CLI 自动化、普通已有输出/Evidence 部分写、强杀与非本地 FS 原子性边界；其中 CLI 自动化已由 Task 8 关闭，其余缺口不阻塞当前子任务，但 G-04 不关闭，G-05 保持 `OPEN`。

### Task 8 子门槛

| 子门槛 | 范围 | 证据 | 状态 |
|---|---|---|---|
| Task 8：Build Drift Verification | 非破坏性 clean/drift 摘要核对；artifact root 唯一真实 Skill 目录；额外根条目拒绝；output/Evidence/Manifest/artifact tree 直接 symlink 在读取前拒绝；真实 CLI build/verify JSON 与退出码 | `b5f4ebe` + `077a540` + `220669e` + `4474f48` + `2ec976a`；规格/代码质量最终复审均 `Approved`，无 Critical/Important；主控 fresh 定向 `14 passed`、全量 `58 passed`；`git diff --check` 通过；feature worktree clean | 已验证（子任务） |

Task 8 的 drift 验证不写回 artifact/Evidence，也不提供自动修复。测试辅助快照只能证明内容未改变，不能单独证明从未读取或元数据未变；实现顺序已静态确认直接 symlink 在读取前拒绝。普通已有输出、Evidence 写入中途失败、强杀和非本地 FS 原子性仍未验证，因此 G-04 保持部分完成，G-05 保持 `OPEN`。

### Plan 勘误基线

`main` 提交 `1b7fb10` 已更新后续验收：Task 3 在单 Loop Profile 下删除 duplicate 检查；Task 4/5 强化确定性、完整投影/Source Map 与 quoted safe frontmatter；Task 6 digest 覆盖完整 core subset。Task 8 的原始预期计数 4 已由最终 14 个 drift + pipeline/CLI 测试取代。这里只记录计划门槛，不代表未执行任务已实现。

## 不作为当前门槛的范围

Runtime、Scheduler、Hooks、递归/并行 Subloop、远程 Registry、Library Edition、三入口交互和完整 Override 是 Spec/Plan 明确的后续范围；它们在本切片中应保持未实现且不得被产品 Skill 宣称支持。
