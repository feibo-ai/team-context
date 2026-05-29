---
name: phase-01-kickoff
description: "Use when starting a new PROJECT-LAYER effort. Triggers '启动新项目', 'kickoff', 'new project', 'phase 01', 'Phase 01 启动', '我想做一个新项目'. Walks through SOP v0.4 P-3 Phase 01 6-step in order: 5min intent → Research → Plan → review → DRI 拍板 → broadcast. Pairs with project_kickoff MCP tool."
---

# Phase 01 Kickoff — 6-step Wizard

## Pre-check: is this really project-layer?
Test: would you call this 'an independent big direction' (3+ days, has DRI, deserves a debrief at the end)?
- YES → continue
- NO → task-layer, use task-mode plan_create with 3-sentence plan instead

## The 6 steps (run in order)

### Step 1 — 5-minute intent statement
Post to team feishu: "I'm thinking about starting [X], because [Y]."
Goal: let the team know, NOT commit. No formal plan yet.

### Step 2 — Research session (fresh session)
INVOKE rpi-research skill. Output: docs/research/research_<date>_<topic>.md.
Critical: SEPARATE session from Step 3.

### Step 3 — Plan session (yet another fresh session)
INVOKE rpi-plan-template skill. Read research file as input. Output: docs/plans/plan_<date>_<topic>.md with all 4 mandatory fields.
Or call MCP `plan_create` for skeleton.

### Step 4 — Review by second session
Spawn NEW session with role = staff engineer. Hand it the plan. Wait for verdict.
Or call MCP `plan_request_review` — labels issue `计划-评审中`.

### Step 5 — DRI 拍板
DRI reads review verdict. Final call: proceed / revise / kill.
If proceed: call MCP `plan_approve` → issue gets `计划-已批准` label. SOP non-negotiable #1 gate.

### Step 6 — Broadcast
Post to feishu: "Starting [project]. Plan: [link]. DRI: [me]. Appetite: [X]." Tag the team.
24h default tacit approval.

## Hand-off
After all 6: invoke pre-clear → /clear → start Implementation per rpi-implement-discipline skill.

## Anti-patterns
- ❌ Skip Step 1 (everyone surprised in Step 6)
- ❌ Combine Research and Plan in one session
- ❌ Self-review (Step 4 must be DIFFERENT session)
- ❌ Treat Step 5 as bureaucracy (only step needing human focused thought)
- ❌ Skip Step 6 because "everyone knows" (broadcast needed for 24h tacit approval)
