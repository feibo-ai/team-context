---
name: pre-clear
description: "Use BEFORE running /clear, starting a new Claude/Codex session, or whenever user signals context restart ('I am stuck', '走偏了', '换个 session', '重开', 'start over', 'restart', '浑浊了', 'new session', '/clear'). Captures handoff state to plan markdown and commits WIP so the new session can resume without losing work or repeating dead ends. Required for AI MIQ SOP v0.4 P-2 / P-4 / Daily 02 / Daily 03 compliance."
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
- **commit** — `git add -A && git commit -m "wip: <one-line state>"` —
  default for any meaningful work
- **stash** — `git stash push -m "wip: <one-line>"` — when not sure it's
  worth keeping but might want it back
- **discard** — `git checkout .` — ONLY with explicit user confirmation,
  never default

### 3. Locate active plan markdown
Look in `docs/plans/` for the file with most recent mtime matching this
work. If multiple plans or none, ask.

### 4. Update plan markdown — append or replace this section

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

### 5. Optional — post to multica issue
If this work is tracked in a multica issue, post the same Current State
block as a comment:
`multica issue comment --issue <id> --body-file <path>`

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
Often, what is needed is a 2-minute plan markdown rewrite, not a restart.
Ask: would a sharper plan section save this session?
