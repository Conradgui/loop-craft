# Loop Craft 双 Adapter 与 Codex 兼容门设计

> 日期：2026-07-31
>
> 状态：设计已获用户口头确认，等待书面规格复核
>
> 目标版本：0.4.0 candidate
>
> 范围：Compact Prompt Adapter、Codex Skill 兼容门、Adapter 中立 Evidence

## 1. 产品结果

Loop Craft 从同一份已批准的 Final Execution IR 提供两条真实、可验证的输出路径：

1. `codex-skill`：生成完整 Codex Agent Skill；
2. `compact-prompt`：生成可直接复制使用的短 Prompt。

一次 build 只选择一个 Adapter，并生成一个 Artifact 与一份绑定该 Artifact 的 Evidence
Package。两条路径不互相转换，也不把 Evidence 当作生成输入。

Runtime、Override、Subloop、多 Loop、Catalog、发布和调度不属于这次双输出闭环。

## 2. 已确认的架构

```text
From scratch ─┐
Existing Skill├─→ Shared Gate / Review → Accepted Definition
Conversation ─┘                                ↓
                                     Deterministic Compiler
                                                ↓
                                       Final Execution IR
                              ┌─────────────────┴─────────────────┐
                              ↓                                   ↓
                      Evidence Packager                     Adapter Router
                              ↓                          ┌─────────┴─────────┐
                       Evidence Package                  ↓                   ↓
                                                  Codex Skill         Compact Prompt
```

Evidence Packager 与 Adapter Router 是 Final Execution IR 的并行消费者。Evidence 负责审计；
Artifact 只携带目标使用场景需要的内容。

## 3. 方案选择

采用混合方案：

- 保留内部确定性的 Codex Skill Adapter 作为构建权威；
- 从旧 Loopy 迁移 Compact Prompt 的压缩规则，不从零发明另一套 Loop 语义；
- 复用 Skill Creator PRO@`eb23656e56ea3555599a6c5278a8b5834dc56b6d` 的 Behavior
  Contract、信息层级、确定性脚本、quality lint 和风险比例化 forward-test 方法；
- 使用当前 Codex 内置 Skill Creator 的原生 Validator 做结构兼容检查；
- Agent 复核只提出问题。问题必须修回 Adapter 或模板，再从同一个 IR 重建；不得直接修改
  已生成 Artifact 后继续沿用旧 Evidence。

不在每次 build 中调用另一个 Agent 临场撰写 Skill。这样既减少重复设计，又保留可重现构建、
Source Map、digest 和 drift verify。

## 4. Adapter Router 与命令合同

构建命令增加显式 Adapter 选择：

```powershell
python scripts/build_loop.py build definition.json output-dir --adapter codex-skill
python scripts/build_loop.py build definition.json output-dir --adapter compact-prompt
```

规则：

- `--adapter` 缺省值保持为 `codex-skill`，现有调用不被破坏；
- 合法值只有 `codex-skill` 与 `compact-prompt`；
- 一次 build 只生成一个 Artifact 目录；
- `--source-skill` / `--package-manifest` 只与 `codex-skill` 兼容；
- Existing Skill 的 source-preserving upgrade 不得被压缩成短 Prompt；请求该组合时明确停止；
- Direct Build、From-scratch 和兼容的 Conversation Definition 可以选择 Compact Prompt；
- Adapter 选择不改变 Accepted Definition 或 Final Execution IR 的语义。

## 5. Adapter 中立 Artifact 合同

把当前 Evidence Packager 对 `SkillArtifact` 的硬依赖收窄为 Adapter 中立结果。公共结果至少包含：

```text
artifact_dir
artifact_digest
source_map
adapter_name
adapter_version
profile_digest
compatibility_report
conformance
```

Codex Skill Adapter 与 Compact Prompt Adapter 分别负责自己的内部结构验证。Evidence Packager
只验证公共合同、IR 绑定、Artifact digest 与物理隔离，不假设 Artifact 必须含有
`references/final-execution-ir.json`。

Codex Skill 仍可保留当前受控 IR reference；Compact Prompt 不为满足 Skill 专属假设而携带额外
运行文件。

## 6. Compact Prompt Adapter

### 6.1 输出形态

```text
artifact/
└─ <identity-id>/
   └─ PROMPT.md
```

`PROMPT.md` 包含一个简短标题、一句用途说明和一个可复制 Prompt。说明不计入 Prompt 本体。

### 6.2 压缩规则

迁移旧 Loopy 已验证的表达顺序：

```text
触发/目标 → 行动 → 反馈检查 → 调整 → 停止 → 审批边界
```

普通零 Loop Workflow 改用：

```text
触发/目标 → 必要步骤 → 成功证据 → 失败或停止 → 审批边界
```

Adapter 必须保留会改变行为的 required 能力、验证规则、停止条件、禁止项和审批边界。不得为了
达到字数目标而静默删除安全或正确性语义。

短 Prompt 以英文少于约 80 words 为软目标；中文和其他语言采用“一个短、自包含段落”的等价
目标。安全与正确性需要时允许超过软目标，并在 Compatibility Report 中记录原因。

### 6.3 兼容性结论

- `native + self_contained`：必要语义均可在 Prompt 中表达；
- `degraded`：只允许 Optional 能力降级，并在 Evidence 中列明；
- `unsupported`：required 能力、审批、验证或停止语义无法无损表达，构建失败；
- `lossy` 产物不得被交付为完整 Loop。

## 7. Codex Skill 兼容门

### 7.1 每次构建的确定性门

Codex Skill Candidate 生成后、Evidence 最终落盘前执行：

1. Loop Craft 内部 Adapter contract 检查；
2. 当前 Codex 内置 Skill Creator 的 `quick_validate.py`；
3. 生成 Native Validation Receipt，再由 Manifest 绑定。

Receipt 记录 validator 名称、可识别版本或脚本 SHA-256、退出状态和规范化结果，不记录本机绝对
路径。官方 Validator 不可达时，用户入口停止并报告 `native_validation_unavailable`，不得宣称
当前 Codex 原生兼容。测试可以注入固定 Validator fixture，不依赖开发机绝对路径。

### 7.2 Agent 质量复核

Skill Creator PRO 的 `quality_lint.py` 是结果稳定的启发式扫描，但 finding 需要工程判断，不能
伪装成确定性合规结论。它与 Codex 内置 Skill Creator 的 Agent 复核都不进入每次 build 的生成
步骤，而在以下情况触发：

- Codex Skill Adapter 或模板发生行为性变化；
- 官方 Validator 或 Skill 规范发生变化；
- 发布候选需要新鲜上下文复核。

复核只产生 finding。修复必须落到 Adapter、模板或公共合同，随后重新 build、重新运行 Validator、
重新生成 Evidence。quality lint finding 必须修复或逐项说明不适用；禁止仅修某一个输出目录。

## 8. Skill Creator PRO 复用边界

复用：

- Behavior Contract-first；
- trigger branches 与 near misses；
- 一个 owner 对应一个 behavior、artifact、adapter 和 route；
- progressive disclosure 与运行 Artifact / 人类文档分离；
- 确定性的 Validator 与必要元数据生成机制；
- 作为 Adapter 变更/发布复核输入的 heuristic quality lint；
- 与本次风险对应的最小 forward test。

不复用：

- 把 Skill Creator PRO 变成 Kernel 语义权威；
- 每次构建时让 Agent 重写 Skill；
- 与发布、仓库初始化或远端变更有关的默认分支；
- 不适用于 Loop Craft 当前 0/1 Loop profile 的完整生命周期步骤。

任何被抽取或本地化的确定性脚本必须记录上游 revision、许可证与本地改动，不复制无关文件。

## 9. Evidence 与 Verify

Build Manifest 根据选择写入真实 Adapter：

```text
adapter: codex-skill | compact-prompt
adapter_version: <adapter-owned version>
profile_digest: <selected profile digest>
artifact_digest: <selected artifact digest>
```

Codex Skill 路径另外绑定 Native Validation Receipt。Compact Prompt 路径绑定自己的
Compatibility Report 与 Conformance，不伪造 Codex Skill 原生验证。

`verify` 继续只读检查：Evidence 文件集合、Manifest 绑定、Source Map、Artifact digest 与可选
Validator Receipt。它不重新生成、不修复，也不要求原始输入路径继续存在。

## 10. 错误与停止行为

- 未知 Adapter：参数错误，输出目录保持不存在；
- Compact Prompt + source-preserving 参数：明确不兼容，输出目录保持不存在；
- required 语义不可表达：`unsupported`，不产出伪完整 Prompt；
- 官方 Codex Validator 失败：保留临时诊断，正式输出目录不落盘；
- 官方 Validator 不可达：用户路径停止，不声称兼容；
- quality lint finding：在 Adapter 变更/发布复核中修复或记录不适用理由，不把启发式结果伪装成
  每次 build 的确定性硬门；
- Agent 复核发现问题：修改 Adapter 后重建，不直接修 Artifact；
- 任一步失败：不覆盖既有输出目录。

## 11. 最小验证策略

测试只覆盖会改变交付判断的现实风险：

1. 省略 `--adapter` 时现有 Codex Skill build 字节与合同保持兼容；
2. 同一 IR 两次生成 Compact Prompt，Artifact 与 Source Map digest 相同；
3. 0-loop Workflow 与 1-loop Loop 分别保留成功/反馈、停止和审批边界；
4. 不可无损表达的 required 语义 fail closed；
5. Compact Prompt 与 source-preserving 参数组合被拒绝；
6. 两种 Adapter 的 Manifest、Evidence 文件集合和 drift verify 各自正确；
7. Codex 原生 Validator 的 pass、fail、unavailable 三条路径可观察；
8. 当前官方 Validator 对生成 Skill 通过；
9. 只安排一个针对 Skill 路径和一个针对 Prompt 路径的新鲜上下文 smoke，不重跑历史大规模实验。

共享合同完成后运行一次现有全量测试；此前只运行与当前改动对应的定向测试。

## 12. 文档与仓库收口

能力实现并验证后再重写 README：

- 架构图把 Skill 与 Compact Prompt 都画成当前实线输出；
- Runtime 与未来标准只保留为一句兼容方向，不列成长篇未完成清单；
- README 增加当前版本、CI、License、双语入口等必要 badges；
- GitHub 补充 Description 与 Topics；
- GitHub Topics 与 Git 版本 Tag 分开处理，未经单独发布决定不创建 Git Tag 或 Release；
- dashboard 同步双 Adapter 的实现与验证事实。

## 13. 完成标准

本轮只有同时满足以下条件才可称为完成：

- 用户可从同一已批准 Definition 选择 Skill 或 Compact Prompt；
- 两条路径都经过真实 Adapter、Evidence 和只读 verify；
- Skill 路径通过当前 Codex 原生 Validator；
- Compact Prompt 不静默丢失 required 语义；
- Skill Creator / Skill Creator PRO finding 在 Adapter 变更或发布复核中通过修改 Adapter 并
  重建闭环，或有可审计的不适用理由；
- 旧 Codex Skill 命令保持兼容；
- README、dashboard、版本事实和 GitHub 元数据与代码一致。
