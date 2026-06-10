#!/usr/bin/env bash
# _autopilot-common.sh — shared logic for my-autopilot.sh (个人版) + team-autopilot.sh (团队版).
#
# NOT executable on its own · both entry scripts `source` it.
# Per spec 2026-05-28 §3.1 + plan TEA-93 (2026-06-10 autopilot-agent-consolidation):
# the only real difference between the two entry scripts is SCOPE + naming SUFFIX;
# everything else (preflight, runtime pick, PB-04 lint, agent/autopilot build) is shared here.
#
# Object model (TEA-93 · 命名规范 standards/feishu-card-style.md):
# ONE identity agent per scope (助理·<显示名>) carrying
# instructions (single source: autopilots/_agent-instructions.md) + custom_env; N thin
# autopilots per scope pointing at that agent, each carrying only task-specific prompt.
# Closing step archives legacy per-kind agents (<kind>-bot-<suffix>).
# Capture-then-jq throughout to avoid grep/head SIGPIPE'ing the upstream command
# under `set -o pipefail`.

set -euo pipefail

AC_REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AC_AUTOPILOTS_DIR="${AC_REPO_DIR}/autopilots"
AC_INSTRUCTIONS_FILE="${AC_AUTOPILOTS_DIR}/_agent-instructions.md"
AC_KINDS=(daily-summary daily-kickoff monday-kickoff wednesday-stats monthly-health)

# tcmcp-remote lives in the cloud (Zeabur) since W5 · agents reach feishu through it.
: "${TCMCP_REMOTE_URL:=https://mcp.teamctx.actionow.ai/mcp}"

ac_die() { echo "ABORT: $*" >&2; exit 1; }

# Is $1 one of the 5 known kinds?
ac_is_kind() {
  local k
  for k in "${AC_KINDS[@]}"; do [ "$1" = "$k" ] && return 0; done
  return 1
}

# kind(英文文件名/代码标识) → 任务中文名(线上 autopilot title 用 · 单源映射,
# 规范见 standards/feishu-card-style.md §1;case 写法兼容 macOS bash 3.2 无关联数组)
ac_kind_cn() {
  case "$1" in
    daily-kickoff)   printf '每日开工' ;;
    daily-summary)   printf '每日总结' ;;
    monday-kickoff)  printf '周一计划' ;;
    wednesday-stats) printf '周三体检' ;;
    monthly-health)  printf '月度健康' ;;
    *) ac_die "ac_kind_cn: 未知 kind $1" ;;
  esac
}

ac_preflight() {
  command -v jq >/dev/null 2>&1 || ac_die "缺 jq · brew install jq"
  command -v yq >/dev/null 2>&1 || ac_die "缺 yq · brew install yq"
  multica auth status >/dev/null 2>&1 || ac_die "未登录 · 先 multica login"
  # capture-then-grep: grep -q would SIGPIPE `multica daemon status` under pipefail
  local ds; ds=$(multica daemon status 2>&1 || true)
  printf '%s' "$ds" | grep -qi running || ac_die "daemon 离线 · 先 multica daemon start (离线日 autopilot 静默 skip)"
  [ -n "${TCMCP_AGENT_TOKEN:-}" ] || ac_die "TCMCP_AGENT_TOKEN 未设 · export TCMCP_AGENT_TOKEN=\$MULTICA_TOKEN"
  # agent instructions 单源必须存在且非空(注空 instructions = 砍掉所有通用约束)
  [ -s "$AC_INSTRUCTIONS_FILE" ] || ac_die "缺 ${AC_INSTRUCTIONS_FILE} (agent instructions 单源) 或文件为空"
}

# $1 = provider (codex|claude|hermes) → echoes one online runtime id (or aborts)
ac_select_runtime() {
  local p="$1" out rid
  out=$(multica runtime list --output json)
  rid=$(printf '%s' "$out" | jq -r --arg p "$p" '[.[] | select(.provider==$p and .status=="online")][0].id // empty')
  [ -n "$rid" ] || ac_die "没有在线的 $p runtime · 先 multica daemon start (provider 拼错? codex|claude|hermes)"
  printf '%s' "$rid"
}

# $1 = yaml path · mirrors CI PB-04 lint (SOP CRITICAL gate · 三处 lint 同步: lint.yml / tc-ops/autopilot_lint.py / 这里)
ac_lint_yaml() {
  local yaml="$1" name g fc_count fc_lines budget fp_count
  name=$(yq eval '.name' "$yaml")
  g=$(yq eval '.guardrails' "$yaml")
  [[ "$g" == "null" || -z "$g" ]] && ac_die "${name}: 缺 guardrails 段 (PB-04 违反)"
  fc_count=$(yq eval '.guardrails.forbidden_commands | length' "$yaml")
  { [ "$fc_count" = null ] || (( fc_count < 5 )); } && ac_die "${name}: forbidden_commands ${fc_count} 条 (< 5)"
  fc_lines=$(yq eval '.guardrails.forbidden_commands[]' "$yaml")
  printf '%s' "$fc_lines" | grep -qi "git push" || ac_die "${name}: forbidden_commands 缺 'git push'"
  fp_count=$(yq eval '.guardrails.forbidden_paths | length' "$yaml")
  { [ "$fp_count" = null ] || (( fp_count < 1 )); } && ac_die "${name}: forbidden_paths 需 ≥ 1 条"
  budget=$(yq eval '.guardrails.max_budget_usd' "$yaml")
  [[ -z "$budget" || "$budget" == null ]] && ac_die "${name}: 缺 max_budget_usd"
  if (( budget > 150 )); then ac_die "${name}: max_budget_usd ${budget} > 150 硬上限 (PB-04)"; fi
}

# $1 = scope (team|email) → echoes display name (member list 显示名 · team=全队 · fallback email 前缀)
ac_scope_display_name() {
  local scope="$1" members dn
  if [ "$scope" = team ]; then printf '全队'; return 0; fi
  members=$(multica workspace member list --output json 2>/dev/null || echo '[]')
  dn=$(printf '%s' "$members" | jq -r --arg e "$scope" '[.[] | select(.email==$e)][0].name // empty')
  [ -n "$dn" ] && printf '%s' "$dn" || printf '%s' "${scope%@*}"
}

# $1=runtime-id $2=scope $3=display(范围显示名) → stdout = agent id (progress lines go to stderr)
# Idempotent by name=助理·<显示名>: create with instructions + 4-key env;
# on reuse sync runtime binding + instructions drift (env 只增不改不删 · reuse 不碰 env).
ac_ensure_agent() {
  local rid="$1" scope="$2" display="$3"
  local agent_name="助理·${display}"
  local instr; instr="$(cat "$AC_INSTRUCTIONS_FILE")"
  [ -n "$instr" ] || ac_die "${AC_INSTRUCTIONS_FILE} 读出来为空 · 拒绝注入空 instructions"

  local agents agent_id
  agents=$(multica agent list --output json)
  agent_id=$(printf '%s' "$agents" | jq -r --arg n "$agent_name" '[.[] | select(.name==$n)][0].id // empty')

  if [ -z "$agent_id" ]; then
    local envfile created
    envfile=$(mktemp); chmod 600 "$envfile"
    # jq -n builds the JSON safely (no shell interpolation of token into JSON)
    jq -n --arg url "$TCMCP_REMOTE_URL" --arg tok "$TCMCP_AGENT_TOKEN" --arg scope "$scope" --arg sname "$display" \
      '{TCMCP_REMOTE_URL:$url, TCMCP_AGENT_TOKEN:$tok, AUTOPILOT_SCOPE:$scope, AUTOPILOT_SCOPE_NAME:$sname}' > "$envfile"
    created=$(multica agent create --name "$agent_name" --runtime-id "$rid" \
      --visibility workspace --custom-env-file "$envfile" --instructions "$instr" --output json) \
      || { rm -f "$envfile"; ac_die "agent create 失败: ${agent_name}"; }
    rm -f "$envfile"
    agent_id=$(printf '%s' "$created" | jq -r '.id // empty')
    [ -n "$agent_id" ] || ac_die "agent create 没返回 id: ${agent_name}"
    echo "  + agent ${agent_name} (${agent_id}) · runtime ${rid} · scope=${scope}" >&2
  else
    # runtime 重绑检测 (换机 / 换 provider / daemon 重启后 runtime id 会变)
    local cur_rid
    cur_rid=$(printf '%s' "$agents" | jq -r --arg n "$agent_name" '[.[] | select(.name==$n)][0].runtime_id // empty')
    if [ -n "$cur_rid" ] && [ "$cur_rid" != "$rid" ]; then
      echo "  ! agent ${agent_name} runtime 变了 (${cur_rid} → ${rid}) · 重绑" >&2
      multica agent update "$agent_id" --runtime-id "$rid" >/dev/null 2>&1 \
        || echo "  ⚠️ 重绑失败 · 手动: multica agent update ${agent_id} --runtime-id ${rid} / web UI 改绑" >&2
    fi
    # instructions 漂移同步 (单源文件改了 → 推到 agent)
    local cur_instr
    cur_instr=$(printf '%s' "$agents" | jq -r --arg n "$agent_name" '[.[] | select(.name==$n)][0].instructions // empty')
    if [ "$cur_instr" != "$instr" ]; then
      multica agent update "$agent_id" --instructions "$instr" >/dev/null
      echo "  ~ agent ${agent_name} (${agent_id}) instructions 同步自 _agent-instructions.md" >&2
    else
      echo "  = agent ${agent_name} (${agent_id}) 复用 (runtime/instructions 未变)" >&2
    fi
  fi
  printf '%s' "$agent_id"
}

# $1=kind $2=agent-id $3=scope $4=display(范围显示名) · ensure 该 kind 的瘦 autopilot 指向 scope 级 agent
ac_build_one() {
  local kind="$1" agent_id="$2" scope="$3" display="$4"
  local yaml="${AC_AUTOPILOTS_DIR}/${kind}.yaml"
  [ -f "$yaml" ] || ac_die "${yaml} 不存在"
  ac_lint_yaml "$yaml"

  local mode desc prompt cron tz
  mode=$(yq eval '.mode' "$yaml")
  desc=$(yq eval '.description' "$yaml")
  prompt=$(yq eval '.prompt' "$yaml")
  cron=$(yq eval '.trigger.cron' "$yaml")
  tz=$(yq eval '.trigger.timezone' "$yaml")

  # 个人版降噪 (spec §4.1 default): 个人 scope 下 create_issue → run_only · 只推群不建 issue
  if [ "$scope" != team ] && [ "$mode" = create_issue ]; then
    mode=run_only
  fi

  local autopilot_title; autopilot_title="$(ac_kind_cn "$kind")·${display}"
  # 瘦 description = YAML desc + 任务差异 prompt (通用约束在 agent instructions 单源 · 不进 description)
  local full_desc; full_desc=$(printf '%s\n\n%s' "$desc" "$prompt")

  local apid aps
  aps=$(multica autopilot list --output json 2>/dev/null || echo '{}')
  apid=$(printf '%s' "$aps" | jq -r --arg t "$autopilot_title" '[.autopilots[]? | select(.title==$t)][0].id // empty')
  if [ -n "$apid" ]; then
    multica autopilot update "$apid" --description "$full_desc" --agent "$agent_id" >/dev/null
    echo "  = autopilot ${autopilot_title} (${apid}) 就绪 (desc/agent 已同步)"
  else
    local out
    out=$(multica autopilot create --title "$autopilot_title" --description "$full_desc" \
      --mode "$mode" --agent "$agent_id" --output json)
    apid=$(printf '%s' "$out" | jq -r '.id // empty')
    [ -n "$apid" ] || ac_die "autopilot create 失败: ${autopilot_title}"
    if [ "$mode" = create_issue ]; then
      local tt; tt=$(yq eval '.issue_title_template // ""' "$yaml")
      [ -n "$tt" ] && multica autopilot update "$apid" --issue-title-template "$tt" >/dev/null
    fi
    echo "  + autopilot ${autopilot_title} (${apid}) · mode=${mode}"
  fi

  # trigger: add if missing, else update cron (idempotent · 不重复建 cron)
  local trig apget
  apget=$(multica autopilot get "$apid" --output json 2>/dev/null || echo '{}')
  trig=$(printf '%s' "$apget" | jq -r '[.triggers[]? | select(.kind=="schedule")][0].id // empty')
  if [ -z "$trig" ]; then
    multica autopilot trigger-add "$apid" --kind schedule --cron "$cron" --timezone "$tz" >/dev/null
  else
    multica autopilot trigger-update "$apid" "$trig" --cron "$cron" >/dev/null
  fi

  echo "AUTOPILOT_OK ${autopilot_title} ${apid}"
}

# $1=suffix · 收尾: archive 本 scope 的 legacy per-kind agent (<kind>-bot-<suffix>)
# 幂等: list 不含 archived → 第二次跑找不到 → 无输出。status 非 idle 的跳过并警告(避免砍 in-flight run)。
ac_archive_legacy() {
  local suffix="$1" agents k legacy_name legacy_id legacy_status
  agents=$(multica agent list --output json)
  for k in "${AC_KINDS[@]}"; do
    legacy_name="${k}-bot-${suffix}"
    legacy_id=$(printf '%s' "$agents" | jq -r --arg n "$legacy_name" '[.[] | select(.name==$n)][0].id // empty')
    [ -n "$legacy_id" ] || continue
    legacy_status=$(printf '%s' "$agents" | jq -r --arg n "$legacy_name" '[.[] | select(.name==$n)][0].status // empty')
    if [ "$legacy_status" != idle ]; then
      echo "  ⚠️ legacy agent ${legacy_name} status=${legacy_status} ≠ idle · 跳过 archive,跑完后重跑本脚本收尾"
      continue
    fi
    multica agent archive "$legacy_id" >/dev/null \
      && echo "  - legacy agent ${legacy_name} (${legacy_id}) archived" \
      || echo "  ⚠️ archive 失败: ${legacy_name} (${legacy_id}) · 手动: multica agent archive ${legacy_id}"
  done
}

# $1=kind|all $2=provider $3=scope $4=suffix · runtime → ensure 身份 agent → build → archive legacy
# suffix(email 前缀/team)只用于 legacy 英文对象的 archive 匹配;新对象命名一律用 member 显示名。
ac_run() {
  local kind="$1" provider="$2" scope="$3" suffix="$4"
  local rid agent_id display
  rid=$(ac_select_runtime "$provider")
  display="$(ac_scope_display_name "$scope")"
  agent_id=$(ac_ensure_agent "$rid" "$scope" "$display")
  if [ "$kind" = all ]; then
    local k; for k in "${AC_KINDS[@]}"; do ac_build_one "$k" "$agent_id" "$scope" "$display"; done
  elif ac_is_kind "$kind"; then
    ac_build_one "$kind" "$agent_id" "$scope" "$display"
  else
    ac_die "未知 kind: ${kind} (应为 ${AC_KINDS[*]} 或 all)"
  fi
  ac_archive_legacy "$suffix"
  echo ""
  echo "⚠️ 这些 autopilot 只在你的 [${provider}] daemon 在线时跑 · 关机/睡眠日 cron 静默 skip。"
  echo "验证: multica autopilot list | grep -- \"·${display}\""
  echo "手动测: multica autopilot trigger <id>  → 飞书群应收到一张卡"
}
