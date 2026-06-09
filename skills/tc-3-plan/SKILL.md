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
3. **产出+发布(一步 · 调脚本)**:把字段写成 `fields.json`(`goal` / `completionCriteria` / `dri` / `layer` / `exec` / `collab` / `reviewer` / `appetite` / `approach` / `slug`),调:
   `python3 ~/.claude/skills/tc-render/publish.py --type plan --data fields.json --issue <issue-UUID> --out docs/plans/plan_<YYYY-MM-DD>_<slug>.html`
   脚本**渲染 + 硬校验 + 命门A 发布 + 自检 attachments** 一步到位,成功打印 `comment_id`/`url`。先 `--dry-run` 预览。
4. **更新(原 plan_upgrade)**:换新 `--out` 文件名(`_v2`…)再调一次,append-only;永不改附件、永不改 issue 描述。

> **硬校验(publish.py 内建 · exit 1 硬挡,不再靠自觉)**:`goal` ≥10 字符、完成标准 ≥1 条、`--issue` 完整 UUID。违约脚本直接报错、发不出,回去补。

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
