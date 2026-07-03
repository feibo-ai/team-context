#!/usr/bin/env bash
# sync-to-multica.sh — DEPRECATED 薄壳:registry 推送单源在 sync-team-config.sh。
#
# 旧实现走 `multica skill import --url <github-url>`,对多 skill 仓库不工作
# (import 期望 URL 处恰好一个 SKILL.md),且尾部隐式串联 autopilot 部署——
# skill 同步与 autopilot 部署是两件事,不该捆绑。
# 现在:skill → registry 走 sync-team-config.sh(create-or-update + files[] + 失败即非零退出);
# autopilot 部署显式跑 team-autopilot.sh / my-autopilot.sh。
set -euo pipefail
[ $# -gt 0 ] && echo "[deprecated] 忽略参数 '$*'(不再走 skill import --url)" >&2
echo "[deprecated] sync-to-multica.sh → 转发 sync-team-config.sh(registry 推送单源)" >&2
exec bash "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/sync-team-config.sh"
