# team-context

AI MIQ 团队跨项目方法学的唯一权威来源。

**配套**: SOP v0.4 (`sop/group_sop_v0.4.html`) · 团队 Manifesto · Constitution · 决策记录。

> **v2 (W5+) · Multica control plane**: integration configs + secrets 集中存活在 multica。
> 本仓库 `autopilots/*.yaml` 通过 `integration_ref: team-context-mcp` 引用 (不再含 secret)，
> apply 时由 `scripts/team-autopilot.sh`（全队）/ `my-autopilot.sh`（个人）解析成 multica CLI 调用；运行时 tcmcp-remote 启动时拉 + WS 订阅 hot-reload。
> 见 [decisions/2026-05-29-multica-control-plane.md](decisions/2026-05-29-multica-control-plane.md) (rationale) ·
> [standards/integration-overview.md](standards/integration-overview.md) (operator 用法)。
> 团队成员**不再**需要本地装 feishu-cli。

## 装

### 第一次拿到这个仓库 (团队成员)

```bash
git clone https://github.com/<your-org>/team-context ~/team-context
cd ~/team-context

# 同步 skills + 全局规则到本地各 agent 界面 (Claude Code / Codex · 统一入口)
bash scripts/sync-team-config.sh
```

完事。重启 Claude Code · 试 "我想 /clear" · 应该弹 tc-handoff skill。

> feishu-cli 不再是团队成员入门前提 (W5+ 用 tcmcp-remote 集中处理飞书)。
> `scripts/install-feishu-cli.sh` 已 deprecated · 只 DRI 排查飞书 OpenAPI 时偶尔用。

### DRI / 管理员的额外步骤

```bash
# 在 multica workspace 建 11 个标准 label
bash scripts/create-labels.sh

# 同步 12 个 skill 到 multica workspace
bash scripts/sync-to-multica.sh https://github.com/<your-org>/team-context

# 一次性把飞书 secret 从 env-file 推到 multica · 替代旧的散户配置流程
bash scripts/multica-secrets-bootstrap.sh team-context-mcp

# 部署 5 个全队 autopilot (含 PB-04 guardrails 预检 + integration_ref 解析)
bash scripts/team-autopilot.sh all codex   # 个人版: bash scripts/my-autopilot.sh all codex
```

team-autopilot.sh / my-autopilot.sh **不再注入 secret 到 agent env** —— 只注入 `TCMCP_REMOTE_URL` + `TCMCP_AGENT_TOKEN`,agent 调远程 MCP 工具时由 tcmcp-remote 内部用 multica 拉到的 secret 完成飞书连接。(`apply-autopilots.sh` 已 deprecated。)详见 `autopilots/README.md`。

## 目录结构

```
team-context/
├── README.md                          ← 你在看
├── claude_md_team_global.md           ← 团队级 CLAUDE.md (≤ 3k token · 自动加载到所有 session)
│
├── sop/                               ← Team Context 三件套
│   ├── group_sop_v0.4.html            ← SOP 源 (reference Handbook)
│   ├── group_sop_v0.4.md              ← pandoc 渲染版 · 便于 diff / grep
│   ├── team_manifesto.md              ← 团队 WHY (给人)
│   └── team_context_constitution.md   ← Agent 规则书 (给 Agent)
│
├── skills/                            ← 12 个跨项目 SKILL.md
│   ├── tc-handoff/                     ← /clear 前 6 步检查
│   ├── tc-2-research/                  ← Research session 协议
│   ├── tc-3-plan/             ← Plan session · 4 必备字段
│   ├── tc-4-build/      ← Implement 纪律
│   ├── tc-5-review/              ← case file 5 section
│   ├── tc-health-check/    ← 浑浊 4 信号扫描
│   ├── tc-self-check/       ← 10 反 pattern + 3 红线
│   ├── tc-1-start/              ← Phase 01 6 步 wizard
│   ├── tc-monday/       ← 周一 30 分会引导
│   ├── tc-friday/          ← 周五 demo + betting 双议程
│   ├── tc-roles/      ← DRI/EXEC/COLLAB/REVIEW 认领
│   └── tc-conflict/         ← 冲突 4 原则 → decisions/
│
├── autopilots/                        ← 5 个 multica autopilot YAML
│   ├── README.md                      ← YAML 不被 multica 直接读 · 必经 team/my-autopilot.sh
│   ├── daily-kickoff.yaml             ← 工作日 09:00 → 飞书 (今日聚焦)
│   ├── daily-summary.yaml             ← 工作日 18:00 → 飞书 (今日回顾)
│   ├── monday-kickoff.yaml            ← 周一 09:30 → 飞书 + 建 issue
│   ├── wednesday-stats.yaml           ← 周三 09:00 → 飞书
│   └── monthly-health.yaml            ← 月 1 号 10:00 → 触发 monthly_health_report
│
├── standards/                         ← 跨项目判断标准 (无上限累积)
│   ├── labels.md                      ← 11 个 multica label 字典 (owner: DRI)
│   ├── integration-overview.md        ← v2 control plane operator 指南
│   ├── integration-schemas/           ← 3 个 integration schema YAML (mcp-server / feishu / autopilot-bot)
│   ├── skill-smoke-test-results.md    ← skill 加载/触发验证记录
│   ├── feishu-cli-smoke.md            ← v1 历史验证记录 (W5+ deprecated)
│   └── multica-sync-results.md        ← multica skill / integration 导入记录
│
├── decisions/                         ← 团队级架构决策 (ADR 格式 · YYYY-MM-DD-<slug>.md)
│   ├── 2026-05-26-v0.2-launch.md      ← 项目启动 6 项决策
│   └── 2026-05-29-multica-control-plane.md ← v2 控制面架构决策 (supersedes 部分 v0.2 launch)
│
├── health/                            ← 健康度归档 (autopilot + manual)
│   ├── monthly/                       ← 月度 health report 本地副本
│   └── burnout/                       ← 月度 burnout check 匿名聚合
│
├── scripts/                           ← 运维脚本
│   ├── sync-team-config.sh            ← skills + 全局 md → 各 agent 界面 + multica registry (统一入口)
│   ├── team-autopilot.sh              ← 全队 autopilot: YAML → multica CLI (PB-04 预检 + integration_ref)
│   ├── my-autopilot.sh                ← 个人 autopilot (同上 · 只本人 scope)
│   ├── _autopilot-common.sh           ← 上两者共享逻辑 (ac_lint_yaml 等)
│   ├── sync-to-local.sh · sync-to-multica.sh ← 分项 sync (统一入口见 sync-team-config.sh)
│   ├── apply-autopilots.sh            ← DEPRECATED · 被 team/my-autopilot.sh 取代
│   ├── create-labels.sh               ← 11 个标准 label 创建
│   ├── multica-secrets-bootstrap.sh   ← v2 · env-file → multica secret upsert (DRI 一次性)
│   └── install-feishu-cli.sh          ← DEPRECATED · 仅 DRI 排查保留 · 团队成员不需要
│
└── .github/workflows/
    └── lint.yml                       ← SKILL.md frontmatter + token + autopilot YAML schema
```

## Multica control plane integration (v2)

W5 起，本仓库不再持有飞书 secret · 不再生成 `.env`：

| 物件 | 存哪 | 谁管 |
|---|---|---|
| Integration `team-context-mcp` (kind: `mcp-server`) | multica workspace | DRI (web UI / CLI) |
| Config (chat_id · wiki_space_id · team_members · …) | multica integration `config` 字段 | DRI |
| Secrets (`FEISHU_APP_ID` · `FEISHU_APP_SECRET` · …) | multica `Secret` 对象 (加密) | DRI |
| Schema (config 形状的 source of truth) | `standards/integration-schemas/mcp-server-v1.json` (本仓库) | DRI PR review |
| Autopilot YAML (含 `integration_ref: team-context-mcp`) | 本仓库 `autopilots/*.yaml` | EXEC PR · DRI review |

**Hot-reload**：tcmcp-remote 启动时通过 ConfigSource 抽象拉一次 multica integration · 之后订阅 WS `integration.config-changed` 事件 · DRI 改 chat_id / team_members 不需要重启 server · 也不需要找 5 个人改 `.env`。

**Bootstrap**：第一次切到 v2 用 `scripts/multica-secrets-bootstrap.sh` 一次性把 env-file → multica secret。

操作细节 (创建 integration · rotate secret · 看 deployment 状态) 见 [standards/integration-overview.md](standards/integration-overview.md)。
设计动机 (W2-W3 暴露的 secret 漂移 / 离职吊销 / 配置漂移问题) 见 [decisions/2026-05-29-multica-control-plane.md](decisions/2026-05-29-multica-control-plane.md)。

## 三件套关系

```
manifesto (给人 · WHY)              ← 团队为什么这样工作
   ↓ 衍生
group_sop_v0.4.html (给人 · HOW)   ← 团队怎么协作工作
   ↓ 衍生
constitution (给 Agent · 优先级)    ← Claude/Codex 在 SOP 框架内的行为规则
   ↓ 加载
claude_md_team_global.md           ← L1 抽象层 · 每个 session 自动加载 · 硬上限 3k token
   ↓ 调用
12 个 skill (≤ 2k token each)     ← 触发式 · 按场景激活
```

## SOP 沉淀三层架构

```
L1 抽象 (本仓库)
  claude_md_team_global.md          ← 团队级 · 每 session 自动加载 · 硬上限 3k
  每个产品仓库 CLAUDE.md             ← 项目级 · 跟代码绑定 · 硬上限 3k

L2 具体 (本仓库 + 各项目仓库)
  各项目 cases/YYYY-MM-DD-<slug>.md ← 项目 debrief 产物 · 无上限累积

L3 中间 (本仓库)
  skills/  ← 被验证 prompt · ≤ 2k token each · Agent 自动触发
  standards/  ← 跨项目判断标准 · 人检索
  decisions/  ← 非平凡架构决策 · 历史追溯
```

## 月度维护 (DRI 责任)

每月 1 号 monthly-health autopilot 自动跑 → 飞书 doc。但<u>有些事工具替不了</u>：

- 11 个 label 仍然存在? 看 `multica label list`
- skills/* 谁 own / 90 天未 review? `monthly_health_report` 列出
- claude_md_team_global.md token 数过 2800? CI 失败 → 手动 prune

每季度（3/6/9/12 月）额外：
- CLAUDE.md prune 强制（过 3.5k 必须删）
- skills/ 没人调用的归档
- standards/labels.md vs multica workspace 实际 label 差异 diff

## 加新东西怎么走

| 加什么 | 怎么走 |
|---|---|
| 新 skill (跨项目) | PR · 含 SKILL.md + smoke test result + owner_email + last_reviewed_at frontmatter |
| 新 autopilot YAML | PR · 含完整 guardrails 段 (autopilot_lint 必须 pass) |
| 新 label | 改 `standards/labels.md` + 重跑 `create-labels.sh` · PR review |
| 新 standard | PR · 写 `standards/<topic>.md` · owner = 写的人 |
| 新 decision | 开 `decisions/YYYY-MM-DD-<topic>.md` · 不修改既有 decision |
| 新 script | PR · 含 `bash -n` 语法验证 |
| 调 CLAUDE.md (L1 提升) | <u>只能</u>通过 `case_promote_rule` MCP 工具 · 不能手改 |

## License

内部使用。仅 AI MIQ 团队使用。

## 关联文档

- 团队 SOP: `sop/group_sop_v0.4.html`
- v2 控制面 operator 指南: `standards/integration-overview.md`
- v2 控制面架构 ADR: `decisions/2026-05-29-multica-control-plane.md`
- Integration schema source of truth: `standards/integration-schemas/`
- 实施详情 (在 multica docs 仓库,不在本仓库):
  - Plan 1 (本仓库 W1): `docs/superpowers/plans/2026-05-26-plan-1-team-context-foundation.md`
  - Plan 2 (team-context-mcp 服务 W1): `docs/superpowers/plans/2026-05-26-plan-2-team-context-mcp.md`
  - Plan 3 (multica fork PR W1): `docs/superpowers/plans/2026-05-26-plan-3-multica-core-prs.md`
  - Plan 4 (tc-multica control plane W5): `docs/superpowers/plans/2026-05-29-plan-4-tc-multica-control-plane.md`
  - Plan 5 (tcmcp 远程重构 W5): `docs/superpowers/plans/2026-05-29-plan-5-tcmcp-remote-refactor.md`
  - Plan 6 (本仓库迁移 W5): `docs/superpowers/plans/2026-05-29-plan-6-team-context-integration-config.md`
- W1 项目决策: `decisions/2026-05-26-v0.2-launch.md`
- W5 控制面决策: `decisions/2026-05-29-multica-control-plane.md`
