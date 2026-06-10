---
name: tc-4-build
description: "Use during Implement phase of RPI framework — when actually writing or running code against an approved plan. Triggers: user enters execution session, '执行', 'implement', 'start coding', or you are in a Claude Code session with an approved plan doc (HTML) loaded. Enforces 30-second CoT supervision, ESC patterns, pollution signal detection, and the discipline checklist that prevents vibe code. Pairs with tc-handoff skill on context pollution."
owner: 曾振华
last_reviewed_at: 2026-06-10
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
- [ ] **项目层:work issue 带 `设计-已审`**(设计评审门已过 · 见 tc-design-review;
      任务层可跳;`设计-待审` 在场 = 评审中,不得开工,build-start 会告警)
- [ ] You can name goal and completion criteria back without rereading
- [ ] You can name what is IN scope and what is OUT of scope

Any No → stop. invoke tc-handoff → `/clear` → go back to Plan.

## 开工:状态转换 + 广播(任务开工卡)
Pre-flight 全过、写第一行代码**之前**:

1. **开工状态转换(与开工卡同时机 · 幂等,续作 session 重跑无害)**:
   ```bash
   python3 ~/.claude/skills/tc-render/transition.py build-start <plan-issue>
   ```
   plan issue `todo`(批准后的待启动)→ `in_progress`。**这是 in_progress 的唯一设置点**
   ——批准时不设(见 tc-3-plan「批准 ≠ 开工」),daily-kickoff「进行中/待启动」两桶依赖此语义。

2. **发「任务开工」卡**到团队飞书群(骨架与纪律见 standards/feishu-card-style.md §2/§3 · header=`blue`):
   - 标题: `任务开工 · <任务短名> · MM-DD`
   - 概览 fields: DRI / 体量 / 计划(TEA-xx + 已批准) / 分支
   - 内容段:「目标」一句话
   - note 页脚: `build session 已开工 · 完成后有复盘 · 进度看 TEA-xx`
   `notify_team({ card: ... })` 发送。
   仅**该计划的首个** build session 发;handoff/`/clear` 后重启的续作 session 不重发。

## 子 agent 杠杆(测试/验证 = 独立 session)
SOP 里「另开 session 验证」类工作(跑测试矩阵、独立复算、red-team 自查)默认派
**子 agent**承担——全新上下文天然独立,不污染本 session。规则:子 agent 只产出
结论/verdict,**状态转换与 commit 权始终归本(编排)session**;verdict 返回点即动作点。

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
