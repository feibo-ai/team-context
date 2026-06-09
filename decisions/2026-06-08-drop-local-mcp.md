# Decision · 去本地 MCP — RPI 文档流迁到 skills + multica CLI + agent

**Date**: 2026-06-08 (迭代1 交付 · 迭代2 收尾进行中)
**DRI**: feibo
**Status**: decided
**Supersedes**: `2026-05-29-multica-control-plane.md` 与 `2026-05-26-v0.2-launch.md` 中「本地 MCP(@tcmcp/local · 13 工具)是 RPI 文档流当前机制」的假设;推翻 `plan_2026-06-08_team-iteration-sync.html`(非 dropmcp 版)的「把 local 改 HTTP transport / 远程化」方向。
**Issue**: TEA-79(迭代1)· TEA-84/48c1d637(迭代2 收尾)

## Context

W5 模型:团队 RPI 全程(plan/research/case/handoff 四类文档生成 + 方案A 内联渲染、低频工具)靠**本地 MCP 包 @tcmcp/local**(stdio · 由 Claude Code / Codex CLI spawn · 13 工具)。痛点:
1. **版本无关性差** — 渲染/发布逻辑埋在 MCP server 里,改一处要重装 server;Claude 与 Codex 两端各装一份,易漂移。
2. **命门(内联渲染)脆** — doc_publish 的 upload→comment 两步逻辑只活在 server 内,CLI/agent 无法独立复现。
3. **三份真相** — 渲染逻辑散在 repo / 物理 ~/.claude/skills / registry 三处,软链脏态(物理 SKILL.md 遮蔽)。

## Decision

把本地 MCP 的功能**搬出服务器**,落到三处版本无关的载体:

1. **渲染 + 校验 + 发布 → skill 自带脚本**:`team-context/skills/tc-render/publish.py`(render 复刻 renderShell + 硬校验复刻 zod + 命门A 内联发布 + 自检 attachments)。CSS 单源 `assets/style.css`(1775B)。4 个 RPI skill(tc-2-research/tc-3-plan/tc-5-review/tc-handoff)调它。
2. **命门(内联渲染发布)= agent raw HTTP(命门A)默认 + CLI `--inline`(命门B)收口**:
   - 命门A:upload-file 带 `issue_id` + `X-Workspace-ID` → raw POST `/api/issues/{id}/comments` 带 `!file` + `attachment_ids`。**真信号 = 返回评论 attachments 非空**(非 url 形态)。
   - 命门B:`multica issue comment add --inline <doc.html>`(feibo-ai fork v0.4.11+)。
3. **低频工具 → CLI 命令 / skill 调原语 / tc-ops 脚本**:`skill_lint`→`multica skill lint`;skill 自更→`multica skill pull`(registry→本地含脚本);`plan_approve`/`case_review`→skill 调 `multica issue label/status/get`;`project_kickoff`→tc-1-start;`case_promote_rule`→tc-5-review 手动追加 CLAUDE.md;`monthly_health_report`/`autopilot_lint`→`tc-ops/*.py`。
4. **单一真相 + 分发**:渲染逻辑单源在 repo `skills/tc-render/`;registry 经 `multica skill update` + `skill files upsert` 存完整 skill(含脚本);团队 `multica skill pull --all` 取全。
5. **Codex 侧**:`~/.codex/AGENTS.md`(= 团队全局 CLAUDE.md 同物理文件)加 1 行中性指针指向 tc-render,不内联多步(防污染每个 Claude session)。

## Consequences

- ✅ Claude 侧日常 RPI **零 local MCP 调用**(实测闭环:research→plan→case→handoff 经 publish.py 全绑定,grep 零 `mcp__tcmcp-local__*`)。
- ✅ 净损失(原 zod 硬约束:goal≥10 / criteria≥1 / keyJudgments≥1 / section4≥100 / handoff confirmDiscard+<60s / projectId 完整UUID)**复刻为 publish.py 脚本 exit 1 硬挡**,强度不降。
- ✅ 版本无关:逻辑在 repo(skill 脚本)+ CLI(Go 发版),两端共享,registry 分发。
- ⚠️ **本地 MCP @tcmcp/local 整包 + 两端 local 注册:迭代2 删除(不可逆 · 硬前置 = 全员 update 到含三新命令的 CLI + `skill pull --all` + Codex 零 local 闭环硬验)。本期(迭代1)保留作兜底。**
- ⚠️ `notify_team` / `betting_table_capture` 等 = **@tcmcp/remote**(Zeabur 公网),**保留**,不在删除范围。
- 📌 边界澄清:删除范围 = 本地 MCP(@tcmcp/local · team-context-mcp 仓 local 包);remote MCP 与控制面保留。

## 反对过的死路(别再走)

- local 改 HTTP transport / local 远程化 / doc_publish 纯 CLI 单命令复现内联渲染 —— 均已证不行(见 research TEA-78 r2)。
- `multica issue comment add --attachment <url>` 发内联 —— CLI 拒 url 形 attachment;attachment_ids 非用户 flag。命门B 的 `--inline` 才是 CLI 路径。
