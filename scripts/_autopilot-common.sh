#!/usr/bin/env bash
# _autopilot-common.sh — shared logic for my-autopilot.sh (个人版) + team-autopilot.sh (团队版).
#
# NOT executable on its own · both entry scripts `source` it.
# Per spec 2026-05-28-personal-autopilot-script-spec.md §3.1: the only real
# difference between the two entry scripts is SCOPE + naming SUFFIX; everything
# else (preflight, runtime pick, PB-04 lint, agent/autopilot build) is shared here.
#
# Reuses apply-autopilots.sh's yq-based PB-04 lint + (desc + prompt) → --description
# injection. Adds what apply-autopilots.sh does NOT: it CREATES the runtime-bound
# agent with AUTOPILOT_SCOPE in custom_env (apply-autopilots.sh assumes the agent
# pre-exists). Capture-then-jq throughout to avoid grep/head SIGPIPE'ing the
# upstream command under `set -o pipefail` (same hazard apply-autopilots.sh notes).

set -euo pipefail

AC_REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AC_AUTOPILOTS_DIR="${AC_REPO_DIR}/autopilots"
AC_KINDS=(daily-summary daily-kickoff monday-kickoff wednesday-stats monthly-health)

# tcmcp-remote lives in the cloud (Zeabur) since W5 · agents reach feishu through it.
: "${TCMCP_REMOTE_URL:=https://mcp.teamctx.actionow.ai/mcp}"

ac_die() { echo "ABORT: $*" >&2; exit 1; }

# Is $1 one of the 4 known kinds?
ac_is_kind() {
  local k
  for k in "${AC_KINDS[@]}"; do [ "$1" = "$k" ] && return 0; done
  return 1
}

ac_preflight() {
  command -v jq >/dev/null 2>&1 || ac_die "缺 jq · brew install jq"
  command -v yq >/dev/null 2>&1 || ac_die "缺 yq · brew install yq"
  multica auth status >/dev/null 2>&1 || ac_die "未登录 · 先 multica login"
  # capture-then-grep: grep -q would SIGPIPE `multica daemon status` under pipefail
  local ds; ds=$(multica daemon status 2>&1 || true)
  printf '%s' "$ds" | grep -qi running || ac_die "daemon 离线 · 先 multica daemon start (离线日 autopilot 静默 skip)"
  [ -n "${TCMCP_AGENT_TOKEN:-}" ] || ac_die "TCMCP_AGENT_TOKEN 未设 · export TCMCP_AGENT_TOKEN=\$MULTICA_TOKEN"
}

# $1 = provider (codex|claude|hermes) → echoes one online runtime id (or aborts)
ac_select_runtime() {
  local p="$1" out rid
  out=$(multica runtime list --output json)
  rid=$(printf '%s' "$out" | jq -r --arg p "$p" '[.[] | select(.provider==$p and .status=="online")][0].id // empty')
  [ -n "$rid" ] || ac_die "没有在线的 $p runtime · 先 multica daemon start (provider 拼错? codex|claude|hermes)"
  printf '%s' "$rid"
}

# $1 = yaml path · mirrors apply-autopilots.sh PB-04 fallback lint (SOP CRITICAL gate)
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

# $1=kind $2=runtime-id $3=scope $4=suffix
ac_build_one() {
  local kind="$1" rid="$2" scope="$3" suffix="$4"
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

  local agent_name="${kind}-bot-${suffix}"
  local autopilot_title="${kind}-${suffix}"

  # 3a · build/reuse agent (idempotent by name · 同名 = 同 scope)
  local agent_id agents
  agents=$(multica agent list --output json)
  agent_id=$(printf '%s' "$agents" | jq -r --arg n "$agent_name" '[.[] | select(.name==$n)][0].id // empty')
  if [ -z "$agent_id" ]; then
    local envfile created
    envfile=$(mktemp); chmod 600 "$envfile"
    # jq -n builds the JSON safely (no shell interpolation of token into JSON)
    jq -n --arg url "$TCMCP_REMOTE_URL" --arg tok "$TCMCP_AGENT_TOKEN" --arg scope "$scope" \
      '{TCMCP_REMOTE_URL:$url, TCMCP_AGENT_TOKEN:$tok, AUTOPILOT_SCOPE:$scope}' > "$envfile"
    created=$(multica agent create --name "$agent_name" --runtime-id "$rid" \
      --visibility workspace --custom-env-file "$envfile" --output json) \
      || { rm -f "$envfile"; ac_die "agent create 失败: ${agent_name}"; }
    rm -f "$envfile"
    agent_id=$(printf '%s' "$created" | jq -r '.id // empty')
    [ -n "$agent_id" ] || ac_die "agent create 没返回 id: ${agent_name}"
    echo "  + agent ${agent_name} (${agent_id}) · runtime ${rid} · scope=${scope}"
  else
    # T2-6: 复用时检测 runtime 是否变了 (换机 / 换 provider / daemon 重启后 runtime id 会变)
    local cur_rid
    cur_rid=$(printf '%s' "$agents" | jq -r --arg n "$agent_name" '[.[] | select(.name==$n)][0].runtime_id // empty')
    if [ -n "$cur_rid" ] && [ "$cur_rid" != "$rid" ]; then
      echo "  ! agent ${agent_name} runtime 变了 (${cur_rid} → ${rid}) · 重绑"
      multica agent update "$agent_id" --runtime-id "$rid" >/dev/null 2>&1 \
        || echo "  ⚠️ 重绑失败 (multica agent update --runtime-id 可能不支持) · 手动: 删 agent 重跑 / web UI 改绑 · 否则任务可能绑到离线 runtime"
    else
      echo "  = agent ${agent_name} (${agent_id}) 复用 (runtime 未变)"
    fi
  fi

  # prompt 注入 (照 apply-autopilots.sh): desc + prompt → autopilot --description
  local full_desc; full_desc=$(printf '%s\n\n%s' "$desc" "$prompt")

  # 3c · build/update autopilot (idempotent by title) + trigger
  local apid aps
  aps=$(multica autopilot list --output json 2>/dev/null || echo '{}')
  apid=$(printf '%s' "$aps" | jq -r --arg t "$autopilot_title" '[.autopilots[]? | select(.title==$t)][0].id // empty')
  if [ -n "$apid" ]; then
    multica autopilot update "$apid" --description "$full_desc" --agent "$agent_id" >/dev/null
    echo "  = autopilot ${autopilot_title} (${apid}) 更新"
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

# $1=kind|all $2=provider $3=scope $4=suffix · selects runtime once, builds, prints footer
ac_run() {
  local kind="$1" provider="$2" scope="$3" suffix="$4"
  local rid; rid=$(ac_select_runtime "$provider")
  if [ "$kind" = all ]; then
    local k; for k in "${AC_KINDS[@]}"; do ac_build_one "$k" "$rid" "$scope" "$suffix"; done
  elif ac_is_kind "$kind"; then
    ac_build_one "$kind" "$rid" "$scope" "$suffix"
  else
    ac_die "未知 kind: ${kind} (应为 ${AC_KINDS[*]} 或 all)"
  fi
  echo ""
  echo "⚠️ 这些 autopilot 只在你的 [${provider}] daemon 在线时跑 · 关机/睡眠日 cron 静默 skip。"
  echo "验证: multica autopilot list | grep -- -${suffix}"
  echo "手动测: multica autopilot trigger <id>  → 飞书群应收到一张卡"
}
