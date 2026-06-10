---
name: tc-friday
description: "Use Friday afternoon for the 30-min demo + 15-min betting table double-session. Triggers '周五 demo', 'Friday demo', 'betting table', '周五演示', '下周做什么'. Guides DRI through demo (real artifacts not slides) + betting (decide next week's work, NO backlog). Pairs with `betting_table_capture`(**remote** MCP · 非本地,本期保留)."
owner: 曾振华
last_reviewed_at: 2026-06-10
---

# Friday Demo + Betting Table — 45-min protocol

## Pre-flight (DRI does, 1 hr before)
Query cases awaiting debrief review (label 即真值,不附加 status 条件——按状态机语义,
待审 case 的 status 是 `in_review`,审完才 `done`,旧查询 `--status done --label 复盘-待审`
是永空集):
`multica issue list --label 复盘-待审`

For each: identify demo-worthy artifact (deployed feature, completed migration, working prototype).
评审通过的 case 当场收尾:`python3 ~/.claude/skills/tc-render/transition.py case-finalize <case-issue>`
(phase case 加 `--keep-parent`;连带关闭其父 plan)。

## Demo · 30 min (celebrate, don't report)

### 0-25 min — Demos
3-5 demos. Each ~5 min. Format:
- 30 sec what
- 3 min **show the actual thing working** (live, not slides)
- 1 min what we learned
- 30 sec ovation

NEVER: PowerPoint, screenshots, status update.

### 25-30 min — Celebrate
Real food/drink ideally. Mark week as done.

## Betting Table · 15 min (decide next week)

### Setup
Use `betting_table_capture`(remote MCP):
1. Anyone propose ≤ 5 candidates (1 sentence each)
2. 5 min silent thinking
3. Each person votes for ≤ 3 candidates
4. Top vote-getters become next week's plan-candidates
5. **All un-voted candidates are DROPPED** — NOT added to backlog

## What this protocol enforces
- Demo is CELEBRATION, not reporting
- Betting replaces "backlog grooming" (Shape Up principle)
- "Important things will re-surface" — un-voted = wasn't urgent

## Anti-patterns
- ❌ Demo becomes status update or roadmap presentation
- ❌ Move un-voted betting candidates to backlog "for later"
- ❌ Skip Friday slot when nothing shipped (do "what we learned" instead — but don't skip)
