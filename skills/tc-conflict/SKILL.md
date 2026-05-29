---
name: tc-conflict
description: "Use when team members disagree on a project decision. Triggers '冲突', '分歧', 'conflict', 'disagree', '意见不合', '谁说了算'. Walks through SOP v0.4 P-5 conflict 4 principles. Writes resolution to decisions/YYYY-MM-DD-<topic>.md regardless of outcome."
---

# Conflict Adjudication — 4 principles

## When to invoke
Two or more members have genuinely different views on a project decision (not casual taste — real consequence).

## The 4 principles

### 1. 对事不对人
Frame as "two options" or "two interpretations," not "X vs Y people." If you can't restate other side's argument fairly, you don't understand it — back up.

### 2. 依据优先于偏好
What does EVIDENCE say?
- Performance data? Test results? Prior cases? Industry refs? Cite them.
- "I feel" or "in my experience" without specifics doesn't count.
- If no evidence either way, label explicitly: "this is judgment call X vs Y."

### 3. DRI 最终决定权
After 1 + 2:
- If consensus → great, document.
- If still split → DRI decides. Even if DRI is more junior. Even if DRI is wrong (you still execute and observe outcome).

### 4. 决策必须记录到 decisions/
Write `decisions/YYYY-MM-DD-<topic>.md`:
- Context (what was choice?)
- Options considered
- Evidence cited for each
- DRI's decision
- Dissenter's flag if any
- Date + signatures

Non-negotiable. Without file, decision didn't happen.

## Output template

```markdown
# Decision: <topic>

**Date**: YYYY-MM-DD
**DRI**: <name>
**Status**: decided

## Context
<what was the choice?>

## Options
- A: <description>
- B: <description>

## Evidence per option
- For A: <citation>
- For B: <citation>

## DRI decision
Chose: <A or B>
Reason: <1-2 sentences>

## Dissent
<name> disagreed with <reason>, but agreed to execute.

## Review trigger
If <observable signal> happens, revisit.
```

## Anti-patterns
- ❌ "Let's vote on it" — DRI model means DRI decides, not majority
- ❌ Skip the file because "decision was obvious in the meeting"
- ❌ "I told you so" later when dissent turns out right (SOP P-5 forbids)
- ❌ Senior overrides intern DRI without documenting
