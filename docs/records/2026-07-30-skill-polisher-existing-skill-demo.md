# Skill Polisher Existing Skill Upgrade 真实 Demo 执行记录

> 状态：本地实验链路完成，等待结果提交
>
> 执行分支：`codex/skill-polisher-demo`
>
> 目标：`Conradgui/skill-polisher@63df4b508acbbbe4d351d30f1c7d0701c8fc75f7`

## 1. 产品结果口径

本记录只在以下链路全部形成证据后，才把 Existing Skill Demo 计为完成：

```text
真实 Existing Skill
→ 只读 Assessment
→ 已批准 Candidate
→ source-preserving build
→ clean / drift verify
→ 一个 Review → Polish → Recheck smoke case
```

Assessment、manifest 或 build 单独成功都不是用户 Demo 完成。生成产物位于被 Git 忽略的
`build/experiments/2026-07-30-skill-polisher-demo/`，本记录只保存受控摘要、摘要值和结果，
不复制原始 Skill payload。

## 2. 固定输入与只读边界

- 完整 revision：`63df4b508acbbbe4d351d30f1c7d0701c8fc75f7`
- canonical Skill root：`skills/skill-polisher/`
- root entries：`SKILL.md`、`license.txt`、`agents/`、`references/`
- regular files：5
- links / junctions：0
- 目标脚本执行：0
- 获取后 Git 状态：clean

文件 SHA-256：

| Path | SHA-256 |
|---|---|
| `SKILL.md` | `1d62909f2381f3a909d16e625a5c28065e06a8b33c027209adfe542e52ba6aca` |
| `agents/openai.yaml` | `4f973963515518d4078376eebbc69dade136c892b90ae411a8873231e6538acd` |
| `references/polish-and-recheck.md` | `a38810d41b89a7abaad61f4e6d6f3c589159b8619b49b5ce94ba2da1a6b47108` |
| `references/release-drift.md` | `2088ceedb7d6aa8e55b26cdfcd7eec479687522c2965c4f93ba66c10f40b71f7` |
| `license.txt` | `df34f959f25eea10c7751cc9345ed9cc6d8f3548d5c5159c9b16753ce6ef4817` |

## 3. Skill-to-Loop Decision Record

**Target:** `skill-polisher` canonical Skill root at pinned revision  
**Status:** Ready  
**Verdict:** `embedded_loop`

### Evidence

- 主 `SKILL.md` 把 Review 定义为只读默认，把 Polish 定义为经用户直接要求后的本地最小修改，把 Recheck 定义为对已改变 Artifact 的既有 Finding 复核。
- `references/polish-and-recheck.md` 已要求 Polish 保存 pre-edit baseline、最小修复、验证原回归与 near miss；Recheck 已要求复用 Finding ID 和原证据标准，并提供稳定状态词表。
- 现有文本没有规定 `PARTIAL` 如何在同一 Finding 内返回一次 Polish，也没有统一尝试预算、同一权限边界和第二次 Recheck 后的强制停机。
- Skill 的中央结果仍是“诊断并精炼 existing Skill”；反馈循环只支撑经批准的 Polish/Recheck 阶段，不替代 Review、release drift 或 rebuild handoff。

### Material finding

- **STL-001 — Polish 与 Recheck 具备组成反馈循环的部件，但返回边未实现。**  
  影响：用户批准一次最小修复后，Agent 可能把 `PARTIAL` 当成结束，也可能无界继续，或在新 Finding
  下沿用旧批准。最小改变是把同一 Finding、同一证据、最多两次修改/复核和扩大范围停机写成一个
  supporting bounded Loop；不重建 Skill，不改变 identity。

### Loopability Gate

1. **Fresh evidence：通过。** 每次 Recheck 对当前 Artifact 重现原 Finding，产生新状态与证据。
2. **Feedback changes action：通过。** `RESOLVED` 停止；`PARTIAL` 可能选择一次更早因果缺口；新 Finding 或越界则停止。
3. **Observable verifier：通过。** 原 Finding 的 claim、evidence 与 near miss 是复核标准，状态词表给出可观察判断。
4. **Bounded action：通过。** 每次只允许一个被批准 Finding 的最小本地修复。
5. **Distinct states：通过。** success、no-op、blocked、stagnated、exhausted 可由既有状态词表与新增停机映射区分。
6. **Iteration value：通过。** 第一次修复后 `PARTIAL` 的新证据可支持一次更精确修正；第三轮没有足够收益和授权。
7. **State / recovery：通过。** revision、Finding ID、原证据、baseline、diff、status 和 attempt count 可记录并用于恢复或交接。

独立循环计数为 1。Release drift 是条件式审计分支，不与本次被批准 Polish/Recheck 共享验收目标，
不压缩进此 Loop。

### Loop boundaries

- **Loop:** `polish-recheck`
- **Evidence status:** Inferred（部件已观察到，返回边由批准设计补齐）
- **Parent phase / entry:** Review 产出稳定 Finding，用户选择 `STL-001` 并批准本地修改后进入
- **Feedback source:** 同一 Finding 对当前本地 Artifact 的 Recheck 证据
- **Bounded action:** 修复最早因果缺口的一次最小本地修改
- **Verifier / acceptance:** 原 Finding、原证据标准和 affected near miss；`RESOLVED` 为成功
- **Terminal states:** success、clean no-op、blocked、stagnated、exhausted、approval-required handoff
- **State / recovery:** revision、Finding ID、baseline、diff、evidence、status、attempt count
- **Parent handoff:** 返回 Decision Brief 与实际状态；新 Finding、权限扩大或第二次失败交还用户

### Preserve

- Review read-only 默认；
- proportional evidence boundary；
- stable Finding IDs 和原证据标准；
- pre-edit baseline、最小修复、near-miss 检查；
- source / repository / published / installed 状态分离；
- Skill Creator Pro 对新 identity 或 full rebuild 的所有权；
- 原 metadata、references 与 MIT license 字节；
- 不修改源 Skill，不安装、不发布、不远端写入。

### Validation plan

1. canonical root inventory；
2. source-preserving build 与 clean verify；
3. validator；
4. tampered copy drift verify；
5. 一个隔离 Review → 授权一个 Finding → Polish → Recheck smoke case。

### Open decisions

无。用户已书面批准一个目标、一个 Finding、上述 Loop 边界、最多两次 Polish/Recheck 和本地
Artifact + Evidence build。`STL-001` 是对已批准问题的稳定编号，不扩大批准内容。

## 4. Candidate Review

**Classification:** 1-loop bounded Loop，作为 existing Skill 工作流中的 supporting Loop。  
**Ready state:** Ready。

1. **Outcome / use conditions**  
   只在 Review 已形成稳定证据、用户选择 `STL-001` 并批准本地修改时，把最小 Polish 与同一
   Finding Recheck 连接为有界返回边。来源边界是固定 revision 的 canonical Skill root 和用户已
   批准规格。
2. **Inputs / outputs**  
   输入是 existing Skill、稳定 Finding、原证据标准和本地 mutation boundary；输出是完整
   source-preserving Skill、same-Finding recheck record 和独立 Evidence。
3. **Authority**  
   允许读目标、只改生成副本中解决 `STL-001` 所需文件、运行批准的本地检查；扩大 Finding、
   目标、权限、成本或任何外部副作用需要新批准；禁止修改源 Skill、无关文件、identity、远端、
   安装、发布、调度或第三轮。
4. **Success / stop / handoff**  
   同一 Finding 在原证据下 `RESOLVED` 成功；`NOT_REPRODUCED` clean no-op；缺证据/权限、
   新 Finding、无进展或第二次不成功时停止并交接实际状态。
5. **Inferred / proposed facts**  
   `embedded_loop` 已由 Gate 决定；返回边、两轮预算和 attempt state 是已批准 proposal；
   definition 内部版本 `0.1.1` 仅表示本地最小行为升级，不宣称上游发布版本。
6. **Current boundary**  
   单 Loop、本地 Artifact + Evidence；无 Runtime、Library Edition、安装、发布、调度或远端写入。
7. **Approval scope**  
   仅写 accepted definition，并从不变 source 构建新的本地 Artifact 与 Evidence。

批准来源：`docs/specs/2026-07-30-existing-skill-demo-skill-polisher-design.md` 的书面批准，以及
用户对持续完成本地实验的明确授权。

## 5. 执行结果

### 5.1 Definition 与 Entry Evidence

- accepted definition Schema：通过
- definition digest：`sha256:190fc787f7573e222f75cac09f7d299ad597dbad7542d8141753b9d10a36b46c`
- Entry Evidence Schema、entry kind、classification、digest binding 与本地绝对路径检查：通过
- 内部版本：`0.1.1`，仅标识本地最小行为升级，不是上游 release claim

### 5.2 Source inventory

- inventory exit：`0`
- manifest schema：`source-skill-package-v0.1`
- source Skill digest：`sha256:56f2ae9ddcc08744bf5e8ba62dfb80f736e00ee2fc15100eff7136ec79e74b1f`
- entries：5；`SKILL.md` 为 `overlay`，其余 4 个文件为 `preserve`
- reviewed manifest 与重新 inventory：完全相等
- inventory 后 revision：仍为完整 pinned SHA
- inventory 后目标 Git 状态：clean

**LC-009 判定：本目标未触发。** canonical Skill root 可由现有 Adapter 直接 inventory，因此本实验不修改
`source_skill.py`，也不新增 LC-009 测试。P1-02 不能据此全局关闭：本证据只证明 Skill Polisher
这一真实包可达，不证明其它常见 root 已支持。

### 5.3 Build、verify、validator 与 smoke

Build：

- Artifact：`build/experiments/2026-07-30-skill-polisher-demo/output/artifact/skill-polisher/`
- Evidence：`build/experiments/2026-07-30-skill-polisher-demo/output/evidence/`
- build exit：`0`
- adapter compatibility：`native`
- Artifact digest：`sha256:a235cbb8fe4a6fb5cd51d73a34a9bd9bcac7ffd4ccb19b0e25c522ec207ced6b`
- definition digest：`sha256:190fc787f7573e222f75cac09f7d299ad597dbad7542d8141753b9d10a36b46c`
- Entry Evidence digest：`sha256:d0fcbc0521def0fb19e7f7f0b2df785a1e8aff183a780d0cfd9456408f53e352`
- source manifest digest：`sha256:d0c6b8d5592cf1fd830c78a0e41ad69e796009dee709d25d57aa9fe310f1a7c5`

Preservation：

- `agents/openai.yaml`、`license.txt` 和两个 source references 与原文件 SHA-256 完全相等；
- Artifact `SKILL.md` 的前 7,704 bytes 与 source `SKILL.md` 完全相等；
- 新增 4,179 bytes 仅为批准的 `## Feedback Loop`；
- Artifact 增加 `references/final-execution-ir.json`；
- Entry Evidence 只存在于 Evidence，不进入 Artifact；
- Artifact 与 Entry Evidence 对本地绝对路径、用户名、工作区名和实验路径的定向扫描为 0 命中。

验证：

- clean verify：退出 `0`，actual/expected 均为 Artifact digest，`status: clean`；
- official `quick_validate.py`：`Skill is valid!`；
- tampered copy：实际 digest `sha256:8f30d5d3…3d20`，预期 `sha256:a235cbb8…ed6b`，
  `status: drifted`，退出 `1`；
- drift verify 前后 tampered 文件 SHA-256 相等，证明 verify 没有写回；
- 篡改验证后主输出再次 verify 为 `clean`；
- 最终 source revision 仍为完整 pinned SHA，Git 状态 clean，重新 inventory 的 source digest 不变。

### 5.4 隔离行为 smoke case

输入边界：

- 被测执行器只得到生成后的 Skill Polisher、一个极小 fixture 和任务指令；
- Review 提示没有预期 Finding、疑似缺陷或 intended fix；
- fixture 初始 SHA-256：`1c190fb0bf74337c8c937389b311440bdd8f7978182be73dbe3b974a4dca67a1`；
- 规格、执行记录、source repo、Core output/evidence 与 baseline 明确排除；
- Review 使用只读沙箱，Polish 使用只对 fixture workdir 可写的沙箱。

实际行为：

1. 独立 Review 找到唯一 Finding `RNT-001`：Review 声明只读，但 Process 第 3 步要求先修改再报告。
2. Review 后 fixture SHA-256 与 baseline 相等，证明 Review 无写入。
3. 第一次 Polish 执行器因 `--ignore-user-config` 在 Windows Desktop 下实际降级为 read-only；
   生成 Skill 复用 `RNT-001`、报告 `BLOCKED` 并保持文件不变，没有越权。
4. 最小诊断证明移除该 CLI 选项后实际沙箱为 `workspace-write [workdir]`；不重复 Review，
   使用相同 Finding、原证据与授权边界重试。
5. 重试只修改 fixture `SKILL.md` 的 Process 第 3 步：Review 改为“识别并报告”，修改留给
   显式批准后的 Fix。
6. Recheck 继续使用 `RNT-001`，由 `OPEN` 变为 `RESOLVED`；有效 Polish `1` 次、Recheck
   `1` 次、`scope_expanded: false`、terminal `success`。

主控复核：

- baseline → fixture diff 只有上述两行替换；
- fixture 仍只有一个文件；
- copied Polisher、Review result、baseline 和原 source 均未改变；
- fixture 与 copied Polisher 均通过 official validator；
- 成功后主 Artifact 仍 `verify clean`。

Windows `apply_patch` 沙箱包装器在成功重试中拒绝了补丁工具；子进程在同一受限 workdir
使用一次精确正则块替换完成实际写入。该平台细节没有扩大修改范围，也不登记为 Loop Craft
产品风险。

CLI 显示的 smoke/诊断 token 使用量为：

- blind Review：30,842；
- read-only 正确停机：29,375；
- 最小沙箱诊断：22,836；
- 成功 Polish/Recheck：36,541；
- 合计：119,594。

这比预想成本高，主要来自一次执行器降级和一次诊断；本轮不再追加第二目标、第二 smoke 或
大套件。主会话开发 token 无精确账单，因此不伪造测试/开发精确比例。

## 6. 未执行检查与声明边界

未执行：

- 不执行目标仓库脚本；
- 不重复运行 160 项全量测试；本轮未修改 Core、Schema、Adapter 或测试，进入实验前基线已是
  `160 passed`；
- 不测试第二个真实目标或 Skill Creator Pro 行为；
- 不做大规模盲测、跨模型比较或 cross-platform smoke；
- 不安装生成 Skill，不比较 installed copy；
- 不发布、不推送、不运行远端 GitHub Actions；
- 不决定 Loop Craft LICENSE。

因此本记录只证明：

> 在本地 Windows/Codex 环境中，固定 revision 的 Skill Polisher 可由 Loop Craft Existing Skill
> 入口形成一个完整、source-preserving、Evidence-bound 的单 Loop 升级，并在一个隔离 smoke
> case 中遵守 Review 只读、单 Finding 授权、最小 Polish、同 Finding Recheck 与有界停机。

它不证明所有真实 Skill 包均可 inventory，不关闭 RV-003，不证明远端 CI、安装或发布状态。

## 7. 结论

Existing Skill Demo 本地实验链路通过。`STL-001` 的 `embedded_loop` 架构在真实目标上可由当前
Core 无语义丢失地构建；`RNT-001` smoke 以一次有效 Polish 和一次 Recheck 达到 `RESOLVED`。
LC-009 对本目标未触发，因此不修改 Adapter；P1-02 只缩小为“更广真实包形边界仍未闭合”。

阶段出口仍为 `DRIFT`：Conversation Distillation 尚无真实 Demo，RV-003、远端 CI 和 LICENSE
仍开放。
