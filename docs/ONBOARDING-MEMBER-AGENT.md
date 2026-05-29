# MEMBER · Agent Onboarding Spec v1

> **Audience:** AI agent (Claude Code / Codex / generic LLM agent)
> **Purpose:** End-to-end configure a new team member's machine.
> **Human equivalent:** [`ONBOARDING-MEMBER.md`](./ONBOARDING-MEMBER.md) (don't ask user to read both — pick one).

---

## EXECUTION CONTRACT

1. **Collect INPUTS first** (see §INPUTS). Any missing → ABORT with explicit ask.
2. **Run STEP-00 to STEP-05 in order**. Each STEP has a `VERIFY` clause:
   - VERIFY exit code 0 + stdout matches `Expected:` → proceed
   - Otherwise → STOP, print full step output, do **not** auto-retry except where step says so
3. **Steps are IDEMPOTENT** (safe to re-run on partial-completion machines).
4. **On final success** print exactly `MEMBER_ONBOARD_OK <ISO-8601 UTC timestamp>` to stdout (orchestrators grep this).
5. **NEVER:**
   - Commit `MULTICA_TOKEN` to git
   - Print PAT in plaintext beyond first 14 chars
   - `sudo` unless step explicitly says so
   - Auto-restart user's CLI (codex / claude-code) — print instruction instead

---

## INPUTS (collect from user · abort if missing)

| key | regex | how to obtain | example |
|---|---|---|---|
| `MULTICA_TOKEN` | `^mul_[a-f0-9]{40}$` | DRI 飞书 DM 给的 PAT | `mul_6f7119003c…` |
| `MULTICA_WORKSPACE_ID` | `^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$` | DRI 飞书 DM 给的 UUID | `b18d7b35-344a-4663-9ddc-00a71de89399` |
| `CLI_TARGET` | enum: `codex` \| `claude-code` | 用户选 | `codex` |

---

## CONSTANTS (do not parameterize)

```
CLOUD_API   = https://api.teamctx.actionow.ai
CLOUD_WEB   = https://teamctx.actionow.ai
CLOUD_MCP   = https://mcp.teamctx.actionow.ai/mcp
TCMCP_REPO  = https://github.com/feibo-ai/team-context-mcp.git
TCMCP_DIR   = $HOME/team-context-mcp
SKILLS_DIR  = $HOME/.claude/skills
```

---

## STEP-00 · Prereqs

```bash
# macOS only · Linux: substitute apt/yum and ABORT if any tool absent
command -v brew >/dev/null || { echo "ABORT_NEED_BREW"; exit 1; }
# jq / node via brew
brew install jq node@22 2>&1 | tail -3
# multica via official install.sh (NOT brew — brew multica is upstream CLI, missing control-plane subcommands).
# install.sh self-detects upgrade, so re-running it is also the upgrade path.
curl -fsSL https://raw.githubusercontent.com/feibo-ai/tc-multica/main/scripts/install.sh | bash
command -v pnpm >/dev/null || npm install -g pnpm@11
```

**VERIFY:**
```bash
multica --version 2>&1 | grep -qE 'multica v[0-9]+\.[0-9]+' \
 && multica integration --help >/dev/null 2>&1 \
 && node --version | grep -qE '^v2[2-9]\.' \
 && jq --version | grep -qE 'jq-1\.[7-9]' \
 && pnpm --version | grep -qE '^1[1-9]\.' \
 && echo VERIFY_00_OK
```

**Expected:** stdout contains `VERIFY_00_OK`.
**ON_FAIL:** print which tool's version check failed, ABORT. If `multica integration --help` errors, the wrong `multica` is installed (upstream brew CLI lacks control-plane subcommands) — re-run the install.sh curl from STEP-00.

---

## STEP-01 · Multica CLI config + auth

```bash
multica config set server_url  https://api.teamctx.actionow.ai >/dev/null
multica config set app_url     https://teamctx.actionow.ai     >/dev/null
multica config set workspace_id "$MULTICA_WORKSPACE_ID"         >/dev/null

# Pick shell rc · prefer zsh on macOS · idempotent line replace
# (tcmcp-local reads ALL 3 env vars at startup · multica config alone is not enough)
RC="$HOME/.zshrc"; [ -n "$BASH_VERSION" ] && [ ! -f "$RC" ] && RC="$HOME/.bashrc"
touch "$RC"
grep -vE '^export (MULTICA_TOKEN|MULTICA_SERVER_URL|MULTICA_WORKSPACE_ID)=' "$RC" > "$RC.tmp" && mv "$RC.tmp" "$RC"
cat >> "$RC" <<RCEOF
export MULTICA_SERVER_URL=https://api.teamctx.actionow.ai
export MULTICA_WORKSPACE_ID=$MULTICA_WORKSPACE_ID
export MULTICA_TOKEN=$MULTICA_TOKEN
RCEOF
export MULTICA_SERVER_URL=https://api.teamctx.actionow.ai
export MULTICA_WORKSPACE_ID
export MULTICA_TOKEN
```

**VERIFY:**
```bash
multica auth status 2>&1 | awk '/^User:/ {found=1} END {exit found?0:1}' \
 && echo VERIFY_01_OK
```

**Expected:** stdout contains `VERIFY_01_OK`.
**ON_FAIL:** PAT invalid OR cloud unreachable. Do not retry.
- diagnose: `curl -fsS https://api.teamctx.actionow.ai/healthz` (must return 200 with `{"status":"ok"}`)
- if cloud OK but auth fails → token invalid · ask DRI to re-issue · ABORT
- if cloud unreachable → network · ABORT

---

## STEP-02 · tcmcp-local build (12 stdio tools)

```bash
TCMCP_DIR="$HOME/team-context-mcp"
if [ ! -d "$TCMCP_DIR/.git" ]; then
  git clone https://github.com/feibo-ai/team-context-mcp.git "$TCMCP_DIR"
fi
cd "$TCMCP_DIR"
git pull --ff-only 2>/dev/null || true   # fail-open: continue with current commit
CI=true pnpm install --frozen-lockfile 2>&1 | tail -3   # CI=true: avoid no-TTY purge prompt on re-runs
pnpm --filter @tcmcp/shared build 2>&1 | tail -3
pnpm --filter @tcmcp/local  build 2>&1 | tail -3
```

**VERIFY:** (spawns server, sends MCP init+tools/list, parses count, kills)
```bash
count=$({
  printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"v","version":"0"}}}'
  printf '%s\n' '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'
  sleep 2
} | node "$TCMCP_DIR/packages/local/dist/server.js" 2>/dev/null \
  | jq -r 'select(.id==2)|.result.tools|length')
[ "$count" = "12" ] && echo VERIFY_02_OK || echo "VERIFY_02_FAIL got=$count expected=12"
```

**Expected:** stdout contains `VERIFY_02_OK`.
**ON_FAIL:**
- `count = 0` or empty → build broke. Run `pnpm install --frozen-lockfile` again, then VERIFY.
- After 2 attempts still ≠ 12 → ABORT, attach `pnpm install` output to report.

---

## STEP-03 · Sync 12 team skills from multica

```bash
SKILLS_DIR="$HOME/.claude/skills"
mkdir -p "$SKILLS_DIR"

ids=$(curl -fsS -H "Authorization: Bearer $MULTICA_TOKEN" \
  "https://api.teamctx.actionow.ai/api/skills?workspace_id=$MULTICA_WORKSPACE_ID" \
  | jq -r '.[].id')

n=0
for id in $ids; do
  json=$(curl -fsS -H "Authorization: Bearer $MULTICA_TOKEN" \
    "https://api.teamctx.actionow.ai/api/skills/$id?workspace_id=$MULTICA_WORKSPACE_ID")
  name=$(echo "$json" | jq -r .name)
  desc=$(echo "$json" | jq -r .description)
  body=$(echo "$json" | jq -r .content)
  d="$SKILLS_DIR/$name"
  mkdir -p "$d"
  {
    printf -- '---\n'
    printf 'name: %s\n' "$name"
    printf 'description: %s\n' "$(echo "$desc" | jq -R -s .)"
    printf -- '---\n'
    printf '%s\n' "$body"
  } > "$d/SKILL.md"
  n=$((n+1))
done
echo "synced=$n"
```

**VERIFY:**
```bash
count=$(ls "$HOME/.claude/skills" 2>/dev/null | wc -l | tr -d ' ')
[ "$count" = "12" ] && echo VERIFY_03_OK || echo "VERIFY_03_FAIL got=$count expected=12"
```

**Expected:** stdout contains `VERIFY_03_OK`.
**ON_FAIL:**
- `count = 0` → curl returned error. Check:
  - `curl -fsS -H "Authorization: Bearer $MULTICA_TOKEN" https://api.teamctx.actionow.ai/api/skills?workspace_id=$MULTICA_WORKSPACE_ID | head -c 100`
  - If `{"error":"invalid token"}` → ABORT (PAT issue, re-do STEP-01)
  - If `[]` → ABORT (wrong workspace_id, ask user to verify)
- `count > 0 && count < 12` → partial sync · network flake. Re-run STEP-03 once. If still < 12, ABORT.

---

## STEP-04 · MCP config (branch on `$CLI_TARGET`)

### STEP-04a · IF `$CLI_TARGET == codex`

```bash
TCMCP_DIR="$HOME/team-context-mcp"
CFG="$HOME/.codex/config.toml"
mkdir -p "$(dirname "$CFG")"
touch "$CFG"
cp "$CFG" "$CFG.bak.$(date +%s)"   # backup

# Idempotent: append only if section doesn't already exist
if ! grep -q '^\[mcp_servers\.tcmcp-local\]' "$CFG"; then
  cat >> "$CFG" <<TOMLEOF

[mcp_servers.tcmcp-local]
command = "node"
args = ["$TCMCP_DIR/packages/local/dist/server.js"]
TOMLEOF
fi

if ! grep -q '^\[mcp_servers\.tcmcp-remote\]' "$CFG"; then
  cat >> "$CFG" <<TOMLEOF

[mcp_servers.tcmcp-remote]
url = "https://mcp.teamctx.actionow.ai/mcp"
bearer_token_env_var = "TCMCP_AGENT_TOKEN"
TOMLEOF
else
  # Section exists · do NOT auto-modify (could clobber custom user config).
  # Manually verify url == https://mcp.teamctx.actionow.ai/mcp and bearer_token_env_var == TCMCP_AGENT_TOKEN.
  echo "WARN: [mcp_servers.tcmcp-remote] already exists in $CFG · agent will not modify"
  echo "      VERIFY MANUALLY · or remove the section and re-run STEP-04a"
fi

# Set TCMCP_AGENT_TOKEN env var (codex reads via bearer_token_env_var)
RC="$HOME/.zshrc"; [ -n "$BASH_VERSION" ] && [ ! -f "$RC" ] && RC="$HOME/.bashrc"
grep -v '^export TCMCP_AGENT_TOKEN=' "$RC" > "$RC.tmp" && mv "$RC.tmp" "$RC"
echo 'export TCMCP_AGENT_TOKEN=$MULTICA_TOKEN' >> "$RC"
```

**VERIFY:**
```bash
count=$(grep -c '^\[mcp_servers\.tcmcp-' "$HOME/.codex/config.toml")
[ "$count" -ge "2" ] \
 && grep -q '^export TCMCP_AGENT_TOKEN=' "$HOME/.zshrc" "$HOME/.bashrc" 2>/dev/null \
 && echo VERIFY_04a_OK \
 || echo "VERIFY_04a_FAIL sections=$count"
```

**Expected:** stdout contains `VERIFY_04a_OK`.

### STEP-04b · IF `$CLI_TARGET == claude-code`

```bash
TCMCP_DIR="$HOME/team-context-mcp"
CFG="$HOME/.claude/mcp.json"
mkdir -p "$(dirname "$CFG")"

# Read existing (or seed empty); validate JSON; merge our 2 entries
if [ -f "$CFG" ]; then
  cp "$CFG" "$CFG.bak.$(date +%s)"
  jq . "$CFG" >/dev/null || { echo "ABORT: $CFG is invalid JSON"; exit 1; }
  base=$(cat "$CFG")
else
  base='{"mcpServers":{}}'
fi

echo "$base" | jq \
  --arg tcmcp_dir "$TCMCP_DIR" \
  --arg url "https://mcp.teamctx.actionow.ai/mcp" \
'
  .mcpServers["tcmcp-local"]  = {"command":"node","args":[($tcmcp_dir + "/packages/local/dist/server.js")]}
  | .mcpServers["tcmcp-remote"] = {"url":$url, "headers":{"Authorization":"Bearer ${MULTICA_TOKEN}"}}
' > "$CFG.new" && mv "$CFG.new" "$CFG"
```

**VERIFY:**
```bash
keys=$(jq -r '.mcpServers | keys[]' "$HOME/.claude/mcp.json" 2>/dev/null | sort | tr '\n' ' ')
echo "$keys" | grep -q 'tcmcp-local' && echo "$keys" | grep -q 'tcmcp-remote' \
 && echo VERIFY_04b_OK \
 || echo "VERIFY_04b_FAIL keys=$keys"
```

**Expected:** stdout contains `VERIFY_04b_OK`.

---

## STEP-05 · Cloud-side smoke (does NOT require restarted CLI)

Agent can verify upstream wiring without restarting user's codex/claude-code:

```bash
# tcmcp /health must report feishu_ready true AND multica_reachable true
curl -fsS https://mcp.teamctx.actionow.ai/health 2>&1 | \
  jq -e '.feishu_ready == true and .multica_reachable == true and .status == "healthy"' \
  >/dev/null \
 && echo VERIFY_05_OK \
 || { echo "VERIFY_05_FAIL"; curl -s https://mcp.teamctx.actionow.ai/health | jq .; }
```

**Expected:** stdout contains `VERIFY_05_OK`.
**ON_FAIL:** This is a cloud-side issue (not the member's machine). ABORT and tell user to contact DRI.

---

## STEP-06 · (OPTIONAL) personal autopilots — only if user opts in

NOT part of `MEMBER_ONBOARD_OK`. Run ONLY if the user explicitly asks to set up their
personal autopilots. Requires: the `team-context` repo (team members have read access
via org membership), and the user's `multica daemon` staying online (offline days → cron silently skips).

```bash
# team members have read access via org; if clone fails it's a network issue → report & skip
[ -d "$HOME/team-context/.git" ] || git clone https://github.com/feibo-ai/team-context.git "$HOME/team-context"
cd "$HOME/team-context" && git pull --ff-only 2>/dev/null || true
export TCMCP_AGENT_TOKEN="$MULTICA_TOKEN"
multica daemon start
bash scripts/my-autopilot.sh all codex   # provider = registered runtime: codex | claude | hermes
```

**VERIFY (optional):**
```bash
PREFIX=$(multica auth status 2>&1 | awk -F'[()]' '/User:/{print $2; exit}' | cut -d@ -f1)
[ "$(multica autopilot list 2>/dev/null | grep -c -- "-${PREFIX}")" -ge 1 ] && echo VERIFY_06_OK || echo VERIFY_06_SKIP
```
**ON_FAIL:** not required for onboarding · print `VERIFY_06_SKIP` and continue to STEP-FINAL.

---

## STEP-FINAL · Print success marker + next-human-action

```bash
echo "MEMBER_ONBOARD_OK $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "NEXT_HUMAN_ACTION_1: open a new terminal (so shell rc reloads MULTICA_TOKEN + TCMCP_AGENT_TOKEN)"
echo "NEXT_HUMAN_ACTION_2: fully restart your CLI ($CLI_TARGET) to load MCP config"
echo "NEXT_HUMAN_VERIFY: ask CLI 'call search_chat to find the Team Context group, return its chat_id'"
echo "NEXT_HUMAN_EXPECT: chat_id == oc_035c15b7fb12fed8d0e022fe2f529553"
```

---

## ABORT / RETRY POLICY (machine-actionable)

| Failure class | Action |
|---|---|
| Tool missing (STEP-00 verify) | ABORT · name the tool · do not auto-install via sudo |
| Token invalid (STEP-01/03 verify with 401-shape error) | ABORT · ask user to re-obtain PAT from DRI · do not retry |
| Cloud unreachable (curl exit 6/7) | Retry once after 5s · still fail → ABORT |
| Build broken (STEP-02 verify count ≠ 12) | Retry STEP-02 once · still fail → ABORT with `pnpm install` output |
| Config file invalid JSON/TOML (STEP-04) | Restore from `.bak.<ts>` · ABORT |
| `[mcp_servers.tcmcp-remote]` already exists with conflicting url (STEP-04a) | Warn but **do not** modify · let user decide |
| `feishu_ready=false` (STEP-05) | Cloud-side issue · ABORT · tell user to contact DRI |

---

## DRY-RUN MODE (optional)

If env `DRY_RUN=1`:
- Skip `brew install`, the `install.sh` curl, `git clone`, `pnpm install`, `mkdir`, file writes
- Still run all VERIFY commands (to assess current state)
- Output: `WOULD_DO: <command>` instead of execution

---

## SUCCESS CRITERIA (orchestrator checklist)

Onboarding is complete iff **all** of these hold:
- `VERIFY_00_OK` through `VERIFY_05_OK` printed in order
- `MEMBER_ONBOARD_OK <timestamp>` printed
- No `ABORT*` or `VERIFY_*_FAIL` marker in output

Orchestrators: grep for these literals; do not parse natural-language status messages.

---

**Owner:** DRI
**Spec version:** 1
**Last reviewed:** 2026-05-28
**Tested:** all 5 steps' VERIFY commands ran during 2026-05-28 W5 cloud bootstrap (DRI mac · macOS) + STEP-03 + STEP-04a (Codex branch) re-validated with throwaway `teammate-test@actionow.ai` member PAT before doc commit.
