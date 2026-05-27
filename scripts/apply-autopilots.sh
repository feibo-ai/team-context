#!/usr/bin/env bash
# apply-autopilots.sh — translate autopilots/*.yaml into multica CLI calls
# Idempotent: re-runnable to update existing autopilots.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AUTOPILOTS_DIR="${REPO_DIR}/autopilots"

command -v yq >/dev/null || { echo "Install yq first: brew install yq"; exit 1; }
command -v jq >/dev/null || { echo "Install jq first: brew install jq"; exit 1; }
command -v feishu-cli >/dev/null || {
  echo "ERROR: feishu-cli not installed (autopilots push to feishu)."
  echo "Install: curl -fsSL https://raw.githubusercontent.com/riba2534/feishu-cli/main/install.sh | bash"
  exit 1
}

multica auth status > /dev/null || { echo "Run: multica login"; exit 1; }

# Pre-check: run autopilot_lint MCP tool on every YAML before apply
# (PB-04 guardrails + budget cap — SOP CRITICAL gate)
echo "=== Pre-check: autopilot_lint on all YAMLs ==="
LINT_FAIL=0
for yaml in "${AUTOPILOTS_DIR}"/*.yaml; do
  [[ -f "${yaml}" ]] || continue
  name=$(yq eval '.name' "${yaml}")
  # Call team-context-mcp's autopilot_lint via MCP CLI shim, or fall back to yq-based check
  if command -v team-context-mcp-cli >/dev/null 2>&1; then
    if ! team-context-mcp-cli autopilot_lint --yaml-path "${yaml}"; then
      echo "  ❌ ${name}: autopilot_lint failed"
      LINT_FAIL=$((LINT_FAIL + 1))
    fi
  else
    # Fallback: minimal inline check (mirror autopilot_lint's required fields)
    g_present=$(yq eval '.guardrails' "${yaml}")
    if [[ "${g_present}" == "null" || -z "${g_present}" ]]; then
      echo "  ❌ ${name}: missing guardrails section (PB-04 violation)"
      LINT_FAIL=$((LINT_FAIL + 1))
      continue
    fi
    fc_count=$(yq eval '.guardrails.forbidden_commands | length' "${yaml}")
    if (( fc_count < 5 )); then
      echo "  ❌ ${name}: forbidden_commands has ${fc_count} entries (< 5)"
      LINT_FAIL=$((LINT_FAIL + 1))
    fi
    if ! yq eval '.guardrails.forbidden_commands[]' "${yaml}" | grep -qi "git push"; then
      echo "  ❌ ${name}: forbidden_commands missing 'git push'"
      LINT_FAIL=$((LINT_FAIL + 1))
    fi
    budget=$(yq eval '.guardrails.max_budget_usd' "${yaml}")
    if [[ -z "${budget}" || "${budget}" == "null" ]]; then
      echo "  ❌ ${name}: missing max_budget_usd"
      LINT_FAIL=$((LINT_FAIL + 1))
    elif (( budget > 150 )); then
      echo "  ❌ ${name}: max_budget_usd ${budget} > 150 hard cap"
      LINT_FAIL=$((LINT_FAIL + 1))
    fi
  fi
done

if (( LINT_FAIL > 0 )); then
  echo ""
  echo "🛑 ${LINT_FAIL} autopilot YAML(s) failed lint. Refusing to apply."
  echo "Fix the YAML(s) to satisfy SOP PB-04 guardrails, then re-run."
  exit 1
fi
echo "  ✅ All autopilots passed lint"
echo ""

for yaml in "${AUTOPILOTS_DIR}"/*.yaml; do
  [[ -f "${yaml}" ]] || continue

  name=$(yq eval '.name' "${yaml}")
  desc=$(yq eval '.description' "${yaml}")
  mode=$(yq eval '.mode' "${yaml}")
  agent=$(yq eval '.agent.name' "${yaml}")
  prompt=$(yq eval '.prompt' "${yaml}")
  cron=$(yq eval '.trigger.cron' "${yaml}")
  tz=$(yq eval '.trigger.timezone' "${yaml}")

  echo "Applying autopilot: ${name}"

  existing_id=$(multica autopilot list --output json 2>/dev/null \
    | jq -r ".[] | select(.name==\"${name}\") | .id" || echo "")

  if [[ -n "${existing_id}" ]]; then
    echo "  Updating ${existing_id}"
    multica autopilot update "${existing_id}" \
      --description "${desc}" \
      --agent "${agent}" \
      --prompt "${prompt}"
  else
    echo "  Creating new"
    new_id=$(multica autopilot create \
      --name "${name}" \
      --description "${desc}" \
      --mode "${mode}" \
      --agent "${agent}" \
      --prompt "${prompt}" \
      --output id-only)

    if [[ "${mode}" == "create_issue" ]]; then
      title_template=$(yq eval '.issue_title_template' "${yaml}")
      multica autopilot update "${new_id}" --issue-title-template "${title_template}"
    fi

    existing_id="${new_id}"
  fi

  # Apply or update schedule trigger
  multica autopilot trigger-add "${existing_id}" \
    --kind schedule \
    --cron "${cron}" \
    --timezone "${tz}" || \
  multica autopilot trigger-update "${existing_id}" \
    --kind schedule \
    --cron "${cron}" \
    --timezone "${tz}"

  echo "  Done: ${name}"
done

echo ""
echo "All autopilots applied. Verify with: multica autopilot list"
