# Skill Polisher Existing Skill Upgrade 真实 Demo 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Do not dispatch subagents. Keep generated target payloads under the ignored `build/` tree and persist only bounded evidence summaries in Git.

**Goal:** 让用户把固定 revision 的真实 Skill Polisher 交给 Loop Craft，完成一次只读 Existing Skill Assessment、一个已批准 Finding 的 source-preserving 单 Loop 升级、确定性验证和一个隔离行为 smoke case。

**Architecture:** 目标仓库只读固定到 `63df4b508acbbbe4d351d30f1c7d0701c8fc75f7`，canonical Skill root 为 `skills/skill-polisher/`。Loop Craft 先恢复完整行为合同并用 `STL-001` 标记“Review、Polish、Recheck 已存在但没有形成一个权限受控、复用同一 Finding 的有界返回边”这一已批准问题；通过兼容门后才生成 definition、Entry Evidence 和 source manifest。Core 将原 Skill 全量保留，只在新 Artifact 的 `SKILL.md` 追加一个 Feedback Loop，Evidence 与 Artifact 分离。

**Tech Stack:** Git 只读获取、Python 3.13、jsonschema、Loop Craft `build_loop.py`、Codex CLI 独立上下文（若本机可用）、PowerShell、JSON、Markdown。

**批准边界:** 用户已书面批准设计、单一目标、一个 Finding、最多两次 Polish/Recheck、本地依赖安装与持续本地执行。批准不包含修改目标远端、安装生成 Skill、发布、推送 Loop Craft 分支或决定许可证。

**测试预算:** 复用现有 160 项基线一次；实验阶段只运行真实 inventory、一次 build、clean/drift verify、官方 validator 和一个两段式 smoke case。除非 LC-009 真实触发且需要改代码，不新增或重跑全量测试。

---

## 产物布局

- Generated, ignored: `build/experiments/2026-07-30-skill-polisher-demo/source-repo/`
- Generated, ignored: `build/experiments/2026-07-30-skill-polisher-demo/inputs/`
- Generated, ignored: `build/experiments/2026-07-30-skill-polisher-demo/output/`
- Generated, ignored: `build/experiments/2026-07-30-skill-polisher-demo/smoke/`
- Create: `docs/records/2026-07-30-skill-polisher-existing-skill-demo.md`
- Modify: `dashboard/status.json`
- Modify only on real LC-009 failure: `loop-craft/scripts/loopcraft_core/adapters/source_skill.py`
- Add only on real LC-009 failure: targeted tests in `tests/integration/test_skill_packaging_adapter.py`

### Task 1: 固定来源并完成只读 Assessment

- [x] 获取 `Conradgui/skill-polisher` 到忽略目录，checkout detached 到完整 SHA；记录 `git rev-parse HEAD`。
- [x] 确认 canonical root 恰为 `skills/skill-polisher/`，列出根条目、链接/ junction 和文件摘要，不执行目标脚本。
- [x] 渐进读取 `SKILL.md`、`agents/openai.yaml`、两个直接链接的 references 和许可证；只有会改变 Finding/Preserve/边界时才读取更多。
- [x] 形成 Skill-to-Loop Decision Record：唯一候选 `STL-001`、预期 verdict `embedded_loop`、证据状态 `Inferred`；逐项应用七项 Loopability Gate。
- [x] 若出现多 Loop、语义损失、身份不一致或 unsupported root，诚实停在 Assessment；不得为了产物放宽安全规则。

Expected: revision、canonical root、合同和 Decision Record 都能从目标字节追溯；目标目录未被修改。

### Task 2: 锁定已批准 Candidate 并生成三个受审输入

- [x] 将已批准设计映射为 1-loop Candidate Review：Review 只读；用户选择 `STL-001` 后允许最小本地 Polish；Recheck 使用同一 Finding 与证据；最多两次 Polish/两次 Recheck；新 Finding、扩大权限或第三轮必须停机。
- [x] 在 `inputs/accepted-definition.json` 写 `skill-package-v0.1` 定义，identity id 必须为 `skill-polisher`。
- [x] 用 Core canonical digest 生成 `inputs/entry-evidence.json`：`entry_type: existing_skill`、`kind: skill_assessment`、安全 source IDs、无绝对路径或原始 Skill payload。
- [x] 从 `loop-craft/` 运行正式 inventory：

```powershell
python scripts/build_loop.py inventory `
  ..\build\experiments\2026-07-30-skill-polisher-demo\source-repo\skills\skill-polisher `
  ..\build\experiments\2026-07-30-skill-polisher-demo\inputs\source-package-manifest.json
```

- [x] 审阅 manifest 的 sorted paths、actions、file digests 与 source digest，并重新核对 pinned revision。

Expected: inventory 退出 `0`。若 canonical root 真实因允许范围内的常见条目失败，才进入 Task 3；若因选错根目录失败，只修正调用。

### Task 3（条件式）: 仅在真实失败时最小修复 LC-009

**结果：未触发。** canonical Skill root 的 5 个标准文件 inventory 成功；不修改 Adapter，不新增测试。

- [x] 写一个只复现该真实 root 条目的失败测试，并绑定现有链接越界负例。（不适用：未发生真实失败）
- [x] 运行定向 RED：（不适用：未发生真实失败）

```powershell
$env:PYTHONUTF8='1'
python -m pytest tests/integration/test_skill_packaging_adapter.py -q
```

- [x] 只扩展被真实证明必要的标准 root；链接/junction 仍无条件拒绝，未知 root 仍 fail closed。（不适用）
- [x] 运行同一文件定向 GREEN；不运行全量套件。（不适用）
- [x] 回到 Task 2，重新创建新 manifest 路径。（不适用）

Expected: 若 inventory 本来通过，本 Task 标记“不触发”，不修改 Core 或测试。

### Task 4: 真实 source-preserving build 与确定性验证

- [x] 从 `loop-craft/` 构建到全新输出目录：

```powershell
python scripts/build_loop.py build `
  ..\build\experiments\2026-07-30-skill-polisher-demo\inputs\accepted-definition.json `
  ..\build\experiments\2026-07-30-skill-polisher-demo\output `
  --source-skill ..\build\experiments\2026-07-30-skill-polisher-demo\source-repo\skills\skill-polisher `
  --package-manifest ..\build\experiments\2026-07-30-skill-polisher-demo\inputs\source-package-manifest.json `
  --entry-evidence ..\build\experiments\2026-07-30-skill-polisher-demo\inputs\entry-evidence.json
```

- [x] 检查 Artifact 含完整原 Skill、追加 `## Feedback Loop`，Evidence 独立且包含 definition、source manifest、Entry Evidence 和 bindings。
- [x] 运行 clean verify，预期退出 `0` 且 `status: clean`。
- [x] 查找现有官方 Skill validator；仅在缺失时把 Skill Creator Pro 工具依赖获取到 ignored build 目录。以 `PYTHONUTF8=1` 对 Artifact 运行 validator。
- [x] 复制 build 到独立 tampered 目录，只修改 tampered Artifact 一字节，运行 drift verify，预期退出 `1` 且不写回。
- [x] 比较 source revision/digest，证明目标源未变。

### Task 5: 一个隔离行为 smoke case

- [x] 在 ignored `smoke/fixture/` 创建一个极小本地 Skill，包含一个已知但不向被测模型泄漏的 Review/修改权限矛盾。
- [x] 确认 `codex exec` 可在新上下文运行；只把生成 Artifact、fixture 路径和 Review-only 请求交给它，禁止编辑，保存 Decision Brief。
- [x] 从输出选择一个真实 Finding ID，再启动第二个干净上下文，明确授权仅该 Finding 的本地修改，并要求 Polish → Recheck；不提供预期缺陷或 intended fix。
- [x] 检查：Review 无写入；修改仅在授权 fixture；Recheck 复用 Finding 和证据；最多两轮；无远端、安装、发布或其它副作用。
- [x] 若 Codex CLI 不可用或认证失败，记录为明确的行为验证 blocker；确定性 build 不能冒充 smoke 通过。（不适用：CLI 可用；一次 read-only 降级被正确停机，修正执行器后成功）

Expected: 同一个 smoke case 完成 Review 与一次授权后的 Polish/Recheck，或诚实记录外部执行器 blocker。

### Task 6: 证据记录、看板与本地提交

- [x] 创建执行记录，包含 revision、source digest、Decision Record、Candidate Review 摘要、definition digest、manifest 摘要、build/verify/validator/drift/smoke 结果、目标源无修改证明和未解决风险。
- [x] 更新 `dashboard/status.json`：
  - 若全链路通过：Existing Skill Demo `1 / 1`，其余入口 `1 / 2`，里程碑进度校准为 80；
  - 若停在 Assessment 或 smoke blocker：保持 `0 / 1`，写明准确停机点；
  - LC-009 只按真实 inventory 结果更新，RV-003、远端 CI、LICENSE 继续保留。
- [x] 最小静态检查：

```powershell
Get-Content -Raw dashboard/status.json | ConvertFrom-Json -Depth 100 | Out-Null
git diff --check
git status --short
```

- [x] 按 `superpowers:verification-before-completion` 复核所有成功声明。
- [x] 仅提交 `codex/skill-polisher-demo` 本地分支，不推送；ignored build 产物留在工作树内供检查。

Expected: 本地提交可追溯，工作树干净；远端和许可证状态不被误报。
