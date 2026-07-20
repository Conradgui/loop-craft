# Loop Craft 风险登记表

> 基线日期：2026-07-20
> 严重度定义：P1 = 首条切片开始或验收前必须关闭；P2 = 不阻塞当前切片但需排期；P0 = 当前未发现。

| ID | 严重度 | 风险与证据 | 影响 | 关闭门槛 / 状态 |
|---|---|---|---|---|
| R-001 | P1 | Spec §17 与 Plan §Scope 已引入 `core-slice-v0.1`：只接受一个 Loop，并明确它是完整 Semantic IR 的受限实现子集，不代表 0..n、完整状态、Override 或 Runtime。Task 2 `e21c970` 已实现并通过规格审查。 | 规格与定向 Schema 验证已有证据；代码质量审查未完成，产品 Skill、Evidence 和阶段出口仍未验证。 | 保留边界声明；完成质量审查并补产品/执行证据。当前：部分验证，仍 OPEN。 |
| R-002 | P1 | Plan schema 已设置 `loops.minItems = 1`、`maxItems = 1`；Task 2 的 0/2 Loop 负例纳入联合命令并通过。Adapter workflow Source Map 仍属于后续任务。 | Schema 层空/多 Loop 约束已有定向证据；Adapter/Source Map 和所有关键输出字段仍未验证。 | 完成代码质量审查、Adapter/Source Map 测试和阶段出口核对。当前：部分验证，仍 OPEN。 |
| R-003 | P1 | Plan 的 Manifest 已加入 `semantic_ir_digest`、`override_mode: none`、`override_digest: null`，并补充对应测试断言。 | 静态契约已能区分受限 Semantic IR、Execution IR 与无 Override 状态；尚未有生成文件证明。 | 待运行 Evidence Package、双构建和 Manifest 断言。当前：待执行验证。 |
| R-004 | P1 | Plan 已改用同父目录 `TemporaryDirectory` 进行 staging，成功后以 `Path.replace` 提交；并规划 Adapter 注入失败后输出目录不存在的测试。 | 设计上已避免 Adapter/Evidence 写入中途留下正式输出；异常路径和平台文件系统行为尚未实跑。 | 待运行 Adapter 失败测试和端到端构建；Evidence 失败注入作为残余边界检查。当前：待执行验证。 |
| R-005 | P1 | 用户已确认本地 ASCII 路径、项目显示名、隔离 worktree 和不安装新依赖；`main` 与 `feature/core-vertical-slice` 均有远程 tracking，执行环境版本已核对。 | 执行前置条件已有用户确认和命令证据。 | 仅表示执行前置门槛满足，不代表实现或测试完成。当前：已关闭（对应 G-01 PASS）。 |
| R-006 | P1 | Task 2 首次代码质量审查因服务返回 HTTP 503 未形成结论，重试审查进行中。 | Task 2 无法在质量结论缺失时关闭，后续任务状态可能被误报。 | 等待重试审查的明确结论；期间 Task 2 保持待质量审查。当前：OPEN。 |

## 当前判断

- 本次审查未发现 P0。
- R-001、R-002 已有 Task 2 的规格/定向测试部分证据，但代码质量和后续适配器范围仍 OPEN。
- R-005 已关闭为执行前置门槛；不代表生产链路完成。
- R-006 因质量审查 503 保持 OPEN，Task 2 不得标为完成。
- 资源复用记录 §13 第 237 行已更新为“阶段 2 最终 Spec 已写入并批准”；此前的 `stale` 已消除。第 238 行“Git 仓库尚未初始化”因后续 `git init` 已成为新的过时状态，本日志以实际 Git 命令为准。
