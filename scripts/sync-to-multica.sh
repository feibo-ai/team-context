#!/usr/bin/env bash
# sync-to-multica.sh — import skills/ to current multica workspace
# Usage: ./scripts/sync-to-multica.sh <github-url>
set -euo pipefail

REPO_URL="${1:-}"
if [[ -z "${REPO_URL}" ]]; then
  echo "Usage: $0 <github-url>"
  echo "Example: $0 https://github.com/multica-ai/team-context"
  exit 2
fi

# Pre-flight
multica auth status > /dev/null || {
  echo "ERROR: not authenticated. Run: multica login" >&2
  exit 1
}

multica daemon status 2>/dev/null | grep -qi "running" || {
  echo "WARN: daemon not running. Starting..." >&2
  multica daemon start
}

# Identify current workspace
WS="$(multica workspace list 2>/dev/null | head -1 || echo unknown)"
echo "Target workspace: ${WS}"

# Import. multica skill import scans the repo's skills/ subdir.
multica skill import --url "${REPO_URL}"

echo ""
echo "Now applying autopilots (requires daemon running)..."
~/team-context/scripts/apply-autopilots.sh

echo ""
echo "Skills imported. Verify with: multica skill list"
