---
name: tc-self-check
description: "Use mid-work or at any moment of doubt to check yourself against SOP v0.4 10 anti-patterns. Triggers 'am I doing this right', '反 pattern', 'self check', user reports feeling something is off, monthly review, or any time the model feels uncertain about the meta-approach. Returns explicit OK/FLAG/? per anti-pattern + status on the 3 red lines specific to AI MIQ team."
owner: 曾振华
last_reviewed_at: 2026-06-09
---

# Anti-Pattern Self-Check (SOP v0.4 P-7)

Read this list. For each, ask "am I doing this RIGHT NOW?"

## The 10

- **❌1 Letting Claude review its own code**
  Hint: same session wrote and reviewed. Fix: spawn second session with
  role=reviewer.
- **❌2 Multiple Claude in same problem space**
  Hint: two of your active agents work on the same file/feature with
  different mental models. Fix: consolidate or designate lead.
- **❌3 50+ agents simultaneously**
  Hint: agent count exceeded 10 active. Fix: queue, don't fan out further.
- **❌4 CLAUDE.md as junk drawer (> 3k tokens)**
  Hint: case-specific content sneaking in. Fix: move to case file.
- **❌5 Skills without owner or last-review date**
  Hint: open a skill, can't find who maintains it. Fix: add owner +
  last_reviewed_at fields.
- **❌6 Using AI beyond capability frontier**
  Hint: same task failed 3+ times despite plan revision. Fix: human takes
  over, AI as research assistant only.
- **❌7 "Usage rate" mistaken for transformation**
  Hint: high seat usage but .claude/skills/ empty. Fix: measure
  sedimentation quality, not usage frequency.
- **❌8 Experienced dev + familiar codebase + AI**
  Hint: METR-style "AI slows me 19%" zone. Fix: just write it.
- **❌9 "Maximize efficiency" → burnout**
  Hint: feel pressured to always keep all agents busy. Fix: monthly
  burnout check 3 questions, reduce to 3-5 active if any yes.
- **❌10 Project without DRI**
  Hint: no one's name on the plan doc. Fix: assign or refuse to
  start.

## 3 red lines for AI MIQ specifically

(SOP — these need DRI intervention without waiting for monthly review)

1. **❌6 frontier** — Aaron's underlying-algorithm work especially.
2. **❌8 familiar code** — 2 fullstack devs on routine tasks.
3. **❌9 burnout** — interns especially. Monthly check mandatory.

## Output

For each of the 10 anti-patterns, report one of:
- `OK` — not doing this
- `FLAG: <one-sentence why>` — doing this, fix needed
- `?` — uncertain, ask user

End with "3 red lines status" — explicit yes/no/maybe per red line.
