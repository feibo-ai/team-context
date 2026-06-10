---
name: tc-3-plan
description: "Use when entering Plan phase of RPI framework — after Research is done. Triggers: 'write a plan', 'let us plan', '做个 plan', 'Plan session', user invokes Phase 01 step 3. Generates a plan doc (HTML) with the 4 mandatory SOP v0.4 fields (goal / completion criteria / who does what / appetite). Differs by layer: project plans get a full plan doc, task plans get a 3-sentence mini-plan. Required for SOP non-negotiable #1 (Plan Mode — never vibe code)."
owner: 曾振华
last_reviewed_at: 2026-06-10
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
   脚本**渲染 + 硬校验 + 命门B 发布 + 自检 attachments + 入口状态转换**一步到位(发布成功自动加 `计划-草稿`,仅当 issue 尚无任何 计划-* label;exit 2 = 评论已发但转换失败,按 stderr 补救,**绝不重跑 publish**)。先 `--dry-run` 预览。
4. **更新(原 plan_upgrade)**:换新 `--out` 文件名(`_v2`…)再调一次,append-only;永不改附件、永不改 issue 描述。已批准后实质改方案 → 先 `transition.py plan-upgrade`(摘已批准 · 加已升级+草稿 · 回 todo)再重走评审。

> **硬校验(publish.py 内建 · exit 1 硬挡,不再靠自觉)**:`goal` ≥10 字符、完成标准 ≥1 条、`--issue` 完整 UUID。违约脚本直接报错、发不出,回去补。

## Review gate (non-negotiable)

Before writing ANY code, the plan must be reviewed by a SECOND session
with role = staff engineer. NEVER let the same session that wrote the
plan also execute it.

**「第二个 session」= 评审子 agent(团队成员人手大量 agent,这是默认形态):**
1. **请审转换(plan 写完、派评审之前)**:
   `python3 ~/.claude/skills/tc-render/transition.py plan-request-review <plan-issue>`
   (+`计划-评审中` · status `in_review`;task 层 plan 同样适用)
2. **派评审子 agent**(全新上下文 = 天然满足独立性):role = staff engineer,只给
   plan HTML 路径 + research 输入,**不带实现方对话记忆**;要求输出
   `VERDICT: approved | changes-requested` + blocking/non-blocking 清单 + 事实核查。
3. **verdict 返回点 = 转换执行点(编排 session 立即执行,不留无主窗口)**:
   - approved → 走下方「批准状态转换」;
   - changes-requested → 修订后 `publish.py` 再发一版(append-only),回到第 2 步。
   子 agent 只产出 verdict、不碰状态;转换权始终归编排 session。

For project plans: REVIEW agent gives explicit approval recorded in the
plan's "## Review" section.

For task plans: 3-sentence plan can self-approve, but state it out loud
before coding.

### 批准状态转换(脚本原子收口 · 取代散文 bash 块)
plan 批准时(approved verdict 返回后立即执行):
```bash
python3 ~/.claude/skills/tc-render/transition.py plan-approve <plan-issue>
```
原子做完:+`计划-已批准` · −{`计划-草稿`,`计划-评审中`,`计划-已升级`} · status **`todo`(待启动)**,
并复核后置状态(P-7 真验证)。**批准 ≠ 开工**:`in_progress` 由 build session 开工时
`transition.py build-start` 设置(见 tc-4-build)——daily-kickoff 的「待启动」桶
(`计划-已批准`+`todo`)依赖此语义。
Reviewer / Verdict 写进 plan 的 `approach`/评审字段,用 `publish.py --type plan` 再发一版(append-only)。

## Anti-patterns
- ❌ Write plan and immediately start coding (skipped review)
- ❌ Skip the 4 fields ("I know the goal in my head")
- ❌ Vague "as needed" instead of explicit completion criteria
- ❌ Mix Research and Plan in same session

## Hand-off to Implement
Plan reviewed and approved → invoke tc-handoff → `/clear` → open Implement
session with the plan doc (HTML) as primary input.
