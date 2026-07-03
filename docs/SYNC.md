# 团队配置同步 — Skills · MCP · 全局规则 × 4 个 agent 界面

把团队的 **① SOP skills ② MCP 服务配置 ③ 全局规则(claude_md_team_global)** 一致地铺到
**Claude Code · Claude Desktop · Codex CLI · Codex app** 四个界面。

## 规范源(唯一真相)
| 产物 | 源 |
|---|---|
| SOP skills(含脚本)| multica registry(`multica skill`)—— registry 是第三份真相;本 repo `skills/tc-*/` 为编辑源,经 `multica skill push` 推上 registry |
| 全局规则 | `claude_md_team_global.md`(团队 5 条核心规则 + 跨项目规则) |
| MCP 配置值 | 见下「MCP 配置」节(remote server URL 固定 + per-user token) |

## 一键同步
**Skills 走 registry**(脚本/正文一起拉),全局规则走软链:
```bash
# 1) 从 registry 把全部 tc-* skill(含脚本)拉到双目录:
#    ~/.claude/skills(Claude Code/Desktop)+ ~/.agents/skills(Codex 原生扫描)
multica skill pull --all
multica skill pull --all --dir ~/.agents/skills

# 2) 全局规则软链到各界面(改源各界面自动最新)
bash scripts/sync-team-config.sh

# 3) (推荐 · 一次性)装每小时自动同步,之后 registry 更新至多 1h 全机就位
bash scripts/install-skill-pull-cron.sh
```
`multica skill pull` 原子换入(不会留半写 skill)、frontmatter spec-clean(只 name+description)。
过期检测:`multica skill pull --all --check`(有漂移非零退出)或直接 `multica doctor`
(内置 skills-sync 软检查)。DRI 开发机走 git 软链(sync-team-config.sh),pull 会拒绝
覆盖软链(--force 才会)——两种布局互斥,别混。

`scripts/sync-team-config.sh` 做 2 件:
1. **全局规则 → ** `~/.claude/CLAUDE.md`(Claude Code 全局)+ `~/.codex/AGENTS.md`(Codex 全局),均软链到 `claude_md_team_global.md`。
2. **Skills 编辑源 → multica registry**(`multica skill push`):把本 repo `skills/tc-*/` 推上 registry(共享存储,daemon/autopilot + 任意界面经 `multica skill pull` 取);缺则建,已存更新。

> 改 skill 正文/脚本:编辑本 repo `skills/tc-*/` → `multica skill push` 推 registry → 各机 `multica skill pull --all` 取。**不再 clone/build 本地 MCP**。
> MCP 配置(只剩 remote)**不在脚本里**(含 per-user token,且每界面文件格式不同)—— 按下表手动配一次。

## 同步矩阵
| 产物 | Claude Code | Claude Desktop | Codex CLI | Codex app |
|---|---|---|---|---|
| **Skills (tc-*)** | `multica skill pull --all` → `~/.claude/skills/`(含脚本)| 本地 agent 模式 skills-plugin,复用 `~/.claude/skills/`(`pull` 即覆盖) | **原生**(agentskills.io):扫 `~/.agents/skills/`,description 自动触发 → `multica skill pull --all --dir ~/.agents/skills` | 同 Codex CLI(共用 `~/.agents/skills`) |
| **MCP**(tcmcp-remote)| `~/.claude.json` → `mcpServers` | `~/Library/Application Support/Claude/claude_desktop_config.json` → `mcpServers` | `~/.codex/config.toml` → `[mcp_servers.*]` | 共用 `~/.codex/config.toml` |
| **全局规则** | `~/.claude/CLAUDE.md` 软链(脚本)+ 各产品 repo 的 `CLAUDE.md` | 设置→自定义指令 / Project(手动粘 `claude_md_team_global.md`) | `~/.codex/AGENTS.md` 软链(脚本)+ 各产品 repo 的 `AGENTS.md` | 共用 `~/.codex/AGENTS.md` |

**要点**
- **Skills**:Claude 系走 `~/.claude/skills/`,Codex 走 `~/.agents/skills/`(原生 agentskills.io 发现,同一份标准 skill 目录,无需 index 文件);双目录都用 `multica skill pull` 从 registry 拉 = 自动最新(装 cron 后免手动)。
- **全局规则**:Claude Code / Codex 软链同一个源 → 改一处全更新。Claude Desktop 无 CLAUDE.md 机制 → 需手动把内容贴进“自定义指令/Project”(变更少,手动可接受)。
- **MCP**:RPI 文档流已迁到 skill + `multica` CLI + `tc-render/publish.py`,**日常不再走本地 MCP**。MCP 配置只需接 `tcmcp-remote`(`notify_team` 等飞书工具)。`tcmcp-local` 本期作兜底仍可注册但日常不调(迭代 2 删),新成员**只配 remote**即可。token 由成员自己 `multica login` 拿(`jq -r .token ~/.multica/config.json`),不是 DRI 私信(per-user 审计)。

## MCP 配置(每界面一次 · 只剩 tcmcp-remote · token 占位)
RPI 文档流已迁到 skill + `multica` CLI + `tc-render/publish.py`,**日常不再走本地 MCP**。这里只需接 `tcmcp-remote`(`notify_team` 等飞书工具)。

**值(固定)**:
- `MULTICA_TOKEN = <你自己 multica login 拿的 mul_ token>`(取值:`jq -r .token ~/.multica/config.json` · 非 DRI 发)
- tcmcp-remote:`https://mcp.teamctx.actionow.ai/mcp`,头 `Authorization: Bearer <同一 token>`

**Claude Code** `~/.claude.json`(或项目 `.mcp.json`):
```jsonc
"mcpServers": {
  "tcmcp-remote": { "type":"http","url":"https://mcp.teamctx.actionow.ai/mcp","headers":{"Authorization":"Bearer mul_…"} }
}
```
**Claude Desktop** `claude_desktop_config.json`:同上 `mcpServers`(`tcmcp-remote` 若 Desktop 版本不支持 http 远程则用 `mcp-remote` 代理)。
**Codex CLI / app** `~/.codex/config.toml`:
```toml
[mcp_servers.tcmcp-remote]
url = "https://mcp.teamctx.actionow.ai/mcp"
bearer_token_env_var = "TCMCP_AGENT_TOKEN"   # export TCMCP_AGENT_TOKEN=mul_… in shell rc
```

> **兜底说明**:本地 MCP `@tcmcp/local` 本期**两端仍保留注册作兜底,但日常不调**(迭代 2 删)。新成员**只配上面的 `tcmcp-remote`** 即可,无需再 clone/build/注册 `tcmcp-local`。

## 改了东西怎么办
- 改 skill 正文/脚本:编辑 repo 内 `skills/tc-*/` → PR 合并 → 跑 `scripts/sync-team-config.sh` 推 registry(create-or-update + files + **写后校验**,失败非零退出)→ 各机 cron 每小时自动 `pull`(或手动 `multica skill pull --all` 立即取)。
- 改全局规则:编辑 repo 内的源 → 软链处自动最新。
- 加新成员:成员自己 `multica login` 拿 token → 把 email 告诉 DRI → DRI 跑 `multica user create --email <email> --role member` 把其加进 workspace(幂等 · **不发 token**)+ 给 workspace UUID;成员再 `multica skill pull --all` 同步 skill → 接 remote MCP(`tcmcp-remote`)→ 跑 `scripts/sync-team-config.sh` 软链全局规则。**不再 clone/build 本地 MCP**。
- 换 token / workspace:更新各界面 MCP 配置的 `MULTICA_TOKEN` / `MULTICA_WORKSPACE_ID`(只剩 `tcmcp-remote` 一处 + shell rc 的 `TCMCP_AGENT_TOKEN`;CLI 自己读 `~/.multica/config.json` 无需改)。
