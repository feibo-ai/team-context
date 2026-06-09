---
name: tc-health-check
description: "Use when conversation shows signs of going in circles, model seems confused, or you suspect the session has entered SOP v0.4 'dumb zone'. Triggers '走偏了', '感觉不对', 'going in circles', '怎么回事', repeated rejected solutions in conversation, model agreeing too readily. Outputs explicit pollution signals detected and recommends invoke tc-handoff or continue."
owner: 曾振华
last_reviewed_at: 2026-06-09
---

# Context Pollution Detector

## Mandate
Identify whether THIS session has entered the dumb zone BEFORE user does.
Self-monitoring loop. Cheap to run. Worst case: false alarm and user
overrides. Best case: catch a doomed thread early.

## The 4 signals (SOP v0.4 P-2)

### Signal 1: "You're absolutely right" loop
Look back 5 turns. Did the model agree with user 3+ times without
pushback? Specifically: did it reverse a position when challenged with no
new evidence?
- 0 occurrences → OK
- 1 → noted, watch
- 2+ → POLLUTED

### Signal 2: Repeating rejected solutions
Look back 10 turns. Has the model re-proposed something the user
already rejected?
- No → OK
- Once → noted
- Twice or more → POLLUTED

### Signal 3: Answering the wrong question
The last 2 user messages: did the model's response address what was
asked? Or an adjacent but different question?
- Both answered → OK
- One off → noted
- Both off → POLLUTED

### Signal 4: Resolving "earlier" issues that do not exist
Did the model say "let me fix the issue from before" or "going back to
the earlier problem" when no such problem was raised?
- No → OK
- Yes → POLLUTED

## Aggregation rule
- Any signal POLLUTED → invoke tc-handoff skill
- Two signals "noted" → tell user, recommend tc-handoff, let user decide
- Zero or one "noted" → continue

## Output

```
Pollution scan:
- Signal 1 (yes-loop):          OK | noted | POLLUTED
- Signal 2 (repeat-rejection):  OK | noted | POLLUTED
- Signal 3 (wrong-question):    OK | noted | POLLUTED
- Signal 4 (phantom-issue):     OK | noted | POLLUTED

Verdict: continue | mention | tc-handoff-now
```

## Anti-patterns
- ❌ Run every turn (overhead, false positives, annoying)
- ❌ Trust your own assessment without re-reading transcript (the dumb
  zone is invisible from inside)
- ❌ Skip when user invokes — they have a reason
