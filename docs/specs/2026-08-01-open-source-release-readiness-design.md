# Loop Craft 0.4.0 正式开源发布设计

> 日期：2026-08-01
> 状态：已批准——用户在收到发布就绪度审计与四项建议后，明确要求完成迭代并提交 GitHub

## 1. 目标

把当前已经公开、产品链路通过的 Loop Craft 0.4.0 候选，收口为一个可被陌生用户安装、可被
外部贡献者参与、可被维护者稳定复现，并拥有正式版本入口的 GitHub 开源发布。

本轮成功不是“多几个社区文件”，而是同时满足：

1. `v0.4.0` 指向的源码 commit 本身通过 Ubuntu / Windows × Python 3.12 / 3.13 CI；
2. CI 使用的第三方 Action 与 Skill Creator PRO revision 都不可漂移；
3. 用户能从稳定版本链接安装 Skill，而不是被迫追踪可变的 `main`；
4. 漏洞、Bug、功能建议与 Pull Request 都有明确入口；
5. GitHub Release 提供发布说明、可安装压缩包和 SHA-256；
6. `main` 在发布后受保护，不能绕过 CI、强推或删除。

## 2. 方案选择

### A. 最小但完整的正式发布（采用）

补齐供应链固定、安全与协作文件、稳定安装链接、PR/CI 发布路径、Release 资产和分支保护。
它直接关闭本次审计发现的发布缺口，不引入文档站、遥测、包管理器或新的 Core 能力。

### B. 只补 GitHub 模板后立即打 Tag（拒绝）

成本最低，但外部 Validator 仍从可变默认分支拉取，Tag 也可能没有精确 CI 证据。它提高了
仓库外观，却没有解决可复现性这一更重要的工程风险。

### C. 一次建设完整社区平台（暂不采用）

同时增加 Docs Site、示例库、Discussions、覆盖率服务、Dependabot、路线图自动化和多渠道
支持。这会显著增加维护面，并且没有证据表明 0.4.0 首发需要这些能力。

## 3. 仓库内变更

### 3.1 可复现 CI

修改 `.github/workflows/validate.yml`：

- 声明最小 `contents: read` 权限；
- 增加 `workflow_dispatch`，允许对指定最终 commit 运行发布门；
- 将 `actions/checkout` 固定为 `v7.0.1` 对应 commit
  `3d3c42e5aac5ba805825da76410c181273ba90b1`；
- 将 `actions/setup-python` 固定为 `v7.0.0` 对应 commit
  `5fda3b95a4ea91299a34e894583c3862153e4b97`；
- 将 Skill Creator PRO checkout 固定到
  `eb23656e56ea3555599a6c5278a8b5834dc56b6d`；
- 保留现有四平台矩阵、Skill validator、真实 build/verify 与 drift negative case。

Action revision 来自各自 GitHub 官方仓库的 release tag；注释同时保留可读版本号和不可变 SHA。

### 3.2 安全与社区合同

新增：

- `SECURITY.md`：支持版本、私密漏洞报告入口、本地文件与权限边界、响应预期；
- `CODE_OF_CONDUCT.md`：简洁的社区行为与执行合同；敏感报告使用 GitHub 私密报告入口，
  不编造维护者邮箱；
- `.github/ISSUE_TEMPLATE/bug_report.yml`：要求版本、入口、Adapter、最小复现、预期/实际结果、
  Evidence 脱敏确认；
- `.github/ISSUE_TEMPLATE/feature_request.yml`：要求用户价值、当前替代方案、产品边界与证据；
- `.github/ISSUE_TEMPLATE/config.yml`：关闭空白 Issue，并将安全问题导向私密报告；
- `.github/pull_request_template.md`：用户能力、范围、验证、未运行项目和边界清单。

修改 `README.md`、`README.zh.md` 与 `CONTRIBUTING.md`，增加稳定版本安装、Security、Issues、
Pull Requests 和 Code of Conduct 入口。开发文档继续保留 `main` 路径；用户安装默认指向
`v0.4.0/loop-craft`。

### 3.3 项目事实

更新 `CHANGELOG.md`、`dashboard/status.json` 与发布执行记录，区分：

- 产品 0.4.0 已通过；
- 正式开源发布门正在执行；
- Release 与分支保护只有在远端动作实际成功后才写成完成。

## 4. GitHub 交付流程

1. 在 `codex/oss-release-readiness` 隔离分支实现并做静态检查；
2. 运行完整本地出口，推送分支并创建 ready-for-review PR；
3. 等待 PR 的四项矩阵通过后合并到 `main`；
4. 等待合并 commit 的 `main` CI 四项通过；
5. 从该已验证 commit 生成 `loop-craft-v0.4.0.zip` 与 `SHA256SUMS.txt`；
6. 创建 `v0.4.0` annotated Tag 和 GitHub Release，附两份资产；
7. 启用 GitHub Private Vulnerability Reporting，关闭空 Wiki；
8. 启用 `main` 保护：严格要求四个矩阵状态、禁止强推和删除，不要求维护者自己批准自己的 PR；
9. 分支保护启用后，从 `main` 创建只含看板与执行记录的 closure 分支，通过第二个 PR 写入
   Release URL、CI run 与保护结果；等待 closure PR 与合并后的 `main` CI 成功。

Tag 始终指向已通过 CI 的产品/发布 commit。最后的事实投影通过受保护分支正常合并，不移动
Tag，也不被描述为新的产品版本。

## 5. 错误与停止边界

- 任一 PR 或 `main` CI 失败：停止 Tag 与 Release，先修复并重新获得完整矩阵结果；
- Release 资产摘要与上传文件不一致：停止发布，重新从已验证 commit 构建；
- Tag 或 Release 已存在但目标不一致：不覆盖、不强推，停止并报告；
- GitHub 设置 API 权限不足：代码和 Release 可以保留，但不得声称分支保护或私密报告已启用；
- 不创建 PyPI 包，不把 `loopcraft-development` 宣称为用户安装包；
- 不修改 Core、Adapter、Schema 或 Skill 行为；Runtime、多 Loop、Override、Subloop 继续在范围外。

## 6. 验证

本地：YAML/JSON 解析、本地 Markdown 链接、官方 Skill validator、`compileall`、190 项测试和
同一 Definition 的真实 Skill/Prompt build + verify。

远端：PR 与合并 commit 的 GitHub Actions 四项矩阵。发布后回读 Tag target、Release assets、
SHA-256、Private Vulnerability Reporting、Wiki 状态、Community Profile 与 branch protection。

## 7. 不进入本轮

文档站、GitHub Pages、Discussions、Sponsor、PyPI、自动发布流水线、覆盖率 SaaS、Dependabot、
CODEOWNERS 强制审批、示例库扩张和新的产品能力均不进入本轮。它们可在真实社区使用信号出现后
单独决策。
