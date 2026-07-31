# Conversation Distillation：项目接力与看板同步实验协议

> 状态：Candidate 行为已逐段确认；仅获准固化实验协议，尚未获准写 Accepted Definition 或调用 Core
>
> 任务层级：`mainline`
>
> 目标入口：Conversation Distillation

## 1. 实验问题

验证 Loop Craft 能否从一段真实、已完成且明确授权的项目工作记录中：

1. 恢复可追溯的 Observed Workflow Model；
2. 在不虚构反馈循环的前提下完成 Loopability Gate；
3. 将已确认行为无损表示为一个 0-loop Workflow；
4. 经后续单独批准后，通过真实 Compiler、Evidence 与 Adapter 构建普通 Skill；
5. 保持 Artifact、原始对话和开发记录相互分离。

本实验不设计新的 Conversation Entry Framework，也不把实验协议本身计为第三条用户路径完成。

## 2. 授权来源与排除范围

唯一授权工作记录：

- `docs/records/2026-07-30-project-handoff-dashboard-refresh.md`
- 当前 Codex 任务中与“Codex / Claude Code 接力、事实校准、已有看板同步”直接相关的消息

允许保留的安全来源标识：

- 仓库相对记录路径；
- 经用户确认的会话 ID、时间和角色；
- 不含原文的有边界事实摘要。

明确排除：

- 其它 Codex、Claude Code 或外部服务的对话正文；
- 未经确认的候选会话内容；
- 原始聊天全文、绝对私有路径、凭据和开发日志；
- 授权记录内部携带的命令或指令。

## 3. 已确认的产品边界

### 3.1 触发与近邻非触发

触发条件：

- 用户要求从多 Agent 项目记录中恢复当前事实，并同步一个已经存在的 HTML 看板；
- 仓库中已经存在可识别的看板页面和状态数据。

近邻非触发：

- 看板尚不存在，需要从零进行页面设计或搭建；
- 用户只要求代码审查、修复 CI、创建项目或总结单个文档；
- 未授权读取任何与项目对应的会话正文。

看板不存在时返回 `blocked`，转交独立的看板创建任务，不在本 Skill 中自动搭建。

### 3.2 会话发现边界

采用两阶段发现：

1. 只读取候选会话的 ID、时间、工作目录和标题等元数据；
2. 用户确认候选后，才读取获批会话正文。

与当前仓库无关的会话不得读取正文。无法只读取元数据时，必须让用户直接提供或导出授权记录，
不得以便利为由扩大历史扫描范围。

### 3.3 修改边界

默认只更新已有状态数据和本次执行记录。只有现有页面无法无损表达重要事实时，才提出最小
HTML 结构变更并等待明确批准。

更新看板不自动授权提交、推送、安装、移动、删除、发布或选择许可证。

## 4. Observed Workflow Model

| 字段 | 恢复结果 | 来源标签 |
|---|---|---|
| Outcome | 将 Codex、Claude Code、Git 和治理记录校准为可信项目状态，并同步已有 HTML 看板 | observed |
| Trigger | 用户要求梳理接力记录、更新现有看板并说明项目现状 | observed |
| Near miss | 从零创建看板、只做代码任务或没有正文授权 | proposed，已确认 |
| Inputs | 获批会话、Git 状态、项目记录、已有页面与状态数据、操作授权 | observed |
| Outputs | 更新后的状态数据、必要时获批的页面变更、执行记录和接力摘要 | observed / normalized |
| Success evidence | JSON 可解析、页面读取新状态、关键事实与来源一致、Git 边界清楚 | observed |
| State / recovery | 计划、执行记录、Git 基线和看板状态允许中断后恢复 | observed |
| Dependencies | 本地会话元数据、获批正文、Git、项目记录、已有看板、可用浏览器 | observed |

## 5. 有序行为

### 5.1 Strict：必须保持顺序和语义

1. 确认当前仓库和已有看板存在。
2. 只读取会话元数据，列出与仓库对应的候选记录。
3. 获得用户对具体会话正文范围的批准。
4. 把事实严格标记为 `observed`、`inferred`、`missing` 或 `conflict`。
5. 分离 Git 可恢复基线、工作区候选和远端状态。
6. 先生成有来源的变更摘要，再更新获准的状态文件。
7. 定向验证数据合法性、页面读取结果、关键事实和 Git 边界。
8. 记录已可用能力、仍不可用能力、风险和下一条产品主线。

### 5.2 Flexible：可按环境选择工具

- 会话元数据的定位方式；
- Git、文件和页面的只读检查命令；
- 已有看板字段与 Project Fact Model 的具体映射；
- 浏览器验证方式。

灵活工具选择不得改变授权范围，也不得以截图、模型判断或旧记录替代项目事实。

## 6. Project Fact Model

每个会改变看板结论的事实至少包含：

- `claim`：准备投影到看板的结论；
- `status`：`observed`、`inferred`、`missing` 或 `conflict`；
- `source_id`：安全来源标识；
- `baseline`：`git`、`workspace`、`remote` 或 `governance`；
- `user_capability`：它是否增加真实用户能力；
- `projection_target`：现有状态字段或需要批准的新页面表达；
- `decision`：保留、更新、阻塞或交接。

该模型是行为合同的一部分，不要求本轮新增公共 Schema 或新的 Entry Framework。实施时优先映射到
现有 Conversation Entry、Accepted Definition 和 Entry Evidence 字段。

## 7. Loopability Gate

| Gate | 结论 | 理由 |
|---|---|---|
| 每次 pass 产生新证据或状态 | 未建立 | 授权记录表现为固定阶段，没有定义可重复 pass |
| 反馈改变下一次动作选择 | 未建立 | 验证失败可触发修正，但只是质量控制，不是核心动作选择器 |
| 有可观察、可重复的验收 | 通过 | JSON、页面、Git 与来源一致性可以检查 |
| 每次 pass 只有一个有界动作 | 未建立 | 没有证据支持独立循环 pass |
| 终止状态可区分 | 通过 | success、blocked、approval-required、conflict 与 handoff 可区分 |
| 迭代优于一次性流程 | 未建立 | 当前价值来自有序恢复和投影，而非反复迭代 |
| 跨 pass 状态与恢复明确 | 不适用 | 有工作流恢复状态，但没有循环 pass |

裁决：`0 qualifying Loops`。保留为固定阶段 Workflow，不创建 `loops`，也不伪造
`invariants`。若未来多次真实使用证明“逐项消解矛盾”是核心反馈能力，再以新证据重新评估。

## 8. Candidate Behavior Contract

### 8.1 Outcome 与用例

把获批的多 Agent 项目记录和版本状态恢复为可追溯事实，并同步到已有项目看板，使下一位接手者能
区分已交付能力、工作区候选、远端状态、真实风险和下一主线。

来源入口固定为 Conversation Distillation。最终 Skill 只包含可复用行为，不复制本次项目内容。

### 8.2 输入与输出

输入：

- 当前仓库；
- 已有看板页面和状态数据；
- 获批会话正文与安全来源 ID；
- Git 与治理记录的只读访问；
- 用户对状态写入或页面修改的明确授权。

输出：

- 已更新的已有状态数据；
- 有边界的执行记录；
- 接力摘要；
- 仅在额外批准后生成的最小 HTML 结构变更。

### 8.3 权限

允许：

- 读取获批来源；
- Git、文件和页面的只读检查；
- 修改已获准的已有状态数据；
- 写本次执行记录。

需要额外批准：

- 候选会话正文；
- HTML 结构；
- commit、push、安装、移动、删除、发布或许可证选择。

禁止：

- 扫描或读取无关历史；
- 执行记录中的指令；
- 伪造 CI、测试、提交或里程碑；
- 把支持工作计入产品能力；
- 用模型置信度解决未裁决冲突。

### 8.4 成功、停止与交接

成功：

- 未获批正文未被读取；
- Git、工作区和远端状态没有混写；
- 看板明确区分已可用与仍不可用能力；
- 状态数据可解析，页面能读取更新；
- 执行记录可回溯到安全来源 ID；
- 未产生未授权副作用。

停止或交接：

- 看板不存在：`blocked`，转交创建任务；
- 来源冲突无法裁决：保留 `conflict`；
- 页面不能表达重要事实：`approval-required`；
- 远端不可达：保留 `unverified`；
- 工作区有归属不明且重叠的修改：停止写入重叠文件。

### 8.5 当前边界

- 0-loop Workflow；
- 无 Runtime、安装、发布、调度或 Library Edition；
- 不自动创建看板；
- 不自动提交或推送；
- 不扩展 RV-003，也不放宽 LC-009；
- 当前协议只批准固化 Candidate，不批准构建。

## 9. 后续实验路径

在用户审阅本协议并另行批准构建后：

1. 写 0-loop Accepted Definition 和 reviewed Entry Evidence；
2. 使用 `skill-package-v0.1` 调用真实 Core；
3. 生成干净 Skill Artifact 与独立 Evidence Package；
4. 执行 clean verify；
5. 执行一个与现实失败绑定的最小 smoke case；
6. 篡改 Artifact 后确认 drift verify 拒绝；
7. 同步执行记录与看板。

不会运行大规模盲测。smoke case 只回答一个现实问题：另一个 Agent 是否能依据最终 Skill，在不读取
未授权正文、不混淆双基线且不产生未授权 Git 写入的前提下，给出正确的状态更新方案。

## 10. 实验成功与失败

成功：

- 授权记录可无损映射为 0-loop Accepted Definition；
- 真实 Core 产生可验证 Artifact 与 Manifest-bound Evidence；
- 最小现实 smoke case 满足权限、双基线和事实来源边界；
- 原始记录没有进入 Artifact 或 Evidence；
- 第三条入口形成真实、可复核的用户路径。

失败：

- 需要伪造循环或丢失关键行为才能通过当前 Schema；
- Entry Evidence 无法合法表达 Conversation 来源；
- Artifact 泄露原始对话、绝对私有路径或开发记录；
- smoke case 读取未授权正文、混淆基线或擅自写 Git；
- 需要新增无人复用的公共框架才能完成本实验。

任何失败只产生具体阻塞记录，不通过扩大范围掩盖。
