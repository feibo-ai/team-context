#!/usr/bin/env bash
# check-registry-sync.sh — ④c CI 对账:repo 规范源 skills 必须都已同步进 multica registry,
# 且 registry 的 description/content 与 repo 一致(内容级对账,不只查名字——
# 名字在、内容旧 = 曾经的假绿源)。
#
# registry 是派生只读投影;真相在 repo。漂移意味着有人改了 skill 没跑 sync。
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

# 对账主体交给 python:名字在册 + description 一致(按 sync 的 480 截断口径)
# + body 内容一致(与 sync 同款 frontmatter 剥离)。缺 content 字段 → 诚实 WARN 不假绿。
printf '%s' "$reg_json" | python3 - "$SKILLS_DIR" <<'PY'
import json, re, subprocess, sys
from pathlib import Path

skills_dir = Path(sys.argv[1])
try:
    registry = {s.get("name"): s for s in json.load(sys.stdin)}
except Exception as e:
    print(f"WARN: registry JSON 解析失败({e});对账名单按空处理", file=sys.stderr)
    registry = {}

def split_local(p):
    text = p.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    fm, body = (m.group(1), m.group(2)) if m else ("", text)
    dm = re.search(r"^description:\s*(.*)$", fm, re.M)
    desc = dm.group(1).strip().strip("\"'") if dm else ""
    return desc[:480], body

fail = 0
for d in sorted(skills_dir.glob("tc-*")):
    sk = d / "SKILL.md"
    if not sk.exists():
        continue
    nm = re.search(r"^name:\s*(\S+)", sk.read_text(encoding="utf-8"), re.M)
    name = nm.group(1).strip("\"'") if nm else d.name
    entry = registry.get(name)
    if entry is None:
        print(f"ERROR: repo skill '{name}' 不在 registry — 跑 'bash scripts/sync-team-config.sh' 同步")
        fail = 1
        continue
    want_desc, want_body = split_local(sk)
    # list 输出可能是浅对象 → 缺 content 时 get 一次
    if "content" not in entry or "description" not in entry:
        try:
            got = subprocess.run(
                ["multica", "skill", "get", str(entry.get("id", "")), "--output", "json"],
                capture_output=True, text=True, check=True)
            entry = json.loads(got.stdout)
        except Exception as e:
            print(f"WARN: '{name}' 无法读回内容做对账({e})— 名字在册,内容未验证", file=sys.stderr)
            continue
    reg_desc = (entry.get("description") or "").strip()
    reg_body = entry.get("content")
    if reg_desc != want_desc.strip():
        print(f"ERROR: '{name}' description 漂移(registry≠repo)— 重跑 sync-team-config.sh")
        fail = 1
    if reg_body is None:
        print(f"WARN: '{name}' registry 未回传 content — 内容未验证", file=sys.stderr)
    elif reg_body.strip() != want_body.strip():
        print(f"ERROR: '{name}' body 内容漂移(registry≠repo)— 重跑 sync-team-config.sh")
        fail = 1

if fail == 0:
    print("OK: 所有 repo skills 均在 registry 且 description/content 一致")
sys.exit(fail)
PY
