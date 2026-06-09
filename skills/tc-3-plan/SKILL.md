---
name: tc-3-plan
description: "Use when entering Plan phase of RPI framework — after Research is done. Triggers: 'write a plan', 'let us plan', '做个 plan', 'Plan session', user invokes Phase 01 step 3. Generates a plan doc (HTML) with the 4 mandatory SOP v0.4 fields (goal / completion criteria / who does what / appetite). Differs by layer: project plans get a full plan doc, task plans get a 3-sentence mini-plan. Required for SOP non-negotiable #1 (Plan Mode — never vibe code)."
---

# RPI · Plan Session

## Mandate
Produce a plan that is reviewable, refinable, and persistent. The plan
is the contract — between humans, between sessions, between Claude
instances.

## Discrete session
This is a fresh session with NO Research conversation context. Read
`docs/research/research_<date>_<topic>.html` as input. Re-read it. Do not
trust conversational memory.

## The 4 mandatory fields (SOP v0.4)

### 1. Goal
Specific, verifiable. Not "do better".
- ✅ "Reduce p99 latency on /api/feed from 800ms to <400ms"
- ❌ "Make the feed faster"

### 2. Completion criteria
Observable signals, not "done when good".
- ✅ "Three consecutive prod runs show p99 <400ms for 24h"
- ❌ "Performance is acceptable"

### 3. How to split (who does what)
- Project layer: DRI + EXEC list + COLLAB invites + REVIEW assignment
- Task layer: just you (default DRI)

### 4. Time box (appetite — Shape Up style)
- Project: days / week / month (not estimate)
- Task: hour count

## Template — project layer

```markdown
# Plan: <topic>

**Created:** YYYY-MM-DD
**DRI:** <name>
**Layer:** project

## Goal
<specific, verifiable>

## Completion criteria
- [ ] Signal 1: ...
- [ ] Signal 2: ...

## How to split
- DRI: <name>
- EXEC: <names>
- COLLAB: <names + scope>
- REVIEW: <second Claude session or person>

## Appetite
<days / week / month>

## Research input
docs/research/research_YYYY-MM-DD_<topic>.html

## Approach
<3-10 paragraphs explaining the chosen direction>

## Review
- Reviewer: <agent or person>
- Reviewed: <YYYY-MM-DD>
- Verdict: pending / approved / changes-requested

## Current State (handoff slot — see tc-handoff skill)
(empty until first handoff)
```

## Template — task layer (3 sentences minimum)

```markdown
# Plan: <short topic>

**Layer:** task
**What:** <1 sentence>
**Done when:** <1 sentence>
**Boundary:** <what is out of scope, 1 sentence>
```

## 产出与发布(经 tc-render · 不再走 plan_create MCP)

产出是 HTML,作为 issue **评论**内联渲染(append-only),走共享地基 **tc-render**(`~/.claude/skills/tc-render/`):

1. **选定项目**:`multica project list --full-id` 取**完整 UUID** 作 projectId(8 位短 ID 报 400;**拿不准就问用户**:对不对?要不要 `multica project create` 新建?)。绝不建无项目的孤儿 issue。(rule #6)
2. **建/定位 plan issue**:`multica issue create --project <UUID> --title "计划:<slug>" [--parent <research-issue-id>]`(取回 issue id 完整 UUID)。
3. **产出 HTML**:填 `tc-render/templates/plan.html`(占位 + 两处动态注入:文件名日期、空列表→`(无)`),存本地 `docs/plans/plan_<YYYY-MM-DD>_<slug>.html`(git/离线副本)。
4. **发布**:照 `tc-render/PUBLISH.md` 命门A(upload 带 issue_id + X-Workspace-ID → raw POST 评论带 `!file` + attachment_ids)。成功真信号 = 返回评论 `attachments` 非空。
5. **更新(原 plan_upgrade 行为)**:用命门A **再发一条新评论**(文件名 `_v2`/`_v3`…),永不改附件、永不改 issue 描述(CLI 也传不回附件)。

> **护栏(原 plan_create zod 约束 · 迁移后无 zod 兜底,须自检 · 对抗验收非 grep)**:
> ① **goal ≥10 字符**且具体可验(非「做得更好」);② **完成标准 ≥1 条**,每条非空且可观测;③ projectId 用**完整 UUID**(rule #6)。任一不满足 → 不产出、不发布,回去补。

## Review gate (non-negotiable)

Before writing ANY code, the plan must be reviewed by a SECOND session
with role = staff engineer. NEVER let the same session that wrote the
plan also execute it.

For project plans: REVIEW agent gives explicit approval recorded in the
plan's "## Review" section.

For task plans: 3-sentence plan can self-approve, but state it out loud
before coding.

## Anti-patterns
- ❌ Write plan and immediately start coding (skipped review)
- ❌ Skip the 4 fields ("I know the goal in my head")
- ❌ Vague "as needed" instead of explicit completion criteria
- ❌ Mix Research and Plan in same session

## Hand-off to Implement
Plan reviewed and approved → invoke tc-handoff → `/clear` → open Implement
session with the plan doc (HTML) as primary input.
