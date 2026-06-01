# 团队配置同步 — Skills · MCP · 全局规则 × 4 个 agent 界面

把团队的 **① SOP skills ② MCP 服务配置 ③ 全局规则(claude_md_team_global)** 一致地铺到
**Claude Code · Claude Desktop · Codex CLI · Codex app** 四个界面。

## 规范源(唯一真相,在本 repo)
| 产物 | 源 |
|---|---|
| SOP skills | `skills/tc-*/SKILL.md`(12 个) |
| 全局规则 | `claude_md_team_global.md`(团队 5 条核心规则 + 跨项目规则) |
| MCP 配置值 | 见下「MCP 配置」节(server URL 固定 + per-user token) |

## 一键同步(软链为主 → 改源各界面自动最新)
```bash
bash scripts/sync-team-config.sh
```
脚本做 3 件:
1. **Skills → Claude Code**:`~/.claude/skills/tc-* ` 软链到本 repo(Claude Desktop 本地 agent 模式的 skills-plugin 复用同一目录)。
2. **全局规则 → ** `~/.claude/CLAUDE.md`(Claude Code 全局)+ `~/.codex/AGENTS.md`(Codex 全局),均软链到 `claude_md_team_global.md`。
3. **Skills → multica registry**(`multica skill`):共享存储,daemon/autopilot + 任意界面经 MCP 发现;缺则建,已存跳过(改正文用 `multica skill update`)。

> MCP 配置**不在脚本里**(含 per-user token,且每界面文件格式不同)—— 按下表手动配一次。

## 同步矩阵
| 产物 | Claude Code | Claude Desktop | Codex CLI | Codex app |
|---|---|---|---|---|
| **Skills (tc-*)** | `~/.claude/skills/tc-*` 软链(脚本①)| 本地 agent 模式 skills-plugin,复用 `~/.claude/skills/`(脚本① 即覆盖) | **无原生 skill** → 流程靠 AGENTS.md;skill 正文经 multica registry(MCP `multica skill get`)或直接读 repo | 同 Codex CLI(共用 `~/.codex/`) |
| **MCP**(tcmcp-local + tcmcp-remote) | `~/.claude.json` → `mcpServers` | `~/Library/Application Support/Claude/claude_desktop_config.json` → `mcpServers` | `~/.codex/config.toml` → `[mcp_servers.*]` | 共用 `~/.codex/config.toml` |
| **全局规则** | `~/.claude/CLAUDE.md` 软链(脚本②)+ 各产品 repo 的 `CLAUDE.md` | 设置→自定义指令 / Project(手动粘 `claude_md_team_global.md`) | `~/.codex/AGENTS.md` 软链(脚本②)+ 各产品 repo 的 `AGENTS.md` | 共用 `~/.codex/AGENTS.md` |

**要点**
- **Skills**:Claude Code / Desktop 走 `~/.claude/skills/`(软链=自动最新)。**Codex 没有 Claude 式 skill 机制** —— AGENTS.md 把 tc-* 当“流程描述”读,需要 skill 正文时经 multica registry 或读 repo。所有界面经 MCP 连 multica 都能发现 registry 里的 skill。
- **全局规则**:Claude Code / Codex 软链同一个源 → 改一处全更新。Claude Desktop 无 CLAUDE.md 机制 → 需手动把内容贴进“自定义指令/Project”(变更少,手动可接受)。
- **MCP**:三处配置文件已含 `tcmcp-local` + `tcmcp-remote`;新成员按下方模板配,token 由 DRI 私信。

## MCP 配置(每界面一次 · token 占位)
**值(固定)**:
- `MULTICA_SERVER_URL = https://api.teamctx.actionow.ai`
- `MULTICA_WORKSPACE_ID = fb23cf99-5f4c-4815-b2b3-8d5e323659f6`(slug `team-context`)
- `MULTICA_TOKEN = <DRI 私信给你的 mul_ token>`
- tcmcp-remote:`https://mcp.teamctx.actionow.ai/mcp`,头 `Authorization: Bearer <同一 token>`

**Claude Code** `~/.claude.json`(或项目 `.mcp.json`):
```jsonc
"mcpServers": {
  "tcmcp-local":  { "type":"stdio","command":"node","args":["<team-context-mcp>/packages/local/dist/server.js"],
                    "env":{"MULTICA_SERVER_URL":"https://api.teamctx.actionow.ai","MULTICA_WORKSPACE_ID":"fb23cf99-5f4c-4815-b2b3-8d5e323659f6","MULTICA_TOKEN":"mul_…"} },
  "tcmcp-remote": { "type":"http","url":"https://mcp.teamctx.actionow.ai/mcp","headers":{"Authorization":"Bearer mul_…"} }
}
```
**Claude Desktop** `claude_desktop_config.json`:同上 `mcpServers`(Desktop 只吃 stdio · `tcmcp-local` 必走 stdio;`tcmcp-remote` 若 Desktop 版本不支持 http 远程则用 `mcp-remote` 代理)。
**Codex CLI / app** `~/.codex/config.toml`:
```toml
[mcp_servers.tcmcp-local]
command = "node"
args = ["<team-context-mcp>/packages/local/dist/server.js"]
[mcp_servers.tcmcp-local.env]
MULTICA_SERVER_URL = "https://api.teamctx.actionow.ai"
MULTICA_WORKSPACE_ID = "fb23cf99-5f4c-4815-b2b3-8d5e323659f6"
MULTICA_TOKEN = "mul_…"
[mcp_servers.tcmcp-remote]
url = "https://mcp.teamctx.actionow.ai/mcp"
bearer_token_env_var = "TCMCP_AGENT_TOKEN"   # export TCMCP_AGENT_TOKEN=mul_… in shell rc
```

## 改了东西怎么办
- 改 skill / 全局规则:编辑 repo 内的源 → 软链处自动最新;skill 正文还要 `multica skill update` 推 registry(或重跑同步脚本,新增的会自动建)。
- 加新成员:发 token + 让其 clone 本 repo + 跑 `scripts/sync-team-config.sh` + 按上表配 MCP。
- 换 token / workspace:更新各界面 MCP 配置的 `MULTICA_TOKEN` / `MULTICA_WORKSPACE_ID`(共 3-4 处:Claude Code / Desktop / Codex / shell rc 的 `TCMCP_AGENT_TOKEN`)。
