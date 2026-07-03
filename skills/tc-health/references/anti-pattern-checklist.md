The 10 team anti-patterns, the 3 AI MIQ red lines, the monthly burnout-check questions, and the OK/FLAG/? output contract for the tc-health self-check.

# Anti-Pattern Self-Check

Read this list. For each item, ask "am I doing this RIGHT NOW?"

## The 10

- **❌1 Letting Claude review its own code**
  Hint: same session wrote and reviewed. Fix: spawn a second session with role=reviewer.
- **❌2 Multiple Claude in same problem space**
  Hint: two of your active agents work on the same file/feature with different mental models. Fix: consolidate or designate a lead.
- **❌3 50+ agents simultaneously**
  Hint: agent count exceeded 10 active. Fix: queue, don't fan out further.
- **❌4 CLAUDE.md as junk drawer (> 3k tokens)**
  Hint: case-specific content sneaking in. Fix: move to the case file.
- **❌5 Skills without owner or last-review date**
  Hint: open a skill, can't find who maintains it. Fix: record owner + last-review date in the skill pack's governance metadata (pack manifest / registry).
- **❌6 Using AI beyond capability frontier**
  Hint: same task failed 3+ times despite plan revision. Fix: human takes over, AI as research assistant only.
- **❌7 "Usage rate" mistaken for transformation**
  Hint: high seat usage but the project's skills directory is empty. Fix: measure sedimentation quality, not usage frequency.
- **❌8 Experienced dev + familiar codebase + AI**
  Hint: METR-style "AI slows me 19%" zone. Fix: just write it.
- **❌9 "Maximize efficiency" → burnout**
  Hint: feel pressured to always keep all agents busy. Fix: monthly burnout check (3 questions below); reduce to 3-5 active if any yes.
- **❌10 Project without DRI**
  Hint: no one's name on the plan doc. Fix: assign or refuse to start.

## Monthly burnout check — the 3 questions

1. 这个月跑 5-10 个 active Claude，你觉得疲惫吗？
2. 有没有出现"看到通知就反感"的情况？
3. 下班后还在想 Claude session 状态吗？

Any yes → drop to 3-5 active this month, no pushing through; return to the 5-10 baseline after recovery. This is a brake mechanism, not a retreat.

## 3 red lines for AI MIQ specifically

(These need DRI intervention without waiting for the monthly review.)

1. **❌6 frontier** — Aaron's underlying-algorithm work especially.
2. **❌8 familiar code** — 2 fullstack devs on routine tasks.
3. **❌9 burnout** — interns especially. Monthly check mandatory.

## Output contract

For each of the 10 anti-patterns, report one of:
- `OK` — not doing this
- `FLAG: <one-sentence why>` — doing this, fix needed
- `?` — uncertain, ask user

End with "3 red lines status" — explicit yes/no/maybe per red line.
