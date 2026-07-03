#!/usr/bin/env bash
# decommission-personal-autopilots.sh — 30→5 收敛(2026-07-03 决策)的一次性下线脚本。
#
# 个人 autopilot 的信息 = 团队卡按人归并后的行(纯冗余),且个人机器
# 在 cron 时间点离线 → run 被 admission gate 静默 skip(丢失)。收敛后
# 只保留 team scope 5 个,跑在 DRI 常驻机 / cloud runtime。
#
# 做什么(可逆组合,不 delete):
#   1. 暂停所有个人身份 agent(助理·* 且 ≠ 助理·全队)名下的 autopilot(update --status paused)
#   2. archive 这些 agent(admission gate 双保险;status ≠ idle 的跳过并提示)
#
# 用法:
#   bash scripts/decommission-personal-autopilots.sh            # dry-run(只打印将做什么)
#   bash scripts/decommission-personal-autopilots.sh --apply    # 真执行(DRI 跑 · 需 workspace admin)
set -euo pipefail

APPLY=0
[ "${1:-}" = "--apply" ] && APPLY=1
say() { printf '  %s\n' "$*"; }

command -v multica >/dev/null 2>&1 || { echo "ERROR: multica CLI 不在 PATH" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "ERROR: 需要 jq" >&2; exit 1; }

agents_json=$(multica agent list --output json)
autopilots_json=$(multica autopilot list --output json 2>/dev/null || echo '[]')

# 个人身份 agent = 助理·* 除了 助理·全队
personal=$(printf '%s' "$agents_json" | jq -r '[.[] | select((.name // "" | startswith("助理·")) and .name != "助理·全队")]')
count=$(printf '%s' "$personal" | jq 'length')
[ "$count" = 0 ] && { echo "没有个人身份 agent(助理·* 且 ≠ 助理·全队)· 无事可做"; exit 0; }

echo "发现 ${count} 个个人身份 agent$([ "$APPLY" = 1 ] || printf ' · DRY-RUN(加 --apply 真执行)')"

printf '%s' "$personal" | jq -c '.[]' | while IFS= read -r a; do
  aid=$(printf '%s' "$a" | jq -r '.id')
  aname=$(printf '%s' "$a" | jq -r '.name')
  astatus=$(printf '%s' "$a" | jq -r '.status // empty')
  echo "— ${aname} (${aid})"

  # 1) 暂停名下 autopilot(list 返回 {autopilots:[...],total};agent 绑定字段 = assignee_type/assignee_id)
  printf '%s' "$autopilots_json" | jq -r --arg aid "$aid" \
    '(.autopilots // .)[] | select((.assignee_type // "") == "agent" and (.assignee_id // "") == $aid and (.status // "active") == "active") | .id + "\t" + (.title // .name // "?")' \
  | while IFS=$'\t' read -r apid aptitle; do
      [ -n "$apid" ] || continue
      if [ "$APPLY" = 1 ]; then
        multica autopilot update "$apid" --status paused >/dev/null \
          && say "‖ autopilot paused: ${aptitle} (${apid})" \
          || say "⚠️ pause 失败: ${aptitle} (${apid}) · 手动: multica autopilot update ${apid} --status paused"
      else
        say "[dry-run] 将 pause autopilot: ${aptitle} (${apid})"
      fi
    done

  # 2) archive agent(双保险;非 idle 跳过防砍 in-flight run)
  if [ -n "$astatus" ] && [ "$astatus" != idle ]; then
    say "⚠️ agent status=${astatus} ≠ idle · 跳过 archive,run 结束后重跑本脚本"
    continue
  fi
  if [ "$APPLY" = 1 ]; then
    multica agent archive "$aid" >/dev/null \
      && say "▣ agent archived: ${aname}" \
      || say "⚠️ archive 失败: ${aname} · 手动: multica agent archive ${aid}"
  else
    say "[dry-run] 将 archive agent: ${aname}"
  fi
done

echo ""
echo "完成。验证: multica agent list · multica autopilot list"
[ "$APPLY" = 1 ] || echo "(这是 dry-run · 确认无误后加 --apply)"
