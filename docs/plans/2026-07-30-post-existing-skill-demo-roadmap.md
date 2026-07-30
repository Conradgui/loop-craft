# Existing Skill Demo 完成后的推进计划

> 状态：当前后续计划
>
> 事实基线：本地 `main@3a5fe1e`；远端 `origin/main@255438f`

## 目标

在不回到基础设施优先的前提下，把已经完成的 Existing Skill 真实证据同步到远端验证，再完成
Conversation Distillation 真实用户路径，最后处理发布许可证。

## 已确认结论

- [x] From-scratch 与 Existing Skill 两条真实入口已走通。
- [x] Skill Polisher canonical root 可由现有 Adapter inventory；本目标未触发 LC-009。
- [x] RV-003 direct-build provenance 不在 Existing Skill Demo 路径。
- [x] Demo 规格、计划、执行记录和看板已 fast-forward 并入本地 main。
- [x] 实验 worktree 暂时保留，以保存 ignored Artifact、Evidence 与 smoke 原始结果。

## 后续顺序

### 1. 推送决策与远端 CI

- [ ] 项目所有者明确决定是否推送本地 `main`。
- [ ] 若获授权，推送当前 main，不夹带 LICENSE 或新的架构修改。
- [ ] 观察首次 GitHub Actions 矩阵并保存真实结果。
- [ ] CI 通过：只更新远端验证证据。
- [ ] CI 失败：只诊断并修复实际失败；不借机扩大测试或重构。

停止条件：没有推送授权时停在本地，不把工作流文件存在表述为远端 CI 已通过。

### 2. Conversation Distillation 真实 Demo

- [ ] 选择一段已授权、已完成的真实工作记录作为唯一输入。
- [ ] 复用现有 Workflow Model、Loopability Gate、Candidate Review、Compiler、Evidence 和 Adapter。
- [ ] 只构建一个可无损表示的 0-loop Workflow 或 1-loop Skill；多 Loop 如实停在 Assessment。
- [ ] 完成一个最小现实 smoke case，并同步执行记录与看板。

产品出口：三入口都至少有一条真实、可复核的用户路径。

### 3. 条件式问题，不做前置建设

- [ ] RV-003：只有 direct-build 被接受为真实用户路径时，才设计不伪造 Candidate Review 的
  Entry Evidence。
- [ ] LC-009：只有新的真实 canonical Skill root 因包形失败时，才在保留 RV-001
  link/junction fail-closed 的前提下修复。

这两项继续保留在问题台账，但不阻塞 Conversation Distillation，也不为了关闭编号而制造输入。

### 4. LICENSE 最后决定

- [ ] 远端 CI 状态与上游归属边界明确后，再比较许可证选项。
- [ ] 由项目所有者做最终选择；同步 `LICENSE`、README、NOTICE 与发布声明。

## 当前明确不做

- 不自动推送、发布、安装或创建 PR；
- 不删除实验 worktree；
- 不重新运行大规模盲测；
- 不预先实现 RV-003 或放宽 LC-009；
- 不进入 Runtime、Override、Subloop、Library Edition 或多 Loop。
