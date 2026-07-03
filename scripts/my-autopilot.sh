#!/usr/bin/env bash
# my-autopilot.sh — DEPRECATED(2026-07-03 收敛决策:30→5,只保留 team scope)。
#
# 个人 autopilot 已下线:个人卡的信息 = 团队卡按人归并后的行(纯冗余),
# 且个人机器在 cron 时间点离线时 run 被静默 skip(丢失)。团队卡跑在
# DRI 常驻机 / cloud runtime,离线丢失面与刷屏一并消掉。
#
# - 团队版部署: bash scripts/team-autopilot.sh all codex(DRI 在常驻机跑)
# - 旧个人 autopilot 清理: bash scripts/decommission-personal-autopilots.sh
# - 确有个人版需求 → 先在团队群提出,恢复前先解决离线丢失(catch-up)问题
set -euo pipefail
echo "[deprecated] my-autopilot.sh 已随 2026-07-03 收敛决策下线(30→5 · team-only)。" >&2
echo "  团队版: bash scripts/team-autopilot.sh all codex" >&2
echo "  清理旧个人 autopilot: bash scripts/decommission-personal-autopilots.sh" >&2
exit 2
