# AI MIQ Team-Context · DRI 运维手册 v1.0

> **Audience:** Team DRI (workspace owner) · 唯一权限管理者
> **配套:** [`ONBOARDING-MEMBER.md`](./ONBOARDING-MEMBER.md) (你自己也走这个流程 · 你也是团队成员) ·
> [`ONBOARDING-NEW-HIRE.md`](./ONBOARDING-NEW-HIRE.md) (你 onboard 新人时给他)

## 你管的资产

| 资产 | 在哪 | UUID/标识 |
|---|---|---|
| Zeabur 项目 | server `AI-Gateway` (Aliyun SG · `server-69ad9804ea9fa7a75475eb45` · IP `43.106.62.232`) | `teamctx` |
| Zeabur services × 4 | 同上 | `postgresql / multica-backend / multica-web / tcmcp-remote-gres` |
| Multica workspace | `https://teamctx.actionow.ai` | `team-context` (UUID `b18d7b35-...`) |
| 3 个 cloud 域名 | DNS @ Cloudflare actionow.ai 区 | `teamctx.actionow.ai` · `api.teamctx.actionow.ai` · `mcp.teamctx.actionow.ai` (全部 gray cloud) |
| 飞书 integration | multica workspace `team-context-mcp` (UUID `ef5f21b9-...`) | 2 secret + chat_id config |
| Multica daemon | 你 mac (本地 · `multica daemon status` pid) | runtime IDs: Claude/Codex/Hermes |
| 4 个 autopilot | multica workspace | `daily-summary / monday-kickoff / wednesday-stats / monthly-health` |

记下来 / 收藏。出事时这张表是 ground truth。

---

## 0 · 前置 (DRI 自己机器 · 一次性)

```bash
brew tap multica-ai/tap && brew install multica
brew install jq node@22 zeabur

multica config set server_url https://api.teamctx.actionow.ai
multica config set app_url    https://teamctx.actionow.ai
multica config set workspace_id b18d7b35-344a-4663-9ddc-00a71de89399
multica login                    # 浏览器登 · 输 actionow.ai@gmail.com + 验证码

zeabur auth login                # 浏览器登 actionow Zeabur 账号

# 路径标准: autopilot YAML 与成员文档统一用 ~/team-context。
# DRI 仓库若 clone 在别处 (如 ~/feibo/team-context),建 symlink 让路径解析一致 (一次性):
[ -e ~/team-context ] || ln -s ~/feibo/team-context ~/team-context
```

**验证:**
```bash
multica auth status              # 期望: Server/User/Token 三行 OK
zeabur project list              # 期望: 包含 teamctx
multica autopilot list           # 期望: 4 个 active
```

---

## 1 · Onboard 新团队成员 (最常用 · 30 秒)

每次有新人加入,你做 3 件事:

### 1a · 在 multica 建 user + 发 PAT

```bash
EMAIL="newbie@actionow.ai"
NAME="Newbie Display Name"

# 建 user (默认 role=member · admin 操作)
multica user create --email "$EMAIL" --name "$NAME" --role member 2>&1 | head -5

# 给他/她 issue 个 PAT (实测命令)
PAT=$(multica auth issue-token \
  --user-email "$EMAIL" \
  --name "${EMAIL%@*}-onboarding" \
  --output token | tail -1)
echo "PAT len=${#PAT} · prefix=${PAT:0:14}..."
echo "$PAT"   # 复制给本人 · 不要留在你 shell history
```

**验证 1a:**
```bash
# 用刚发的 PAT 试 /api/me
curl -s -H "Authorization: Bearer $PAT" https://api.teamctx.actionow.ai/api/me | jq .email
# 期望: "newbie@actionow.ai"
```

### 1b · GitHub 加他到 org

```bash
gh api -X PUT "/orgs/feibo-ai/memberships/<their-github-username>" \
  -f role=member 2>&1 | head -5
```
他/她会收到 GitHub 邀请邮件。`team-context-mcp` 已 public 不需要 explicit access; `team-context` 是 private,**团队成员通过 org membership 有 read 权限** —— skill 本身走 multica API 不依赖它,但建个人 autopilot(`scripts/my-autopilot.sh`)需要 clone 本仓库。

### 1c · 飞书 + 文档发给他

飞书 DM 给他 4 条信息 + 1 个文档链接:
- email: `<EMAIL>`
- PAT: `<PAT>`
- workspace_id: `b18d7b35-344a-4663-9ddc-00a71de89399`
- 飞书群:已邀请你进「Team Context」群
- 文档: [`ONBOARDING-MEMBER.md`](./ONBOARDING-MEMBER.md) (普通团队成员) 或 [`ONBOARDING-NEW-HIRE.md`](./ONBOARDING-NEW-HIRE.md) (一周入职计划)

`ONBOARDING-MEMBER.md` 是技术接入 30 min 跑完 · 文档第一页就告诉他要"DRI 给你 4 样东西" · 你刚刚给的 4 样跟它一对。

---

## 2 · 日常 ops

### 2a · 看 autopilot 跑得怎么样

```bash
multica autopilot list                                  # 4 个状态
multica autopilot runs 4d4d1120 2>&1 | head -5          # monday-kickoff 历史 (替换 ID)
```

**预期 STATUS:**
- `completed` = 跑成功
- `issue_created` = 已建 issue 但 agent 任务还没完 (5-10min 内变 completed)
- `failed` = 看 issue body 找原因 (常见:agent 没 MCP 工具 · 见 §6 排查)

### 2b · 手动触发 autopilot (测 / 重跑)

```bash
multica autopilot trigger 4d4d1120                      # monday-kickoff (替换 ID)
sleep 90
tail -30 ~/.multica/daemon.log | grep -E "task=|agent finished"
```

期望:`daemon.log` 末尾出现 `agent finished … status=completed duration=Xs tools=N`。

### 2c · 检查 cloud 健康

```bash
# multica backend
curl -s https://api.teamctx.actionow.ai/healthz | jq
#   期望: {"status":"ok","checks":{"db":"ok","migrations":"ok"}}

# tcmcp-remote
curl -s https://mcp.teamctx.actionow.ai/health | jq '{status, multica_reachable, feishu_ready, config_version}'
#   期望: status:healthy · multica_reachable:true · feishu_ready:true

# multica web (HTML 落地页)
curl -sI https://teamctx.actionow.ai/ | head -1
#   期望: HTTP/2 200
```

### 2d · 查/改 integration 配置 (chat_id / wiki / team_members)

```bash
multica integration get team-context-mcp 2>&1 | head -15

# 改飞书全体群 (例:换群)
multica integration set team-context-mcp \
  feishu_team_chat_id=oc_NEW_xxx

# 加 wiki space (archive_to_wiki 工具)
multica integration set team-context-mcp \
  feishu_wiki_space_id=wkt_xxx

# (可选) team_members —— autopilot 已全去 P2P (notify_team only · spec §1.2),daily-summary 不再按人私信。
# 仅当你手动调 dm_member / read_member_dm 时才需要这份 roster;否则可不配。
multica integration set team-context-mcp \
  team_members='[{"email":"alice@actionow.ai","feishu_id":"ou_xxx","role":"member"},{...}]'
```

改完后 tcmcp-remote 走 WS push hot-reload · **不需要重启 zeabur 服务** (用 `curl https://mcp.teamctx.actionow.ai/health | jq .config_version` 应该升 1)。

### 2e · 飞书 secret rotation

```bash
# 旧的 (查) - 列出 key 名,不打印值
multica secret list --integration team-context-mcp

# 推新 secret (例:rotate APP_SECRET)
echo -n "new_secret_value_here" | multica secret set FEISHU_APP_SECRET \
  --integration team-context-mcp --value-stdin

# tcmcp-remote 5min cache TTL 内自动用新 secret (无需重启)
# 想立即生效: zeabur service restart --id 6a1805b332700e299b750370
```

---

## 3 · Autopilot 管理

### 3a · 建 / 更新 autopilot (2026-05-28 spec · 个人版 + 团队版)

**个人 vs 团队是「数据范围」不是「推送渠道」**:两版都用 `notify_team` 推同一个群,区别只在范围(team=全队 / 个人=本人)和绑哪个 runtime。

```bash
cd ~/team-context
export TCMCP_AGENT_TOKEN=$(cat /path/to/autopilot-bot-pat.txt)   # 一次性 ops · 不要 commit
multica daemon start                                              # 常驻 runtime 在线

# 团队版(全队汇总 · DRI 跑) —— 取代旧的 apply-autopilots.sh
bash scripts/team-autopilot.sh all codex        # 或单个: monday-kickoff / daily-summary / wednesday-stats / monthly-health
```

- 脚本自动:选在线 runtime → 建/复用 agent(注入 `AUTOPILOT_SCOPE`)→ 建/更新 autopilot + cron(幂等)。**不需要**手动先建 agent。
- 团队成员自己跑 `bash scripts/my-autopilot.sh all codex` 建个人版(见 [`ONBOARDING-MEMBER.md`](./ONBOARDING-MEMBER.md) §6)。
- 改 YAML(新 autopilot / 改 prompt):仍须含 PB-04 guardrails(`forbidden_commands ≥ 5` 含 `git push` · `max_budget_usd ≤ 150`)+ `integration_ref: team-context-mcp`;脚本会 lint,缺一拒建。
- `apply-autopilots.sh` 已 **deprecated**(不注入 `AUTOPILOT_SCOPE` · 与 scope 分支 prompt 不兼容)。

### 3b · 加新 agent (autopilot bot)

```bash
# 找当前 Codex runtime ID
CODEX_RUNTIME=$(multica runtime list --output json | jq -r '.[] | select(.provider=="codex") | .id' | head -1)

# 准备 custom_env · ⚠️ AUTOPILOT_SCOPE 必填,否则 scope 分支 prompt 落到 undefined
# (这正是 apply-autopilots.sh 废弃的原因)。多数情况用 team/my-autopilot.sh 自动注入,下面是手动 fallback。
cat > /tmp/agent-env.json <<EOF
{"TCMCP_REMOTE_URL":"https://mcp.teamctx.actionow.ai/mcp","TCMCP_AGENT_TOKEN":"$(cat /path/to/autopilot-bot-pat.txt)","AUTOPILOT_SCOPE":"team"}
EOF
chmod 600 /tmp/agent-env.json

# 建 agent
multica agent create \
  --name new-autopilot-bot-codex \
  --runtime-id $CODEX_RUNTIME \
  --visibility workspace \
  --custom-env-file /tmp/agent-env.json \
  --output table
rm /tmp/agent-env.json
```

### 3c · 暂停 / 删除 autopilot

```bash
multica autopilot delete <id>   # 整个删 · 触发器一起没
# 单删触发器: multica autopilot trigger-delete <trigger-id>
```

---

## 4 · Zeabur ops

### 4a · 看服务状态

```bash
zeabur project list                       # 包含 teamctx
zeabur -i=false service list --project-id 6a1800dd7ba640a55b20bf41 --json | jq '.[] | {Name, ID}'
zeabur -i=false service network --id <svc-id>     # 内部 DNS + 外部端口
```

### 4b · 看 build / runtime log

```bash
TCMCP=6a1805b332700e299b750370
DEPLOY_ID=$(zeabur -i=false deployment list --service-id $TCMCP --json | jq -r '.[0].ID')

# Runtime log (default)
zeabur -i=false deployment log --service-id $TCMCP --deployment-id $DEPLOY_ID | tail -20

# Build log
zeabur -i=false deployment log --service-id $TCMCP --deployment-id $DEPLOY_ID --type build | tail -30
```

### 4c · Redeploy / 回滚

```bash
# 重新部署当前 main
zeabur -i=false service redeploy --id $TCMCP -y

# 回滚: Zeabur dashboard → service → Deployments tab → 前一次 → Redeploy
# (CLI 不直接支持 specific-deployment redeploy)
```

### 4d · 改环境变量

```bash
# 加 (key 已存在会报 already exists · 用 update)
zeabur -i=false variable create --id $TCMCP -k NEW_KEY=value -y

# 改
zeabur -i=false variable update --id $TCMCP -k EXISTING_KEY=new_value -y

# 看
zeabur -i=false variable list --id $TCMCP

# 删: 走 dashboard
```

---

## 5 · 月度维护 (每月 1 号 30 分钟)

| 任务 | 命令 / 文档 |
|---|---|
| 看 monthly-health autopilot 报告 | 飞书群应自动收到 · 没收到看 `multica autopilot runs <monthly-id>` |
| Skill 健康检查 (90 天 stale) | `multica skill list --output json \| jq '.[] \| select(.last_reviewed_at == null) \| .name'` · 没 review 过的 |
| Label 跟 standards 对齐 | `multica label list` 跟 `team-context/standards/labels.md` diff · 不一致更新代码或 label |
| CLAUDE.md token check | `wc -w team-context/claude_md_team_global.md` · ≤ 2800 (CI 限);超了 prune |
| Cost check | Zeabur dashboard → project teamctx → Resource Usage |

季度额外:
- 老 autopilot run 历史归档 (`multica autopilot runs --since 90d` 之前的可考虑清掉)
- 老 agent (archived) 真删 (目前需 web UI · CLI 无 hard-delete)
- DRI mac daemon 升 multica binary (`multica update`)

---

## 6 · Incident 排查

### 6a · Autopilot run 显示 `failed`

```bash
# 1. 看 run 详情 + issue body (agent 会写失败原因到 issue)
RUN_ID=<failed run id>
multica autopilot runs <autopilot-id> --output json | jq '.[] | select(.id=="'$RUN_ID'")'
ISSUE_ID=$(multica autopilot runs <autopilot-id> --output json | jq -r '.[] | select(.id=="'$RUN_ID'") | .issue_id')
# 看 issue body (Codex/Claude 会把失败原因写到这)
multica issue get $ISSUE_ID --output json | jq -r .description

# 2. 看 daemon log
grep "task=" ~/.multica/daemon.log | grep -A20 "<task-id>"
```

**常见 failed 类型:**
- `notify_team` 工具找不到 → 这正是我们 W5 部署遇到的坑。修法:
  - Codex agent: 检查 `~/.codex/config.toml` 有 `[mcp_servers.tcmcp-remote]` 段 · url 指云 · `bearer_token_env_var = TCMCP_AGENT_TOKEN`
  - Claude agent: 检查 agent.mcp_config 字段不是 null
  - 验证 token: `curl https://api.teamctx.actionow.ai/api/me -H "Authorization: Bearer $TCMCP_AGENT_TOKEN"`
- `daemon timeout (2h)` → agent 卡 · 看 `~/.multica/daemon.log` 找具体堵在哪
- `unable to ping database` (tcmcp 端) → 看 tcmcp `/health` · multica_reachable 应该 true · 否则 multica-backend 挂了

### 6b · tcmcp /health 不通 / 返 Bad Gateway

```bash
TCMCP=6a1805b332700e299b750370
zeabur -i=false deployment list --service-id $TCMCP | head -3   # 看 STATUS
zeabur -i=false deployment log --service-id $TCMCP --deployment-id <latest> | tail -30
```

**常见原因:**
- `MULTICA_SERVICE_TOKEN/WORKSPACE_ID 必填` → 这 2 个 env 漏了 / token 失效 · 重发
- `unable to ping database` (multica 端) → multica-backend 挂 · 先修它
- 端口不对 → tcmcp 听 `MCP_HTTP_PORT` · Zeabur ingress 期望 8080 · 验证 `zeabur -i=false service network --id $TCMCP` 显示 `port: 8080`

### 6c · multica-backend 挂

```bash
BACKEND=6a1803627ba640a55b20c146
curl -s https://api.teamctx.actionow.ai/healthz
# 不返 200:
zeabur -i=false deployment log --service-id $BACKEND --deployment-id <latest> | grep -iE "error|fatal|panic|FATAL" | tail -10
```

**常见:** `MULTICA_SECRET_MASTER_KEY not set` (control plane 启动校验) · `unable to ping database` (postgres 挂) · `JWT_SECRET=change-me-in-production` (生产 env 校验)。

### 6d · 飞书消息发不出

```bash
# tcmcp /health 看 feishu_ready
curl -s https://mcp.teamctx.actionow.ai/health | jq .feishu_ready
# false → secret/config 没拉到 · 检查:
multica secret list --integration team-context-mcp           # 应 ≥ 2 (APP_ID + APP_SECRET)
multica integration get team-context-mcp | jq .config        # 应有 feishu_team_chat_id

# true 但仍发不出 → 飞书 app 没权限或 chat_id 不对 · 浏览器开飞书开发者后台校验 app scope
```

### 6e · DRI mac daemon 挂

```bash
multica daemon status               # 看 pid
multica daemon restart              # 重启
tail -30 ~/.multica/daemon.log
multica runtime list                # 重启后应该 3 个 runtime 都 online
```

---

## 7 · 紧急回退 (上线后 < 7 天可用)

如果云端整体出大问题 · 临时拉回 10.0.5.51 本地 multica:

```bash
# 1. 改本地 CLI 回老 server
multica config set server_url http://10.0.5.51:8083

# 2. 起 10.0.5.51 上的 docker compose
cd ~/feibo/tc-multica
docker compose -f docker-compose.selfhost.yml up -d

# 3. 团队成员: 把他们 ~/.codex/config.toml 里 tcmcp-remote url 改回 http://10.0.5.51:8443/mcp
#    (或 DRI 临时 ssh 到那台机器跑 docker compose -f team-context-mcp/docker-compose.yml up -d)
```

**前提:** 10.0.5.51 上 `pgdata` volume 还在(我们承诺 7 天才删 · 上云后**不要立即清** docker volume)。

---

## 8 · 给团队成员发的「3 步速查卡」(可选 · 飞书钉到群公告)

```
🆘 卡住怎么办

1. CLI 报错: 截图 + 完整命令 + 输出贴飞书 @ DRI
2. MCP 工具看不到: ~/.codex/config.toml 或 ~/.claude/mcp.json 复查 (路径里 <your-user> 改了吗)
3. 跑慢 / 没响应: 重启 CLI · 重连 wifi · 仍卡 @ DRI

下面命令报错就直接抄给 DRI:
  multica auth status
  curl -s https://api.teamctx.actionow.ai/healthz
  curl -s https://mcp.teamctx.actionow.ai/health
```

---

**Owner:** DRI
**Last reviewed:** 2026-05-28
**实测来源:** 本文档命令全部来自 2026-05-28 W5 cloud 部署 + 修 codex MCP wiring + bootstrap A-E 全过程 · `multica autopilot trigger monday-kickoff` 真送出飞书 card `om_xxx` 验证。
