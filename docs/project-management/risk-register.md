# Loop Craft 风险登记表

> 基线日期：2026-07-20
> 严重度定义：P1 = 首条切片开始或验收前必须关闭；P2 = 不阻塞当前切片但需排期；P0 = 当前未发现。

| ID | 严重度 | 风险与证据 | 影响 | 关闭门槛 / 状态 |
|---|---|---|---|---|
| R-001 | P1 | Spec §17 与 Plan §Scope 已引入 `core-slice-v0.1`：只接受一个 Loop，并明确它是完整 Semantic IR 的受限实现子集，不代表 0..n、完整状态、Override 或 Runtime。 | 设计歧义已实质修订；若实现或成品省略 Profile/边界声明，仍可能产生过度完成声明。 | 静态修订已核对；待 Schema、fixture、产品 Skill 和执行记录的测试证据。当前：待执行验证。 |
| R-002 | P1 | Plan schema 已设置 `loops.minItems = 1`、`maxItems = 1`，并规划 0/2 Loop 负例；Adapter workflow Source Map 已按 `execution["loops"]` 动态生成。 | 原先空 Loop 与固定 `/loops/0` 的设计缺口已修订；生成元数据的细粒度映射覆盖仍需在阶段出口核对。 | 待运行 Schema 负例、Adapter/Source Map 测试，并检查所有关键输出字段的映射。当前：待执行验证。 |
| R-003 | P1 | Plan 的 Manifest 已加入 `semantic_ir_digest`、`override_mode: none`、`override_digest: null`，并补充对应测试断言。 | 静态契约已能区分受限 Semantic IR、Execution IR 与无 Override 状态；尚未有生成文件证明。 | 待运行 Evidence Package、双构建和 Manifest 断言。当前：待执行验证。 |
| R-004 | P1 | Plan 已改用同父目录 `TemporaryDirectory` 进行 staging，成功后以 `Path.replace` 提交；并规划 Adapter 注入失败后输出目录不存在的测试。 | 设计上已避免 Adapter/Evidence 写入中途留下正式输出；异常路径和平台文件系统行为尚未实跑。 | 待运行 Adapter 失败测试和端到端构建；Evidence 失败注入作为残余边界检查。当前：待执行验证。 |
| R-005 | P1 | Git 已初始化；`git status --porcelain=v2 --branch` 显示 `branch.oid (initial)`、`branch.head main`，`.gitignore` 与 `docs/` 未跟踪。Python `3.13.13`、pytest `9.0.3`、jsonschema `4.26.0` 已核对；尚无 commit，也没有额外隔离 branch/worktree。 | 环境漂移风险已降低，但没有初始提交和隔离工作区时仍缺少可回滚、可审计的实施起点。 | 完成批准记录、初始 commit 与隔离 branch/worktree 后再关闭。当前：部分完成，仍 OPEN。 |

## 当前判断

- 本次审查未发现 P0。
- R-001 至 R-004 已完成 Spec/Plan 层修订，状态进入“待执行验证”；这不等于实现或测试通过。
- R-005 只完成 Git 初始化和环境版本核对；初始 commit 与额外隔离 worktree/branch 尚未完成。
- 资源复用记录 §13 第 237 行已更新为“阶段 2 最终 Spec 已写入并批准”；此前的 `stale` 已消除。第 238 行“Git 仓库尚未初始化”因后续 `git init` 已成为新的过时状态，本日志以实际 Git 命令为准。
