Full 4-signal context-pollution rubric for the tc-health pollution scan: scoring thresholds, aggregation rule, and the fixed output template.

# Context-Pollution Check — the 4 signals

Re-read the actual transcript before scoring. The dumb zone (degraded, polluted context) is invisible from inside — never score from memory.

## Signal 1: "You're absolutely right" loop
Look back 5 turns. Did the model agree with the user 3+ times without pushback? Specifically: did it reverse a position when challenged with no new evidence?
- 0 occurrences → OK
- 1 → noted, watch
- 2+ → POLLUTED

## Signal 2: Repeating rejected solutions
Look back 10 turns. Has the model re-proposed something the user already rejected?
- No → OK
- Once → noted
- Twice or more → POLLUTED

## Signal 3: Answering the wrong question
The last 2 user messages: did the model's response address what was asked? Or an adjacent but different question?
- Both answered → OK
- One off → noted
- Both off → POLLUTED

## Signal 4: Resolving "earlier" issues that do not exist
Did the model say "let me fix the issue from before" or "going back to the earlier problem" when no such problem was raised?
- No → OK
- Yes → POLLUTED

## Aggregation rule → verdict mapping
- Any signal POLLUTED → verdict `tc-handoff-now`: INVOKE tc-handoff skill.
- Two signals "noted" → verdict `mention`: tell the user, recommend tc-handoff, let the user decide.
- Zero or one "noted" → verdict `continue`.

## Output (fixed template)

```
Pollution scan:
- Signal 1 (yes-loop):          OK | noted | POLLUTED
- Signal 2 (repeat-rejection):  OK | noted | POLLUTED
- Signal 3 (wrong-question):    OK | noted | POLLUTED
- Signal 4 (phantom-issue):     OK | noted | POLLUTED

Verdict: continue | mention | tc-handoff-now
```
