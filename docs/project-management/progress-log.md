# Loop Craft 项目进度日志

> 基线日期：2026-07-20
> 记录规则：只写已执行动作和观察到的证据；计划步骤、Expected 输出和模板文本不算完成。

## 2026-07-20：管理基线与计划预审

### 已完成

- 完整阅读并按行核对：
  - `docs/specs/2026-07-20-loop-craft-phase-2-design.md`（614 行，状态 `Approved`，版本 `0.1.0`）；
  - `docs/plans/2026-07-20-loop-craft-core-vertical-slice.md`（1689 行）；
  - `docs/records/2026-07-20-resource-reuse-strategy.md`（240 行）；
  - `docs/references/resource-registry.yaml`（367 行）。
- 已确认工作区 `C:\Users\Administrator\Documents\loopcraft` 当前只有 `docs/`，尚未出现生产代码或测试目录；本 Agent 未修改生产代码、Spec、Plan 或资源注册表。
- 已执行 `git status --short`，结果为 `fatal: not a git repository`；因此当前没有可验证的 commit、branch 或“未提交改动清单”。
- 已建立本目录下四份治理文档：`decision-log.md`、`risk-register.md`、`quality-gates.md`、`progress-log.md`。
- 已记录五项 P1 门槛（输入契约子集、Loop 基数与 Source Map、Manifest 摘要、失败原子性、Git/环境前置）。
- 已把资源复用记录 §13 第 237 行“阶段 2 最终 Spec 尚未写入”标记为 `stale`，未改动原记录。

### 当前状态

- 管理状态：基线已建立，五项 P1 均为 `OPEN`。
- 实施状态：未开始；没有任何测试、构建、官方 Skill 校验或执行记录证据。
- P0：当前未发现。

### 下一步入口条件

1. 先获得 Plan 所列 Git、目录命名、隔离分支/worktree 和环境确认的批准，并留存命令输出。
2. 关闭 G-02，明确首条切片 Accepted Definition 子集和 Loop 基数；再开始生产实现。
3. 每个里程碑追加真实命令、摘要、差异和剩余风险；未通过的 Gate 保持 `OPEN` 或 `FAIL`。

## 2026-07-20：P1 设计修订复核

### 已观察修订

- Spec 当前为 616 行；§17 新增 `core-slice-v0.1`，明确首条切片恰好一个 Loop，且只是完整 Semantic IR 的受限实现子集。
- Plan 当前为 1746 行；已同步 Profile 字段、`loops` 的 `minItems/maxItems = 1`、0/2 Loop 负例、按实际 Loop 生成的 workflow Source Map、Manifest 的 `semantic_ir_digest/override_mode/override_digest`，以及 TemporaryDirectory staging、原子 `replace` 和 Adapter 失败清理测试设计。
- 资源复用记录 §13 第 237 行已改为“阶段 2 最终 Spec 已写入并批准”，此前 stale 项已消除。本 Agent 未修改该记录。
- 静态复核后，R-001 至 R-004 和 G-02 至 G-04 从 `OPEN` 更新为“待执行验证”；这只表示设计缺口已实质修订，不表示代码存在或测试通过。

### Git 与环境证据

- `git status --porcelain=v2 --branch`：当前为 initial `main`，`.gitignore` 与 `docs/` 均未跟踪。
- `git log --oneline -5`：返回当前分支没有 commit。
- `git worktree list --porcelain`：只列出主工作目录，HEAD 为全零；没有额外隔离 worktree/branch。
- `python --version`：`Python 3.13.13`。
- `python -m pytest --version`：`pytest 9.0.3`。
- jsonschema 版本：`4.26.0`。查询使用了已弃用的 `__version__` 属性并产生 DeprecationWarning；版本事实有效，后续应改用 `importlib.metadata.version("jsonschema")`。
- 未执行安装、提交、分支/worktree 创建、生产实现或测试。

### 当前状态

- G-01：部分完成。Git 初始化与依赖版本已确认；初始 commit、额外隔离 branch/worktree 和可引用批准记录仍缺失。
- G-02、G-03、G-04：待执行验证。
- G-05：仍为 `OPEN`，阶段出口不能提前通过。
- 残余检查：Adapter Source Map 已动态覆盖 workflow 的实际 Loop 集合，但其他生成元数据的字段级覆盖仍需在 G-03 验证；Plan 目前只显式注入 Adapter 失败，Evidence 写入失败由 staging 设计兜底但仍建议补定向测试。
- 资源复用记录 §13 第 238 行“Git 仓库尚未初始化”已被实际 `git init` 超越；未修改原记录，后续治理以本日志的命令证据为准。

## 2026-07-20：基线提交复核

### 已确认

- `git log -1`：`effd60b35d1ff438a75d6827d779011d433099f0`（短 SHA：`effd60b`），提交信息为 `docs: establish Loop Craft project baseline`。
- `git status --short --branch`：当前分支为 `main`；基线提交已存在。当前工作树另有资源记录的修改待提交，不能视为 clean；这不代表生产代码已实现。
- `git worktree list --porcelain`：只有主工作目录 `C:/Users/Administrator/Documents/loopcraft`，尚未创建额外隔离 worktree/branch。
- 资源记录 Git 条目已更新为基线提交 `effd60b`；管理文档中的 P1 设计修订已包含在该基线提交中。

### 当前状态

- G-01：部分完成。基线 SHA、环境版本和主分支已可追溯；隔离 worktree/branch 及批准记录仍缺失。
- G-02、G-03、G-04：待执行验证；设计修订已进入 `effd60b`，但没有实现、测试或构建通过证据。
- G-05：保持 `OPEN`。

## 2026-07-21：远程同步与隔离 worktree 复核

### 已确认命令事实

- `git remote -v`：`origin` fetch/push 均为 `https://github.com/Conradgui/loop-craft.git`。
- `git show -1 5a38ec7`：完整 SHA `5a38ec760ebd63920b111c7592095988368c59b4`，提交信息 `docs: record project baseline verification`。
- `git branch -vv`：`main` 为 `5a38ec7` 并跟踪 `origin/main`；本地 `feature/core-vertical-slice` 位于同一提交。
- `git status --short --branch`（主工作树）：`## main...origin/main`，无输出的未提交文件，主工作树干净。
- `git worktree list --porcelain`：主工作树之外，已创建 `C:/Users/Administrator/Documents/loopcraft/.worktrees/core-vertical-slice`，分支为 `feature/core-vertical-slice`，HEAD 为 `5a38ec760ebd63920b111c7592095988368c59b4`。
- 在隔离 worktree 执行 `git status --short --branch`：`## feature/core-vertical-slice`，未见未提交文件；`git log -1` 同为 `5a38ec7`。
- `git ls-remote --heads origin main feature/core-vertical-slice`：远端已确认 `main` 指向 `5a38ec7`；未返回 feature 分支，故 feature 当前仅有本地 worktree 证据。
- `git merge-base --is-ancestor effd60b 5a38ec7` 返回成功；P1 设计修订所在基线已进入治理更新提交的祖先链。

### 复核期间的状态变化

- 首次命令检查时，主工作树和隔离 worktree 均未列出未提交文件。
- 本次三份治理文档更新后，主工作树 `git status --short --branch` 显示 `decision-log.md`、`progress-log.md`、`quality-gates.md` 被修改，属于本次治理更新，尚未提交。
- 同期再次检查隔离 worktree，状态变为 `## feature/core-vertical-slice` 与 `?? tests/`。这些未跟踪文件不是本 Agent 创建或修改的；本 Agent 未读取、删除或移动它们。
- `tests/` 的存在不能证明测试已运行或通过；在有实际命令输出前，G-02 至 G-05 状态不变。

### 中间复核

- 隔离 worktree HEAD 仍为 `5a38ec7`，最新 `git status --short --branch` 显示以下新增文件已暂存：`loop-craft/scripts/loopcraft_core/__init__.py`、`loop-craft/scripts/loopcraft_core/canonical.py`、`pyproject.toml`、`tests/conftest.py`、`tests/unit/test_canonical.py`。
- 这些文件表明实现/测试脚手架正在进入暂存区，但没有提供测试命令、测试结果或新提交证据；G-02 至 G-05 不变。
- 主工作树仍有本次三份治理文档的未提交修改；本 Agent 未触碰隔离 worktree 中的实现/测试文件。

### 随后复核

- `git log -1`（隔离 worktree）：`ab9116c9c4230169f9c4c509361911b9bcb7f87f`，提交信息为 `test: establish deterministic core serialization`。
- `git show --stat ab9116c`：提交包含前述五个文件，共 66 行新增；`git status --short --branch` 随后只输出 `## feature/core-vertical-slice`，worktree clean。
- 未获得该提交对应的 pytest 命令或输出，因此只记录提交事实，不把提交信息中的 `test` 解释为测试通过。

### 当前状态

- G-01：部分完成。远程、main 推送、隔离 worktree/branch 和两处 HEAD 均有命令证据；目录命名决策尚未单独归档。
- G-02、G-03、G-04：待执行验证；`5a38ec7` 证明治理/设计基线，`ab9116c` 证明首批实现/测试脚手架已提交，但均未提供测试通过证据。
- G-05：保持 `OPEN`。
- 本 Agent 未执行或验证生产代码、安装、测试、构建或官方 Skill 校验；隔离 worktree 中虽已有 `ab9116c`，仍未将提交写成测试完成。

## 2026-07-21：Task 1 最终验证

### 已确认命令事实

- 隔离 worktree：`C:/Users/Administrator/Documents/loopcraft/.worktrees/core-vertical-slice`。
- 分支：`feature/core-vertical-slice`，跟踪 `origin/feature/core-vertical-slice`。
- `git log --oneline --decorate -8`：HEAD `8d811db`，其祖先包含 `d95e4e3`、`ab9116c`，基线为 `5a38ec7`。
- `git status --short --branch`：`## feature/core-vertical-slice...origin/feature/core-vertical-slice`，worktree clean。
- `python -m pytest tests/unit/test_canonical.py -q`：`.... [100%]`，`4 passed in 0.02s`。
- 当前里程碑交接结论称规格审查通过、代码质量审查最终为 `Approved`；本记录不把这两项审查结论扩展为后续任务通过。

### 门槛状态

- G-02-T1（canonical serialization/harness）：已验证。
- 全局 G-02：仅当前 Task 1 子范围有验证；Schema/Profile、单 Loop 负例、后续输入契约和范围边界仍待执行验证。
- G-03、G-04：仍待执行验证。
- G-05：仍为 `OPEN`；没有完整链路、官方校验、双构建、drift 或最终执行记录证据。

### 边界声明

Task 1 的 4 个测试通过只支持 canonical serialization/harness 的局部声明；不支持“Core vertical slice 已完成”或任何后续任务通过的声明。

## 2026-07-21：G-01 前置门槛纠正

### 用户已确认决策

- 保留本地 ASCII 路径：`C:/Users/Administrator/Documents/loopcraft`，不改为中文目录名。
- 项目显示名称：`Loopcraft开发`；本地目录名与产品显示名不要求相同。
- 使用隔离 worktree：`C:/Users/Administrator/Documents/loopcraft/.worktrees/core-vertical-slice`。
- 使用已确认的 Python/pytest/jsonschema 环境，不安装新依赖。

### Git 事实

- `git remote -v`：`origin` 为 `https://github.com/Conradgui/loop-craft.git`。
- `git branch -vv`：`main` 跟踪 `origin/main`；`feature/core-vertical-slice` 跟踪 `origin/feature/core-vertical-slice`。
- 用户已确认远程 feature 分支完成推送；后续远端 SHA 复核记录作为同步状态的权威证据。
- 隔离 worktree 正在推进后续任务；其当前未提交文件不影响 G-01 的“前置条件已建立”判断，也不能证明后续测试通过。

### 门槛状态

- G-01：`PASS`，仅表示执行前置门槛满足。
- G-02-T1：保持已验证；全局 G-02 仍只部分验证。
- G-03、G-04 仍待执行验证；G-05 保持 `OPEN`。

## 2026-07-21：Task 2 审查断点

### 已确认事实

- 隔离 worktree 当前分支为 `feature/core-vertical-slice`，HEAD 为 `e21c970`（`feat: validate accepted loop definitions`）。
- `git rev-list --left-right --count origin/feature/core-vertical-slice...feature/core-vertical-slice` 输出 `0 1`：feature 分支领先远程 1 个提交，尚未推送；worktree 当前 clean。
- Task 2 已通过规格审查（当前任务交接结论）。
- 独立联合定向命令：`python -m pytest tests/unit/test_canonical.py tests/unit/test_validation.py -q`，输出 `........ [100%]`、`8 passed in 0.06s`。
- 独立 Schema 元校验输出：`Schema check passed`。
- 当前快照尚无最终代码质量结论。本记录不写 `Approved`，也不把 Task 2 标为完成。

### 门槛状态

- G-01：PASS，仅表示执行前置门槛满足。
- G-02-T1：已验证。
- G-02-T2：待质量审查；规格和定向测试证据已存在，但质量审查结论缺失。
- 全局 G-02：部分验证，后续任务仍 OPEN。
- G-03、G-04：待执行验证。
- G-05：OPEN。

## 2026-07-21：Task 2 最终复核

### 提交与审查

- Task 2 修复提交：`a65f3b2`，验证基线范围为 `8d811db..a65f3b2`。
- 规格复审：`Approved`。
- 代码质量复审：`Approved`；此前未决状态已由最终复审结果取代。
- feature 后续合并 main 形成 `20d3ad4`。`git status --short --branch` 显示 worktree clean；`git rev-list --left-right --count origin/feature/core-vertical-slice...feature/core-vertical-slice` 为 `0 0`，`ls-remote` 也显示远端 feature 指向 `20d3ad4`。分支已同步不等于 Task 3 或纵向切片完成。

### 独立验证

- `python -m pytest -q`：`21 passed in 0.14s`。
- `python -m pytest tests/unit/test_canonical.py tests/unit/test_validation.py -q`：`21 passed in 0.13s`。
- `Draft202012Validator.check_schema(...)`：`Schema check passed`。
- `git diff --check`：退出码 0，无输出。

### 问题关闭与保留

- 已关闭 Important：surrogate canonical boundary。
- 已关闭 Important：identifier trailing controls。
- 已关闭 Important：blank/whitespace fields。
- 已关闭 Important：RFC 6901 root。
- `id.maxLength = 64` 已由规格复审认可。
- 保留 Minor：`validation.py` 使用原始 jsonschema `error.message`，非法输入诊断文本可能受键插入顺序影响；当前不阻塞有效定义确定性验收，defer。

### Plan 勘误

- `main` 远端提交 `1b7fb10` 已落地：Task 3 单 Loop 删除 duplicate 检查。
- Task 4/5：补强确定性、完整投影/Source Map、quoted safe frontmatter。
- Task 6：digest 覆盖完整 core subset。
- Task 8：预期测试数修正为 4。

### 当前状态

- G-01：PASS，仅执行前置门槛。
- G-02-T1、G-02-T2：已验证；全局 G-02 仍只覆盖 Task 1/2，后续范围 OPEN。
- G-03、G-04：待执行验证。
- G-05：OPEN。
- Task 3 已从 `20d3ad4` 启动但尚未完成；整个 Core vertical slice 尚未完成。

### 后续并发状态

- Task2 验证快照完成后，feature 新增提交 `5299f81`（`feat: reject contradictory authority semantics`）。
- 当前 `git rev-list --left-right --count origin/feature/core-vertical-slice...feature/core-vertical-slice` 为 `0 1`；该新提交尚未推送，且没有本次记录范围内的规格/代码质量复审结论。
- Task2 的 `21 passed`、Schema check 和 diff check 证据绑定到 `a65f3b2` / `20d3ad4` 快照，不外推到 `5299f81`。

## 2026-07-21：Task 3 质量阻塞

### Finding

- Task 3 提交 `5299f81` 暂不批准。
- 重要问题：当前验证顺序为 schema → semantic → canonical；semantic authority overlap 检查先运行时，如果同一孤立 surrogate 同时存在于重叠 authority 集合，错误消息格式化可能触发 `UnicodeEncodeError`。
- 该问题会把应有的稳定验证错误变成非预期编码异常，属于 P1 质量阻塞。

### 修复状态

- 已启动修复 Agent，目标顺序为 schema → canonical → semantic。
- 修复提交待定；需要补充 surrogate + authority overlap 回归测试，并重新进行代码质量审查。
- 当前 feature HEAD 为 `5299f81`，相对 origin 领先 1；`tests/unit/test_validation.py` 存在未提交修复改动。本次治理不触碰这些生产/测试文件，也不推送 feature。

### 门槛状态

- G-02-T1、G-02-T2：已验证，仅覆盖 Task 1/2。
- G-02-T3：质量阻塞，未完成。
- 全局 G-02：后续范围 OPEN。
- G-03、G-04：待执行验证。
- G-05：OPEN；Task 3 和整个 Core vertical slice 均未完成。

### 修复提交观察

- 修复 Agent 已提交 `2da604d`（`fix: validate canonical input before semantic checks`）。
- 当前 feature worktree clean，相对 `origin/feature/core-vertical-slice` ahead 2；本次治理没有推送 feature。
- 尚无该修复对应的回归测试输出或代码质量复审结论；G-02-T3 / R-008 继续保持质量阻塞，Task 3 仍未完成。

## 2026-07-21：Task 3 最终复核

### 实现与审查

- Task 3 实现提交为 `5299f81`，审查修复提交为 `2da604d`。
- 最终验证顺序为 schema → canonical → semantic；canonical 检查在 authority 集合运算与语义错误消息格式化之前执行。
- authority overlap 测试覆盖 `allowed` / `approval_required` / `forbidden` 的三组两两交叉；新增 surrogate 与 authority overlap 同时出现时优先返回 `non_canonical_json` 的组合回归。
- 当前 `core-slice-v0.1` 由 Schema 限制为恰好一个 Loop，Task 3 不实现 `duplicate_loop_id`。
- 规格复审：`Approved`。
- 代码质量复审：`Approved`，无 Critical 或 Important。该次复审未提供独立测试输出，测试证据以下述主控 fresh 执行为准。

### 独立验证

- 主控在 feature worktree 运行 `python -m pytest -q`：`25 passed`。
- 主控运行 `python -m pytest tests/unit/test_validation.py tests/unit/test_canonical.py -q`：`25 passed`。
- `Draft202012Validator.check_schema(...)`：`Schema check passed`。
- `git diff --check`：通过。
- feature worktree clean，HEAD 为 `2da604d`；相对 `origin/feature/core-vertical-slice` ahead 2。`5299f81` 与 `2da604d` 尚未推送，远端同步未完成。

### 门槛状态

- R-008：已关闭。
- G-02-T3：已验证（子任务）。
- 全局 G-02：仍为部分验证；Task 1-3 已验证，Compiler 及后续范围仍 OPEN。
- G-03、G-04：待执行验证；G-05：OPEN。
- Task 3 的通过不表示 Compiler、Adapter、Evidence、Pipeline、整个 Core vertical slice 或阶段 2 已完成。

## 2026-07-21：Task 4 最终复核

### 实现边界与审查

- Task 4 实现提交为 `61e9bbc`（`feat: compile accepted definitions deterministically`）。
- Compiler 先调用既有 schema → canonical → semantic validation，再对有效输入建立 `deepcopy` 快照并投影 Final Execution IR，避免结果与调用方可变输入共享嵌套对象。
- 确定性测试递归反转输入中所有字典键顺序，并比较 Final Execution IR canonical bytes/digest、`definition_digest` 和 Source Map canonical bytes。
- Source Map 覆盖根 definition digest、Schema/Profile、Behavior Contract、Loop id/entrypoint、node id/instruction/next、terminal mapping 和 invariants；`compiler_version` 是生成元数据，不建立伪造的语义映射。
- 规格审查：`Approved`。代码质量审查：`Approved`，无 Critical 或 Important。
- 保留 Minor：测试尚未直接断言 `definition_digest == sha256_digest(definition)`；当前实现正确且该项不阻塞 Task 4，登记为 R-009。

### 独立验证

- 主控使用项目选定的 Python 3.13 绝对路径运行 `python -m pytest tests/unit/test_compiler.py -q`：`5 passed`。
- 主控运行 validation + canonical + compiler 组合测试：`30 passed`。
- 主控运行全量 `python -m pytest -q`：`30 passed`。
- `Draft202012Validator.check_schema(...)`：`schema check: passed`。
- `git diff --check`：通过。
- feature worktree clean，HEAD 为 `61e9bbc`；相对 `origin/feature/core-vertical-slice` ahead 1。该提交尚未推送，不记录远端同步完成。

### 门槛状态

- G-02-T4：已验证（子任务）；全局 G-02 仍为部分验证。
- G-03、G-04、G-05 不提前关闭；Adapter、Evidence、Manifest、重复构建与阶段出口仍待验证。
- Task 4 的通过不表示 Adapter、Evidence、Runtime、Pipeline、整个 Core vertical slice 或阶段 2 已完成。

## 2026-07-21：Task 5 最终复核

### 实现边界与审查

- Task 5 原始实现提交为 `db4e4b2`（`feat: render target Codex Skills from execution IR`），审查修复提交为 `c282fc6`（`fix: harden generated Skill boundaries`）。
- Adapter 只把 Final Execution IR 投影为 `SKILL.md`、`agents/openai.yaml` 和 `references/final-execution-ir.json` 三个目标 Skill 文件；不生成 Evidence Package，不承担 Runtime，不引入 Loop Library 或 Library Edition 内容。
- Markdown 正文的自由文本以单行 JSON string literal 输出，保留原值的同时避免换行、标题和列表内容被解释为新的 Markdown 结构；这不宣称具备通用 HTML sanitization。
- `directory_digest` 按排序后的 POSIX 相对路径和文件 bytes 计算，并分别加入 8-byte big-endian path/content 长度前缀，关闭原 NUL 分隔算法的 digest 碰撞边界。
- coarse workflow Source Map 覆盖 `id`、`entrypoint`、`nodes`、`terminal_mapping`、`invariants`，并提供逐字段细粒度映射。固定 stop rule 规定 terminal condition 一旦满足立即停止，terminal outcome 优先于任何 node `Next` 转移。
- 规格复审：`Approved`。代码质量复审：`Approved`，无 Critical 或 Important。修复关闭 Markdown 多行注入、NUL digest 碰撞、coarse workflow Source Map 缺口和 terminal stop precedence 四项问题。
- 保留 Minor：JSON literal 仍保留 `<...>`。未来若接入不可信 HTML renderer，需要由对应 Adapter 做上下文相关 sanitization；登记为 R-010，当前不阻塞。

### 独立验证与证据来源

- 主控使用 fresh Python 3.13 独立运行 `python -m pytest tests/unit/test_codex_skill_adapter.py -q`：`8 passed`。
- 主控独立运行全量 `python -m pytest -q`：`38 passed`；静态检查通过。
- 官方 `quick_validate.py` 在修复前的 rich fixture 上由主控独立确认输出 `Skill is valid!`。
- 修复后的 hardened injection fixture validator 只有实现 Agent 的结果；该结果不登记为主控独立验证证据，也不据此扩大质量声明。
- feature worktree clean，HEAD 为 `c282fc6`；远端 feature 仍为 `09cc0c1`，本地当前领先 2 个提交。`db4e4b2` 和 `c282fc6` 尚未推送，不记录远端同步完成。

### 门槛状态

- G-02-T5：已验证（子任务）；全局 G-02 仍为部分验证。
- G-03 只增加 Adapter/Adapter Source Map 子范围证据，仍为部分完成；G-04、G-05 不提前关闭。
- Task 5 的通过不表示 Evidence、Manifest、Runtime、Library、Pipeline、整个 Core vertical slice 或阶段 2 已完成。

## 2026-07-21：Task 5 远端同步闭环

- main 与远端 main 均为治理提交 `27046644a0181f0b6fa3efb0bcb3e541e9594f5a`。
- feature 的本地与远端均为 merge 后 HEAD `1c0f1852b765a4aef288bf33ed88ce653a0ff071`；该提交包含 Task 5 实现提交 `db4e4b2`、审查修复提交 `c282fc6` 和 main 治理提交 `2704664`。
- 主控在治理提交合并进 feature 后 fresh 运行全量 pytest：`38 passed`；`git diff --check` 通过，main 与 feature 两个工作树均 clean。
- 本记录只关闭 Task 5 的远端同步闭环，不改变后续任务或全局门槛状态。

## 2026-07-21：Task 6 最终复核

### 实现边界与审查

- Task 6 实现提交为 `826f285`（`feat: package auditable build evidence`），审查修复提交为 `475b2a4`（`fix: reject inconsistent evidence inputs`）。
- Evidence Package 与 artifact 物理隔离；五份输出均为 canonical JSON + LF：Accepted Definition、Final Execution IR、Source Map、Validation Report 和 Build Manifest。
- Manifest 绑定 definition、完整 core semantic subset、Final Execution IR、Profile、Adapter 和当前 artifact digest，并明确 `override_mode: none`、`override_digest: null`。
- `package_evidence` 在 `mkdir` 前拒绝 definition/Execution IR、artifact/Execution IR、当前 artifact digest 错配，以及 Evidence/artifact 路径相同或互为祖先/后代；拒绝路径不留下 Evidence 目录。
- 初始 TDD RED 为 import failure；审查加固的四类 RED 均为 `DID NOT RAISE ValueError`。
- 规格复审：`Approved`，无 Missing、Extra、Misinterpreted 或越界。代码质量复审：`Approved`，无 Critical 或 Important。
- 保留 Minor：`artifact.source_map` 是浅可变字典，调用方可在 render 后篡改；当前内部立即传递场景不触发，且 Task 6 无 Source Map 自身摘要契约。登记为 R-011，deferred，不阻塞。

### 独立验证

- 主控使用 fresh Python 3.13 运行 `python -m pytest tests/unit/test_evidence_package.py -q`：`6 passed`。
- 主控运行全量 `python -m pytest -q`：`44 passed`。
- `git diff --check`：通过。
- feature worktree clean，HEAD 为 `475b2a4`；相对远端 ahead 2。`826f285` 和 `475b2a4` 尚未 push，不记录远端同步完成。

### 门槛状态

- Task 6 子门：已验证（子任务）。
- G-03、G-04 只增加 Evidence/Manifest 与写入前拒绝子范围证据，仍为部分完成；G-05 保持 `OPEN`。
- Task 6 的通过不表示 Pipeline、双构建、drift、Runtime、Library、整个 Core vertical slice 或阶段 2 已完成。

## 2026-07-21：Task 6 远端同步闭环

- main 本地与远端均为 Task 6 治理提交 `cdc31045a74a1d7b30a5715cd74195804f2a431f`。
- feature 本地与远端均为 `6d295abd48b2afc0e6bf8178595f8d6fd5840776`；该 HEAD 包含 Task 6 实现 `826f285`、修复 `475b2a4`、治理 `cdc3104`，以及后续 Task 7 提交。
- 远端核验时 main 与 feature 两个 worktree 均 clean；该记录只关闭 Task 6 远端同步，不扩大 Task 6 的质量声明。

## 2026-07-21：Task 7 最终复核

### 实现边界与审查

- Task 7 实现提交为 `8253c24`（`feat: build Skill and evidence in one deterministic pipeline`），安全修复提交为 `6d295ab`（`fix: preserve occupied output paths`）。
- Pipeline 在 `output_root.parent` 内创建 `TemporaryDirectory`，按 Adapter → Evidence 顺序写入 staging；只有两者全部成功后才执行 `staging_root.replace(output_root)`。
- 非法定义与 Adapter 失败不留下正式 output；两次构建的文件树和 Manifest 相同。
- 初始 TDD RED 为 `ModuleNotFoundError`（`loopcraft_core.pipeline`）；dangling symlink 回归 RED 为最终 replace 处 `PermissionError: [WinError 5]`。修复使用 `output_root.exists() or output_root.is_symlink()` 提前拒绝已占用路径并保留 symlink。
- 本任务 CLI 只有 `definition`、`output` 两个位置参数；drift/verify 子命令不属于 Task 7。
- 规格复审与代码质量复审均为 `Approved`，无 Critical 或 Important；symlink Minor 已关闭。

### 独立验证与边界

- 主控 fresh 运行 `python -m pytest tests/integration/test_build_pipeline.py -q`：`4 passed`。
- 主控运行全量 `python -m pytest -q`：`48 passed`。
- 真实 CLI 退出 0；生成 artifact 3 文件、Evidence 5 文件。
- `git diff --check`：通过。
- main 本地/远端均为 `cdc3104`，feature 本地/远端均为 `6d295ab`；两个 worktree clean。
- 保留边界：受限 Windows 可能无 symlink 测试权限；真实 CLI 尚未自动化，普通已有输出与 Evidence 部分写失败没有自动回归；强杀和非本地文件系统的 replace 原子性未验证。合并登记为 R-012，deferred，不阻塞 Task 7。

### 门槛状态

- Task 7 子门：已验证（子任务）。
- G-03 增加 deterministic dual-build 子证据；G-04 增加 Pipeline 正常提交及已测试失败路径子证据，仍不关闭；G-05 保持 `OPEN`。
- Task 7 的通过不表示 drift、Runtime、Library、整个 Core vertical slice 或阶段 2 已完成。

## 2026-07-22：Task 7 远端同步闭环

- main 本地与远端均为 Task 7 治理提交 `4e302b57d93cff563fd7dab7cd20203d4384f863`。
- feature 本地与远端均为 `98e3f9aa079da978265ab9d2112685ed1fc1a276`；该 HEAD 包含 Task 7 实现 `8253c24`、修复 `6d295ab` 和治理 `4e302b5`。
- 远端核验时两个 worktree 均 clean；该记录只关闭 Task 7 远端同步，不扩大质量声明。

## 2026-07-22：Task 8 最终复核

### 实现边界与审查

- Task 8 功能提交为 `b5f4ebe`；审查加固提交为 `077a540`、`220669e`、`4474f48` 和 `2ec976a`。
- `verify_build` 只读 Manifest 与 artifact 摘要，返回 `clean` / `drifted`，不会重建、修复或写回 artifact/Evidence。
- artifact root 必须恰好包含一个真实 Skill 目录；额外文件/目录、symlinked Skill 目录和 tree 内 symlink 均拒绝。
- `output_root`、Evidence 目录和 Build Manifest 的直接 symlink 在读取 JSON 前拒绝，避免沿链接读取 output 外内容。
- CLI 提供 `build` / `verify` 子命令；真实 subprocess 回归覆盖 build 0、clean verify 0、drifted verify 1、JSON 报告及不写回 artifact。
- 初始 RED 为 `verify_build` 导入失败；路径边界负例在修复前均为 `DID NOT RAISE ValueError`。CLI 测试通过临时未提交的错误退出码验证能捕获回归，最终提交不含故障注入。
- 最终规格复审与代码质量复审均为 `Approved`，无 Critical 或 Important。

### 独立验证与边界

- 主控 fresh Python 3.13 运行 drift + pipeline/CLI 定向测试：`14 passed`。
- 主控运行全量测试：`58 passed`。
- `git diff --check`：通过；feature HEAD 为 `2ec976a`，worktree clean，相对远端领先 5 个提交，尚未 push。
- 保留 residual：测试辅助 `file_snapshot` 能证明文件内容未改变，但不能单独证明从未读取或元数据未变；实现顺序已静态确认直接 symlink 在读取相应目标前拒绝。当前不扩展到 junction、hardlink 或数字签名。

### 门槛状态

- Task 8 子门：已验证（子任务）。
- G-03 增加 clean/drift 摘要核对子证据；G-04 增加非破坏性 drift 与直接 symlink 边界证据，仍为部分完成；G-05 保持 `OPEN`。
- Task 8 的通过不表示产品 Skill、Runtime、Library、整个 Core vertical slice 或阶段 2 已完成。

## 2026-07-22：Task 9 最终复核

### 产品包装与边界

- Task 9 实现提交为 `d6a3ebb`；测试加固提交为 `67b1d22` 和 `adbde41`。
- 产品 Skill 新增 `SKILL.md`、`agents/openai.yaml` 和 `references/core-build.md`；集成测试位于 `tests/integration/test_loop_craft_skill.py`。
- Skill 只覆盖 accepted Behavior Contract JSON 的 build 与 existing build 的 drift verify。reference 明确从 `loop-craft` Skill 目录运行命令，build 要求新输出目录，verify 对已有 build 只读；不宣称三入口、Runtime、Library、发布或调度。
- 测试锁定精确 metadata、相对 reference 链接、文档命令，以及 build、clean verify、drift verify 的 CLI 合同；drift 回归确认 JSON `drifted`、退出码 `1` 且不写回 `SKILL.md`。

### 独立验证与审查

- 主控 fresh Python 3.13 运行 Task 9 集成测试：`6 passed`。
- 主控运行全量测试：`64 passed`。
- 官方 `quick_validate.py`：`Skill is valid!`；`git diff --check`：通过。
- 规格复审和代码质量复审均为 `Approved`，无 Missing、Extra、Misinterpreted、越界、Critical 或 Important。Creator Pro 行为合同、branch index、信息层级、可观察门和剪枝原则已应用；官方 validator 是兼容底线，不记录 `quality_lint` 已通过。
- feature HEAD 为 `adbde41`，worktree clean，相对 `origin/feature/core-vertical-slice` ahead 3，未 push。真实 forward behavioral test 按约束留到整个链路完成后。

### 门槛状态

- Task 9 子门：已验证（子任务）。
- G-02 增加产品 Skill 声明与 Build/reference 边界证据；G-03、G-04 保持现有部分完成状态；G-05 仍为 `OPEN`。
- Task 9 的通过不表示 Runtime、Library、三入口、发布/调度或阶段出口完成；Task 10 仍需执行完整出口核对。

## 2026-07-22：Task 10 Core 纵向切片出口

### 契约收口

- 最终代码 SHA：`d9bfab2e297f6d0ebf0e64df5d1b39f8f1d7ccd8`；worktree 在出口验证前 clean。
- 最终修复补齐 Evidence 五文件/摘要/成功状态、全部触发条件投影与目标上限、短描述和 Source Map、严格摘要格式、空 artifact、普通已有输出保护、Evidence 部分写失败清理，以及清洗后空触发条件的写入前拒绝。
- 最终规格复审和全局代码质量复审均为 `Approved`；最终契约修复无未关闭的 Critical 或 Important。R-007、R-009、R-010、R-011 的既有 deferred Minor 与 R-012 的 P2 residual 继续跟踪。

### Fresh 出口证据

- Python `3.13.13`；`python -m pytest -q`：`110 passed in 6.04s`。
- `build/final-20260722-a` 与 `build/final-20260722-b` 均由 accepted fixture 独立构建成功。
- 产品 `loop-craft` 与生成 `skill-polish-loop` 均由官方 `quick_validate.py` 验证为 `Skill is valid!`。
- 两次 `verify` 均为 `clean`；artifact expected/actual digest 均为 `sha256:23ac2315e146fcb6b278b004fed44e9a4473425147449b348ffefee21939f357`。
- 两棵输出树均为 8 个文件，路径和逐文件 SHA-256 完全一致；产品 Skill 与生成 artifact 的 `loopy|loop library` 扫描无匹配。
- 完整命令、逐文件摘要和 Manifest 摘要已固化在 `docs/records/2026-07-22-core-vertical-slice-execution.md`。

### 门槛与边界

- G-02、G-03、G-04、G-05 对当前 Core vertical slice 均达到 PASS；R-001 至 R-004 的当前切片 P1 关闭。
- 强杀与非本地文件系统原子性继续作为 P2 residual，不外推当前本地文件系统证据。
- 本次不表示阶段 2 全链路完成；三入口、Runtime、Override、Subloop、Library Edition、发布/调度及真实 forward behavioral experiment 仍未实现或未执行。

## 2026-07-22：Skill Upgrade 第二入口 Walking Skeleton

- 复用 Phase 1 的 Skill contract recovery、Observed/Inferred、七项 Loopability Gate、四类 verdict、finding IDs 和先决策后修改规则；未重写一套入口框架。
- `loop-craft/SKILL.md` 已暴露 Existing Skill Upgrade；新增 `references/upgrade-skill.md`，Assessment 默认只读并返回完整 Decision Record。
- 当前 Core compatibility gate 只允许单一 `loop_first_skill`、可无损映射 `core-slice-v0.1`、且无需保留关键 scripts/assets/references/扩展 metadata 的情况进入真实 build。其他 verdict 或资源型 Skill 明确停在 `Assessment only`。
- 该边界避免把 embedded/split Loop 压扁成一个 Loop，也避免把新生成的替代 Skill 冒充任意既有 Skill 的保真升级。
- 必要验证：官方 `quick_validate.py` 输出 `Skill is valid!`；路由、四 verdict、Assessment only、Core reference、禁用名称残留和 dashboard JSON 静态检查通过；`git diff --check` 通过。未重复运行 Core 全量测试，因为本次未修改 Core 代码。
- 质量管理 Agent 按 8 项主线清单复核，Critical、Important、Minor 均无发现。

## 2026-07-22：Conversation Distiller 第三入口 Walking Skeleton

- 高保真复用 Workflow Skill Creator 的“已发生工作流摘要 → 用户纠正 → 逐步澄清 → 明确批准”，没有复制其领域包、固定运行器、CLI-first、固定安装路径或独立测试假设。
- 新增 `references/from-conversation.md`：只读取用户授权材料，恢复带 `observed / inferred / proposed / missing / conflict` 标签的 Workflow Model，再形成 Candidate Behavior Contract。
- 第三入口复用现有七项 Loopability Gate、泛化后的三入口 Candidate Review 和 Core compatibility gate，没有新增第二套 Workflow-to-Loop 或 Compiler。
- 0 个 Loop 返回一次性 Workflow/Skill assessment；多个独立 Loop 或无法无损表达时停在 Candidate；只有一个 defining Loop 且兼容 `core-slice-v0.1` 时才进入真实 build。
- 当前 Core manifest 不绑定入口来源证据。Workflow Model、澄清和批准记录只能暂存为输出根目录的 `entry-evidence.md`，明确标记 `supplemental, manifest-unbound`；它不进入要求恰好五个文件的确定性 `evidence/`。
- 必要验证：官方 Skill validator 输出 `Skill is valid!`；第三入口引用、五类标签、0/1/>1 分流、补充证据声明、旧产品名残留和 dashboard JSON 静态检查通过；未运行 Core 全量测试。
- 质量管理 Agent 最终复核无 Critical 或 Important；一个入口首句预期过强的 Minor 已修正。

## 2026-07-22：Skill Packaging Adapter Walking Skeleton

- 新增 `skill-package-v0.1`，不放宽原 `core-slice-v0.1`。新 profile 严格二选一：`loops: []` 时必须提供 `workflow.steps / success_evidence / failure_or_stop`；一个 Loop 时禁止同时携带 workflow。
- 0-loop 路线从获批 Behavior Contract 和 Final Execution IR 生成完整普通 Skill，不制造反馈闭环。
- 既有 Skill 路线先用 `inventory` 生成只含相对路径、逐文件摘要和 `preserve / overlay / generated` 动作的 Source Package Manifest；构建时重新盘点并逐文件复核摘要。
- Source overlay 保留原 `SKILL.md`、metadata、references、scripts、assets 和 license bytes，在新目录追加完整获批 Behavior Contract + Loop；原源目录不修改，未知根项、链接/junction、名称不一致、路径重叠和 stale manifest 均阻断。
- Source Package Manifest 作为第六份 Evidence 文件，其摘要和完整源包摘要由 Build Manifest 绑定；`verify` 同时支持五文件新包和六文件 source-bound 包。
- Codex Adapter 输出 `native / degraded / unsupported` Compatibility 和 `self_contained` Conformance；required unsupported 在写出前阻断，optional unsupported 记录 degraded，`verify` 从 Final IR 重算。
- 复用 Skill Creator Pro 的 Behavior Contract、最小完整目录、元数据后置生成与结构 validator；复用 Skill Polisher 的只读盘点、保留不变量、最小批准修改和完整包复核。两者仅为设计参考，不成为运行依赖。
- 主控定向验证：Packaging 相关测试 `9 passed`；元数据测试 `1 passed`；0-loop 与 source-overlay 两个真实构建均通过官方 Skill validator 和 clean verify；未运行无关全量测试。
- 首次独立质量复核提出 3 个 Important：workflow+Loop 含混、verify junction 边界和 Compatibility/Conformance 缺失；均已最小修复并定向复验。
