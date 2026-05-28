# Multica skill 同步结果 — 2026-05-27

**Workspace**: `team-context` (slug: `team-context`, id: `766a0455-62d4-4454-b8b3-1794e2e92864`)
**Server**: `http://localhost:8080` (本地 Docker)
**导入的 skills**: 12 / 12

## 如何执行

plan 里原来的路径 —— `multica skill import --url https://github.com/feibo-ai/team-context` —— 在这个 repo 上跑不通，原因：

1. `multica skill import` 期望 URL 根目录下恰好有一个 `SKILL.md`，所以必须用「每个 skill 一个 URL」（不是「整个 repo 一个 URL」）。
2. 这个 repo 是**私有的**，multica server 的 GitHub fetcher 在 `raw.githubusercontent.com` 上拿到 HTTP 404。团队 SOP 和 skill 正文按设计就是私有的。

绕路方案：本地走 `multica skill create --name <n> --description <d> --content <body>`，对每个 `skills/<name>/SKILL.md` 单独执行。frontmatter 单独拆出来，正文通过 `--content` 传入。12 个全部成功。

## 已导入 skills

| Skill | Multica ID |
| --- | --- |
| anti-pattern-self-check | `757e089c-516d-4bc5-a1b6-f408edec853c` |
| conflict-adjudication | `c85b71c4-6f03-4977-9fcd-38acd447cf53` |
| context-pollution-detector | `681944d5-09f6-4b73-bcaf-b4e292e30b30` |
| debrief-template | `022135cb-4706-4fd7-9379-219edd9eb7a6` |
| friday-demo-protocol | `e8974254-9cf5-411e-9553-8da0d2a634cb` |
| monday-kickoff-protocol | `13dc900d-895f-49d1-af30-15027bc2a690` |
| phase-01-kickoff | `41bff02d-396c-4805-9c25-40452955f263` |
| pre-clear | `22df81c5-9337-4df2-9782-4c734d907632` |
| role-assignment-protocol | `bbe4e0e4-9f63-487f-84aa-5f12c0a18c1e` |
| rpi-implement-discipline | `293aa859-aee8-49e2-9294-0e336aa1ee2c` |
| rpi-plan-template | `a6797576-09a5-4c41-b2a8-bf01a4ed56a0` |
| rpi-research | `8cdfc6b3-8779-407a-8178-f3f02459227f` |

## Agent 挂载 (Step 4) — DEFERRED

plan 的 Step 4 假设已经有一个测试 agent 可以把这 12 个 skills 挂上去。当前本地 workspace 里有 **0 个 agent**：

```
$ multica agent list
ID  NAME  STATUS  RUNTIME  ARCHIVED
(empty)
```

等第一个 agent 创建出来后（通过 `multica agent create` 或 squad 导入），跑：

```bash
multica agent skills set --agent <agent-id> \
  --skill-ids "$(multica skill list --output id-only | tr '\n' ',' | sed 's/,$//')"
multica agent skills list --agent <agent-id>
```

## Autopilot 部署 (补于 2026-05-27 18:24)

修好 `apply-autopilots.sh`（见 commit `ecf9a36`）后，4 个 autopilot 全部 apply 成功：

| Autopilot | Mode | Cron (Asia/Shanghai) | 绑定的 agent |
| --- | --- | --- | --- |
| daily-summary | run_only | `0 18 * * 1-5` | daily-summary-bot |
| monday-kickoff | create_issue | `30 9 * * 1` | weekly-roundup-bot |
| wednesday-stats | run_only | `0 9 * * 3` | wednesday-stats-bot |
| monthly-health | run_only | `0 10 1 * *` | monthly-health-bot |

### Runtime：Codex（不是 Claude）

第一次尝试用的是 Claude runtime → 所有 run 全部以 `401 Invalid authentication credentials` 失败（这台机器上的 Claude CLI auth 过期或缺失）。通过 `multica agent update --runtime-id` 把 4 个 agent 全部切到 Codex runtime。切换之后，daily-summary 端到端在 2m38s 跑完，并向 Team Context 群发出 feishu 互动卡片 `om_x100b6e582d28b8acb16489122d931ee`。

### `multica agent env set`（不是 `multica agent update --custom-env`）

Plan 1 Task A13 Step 5 写的是 `multica agent update --custom-env "..."`。这个 flag 在 `agent update` 上不存在。真正的入口是专门的 `multica agent env set <agent-id> --custom-env "..."` 子命令（带 audit 的写操作）。每个 agent 都注入了 `FEISHU_TEAM_CHAT_ID` + `FEISHU_CONFIG_DIR`；通过 `multica agent env get` 确认 `has_custom_env=true, key_count=2`。

### 路径软链（按 workstation 一次性配置）

Autopilot 的 prompt 里引用了 `~/team-context` 和 `~/projects`。在这台机器上真实路径是 `/Users/feibo/feibo/team-context` 和 `/Users/feibo/feibo`。用 symlink 修一下，让 YAML 在不同 workstation 之间保持可移植：

```bash
ln -s /Users/feibo/feibo/team-context ~/team-context
ln -s /Users/feibo/feibo ~/projects
```

加完软链后，第三次触发跑出了一张完全中文、基于真实数据（TEA-1/TEA-2 issues + 近期 commits）的卡片，耗时 3m19s。feishu message ID `om_x100b6e58dd64f4acb22950d27bb44ec` 已投递到 Team Context 群。

其他 workstation 如果项目根目录不同：调整 symlink 目标即可 —— autopilot YAML 保持不变。

## 重新同步流程

如果本地的 `skills/*/SKILL.md` 有改动：

```bash
cd ~/team-context
git pull             # 从 feibo-ai/team-context 拉取
# 重新导入：本地 create 这条路只有先删才幂等。
# 单 skill 更新用：  multica skill update --name X --content <body>
```

plan 里的 `scripts/sync-to-multica.sh` wrapper 假设 GitHub URL 是公开的；对于当前这个私有 setup，先走上面的本地 create 路径，等 multica 支持带 auth 的 GitHub fetch 或本地路径导入再切。

---

## v2 control plane bootstrap · 2026-05-28

**Plan**: [2026-05-29-plan-6-team-context-integration-config](../../multica/docs/superpowers/plans/2026-05-29-plan-6-team-context-integration-config.md)
**Branch**: `feat/integration-config-migration` (4 commits: b4b5094, 8986ca0, 2251ee6, 4f99a7a)

### Bootstrap results

| 项 | 状态 | 数据 |
|---|---|---|
| Integration `team-context-mcp` | ✅ | id=`cc68a7cf-b1af-4acd-93d2-5a18b6a08cd6` · workspace=`team-context` |
| Secrets | ✅ | `FEISHU_APP_ID` + `FEISHU_APP_SECRET` (v=1) |
| autopilot-bot user | ✅ | id=`5061ced2-f2be-41a6-87fa-fd9979f0589b` · role=admin |
| autopilot-bot PAT (90d) | ✅ | name=`autopilot-bot-2026-q2` · 注入到 4 个 agent custom_env |
| Daemon runtime | ✅ | codex runtime `279b9cc2-d20e-4713-a86f-c6df7cd7faa8` |
| 4 个 autopilot 应用 | ✅ | daily-summary / monday-kickoff / wednesday-stats / monthly-health |
| 4 个 autopilot 对应 agent | ✅ | 全部接入 `TCMCP_REMOTE_URL` + `TCMCP_AGENT_TOKEN` env |
| tcmcp-remote `/health` | ✅ | `multica_reachable=true · feishu_ready=true · config_source=LayeredConfigSource` |
| codex `mcp add tcmcp-remote` | ✅ | http://localhost:8443/mcp · bearer-token-env-var=`TCMCP_AGENT_TOKEN` |

### End-to-end smoke (daily-summary autopilot)

- Run id: `e58dcb40-6404-46fd-9731-92a820021a38` · task id: `abe9b6dc-8870-4058-860b-1539a20230ee`
- Triggered: `15:20:08+08:00` · Completed: `15:25:26+08:00` (5min18s)
- Status: `completed` · failure_reason: `null`
- 路径验证:
  1. ✅ multica autopilot trigger → daemon picked task in 2s
  2. ✅ codex spawned with `TCMCP_AGENT_TOKEN` injected from agent.custom_env
  3. ✅ codex 收集数据 (47 个 git commit · 2 个 multica issue)
  4. ✅ codex 调用 MCP tool `notify_team` via tcmcp-remote HTTP /mcp
  5. ✅ tcmcp-remote 从 multica integration 解析 `feishu_team_chat_id`
  6. ✅ tcmcp-remote 通过 lark SDK 发卡 → feishu messageId `om_x100b6e4a941b3098b3bdb37c982c0ad`
- 已知 gap (operational · 不影响 code path):
  - `team_members` 字段未在 integration config 配置 → agent 用 workspace member 兜底 → `dm_member` 对 `test@multica.local` 返回 feishu 400 (非真实邮箱)
  - DRI 在生产前需补 `feishu_team_chat_id` 与 `team_members` 真实数据 (参见 `standards/integration-schemas/mcp-server-v1.yaml`)

### Hot-reload (TC-10 Step 6 · skipped)

工作空间无第二个测试 chat_id 可用 · 跳过 chat_id 翻转测试 · 待 DRI 在生产前补做。

**Status**: v2 control plane CODE 完整 · 操作配置补全后即可上线。
