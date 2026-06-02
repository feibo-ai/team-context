---
name: tc-1-start
description: "Use when starting a new PROJECT-LAYER effort. Triggers '启动新项目', 'kickoff', 'new project', 'phase 01', 'Phase 01 启动', '我想做一个新项目'. Walks through SOP v0.4 P-3 Phase 01 6-step in order: 5min intent → Research → Plan → review → DRI 拍板 → broadcast. Pairs with project_kickoff MCP tool."
---

# Phase 01 Kickoff — 6-step Wizard

## Pre-check: is this really project-layer?
Test: would you call this 'an independent big direction' (3+ days, has DRI, deserves a debrief at the end)?
- YES → continue
- NO → task-layer, use task-mode plan_create with 3-sentence plan instead

## The 6 steps (run in order)

### Step 1 — 5-minute intent statement
Post to team feishu: "I'm thinking about starting [X], because [Y]."
Goal: let the team know, NOT commit. No formal plan yet.

### Step 2 — Research session (fresh session)
INVOKE tc-2-research skill. Output: docs/research/research_<date>_<topic>.html. project_kickoff creates the research issue + a LOCAL skeleton only (no upload); after findings are filled, publish them with `doc_publish` (a comment · `!file` inline render). Never update an attachment / rewrite the description.
Critical: SEPARATE session from Step 3.

### Step 3 — Plan session (yet another fresh session)
INVOKE tc-3-plan skill. Read research file as input. Output: docs/plans/plan_<date>_<topic>.html with all 4 mandatory fields (posted as a comment on the plan issue · `!file` inline render · updates via plan_upgrade = a new comment).
Or call MCP `plan_create` for skeleton.

> ⚠️ **每个 issue 必须挂项目**:`project_kickoff` 会自己建 project 并把 issue 挂好;若手动用 `research_create` / `plan_create`,必须先 `multica project list` 选定 `projectId`(必填),拿不准问用户(对不对?要不要新建?)。(team-global rule #6)

### Step 4 — Review by second session
Spawn NEW session with role = staff engineer. Hand it the plan. Wait for verdict.
Or call MCP `plan_request_review` — labels issue `计划-评审中`.

### Step 5 — DRI 拍板
DRI reads review verdict. Final call: proceed / revise / kill.
If proceed: call MCP `plan_approve` → issue gets `计划-已批准` label. SOP non-negotiable #1 gate.

### Step 6 — Broadcast
Post to feishu: "Starting [project]. Plan: [link]. DRI: [me]. Appetite: [X]." Tag the team.
24h default tacit approval.

## ⚠️ project_kickoff 是脚手架,不替代真做 — 真验证 (SOP P-7)
`project_kickoff` MCP 工具是快捷方式:它建 project + research/plan issue + 文件 stub。但它**不替代真做**:
- research/plan stub 是**空文件** —— 真调研 / 规划仍要各开 fresh session 跑 `tc-2-research`(Step 2)/ `tc-3-plan`(Step 3)深度填充。
- 它**不发** Step 1 / Step 6 的 `notify_team` 广播 —— 那两条要你**手动**调 `notify_team`。
- **工具返回 success ≠ 做对了。** kickoff 后必须**真验证产物**(SOP P-7),逐项查:
  - issue 真挂到了 project 上?
  - research issue 真的在?
  - 飞书群真收到 Step 1 / Step 6 广播?
- 📌 2026-05-29 实测:上面这三处**都曾静默失败**(工具返回成功 · 产物却没到位)。

## Hand-off
After all 6: invoke tc-handoff → /clear → start Implementation per tc-4-build skill.

## Anti-patterns
- ❌ Skip Step 1 (everyone surprised in Step 6)
- ❌ Combine Research and Plan in one session
- ❌ Self-review (Step 4 must be DIFFERENT session)
- ❌ Treat Step 5 as bureaucracy (only step needing human focused thought)
- ❌ Skip Step 6 because "everyone knows" (broadcast needed for 24h tacit approval)
