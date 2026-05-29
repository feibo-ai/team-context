# scripts/

## 同步
- `sync-to-local.sh` — 把 skills/* 软链接到 ~/.claude/skills/*
- `sync-to-multica.sh` — 通过 `multica skill import` 把 skills/ 推送到 multica workspace

## Autopilot (2026-05-28 spec · 个人版 + 团队版)
- `my-autopilot.sh <kind|all> <provider>` — 团队成员建「个人版」autopilot(绑自己 runtime · 只汇报自己 · 推团队群)
- `team-autopilot.sh <kind|all> <provider>` — DRI 建「团队版」autopilot(绑常驻 runtime · 汇总全队 · 推团队群)
- `_autopilot-common.sh` — 上面两个共享逻辑(被 `source` · 非独立运行)
- `apply-autopilots.sh` — ⚠️ DEPRECATED · 被 `team-autopilot.sh` 取代(不注入 `AUTOPILOT_SCOPE`,与 scope 分支 prompt 不兼容)
  - `kind`: daily-summary | monday-kickoff | wednesday-stats | monthly-health | all
  - `provider`: codex | claude | hermes

## 其他
- `create-labels.sh` — 在 multica workspace 建 11 个标准 label
- `multica-secrets-bootstrap.sh` — DRI 一次性把飞书 secret 推到 multica(env-file → multica secret)
- `install-feishu-cli.sh` — ⚠️ DEPRECATED(W5 起团队成员不需要 feishu-cli)
