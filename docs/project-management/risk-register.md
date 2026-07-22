# Loop Craft 风险登记表

> 基线日期：2026-07-20
> 严重度定义：P1 = 首条切片开始或验收前必须关闭；P2 = 不阻塞当前切片但需排期；P0 = 当前未发现。

| ID | 严重度 | 风险与证据 | 影响 | 关闭门槛 / 状态 |
|---|---|---|---|---|
| R-001 | P1 | Spec §17 与 Plan §Scope 已引入 `core-slice-v0.1`：只接受一个 Loop，并明确它是完整 Semantic IR 的受限实现子集。Task 2 修复提交 `a65f3b2` 已通过规格与代码质量复审；Task 9 三次提交已锁定产品 Skill 的 accepted JSON build / existing build drift verify 边界。 | Schema/validation、Evidence/Manifest、Pipeline、drift 和产品 Skill 子范围已有里程碑证据；真实 forward behavioral test 与阶段出口仍未验证。 | 保留边界声明并补 Task 10 执行证据。当前：Task 2/6-9 子范围已验证，整体仍 OPEN。 |
| R-002 | P1 | Plan schema 已设置 `loops.minItems = 1`、`maxItems = 1`；Task 2 的 0/2 Loop 负例和输入边界已验证；Task 5 Adapter workflow Source Map 与 Task 9 产品 Skill 声明边界已通过复审。 | 当前 Profile 的 Schema、Adapter/Source Map 与产品 Skill 子范围已有证据；真实 forward behavioral test、完整阶段出口和未实现能力仍不能外推。 | 在 Task 10 核对完整阶段出口并保持不越界宣称。当前：Schema + Adapter + Product Skill 子范围已验证，整体仍 OPEN。 |
| R-003 | P1 | Task 6 已验证 Manifest 关键绑定；Task 7 两次 Pipeline 构建的完整文件树和 Manifest 相同；Task 8 已验证 clean/drift 摘要核对。 | 单次绑定、deterministic dual-build 与 drift 子范围已有执行证据；最终阶段出口仍未验证。 | Task 6-8 子范围已验证；待完成产品包装与阶段出口核对。当前：整体仍 OPEN。 |
| R-004 | P1 | Task 6 已验证写入前隔离/摘要拒绝；Task 7 已验证 staging 与部分失败路径；Task 8 已验证非破坏性 drift、唯一 artifact 根条目和直接 symlink 读取边界。 | 正常提交、已测试失败路径和 drift 不写回已有证据；普通已有输出、Evidence 写入中途失败、强杀和非本地 FS 原子性仍未验证。 | Task 6-8 子范围已验证；待补剩余失败路径与阶段出口。当前：部分验证，整体仍 OPEN。 |
| R-005 | P1 | 用户已确认本地 ASCII 路径、项目显示名、隔离 worktree 和不安装新依赖；`main` 与 `feature/core-vertical-slice` 均有远程 tracking，执行环境版本已核对。 | 执行前置条件已有用户确认和命令证据。 | 仅表示执行前置门槛满足，不代表实现或测试完成。当前：已关闭（对应 G-01 PASS）。 |
| R-007 | P2 | `validation.py` 直接保留 jsonschema 的 `error.message`；对包含多个非法键的输入，消息文本可能受键插入顺序影响。 | 可能影响非法输入诊断文本的完全确定性；当前不影响有效定义编译输入的确定性验收。 | 在稳定诊断协议时改为结构化、排序后的自有消息；当前：deferred，非 Task 2 阻塞项。 |
| R-008 | P1 | Task 3 `5299f81` 曾在 semantic authority overlap 检查后才执行 canonical 校验；同一孤立 surrogate 跨 authority 集合重叠时，错误文本格式化可能触发 `UnicodeEncodeError`。修复提交 `2da604d` 已改为 schema → canonical → semantic，并增加组合回归。 | 原问题会把稳定验证错误变成非预期编码异常；修复后非 canonical 输入在进入语义检查前被拒绝。 | 规格/代码质量复审均 `Approved`；全量与 validation + canonical 定向回归均为 `25 passed`；Schema 元校验和 `git diff --check` 通过。当前：已关闭。 |
| R-009 | P2 | `tests/unit/test_compiler.py` 当前只断言两个递归重排输入产生相同 `definition_digest`，未直接断言该字段等于 `sha256_digest(definition)`；实现当前确实使用 canonical digest。 | 当前实现行为正确且其余确定性测试通过，但回归测试没有把该字段直接锚定到 canonical digest 契约。 | Task 4 保持通过、不阻塞；后续增强测试为 `assert result.final_execution_ir["definition_digest"] == sha256_digest(definition)`。当前：deferred。 |
| R-010 | P2 | Task 5 已把 Markdown 正文中的自由文本编码为单行 JSON string literal，关闭多行 Markdown 结构注入；但 JSON literal 仍会原样保留 `<...>`。 | 当前 Skill 以 Markdown 文件交付且官方结构校验通过，不影响本切片；未来若把不可信文本直接送入允许原始 HTML 的渲染器，仍需独立的输出 sanitization。 | 在引入不可信 HTML 渲染目标时由对应 Adapter 增加并测试上下文相关 sanitization；当前为 Minor、deferred，不阻塞 Task 5。 |
| R-011 | P2 | `SkillArtifact` dataclass 虽 frozen，但 `artifact.source_map` 是浅可变字典；调用方可在 render 后、Evidence 写出前修改其内容。 | 当前内部流程立即把 artifact 传给 Evidence Packager，且 Task 6 没有 Source Map 自身摘要契约，因此已验证路径不受影响；未来开放插件调用或延迟传递时可能形成未绑定的 Source Map 漂移。 | 在建立 Source Map 独立摘要契约或开放外部调用边界时改为深不可变快照/防御性复制并加测试。当前：Minor、deferred，不阻塞 Task 6。 |
| R-012 | P2 | Task 7-8 的 CLI、symlink 和 drift 回归已自动化；Task 9 补充了产品 Skill 结构、相对 reference 链接及从 Skill 目录运行 build/verify 的安装命令边界。普通已有输出与 Evidence 部分写失败、强杀及非本地文件系统的 replace 原子性仍未验证。`file_snapshot` 只能证明内容未改变，不能单独证明未读取或元数据未变。 | 当前本地文件系统的正常路径、非法定义、Adapter 失败、dangling symlink、直接 symlink drift、真实 CLI 和产品 Skill 结构/命令合同已有证据；剩余故障模式不能外推为更强原子性或访问证明。 | 后续把普通已有输出和 Evidence 写失败纳入自动测试；部署到非本地 FS 前验证 replace 语义。当前：Task 9 结构/命令边界已验证，故障 residual deferred，不阻塞 Task 9。 |

## 当前判断

- 本次审查未发现 P0。
- R-001 的 Task 2 Schema/validation、Task 6-8 Core build 与 Task 9 产品 Skill 子范围已验证；真实 forward behavioral test 与阶段出口仍 OPEN。
- R-005 已关闭为执行前置门槛；不代表生产链路完成。
- `a65f3b2` 已关闭四个 Important：surrogate canonical boundary、identifier trailing controls、blank/whitespace fields、RFC 6901 root；`id.maxLength = 64` 已获规格认可。
- R-007 为保留的 Minor，不阻塞 Task 2；不得因此宣称非法输入诊断已完全确定。
- R-008 已由 `2da604d`、surrogate + authority overlap 回归和最终复审关闭；这只解除 Task 3 阻塞，不表示 Compiler、Adapter、Evidence、Pipeline 或纵向切片出口已完成。
- R-009 是代码质量审查保留的 Minor；不阻塞 Task 4，但后续应补充 `definition_digest` 对 canonical digest 的直接契约断言。
- R-010 是 Task 5 保留的 HTML rendering Minor；单行 JSON literal 已关闭 Markdown 结构注入，但不应被误写为通用 HTML sanitization。当前不阻塞 Task 5。
- R-011 是 Task 6 保留的浅可变 Source Map Minor；当前内部立即传递和无 Source Map 摘要契约的边界下不阻塞，扩大调用边界前必须重新评估。
- R-012 合并记录 Task 7-9 的结构、命令与剩余故障边界；直接 symlink、CLI 和产品 Skill 安装命令缺口已关闭，但不得把本地结果外推为强杀、非本地文件系统原子性或完整访问监控保证。
- 资源复用记录 §13 第 237 行已更新为“阶段 2 最终 Spec 已写入并批准”；此前的 `stale` 已消除。第 238 行“Git 仓库尚未初始化”因后续 `git init` 已成为新的过时状态，本日志以实际 Git 命令为准。
