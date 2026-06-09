---
name: tc-2-research
description: "Use when entering Research phase of the RPI framework — before any plan or code work on a project-layer goal. Triggers: 'start research', 'let us understand', '调研', '研究一下', 'Research session', user explicitly invokes Phase 01 step 2. Orchestrates parallel subagent research with context budget discipline. Output: a local skeleton at docs/research/research_YYYY-MM-DD_topic.html; filled findings are published as an issue COMMENT via tc-render 命门A (upload-file with issue_id + raw POST comment with !file + attachment_ids) — never auto-uploaded to the description. Required for SOP v0.4 P-3 Phase 01."
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

> **文档怎么进 issue(经 tc-render · 不再走 research_create / doc_publish MCP · append-only 评论制)**:
> 1. **选定项目** `multica project list --full-id` 取**完整 UUID**(拿不准问用户/或 `multica project create`);绝不建孤儿 issue(rule #6)。
> 2. **建研究 issue** `multica issue create --project <UUID> --title "研究:<topic>"`。
> 3. **本地骨架** 填 `tc-render/templates/research.html`(Findings 先填字面「(待 fresh session 深度调研填充)」),存 `docs/research/research_<YYYY-MM-DD>_<topic>.html`,**此刻不发布**。
> 4. **填发现后发布** 把 findings 填进本地 HTML,照 `tc-render/PUBLISH.md` 命门A(upload 带 issue_id → raw POST 评论带 `!file` + attachment_ids)发为一条**评论**(内联渲染 · 自检 `attachments` 非空)。
> 之后每次更新 = 用命门A **再发一条新评论**(新文件名)。**永不**改附件(CLI 传不回)或把文档塞进 issue 描述 —— 那正是之前卡死的弯路。本地 `docs/research/*.html` 留作 git/离线副本。
> projectId 一律**完整 UUID**(8 位短 ID 报 400 · rule #6)。

## What this session does NOT do
- ❌ Pick a plan (Plan session does)
- ❌ Write code (Implement session does)
- ❌ Make architecture decisions (Plan session does, with research as input)
- ❌ Continue past 40% context (start over with a sharper question)

## Hand-off
When done: invoke tc-handoff skill → `/clear` → open Plan session with
`docs/research/research_<date>_<topic>.html` as primary input.
