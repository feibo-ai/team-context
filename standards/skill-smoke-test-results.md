# Skill smoke-test results — 2026-05-27

Manual test in a fresh Claude Code session: paste the trigger phrase, verify the named skill is invoked. Mark PASS or FAIL.

| Skill | Trigger phrase | Status |
| --- | --- | --- |
| pre-clear | "I want to /clear" | PENDING |
| rpi-research | "Let's research X" | PENDING |
| rpi-plan-template | "Write a plan for X" | PENDING |
| rpi-implement-discipline | "Let's start implementing" | PENDING |
| debrief-template | "Project done, debrief" | PENDING |
| anti-pattern-self-check | "Am I doing this right?" | PENDING |
| context-pollution-detector | "We're going in circles" | PENDING |
| phase-01-kickoff | "启动新项目" / "kickoff new project" | PENDING |
| monday-kickoff-protocol | "周一 kickoff" / "Monday meeting" | PENDING |
| friday-demo-protocol | "周五 demo" / "betting table" | PENDING |
| role-assignment-protocol | "认领角色" / "role assignment" | PENDING |
| conflict-adjudication | "冲突" / "意见不合" | PENDING |

**Sync status (mechanical, not subjective):**
- `~/team-context/scripts/sync-to-local.sh` ran 2026-05-27 14:10, all 12 skills symlinked into `~/.claude/skills/`.
- Verify: `ls -la ~/.claude/skills/ | grep team-context` should show 12 symlinks pointing at `/Users/feibo/feibo/team-context/skills/*`.

**Method:**
1. Open a fresh Claude Code session in any project (e.g. `cd /tmp && claude`).
2. For each skill: paste the trigger phrase verbatim. The model should invoke the skill via the `Skill` tool within its first response.
3. Replace `PENDING` with `PASS` or `FAIL`. If FAIL, open the `SKILL.md` and sharpen the `description:` field (add the missed trigger, tighten the use case). Re-test.

**On the description field**: every line of `description:` is in the model's attention budget. Don't pad it with body content. Use 1-3 sentences ending with explicit triggers; the model uses these as substring matches.
