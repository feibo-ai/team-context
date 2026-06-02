#!/usr/bin/env bash
# team-autopilot.sh — DRI 一键建「团队版」autopilot (取代旧的 apply-autopilots.sh · spec §4.2 选项 A)。
#   绑常驻 runtime · 汇总全队 · 全部推团队群 (notify_team · 无 P2P)。
#
# 用法:
#   bash scripts/team-autopilot.sh all codex            # 建全队 5 个汇总
#   bash scripts/team-autopilot.sh monday-kickoff codex # 或单个
#     kind:     daily-summary | daily-kickoff | monday-kickoff | wednesday-stats | monthly-health | all
#     provider: codex | claude | hermes
#
# 前置: multica login + 常驻 daemon 在线 + export TCMCP_AGENT_TOKEN=<autopilot-bot PAT 或 $MULTICA_TOKEN>
# 在 DRI 常驻 mac 上跑 (未来若有云端 daemon · 在那台跑)。
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/_autopilot-common.sh
source "${DIR}/_autopilot-common.sh"

KIND="${1:-}"; PROVIDER="${2:-}"
[ -n "$KIND" ] && [ -n "$PROVIDER" ] || ac_die "用法: bash scripts/team-autopilot.sh <kind|all> <provider>"

ac_preflight

# 团队版: scope 固定 team · suffix 固定 team
SCOPE="team"; SUFFIX="team"

echo "团队版 autopilot · scope=全队 · provider=${PROVIDER}"
ac_run "$KIND" "$PROVIDER" "$SCOPE" "$SUFFIX"
