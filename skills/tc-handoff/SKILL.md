---
name: tc-handoff
description: "Use BEFORE running /clear, starting a new Claude/Codex session, or whenever user signals context restart ('I am stuck', '走偏了', '换个 session', '重开', 'start over', 'restart', '浑浊了', 'new session', '/clear'). Captures handoff state to the plan doc (HTML) + the multica issue, and commits WIP so the new session can resume without losing work or repeating dead ends. Required for AI MIQ SOP v0.4 P-2 / P-4 / Daily 02 / Daily 03 compliance."
---

# Pre-Clear Handoff Protocol

You are about to /clear or start a new session. SOP v0.4 makes this the most
common operation — but only safe if state is properly handed off.

## When to invoke
- User says: /clear, new session, start over, restart, 重开, 走偏了, 换 session
- You detect context pollution: "You're absolutely right" loops, repeating
  rejected solutions, answering the wrong question, solving the wrong layer
- 30 minutes elapsed with no measurable progress

## Checklist — execute in order

### 1. Surface what's uncommitted
Run `git status --short`. Report to user.

### 2. Decide WIP fate
Three options — ask user if not obvious:
- **commit** — 显式暂存本次相关文件 `git add <具体路径>`,再 `git commit -m "wip: <one-line state>"` —
  default for any meaningful work. **绝不 `git add -A`**:工作树常有别项目/别人未提交文件(本仓即如此),`-A` 会一并裹挟;先 `git status --short` 看清再按路径 add。
- **stash** — `git stash push -m "wip: <one-line>" -- <具体路径>` — when not sure it's
  worth keeping but might want it back
- **discard** — `git checkout -- <具体路径>` — **ONLY with explicit user confirmation(confirmDiscard 门:discard 前必须用户显式点头),never default**;别用裸 `git checkout .`(会连带别项目改动一起丢)

### 3. Locate active plan doc
Look in `docs/plans/` for the .html file with most recent mtime matching this
work. If multiple plans or none, ask.

### 4. Capture the Current State block

    ## Current State (handoff @ <YYYY-MM-DD HH:MM>)

    **Last commit**: <hash> <subject>
    **Worktree**: <branch>, <N> file(s) changed since last commit

    **What's done**:
    - <1-3 specific bullets>

    **Next action** (concrete enough for a fresh session to start cold):
    - <1-3 sentences, naming files/functions if applicable>

    **Dead ends — do NOT retry**:
    - <approach tried + why it failed>
    - ...

    **Context pollution signal** (why we are clearing):
    - <one sentence>

### 5. Persist to the multica issue(经 tc-render 命门A · 不再走 session_handoff MCP)
If this work is tracked in a multica issue:
- **防重复 handoff(原 session_handoff <60s 幂等门 · 净损失须复刻)**:先查当期 plan / issue 是否已有 `handoff @ YYYY-MM-DD HH:MM` 标记且在 **<60 秒**前 —— 若是,**拒绝重复 handoff**(提示 `last handoff <N>s ago — refusing duplicate within 60s`),不重发,直接进第 6 步。
- **Current State 评论**:把上面的 Current State 块发为一条评论。快捷=纯 markdown:`multica issue comment add <id> --content-file <path>`;或要内联渲染=把 `{slug, at, lastCommit, branch, done, nextAction, deadEnds, pollutionSignal}` 写成 `fields.json`,调 `python3 ~/.claude/skills/tc-render/publish.py --type handoff --data fields.json --issue <id>`(渲染 + 命门A + 自检 attachments)。
- **plan 同步(原 session_handoff 重生成 plan 行为 · 可选)**:把这次 handoff 快照并进当期 plan 的 `approach`/末尾,用 `publish.py --type plan` **再发一条新 plan 评论**(append-only · 旧版本留存 · 演化可追溯),让 plan doc 也带最新交接状态。`--issue` 一律完整 UUID。

### 6. Final confirmation
Show user the updated plan + commit hash + (if posted) multica comment URL.
Only then proceed to actual /clear.

## Anti-patterns

- ❌ /clear with uncommitted meaningful changes (new session may rewrite)
- ❌ Skip "Dead ends" (new session repeats same mistakes — costs 2× time)
- ❌ Vague next action ("continue the work") — must name files/functions
- ❌ Touch CLAUDE.md here (CLAUDE.md changes go through monthly review)
- ❌ Run this AFTER /clear (too late — state already lost)

## Escalation signals

If git log shows you've handed off **3+ times on the same issue**:
this is no longer a task-layer problem — upgrade to greenfield playbook
(PB1), re-do Research session, re-Plan from scratch.

If user has done this **5+ times this week**:
mention it. Monthly burnout-check signal — `multica issue runs <id>` will
show the pattern.

## Cost reminder
Each /clear ≈ 30-60s priming + lost prompt cache. Sometimes worth it.
Often, what is needed is a 2-minute plan doc rewrite, not a restart.
Ask: would a sharper plan section save this session?
