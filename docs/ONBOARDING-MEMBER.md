# AI MIQ Team-Context · 接入文档 v1.0

> **5-10 分钟完成** · macOS (Linux 命令几乎一致 · brew → apt/yum)
> 每步带验证 · 期望输出对不上就停下来,别往下走

## 你拿到 (DRI 给你)

| 物件 | 形式 | 干嘛用 |
|---|---|---|
| multica 账号 | email · 你常用的 | 登 web UI + CLI(**你自己的身份**) |
| token | `mul_...` · **你自己 `multica login` 拿的** | CLI auth · MCP bearer(归属你本人 · 可审计) |
| workspace_id | UUID `fb23cf99-...` (slug `team-context`) | 你属于哪个团队空间 |
| 飞书群邀请 | 「Team Context」群 | 接收 autopilot 推送 + DM |

> **DRI 给你**:① 你先 `multica login` 拿到自己的 token,把 email 给 DRI → DRI 跑 `multica user create --email <你的 email> --role member` 把你加进 workspace ② workspace UUID + 飞书群邀请。
> **token 不是 DRI 发的** —— 你自己 `multica login`(你自己的账号)拿;每个人用自己的 token,操作都归属到本人(per-user 审计)。
> (例外:无法自助登录的服务/bot 账号,才由 DRI 用 `multica auth issue-token` 发 PAT。)

如果 `multica login` 后 `multica workspace list` 看不到 `team-context` · 找 DRI 把你加进 workspace。

---

## 0 · 前置 (一次性 · 3 分钟)

```bash
# jq / node 用 brew
brew install jq node@22

# multica CLI 走官方 tap(升级 = brew upgrade multica-ai/tap/multica)
brew install multica-ai/tap/multica
```

> 已装过想升级:`brew upgrade multica-ai/tap/multica`。当前版本 v0.4.x。

**验证 0:**
```bash
multica --version    # 期望: multica v0.4.x
node --version       # 期望: v22 或以上 (v22-v29 都行)
jq --version         # 期望: jq-1.7+
```

3 个命令任何一个报 not found · 装它再继续。

---

## 1 · 连云 multica (1 分钟)

```bash
# 浏览器登录(会跳 teamctx.actionow.ai 授权)
multica login

# 切到团队 workspace
multica workspace switch team-context
```

> `multica login` 走浏览器授权到 `https://teamctx.actionow.ai`,搞定后再 `workspace switch team-context`。

`multica login` 把**你自己的 token** 存进 `~/.multica/config.json`。tcmcp-local 启动只读 env(不读 multica config),所以把 3 个 export 写进 shell rc —— token 直接从你的 login 结果读出来(**不用任何人发给你**):

```bash
cat >> ~/.zshrc <<'EOF'
export MULTICA_SERVER_URL=https://api.teamctx.actionow.ai
export MULTICA_WORKSPACE_ID=fb23cf99-5f4c-4815-b2b3-8d5e323659f6
export MULTICA_TOKEN=$(jq -r .token ~/.multica/config.json 2>/dev/null)
EOF
source ~/.zshrc
```
> `<<'EOF'` 让那行 `$(jq …)` 原样写进 rc —— 每开新 shell 自动从 config.json 读你当前 login 的 token。重新 `multica login` 后无需改 rc。
> MCP 配置文件(`~/.claude.json` / `~/.codex/config.toml`)是 JSON/TOML,不能跑 `$(…)`,需把 token **实值**填进去:`jq -r .token ~/.multica/config.json` 取值粘贴(见下「MCP 接入」)。

**验证 1:**
```bash
multica auth status
```
期望(精确匹配 3 行):
```
Server:  https://api.teamctx.actionow.ai
User:    <你的 name> (<你的 email>)
Token:   mul_xxxxxxxx...
```

报 `invalid token` · 你的 token 失效 / 没 login · 重新 `multica login`(拿你自己的新 token)再 `source ~/.zshrc`。
报 `User:` 那行不是你本人 / 看不到 `team-context` · 你还没被加进 workspace · 找 DRI 跑 `multica user create --email <你的 email> --role member`。
报 `connection refused` · 网络问题 · curl 一下 `https://api.teamctx.actionow.ai/healthz` 应该返 `{"status":"ok"...}`。

---

## 2 · 装 tcmcp-local (本地 12 工具 · 2 分钟)

```bash
cd ~
git clone https://github.com/feibo-ai/team-context-mcp.git
cd team-context-mcp
npm install -g pnpm@11
CI=true pnpm install --frozen-lockfile   # CI=true 避开非交互式 TTY 阻塞
pnpm --filter @tcmcp/shared build
pnpm --filter @tcmcp/local  build
```

**验证 2:** (会等 ~4 秒 · 起 server → 列工具 → 杀掉)
```bash
# 这里 sleep 不能省 · 给 server 时间响应
{
  echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"v","version":"0"}}}'
  echo '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'
  sleep 2
} | node ~/team-context-mcp/packages/local/dist/server.js 2>/dev/null \
  | jq -r 'select(.id==2)|.result.tools|length'
```
期望:`12`

返回 `0 / empty / error`:
- 报 `multica config missing. Set MULTICA_SERVER_URL/MULTICA_TOKEN/MULTICA_WORKSPACE_ID` → 你 Step 1 那 3 个 env 没 source · 跑 `source ~/.zshrc` 或重开 terminal
- build 没成功 → `cd ~/team-context-mcp && CI=true pnpm install --frozen-lockfile && pnpm --filter @tcmcp/local build` 重跑

---

## 3 · 同步 12 个团队 skill (1 分钟)

把下面整段贴到终端跑 · 会写一个 sync 脚本到 `~/.local/bin/`:

```bash
mkdir -p ~/.local/bin
cat > ~/.local/bin/sync-skills.sh <<'SYNC_EOF'
#!/usr/bin/env bash
# Pull all team skills from multica → ~/.claude/skills/
set -euo pipefail
: "${MULTICA_SERVER_URL:=https://api.teamctx.actionow.ai}"
: "${MULTICA_WORKSPACE_ID:?MULTICA_WORKSPACE_ID must be set}"
: "${MULTICA_TOKEN:?MULTICA_TOKEN must be set}"

TARGET="${HOME}/.claude/skills"
mkdir -p "$TARGET"
ids=$(curl -fsS -H "Authorization: Bearer $MULTICA_TOKEN" \
  "${MULTICA_SERVER_URL}/api/skills?workspace_id=${MULTICA_WORKSPACE_ID}" \
  | jq -r '.[].id')
n=0
for id in $ids; do
  json=$(curl -fsS -H "Authorization: Bearer $MULTICA_TOKEN" \
    "${MULTICA_SERVER_URL}/api/skills/${id}?workspace_id=${MULTICA_WORKSPACE_ID}")
  name=$(echo "$json" | jq -r .name)
  desc=$(echo "$json" | jq -r .description)
  body=$(echo "$json" | jq -r .content)
  d="${TARGET}/${name}"; mkdir -p "$d"
  {
    printf -- '---\n'
    printf 'name: %s\n' "$name"
    printf 'description: %s\n' "$(echo "$desc" | jq -R -s .)"
    printf -- '---\n'
    printf '%s\n' "$body"
  } > "${d}/SKILL.md"
  echo "synced: $name"
  n=$((n+1))
done
echo "Done · $n skills → $TARGET"
SYNC_EOF
chmod +x ~/.local/bin/sync-skills.sh

# 跑
MULTICA_WORKSPACE_ID=$(multica config show | awk '/workspace_id:/{print $2}') \
  bash ~/.local/bin/sync-skills.sh
```

**验证 3:**
```bash
ls ~/.claude/skills/ | wc -l       # 期望: 12
ls ~/.claude/skills/                # 期望看到: tc-handoff / tc-2-research / ...
head -3 ~/.claude/skills/tc-handoff/SKILL.md
```
期望前 3 行:
```
---
name: tc-handoff
description: "Use BEFORE running /clear...
```

少于 12 个目录 · 重跑 sync 脚本 · 仍少看 stderr 哪个 skill 失败。

---

## 4 · 配 MCP (你装哪个 CLI 就走哪节)

### 4a · Codex 用户

编辑 `~/.codex/config.toml` · 加 2 段(放在文件末尾即可):

```toml
[mcp_servers.tcmcp-local]
command = "node"
args = ["/Users/<把-我换成你的用户名>/team-context-mcp/packages/local/dist/server.js"]

[mcp_servers.tcmcp-remote]
url = "https://mcp.teamctx.actionow.ai/mcp"
bearer_token_env_var = "TCMCP_AGENT_TOKEN"
```

设 token 环境变量(MCP server 启动时读):
```bash
echo 'export TCMCP_AGENT_TOKEN=$MULTICA_TOKEN' >> ~/.zshrc
source ~/.zshrc
```

**验证 4a:** 重启 Codex · 新 session 里说:
> 调 search_chat 找包含 "Team Context" 的群 · 告诉我 chat_id

期望 Codex:
- 调用 `tcmcp-remote__search_chat` 工具
- 返回 `oc_035c15b7fb12fed8d0e022fe2f529553`

工具找不到 · `cat ~/.codex/config.toml | grep tcmcp` 看格式有没有抄错 + 路径里 `<把-我换成你的用户名>` 改没改。

### 4b · Claude Code 用户

编辑 `~/.claude/mcp.json` (没有的话新建):

```json
{
  "mcpServers": {
    "tcmcp-local": {
      "command": "node",
      "args": ["/Users/<把-我换成你的用户名>/team-context-mcp/packages/local/dist/server.js"]
    },
    "tcmcp-remote": {
      "url": "https://mcp.teamctx.actionow.ai/mcp",
      "headers": { "Authorization": "Bearer ${MULTICA_TOKEN}" }
    }
  }
}
```

**验证 4b:** 重启 Claude Code · `/clear` · 输入:
> list mcp tools whose name contains 'notify' or 'plan_create'

期望看到至少:
- `tcmcp-remote/notify_team` (远程飞书工具)
- `tcmcp-local/plan_create` (本地 RPI 工具)

---

## 5 · 端到端冒烟 (30 秒)

任一 CLI 里说:
> 用 search_chat 查一下飞书群,告诉我「Team Context」群的 chat_id

期望:回 `oc_035c15b7fb12fed8d0e022fe2f529553`。**这意味着:**
- ✅ MCP 配置加载了 (tcmcp-remote 工具能调)
- ✅ TCMCP_AGENT_TOKEN 通过了 multica bearer auth
- ✅ tcmcp-remote 从 multica 拉到飞书 secret 初始化了 lark SDK
- ✅ lark SDK 真的能调飞书 OpenAPI

回的 chat_id 跟期望一致 = 接入完毕。

---

## 6 · (可选) 建你的个人 autopilot

接入完成后,可一键建你自己的 4 个 autopilot(日报 / 周一 / 周三 / 月度):数据范围只你自己 · 全部推团队群(卡片标题带你名字 · 不是私信)。

**前提:** clone 本仓库(团队成员有 read 权限) —— 没 clone 过先 `git clone https://github.com/feibo-ai/team-context.git ~/team-context`。

```bash
cd ~/team-context && git pull
export TCMCP_AGENT_TOKEN=$MULTICA_TOKEN   # 个人 autopilot 用你自己的 token 连飞书
multica daemon start                       # autopilot 靠你这台机的 daemon 在线才跑
bash scripts/my-autopilot.sh all codex     # provider: codex | claude | hermes
```

- ⚠️ **只在你 daemon 在线时跑** · 关机 / 睡眠日 cron 静默 skip(这是设计 · 不是 bug)。
- 撤掉:`multica autopilot list | grep -- -<你的 email 前缀>` 找 id → `multica autopilot delete <id>`。

---

## 故障速查

| 症状 | 原因 | 修法 |
|---|---|---|
| `multica auth status` → invalid token | 你的 token 失效 / 没 login | 重新 `multica login`(拿你自己的新 token)· 再 `source ~/.zshrc` |
| `multica auth status` → connection refused | DNS/网络 | `curl https://api.teamctx.actionow.ai/healthz` 应返 200 |
| Step 2 jq 验证返回 ≠ 12 | tcmcp-local build 失败 | `cd ~/team-context-mcp && pnpm install --frozen-lockfile && pnpm --filter @tcmcp/local build` 重跑 |
| Step 3 同步 0 个 skill | workspace_id 抄错 | `multica config show` 看;DRI 给的应是 UUID 36 字符 |
| Step 4 MCP 工具找不到 | config 路径里 `<把-我换成你的用户名>` 没改 | 改成 `whoami` 输出的真实用户名 |
| Codex 4a 验证看不到 search_chat | 没重启 Codex | 完全退出再开 |
| Claude Code 4b 看不到工具 | mcp.json 路径不对 OR JSON 语法错 | `jq . ~/.claude/mcp.json` 检查语法 |

---

## 进阶 (按需 · 默认 DRI 已配)

### 启用 Skill 自动 fuzzy match (Claude Code)
12 个 skill 已落 `~/.claude/skills/` · Claude Code 会自动按 SKILL.md `description` 字段触发(比如你说 `/clear` · `tc-handoff` skill 自动启)。无需额外操作。

Codex 暂不支持自动 fuzzy match · 工具仍可手动调:`/skill tc-handoff`。

### 本地跑 multica daemon (autopilot 执行环境)
默认 DRI mac 跑 daemon · 4 个 autopilot 由 DRI 上注册的 Codex/Claude runtime 执行。**你不需要装。** 如果团队规模上去 · 多人跑 daemon 分担:
```bash
multica daemon start
multica runtime list   # 应看到你 mac 的 runtime
```

### 创建自己的 PAT (轮换 / 重发)
DRI 给的 PAT 应该够用半年。需要新的:
1. 浏览器开 https://teamctx.actionow.ai
2. 右上 Settings → API Tokens → Generate
3. 抄出来 · 覆盖 `~/.zshrc` 的 `MULTICA_TOKEN`
4. `source ~/.zshrc`

---

## 联系

任何步骤卡住 · 直接戳 DRI (actionow.ai@gmail.com) · 把出错的命令 + 完整输出贴过来。

**接入完成的标准:** Step 1 + Step 5 都通过验证 = 你已就绪 · 可以开始用了。
