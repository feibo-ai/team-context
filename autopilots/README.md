# autopilots/

multica autopilot 的 YAML 模板 + agent 通用约束单源。

## 对象模型(TEA-93 · 2026-06-10 起)

**一个 team 身份 agent + 5 个瘦 autopilot**(2026-07-03 收敛:个人 scope 下线——
个人卡的信息 = 团队卡按人归并后的行,纯冗余;且个人机器 cron 时点离线 → run 被
admission gate 静默 skip 丢失。团队 agent 跑 DRI 常驻机 / cloud runtime):

- **agent = 身份载体**:`助理·全队` 一个,承载:
  - `instructions` ← 单源 [`_agent-instructions.md`](./_agent-instructions.md)
    (语言要求 / AUTOPILOT_SCOPE 语义 / notify_team-only / issue 纪律 / 执行纪律 ——
    改这一个文件 = 改所有 autopilot 任务的通用行为)
  - `custom_env`:`TCMCP_REMOTE_URL` + `TCMCP_AGENT_TOKEN`(PAT) + `AUTOPILOT_SCOPE`
    (team / 本人 email) + `AUTOPILOT_SCOPE_NAME`(显示名 · member list 的 name / team=全队)
- **autopilot = 调度载体**:每 kind 一个,description 只含该任务的
  差异 prompt(YAML 的 desc + prompt),`--agent` 指向本 scope 的身份助理;title=`<任务名>·<显示名>`(如 每日开工·全队)。
  cron/observability/guardrails 按任务独立保留。

实况分布:1 scope(team)× 5 kind = **5 个**。历史包袱(此前 6 scope × 5 kind = 30 个满编)
用 `scripts/decommission-personal-autopilots.sh` 下线(pause autopilot + archive 个人 agent,可逆)。
AUTOPILOT_SCOPE 机制保留(agent 级 env),当前部署恒为 `team`。

**重要 1**: `multica autopilot create` 不读取 YAML 文件 —— 它接收 CLI flags。
模板要经脚本解析成 `multica agent/autopilot` 调用(2026-05-28 spec + TEA-93):
- `scripts/team-autopilot.sh <kind|all> <provider>` —— 团队版(全队汇总 · DRI 跑)
- `scripts/my-autopilot.sh` —— DEPRECATED(2026-07-03 收敛 · 见脚本头注释)
- 两者共享 `scripts/_autopilot-common.sh`:ensure 身份 agent(幂等 by name · 同步
  instructions 漂移)→ ensure 各 kind 瘦 autopilot → 收尾 archive legacy `<kind>-bot-<suffix>`
- `scripts/apply-autopilots.sh` —— ⚠️ 仅历史参考 · 已不可用(读已删除的 agent.name 字段)

**重要 2** (v2 control plane edition · W5+): 这里 **不存任何 secret**,也 **不写 `FEISHU_*` env 变量**。所有飞书 secret 集中存活在 multica 的 `Secret` 对象(加密) · 所有 chat_id / wiki_space / team_members 等非 secret config 集中存活在 multica integration `team-context-mcp` 的 `config` 字段。

## 5 个 autopilot kind

| 文件 | Cron(Asia/Shanghai) | Mode | 用途 |
| --- | --- | --- | --- |
| `daily-kickoff.yaml`   | 工作日 09:00 | `run_only`     | 每日早晨开工:今日聚焦(进行中 / 待启动 / 待评审 / 卡住)→ 飞书群 (notify_team · 个人/全队 scope) |
| `daily-summary.yaml`   | 工作日 18:00 | `run_only`     | 每日 SOP 总结 → 飞书群 (notify_team · 个人/全队 scope) |
| `monday-kickoff.yaml`  | 周一 09:30   | `create_issue` | 周计划汇总 → 飞书群 + 创建 issue(个人版降为 run_only) |
| `wednesday-stats.yaml` | 周三 09:00   | `run_only`     | CLAUDE.md 周度统计 → 飞书群 |
| `monthly-health.yaml`  | 月 1 号 10:00 | `run_only`     | 运行 tc-ops monthly health 脚本 → 飞书 doc + wiki |

## 每个 YAML 必含的 PB-04 guardrails

三处 lint 同步守门(缺一拒建/CI 红):`scripts/_autopilot-common.sh` 的 `ac_lint_yaml`、
CI(`.github/workflows/lint.yml`)、`skills/tc-ops/autopilot_lint.py`。
CI 与 py lint 另查 `_agent-instructions.md` 存在且非空(单源被删/注空 = 全部通用约束消失)。

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

(TEA-93 起 `agent.name` 字段已删 —— 身份 agent 名由脚本派生为 `助理·<显示名>`,任务名映射见 `ac_kind_cn()`。)

`team-autopilot.sh` / `my-autopilot.sh` ensure 身份 agent 时:
1. 按 provider 选一个在线 runtime
2. 注入 custom_env 4 键(见上)· 注入 instructions(单源文件)
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
| 改所有任务的通用行为(语言/推送纪律/SCOPE 语义) | 改 `_agent-instructions.md` → 各成员重跑 `my-autopilot.sh all <provider>`(脚本检测漂移自动 `agent update --instructions`) |
| 改某类任务的差异 prompt | 改 `<kind>.yaml` → 重跑对应脚本(autopilot update --description) |
| 配 / 改 chat_id · wiki_space_id | `multica integration set team-context-mcp <key>=<value>` · WS 推送 hot-reload 到 tcmcp-remote · 无需重启 autopilot |
| 创 / rotate FEISHU_APP_SECRET 等 | `echo -n "<val>" \| multica secret set --integration team-context-mcp <KEY> --value-stdin` · tcmcp-remote 内 5-min cache TTL 后自动用新 secret |
| 加新 autopilot YAML | PR · 必含 `integration_ref` + 完整 `guardrails` 段 · CI lint 守门 |
| 看 autopilot 跑成功没 | `multica autopilot list` · 看 `last_run_at` · 或飞书群是否真收到 |
| 看终态对象 | `multica agent list \| grep 助理`(6 个)· `multica agent list --include-archived \| grep -- -bot-`(legacy 已归档) |
| 迁移前快照(回滚依据) | `docs/plans/snapshot_2026-06-10_autopilot-pre-migration.json` |
| 整体设计动机 | `decisions/2026-05-29-multica-control-plane.md` + plan TEA-93(docs/plans/plan_2026-06-10_autopilot-agent-consolidation_v2.html) |
| operator 用法详解 | `standards/integration-overview.md` |
| integration schema 字段 source of truth | `standards/integration-schemas/mcp-server-v1.yaml` |
