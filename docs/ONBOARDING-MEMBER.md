# AI MIQ Team-Context · 接入文档 v1.0

> **5-10 分钟完成** · macOS (Linux 命令几乎一致 · brew → apt/yum)
> 每步带验证 · 期望输出对不上就停下来,别往下走

## 你拿到 (DRI 给你)

| 物件 | 形式 | 干嘛用 |
|---|---|---|
| multica 账号 | email · 你常用的 | 登 web UI + CLI |
| PAT token | `mul_xxxxxxxxxxxxxxxx` (44 字符) | CLI auth · MCP bearer |
| workspace_id | UUID `b18d7b35-...` | 你属于哪个团队空间 |
| 飞书群邀请 | 「Team Context」群 | 接收 autopilot 推送 + DM |

如果缺任何一项 · 找 DRI 补 · 别自己试着注册。

---

## 0 · 前置 (一次性 · 3 分钟)

```bash
brew tap multica-ai/tap
brew install multica
brew install jq node@22
```

**验证 0:**
```bash
multica --version    # 期望: multica v0.3.x · 不到 0.3 升级
node --version       # 期望: v22.x.x
jq --version         # 期望: jq-1.7+
```

3 个命令任何一个报 not found · 装它再继续。

---

## 1 · 连云 multica (1 分钟)

```bash
multica config set server_url https://api.teamctx.actionow.ai
multica config set app_url https://teamctx.actionow.ai
multica config set workspace_id <DRI 给你的 UUID>

# PAT 写 shell rc · 永久生效
echo 'export MULTICA_TOKEN=<DRI 给你的 mul_xxx>' >> ~/.zshrc
source ~/.zshrc
```

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

报 `invalid token` · PAT 抄错了 · 找 DRI 重发。
报 `connection refused` · 网络问题 · curl 一下 `https://api.teamctx.actionow.ai/healthz` 应该返 `{"status":"ok"...}`。

---

## 2 · 装 tcmcp-local (本地 12 工具 · 2 分钟)

```bash
cd ~
git clone https://github.com/feibo-ai/team-context-mcp.git
cd team-context-mcp
npm install -g pnpm@11
pnpm install --frozen-lockfile
pnpm --filter @tcmcp/shared build
pnpm --filter @tcmcp/local  build
```

**验证 2:** (会等 ~4 秒 · 起 server → 列工具 → 杀掉)
```bash
{
  echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"v","version":"0"}}}'
  echo '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'
  sleep 2
} | node ~/team-context-mcp/packages/local/dist/server.js 2>/dev/null \
  | jq -r 'select(.id==2)|.result.tools|length'
```
期望:`12`

返回别的数字 / 空 / error · build 没成功 · 重跑 `pnpm install` + build。

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
ls ~/.claude/skills/                # 期望看到: pre-clear / rpi-research / ...
head -3 ~/.claude/skills/pre-clear/SKILL.md
```
期望前 3 行:
```
---
name: pre-clear
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

## 故障速查

| 症状 | 原因 | 修法 |
|---|---|---|
| `multica auth status` → invalid token | PAT 错 | 找 DRI 重发 |
| `multica auth status` → connection refused | DNS/网络 | `curl https://api.teamctx.actionow.ai/healthz` 应返 200 |
| Step 2 jq 验证返回 ≠ 12 | tcmcp-local build 失败 | `cd ~/team-context-mcp && pnpm install --frozen-lockfile && pnpm --filter @tcmcp/local build` 重跑 |
| Step 3 同步 0 个 skill | workspace_id 抄错 | `multica config show` 看;DRI 给的应是 UUID 36 字符 |
| Step 4 MCP 工具找不到 | config 路径里 `<把-我换成你的用户名>` 没改 | 改成 `whoami` 输出的真实用户名 |
| Codex 4a 验证看不到 search_chat | 没重启 Codex | 完全退出再开 |
| Claude Code 4b 看不到工具 | mcp.json 路径不对 OR JSON 语法错 | `jq . ~/.claude/mcp.json` 检查语法 |

---

## 进阶 (按需 · 默认 DRI 已配)

### 启用 Skill 自动 fuzzy match (Claude Code)
12 个 skill 已落 `~/.claude/skills/` · Claude Code 会自动按 SKILL.md `description` 字段触发(比如你说 `/clear` · `pre-clear` skill 自动启)。无需额外操作。

Codex 暂不支持自动 fuzzy match · 工具仍可手动调:`/skill pre-clear`。

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
