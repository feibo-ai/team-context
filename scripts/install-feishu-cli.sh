#!/usr/bin/env bash
# ⚠️  DEPRECATED · since W5 (control plane edition)
#
# Team members no longer need feishu-cli. v2 architecture:
#   - tcmcp-remote (Zeabur cloud service · mcp.teamctx.actionow.ai) talks to Feishu via
#     `@larksuiteoapi/node-sdk` (lark Node SDK).
#   - All 10 remote MCP tools (notify_team / dm_member / archive_to_wiki /
#     search_chat / read_member_dm + 5 moved · burnout / plan_request_review /
#     code_review_request / betting_table_capture / should_i_use_ai) talk to
#     Feishu through that single in-process SDK.
#   - feishu-cli was never required at runtime for autopilots after W5.
#
# This script is kept ONLY for:
#   - DRI debugging the Feishu OpenAPI directly (search-chats / api call / etc.)
#   - One-off chat_id discovery if the multica `search_chat` MCP tool isn't
#     reachable for any reason.
#
# If you're onboarding as a team member: skip this script. See README.md.
#
# Continue if you really need it.

set -euo pipefail

echo "⚠️  install-feishu-cli.sh is DEPRECATED since W5 (control plane edition)."
echo "    See header comment for the v2 architecture · team members do NOT need this."
echo ""
read -r -p "Continue anyway (DRI debug only)? [y/N] " confirm
if [[ "${confirm}" != "y" && "${confirm}" != "Y" ]]; then
  echo "Aborted."
  exit 0
fi

echo ""
echo "=== Step 1/5: Install feishu-cli ==="
if command -v feishu-cli >/dev/null 2>&1; then
  echo "  Already installed: $(feishu-cli --version)"
else
  curl -fsSL https://raw.githubusercontent.com/riba2534/feishu-cli/main/install.sh | bash
  echo "  Installed: $(feishu-cli --version)"
fi

echo ""
echo "=== Step 2/5: Check config ==="
if [[ -f ~/.feishu-cli/config.yaml ]]; then
  echo "  Config exists at ~/.feishu-cli/config.yaml"
else
  echo "  ⚠️  No config yet. Run:"
  echo "    feishu-cli config create-app --save"
  echo "  Then 扫码 + 飞书开放平台 → 应用权限管理 → 导入权限"
  echo ""
  echo "  After config, re-run this script."
  exit 1
fi

echo ""
echo "=== Step 3/5: Doctor ==="
if ! feishu-cli doctor; then
  echo "  ❌ doctor failed. Fix issues above first."
  exit 1
fi

echo ""
echo "=== Step 4/5: Find team chat_id (optional · prefer 'search_chat' MCP tool) ==="
if [[ -n "${FEISHU_TEAM_CHAT_ID:-}" ]]; then
  echo "  FEISHU_TEAM_CHAT_ID already set: ${FEISHU_TEAM_CHAT_ID}"
else
  echo "  ℹ️  FEISHU_TEAM_CHAT_ID not set (only needed if you'll use feishu-cli msg send below)."
  echo "  To find it: feishu-cli msg search-chats --query \"AI MIQ\""
  echo "  Or use the multica MCP tool 'search_chat' from Claude Code/Codex."
fi

echo ""
echo "=== Step 5/5: Smoke test (optional) ==="
if [[ -n "${FEISHU_TEAM_CHAT_ID:-}" ]]; then
  read -r -p "  Send a test message to team group via feishu-cli? [y/N] " sm
  if [[ "${sm}" == "y" || "${sm}" == "Y" ]]; then
    feishu-cli msg send \
      --receive-id-type chat_id \
      --receive-id "${FEISHU_TEAM_CHAT_ID}" \
      --text "🤖 feishu-cli smoke test from $(whoami)@$(hostname) at $(date '+%Y-%m-%d %H:%M')"
    echo "  ✅ Message sent. Check team group."
  else
    echo "  Skipped smoke test."
  fi
else
  echo "  Skipped (no FEISHU_TEAM_CHAT_ID)."
fi

echo ""
echo "=== Setup complete ==="
echo ""
echo "DRI reminder · v2 production path: secrets live in multica (\`multica secret set\`),"
echo "config lives in multica (\`multica integration set\`), team members talk to feishu"
echo "via remote MCP tools (notify_team / dm_member / archive_to_wiki / search_chat /"
echo "read_member_dm). This local feishu-cli install is for OPS DEBUG only."
