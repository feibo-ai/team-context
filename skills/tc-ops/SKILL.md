---
name: tc-ops
description: "团队运维/维护脚本集:月度健康报告 + autopilot YAML 校验。Use when 做月度 review(团队健康月报:CLAUDE.md token / 本月规则改动 / skill lint / wip 重启次数)或 新增/修改 autopilot YAML 前校验其 SOP PB-04 guardrails。取代本地 MCP 的 monthly_health_report / autopilot_lint —— agent 直接调脚本,无需 MCP 服务器。Triggers '月度健康','monthly health','autopilot lint','校验 autopilot','health report'。"
owner: 曾振华
last_reviewed_at: 2026-06-10
---

# tc-ops · 运维脚本

取代本地 MCP 的两个低频工具,改为 agent 直接调用的脚本(确定性 + 无需 MCP 服务器)。

## monthly_health.py —— 月度健康报告(原 monthly_health_report)
月度 review 时跑:
```bash
python3 ~/.claude/skills/tc-ops/monthly_health.py <team-context-repo> [<project-repo> ...]
```
输出 markdown,含 5 指标:CLAUDE.md token 数(>3000 ⚠️)/ 本月 claude-md 改动(git log 近30天)/
skill lint(stale + owner gaps,内联复刻 `multica skill lint`)/ `wip:` 重启次数(>50 ⚠️ burnout)/
case 污染人工 grep 提示。报告可经 tc-render 或直接贴月度 review。

## issue_invariants.py —— issue label↔status 不变量巡检(状态机漂移雷达)
月度 review 必跑;backfill / 状态机改动后验收用 `--strict`(有违规 exit 1):
```bash
python3 ~/.claude/skills/tc-ops/issue_invariants.py [--strict]
```
全量**分页**扫描(has_more=false 才停),输出 6 条硬性不变量违规(复盘-已审⇒done /
复盘-待审⇒in_review / 计划-评审中⇒in_review / 计划-已批准⇒todo|in_progress|done /
cancelled⇒无流程 label / 已升级⊕已批准互斥)+ 2 档警告(评审挂起 >48h staleness /
标题像流程 issue 却零流程 label 的入口盲区)。语义单源 = standards/labels.md 不变量表;
修复用 `skills/tc-render/transition.py`,绝不手敲 label/status 命令。

## autopilot_lint.py —— autopilot YAML 校验(原 autopilot_lint · SOP PB-04)
新增/改 autopilot YAML **前**跑(有 error 则 exit 1,挡住不合规的):
```bash
python3 ~/.claude/skills/tc-ops/autopilot_lint.py <yaml-path> [<yaml-path> ...]
```
硬校验:name/description/mode(run_only|create_issue)/prompt/trigger.cron+timezone 必填;
同目录 _agent-instructions.md(通用约束单源 · TEA-93 起取代 agent.name 字段)存在且非空;
guardrails 必填且 forbidden_commands ≥5 条且含 "git push"+"npm publish"、forbidden_paths ≥1、
max_budget_usd 是数字且 ≤150(>80 ⚠️ 大批量需 DRI 批)、max_runtime_minutes 正数。

> ⚠️ 改本 skill 任何文件后必须同步 multica registry:`multica skill files upsert tc-ops --path <file> --content "$(cat <file>)"`。
> 否则 monthly-health autopilot 每次跑 `multica skill pull tc-ops` 会经 `~/.claude/skills/tc-ops` 软链把 registry 旧版写回 repo 工作树(2026-06-10 实测发生)。

## 边界
- 这俩是**低频**工具(月度 / autopilot 变更时),不进 RPI 闭环。
- 校验逻辑逐字复刻原 MCP;改规则同时改脚本。
