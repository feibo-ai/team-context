#!/usr/bin/env bash
# create-labels.sh — populate the 11 standard labels in multica workspace
# (Content embedded above in standards/labels.md — synced here for executability)
#
# Uses parallel arrays instead of `declare -A` so it runs on macOS's bash 3.2.
set -euo pipefail

NAMES=(
  plan-draft
  plan-under-review
  plan-approved
  plan-upgraded
  debrief
  debrief-reviewed
  ancient-impossible
  betting-table
  burnout-alert
  code-review
  research
)
COLORS=(
  "#94A3B8"
  "#F59E0B"
  "#10B981"
  "#A855F7"
  "#3B82F6"
  "#059669"
  "#EC4899"
  "#F97316"
  "#DC2626"
  "#8B5CF6"
  "#06B6D4"
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
