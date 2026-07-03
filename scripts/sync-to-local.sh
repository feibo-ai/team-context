#!/usr/bin/env bash
# sync-to-local.sh — DEPRECATED 薄壳:统一入口是 sync-team-config.sh。
# 保留此文件只为兼容旧习惯/旧文档;软链逻辑单源在 sync-team-config.sh
# (含 ~/.claude/skills + ~/.agents/skills 双端软链 + 失效旧名软链清理)。
set -euo pipefail
echo "[deprecated] sync-to-local.sh → 转发 sync-team-config.sh --no-multica" >&2
exec bash "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/sync-team-config.sh" --no-multica
