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
# ⑥ Codex skills-index:Codex 无原生 skill 发现 → 生成索引让它发现 tc-*,
# 并文档化命门B 收口入口(Claude/Codex 两端经 Bash 调同一 publish.py)。
_gen_codex_index() {  # $1=输出路径
  {
    echo "# AI MIQ tc-* skills 索引(Codex 用 · sync-team-config.sh 生成,勿手改)"
    echo
    echo "Codex 无原生 skill 机制。本索引让 Codex 发现团队 tc-* skills 并共享发布入口。"
    echo
    echo "## 发布收口(命门B · Claude/Codex 两端同一 Bash 入口)"
    echo "把字段写成 JSON 调(渲染 + 硬校验 + 命门B 内联发布 + 自检 attachments;别绕开手拼 curl):"
    echo '```'
    echo "python3 $SKILLS_DIR/tc-render/publish.py --type {plan|research|case|handoff} \\"
    echo "  --data fields.json --issue <完整UUID> [--dry-run]"
    echo '```'
    echo
    echo "## Skills"
    for d in "$SKILLS_DIR"/tc-*; do
      [ -f "$d/SKILL.md" ] || continue
      n="$(awk -F': *' '/^name:/{gsub(/["'"'"']/,"",$2);print $2;exit}' "$d/SKILL.md")"
      [ -n "$n" ] || n="$(basename "$d")"
      echo "- **$n** — $(_skill_desc "$d/SKILL.md")"
      echo "  - 正文:\`$d/SKILL.md\`"
    done
  } > "$1.tmp" && mv "$1.tmp" "$1"   # 原子写:中途 abort 不留半截索引(保护已有文件)
}

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

# ⑥ Codex skills-index:生成索引让 Codex 发现 tc-* + 共享命门B 发布入口(派生artifact,每次重生)
_gen_codex_index "$HOME/.codex/skills-index.md"
say "✓ ~/.codex/skills-index.md(Codex 发现 tc-* + 命门B 对称入口)"

# 3) Skills → multica registry(create-or-update + 推 files[] + owner 解析)
#    registry 是派生只读投影:开发机走 git 软链(步骤1),此处把规范源推上去。
if [ "$SKIP_MULTICA" = 0 ] && command -v multica >/dev/null 2>&1; then
  echo "[3] Skills → multica registry (create-or-update + files[])"
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
    # description:整行抽取(内部冒号安全)+ 按字符截 480(CJK 安全),见 _skill_desc。
    desc="$(_skill_desc "$d/SKILL.md" 480)"
    body="$(awk 'f{print} /^---[[:space:]]*$/{c++} c==2 && !f{f=1}' "$d/SKILL.md")"
    owner_name="$(awk -F': *' '/^owner:/{gsub(/["'"'"']/,"",$2);print $2;exit}' "$d/SKILL.md")"
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
        && say "✓ $name 已更新 (id=$id)" || { say "✗ $name 更新失败"; continue; }
    else
      out="$(multica skill create --name "$name" --description "$desc" --content "$body" $owner_flag 2>/dev/null)" \
        && id="$(printf '%s' "$out" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("id",""))' 2>/dev/null)" \
        && say "✓ $name 已创建 (id=$id)" || { say "✗ $name 创建失败"; continue; }
    fi
    [ -n "$id" ] || continue
    # 推 files[](SKILL.md 之外的 bundled 文件;upsert=幂等)
    _each_skill_file "$d" | while IFS= read -r rel; do
      [ -n "$rel" ] || continue
      multica skill files upsert "$id" --path "$rel" --content "$(cat "$d/$rel")" >/dev/null 2>&1 \
        && say "    ✓ file $rel" || say "    ✗ file $rel"
    done
  done
else
  echo "[3] 跳过 multica registry 同步"
fi

echo "== 完成。MCP 配置(含 token)按 docs/SYNC.md 各界面手动配。 =="
