#!/usr/bin/env bash
# apply-autopilots.sh — translate autopilots/*.yaml into multica CLI calls
# Idempotent: re-runnable to update existing autopilots.
set -euo pipefail

# Required envs (TC-N1 + TC-N2): autopilots reach feishu via tcmcp-remote · NOT feishu-cli.
# Secrets stay in multica; only TCMCP_REMOTE_URL + TCMCP_AGENT_TOKEN are injected into agent env.
: "${MULTICA_WORKSPACE:?MULTICA_WORKSPACE must be set}"
: "${TCMCP_REMOTE_URL:=http://host.docker.internal:8443/mcp}"
: "${TCMCP_AGENT_TOKEN:?TCMCP_AGENT_TOKEN must be set — see TC-3.5 for how DRI issues this once}"
export MULTICA_WORKSPACE

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AUTOPILOTS_DIR="${REPO_DIR}/autopilots"

command -v yq >/dev/null || { echo "Install yq first: brew install yq"; exit 1; }
command -v jq >/dev/null || { echo "Install jq first: brew install jq"; exit 1; }

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
    # Capture-then-grep to avoid `grep -q` SIGPIPE'ing yq under `set -o pipefail`.
    fc_lines=$(yq eval '.guardrails.forbidden_commands[]' "${yaml}")
    if ! echo "${fc_lines}" | grep -qi "git push"; then
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

  # Resolve integration_ref (TC-5 · TC-N2 design): inject only TCMCP_REMOTE_URL +
  # TCMCP_AGENT_TOKEN into agent env. Secrets stay in multica · MCP tools fetch
  # them server-side via tcmcp-remote.
  INTEGRATION_REF=$(yq eval '.agent.integration_ref // ""' "${yaml}")
  if [[ -n "${INTEGRATION_REF}" ]]; then
    echo "  Wiring agent to tcmcp-remote (integration: ${INTEGRATION_REF})"
    multica integration get "${INTEGRATION_REF}" --output json >/dev/null || {
      echo "  ERROR: integration ${INTEGRATION_REF} not found"; exit 1;
    }
    AGENT_ID=$(multica agent list --output json | jq -r ".[] | select(.name==\"${agent}\") | .id")
    if [[ -n "${AGENT_ID}" ]]; then
      multica agent env set "${AGENT_ID}" --custom-env \
        "{\"TCMCP_REMOTE_URL\":\"${TCMCP_REMOTE_URL}\",\"TCMCP_AGENT_TOKEN\":\"${TCMCP_AGENT_TOKEN}\"}"
      echo "  Agent ${agent} now reaches tcmcp-remote (secrets stay in multica)"
    else
      echo "  WARN: agent ${agent} not found · run TC-3.5 first"
    fi
  fi

  # Merge YAML's description + prompt into the CLI's single --description field.
  # CLI semantics: --description IS the task prompt the agent receives.
  full_desc=$(printf '%s\n\n%s' "${desc}" "${prompt}")

  # autopilot list returns {autopilots: [...], total: N}; not a bare array.
  existing_id=$(multica autopilot list --output json 2>/dev/null \
    | jq -r ".autopilots[] | select(.title==\"${name}\") | .id" || echo "")

  if [[ -n "${existing_id}" ]]; then
    echo "  Updating ${existing_id}"
    multica autopilot update "${existing_id}" \
      --description "${full_desc}" \
      --agent "${agent}" >/dev/null
  else
    echo "  Creating new"
    new_id=$(multica autopilot create \
      --title "${name}" \
      --description "${full_desc}" \
      --mode "${mode}" \
      --agent "${agent}" \
      --output json | jq -r '.id')

    if [[ "${mode}" == "create_issue" ]]; then
      title_template=$(yq eval '.issue_title_template' "${yaml}")
      multica autopilot update "${new_id}" --issue-title-template "${title_template}" >/dev/null
    fi

    existing_id="${new_id}"
  fi

  # Schedule trigger: add if missing; update existing one if present.
  existing_trigger=$(multica autopilot get "${existing_id}" --output json 2>/dev/null \
    | jq -r '.triggers[]? | select(.kind=="schedule") | .id' | head -1)
  if [[ -z "${existing_trigger}" ]]; then
    multica autopilot trigger-add "${existing_id}" \
      --kind schedule \
      --cron "${cron}" \
      --timezone "${tz}" >/dev/null
  else
    multica autopilot trigger-update "${existing_id}" "${existing_trigger}" \
      --cron "${cron}" >/dev/null
  fi

  echo "  Done: ${name}"
done

echo ""
echo "All autopilots applied. Verify with: multica autopilot list"
