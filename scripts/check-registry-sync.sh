#!/usr/bin/env bash
# check-registry-sync.sh — ④c CI 对账:repo 规范源 skills 必须都已同步进 multica registry。
#
# repo→registry 不一致(repo 有此 skill、registry 缺)→ exit 1(CI fail)。
# registry 是派生只读投影;真相在 repo。漂移意味着有人改了 skill 没跑 sync。
#
# 需要 multica CLI + 已配置 token。无 multica / 无法访问 registry → SKIP(exit 0 + 打印原因),
# 与 tc-render 契约探针同款诚实兜底:本地或 CI 注入 MULTICA_TOKEN 后才真对账。
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
SKILLS_DIR="$REPO/skills"

if ! command -v multica >/dev/null 2>&1; then
  echo "SKIP: multica CLI 不在 PATH(装 multica 或 CI 注入后启用 repo→registry 对账)"
  exit 0
fi

reg_json="$(multica skill list --output json 2>/dev/null)" || {
  echo "SKIP: 无法访问 registry(未配置 token?)— 设 MULTICA_TOKEN / multica setup 后启用对账"
  exit 0
}

reg_names="$(printf '%s' "$reg_json" | python3 -c 'import sys,json
try: print("\n".join(s.get("name","") for s in json.load(sys.stdin)))
except Exception as e: sys.stderr.write("WARN: registry JSON 解析失败(%s);对账名单按空处理\n" % e)')"

fail=0
for d in "$SKILLS_DIR"/tc-*; do
  [ -f "$d/SKILL.md" ] || continue
  name="$(awk -F': *' '/^name:/{gsub(/["'"'"']/,"",$2);print $2;exit}' "$d/SKILL.md")"
  [ -n "$name" ] || name="$(basename "$d")"
  if ! printf '%s\n' "$reg_names" | grep -qx "$name"; then
    echo "ERROR: repo skill '$name' 不在 registry — 跑 'bash scripts/sync-team-config.sh' 同步"
    fail=1
  fi
done

if [ "$fail" = 0 ]; then
  echo "OK: 所有 repo skills 均已在 registry"
fi
exit "$fail"
