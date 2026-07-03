---
name: tc-health
description: "Audits session health: scans the transcript for context-pollution signals (yes-loops, repeated rejected fixes, wrong-question answers, phantom issues) and self-checks the approach against 10 team anti-patterns + 3 red lines. Use when the user says '污染扫描', '健康检查', 'context 乱了', '自检', '反模式', 'health check', 'self check', 'going in circles', or the model seems confused or too agreeable. Not for the recovery itself — use tc-handoff."
---

# tc-health

## Mandate
Session health audit, two modes: (a) pollution scan — has THIS session's context degraded, before the user notices? (b) self-check — is the working approach hitting a team anti-pattern or red line? Cheap to run; worst case a false alarm.

## Entry gates
- User explicitly invoked → never skip, they have a reason.
- Self-triggered → only on concrete symptoms (circling, over-agreement, meta-doubt), not every turn.

## Steps
1. Pick mode: transcript symptoms (乱了, 走偏了, circling, too agreeable) → pollution scan; approach doubt (自检, 'am I doing this right') → self-check; ambiguous → both.
2. Pollution scan: re-read the last 10 turns first — pollution is invisible from inside. Read references/context-pollution-check.md, score the 4 signals, apply the aggregation rule, output the fixed template.
3. Self-check: read references/anti-pattern-checklist.md; ask "am I doing this RIGHT NOW?" for each of the 10; check the 3 red lines; output the OK/FLAG/? contract.

## References
| File | When |
|---|---|
| references/context-pollution-check.md | Pollution scan: 4-signal rubric, aggregation, template |
| references/anti-pattern-checklist.md | Self-check: 10 anti-patterns, red lines, burnout questions |

## Handoffs / Anti-patterns
- Verdict tc-handoff-now → INVOKE tc-handoff skill. Red line yes → flag the DRI now.
- ❌ Run every turn (overhead, false positives).
- ❌ Score from memory without re-reading the transcript.
- ❌ Skip or soften results when the user invokes.
