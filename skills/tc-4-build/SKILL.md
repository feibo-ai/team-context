---
name: tc-4-build
description: "Use during Implement phase of RPI framework — when actually writing or running code against an approved plan. Triggers: user enters execution session, '执行', 'implement', 'start coding', or you are in a Claude Code session with an approved plan doc (HTML) loaded. Enforces 30-second CoT supervision, ESC patterns, pollution signal detection, and the discipline checklist that prevents vibe code. Pairs with tc-handoff skill on context pollution."
---

# RPI · Implement Session

## Mandate
Execute the plan exactly. NEVER re-plan, re-research, or re-decide in
this session. If something feels wrong, invoke tc-handoff and go back
to Plan session.

## Pre-flight check
Confirm before first code action:
- [ ] Plan doc (HTML) is loaded and READ in this session
- [ ] Plan has an "approved" marker OR 3-sentence task plan was reviewed
- [ ] You can name goal and completion criteria back without rereading
- [ ] You can name what is IN scope and what is OUT of scope

Any No → stop. invoke tc-handoff → `/clear` → go back to Plan.

## 30-second rule
First 30s of every Claude tool-call sequence: read the chain-of-thought.
If direction is wrong, hit ESC. Do NOT let it continue down a wrong path
"to see how it does."

## Pollution signals (immediate tc-handoff)
- "You're absolutely right" — model is in agreement-loop, not thinking
- Re-proposes a solution you already rejected
- Answers a question you did not ask
- Talks about "the issue from before" when there is none

When any signal hits: invoke tc-handoff skill, do not try to "redirect".

## Sanity rule (do not skip)
For every code change AI makes, a human eye must see the diff before
commit. Applies to multi-agent runs, overnight runs, batch runs — all of
them. SOP "AI generated but YOU ship it" liability.

## Commit rhythm
- Commit at every green-test boundary (TDD-aligned)
- Never go more than 30 minutes without commit (so tc-handoff is cheap)
- Commit messages reference plan section (e.g. "feat: criterion 2 — p99 <400ms")

## Stuck-30 rule
If 30 minutes elapsed with no test passing / no progress: invoke tc-handoff
and start over. Do NOT keep trying. SOP P-4 "start over beats fix".

## 3-strike rule
If you have /clear'd 3 times on the same task: this is no longer task-
layer. Upgrade to greenfield playbook (PB1) — re-Research, re-Plan from
scratch.

## What this session does NOT do
- ❌ Change the plan (re-open Plan session if plan is wrong)
- ❌ Add scope beyond plan
- ❌ "Make it better while you're at it" (separate plan)
- ❌ Skip Sanity rule "just this once"

## Hand-off to Debrief
All completion criteria met + tests green + diff reviewed + push →
invoke tc-5-review skill.
