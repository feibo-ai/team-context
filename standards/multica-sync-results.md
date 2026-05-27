# Multica skill sync result — 2026-05-27

**Workspace**: `team-context` (slug: `team-context`, id: `766a0455-62d4-4454-b8b3-1794e2e92864`)
**Server**: `http://localhost:8080` (local Docker)
**Skills imported**: 12 / 12

## How the import ran

The plan's original path — `multica skill import --url https://github.com/feibo-ai/team-context` — does not work for this repo because:

1. `multica skill import` expects exactly one `SKILL.md` at the URL root, so per-skill URLs are required (one URL per skill, not one URL per repo).
2. The repo is **private**, so the multica server's GitHub fetcher gets HTTP 404 on `raw.githubusercontent.com`. The team SOP and skill bodies stay private by design.

Workaround: import locally via `multica skill create --name <n> --description <d> --content <body>` for each `skills/<name>/SKILL.md`. Frontmatter is split off, body is sent as `--content`. All 12 succeeded.

## Imported skills

| Skill | Multica ID |
| --- | --- |
| anti-pattern-self-check | `757e089c-516d-4bc5-a1b6-f408edec853c` |
| conflict-adjudication | `c85b71c4-6f03-4977-9fcd-38acd447cf53` |
| context-pollution-detector | `681944d5-09f6-4b73-bcaf-b4e292e30b30` |
| debrief-template | `022135cb-4706-4fd7-9379-219edd9eb7a6` |
| friday-demo-protocol | `e8974254-9cf5-411e-9553-8da0d2a634cb` |
| monday-kickoff-protocol | `13dc900d-895f-49d1-af30-15027bc2a690` |
| phase-01-kickoff | `41bff02d-396c-4805-9c25-40452955f263` |
| pre-clear | `22df81c5-9337-4df2-9782-4c734d907632` |
| role-assignment-protocol | `bbe4e0e4-9f63-487f-84aa-5f12c0a18c1e` |
| rpi-implement-discipline | `293aa859-aee8-49e2-9294-0e336aa1ee2c` |
| rpi-plan-template | `a6797576-09a5-4c41-b2a8-bf01a4ed56a0` |
| rpi-research | `8cdfc6b3-8779-407a-8178-f3f02459227f` |

## Agent mount (Step 4) — DEFERRED

Plan's Step 4 expects an existing test agent to mount the 12 skills on. The local workspace has **0 agents** at this point:

```
$ multica agent list
ID  NAME  STATUS  RUNTIME  ARCHIVED
(empty)
```

When the first agent is created (via `multica agent create` or via squad import), run:

```bash
multica agent skills set --agent <agent-id> \
  --skill-ids "$(multica skill list --output id-only | tr '\n' ',' | sed 's/,$//')"
multica agent skills list --agent <agent-id>
```

## Re-sync protocol

If `skills/*/SKILL.md` changes locally:

```bash
cd ~/team-context
git pull             # sync from feibo-ai/team-context
# Re-import: the local-create approach is idempotent only if you delete first.
# For per-skill update use:  multica skill update --name X --content <body>
```

The plan's `scripts/sync-to-multica.sh` wrapper assumes a public GitHub URL; for this private setup, prefer the local-create path above until multica supports authenticated GitHub fetch or local-path import.
