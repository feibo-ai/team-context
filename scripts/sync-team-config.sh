#!/usr/bin/env bash
# sync-team-config.sh — 把 team-context 的规范源同步到本机各 agent 界面。
#
# 规范源(本 repo 内,唯一真相):
#   skills/tc-*/SKILL.md        ← 团队 SOP skills
#   claude_md_team_global.md    ← 团队全局规则(CLAUDE.md / AGENTS.md 的源)
#
# 同步策略:能软链就软链(改源 → 各界面自动最新);multica registry 走 CLI 推送。
# MCP 配置不在此脚本(含 per-user token)—— 见 docs/SYNC.md 手动按界面配。
#
# 用法:  bash scripts/sync-team-config.sh           # 全同步
#         bash scripts/sync-team-config.sh --no-multica   # 跳过 multica 推送
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
GLOBAL_MD="$REPO/claude_md_team_global.md"
SKILLS_DIR="$REPO/skills"
SKIP_MULTICA="${1:-}"

say() { printf '  %s\n' "$*"; }

echo "== 规范源:$REPO =="

# 1) Skills → Claude Code(软链每个 tc-* 进 ~/.claude/skills/)
echo "[1] Skills → Claude Code (~/.claude/skills/, 软链)"
mkdir -p "$HOME/.claude/skills"
for d in "$SKILLS_DIR"/tc-*; do
  [ -d "$d" ] || continue
  ln -sfn "$d" "$HOME/.claude/skills/$(basename "$d")"
  say "✓ $(basename "$d")"
done
# Claude Desktop 的本地 agent 模式 skills-plugin 复用 ~/.claude/skills/(同一软链即覆盖)。

# 2) 团队全局规则 → Claude Code 全局 CLAUDE.md + Codex 全局 AGENTS.md(软链 → 自动最新)
echo "[2] 全局规则 → Claude Code CLAUDE.md + Codex AGENTS.md (软链)"
mkdir -p "$HOME/.claude" "$HOME/.codex"
ln -sfn "$GLOBAL_MD" "$HOME/.claude/CLAUDE.md"; say "✓ ~/.claude/CLAUDE.md → claude_md_team_global.md"
ln -sfn "$GLOBAL_MD" "$HOME/.codex/AGENTS.md";  say "✓ ~/.codex/AGENTS.md → claude_md_team_global.md"
# 注:Codex 无原生 skill 机制 —— AGENTS.md 把 tc-* 当"流程描述"读;skill 正文经 multica registry / 直接读 repo。

# 3) Skills → multica registry(共享存储:daemon/autopilot + 任意界面经 MCP 发现)
if [ "$SKIP_MULTICA" != "--no-multica" ] && command -v multica >/dev/null 2>&1; then
  echo "[3] Skills → multica registry (multica skill, 缺则建)"
  EXISTING="$(multica skill list 2>/dev/null | awk 'NR>1{print $2}')" || EXISTING=""
  for d in "$SKILLS_DIR"/tc-*; do
    [ -f "$d/SKILL.md" ] || continue
    name="$(awk -F': *' '/^name:/{gsub(/["'"'"']/,"",$2);print $2;exit}' "$d/SKILL.md")"
    [ -n "$name" ] || name="$(basename "$d")"
    if printf '%s\n' "$EXISTING" | grep -qx "$name"; then
      say "· $name 已在 registry(跳过;改正文用 multica skill update)"
    else
      desc="$(awk -F': *' '/^description:/{gsub(/^["'"'"']|["'"'"']$/,"",$2);print substr($2,1,480);exit}' "$d/SKILL.md")"
      body="$(awk 'f{print} /^---[[:space:]]*$/{c++} c==2 && !f{f=1}' "$d/SKILL.md")"
      if multica skill create --name "$name" --description "$desc" --content "$body" >/dev/null 2>&1; then
        say "✓ $name 已推送 registry"
      else
        say "✗ $name 推送失败(手动 multica skill create)"
      fi
    fi
  done
else
  echo "[3] 跳过 multica registry 同步"
fi

echo "== 完成。MCP 配置(含 token)按 docs/SYNC.md 各界面手动配。 =="
