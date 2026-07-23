# Loop Craft 风险登记表

> 基线日期：2026-07-20
> 严重度定义：P1 = 首条切片开始或验收前必须关闭；P2 = 不阻塞当前切片但需排期；P0 = 当前未发现。

| ID | 严重度 | 风险与证据 | 影响 | 关闭门槛 / 状态 |
|---|---|---|---|---|
| R-001 | P1 | `core-slice-v0.1` 的受限单 Loop 边界贯穿 Schema、产品 Skill、执行记录和最终复审；Task 10 在最终代码 SHA 上完成 fresh 出口。 | 当前切片可被误报为完整阶段 2 的风险由边界声明和门槛名称约束；真实 forward experiment 延后不改变结构/构建出口结论。 | 最终规格/质量复审 Approved，110 tests 与完整执行记录通过。当前：已关闭（仅 Core vertical slice）。 |
| R-002 | P1 | 0/2 Loop 负例、完整 Adapter/Source Map、全部触发条件投影和目标限制均有回归；未实现能力不进入产品声明。 | 当前 Profile 的单 Loop 契约及平台投影可复核；不能外推为完整 Semantic IR 或多 Loop Runtime。 | Task 10 边界复核通过。当前：已关闭（仅 `core-slice-v0.1`）。 |
| R-003 | P1 | Manifest 绑定 definition、semantic IR、Execution IR、Source Map、Validation Report、Profile、Adapter 和 artifact；六个摘要合同严格校验。 | Evidence 缺失、畸形、失败状态或摘要漂移会被拒绝；双构建和 verify 提供最终确定性证据。 | 两棵 8 文件树逐字节一致、双 verify clean。当前：已关闭。 |
| R-004 | P1 | Adapter 失败、Evidence 第 2-5 次写入失败、普通已有 output、空 artifact、symlink 和非破坏性 drift 均有自动回归；Pipeline 仅在完整 staging 后提交。 | 已测试的本地文件系统失败路径不会留下可误用正式 output；强杀/非本地 FS 不外推。 | G-04 对当前本地 Core slice PASS；剩余系统级原子性归入 R-012 P2。当前：已关闭（当前切片）。 |
| R-005 | P1 | 用户已确认本地 ASCII 路径、项目显示名、隔离 worktree 和不安装新依赖；`main` 与 `feature/core-vertical-slice` 均有远程 tracking，执行环境版本已核对。 | 执行前置条件已有用户确认和命令证据。 | 仅表示执行前置门槛满足，不代表实现或测试完成。当前：已关闭（对应 G-01 PASS）。 |
| R-007 | P2 | `validation.py` 直接保留 jsonschema 的 `error.message`；对包含多个非法键的输入，消息文本可能受键插入顺序影响。 | 可能影响非法输入诊断文本的完全确定性；当前不影响有效定义编译输入的确定性验收。 | 在稳定诊断协议时改为结构化、排序后的自有消息；当前：deferred，非 Task 2 阻塞项。 |
| R-008 | P1 | Task 3 `5299f81` 曾在 semantic authority overlap 检查后才执行 canonical 校验；同一孤立 surrogate 跨 authority 集合重叠时，错误文本格式化可能触发 `UnicodeEncodeError`。修复提交 `2da604d` 已改为 schema → canonical → semantic，并增加组合回归。 | 原问题会把稳定验证错误变成非预期编码异常；修复后非 canonical 输入在进入语义检查前被拒绝。 | 规格/代码质量复审均 `Approved`；全量与 validation + canonical 定向回归均为 `25 passed`；Schema 元校验和 `git diff --check` 通过。当前：已关闭。 |
| R-009 | P2 | `tests/unit/test_compiler.py` 当前只断言两个递归重排输入产生相同 `definition_digest`，未直接断言该字段等于 `sha256_digest(definition)`；实现当前确实使用 canonical digest。 | 当前实现行为正确且其余确定性测试通过，但回归测试没有把该字段直接锚定到 canonical digest 契约。 | Task 4 保持通过、不阻塞；后续增强测试为 `assert result.final_execution_ir["definition_digest"] == sha256_digest(definition)`。当前：deferred。 |
| R-010 | P2 | Task 5 已把 Markdown 正文中的自由文本编码为单行 JSON string literal，关闭多行 Markdown 结构注入；但 JSON literal 仍会原样保留 `<...>`。 | 当前 Skill 以 Markdown 文件交付且官方结构校验通过，不影响本切片；未来若把不可信文本直接送入允许原始 HTML 的渲染器，仍需独立的输出 sanitization。 | 在引入不可信 HTML 渲染目标时由对应 Adapter 增加并测试上下文相关 sanitization；当前为 Minor、deferred，不阻塞 Task 5。 |
| R-011 | P2 | `SkillArtifact` dataclass 虽 frozen，但 `artifact.source_map` 是浅可变字典；调用方可在 render 后、Evidence 写出前修改其内容。Manifest 现在会绑定实际写出的 Source Map 摘要，但不阻止内部调用方在打包前改变映射。 | 当前 Pipeline 立即传递且最终 Evidence 摘要可核对；未来开放插件调用或延迟传递时仍可能产生语义上错误但内部一致的 Source Map。 | 扩大调用边界前改为深不可变快照/防御性复制。当前：Minor、deferred，不阻塞 Core slice。 |
| R-012 | P2 | 普通已有 output、Evidence 第 2-5 次写入失败、CLI、symlink 和 drift 回归现已自动化。强杀和非本地文件系统的 `replace` 原子性仍未验证；`file_snapshot` 只能证明内容未改变，不能单独证明从未读取或元数据未变。 | 当前本地文件系统的正常与已测试失败路径有证据；结果不能外推为进程强杀、远程挂载或完整访问监控保证。 | 部署到非本地 FS 或要求 crash consistency 前单独验证。当前：P2 deferred，不阻塞 Core slice。 |
| R-013 | P1 | 三入口曾使用不同 Gate，Conversation Entry Evidence 曾为 manifest-unbound。唯一 Gate、共享 Candidate Review、`entry-evidence-v0.1`、Manifest digest/type 和动态 verify 已完成。 | 同一候选不再因入口不同而使用不同 Gate；来源摘要与批准记录可以随 build 验证。 | 入口合同、Entry Evidence、source+entry 组合和路径边界定向验证通过，独立质量复核 Approved。当前：已关闭。 |
| R-014 | P1 | 公共仓库已有 README 和项目描述，但没有项目许可证或 NOTICE；Resource Registry 记录了 Apache-2.0/MIT 来源边界。 | 外部访问者可以阅读代码，但不能据此推断再分发授权；发布与复用边界不完整。 | 项目所有者明确选择许可证，添加匹配的 LICENSE/NOTICE，并复核上游归属。当前：OPEN。 |
| R-015 | P1 | 三入口、Packaging 和 Entry Evidence 已接通，但尚未使用一个真实用户目标完成调用、澄清、批准、build、Skill + Evidence 交付。 | 结构与定向测试不能替代真实用户体验；阶段出口仍不可批准。 | 完成一次用户授权的真实 Demo，验证产物可调用、Evidence clean、Artifact 无私密来源材料。当前：OPEN。 |
| R-016 | P2 | 公共仓库尚无 GitHub Actions；当前验证由本地定向命令和人工记录承担。 | 外部提交没有自动结构/回归门，长期可能产生发布漂移。 | 在首次 Demo 后添加与本地命令一致的最小 Windows/Linux CI。当前：deferred，不阻塞首次 Demo。 |

## 当前判断

- 本次审查未发现 P0。
- R-001 至 R-004 的当前 Core slice P1 已由 Task 10 关闭；真实 forward behavioral experiment 仍按用户决定延后，不能据此外推完整阶段 2。
- R-005 已关闭为执行前置门槛；不代表生产链路完成。
- `a65f3b2` 已关闭四个 Important：surrogate canonical boundary、identifier trailing controls、blank/whitespace fields、RFC 6901 root；`id.maxLength = 64` 已获规格认可。
- R-007 为保留的 Minor，不阻塞 Task 2；不得因此宣称非法输入诊断已完全确定。
- R-008 已由 `2da604d`、surrogate + authority overlap 回归和最终复审关闭；这只解除 Task 3 阻塞，不表示 Compiler、Adapter、Evidence、Pipeline 或纵向切片出口已完成。
- R-009 是代码质量审查保留的 Minor；不阻塞 Task 4，但后续应补充 `definition_digest` 对 canonical digest 的直接契约断言。
- R-010 是 Task 5 保留的 HTML rendering Minor；单行 JSON literal 已关闭 Markdown 结构注入，但不应被误写为通用 HTML sanitization。当前不阻塞 Task 5。
- R-011 是浅可变 Source Map 的 Minor；新增摘要关闭了未绑定漂移，但没有把调用对象变为深不可变，扩大调用边界前仍需处理。
- R-012 只保留强杀、非本地文件系统原子性和完整访问监控的 P2 residual；普通已有 output 与 Evidence 部分写失败缺口已关闭。
- R-013 已由共享 Gate、Entry Evidence Manifest binding 和独立质量复核关闭。
- R-014 是当前唯一需要项目所有者选择的公共交付 P1；README 不把“无许可证”误写为开源授权。
- R-015 保持 OPEN，直到真实用户 Demo 完成；定向测试和 skeleton 不替代该门槛。
- R-016 为首次 Demo 后的 P2 自动化工作，不抢占当前用户链路。
- 资源复用记录 §13 第 237 行已更新为“阶段 2 最终 Spec 已写入并批准”；此前的 `stale` 已消除。第 238 行“Git 仓库尚未初始化”因后续 `git init` 已成为新的过时状态，本日志以实际 Git 命令为准。
