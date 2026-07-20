# Loop Craft 质量门槛

> 基线日期：2026-07-20
> 使用方式：按顺序记录 `OPEN / 部分完成 / 待执行验证 / PASS / FAIL / WAIVED`；“待执行验证”只表示 Spec/Plan 已实质修订，没有命令输出、测试结果或批准记录时不得写 `PASS`。

| Gate | 对应风险 | 必须满足 | 证据 | 当前状态 |
|---|---|---|---|---|
| G-01 执行前置 | R-005 | 获得 Git 初始化、隔离 branch/worktree、目录命名及依赖环境的批准；确认 Python、pytest、jsonschema 版本；不擅自安装、复制或移动资源。 | 已确认 Git initial `main`；Python 3.13.13、pytest 9.0.3、jsonschema 4.26.0。仍缺初始 commit、额外隔离 branch/worktree 和可引用的批准记录 | 部分完成 |
| G-02 输入契约与范围 | R-001、R-002 | 在代码/Schema/证据中明确首条切片是 Accepted Definition 的受限子集；首条切片明确一个 Loop，或实现并测试空/多 Loop；不得宣称完整 Semantic IR、Runtime 或三入口已完成。 | Spec/Plan 已加入 `core-slice-v0.1`、单 Loop 约束和负例设计；尚无实现/测试输出 | 待执行验证 |
| G-03 编译与 Source Map | R-002、R-003 | 重复构建产生相同 IR、artifact 和摘要；每个关键生成字段、当前 Profile 的 Loop 和元数据都有可回溯映射；Manifest 明确 Semantic IR、Execution IR、Override/no-override、Compiler、Adapter、Profile、Artifact 摘要。 | Plan 已加入动态 workflow 映射及 Semantic IR/Override 字段断言；尚无 `source-map.json`、Manifest 或双构建证据 | 待执行验证 |
| G-04 产物与证据隔离 | R-003、R-004 | artifact 与 evidence 为兄弟目录；证据绑定 artifact digest；Adapter/Evidence 任一中途失败不留下可被误用的部分输出；漂移验证不修改 artifact。 | Plan 已加入 TemporaryDirectory staging、原子 replace 和 Adapter 失败测试；尚无测试输出 | 待执行验证 |
| G-05 阶段出口 | R-001..R-005 | 完整相关测试、官方 Skill 结构校验、两次独立构建、clean/drift 验证、禁用词/依赖残留扫描全部有原始输出；执行记录只在全部通过后创建。 | `docs/records/2026-07-20-core-vertical-slice-execution.md` 及 build evidence | OPEN |

## 不作为当前门槛的范围

Runtime、Scheduler、Hooks、递归/并行 Subloop、远程 Registry、Library Edition、三入口交互和完整 Override 是 Spec/Plan 明确的后续范围；它们在本切片中应保持未实现且不得被产品 Skill 宣称支持。
