---
name: tc-2-research
description: "Use when entering Research phase of the RPI framework — before any plan or code work on a project-layer goal. Triggers: 'start research', 'let us understand', '调研', '研究一下', 'Research session', user explicitly invokes Phase 01 step 2. Orchestrates parallel subagent research with context budget discipline. Output goes to docs/research/research_YYYY-MM-DD_topic.html (auto-uploaded to the issue · renders inline). Required for SOP v0.4 P-3 Phase 01."
---

# RPI · Research Session

## Mandate
Map the territory BEFORE planning. NEVER make planning decisions in this
session — that is Plan session's job. Discrete sessions, no overlap.

## Entry criteria
- This is project-layer (independent big direction), not task-layer
- A new feature, new project, or unfamiliar problem domain
- You do not yet know the unknowns

## First question (mandatory)
**"Is this within AI's capability frontier?"**
If yes → proceed. If no/unsure → flag to DRI, do not push through.
Reason: SOP ❌6 anti-pattern (using AI beyond frontier raises error rate
by 19 percentage points — BCG 2024).

## Parallel subagent dispatch pattern

Spawn 2-4 independent subagents simultaneously. Each gets:
- Specific scope: one dimension to research
- Output target: a section in docs/research/research_<date>_<topic>.html
- Constraint: report findings, do not propose a solution

Common dimension sets:
- Existing codebase: what is already there, where, how organized
- Industry / prior art: what others have done; key papers, repos, docs
- Pitfalls: known failure modes, foot-guns, gotchas
- Constraints: team SOP, security, compliance, legal

## Context budget
Stop Research when YOUR context is at 30-40% used. Past that, the Plan
session that consumes your output cannot hold its findings cleanly either.
Subagents are separate — have them write to disk, you read summaries.

## Output

```
docs/research/research_YYYY-MM-DD_<topic>.html

# Research: <topic>

## Question
<one paragraph: what we are trying to understand>

## Findings (per dimension)

### Existing codebase
- ...

### Prior art
- ...

### Pitfalls
- ...

### Constraints
- ...

## Open questions
<things research could not answer — must be resolved before Plan>

## Recommended approaches (options, not decisions)
1. ...
2. ...
3. ...
```

> **文档怎么进 issue(append-only · 评论制)**:`research_create` 只建 issue + **本地骨架** HTML(`docs/research/*.html`),**不上传**(此刻还没发现)。把发现填进本地 HTML 后,用 **`doc_publish`** 工具发布为一条**评论**(`!file` 内联渲染 · 方案A)。
> 之后每次更新 = **再发一条评论**(新文件名)。**永不**「更新附件」(CLI 只能下载,传不回)或把文档内容塞进 issue 描述 —— 那正是之前卡死的弯路。本地 `docs/research/*.html` 仍留作 git / 离线副本。

> ⚠️ **项目归属(必填)**:`research_create` 的 `projectId` 已是必填。建研究 issue 前先 `multica project list` 选定项目;**拿不准就问用户**(是不是这个项目?要不要 `multica project create` 新建?)。绝不建无项目的孤儿 issue。(team-global rule #6)

## What this session does NOT do
- ❌ Pick a plan (Plan session does)
- ❌ Write code (Implement session does)
- ❌ Make architecture decisions (Plan session does, with research as input)
- ❌ Continue past 40% context (start over with a sharper question)

## Hand-off
When done: invoke tc-handoff skill → `/clear` → open Plan session with
`docs/research/research_<date>_<topic>.html` as primary input.
