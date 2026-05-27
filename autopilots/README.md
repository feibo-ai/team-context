# autopilots/

YAML templates for multica autopilot definitions.

**IMPORTANT**: `multica autopilot create` does NOT read YAML files — it accepts
CLI flags. See `scripts/apply-autopilots.sh` which parses these YAMLs and
translates to `multica autopilot create / trigger-add` calls.

| File | Schedule | Mode | Purpose |
| --- | --- | --- | --- |
| daily-summary.yaml | weekdays 18:00 Asia/Shanghai | run_only | Daily summary to feishu |
| monday-kickoff.yaml | Mon 09:30 Asia/Shanghai | create_issue | Weekly plan roundup |
| wednesday-stats.yaml | Wed 09:00 Asia/Shanghai | run_only | CLAUDE.md weekly stats |
| monthly-health.yaml | 1st of month 10:00 Asia/Shanghai | run_only | Trigger monthly_health_report |

## Required env vars (set in each agent's custom-env)

Feishu integration uses [feishu-cli](https://github.com/riba2534/feishu-cli). See
`docs/integrations/feishu-cli.md` for installation + scope + setup.

- `FEISHU_TEAM_CHAT_ID` — main team group chat_id (oc_xxx) for daily/weekly/monthly pushes
- `FEISHU_DEMO_CHAT_ID` — optional · separate group for Friday demo
- `FEISHU_TEAM_WIKI_SPACE` — optional · wiki space for archiving monthly health reports
- `FEISHU_HEALTH_REPORTS_NODE` — optional · wiki parent node for health archive
- `FEISHU_CONFIG_DIR` — defaults to `~/.feishu-cli` · workstation-shared config

Each EXEC workstation must run `feishu-cli config create-app --save` and
`feishu-cli doctor` once before any autopilot can push.
