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
| R-015 | P1 | 三入口、Packaging 和 Entry Evidence 已接通，但尚未使用一个真实用户目标完成调用、澄清、批准、build、Skill + Evidence 交付。 | 结构与定向测试不能替代真实用户体验；阶段出口仍不可批准。 | `project-asset-inventory` 经真实需求走完 From-scratch 全链路：verify clean、drift 篡改回归退出码 1、官方 validator 通过、Artifact 对绝对路径与私有标识 0 命中。当前：已关闭（仅 From-scratch 入口）。 |
| R-016 | P2 | 公共仓库尚无 GitHub Actions；当前验证由本地定向命令和人工记录承担。 | 外部提交没有自动结构/回归门，长期可能产生发布漂移。 | 已添加 `.github/workflows/validate.yml`，覆盖 ubuntu/windows × Python 3.12/3.13，含编译、全量测试、Schema 元校验、官方 validator、看板 JSON、零断链、真实 build + verify 及一条 drift 必须拒绝篡改的负例。当前：已关闭，待首次远端运行确认。 |
| R-017 | P1 | 平台能力词表 `SUPPORTED_CAPABILITIES` 仅四项，不含网络或托管平台访问；`git.diff` 亦无法精确表达 `remote get-url` / `rev-parse` / `status` / `log`。真实需求首次构建即被 required 能力拒绝。 | 任何需要网络或托管平台访问的 Loop 无法如实声明能力，只能收缩范围或降级为 optional 并接受 `degraded`。 | 扩展词表并同步 Adapter 与其测试，或明确记录为长期边界并在 Skill 文档中声明。当前：OPEN（对应看板 P2-01）。 |
| R-018 | P1 | `upgrade-skill.md` 第 4 节把 supporting cycle 判为 `embedded_loop`，而第 6 节兼容门要求 verdict 必须是 `loop_first_skill`，两节自相矛盾，`embedded_loop` 成为可判定但永不可构建的死路。已逐行核实原文。 | 现实中最常见的"在既有多阶段 Skill 里嵌一个反馈环"永远无法进入构建；盲测 LC-008、LC-011 因此失败。 | 第一批修复已放宽兼容门，允许单一 supporting Loop 在可无损映射时构建。当前：已关闭，由 27 例回归确认。 |
| R-019 | P1 | `loopability-gate.md` 的 check 6 无迭代下限、check 3 未写明目标自带验收判断算合格检查、反捏造条款只有单向，导致有界修订循环被系统性清零为 `zero_loop_workflow`。 | 直接损害产品核心承诺"识别有界 Loop 并构建"；盲测 LC-002、LC-008、LC-015 撞同一组措辞。 | 第一批修复补齐三处限定并加缺省兜底（Loop 数只能被指名的失败检查降到 0）。当前：待 27 例回归确认。 |
| R-020 | P2 | `entry-evidence.schema.json` 的 `entry_type` 与 `source_summary.kind` 枚举缺 direct build 取值，且 `candidate_review` 必填；`core-build.md` 称 direct build 可省略 Entry Evidence，在实现层等于不可能包含。 | 用户在 direct build 路径明确要求 Entry Evidence 时不可满足；强行满足会伪造 Candidate Review 与批准记录，命中 hard-fail。 | 枚举各增一个 direct build 取值并同步映射表，明确要求摘要如实声明未发生 Candidate Review。属第二批（动 schema）。当前：OPEN。 |
| R-021 | P2 | `source_skill.py` 的 `ALLOWED_ROOT_FILES` 仅五项，任何其它根条目直接抛错；`upgrade-skill.md` 把这一包装层限制写成架构门槛，全文无补救指引。一个 `SKILL.md` + `package.json` 的普通形态 Skill 天然无法 inventory。 | 分类完全正确的单 Loop 升级被卡成零产出，用户被推回"你自己去改源包"的死角；盲测 LC-009 即此。 | 把 inventory 失败从架构判定降级为可补救的包装层问题，在源目录之外暂存规范化副本；源目录本身永不修改。属第二批。当前：OPEN。 |
| R-022 | P2 | 盲测评分在"正确停机 vs 过度停机"边界上不稳定：LC-009 两轮模型行为实质一致（均停在批准前、均提阻塞问题、沙箱均为空），判定却由 pass 翻转为 fail。 | 通过率数字在该边界上有噪声，可能把测量波动误读为产品回归或修复成效。 | 为该边界补更明确的评分判据，区分"规则要求的批准闸口"与"可从范围内证据推导却仍然发问"。当前：OPEN。 |
| R-023 | P2 | 24 例盲测中没有任何一例的正确答案是"因包装或输入形态而停机"，数据集对该风险面零覆盖。 | 所有放松停机条件的修复都无法被现有数据集证伪，可能把过度阻断换成过度构建。 | 已补 RV-001（越出 root 的链接应停）、RV-002（真实语义损失应停）、RV-003（散文定义缺必填字段应合并提问一次）三例反向用例。当前：已补齐，待回归确认有效性。 |
| R-024 | P1 | 第三轮盲测 RV-003 命中 fabrication 类 hard-fail：把 schema 必填的 `authority`（allowed/approval-required/forbidden）与验收证据用合理默认值填满，并作为已定内容置于评审包中，以一句"批准"即可整包封定。其中包含源文档从未提及的 `git push` 禁令。 | 这是凭空发明一条安全边界并诱导用户盖章，比不构建严重。是本次评估中唯一一例越权而非交付不足的失败。 | 源材料未陈述的 schema 必填安全字段必须逐项具名列入 Candidate Review 字段 5，且不得被整包批准封定。修复范围严格限制在 `candidate-review.md`，不得引入新构建路线。当前：OPEN，最高优先。 |
| R-025 | P1 | LC-009 的候选修复方案经独立对抗证伪判定为 unsafe：把 §6 兼容门改写为"仅设计条件"会删除 RV-001 赖以停机的机械条款，使越出 root 的链接不再阻断构建；SKILL.md 与 loopability-gate.md 的两处摘要改动同样缺少安全豁免。 | 若照方案应用，将以 2 例失败换取 5 例 critical 回归，其中含安全边界失效与多 Loop 检测整体失效。 | LC-009 的可达性修复必须在保留 link/越界检测无条件停机的前提下重新设计，并先补一例"源可字节绑定但含越界链接"的组合用例。当前：OPEN，LC-009 修复暂缓。 |

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
- R-015 已由 `project-asset-inventory` 的真实 Demo 关闭，但只覆盖 From-scratch 入口；Existing Skill 与 Conversation 两条入口仍无真实 Demo 证据。
- R-016 已由 `.github/workflows/validate.yml` 关闭本地缺口；首次远端运行结果确认前不得宣称 CI 已生效。
- R-017 至 R-023 为 2026-07-27 由真实使用与 24 例盲测暴露的新风险。其中 R-018、R-019 是规则文本自身矛盾而非模型发挥不稳，重跑无法改善，必须改文本；R-020、R-021 需改 schema 与 Python，属第二批，血溅面大于第一批。
- R-022 是测量层风险，不是产品缺陷。在该判据明确前，单次通过率数字在"正确停机"这条边界上不应被当作精确指标。
- R-023 记录的是数据集本身的覆盖缺口。三例反向用例是放松类修复的护栏；护栏未验证有效前不得应用第二批放松改动。
- 三轮盲测共同成立的：失败用例 `outputs/` 全空（批准前零写入）、被测仓库 HEAD 与基线逐字节一致、无一例自述与沙箱事实不符。
- **更正**：此前记录称"三轮均 0 hard-fail"。前两轮经直接核实为 0，第三轮未重新解析 `details[].hard_fails` 即外推，结论错误。第三轮 RV-003 命中 fabrication 类 hard-fail，已登记为 R-024。该错误由独立管控裁决发现。
- 因此"缺口全部位于规则侧、失败全为交付不足"这一判断只对前两轮成立，不适用于第三轮。
- 资源复用记录 §13 第 237 行已更新为“阶段 2 最终 Spec 已写入并批准”；此前的 `stale` 已消除。第 238 行“Git 仓库尚未初始化”因后续 `git init` 已成为新的过时状态，本日志以实际 Git 命令为准。
