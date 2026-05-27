#!/usr/bin/env bash
# create-labels.sh — populate the 11 standard labels in multica workspace
# (Content embedded above in standards/labels.md — synced here for executability)
set -euo pipefail

declare -A LABELS=(
  ["plan-draft"]="#94A3B8"
  ["plan-under-review"]="#F59E0B"
  ["plan-approved"]="#10B981"
  ["plan-upgraded"]="#A855F7"
  ["debrief"]="#3B82F6"
  ["debrief-reviewed"]="#059669"
  ["ancient-impossible"]="#EC4899"
  ["betting-table"]="#F97316"
  ["burnout-alert"]="#DC2626"
  ["code-review"]="#8B5CF6"
  ["research"]="#06B6D4"
)

for name in "${!LABELS[@]}"; do
  color="${LABELS[$name]}"
  existing=$(multica label list --output json | jq -r ".[] | select(.name==\"${name}\") | .id" || echo "")
  if [[ -z "${existing}" ]]; then
    echo "Creating: ${name} (${color})"
    multica label create --name "${name}" --color "${color}"
  else
    echo "Exists:   ${name} (${existing})"
  fi
done

echo ""
echo "Done. Verify: multica label list"
