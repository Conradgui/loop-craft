# Loop Craft 风险登记表

> 基线日期：2026-07-20
> 严重度定义：P1 = 首条切片开始或验收前必须关闭；P2 = 不阻塞当前切片但需排期；P0 = 当前未发现。

| ID | 严重度 | 风险与证据 | 影响 | 关闭门槛 / 状态 |
|---|---|---|---|---|
| R-001 | P1 | Spec §17 与 Plan §Scope 已引入 `core-slice-v0.1`：只接受一个 Loop，并明确它是完整 Semantic IR 的受限实现子集。Task 2 修复提交 `a65f3b2` 已通过规格与代码质量复审。 | Task 2 的 Schema/validation 子范围已有完整里程碑证据；产品 Skill、Evidence 和阶段出口仍未验证。 | 保留边界声明并补后续产品/执行证据。当前：Task 2 子范围已验证，整体仍 OPEN。 |
| R-002 | P1 | Plan schema 已设置 `loops.minItems = 1`、`maxItems = 1`；Task 2 的 0/2 Loop 负例和输入边界已验证。Adapter workflow Source Map 仍属于后续任务。 | Schema 层空/多 Loop 约束已有证据；Adapter/Source Map 和所有关键输出字段仍未验证。 | 完成 Adapter/Source Map 测试和阶段出口核对。当前：Schema 子范围已验证，整体仍 OPEN。 |
| R-003 | P1 | Plan 的 Manifest 已加入 `semantic_ir_digest`、`override_mode: none`、`override_digest: null`，并补充对应测试断言。 | 静态契约已能区分受限 Semantic IR、Execution IR 与无 Override 状态；尚未有生成文件证明。 | 待运行 Evidence Package、双构建和 Manifest 断言。当前：待执行验证。 |
| R-004 | P1 | Plan 已改用同父目录 `TemporaryDirectory` 进行 staging，成功后以 `Path.replace` 提交；并规划 Adapter 注入失败后输出目录不存在的测试。 | 设计上已避免 Adapter/Evidence 写入中途留下正式输出；异常路径和平台文件系统行为尚未实跑。 | 待运行 Adapter 失败测试和端到端构建；Evidence 失败注入作为残余边界检查。当前：待执行验证。 |
| R-005 | P1 | 用户已确认本地 ASCII 路径、项目显示名、隔离 worktree 和不安装新依赖；`main` 与 `feature/core-vertical-slice` 均有远程 tracking，执行环境版本已核对。 | 执行前置条件已有用户确认和命令证据。 | 仅表示执行前置门槛满足，不代表实现或测试完成。当前：已关闭（对应 G-01 PASS）。 |
| R-006 | P1 | Task 2 首次代码质量审查因 HTTP 503 无结论；后续重试审查已完成并给出 `Approved`。 | 原阻塞已解除。 | 当前：已关闭。 |
| R-007 | P2 | `validation.py` 直接保留 jsonschema 的 `error.message`；对包含多个非法键的输入，消息文本可能受键插入顺序影响。 | 可能影响非法输入诊断文本的完全确定性；当前不影响有效定义编译输入的确定性验收。 | 在稳定诊断协议时改为结构化、排序后的自有消息；当前：deferred，非 Task 2 阻塞项。 |
| R-008 | P1 | Task 3 `5299f81` 曾在 semantic authority overlap 检查后才执行 canonical 校验；同一孤立 surrogate 跨 authority 集合重叠时，错误文本格式化可能触发 `UnicodeEncodeError`。修复提交 `2da604d` 已改为 schema → canonical → semantic，并增加组合回归。 | 原问题会把稳定验证错误变成非预期编码异常；修复后非 canonical 输入在进入语义检查前被拒绝。 | 规格/代码质量复审均 `Approved`；全量与 validation + canonical 定向回归均为 `25 passed`；Schema 元校验和 `git diff --check` 通过。当前：已关闭。 |

## 当前判断

- 本次审查未发现 P0。
- R-001、R-002 的 Task 2 Schema/validation 子范围已验证，后续 Adapter/产物范围仍 OPEN。
- R-005 已关闭为执行前置门槛；不代表生产链路完成。
- R-006 已由重试审查 `Approved` 关闭。
- `a65f3b2` 已关闭四个 Important：surrogate canonical boundary、identifier trailing controls、blank/whitespace fields、RFC 6901 root；`id.maxLength = 64` 已获规格认可。
- R-007 为保留的 Minor，不阻塞 Task 2；不得因此宣称非法输入诊断已完全确定。
- R-008 已由 `2da604d`、surrogate + authority overlap 回归和最终复审关闭；这只解除 Task 3 阻塞，不表示 Compiler、Adapter、Evidence、Pipeline 或纵向切片出口已完成。
- 资源复用记录 §13 第 237 行已更新为“阶段 2 最终 Spec 已写入并批准”；此前的 `stale` 已消除。第 238 行“Git 仓库尚未初始化”因后续 `git init` 已成为新的过时状态，本日志以实际 Git 命令为准。
