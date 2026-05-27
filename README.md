## 装

### 第一次拿到这个仓库

```bash
git clone https://github.com/<your-org>/team-context ~/team-context
cd ~/team-context

# 同步 12 个 skill 到本地 Claude Code
bash scripts/sync-to-local.sh

# 装 feishu-cli + smoke test (5 分钟)
bash scripts/install-feishu-cli.sh
```

完事。重启 Claude Code · 试 "我想 /clear" · 应该弹 pre-clear skill。

### DRI / 管理员的额外步骤

```bash
# 在 multica workspace 建 11 个标准 label
bash scripts/create-labels.sh

# 同步 12 个 skill 到 multica workspace
bash scripts/sync-to-multica.sh https://github.com/<your-org>/team-context

# 部署 4 个 autopilot (含 PB-04 guardrails 预检)
bash scripts/apply-autopilots.sh

# 给 4 个 autopilot agent 注入 FEISHU_TEAM_CHAT_ID env
# (详见 docs/superpowers/plans/2026-05-26-plan-1 · Task A13 Step 5)
```

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
│   ├── pre-clear/                     ← /clear 前 6 步检查
│   ├── rpi-research/                  ← Research session 协议
│   ├── rpi-plan-template/             ← Plan session · 4 必备字段
│   ├── rpi-implement-discipline/      ← Implement 纪律
│   ├── debrief-template/              ← case file 5 section
│   ├── context-pollution-detector/    ← 浑浊 4 信号扫描
│   ├── anti-pattern-self-check/       ← 10 反 pattern + 3 红线
│   ├── phase-01-kickoff/              ← Phase 01 6 步 wizard
│   ├── monday-kickoff-protocol/       ← 周一 30 分会引导
│   ├── friday-demo-protocol/          ← 周五 demo + betting 双议程
│   ├── role-assignment-protocol/      ← DRI/EXEC/COLLAB/REVIEW 认领
│   └── conflict-adjudication/         ← 冲突 4 原则 → decisions/
│
├── autopilots/                        ← 4 个 multica autopilot YAML
│   ├── README.md                      ← YAML 不被 multica 直接读 · 必经 apply-autopilots.sh
│   ├── daily-summary.yaml             ← 工作日 18:00 → 飞书
│   ├── monday-kickoff.yaml            ← 周一 09:30 → 飞书 + 建 issue
│   ├── wednesday-stats.yaml           ← 周三 09:00 → 飞书
│   └── monthly-health.yaml            ← 月 1 号 10:00 → 触发 monthly_health_report
│
├── standards/                         ← 跨项目判断标准 (无上限累积)
│   ├── labels.md                      ← 11 个 multica label 字典 (owner: DRI)
│   ├── skill-smoke-test-results.md    ← skill 加载/触发验证记录
│   ├── feishu-cli-smoke.md            ← feishu-cli 集成验证记录
│   └── multica-sync-results.md        ← multica skill 导入记录
│
├── decisions/                         ← 团队级架构决策 (ADR 格式 · YYYY-MM-DD-<slug>.md)
│   └── 2026-05-26-v0.2-launch.md      ← 项目启动 6 项决策
│
├── health/                            ← 健康度归档 (autopilot + manual)
│   ├── monthly/                       ← 月度 health report 本地副本
│   └── burnout/                       ← 月度 burnout check 匿名聚合
│
├── scripts/                           ← 运维脚本
│   ├── sync-to-local.sh               ← symlink skills/* 到 ~/.claude/skills/
│   ├── sync-to-multica.sh             ← multica skill import × 12
│   ├── apply-autopilots.sh            ← YAML → CLI flag 翻译器 + autopilot_lint 预检
│   ├── create-labels.sh               ← 11 个标准 label 创建
│   └── install-feishu-cli.sh          ← feishu-cli 一键安装 + 配置 + smoke
│
└── .github/workflows/
    └── lint.yml                       ← SKILL.md frontmatter + token + autopilot YAML schema
```

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

Internal. 仅 AI MIQ 团队使用。

## 关联文档

- 团队 SOP: `sop/group_sop_v0.4.html`
- Feishu 集成: `docs/integrations/feishu-cli.md` (在产品仓库 docs/ 下，不在 team-context)
- 实施详情:
  - Plan 1 (本仓库): `docs/superpowers/plans/2026-05-26-plan-1-team-context-foundation.md`
  - Plan 2 (team-context-mcp 服务): `docs/superpowers/plans/2026-05-26-plan-2-team-context-mcp.md`
  - Plan 3 (multica fork PR): `docs/superpowers/plans/2026-05-26-plan-3-multica-core-prs.md`
- 项目方案 HTML: `team_context_proposal.html`
- 项目决策: `decisions/2026-05-26-v0.2-launch.md`
