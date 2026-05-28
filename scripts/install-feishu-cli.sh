#!/usr/bin/env bash
echo "⚠️  DEPRECATED · feishu-cli direct install is no longer required for team members." >&2
echo "    team-context-mcp v0.2+ exposes 9 remote MCP tools (notify_team / dm_member /" >&2
echo "    archive_to_wiki / search_chat / read_member_dm + 5 moved) that talk to feishu" >&2
echo "    via lark Node.js SDK inside the remote server container." >&2
echo "" >&2
echo "    DRI debug only · proceeding in 3s · Ctrl-C to abort..." >&2
sleep 3
# install-feishu-cli.sh — one-shot installer + verifier for feishu-cli
# Per AI MIQ SOP plan · ref docs/integrations/feishu-cli.md
set -euo pipefail

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
  echo "  Then 扫码 + 飞书开放平台 → 应用权限管理 → 导入权限 (见 docs/integrations/feishu-cli.md)"
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
echo "=== Step 4/5: Find team chat_id ==="
if [[ -n "${FEISHU_TEAM_CHAT_ID:-}" ]]; then
  echo "  FEISHU_TEAM_CHAT_ID already set: ${FEISHU_TEAM_CHAT_ID}"
else
  echo "  ⚠️  FEISHU_TEAM_CHAT_ID not set."
  echo "  Run: feishu-cli msg search-chats --query \"AI MIQ\""
  echo "  Then: echo 'export FEISHU_TEAM_CHAT_ID=\"oc_xxx\"' >> ~/.zshrc && source ~/.zshrc"
  echo "  Re-run after."
  exit 1
fi

echo ""
echo "=== Step 5/5: Smoke test ==="
read -p "  Send test message to team group? [y/N] " confirm
if [[ "${confirm}" == "y" || "${confirm}" == "Y" ]]; then
  feishu-cli msg send \
    --receive-id-type chat_id \
    --receive-id "${FEISHU_TEAM_CHAT_ID}" \
    --text "🤖 feishu-cli smoke test from $(whoami)@$(hostname) at $(date '+%Y-%m-%d %H:%M')"
  echo "  ✅ Message sent. Check team group."
else
  echo "  Skipped smoke test."
fi

echo ""
echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "  - If you're DRI: run Task A13 Step 5 to inject FEISHU_TEAM_CHAT_ID into 4 autopilot agents"
echo "  - If you're EXEC: you're done. autopilots running on any workstation can now push to feishu."
