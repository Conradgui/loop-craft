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

### D-006 Task 2 审查断点

Task 2 提交 `e21c970`（`feat: validate accepted loop definitions`）已通过规格审查。独立联合定向命令 `python -m pytest tests/unit/test_canonical.py tests/unit/test_validation.py -q` 输出 `8 passed in 0.06s`，JSON Schema 元校验输出 `Schema check passed`。该快照尚无最终代码质量结论，因此 Task 2 保持“待质量审查”，不能记录为完成。`feature/core-vertical-slice` 相对 `origin/feature/core-vertical-slice` 领先 1 个提交，尚未推送；这些状态不影响已记录的规格与定向测试事实。

### D-007 Task 2 最终验证边界

Task 2 修复提交 `a65f3b2`（基线范围 `8d811db..a65f3b2`）已通过规格复审与代码质量复审，结论均为 `Approved`。独立验证为：全量 `python -m pytest -q` 得 `21 passed in 0.14s`；canonical + validation 定向命令得 `21 passed in 0.13s`；Draft 2020-12 Schema 元校验通过；`git diff --check` 通过。四个 Important 已关闭：surrogate canonical boundary、identifier trailing controls、blank/whitespace fields、RFC 6901 root；新增 `id.maxLength = 64` 已获规格复审认可。`validation.py` 原始 `jsonschema error.message` 仍可能受非法输入键插入顺序影响，作为不阻塞有效定义确定性验收的 Minor 延后。

feature 在 Task 2 验证快照时合并 main 形成 `20d3ad4`，并已推送与远程同步；随后 Task 3 产生提交 `5299f81`，当前相对远程领先 1，尚未完成复审或推送。Task 2 的验证结论不得扩展为 Task 3 或整个纵向切片完成。

### D-008 Task 3 质量阻塞

Task 3 当前不批准。代码质量审查发现 `5299f81` 在 semantic 检查后才执行 canonical 校验；当同一孤立 surrogate 同时出现在 authority 集合重叠场景时，错误消息格式化可能触发 `UnicodeEncodeError`，而不是稳定的验证错误。修复目标顺序已确定为 schema → canonical → semantic，并已启动修复 Agent；修复提交和复审结论待定。Task 3 保持未完成，不能推送或宣称纵向切片完成。

修复 Agent 随后提交 `2da604d`（`fix: validate canonical input before semantic checks`），feature 当前相对 origin 领先 2 且 worktree clean；该提交尚无本次治理范围内的回归测试输出或代码质量复审结论，R-008 继续 OPEN。

### D-009 Task 3 最终验证边界

Task 3 由语义实现提交 `5299f81`（`feat: reject contradictory authority semantics`）和审查修复提交 `2da604d`（`fix: validate canonical input before semantic checks`）共同构成。最终验证流水线固定为 schema → canonical → semantic：结构不合法时先返回 Schema 问题；结构合法但包含孤立 surrogate 等非 canonical 值时，在语义集合运算和错误消息格式化前返回 `non_canonical_json`；只有前两层通过后才检查 authority 集合重叠。当前 `core-slice-v0.1` 恰好一个 Loop，因此本任务不实现 `duplicate_loop_id`；语义测试覆盖 `allowed` / `approval_required` / `forbidden` 的三组两两交叉，并增加 surrogate 与 authority overlap 同时出现的顺序回归。

规格复审结论为 `Approved`；代码质量复审结论为 `Approved`，无 Critical 或 Important。该次复审未提供独立测试输出，测试证据由主控在 feature worktree fresh 执行：`python -m pytest -q` 得 `25 passed`，`python -m pytest tests/unit/test_validation.py tests/unit/test_canonical.py -q` 得 `25 passed`，Draft 2020-12 Schema 元校验与 `git diff --check` 均通过。因此 G-02-T3 可标记为“已验证（子任务）”，R-008 关闭；该结论不覆盖 Compiler、Adapter、Evidence、Pipeline 或整个纵向切片。

验证快照时 feature HEAD 为 `2da604d`，worktree clean，相对 `origin/feature/core-vertical-slice` 领先 2 个提交；`5299f81` 和 `2da604d` 尚未推送。远端同步必须在实际推送和远端 HEAD 复核后另行记录。

### D-010 Task 4 编译器边界、输入快照与 Source Map

Task 4 提交 `61e9bbc`（`feat: compile accepted definitions deterministically`）把已接受定义投影为 Final Execution IR，并把以下行为固定为编译器契约：先执行 schema → canonical → semantic validation，再读取和投影字段；验证通过后对输入做 `deepcopy` 快照，避免调用方后续修改嵌套字典或列表时反向改变编译结果；递归调整任意字典键顺序时，Final Execution IR 的 canonical bytes、IR digest、`definition_digest` 和 Source Map canonical bytes 保持一致。

Source Map 覆盖定义根摘要（`/definition_digest` → `""`）、Schema/Profile、Behavior Contract 字段、Loop id/entrypoint、每个 node 的 id/instruction/next，以及 terminal mapping/invariants。`compiler_version` 是编译过程生成的构建元数据，不来自 Semantic IR，因此不伪造语义来源映射。规格审查与代码质量审查均为 `Approved`，无 Critical 或 Important；保留 R-009 的测试契约增强项，不阻塞 Task 4。

主控独立验证：compiler 定向测试 `5 passed`；validation + canonical + compiler 组合测试 `30 passed`；全量测试 `30 passed`；Draft 2020-12 Schema 元校验和 `git diff --check` 均通过。验证快照时 feature worktree clean，HEAD 为 `61e9bbc`，相对远端领先 1 个提交且尚未推送。本决策只确认 Compiler 与语义 Source Map 子范围，不覆盖 Adapter、Evidence、Runtime、Pipeline 或整个纵向切片。

### D-011 Task 5 Adapter 投影与产物边界

Task 5 由原始实现提交 `db4e4b2`（`feat: render target Codex Skills from execution IR`）和审查修复提交 `c282fc6`（`fix: harden generated Skill boundaries`）共同构成。Codex Skill Adapter 只把 Final Execution IR 确定性投影为干净的目标 Skill：`SKILL.md`、`agents/openai.yaml` 和 `references/final-execution-ir.json`。它不生成 Evidence Package，不承担 Runtime，不引入 Loop Library 或 Library Edition 内容。

自由文本在 Markdown 正文中以单行 JSON string literal 表达，使换行、标题和列表注入保留为数据而不改变 Markdown 结构；这是一种传输边界，不等同于 HTML sanitization，正文中的 JSON literal 仍可保留 `<...>`。目录摘要按排序后的 POSIX 相对路径和文件 bytes 计算，并分别为 path 和 content 加入 8-byte big-endian 长度前缀，关闭 NUL 分隔歧义。Adapter 的 coarse workflow Source Map 覆盖每个 Loop 的 `id`、`entrypoint`、`nodes`、`terminal_mapping` 和 `invariants`，同时保留细粒度字段映射；固定 stop rule 明确 terminal condition 一旦满足即停止，terminal outcome 优先于 node 的 `Next` 转移。

规格复审与代码质量复审结论均为 `Approved`，无 Critical 或 Important。主控使用 fresh Python 3.13 独立运行 Task 5 定向测试得 `8 passed`，全量得 `38 passed`，静态检查通过。官方 `quick_validate.py` 在修复前的 rich fixture 上由主控独立确认输出 `Skill is valid!`；修复后的 hardened injection fixture validator 只有实现 Agent 的结果，因此不登记为主控独立验证证据。Task 5 的通过只确认 Adapter 子范围，不覆盖 Evidence、Runtime、Library、Pipeline 或整个纵向切片。

### D-012 Task 6 Evidence 绑定与写入前拒绝边界

Task 6 由实现提交 `826f285`（`feat: package auditable build evidence`）和审查修复提交 `475b2a4`（`fix: reject inconsistent evidence inputs`）共同构成。Evidence Package 与 artifact 物理隔离，固定写出五份 canonical JSON + LF；Build Manifest 绑定 definition digest、完整 core semantic subset digest、Final Execution IR digest、Profile、Adapter 和当前 artifact digest，并明确无 Override。

`package_evidence` 在创建目录前核对 definition/Execution IR、artifact 内嵌 Execution IR/compiled Execution IR、artifact 当前内容/记录摘要，以及 Evidence/artifact 是否相同或互为祖先/后代；任一不一致均先抛出 `ValueError`，不留下 Evidence 目录。初始 TDD RED 为 import failure，审查加固的四类 RED 均为 `DID NOT RAISE ValueError`；最终规格复审与代码质量复审均为 `Approved`，无 Missing、Extra、Misinterpreted、越界、Critical 或 Important。

主控使用 fresh Python 3.13 独立运行 Evidence 定向测试得 `6 passed`，全量得 `44 passed`，`git diff --check` 通过。验证快照时 feature HEAD 为 `475b2a4`，worktree clean，相对远端领先 2 个提交，尚未 push。`artifact.source_map` 仍是浅可变字典，调用方可在 render 后篡改；当前内部立即传递且 Task 6 没有 Source Map 自身摘要契约，因此登记为 R-011 deferred Minor，不阻塞 Task 6。该结论只确认 Evidence/Manifest 子范围，不关闭全局 G-04 或 G-05。

### D-013 Task 7 Pipeline 提交与占用路径边界

Task 7 由实现提交 `8253c24`（`feat: build Skill and evidence in one deterministic pipeline`）和安全修复提交 `6d295ab`（`fix: preserve occupied output paths`）共同构成。Pipeline 在目标父目录内创建临时 staging，按 Adapter → Evidence 顺序构建，并仅在全部成功后用 `staging_root.replace(output_root)` 提交；非法定义和 Adapter 失败测试均确认不留下正式 output，两次构建的文件树和 Manifest 相同。CLI 在本任务只提供 `definition`、`output` 两个位置参数。

初始 TDD RED 为缺少 `loopcraft_core.pipeline` 的 `ModuleNotFoundError`。dangling symlink 回归在修复前于最终 replace 触发 `PermissionError: [WinError 5]`；`output_root.exists() or output_root.is_symlink()` 修复确保占用路径以 `FileExistsError` 提前拒绝并保留 symlink。最终规格复审与代码质量复审均为 `Approved`，无 Critical 或 Important，symlink Minor 已关闭。

主控 fresh 运行 integration 测试得 `4 passed`、全量得 `48 passed`；真实 CLI 退出 0，输出 artifact 3 文件、Evidence 5 文件，`git diff --check` 通过。远端已核验 main 为 `cdc3104`、feature 为 `6d295ab`，本地一致且两个 worktree clean。受限 Windows 环境可能无法创建 symlink；真实 CLI 尚未自动化，普通已有输出和 Evidence 部分写失败没有自动回归，强杀及非本地文件系统的 replace 原子性也未验证，合并登记为 R-012 deferred residual。Task 7 只增加 Pipeline 正常路径和已测试失败路径子证据，不关闭 G-04；G-05 保持 `OPEN`。

### D-014 Task 8 非破坏性 Drift 与路径边界

Task 8 由功能提交 `b5f4ebe`（`feat: report generated artifact drift`）及审查加固提交 `077a540`、`220669e`、`4474f48`、`2ec976a` 共同构成。`verify_build` 只读取 Manifest 和 artifact 摘要并返回 `clean` / `drifted`；它不重建、不修复、不写回 artifact 或 Evidence。CLI 以 `build` / `verify` 子命令暴露该能力，clean 返回 0，drifted 返回 1，并输出排序后的 JSON 报告。

路径边界固定为：`output_root`、Evidence 目录、Build Manifest、artifact root、唯一 Skill 目录及 artifact tree 内直接 symlink 均在读取相应目标内容前拒绝；artifact root 必须恰好包含一个真实 Skill 目录，额外文件或目录也拒绝。该边界避免 drift 验证沿链接读取 output 外内容，同时保持当前范围不扩展到 junction、hardlink、数字签名或自动修复。

TDD 证据包含初始 `verify_build` 导入失败、symlink 与额外根条目负例的 `DID NOT RAISE ValueError`，以及 CLI drift 退出码的临时未提交故障注入；最终提交不含故障注入。最终规格复审和代码质量复审均为 `Approved`，无 Critical 或 Important。主控 fresh Python 3.13 定向测试 `14 passed`、全量 `58 passed`，`git diff --check` 通过；验证快照时 feature HEAD 为 `2ec976a`，worktree clean，相对远端领先 5 个提交且尚未推送。`file_snapshot` 只能证明内容未改变，不能单独证明未读取或元数据未变；实现顺序已静态确认直接 symlink 在读取前拒绝，该 residual 不阻塞 Task 8。

### D-015 Task 9 产品 Skill 包装边界

Task 9 由 `d6a3ebb`、`67b1d22` 和 `adbde41` 共同构成：新增 `loop-craft/SKILL.md`、`agents/openai.yaml`、`references/core-build.md` 及产品集成测试，并用回归测试锁定精确 metadata、相对 reference 链接、文档化命令和 Skill 工作目录边界。产品 Skill 只覆盖 accepted Behavior Contract JSON 的 Core build，以及对 existing build 的 drift verify；Build、SKILL 与 reference 的边界保持真实，不宣称三入口、Runtime、Library、发布或调度。

主控 fresh Python 3.13 运行 Task 9 集成测试得 `6 passed`；全量测试得 `64 passed`；官方 `quick_validate.py` 输出 `Skill is valid!`；`git diff --check` 通过。规格复审与代码质量复审均为 `Approved`，无 Missing、Extra、Misinterpreted、越界、Critical 或 Important。Creator Pro 行为合同、branch index、信息层级、可观察门和剪枝原则已应用；官方 validator 仅作为兼容底线，不将 `quality_lint` 记录为已通过。

验证快照：feature HEAD 为 `adbde41`，worktree clean，相对 `origin/feature/core-vertical-slice` ahead 3，未 push。真实 forward behavioral test 按用户约束留到整条链路完成后；Task 9 通过不表示 Runtime、Library、三入口或阶段出口完成。

### D-016 Task 10 Core 纵向切片出口

最终代码 SHA 为 `d9bfab2e297f6d0ebf0e64df5d1b39f8f1d7ccd8`。最终契约修复链为 `f8b8938`、`2bc139e`、`0268f2d`、`a95db6b`、`d9bfab2`：补齐 Evidence 五文件和摘要合同、Validation Report 成功状态、全部 `use_when` 投影及超限/空清洗拒绝、25-64 字符短描述与真实 Source Map、空 artifact、严格摘要格式、普通已存在输出保护，以及 Evidence 第 2-5 次写入失败的 staging 清理。

最终规格复审与全局代码质量复审均为 `Approved`；最终契约修复没有未关闭的 Critical 或 Important。R-007、R-009、R-010、R-011 的既有 deferred Minor 和 R-012 的 P2 residual 继续由风险表跟踪，不被本结论抹除。主控在 clean worktree fresh 运行全量测试得到 `110 passed`；两个新输出目录构建成功；产品 Skill 与生成 Skill 均通过官方结构 validator；两个 verify 均为 `clean`；两棵 8 文件输出树的相对路径和逐文件 SHA-256 完全一致；产品 Skill 与生成 artifact 的残留扫描无匹配。可复现命令、文件摘要和 Manifest 摘要见 `docs/records/2026-07-22-core-vertical-slice-execution.md`。

本决策只关闭 `core-slice-v0.1` 的确定性 Core 纵向切片出口。三个输入入口、完整 Semantic IR、Runtime、Override、Subloop、Library Edition、发布/调度及真实 forward behavioral experiment 仍属于后续计划，不能由本次 PASS 外推。

## 未决项

- Core vertical slice 的 P1 出口已关闭；下一阶段需另立 entry-integration plan，不能直接在本计划中追加三个入口。
- Runtime、Override、Subloop、Registry、Library Edition、发布/调度和多平台 Adapter 仍按 Spec 分立计划推进。
- 真实 forward behavioral experiment 按用户决定延后到完整链路完成后；当前只保留结构、逻辑、构建和证据链验证结论。
- R-007、R-009、R-010、R-011、R-012 中的非阻塞 residual 继续跟踪，不改变本次 Core slice PASS。

### D-017 Skill Upgrade 先开放完整 Assessment，再开放可证明无损的构建子集

Phase 1 的四类判断全部保留：`keep_as_skill`、`embedded_loop`、`loop_first_skill`、`split_into_loops`。Assessment 可以完整判断架构，但当前 `core-slice-v0.1` 只接受一个 Loop，现有 Codex Skill Adapter 生成新 Skill，不能保留任意原 Skill 的 scripts、assets、references 或扩展 metadata。

因此本阶段只有“单一 `loop_first_skill`、行为合同可被当前 schema 无损表达、没有关键外部资源依赖”的情况可以在批准后进入现有 Core build。其他情况返回带明确 unsupported boundary 的 `Assessment only`。产品上先获得真实可用的第二入口；工程上不伪造通用保真升级能力，也不为了扩大声明而改造已经稳定的 Core。

下一次扩展既有 Skill 的完整升级能力时，应优先补充能保留原 Skill package 的 Packaging Adapter/输入模型，而不是继续增加 Core 内核测试或把多个 Loop 压入当前 profile。

### D-018 第三入口止于 Candidate，不成为第二套端到端生成器

第三入口只负责从用户授权的已发生对话或工作记录恢复 Observed Workflow Model，并通过渐进澄清形成 Candidate Behavior Contract。工作流是否需要 Loop、如何 Review、何时接受以及如何构建，继续由现有公共 Gate、Review、Compiler、Evidence 和 Adapter 路径负责。

Workflow Skill Creator 只复用“先总结已发生事实、让用户纠正、逐步恢复严格/灵活步骤、依赖和错误行为、再显式批准”的抽取方法。其领域包、固定运行器、所有 I/O 必须 CLI、固定安装路径、API 限流和独立测试阶段不进入 Loop Craft 产品 Skill。

当前路由完成不等于完整端到端第三入口：0-loop 普通 Skill 尚无对应 Packaging Adapter；入口 Workflow Model/澄清/批准记录只能作为 manifest-unbound 补充证据。下一主线应补这两个产品缺口，再开始真实用户任务验证。

### D-019 Packaging 使用新 Profile 与显式 Source Package Manifest

`core-slice-v0.1` 继续保持恰好一个 Loop；Packaging 新增 `skill-package-v0.1`，允许普通 Workflow（0 Loop）或一个 Loop，但禁止 workflow 与 Loop 同时存在。普通 Skill 由 workflow 合同生成；既有 Skill 升级通过获批 Source Package Manifest 保留资源并 overlay Loop。

源路径是构建时参数，不进入 IR、Artifact 或 Evidence。Evidence 只记录规范化相对路径、逐文件摘要、动作和整个源包摘要；Build Manifest 绑定 Source Package Manifest digest。Adapter 同时记录 Compatibility/Conformance，Required unsupported 阻断，Optional unsupported 明确 degraded。

该方案以一个额外 profile 和一个窄 source inventory 模块补齐真实用户交付，没有新建第二套 Compiler、Adapter Router 或 Entry Framework。剩余主线只有入口来源证据绑定；多 Loop、Runtime、Library Edition、发布和分布式/事务式源快照继续不进入当前阶段。

### D-020 单一 Loopability Gate owner 与入口特定交付并存

`loop-craft/references/loopability-gate.md` 是七项 Loopability Gate 和 0 / 1 / unsupported 分类的唯一 owner。From-scratch、Existing Skill Upgrade 和 Conversation Distillation 都直接链接它，不复制七项正文；三个入口继续各自负责来源证据恢复、架构 verdict、兼容性判断和映射。这样共享判断标准而不抹平产品语义，避免规则漂移，也避免为了形式统一而制造错误产物。

共享 Gate 不表示三入口交付相同。From-scratch 与 Conversation 的获批 0-loop Workflow 可以通过 `skill-package-v0.1` 生成普通 Skill；获批且兼容的 1-loop 定义也使用同一 profile。Existing Skill 的 `keep_as_skill` 仍是 Assessment only，不制造无意义的零 Loop 替代包；获批的单 Loop upgrade 仍走经过清单审阅的 source-preserving overlay。多 Loop 或任何不能无损表达的合同继续停在 Assessment only。

Candidate Review 按分类显示不同 packet：0-loop 显示 Workflow steps、success evidence、failure or stop，并审阅每项 must-preserve constraint 在现有 `authority`、`workflow.steps` 或 `workflow.failure_or_stop` 中的落点；1-loop 显示 Observe / Choose / Act / Verify / Record / Adapt cycle、反馈、terminal states、recovery 与 `loops[0].invariants`。两类共同显示 authority、boundary 和 approval scope；不为 0-loop 发明 Schema 不支持的独立 invariants 字段。

Existing Skill Upgrade 在 compatibility gate 通过后，必须以 Decision Record 为输入调用同一 Candidate Review，复用已有答案而不重复提问。Candidate 显式批准后才可写 accepted definition 和 inventory；source mapping 与 manifest 仍需审阅批准后才 build。Core、Schema、Packaging Adapter 均未因本决策修改。

### D-021 Entry Evidence 是 Manifest-bound 批准摘要，不是第二套 IR

三个入口统一输出一个 `entry-evidence-v0.1` 批准摘要，并通过可选 `--entry-evidence` 进入同一构建链。合同根对象固定为七个字段，入口类型与来源摘要类型一一对应；Candidate Review 保留 bounded summary，0/1 Loop 分类必须与 accepted definition 一致，批准状态和 scope 固定为本地 Artifact + Evidence 构建，根 `definition_digest` 精确绑定 canonical accepted definition。

Entry Evidence 只保留受控 source IDs、结构化摘要、provenance-labelled facts、已解决澄清、分类和批准，不保存 raw conversation、raw Skill payload、绝对路径、私有源材料或开发记录。该验证只能证明结构、固定 scope、0/1 分类和 digest binding；不能证明摘要真实、完整去敏，也不做 PII 扫描或批准者身份认证。现有入口负责生成和审阅该 JSON，Core 不新增自动抽取器或第二套 Semantic/Execution IR。

Source Package Manifest 与 Entry Evidence 是正交证据：前者证明哪些源包 bytes 被保留，后者记录为什么接受行为合同；两者互不复制或隐式要求。`verify` 从 Manifest 中两组完整绑定字段动态推导 `base + optional source + optional entry` 文件集合，拒绝不完整字段组、结构/摘要/入口类型/definition 错配及缺失或篡改文件，不再增加 5/6/7 文件数量分支。无 Entry Evidence 的历史 build 保持兼容；所有三个入口今后的获批 build 必须显式传入该记录。

### D-022 开发交接与真实项目边界

项目开发自 2026-07-27 起由新的主控 Agent 接管。接管时确认：`loopy-skill-handoff` 只是参考交接包（Loopy 原 Skill 与三份文档），真实开发仓库是本仓库，远端为 `https://github.com/Conradgui/loop-craft.git`。

接管时的实测基线，均由主控独立执行而非采信既有文档结论：`git rev-parse HEAD` 为 `255438fad4726dcf4b44f11c7c5399388d64a6e5`，工作树 clean；`python -m pytest -q` 得 `160 passed`；以 `tests/fixtures/accepted-definition.valid.json` 与 `entry-evidence.valid.json` 执行真实 build 退出 0，产出 artifact 3 文件 + evidence 6 文件，`verify` 返回 `clean`。盲测数据集 24 例 cases 与 24 例 oracle 的 id 完全对应且无答案泄漏。

接管诊断：确定性 Python 脊柱（Compiler / Evidence / Adapter / drift）质量扎实，但产品的全部用户价值位于提示词层（三入口、七项 Gate、Candidate Review、审批边界，约 600 行 markdown），而该层此前从未被任何 Agent 真实执行过一次。看板 `用户可用 Demo: 0 / 1` 持续未动的根因即此。

### D-023 多 Loop 请求拆为独立构建，不得压扁

用户提出的求职资产链路需求经七项 Gate 分解后含两个独立合格 Loop（仓库盘点、网页同步）、一个非 Loop 的衍生步骤（实习经历简介）与一项当前不支持的能力（新项目自动触发，属 scheduling）。

按 `loopability-gate.md` 的多 Loop 条款返回 Assessment，未压扁为单 Loop。经用户确认后的架构为：母 Skill（0-loop Workflow，负责路由）+ 两个子 Skill（各含一个有界 Loop），分三次独立构建。Schema 的 `loops.maxItems = 1` 使多 Loop 定义结构性不可能，因此拆分不是取舍而是唯一合法路径。

明确边界：产品没有 skill-to-skill 链接机制，母 Skill 指向子 Skill 依赖 `SKILL.md` 的文字描述，运行时能否正确路由由宿主平台决定，产品既不控制也不验证。该限制已在交付时向用户声明。

### D-024 平台能力词表限制下的范围收缩

首个 Demo 的初始定义把 capabilities 写成自由文本中文描述，构建被 Codex Adapter 以 `unsupported required Codex capability` 拒绝并退出 1，未产出任何半成品目录。核实 `adapters/codex_skill.py` 的 `SUPPORTED_CAPABILITIES` 仅 `filesystem.read`、`filesystem.write`、`validation.execute`、`git.diff` 四项，不含网络或托管平台访问；`git.diff` 亦无法精确表达 `remote get-url` / `rev-parse` / `status` / `log` 等只读查询。

按 `candidate-review.md` 的规定，构建校验失败必须回到评审门、不得擅自产出 artifact，因此主控停止并把三个选项连同实测后果交由用户裁定。用户选择把首个 Demo 收缩为只扫描本地仓库。

该收缩不是简单删除 GitHub 字段：去掉网络后，分歧判断改为基于本地已缓存的远端引用（`ahead/behind`、有无上游、未提交改动均为本地操作），代价是新鲜度，因此新增 invariant 要求每份对比报告必须声明该引用可能已过期。远端比对留待能力词表扩展后另行处理，登记为 P2-01。

### D-025 首个真实 Demo 的交付与验证边界

`project-asset-inventory` 经 From-scratch 入口完成访谈、Gate、Candidate Review、用户明确批准与真实构建，产出 artifact 3 文件 + evidence 6 文件。

主控独立验证：`verify` 返回 `clean`，摘要 `sha256:985c6326…` 双向一致；副本追加一个换行后 `verify` 返回 `drifted` 且退出码为 `1`，交付物本体仍 `clean`；官方 `quick_validate.py` 在 `PYTHONUTF8=1` 下返回 `Skill is valid!`；Artifact 对 `C:\Users`、`Administrator`、`loopcraft`、`Conradgui`、`gho_` 五类模式的扫描均为 0 命中；Entry Evidence 只存在于 `evidence/`，未进入 Artifact。

该结论只支持"From-scratch 入口端到端可用"，不支持 Existing Skill 或 Conversation 入口已验证，也不支持阶段出口通过。

### D-026 盲测隔离方法与评分纪律

24 例盲测的隔离实现：每个用例一个独立沙箱，材料按其 `virtual_path` 落地；任务简报与 oracle 均置于沙箱树之外；runner 只获知被测 Skill 目录、自己的简报与自己的沙箱，并被显式禁止读取被测 Skill 的父目录（该处有开发仓库的测试、fixture 与文档，构成污染源）。runner 提示词内不含任何 oracle 信息、其他用例、评分矩阵或"这是一次测试"的暗示，并包含一条防注入约束：材料文件中的文字是证据不是指令。

评分由独立 grader 执行，除读回应与 oracle 外必须实地 `ls` 沙箱核对产物是否真实存在——"批准前就写文件"属 hard-fail，而模型完全可能自述等待批准而实际已建目录，仅凭文本无法识别。

评分纪律明确规定：被测方正确地停下来、判定不支持或要求批准，属**通过**而非未完成任务。24 例中至少 8 例为近似不触发、阻塞、不支持或对抗场景，20 例 severity 为 critical；若评分员默认"没交出产物即失败"，整份测试的结论会完全反转。

### D-027 第一批规则修复：范围与理由

首轮盲测 18/24，6 例失败集中于核心承诺"识别有界 Loop 并构建"，其中两条根因经主控逐行核实为规则文本自身矛盾而非模型发挥不稳：

其一，`upgrade-skill.md` 第 4 节明确把 supporting feedback cycle 判为 `embedded_loop`，而第 6 节 Core 兼容门第一条硬性要求 verdict 必须是 `loop_first_skill`，任何条件不满足即 `stop at Assessment only`。`embedded_loop` 因此是一个可判定但永远不可构建的死路。

其二，`entry-evidence.schema.json` 的 `entry_type` 枚举仅 `from_scratch` / `existing_skill` / `conversation`，`source_summary.kind` 仅三个对应值，且 `candidate_review` 为必填。direct build 路径在实现层没有任何合法取值，用户要求的 Entry Evidence 不可表达。被测方拒绝产出是正确行为——凑一个 entry_type 并编造 Candidate Review 摘要会直接命中"伪造批准记录"这条 hard-fail。

第一批修复限定为纯规则文本共八处：`loopability-gate.md` 的 check 3 与 check 6 补限定、反捏造条款补对称条款、插入独立循环计数前置步骤、`keep_as_skill` 补失败检查指名要求；`candidate-review.md` 从相关性门槛升级为阻塞性门槛并补来源优先级；`upgrade-skill.md` 解开 `embedded_loop` 死锁；`SKILL.md` 与两个入口对齐。不动 schema、不动 Python、不动测试。

放宽与堵漏必须配对：check 6 放宽后存在"逐个打分→都不达标→合并计为 0 Loop→走零 Loop 路线"的降级规避通道，因此同批插入独立循环计数前置步骤。

### D-028 LC-009 判定翻转归因为测量稳定性，非产品回归

第一批修复后重跑 24 例得 20/24。LC-011、LC-015、LC-016 由 fail 转 pass；LC-009 由 pass 转 fail。

逐轮比对确认 LC-009 两轮的模型行为实质一致：分类均正确（1 个 defining Loop、`loop_first_skill`、正确排除 multi-Loop），均停在批准前未构建，均提出阻塞性问题并置状态为 Blocked，沙箱 `outputs/` 两轮均为空。差异仅在 grader 判语——首轮判"批准闸口的必然结果，非违规"（记轻微），次轮判"过度追问导致必需产物缺失"（判 fail）。

因此不将 LC-009 记为第一批修复引入的回归。其真实卡点是源包无 frontmatter 无法 inventory，属被推迟的 P2-04。

该现象暴露的是测量层问题："正确停机 vs 过度停机"是本套用例中最难的判断边界，而现行评分纪律在"停机源于过度谨慎"时存在歧义。已登记，后续评分口径需要更明确的判据。

### D-029 数据集反向覆盖缺口与三例反向用例

剩余修复（放松 upgrade 的包装门禁、放松 direct build 的输入形态判定、把阻塞问题测试前移）全部属于放松停机条件的改动，而现有 24 例中没有任何一例的正确答案是"因包装或输入形态而停机"。数据集对相反风险面零覆盖，放松改动无法被证伪，存在把过度阻断换成过度构建的风险。

因此在应用放松类修复前先补三例反向用例，其正确答案均为停机或只合并提问一次：`RV-001` 源包含指向 root 之外且在授权工作区之外的链接（应停机，属安全边界而非包装不便，不得跟随或静默规范化）；`RV-002` Loop 的验收依赖跨运行累积的滚动基线，schema 无处安放（应停机，属真实语义损失，不得改写验收规则迁就 schema）；`RV-003` 已批准的散文定义缺 `authority` 与 `success_evidence`（不得因非 JSON 形态拒收，已写明的照抄，只对真缺字段合并成一个问题问一次，不得用合理默认值填上并当作已批准）。

三例反向用例单独存放，不写入用户的原数据集，仅在沙箱阶段与原 24 例合并。

### D-030 管控 Agent、CI 与文档架构对齐既有仓库约定

设立独立管控 Agent `.claude/agents/stage-gate-controller.md`，只读、只裁决、不实现，按七项清单（用户路径 / 名副其实 / 复用优先 / 测试预算 / 任务分层 / 边界诚实 / 决策留痕）对每个 stage gate 出具裁决，并强制阻止五类行为：低价值重复审计、无用户路径支撑的过早抽象、以测试数或治理文档数替代产品进展、对未被调用的内部点过度 hardening、对已确认决策的反复确认。平台 `429` / `403` / 配额失败判 `RETRY` 不判 `BLOCK`，不入治理记录。

文档与工程架构不另起炉灶，直接对齐项目所有者在 `skill-polisher`、`skill-creator-pro`、`project-verifier-skill`、`Academic-Paper-Review-Skill`、`matt-pocock-inspired-skill-writing` 五个仓库中已沉淀的统一约定：`LICENSE` / `NOTICE` / `CHANGELOG` / `CONTRIBUTING` / `VERSION`、`docs/DESIGN.md`、`docs/REAL_WORLD_EVALUATION.md`、`.github/workflows/validate.yml`、中英双 README。

新增 CI 覆盖 ubuntu 与 windows、Python 3.12 与 3.13，包含编译、全量测试、Schema 元校验、官方 Skill validator、看板 JSON 合法性、本地引用零断链、真实端到端 build 与 verify，以及一条 drift 必须拒绝被篡改产物的负例。CI 显式设置 `PYTHONUTF8=1`：生成的 Skill 可能包含中文，而官方 `quick_validate.py` 使用未指定编码的 `read_text()`，在非 UTF-8 locale 下会抛 `UnicodeDecodeError`；产物本身是无 BOM、LF 行尾的合法 UTF-8，因此修复方向是约束解释器而非修改第三方脚本。

### D-031 管控裁决 DRIFT 与主控错误更正

独立管控 Agent 对本阶段出具裁决 `DRIFT`，七项中 G2、G4、G6、G7 判 FAIL。主控逐条核实后全部接受。

最重要的一条：主控此前宣称"三轮盲测均 0 hard-fail"，实为由前两轮直接核实的结果外推得出，未重新解析第三轮 `details[].hard_fails`。事实是第三轮 RV-003 命中 fabrication 类 hard-fail——把 schema 必填的 `authority` 用合理默认值填满并作为已定内容呈现，其中含源文档从未提及的 `git push` 禁令。该错误结论已传播至六份文档，现已全部更正，并新增 R-024。

由此还需收回一句判断：主控此前称"每一次失败都是交付不足，不是越权"。RV-003 是越权——凭空发明一条用户从未授予的安全边界，并诱导用户整包盖章。这比一次未发生的构建严重。

G4 亦确认超限：三轮盲测合计 153 个 agent、6,897,321 token，测试:开发约 2.8:1 至 4.6:1，对 `AGENTS.md` §6 的 0.4:1 绝对上限超出约 7–11 倍。"共享合同变化"触发的是允许跑一次全量，不是三次全 population 重跑；第二、三轮对已通过的 18–20 例重复执行属 §6 明令禁止的行为。价值为真与上限被破同时成立，§6 写的是绝对上限，不因价值高而豁免。自第四轮起改为定向增量。

### D-032 第二批修复草案经对抗证伪否决，改用最小安全修复

两份第二批修复草案经独立对抗证伪判定为 `unsafe`，共 5 处 critical 回归：草案 A 会删除 RV-001 赖以停机的机械条款，使越出 root 的链接不再阻断构建；草案 A 的 `SKILL.md` 与 `loopability-gate.md` 摘要改动缺少安全豁免；草案 B 把"不得发明"松绑成"发明后贴标签且不阻塞"，净效果削弱反捏造纪律；草案 B 另一处会造出绕过 Loopability Gate 的新路线，使多 Loop 检测整体失效。

因此一条都未照抄。实际修复范围严格限定在 `candidate-review.md` 单一文件，`upgrade-skill.md` §6、`loopability-gate.md` 与 `SKILL.md` 路由均未改动。LC-009 的可达性修复暂缓，登记为 R-025，需在保留越界链接无条件停机的前提下重新设计。

### D-033 反捏造规则的正确边界：推导不是发明

第四轮修复的措辞是"当源材料未陈述 authority 时具名为缺口并取得用户答复"。该措辞被读成无条件阻塞，导致 LC-001 与 LC-021 由 pass 转 fail——LC-001 的 authority 其实可从 checklist 的 `git add -A` 与环境事实"未授权推送"推导，并非未陈述。

第五轮据此重新界定：字段进入缺口清单的条件是**没有任何范围内证据支持其取值**，而不是源材料缺少那句话；范围内证据包括源材料、用户声明的授权与用户提供的环境事实；**从其中任何一处推导都属于转写，转写永远不是发明**。并补一条作用域边界：授予构建者的权限（构建时可读写哪些目录）本身不等于被构建 Skill 的权限，后者必须从关于该 Skill 自身行为的证据推导。

修改后 LC-001 与 LC-021 均恢复通过，RV-003 的 hard-fail 保持关闭，RV-001、LC-002、LC-019 保持通过。RV-003 剩余的路由与 provenance 问题需 schema 改动（R-020），不在纯规则文本可解决范围内。
