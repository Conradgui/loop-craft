# Existing Skill Demo 完成后的推进计划

> 状态：当前后续计划
>
> 事实基线：本地与远端 `main@1530688`；首次 GitHub Actions
> [run 30560334591](https://github.com/Conradgui/loop-craft/actions/runs/30560334591) 4 / 4 通过

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

- [x] 项目所有者明确决定推送本地 `main`。
- [x] 已推送 `main@1530688`，未夹带 LICENSE 或新的架构修改。
- [x] 首次 GitHub Actions 矩阵已完成并保存真实结果。
- [x] CI 通过：Ubuntu / Windows × Python 3.12 / 3.13 共 4 / 4 成功。
- [ ] CI 失败：只诊断并修复实际失败；不借机扩大测试或重构。

实际裁决：CI 通过。checkout@v4 与 setup-python@v5 的 Node 20 弃用提示不影响本次运行，
登记为非阻塞维护信号，不打断 Conversation Distillation 主线。

### 2. Conversation Distillation 真实 Demo

- [x] 已选择项目接力与已有看板同步记录作为唯一输入，并锁定两阶段会话授权边界。
- [x] 已恢复 Observed Workflow Model，逐段确认 0-loop Candidate 行为、权限和停止规则。
- [ ] 审阅精简实验协议，并另行批准 Accepted Definition 与本地构建。
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
