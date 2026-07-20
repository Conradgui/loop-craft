# Loop Craft 质量门槛

> 基线日期：2026-07-20
> 使用方式：按顺序记录 `OPEN / 部分完成 / 待执行验证 / 待质量审查 / 已验证（子任务） / PASS / FAIL / WAIVED`；子任务状态只覆盖列出的范围；没有命令输出、测试结果或明确审查结论时不得写 `PASS`。

| Gate | 对应风险 | 必须满足 | 证据 | 当前状态 |
|---|---|---|---|---|
| G-01 执行前置 | R-005 | 获得 Git 初始化、隔离 branch/worktree、目录命名及依赖环境的批准；确认 Python、pytest、jsonschema 版本；不擅自安装、复制或移动资源。 | 用户已确认整份操作清单：保留 ASCII 路径 `C:\Users\Administrator\Documents\loopcraft`、项目显示名“Loopcraft开发”、创建隔离 worktree、使用现有依赖且不安装。`main` 跟踪 `origin/main`；feature worktree 已创建并跟踪 `origin/feature/core-vertical-slice`；版本已确认 | PASS（仅执行前置门槛） |
| G-02 输入契约与范围 | R-001、R-002 | 在代码/Schema/证据中明确首条切片是 Accepted Definition 的受限子集；首条切片明确一个 Loop，或实现并测试空/多 Loop；不得宣称完整 Semantic IR、Runtime 或三入口已完成。 | `5a38ec7` 承接 Spec/Plan 边界；G-02-T1 已验证；G-02-T2 的 `e21c970` 已通过规格审查、联合定向测试和 Schema check，但代码质量审查 503 无结论且重试中 | 部分验证（Task 1 已验证；Task 2 待质量审查；后续范围 OPEN） |
| G-03 编译与 Source Map | R-002、R-003 | 重复构建产生相同 IR、artifact 和摘要；每个关键生成字段、当前 Profile 的 Loop 和元数据都有可回溯映射；Manifest 明确 Semantic IR、Execution IR、Override/no-override、Compiler、Adapter、Profile、Artifact 摘要。 | `5a38ec7` 承接并包含动态 workflow 映射及 Semantic IR/Override 字段断言设计；尚无 `source-map.json`、Manifest 或双构建证据 | 待执行验证 |
| G-04 产物与证据隔离 | R-003、R-004 | artifact 与 evidence 为兄弟目录；证据绑定 artifact digest；Adapter/Evidence 任一中途失败不留下可被误用的部分输出；漂移验证不修改 artifact。 | `5a38ec7` 承接并包含 TemporaryDirectory staging、原子 replace 和 Adapter 失败测试设计；尚无测试输出 | 待执行验证 |
| G-05 阶段出口 | R-001..R-005 | 完整相关测试、官方 Skill 结构校验、两次独立构建、clean/drift 验证、禁用词/依赖残留扫描全部有原始输出；执行记录只在全部通过后创建。 | `docs/records/2026-07-20-core-vertical-slice-execution.md` 及 build evidence | OPEN |

### G-02-T1 子门槛

| 子门槛 | 范围 | 证据 | 状态 |
|---|---|---|---|
| Task 1：确定性序列化测试基础 | canonical JSON 字节序列、SHA-256、NaN 拒绝及测试 harness；不包含 Schema、Compiler、Adapter、Evidence 或 Runtime | `8d811db`（含 `ab9116c`、`d95e4e3`）；独立运行 `python -m pytest tests/unit/test_canonical.py -q`：`4 passed in 0.02s`；隔离 worktree clean | 已验证（子任务） |

Task 1 的“已验证”不改变全局 G-02、G-03、G-04 或 G-05 的状态；后续任务必须分别提供命令和原始输出。

### G-02-T2 子门槛

| 子门槛 | 范围 | 证据 | 状态 |
|---|---|---|---|
| Task 2：Accepted Definition Schema 与基础语义校验 | Profile/单 Loop Schema、缺失字段、0/2 Loop 负例和基础 authority 语义校验 | `e21c970`；规格审查通过；`python -m pytest tests/unit/test_canonical.py tests/unit/test_validation.py -q`：`8 passed in 0.06s`；Schema check：`Schema check passed`；首次代码质量审查 HTTP 503 无结论，重试中 | 待质量审查 |

Task 2 的定向测试和规格审查不等于代码质量审查通过，也不覆盖 Compiler、Adapter、Evidence、Pipeline 或阶段出口。

## 不作为当前门槛的范围

Runtime、Scheduler、Hooks、递归/并行 Subloop、远程 Registry、Library Edition、三入口交互和完整 Override 是 Spec/Plan 明确的后续范围；它们在本切片中应保持未实现且不得被产品 Skill 宣称支持。
