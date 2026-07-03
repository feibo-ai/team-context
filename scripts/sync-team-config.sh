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
# 用法:  bash scripts/sync-team-config.sh              # 全同步(create-or-update + 推 files[])
#         bash scripts/sync-team-config.sh --no-multica   # 跳过 multica registry 推送
#         bash scripts/sync-team-config.sh --dry-run      # 只打印 registry 将做什么,不改动
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
GLOBAL_MD="$REPO/claude_md_team_global.md"
SKILLS_DIR="$REPO/skills"
DRY_RUN=0
SKIP_MULTICA=0
for arg in "$@"; do
  case "$arg" in
    --no-multica) SKIP_MULTICA=1 ;;
    --dry-run)    DRY_RUN=1 ;;
    *) echo "unknown arg: $arg (use --no-multica | --dry-run)" >&2; exit 2 ;;
  esac
done

say() { printf '  %s\n' "$*"; }

# registry skill name → id(stdin = `multica skill list --output json`)
_json_find_id() {
  python3 -c 'import sys,json
n=sys.argv[1]
try: ss=json.load(sys.stdin)
except Exception: ss=[]
print(next((s.get("id","") for s in ss if s.get("name")==n), ""))' "$1"
}
# owner 名字 → user UUID(stdin = `multica user list --output json`);空名字→空
_json_find_owner() {
  python3 -c 'import sys,json
n=sys.argv[1]
try: us=json.load(sys.stdin)
except Exception: us=[]
print(next((u.get("user_id","") for u in us if u.get("name")==n), "") if n else "")' "$1"
}
# skill 目录里 bundled 文件 = registry files[]。排除 SKILL.md(正文走 --content)、
# tests/(CI 资产非 skill 运行时)、缓存。skill-relative 路径。
_each_skill_file() {
  ( cd "$1" && find . -type f ! -name SKILL.md ! -path '*/tests/*' ! -path '*/__pycache__/*' ! -name '*.pyc' | sed 's|^\./||' )
}
# SKILL.md description 整行抽取(取冒号后整行,去引号,可选按字符截);内部冒号安全、CJK 安全
_skill_desc() {  # $1=SKILL.md 路径 $2=最大字符数(可选,0/省略=不截)
  python3 -c 'import sys,re
mx = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] else 0
for line in open(sys.argv[1], encoding="utf-8"):
    m = re.match(r"^description:\s*(.*)$", line)
    if m:
        v = m.group(1).strip().strip("\"\x27")
        print(v[:mx] if mx else v); break' "$1" "${2:-}"
}
# skill-pack.yaml 里查 owner(治理字段已移出 SKILL.md frontmatter,单源在 pack manifest)
_pack_owner() {  # $1=skill name
  python3 -c 'import re,sys
name=sys.argv[2]
t=open(sys.argv[1],encoding="utf-8").read()
m=re.search(r"- name:\s*"+re.escape(name)+r"\s*\n\s*owner:\s*(\S+)",t)
print(m.group(1) if m else "")' "$REPO/skill-pack.yaml" "$1" 2>/dev/null || true
}
# 清掉指向本仓但目标已消失的 skill 软链(改名/合并后的旧名残留会遮蔽新 skill)
_prune_stale_links() {  # $1=skills 安装根
  [ -d "$1" ] || return 0
  for link in "$1"/tc-*; do
    [ -L "$link" ] || continue
    target="$(readlink "$link")"
    case "$target" in
      "$SKILLS_DIR"/*) [ -d "$target" ] || { rm "$link"; say "✗ 清理失效软链 $(basename "$link")"; } ;;
    esac
  done
}

echo "== 规范源:$REPO =="

# 1) Skills → Claude Code(~/.claude/skills)+ Codex 原生(~/.agents/skills)
#    Codex 原生实现 agentskills.io 标准:扫 ~/.agents/skills,靠 description 自动触发,
#    与 Claude Code 同一份标准 skill 目录 → 旧 skills-index.md hack 已删除。
echo "[1] Skills → Claude Code (~/.claude/skills) + Codex (~/.agents/skills),软链"
mkdir -p "$HOME/.claude/skills" "$HOME/.agents/skills"
_prune_stale_links "$HOME/.claude/skills"
_prune_stale_links "$HOME/.agents/skills"
for d in "$SKILLS_DIR"/tc-*; do
  [ -d "$d" ] || continue
  ln -sfn "$d" "$HOME/.claude/skills/$(basename "$d")"
  ln -sfn "$d" "$HOME/.agents/skills/$(basename "$d")"
  say "✓ $(basename "$d")"
done
# Claude Desktop 的本地 agent 模式 skills-plugin 复用 ~/.claude/skills/(同一软链即覆盖)。

# 2) 团队全局规则 → Claude Code 全局 CLAUDE.md + Codex 全局 AGENTS.md(软链 → 自动最新)
echo "[2] 全局规则 → Claude Code CLAUDE.md + Codex AGENTS.md (软链)"
mkdir -p "$HOME/.claude" "$HOME/.codex"
ln -sfn "$GLOBAL_MD" "$HOME/.claude/CLAUDE.md"; say "✓ ~/.claude/CLAUDE.md → claude_md_team_global.md"
ln -sfn "$GLOBAL_MD" "$HOME/.codex/AGENTS.md";  say "✓ ~/.codex/AGENTS.md → claude_md_team_global.md"
# 旧的 ~/.codex/skills-index.md 是派生 artifact,清掉避免与原生 skill 双份发现源
[ -f "$HOME/.codex/skills-index.md" ] && rm "$HOME/.codex/skills-index.md" && say "✗ 清理旧 ~/.codex/skills-index.md(Codex 已原生发现 skills)"

# 3) Skills → multica registry(create-or-update + 推 files[] + owner 解析)
#    registry 是派生只读投影:开发机走 git 软链(步骤1),此处把规范源推上去。
if [ "$SKIP_MULTICA" = 0 ] && command -v multica >/dev/null 2>&1; then
  echo "[3] Skills → multica registry (create-or-update + files[])"
  PUSH_FAILS=0
  skills_json="$(multica skill list --output json 2>/dev/null || echo '[]')"
  # `multica user list` 是批次2 新增命令(owner 名字→UUID 解析源);旧二进制无此命令 → [].
  users_json="$(multica user list --output json 2>/dev/null || echo '[]')"
  users_available=1
  if [ "$(printf '%s' "$users_json" | tr -d '[:space:]')" = "[]" ]; then
    users_available=0
    say "· user list 不可用/无成员 → 本次 owner 全部留空(待新二进制部署 user list 后启用解析)"
  fi
  for d in "$SKILLS_DIR"/tc-*; do
    [ -f "$d/SKILL.md" ] || continue
    name="$(awk -F': *' '/^name:/{gsub(/["'"'"']/,"",$2);print $2;exit}' "$d/SKILL.md")"
    [ -n "$name" ] || name="$(basename "$d")"
    # description:整行抽取(内部冒号安全)+ 按字符截 1024(agentskills.io spec 上限;
    # 经核实 server/CLI 无长度限制,旧 480 是本脚本单方面的历史截断。
    # validate-skills.py 已把 description 硬限 ≤450 → 此截断纯兜底,不丢内容)
    desc="$(_skill_desc "$d/SKILL.md" 1024)"
    body="$(awk 'f{print} /^---[[:space:]]*$/{c++} c==2 && !f{f=1}' "$d/SKILL.md")"
    # owner 单源 skill-pack.yaml(SKILL.md frontmatter 只留标准字段 name/description)
    owner_name="$(_pack_owner "$name")"
    id="$(printf '%s' "$skills_json" | _json_find_id "$name")"
    # owner_flag unquoted on use → 0 或 2 个 arg(UUID 无空格);避免 bash 3.2 空数组+set -u 坑
    owner_flag=""
    owner_uuid=""
    if [ "$users_available" = 1 ] && [ -n "$owner_name" ]; then
      owner_uuid="$(printf '%s' "$users_json" | _json_find_owner "$owner_name")"
      if [ -n "$owner_uuid" ]; then
        owner_flag="--owner $owner_uuid"
      else
        say "  ! $name owner='$owner_name' 查无此人 → owner 留空"
      fi
    fi

    if [ "$DRY_RUN" = 1 ]; then
      if [ -n "$id" ]; then say "· [dry-run] update $name (id=$id) owner=${owner_uuid:-—}"
      else say "· [dry-run] create $name owner=${owner_uuid:-—}"; fi
      _each_skill_file "$d" | while IFS= read -r rel; do [ -n "$rel" ] && say "    [dry-run] file $rel"; done
      continue
    fi

    if [ -n "$id" ]; then
      multica skill update "$id" --description "$desc" --content "$body" $owner_flag >/dev/null 2>&1 \
        && say "✓ $name 已更新 (id=$id)" || { say "✗ $name 更新失败"; PUSH_FAILS=$((PUSH_FAILS + 1)); continue; }
    else
      out="$(multica skill create --name "$name" --description "$desc" --content "$body" $owner_flag 2>/dev/null)" \
        && id="$(printf '%s' "$out" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("id",""))' 2>/dev/null)" \
        && say "✓ $name 已创建 (id=$id)" || { say "✗ $name 创建失败"; PUSH_FAILS=$((PUSH_FAILS + 1)); continue; }
    fi
    [ -n "$id" ] || continue
    # 推 files[](SKILL.md 之外的 bundled 文件;upsert=幂等)。
    # 用进程替换而非管道 while:管道子 shell 里的失败计数出不来,曾导致半推静默假绿。
    while IFS= read -r rel; do
      [ -n "$rel" ] || continue
      if multica skill files upsert "$id" --path "$rel" --content "$(cat "$d/$rel")" >/dev/null 2>&1; then
        say "    ✓ file $rel"
      else
        say "    ✗ file $rel"
        PUSH_FAILS=$((PUSH_FAILS + 1))
      fi
    done < <(_each_skill_file "$d")
    # 写后校验:读回 registry,description+content 必须与源一致——
    # 半推/静默截断/编码损坏在此现形,而不是等成员 pull 到坏文件才发现
    if multica skill get "$id" --output json 2>/dev/null \
       | REL_DESC="$desc" REL_BODY="$body" python3 -c '
import json, os, sys
try:
    s = json.load(sys.stdin)
except Exception:
    sys.exit(1)
ok = (s.get("description", "").strip() == os.environ["REL_DESC"].strip()
      and (s.get("content") or "").strip() == os.environ["REL_BODY"].strip())
sys.exit(0 if ok else 1)'; then
      say "    ✓ 写后校验(description+content 读回一致)"
    else
      say "    ✗ 写后校验失败(registry 读回 ≠ 源)"
      PUSH_FAILS=$((PUSH_FAILS + 1))
    fi
  done
  if [ "${PUSH_FAILS:-0}" -gt 0 ]; then
    echo "ERROR: registry 推送有 ${PUSH_FAILS} 处失败(见上方 ✗)· registry 处于半推状态,修复后重跑" >&2
    exit 1
  fi
else
  echo "[3] 跳过 multica registry 同步"
fi

echo "== 完成。MCP 配置(含 token)按 docs/SYNC.md 各界面手动配。 =="
