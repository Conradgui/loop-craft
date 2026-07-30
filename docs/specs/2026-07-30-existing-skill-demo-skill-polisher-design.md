# Skill Polisher Existing Skill Upgrade 真实 Demo 设计

> 状态：已书面批准，进入隔离实施
> 日期：2026-07-30
> 任务层级：`mainline`
> 目标仓库：`Conradgui/skill-polisher`
> 固定版本：`63df4b508acbbbe4d351d30f1c7d0701c8fc75f7`
> Canonical Skill root：`skills/skill-polisher/`

## 1. 产品问题

Loop Craft 已完成 From-scratch 的一次真实用户 Demo，但 Existing Skill Upgrade 仍只有骨架与盲测证据。下一条主线需要证明：

> 用户可以把一个真实、已发布、具有行为历史的 Existing Skill 交给 Loop Craft；Loop Craft 能先做只读 Assessment，经用户审阅并批准一个有界改进后，生成完整、source-preserving、Evidence-bound 的升级 Skill。

本 Demo 只使用 Skill Polisher。Skill Creator Pro 不进入本轮输入、测试或比较范围，避免用第二个目标扩大 Token 和判断表面。

## 2. 目标与非目标

### 2.1 用户结果

升级后的 Skill Polisher 应明确提供一条完整路径：

```text
只读 Review
→ 稳定 Finding 与 Decision Brief
→ 用户选择一个 Finding 并授权修改
→ 最小 Polish
→ 使用同一 Finding 与证据标准 Recheck
→ RESOLVED 时停止，或在原范围内进行最多一次纠正
→ 交付结果与 Evidence
```

用户此前需要跨多次请求自行组织 Review、授权、Polish 和 Recheck。升级后，这些阶段形成一条有边界、可观察、不会静默扩大权限的路径。

### 2.2 非目标

本轮不做：

- 不优化 Skill Creator Pro；
- 不把整个 GitHub 仓库误当作 Skill root；
- 不修改 Skill Polisher 的远端仓库或已安装副本；
- 不发布、安装或覆盖原 Skill；
- 不增加新的 Skill identity；
- 不构建多个独立 Loop；
- 不处理 Runtime、Override、Subloop、Library Edition 或调度；
- 不预先修复 RV-003 direct-build Entry Evidence；
- 不为了覆盖 LC-009 而制造错误输入；
- 不运行 24/27 例盲测或双目标对比实验。

## 3. 输入边界

### 3.1 固定来源

来源固定为：

```text
repository: https://github.com/Conradgui/skill-polisher.git
revision: 63df4b508acbbbe4d351d30f1c7d0701c8fc75f7
skill_root: skills/skill-polisher/
```

目标 revision 在整个 Assessment、Candidate Review、inventory 和 build 期间不得漂移。若重新获取后 revision 或文件摘要变化，原批准失效。

### 3.2 渐进读取

默认只读取：

1. `skills/skill-polisher/SKILL.md`；
2. 它直接引用的 `references/polish-and-recheck.md`；
3. 它直接引用的 `references/release-drift.md`；
4. `agents/openai.yaml` 与 `license.txt`，仅用于运行时身份、调用和归属边界。

只有当某项额外仓库证据会改变 Finding、Preserve 项、修改范围或交付声明时，才继续读取仓库历史、测试或发布文档。不能因“资料存在”就全部装入上下文。

## 4. 行为架构

### 4.1 Review 是固定前置阶段，不属于重复循环

Review 保持只读，恢复并记录：

- outcome、触发分支与 near miss；
- 输入、状态、输出与副作用；
- authority、停止规则和成功证据；
- caller、adapter、release boundary；
- learned invariant 与 sediment；
- 当前证据的缺口和不可外推声明。

输出必须使用稳定 Finding ID，并形成：

- `Preserve`：本轮不得破坏的行为和机制；
- `Change`：证据支持的一个候选改进；
- `Evidence limits`：缺少哪些证据，因此不能声称什么。

如果证据不支持修改，Assessment-only 是正确执行结果，不得为了完成 Demo 强行制造 Finding 或构建产物。它不会把 Existing Skill Demo 标记为完成；本轮应如实停止并保留 `0 / 1`，而不是更换第二个目标来消耗额外 Token。

### 4.2 Review → Polish 必须经过显式授权闸口

Review 不自动进入编辑。进入 Polish 前，用户必须明确：

- 选择一个稳定 Finding ID；
- 接受其问题陈述和成功标准；
- 批准修改的 Skill、文件和副作用范围；
- 接受本地 Artifact + Evidence build；
- 保留哪些 invariant；
- 哪些情况必须重新询问。

对一个 Finding 的批准不能封定其它 Finding，也不能授权远端写入、安装、发布或新 identity。

### 4.3 Polish / Recheck 是唯一有界 Loop

每次迭代执行：

1. **Polish**：修复被授权 Finding 的最早因果缺口，只做最小必要修改；
2. **Recheck**：复用 Review 时的 Finding ID、原始问题和证据标准；
3. 检查原问题、受影响分支和一个最相关 near miss；
4. 根据结果决定停止、再修一次或重新请求批准。

允许的 Recheck 状态为：

```text
RESOLVED
PARTIAL
NOT_REPRODUCED
ACCEPTED_RISK
BLOCKED
```

`OPEN` 只表示尚未进入已授权修订，不能作为循环继续条件。

### 4.4 迭代上限

总预算为：

```text
最多 2 次 Polish
最多 2 次对应 Recheck
```

第一次 Recheck 为 `RESOLVED` 时立即停止，不消费第二次修改机会。

只有同时满足以下条件，`PARTIAL` 才能回到第二次 Polish：

- 仍是同一个 Finding；
- 原成功标准没有改变；
- 文件和副作用仍在原批准范围；
- 没有出现新的 learned invariant 或来源变化；
- 第二次修正仍是最小局部改动。

第二次 Recheck 后无条件停止并报告实际状态。不得自动进入第三轮。

### 4.5 必须停机并重新确认

出现以下任一情况时停止：

- 发现新的独立 Finding；
- 修改需要扩大文件、权限、副作用或目标范围；
- 目标 revision 或 source digest 改变；
- 需要删除或覆盖原 Skill；
- 需要远端写入、安装、发布或凭证；
- 需要多个独立 Loop；
- accepted-definition schema 无法无损表达目标行为；
- source-preserving overlay 会造成语义损失；
- 证据不足以区分缺陷与合理 trade-off；
- 两次修改机会已用完。

## 5. Loop Craft 端到端数据流

```text
Pinned Skill Polisher source
→ Existing Skill Assessment / Decision Record
→ Shared Loopability Gate
→ exactly one supporting bounded Loop
→ Shared Candidate Review
→ accepted-definition-v0.1
→ entry-evidence-v0.1
→ source package inventory + reviewed manifest
→ source-preserving build
→ clean Skill Artifact + independent Evidence Package
→ verify / drift rejection
```

预期 verdict 是一个 supporting bounded Loop；但这是待真实 Assessment 验证的假设，不是预设答案。若 Gate 判断为 zero Loop、multiple independent Loops 或 semantic loss，必须如实停在 Assessment/Candidate。

## 6. LC-009 与 RV-003 的处理策略

### 6.1 LC-009：真实失败才进入修复

当前公开运行时结构为：

```text
SKILL.md
license.txt
agents/
references/
```

这些 root 已在当前 Source Skill Adapter 支持范围。实施时先对固定 canonical Skill root 运行 inventory：

- inventory 通过：LC-009 不改、不测；
- 合法 canonical Skill root 真实失败：停止 Demo，记录失败文件和安全边界，再设计最小修复；
- 因误选仓库根目录失败：纠正 target resolution，不把调用错误登记为 LC-009。

若真实触发 LC-009，任何修复必须同时保留：

- source Skill 只读；
- manifest 写在源 Skill 之外；
- symlink/junction 无条件停机；
- 越出 root 的链接无条件停机；
- unresolved 或不可安全绑定内容停机；
- RV-001 与一条“可绑定源包 + 越界链接”的组合负例。

### 6.2 RV-003：本轮不处理

Existing Skill Upgrade 使用：

```text
entry_type: existing_skill
source_summary.kind: skill_assessment
```

它经过真实 Candidate Review，不依赖 direct-build Entry Evidence 取值。RV-003 不位于本 Demo 的执行路径，因此不作为前置任务。

## 7. 高效验证漏斗

### 7.1 原则

每项检查开始前必须回答：

1. 它捕获哪个现实失败？
2. 失败是否会改变实现、交付或发布判断？

不能回答时不执行。通过率、测试数和 Token 消耗都不是进度指标。

### 7.2 第 0 层：确定性源预检

不使用模型行为测试：

- 固定 repository revision；
- 确认 canonical Skill root；
- 检查文件类型、链接和路径边界；
- 执行 source inventory；
- 保存 source digest 和 reviewed manifest；
- 确认源目录在 inventory 前后字节不变。

失败会决定是否进入 LC-009，因此具有直接决策价值。

### 7.3 第 1 层：一次真实 Existing Skill Upgrade

只执行一个主路径：

- 一个真实目标；
- 一个 Assessment；
- 一个候选 Finding；
- 一次 Candidate Review；
- 最多两次 Polish/Recheck；
- 一个最终 build。

不运行第二个目标，不重复做相同 Assessment，不以独立 Agent 数量增加信心。

### 7.4 第 2 层：确定性产物验证

必须验证：

- 原 Skill 字节未被修改；
- Artifact 与 Evidence 分离；
- source package manifest 与 source digest 绑定；
- Entry Evidence 与 definition digest、entry type、classification 绑定；
- source-preserving overlay 保留未授权资源；
- `build` 成功；
- `verify` 返回 `clean`；
- 人为改动 Artifact 后，verify 返回 drift；
- 官方 Skill validator 通过；
- Artifact 不包含绝对本地路径、私有 source payload 或开发记录。

这些检查使用已有命令和摘要，不消耗额外行为测试 Token。

### 7.5 第 3 层：一个最小行为 smoke case

使用一个小型、安全、只有一个已知问题的本地 Fixture 调用升级后的 Skill Polisher。只验证：

- Review 保持只读；
- 未授权时不进入 Polish；
- 授权一个 Finding 后只修改对应范围；
- Recheck 复用原 Finding ID 和证据标准；
- 检查原问题、受影响分支和一个 near miss；
- 第一次解决时提前停止；
- 未解决时最多进入一次纠正；
- 新 Finding 或扩大范围时停机。

Fixture 用于验证升级后行为合同，不作为第二个优化目标。被测 Skill 只接收用户请求和 Fixture，不接收预期 Finding、疑似缺陷或 intended fix；这些只保存在测试判定侧，避免用答案泄漏换取通过。

### 7.6 Python 测试预算

- 未修改 Loop Craft Python/Schema：不运行 160 项全量测试；
- 只修改提示词/参考：做定向静态检查和上述真实路径；
- 若 LC-009 被真实触发并修改 Source Skill Adapter：只运行 inventory 正例、RV-001 负例和一条组合负例；
- 只有共享 Python 合同变化或定向失败无法定位时，才升级到相关 integration tests；
- 不因到达里程碑自动全量重跑。

## 8. 产物与证据

Demo 交付必须包含：

- Existing Skill Decision Record；
- 已批准 Candidate Review；
- accepted definition；
- reviewed Entry Evidence；
- reviewed source package manifest；
- 完整 source-preserving Skill Artifact；
- 独立 Evidence Package；
- build / verify / drift / validator 命令与结果；
- 原 source digest 与最终 Artifact digest；
- 一个 smoke case 的输入边界、实际行为和停止原因；
- 未执行检查及因此不能声称的内容。

原始 GitHub 仓库、完整源 Skill payload、绝对路径、私人标识和开发对话不得复制进 Artifact 或 Entry Evidence。

## 9. 成功标准

只有同时满足以下条件，才可把 Existing Skill Demo 标为真实完成：

1. 用户直接通过 Loop Craft 的 Existing Skill 入口发起任务；
2. 目标固定为 Skill Polisher canonical root 与指定 revision；
3. Assessment 没有预设 verdict，并能指出一个真实 supporting Loop 或如实停止；
4. Review 保持只读，用户明确选择一个 Finding 并批准 Candidate；
5. 最多两次 Polish/Recheck，状态与停机原因可观察；
6. 源 Skill 未被修改；
7. 生成完整、可发现、source-preserving 的 Skill，而非 Loop 片段；
8. Artifact 与 Evidence 独立；
9. Manifest、Entry Evidence、definition 与 Artifact digest 可核对；
10. verify clean、drift 负例和官方 validator 通过；
11. 最小 smoke case 证明授权闸口和迭代上限；
12. 看板仍诚实记录 RV-003、远端 CI、LICENSE 和其它未解决边界。

## 10. 阶段顺序

```text
规格复核
→ 实施计划
→ 固定并获取只读来源
→ inventory 预检
→ Existing Skill Assessment
→ Candidate Review
→ source-preserving build
→ 确定性验证
→ 一个 smoke case
→ 看板与执行记录
→ 再决定是否推送 Loop Craft 并观察远端 CI
→ 最后决定 LICENSE
```

任何前置阶段失败都不得通过扩大测试、放宽安全规则或伪造批准来绕过。

## 11. 已确认决策

- 第二条真实 Demo 使用 Existing Skill Upgrade；
- 只选 Skill Polisher，不运行 Skill Creator Pro；
- 完整路径包含 Review → 授权 → Polish/Recheck；
- Review 为固定只读前置阶段；
- Polish/Recheck 是唯一有界 Loop；
- 最多两次修改与两次定向复核；
- 使用高效验证漏斗，不做大规模盲测；
- LC-009 仅在 canonical Skill root 真实失败时处理；
- RV-003 不作为本 Demo 前置；
- 远端 CI 在本地 Demo 成功后再讨论；
- LICENSE 在发布边界阶段最后决定。
