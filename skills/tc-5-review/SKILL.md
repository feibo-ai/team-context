---
name: tc-5-review
description: "Use when project or task is wrapping up. Triggers: 'let us debrief', '收尾', 'wrap up', '写 case', 'project done', user marks completion criteria met. Generates a case file at cases/YYYY-MM-DD-<slug>.md with the 5 mandatory SOP v0.4 sections. Required for SOP non-negotiable #2 (every project/task ends with debrief)."
---

# Debrief / Case File Template

## Mandate
Document what actually happened, what we learned, what survives forward.
Not a status report. Not "and then we did X, and then Y." A causal chain
of key judgments.

## Filename
- Project: `cases/YYYY-MM-DD-<project-slug>.md`
- Task batch (lightweight): `cases/YYYY-MM-WW-tasks.md` (week-bucketed, append)

## The 5 mandatory sections

### 1. Goal (paste from plan)
Copy the original goal from the plan markdown verbatim.

### 2. What actually happened (≤ 200 words)
Compressed timeline. Not blow-by-blow. Just the structurally important
events. If it does not change the next person's mental model, cut it.

### 3. Completion criteria — met or not?
For each criterion from the plan:
- [x] / [ ] Criterion + observable signal
- If not met: explicit why (scope changed / blocker / etc.)

### 4. Key judgments (this section is the case file's reason to exist)

Not "what we did" but "what we decided, and why."
For each non-obvious decision:

#### Judgment: <one-line>
- **Context:** what was the choice?
- **Options:** what alternatives?
- **Chose:** what / why
- **In hindsight:** was this right? What would you change?
- **"Ancient impossible" check:** would this judgment have been impossible without AI Native?

Aim for 2-5 judgments. If you cannot find any, you did not have a real
project — it was a task. Move to the weekly task bucket instead.

### 5. General rule candidates
0-3 candidates. Each is a sentence that COULD become a CLAUDE.md rule.
DRI marks each: `[ ] needs DRI promotion decision`.

Promotion rule (SOP P-4): "does this apply to ALL future similar projects?"
- YES → DRI promotes to CLAUDE.md via `case_promote_rule` MCP tool
- NO → leave in case file only

About 10% of candidates promote. 90% stay local.

## Anti-patterns
- ❌ Skip section 4 because "nothing notable happened"
  → if truly nothing, this was task-layer, write to weekly bucket
- ❌ Section 2 over 200 words (means you are narrating, not compressing)
- ❌ Section 5 candidates that name the project ("AI hiring uses X")
  → these are case-specific, not general rules
- ❌ Mark all 3 candidates for promotion without examining (most are not)

## Hand-off
- Project layer: present at Friday Demo. Real artifact, not slides.
- Task layer: weekly case batch reviewed in Monthly Review.
