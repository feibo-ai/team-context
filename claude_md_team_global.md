# AI MIQ — team-global CLAUDE.md

Cross-project rules that apply to ALL team work. Copied (or symlinked)
into each product repo's CLAUDE.md, OR layered above it via Claude Code's
`CLAUDE.md` inheritance.

## Who we are
AI MIQ — 5-person AI-Native team. We operate by SOP v0.4 reference
Handbook. Generalist + AI-leveraged, dumbbell model.

## How we work — 5 core rules

1. **Research / Plan / Implement are DISCRETE sessions.** Never blend.
   Use `rpi-research`, `rpi-plan-template`, `rpi-implement-discipline`
   skills as session protocols.
2. **Context pollution → invoke `pre-clear` skill → /clear.** Don't fix
   in place.
3. **Every project/task ends with a debrief in `cases/YYYY-MM-DD-*.md`**
   using the `debrief-template` skill. 5 mandatory sections. SOP
   non-negotiable #2.
4. **Plan markdown required before any code, reviewed by second session.**
   `rpi-plan-template` skill. SOP non-negotiable #1.
5. **Sanity rule: every AI-generated diff seen by a human eye before
   commit.** Yours to ship.

## Cross-project tech rules
(Populated as team standards emerge. Each rule must apply to ALL future
similar projects; project-specific rules go in `cases/`, not here.)

## Mistakes Claude must not repeat
(Promoted from case files via `case_promote_rule` MCP tool.)

## How to call other Claude sessions

| Need | Skill |
| --- | --- |
| Research | `rpi-research` |
| Plan | `rpi-plan-template` |
| Implement | `rpi-implement-discipline` |
| Debrief | `debrief-template` |
| Self-check | `anti-pattern-self-check` |
| Pollution scan | `context-pollution-detector` |
| Before /clear | `pre-clear` |

## When you are stuck
- 30 minutes no progress → invoke `pre-clear` skill
- 3 handoffs on the same issue → upgrade to greenfield playbook (PB1)
- 5 handoffs in a single week → flag burnout signal at monthly review

## Where to find specific context

| What | Where |
| --- | --- |
| Cross-project Skills | `~/.claude/skills/` (synced from team-context repo) |
| Per-project plans | `<project>/docs/plans/` |
| Per-project research | `<project>/docs/research/` |
| Project cases (L2) | `<project>/cases/YYYY-MM-DD-*.md` |
| Team SOP | team-context repo, `sop/group_sop_v0.4.html` |
| Team standards | team-context repo, `standards/` |
| Architecture decisions | `<project>/decisions/` + team-context `decisions/` |
| Multica workspace | `teamctx` (server URL: run `multica config show`) |
| Multica CLI ref | `multica --help` or `~/.claude/skills/multica-cli/` |
