#!/usr/bin/env bash
# my-autopilot.sh — 团队成员一键建「个人版」autopilot。
#   绑你这台机的 runtime · 只汇报你自己 · 全部推团队群 (notify_team · 无 P2P)。
#
# 用法:
#   bash scripts/my-autopilot.sh all codex            # 一键建你的全部 5 个
#   bash scripts/my-autopilot.sh daily-summary codex  # 或单个
#     kind:     daily-summary | daily-kickoff | monday-kickoff | wednesday-stats | monthly-health | all
#     provider: codex | claude | hermes
#
# 前置: multica login + multica daemon start + export TCMCP_AGENT_TOKEN=$MULTICA_TOKEN
# 注意: 只在你的 daemon 在线时跑 · 关机/睡眠日 cron 静默 skip (spec §1.3 离线语义)。
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/_autopilot-common.sh
source "${DIR}/_autopilot-common.sh"

KIND="${1:-}"; PROVIDER="${2:-}"
[ -n "$KIND" ] && [ -n "$PROVIDER" ] || ac_die "用法: bash scripts/my-autopilot.sh <kind|all> <provider>"

ac_preflight

# scope = 自己的 email · suffix = email 前缀 (alice@x → alice)
OWNER=$(multica auth status 2>&1 | awk -F'[()]' '/User:/{print $2; exit}')
[ -n "$OWNER" ] || ac_die "拿不到当前用户 email (multica auth status 无 'User: Name (email)' 行)"
SCOPE="$OWNER"; SUFFIX="${OWNER%@*}"

echo "个人版 autopilot · owner=${OWNER} · provider=${PROVIDER}"
ac_run "$KIND" "$PROVIDER" "$SCOPE" "$SUFFIX"
