---
name: rpi-research
description: "Use when entering Research phase of the RPI framework — before any plan or code work on a project-layer goal. Triggers: 'start research', 'let us understand', '调研', '研究一下', 'Research session', user explicitly invokes Phase 01 step 2. Orchestrates parallel subagent research with context budget discipline. Output goes to docs/research/research_YYYY-MM-DD_topic.md. Required for SOP v0.4 P-3 Phase 01."
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
- Output target: a section in docs/research/research_<date>_<topic>.md
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
docs/research/research_YYYY-MM-DD_<topic>.md

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

## What this session does NOT do
- ❌ Pick a plan (Plan session does)
- ❌ Write code (Implement session does)
- ❌ Make architecture decisions (Plan session does, with research as input)
- ❌ Continue past 40% context (start over with a sharper question)

## Hand-off
When done: invoke pre-clear skill → `/clear` → open Plan session with
`docs/research/research_<date>_<topic>.md` as primary input.
