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

规格复审结论为 `Approved`；代码质量复审结论为 `Approved`，无 Critical 或 Important。质量复审 Agent 因其环境 PATH 缺少 Python 未能自行执行 pytest；主控在 feature worktree 独立运行 `python -m pytest -q` 得 `25 passed`，运行 `python -m pytest tests/unit/test_validation.py tests/unit/test_canonical.py -q` 得 `25 passed`，Draft 2020-12 Schema 元校验与 `git diff --check` 均通过。因此 G-02-T3 可标记为“已验证（子任务）”，R-008 关闭；该结论不覆盖 Compiler、Adapter、Evidence、Pipeline 或整个纵向切片。

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

## 未决项

- Accepted Definition 的 Schema/fixture 与 Core Pipeline 子范围已验证；产品 Skill 和执行记录仍需后续任务证据，见 `risk-register.md` 的 `R-001`。
- Task 3 的 semantic/canonical 顺序和 surrogate 错误边界已验证，R-008 已关闭；阶段出口仍需任务证据。
- Task 4 的 Compiler 与语义 Source Map 子范围已验证；Runtime 和阶段出口仍需后续任务证据。
- Task 6 的 Evidence/Manifest 子范围和远端同步已验证；Pipeline 与 drift 已覆盖正常提交、已测试失败路径和直接 symlink 边界，普通已有输出、Evidence 写入中途失败和阶段出口仍需后续任务证据。
- 当前 OPEN 的 P1 质量门槛关闭前，不得把计划中的 Expected 或模板结果写成执行完成。
