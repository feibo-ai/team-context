---
name: tc-3-plan
description: "Use when entering Plan phase of RPI framework — after Research is done. Triggers: 'write a plan', 'let us plan', '做个 plan', 'Plan session', user invokes Phase 01 step 3. Generates a plan doc (HTML) with the 4 mandatory SOP v0.4 fields (goal / completion criteria / who does what / appetite). Differs by layer: project plans get a full plan doc, task plans get a 3-sentence mini-plan. Required for SOP non-negotiable #1 (Plan Mode — never vibe code)."
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

> **Output is HTML, not a hand-written file.** The `plan_create` / `project_kickoff` MCP tool renders these fields to a 方案A HTML doc and posts it as a **comment** on the plan issue (`!file` inline render · append-only). Updates go through `plan_upgrade`, which posts a **new comment** (v2, v3…) — it never mutates an attachment or rewrites the issue description (the CLI can't re-upload an attachment anyway). Local `docs/plans/*.html` is kept for git history / offline reading.

## Review gate (non-negotiable)

Before writing ANY code, the plan must be reviewed by a SECOND session
with role = staff engineer. NEVER let the same session that wrote the
plan also execute it.

For project plans: REVIEW agent gives explicit approval recorded in the
plan's "## Review" section.

For task plans: 3-sentence plan can self-approve, but state it out loud
before coding.

## Anti-patterns
- ❌ Write plan and immediately start coding (skipped review)
- ❌ Skip the 4 fields ("I know the goal in my head")
- ❌ Vague "as needed" instead of explicit completion criteria
- ❌ Mix Research and Plan in same session

## Hand-off to Implement
Plan reviewed and approved → invoke tc-handoff → `/clear` → open Implement
session with the plan doc (HTML) as primary input.
