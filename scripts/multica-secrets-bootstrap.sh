#!/usr/bin/env bash
# multica-secrets-bootstrap.sh
#
# One-time script. Reads secrets from a local env file and pushes to multica
# integration secret store. Per Decision D-G (W5): env file is the secret source
# (no 1Password / Vault integration in v0 · keep it simple).
#
# Usage:
#   1. Create ~/.tcmcp.secrets file with KEY=VALUE pairs (mode 600)
#   2. export MULTICA_WORKSPACE=<your-workspace>
#   3. bash scripts/multica-secrets-bootstrap.sh <integration-name>
#   4. Shred ~/.tcmcp.secrets after successful push (don't keep on disk)
#
# Example ~/.tcmcp.secrets:
#   FEISHU_APP_ID=cli_xxx
#   FEISHU_APP_SECRET=xxxyyyzzz
#   # NOTE: do NOT put MULTICA_SERVICE_TOKEN here — it's a boot env for tcmcp-remote,
#   # not an integration secret. It's what you USE to fetch the integration.
#
# PRE-REQ · multica user role:
#   Your multica account MUST be workspace owner or admin (Plan-4 v2 Open Q #5).
#   Verify before running:
#     multica auth status --output json | jq '.user.role'
#     # Expected: "owner" or "admin" · "member" / "guest" will hit 403 on secret writes.

set -euo pipefail

# Plan-4 v2 Open Q #7 default: all integration / secret CLI commands require
# --workspace flag OR MULTICA_WORKSPACE env. Export once here so every multica
# call below inherits it without repeating the flag.
: "${MULTICA_WORKSPACE:?MULTICA_WORKSPACE must be set (e.g. export MULTICA_WORKSPACE=teamctx)}"
export MULTICA_WORKSPACE

INTEGRATION_NAME="${1:-}"
if [[ -z "${INTEGRATION_NAME}" ]]; then
  echo "Usage: $0 <integration-name>"
  echo "Example: $0 team-context-mcp"
  exit 2
fi

SECRETS_FILE="${HOME}/.tcmcp.secrets"
if [[ ! -f "${SECRETS_FILE}" ]]; then
  echo "ERROR: ${SECRETS_FILE} not found"
  echo "Create it (mode 600) with KEY=VALUE lines · then re-run."
  exit 1
fi

# Sanity check perms
perms=$(stat -f "%A" "${SECRETS_FILE}" 2>/dev/null || stat -c "%a" "${SECRETS_FILE}")
if [[ "${perms}" != "600" ]]; then
  echo "WARN: ${SECRETS_FILE} mode is ${perms} · should be 600"
  echo "Fix: chmod 600 ${SECRETS_FILE}"
  read -p "Continue anyway? [y/N] " ok
  [[ "${ok}" == "y" ]] || exit 1
fi

# Verify integration exists
multica integration get "${INTEGRATION_NAME}" --output json > /dev/null 2>&1 || {
  echo "ERROR: integration '${INTEGRATION_NAME}' not found in multica"
  echo "Create it first: multica integration create --kind mcp-server --name ${INTEGRATION_NAME} ..."
  exit 1
}

echo "=== Pushing secrets to integration: ${INTEGRATION_NAME} ==="

count=0
while IFS='=' read -r key value; do
  # skip empty lines and comments
  [[ -z "${key}" || "${key}" =~ ^# ]] && continue
  # strip any surrounding quotes from value
  value="${value#\"}"
  value="${value%\"}"
  echo "  Setting: ${key}"
  printf '%s' "${value}" | multica secret set --integration "${INTEGRATION_NAME}" "${key}" --value-stdin
  count=$((count + 1))
done < "${SECRETS_FILE}"

echo ""
echo "Done · ${count} secrets pushed."
echo ""
echo "Verify: multica secret list --integration ${INTEGRATION_NAME}"
echo ""
echo "RECOMMENDED: shred ${SECRETS_FILE} now to avoid leaving plaintext on disk:"
echo "  shred -u ${SECRETS_FILE}     # GNU"
echo "  rm -P ${SECRETS_FILE}        # macOS"
