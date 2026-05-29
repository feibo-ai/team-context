# autopilots/

multica autopilot 的 YAML 模板。

**重要 1**: `multica autopilot create` 不读取 YAML 文件 —— 它接收 CLI flags。
模板要经脚本解析成 `multica autopilot create + trigger-add` 调用(2026-05-28 spec · 个人/团队两版):
- `scripts/team-autopilot.sh <kind|all> <provider>` —— 团队版(全队汇总 · DRI 跑)
- `scripts/my-autopilot.sh <kind|all> <provider>` —— 个人版(只本人 · 成员跑)
- `scripts/apply-autopilots.sh` —— ⚠️ DEPRECATED · 被 team-autopilot.sh 取代

**重要 2** (v2 control plane edition · W5+): 这里 **不存任何 secret**,也 **不写 `FEISHU_*` env 变量**。所有飞书 secret 集中存活在 multica 的 `Secret` 对象(加密) · 所有 chat_id / wiki_space / team_members 等非 secret config 集中存活在 multica integration `team-context-mcp` 的 `config` 字段。

## 4 个 autopilot

| 文件 | Cron(Asia/Shanghai) | Mode | 用途 |
| --- | --- | --- | --- |
| `daily-summary.yaml`   | 工作日 18:00 | `run_only`     | 每日 SOP 总结 → 飞书群 (notify_team · 个人/全队 scope) |
| `monday-kickoff.yaml`  | 周一 09:30   | `create_issue` | 周计划汇总 → 飞书群 + 创建 issue |
| `wednesday-stats.yaml` | 周三 09:00   | `run_only`     | CLAUDE.md 周度统计 → 飞书群 |
| `monthly-health.yaml`  | 月 1 号 10:00 | `run_only`     | 触发 `monthly_health_report` → 飞书 doc + wiki |

## 每个 YAML 必含的 PB-04 guardrails

`scripts/_autopilot-common.sh` 的 `ac_lint_yaml`(被 team/my-autopilot.sh 调用)+ CI(`.github/workflows/lint.yml`)在建 autopilot 前 lint 这些字段 · 缺一拒建:

```yaml
guardrails:
  forbidden_commands:    # ≥ 5 条 · 必含 "git push" 跟 "npm publish"
    - "git push"
    - "git push --force"
    - "npm publish"
    - "rm -rf"
    - "psql.* drop"
  forbidden_paths:       # ≥ 1 条
    - ".env*"
    - ".ssh/*"
    - "secrets/*"
  max_budget_usd: 5      # ≤ 150 (SOP PB-04 大批量上限)
  max_runtime_minutes: 60
```

## 每个 YAML 必含的 `integration_ref`

```yaml
agent:
  integration_ref: team-context-mcp   # ← multica integration 名 (kind: mcp-server)
```

`team-autopilot.sh` / `my-autopilot.sh` 建 agent 时:
1. 按 provider 选一个在线 runtime
2. 给 agent 注入 custom_env: `TCMCP_REMOTE_URL` + `TCMCP_AGENT_TOKEN` (PAT) + `AUTOPILOT_SCOPE` (team / 本人 email)
3. **不**注入 `FEISHU_APP_SECRET` 等 secret —— 云端 tcmcp-remote 用 `MULTICA_SERVICE_TOKEN` server-side 自己拉
4. `integration_ref` 字段保留作文档 / CI(标明对应哪个 integration)· 飞书 config 由云端 tcmcp-remote server-side 解析

agent 在 prompt 里调远程 MCP 工具(`notify_team` / `archive_to_wiki` / `search_chat` 等)推飞书 · feishu 连接全在 tcmcp-remote 进程里完成。
(注:autopilot 一律用 `notify_team` 推群 · **不再用 `dm_member` P2P** —— 2026-05-28 spec §1.2。`dm_member` 工具本身仍在 tcmcp-remote 上,只是 autopilot 不调它。)

## EXEC workstation 装什么

**不装 feishu-cli** (W5 起 deprecated · `scripts/install-feishu-cli.sh` 顶部 banner 已说明)。
EXEC workstation 上跑 multica daemon 即可 · autopilot agent 由 daemon 调度 · agent 通过 MCP 客户端调用 tcmcp-remote。

## 操作清单

| 任务 | 命令 / 文档 |
|---|---|
| 配 / 改 chat_id · wiki_space_id（team_members 已 optional · autopilot 去 P2P 后不用) | `multica integration set team-context-mcp <key>=<value>` · WS 推送 hot-reload 到 tcmcp-remote · 无需重启 autopilot |
| 创 / rotate FEISHU_APP_SECRET 等 | `echo -n "<val>" \| multica secret set --integration team-context-mcp <KEY> --value-stdin` · tcmcp-remote 内 5-min cache TTL 后自动用新 secret |
| 加新 autopilot YAML | PR · 必含 `integration_ref` + 完整 `guardrails` 段 · CI lint 守门 |
| 看 autopilot 跑成功没 | `multica autopilot list` · 看 `last_run_at` · 或飞书群是否真收到 |
| 整体设计动机 | `decisions/2026-05-29-multica-control-plane.md` |
| operator 用法详解 | `standards/integration-overview.md` |
| integration schema 字段 source of truth | `standards/integration-schemas/mcp-server-v1.yaml` |
