# Loop Craft 0.3.0 产品接口贯通审计

> 日期：2026-07-31；被测对象：本机已安装且与仓库候选 24 个 tracked 文件 SHA-256 一致的 `loop-craft`；
> 结论：PASS；最终阶段仍等待远端 CI

## 目的与边界

本审计回答的不是“代码有没有测试”，而是：一个没有项目历史的 Agent，只拿到安装 Skill 时，
是否知道各模块怎样接、何时问用户、何时批准、何时停止，以及最终把什么交给谁。

使用一个 ephemeral Codex context，忽略用户配置与项目规则，以安装 Skill 为工作根并强制只读
sandbox。它被禁止读取开发仓库、测试、fixture、计划、看板和既往会话，也被禁止运行 Core、
构建真实项目或写任何用户文件。原始结构化输出保存在 ignored experiment 目录，不进入 Git。

## 结构校验

- 输出符合 `docs/testing/product-interface-audit.schema.json`；
- 恰好六条且 route id 唯一；
- 每条包含 input、owner、output、next consumer、approval/stop、boundary 与 user-facing next step；
- 审计前后安装副本 24 个 tracked 文件的 SHA-256 仍与仓库候选一致；
- subprocess 退出 0，用时 128.4 秒，单一 fresh Agent 使用 38,141 tokens；
- 没有真实用户项目执行，没有 Artifact/Definition 写入。

## 六条路线结果

| 路线 | 模块步数 | 中性请求终点 | 接口结果 | 关键边界 |
|---|---:|---|---|---|
| From-scratch | 5 | blocked：缺具体目标 | PASS | 一次一个问题 → Gate → Review → 批准后 Core |
| Existing Skill | 5 | blocked：缺目标 Skill 路径 | PASS | 完整只读 Assessment；Candidate 批准后 inventory；manifest 再批准后 build |
| Conversation | 5 | blocked：缺记录与授权范围 | PASS | 只读授权记录；Observed Model → Gate/Review；raw source 不进产物 |
| Direct Build | 4 | blocked：缺已批准 Definition | PASS | 不重跑 Gate/Review；v0.2 + null Review；只问真实缺口 |
| Verify | 2 | blocked：缺 build root | PASS | 输入错误不等于 drift；clean/drifted 都只读终止 |
| Multi-Loop refusal | 2 | unsupported | PASS | Gate 在构建前拒绝压缩两个独立 Loop；不写任何产物 |

`blocked` 在前五个中性请求里是正确结果：brief 刻意不提供真实目标、路径或 Definition，Agent
必须向用户请求真实输入而不能伪造。每条路线都给出了具体下一步，因此不是接口断链。

## 主 Agent 四项裁决

1. **接口完全接上：PASS。** 三个设计入口的 Candidate 均汇合到同一 Core 合法输入；Direct
   Build 的 v0.2 Evidence 独立表达未发生 Review；Verify 只消费完整 build root；unsupported
   不产生孤儿中间态。
2. **边界严谨：PASS。** 来源范围、权限推导、批准前零写入、Artifact/Evidence/raw source
   隔离、0/1 Loop、包形/link 与 clean/drifted 均有明确 owner 和停止条件。
3. **模块衔接流畅：PASS。** Agent 不让用户手写内部 JSON；已知答案不重复询问。Existing
   Skill 的 Candidate approval 与 inventory/build approval 是两个不同风险边界：前者批准行为，
   后者批准精确源字节与输出，因此不是重复确认。
4. **未知 Agent 可正常使用：PASS。** 仅依据安装 Skill，它能从自然语言路由到交付或正确停止，
   并在每个停点给出普通用户可执行的下一步。

## 结论限制

这是一项无副作用的产品逻辑审计，不替代真实项目执行、确定性测试或远端矩阵。真实 Demo 已由
三条保留链路提供，Core 已由 171 tests 与三份 clean verify 提供；本记录只补齐“陌生 Agent
能否理解和贯通接口”这一缺失证据。

产品接口门槛通过后，唯一剩余封板门是将候选 fast-forward 到 main、推送 GitHub，并等待该
commit 的 Ubuntu / Windows × Python 3.12 / 3.13 Actions 全部成功。
