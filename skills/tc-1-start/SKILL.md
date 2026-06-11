---
name: tc-1-start
description: "Use when starting a new PROJECT-LAYER effort. Triggers '启动新项目', 'kickoff', 'new project', 'phase 01', 'Phase 01 启动', '我想做一个新项目'. Walks through SOP v0.4 P-3 Phase 01 6-step in order: 5min intent → Research → Plan → review → DRI 拍板 → broadcast. 去本地MCP:用 multica CLI(project/issue create + label/status)+ tc-render/publish.py 手动编排,不再依赖 project_kickoff MCP。"
owner: 曾振华
last_reviewed_at: 2026-06-11
---

# Phase 01 Kickoff — 6-step Wizard

## Pre-check: is this really project-layer?
Test: would you call this 'an independent big direction' (3+ days, has DRI, deserves a debrief at the end)?
- YES → continue
- NO → task-layer,用 tc-3-plan 的 task-mode(3 句话 mini-plan)即可,不必走 Phase 01

## The 6 steps (run in order)

### Step 1 — 5-minute intent statement
发到团队飞书群,**纯文本**模版(刻意比卡片轻 · 规范 standards/feishu-card-style.md §5):
```
notify_team({ text: "【意向】<人名>:想做 <X>,因为 <Y>。仅通气、非承诺,有想法直接回。" })
```
Goal: let the team know, NOT commit. No formal plan yet.

### Step 2 — Research session (fresh session)
INVOKE tc-2-research skill. Output: docs/research/research_<date>_<topic>.html。建 research issue 用 `multica issue create --project <UUID> --title "研究:<topic>" --assignee "$ME_NAME"`(当前用户运行时解析,不问 · standards/multica-fields.md);本地骨架 + 填充后发布走 `tc-render/publish.py --type research`(命门B 内联渲染评论 + 自动 `研究` label;findings 非空即 status `done`,research issue 不挂账)。Never update an attachment / rewrite the description.
Critical: SEPARATE session from Step 3.

### Step 3 — Plan session (yet another fresh session)
INVOKE tc-3-plan skill. Read research file as input. Output: docs/plans/plan_<date>_<topic>.html with all 4 mandatory fields。建 plan issue 用 `multica issue create --project <UUID> --parent <research-issue> --assignee "$ME_NAME"`;产出 + 发布(含更新 = append-only 新评论)走 `tc-render/publish.py --type plan`(硬校验 goal≥10/criteria≥1)。

> ⚠️ **每个 issue 必须挂项目**:先 `multica project list --full-id` 选定**完整 UUID** projectId(必填),拿不准问用户(对不对?要不要 `multica project create` 新建?)。绝不建孤儿 issue。(team-global rule #6)
> 字段默认值(**不问自动填** · 单源 standards/multica-fields.md):新建 project 带 `--dri "$ME_UID" --lead "$ME_NAME"`;建 issue 带 `--assignee "$ME_NAME"`;当前用户经 `multica auth status`+`user list` 运行时解析,绝不硬编码;priority/due-date 留空。

### Step 4 — Review by second session(= 评审子 agent)
先做请审转换:`python3 ~/.claude/skills/tc-render/transition.py plan-request-review <plan-issue>`
(+`计划-评审中` · status `in_review`)。
再派评审**子 agent**(role = staff engineer · 全新上下文 = 天然独立 session):只给 plan
HTML + research 输入,要求输出 `VERDICT: approved | changes-requested`。Wait for verdict.

### Step 5 — DRI 拍板(verdict 返回点 = 转换执行点,本 session 当场执行)
DRI reads review verdict. Final call: proceed / revise / kill.
- proceed → `python3 ~/.claude/skills/tc-render/transition.py plan-approve <plan-issue>`
  (+已批准 · −草稿/评审中/已升级 · status **todo** 待启动;开工时才 in_progress,见 tc-4-build)。SOP non-negotiable #1 gate.
- revise → 修订后 publish.py 再发一版(append-only),回 Step 4 重审。
- kill → `python3 ~/.claude/skills/tc-render/transition.py cancel <plan-issue>`
  (status cancelled + 清全部流程 label,不留漂移尸体)。

### Step 6 — Broadcast
发「项目开工」卡到团队飞书群(骨架与纪律见 standards/feishu-card-style.md §2/§3 · header=`turquoise`):
- 标题: `项目开工 · <项目短名> · MM-DD`
- 概览 fields: DRI / 体量 / 计划(TEA-xx + 已批准) / 评审(独立 session 通过)
- 内容段:「目标」一句话;「完成标准」▸ 前 2 条,其余收「…其余 N 条见计划 issue」
- note 页脚: `24 小时默许窗口 · 有异议群里提 · 计划全文见 TEA-xx`
`notify_team({ card: ... })` 发送;24h default tacit approval。

## ⚠️ kickoff 是手动编排,不是一个工具 — 真验证 (SOP P-7)
没有 `project_kickoff` 单一工具了:kickoff = 你按 6 步手动用 `multica project/issue create` + `tc-render/publish.py` 编排。所以**每步产物都要真验证**(SOP P-7):
- research/plan 骨架是**空的** —— 真调研 / 规划仍要各开 fresh session 跑 `tc-2-research`(Step 2)/ `tc-3-plan`(Step 3)深度填充。
- Step 1 / Step 6 广播要**手动**发(`notify_team` 走 **remote** MCP,非本地 —— 本期删的是本地 MCP)。
- **CLI 返回 success ≠ 做对了。** 逐项查:issue 真挂到 project?research/plan issue 真在?评论真内联渲染(返回 `attachments` 非空)?飞书真收到 Step 1/6 广播?
- 📌 旧实测:这些都曾静默失败(返回成功 · 产物没到位)。

## Hand-off
After all 6: invoke tc-handoff → /clear → start Implementation per tc-4-build skill.

## Anti-patterns
- ❌ Skip Step 1 (everyone surprised in Step 6)
- ❌ Combine Research and Plan in one session
- ❌ Self-review (Step 4 must be DIFFERENT session)
- ❌ Treat Step 5 as bureaucracy (only step needing human focused thought)
- ❌ Skip Step 6 because "everyone knows" (broadcast needed for 24h tacit approval)
