#!/usr/bin/env bash
# create-labels.sh — populate the 13 standard labels in multica workspace
# (标签字典单源: skills/tc-render/references/issue-label-state-rules.md — 此处内嵌一份以便执行)
#
# Uses parallel arrays instead of `declare -A` so it runs on macOS's bash 3.2.
set -euo pipefail

NAMES=(
  计划-草稿
  计划-评审中
  计划-已批准
  计划-已升级
  设计-待审
  设计-已审
  复盘-待审
  复盘-已审
  古法不可能
  投注表
  倦怠预警
  代码评审
  研究
)
COLORS=(
  "#9ca3af"
  "#f59e0b"
  "#10b981"
  "#8b5cf6"
  "#eab308"
  "#0ea5e9"
  "#f97316"
  "#14b8a6"
  "#ef4444"
  "#ec4899"
  "#dc2626"
  "#6366f1"
  "#3b82f6"
)

for i in "${!NAMES[@]}"; do
  name="${NAMES[$i]}"
  color="${COLORS[$i]}"
  existing=$(multica label list --output json | jq -r ".[] | select(.name==\"${name}\") | .id" || echo "")
  if [[ -z "${existing}" ]]; then
    echo "Creating: ${name} (${color})"
    multica label create --name "${name}" --color "${color}" >/dev/null
  else
    echo "Exists:   ${name} (${existing})"
  fi
done

echo ""
echo "Done. Verify: multica label list"
