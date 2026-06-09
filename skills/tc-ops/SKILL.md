---
name: tc-ops
description: "团队运维/维护脚本集:月度健康报告 + autopilot YAML 校验。Use when 做月度 review(团队健康月报:CLAUDE.md token / 本月规则改动 / skill lint / wip 重启次数)或 新增/修改 autopilot YAML 前校验其 SOP PB-04 guardrails。取代本地 MCP 的 monthly_health_report / autopilot_lint —— agent 直接调脚本,无需 MCP 服务器。Triggers '月度健康','monthly health','autopilot lint','校验 autopilot','health report'。"
owner: 曾振华
last_reviewed_at: 2026-06-09
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

## autopilot_lint.py —— autopilot YAML 校验(原 autopilot_lint · SOP PB-04)
新增/改 autopilot YAML **前**跑(有 error 则 exit 1,挡住不合规的):
```bash
python3 ~/.claude/skills/tc-ops/autopilot_lint.py <yaml-path> [<yaml-path> ...]
```
硬校验:name/description/mode(run_only|create_issue)/agent.name/prompt/trigger.cron+timezone 必填;
guardrails 必填且 forbidden_commands ≥5 条且含 "git push"+"npm publish"、forbidden_paths ≥1、
max_budget_usd 是数字且 ≤150(>80 ⚠️ 大批量需 DRI 批)、max_runtime_minutes 正数。

## 边界
- 这俩是**低频**工具(月度 / autopilot 变更时),不进 RPI 闭环。
- 校验逻辑逐字复刻原 MCP;改规则同时改脚本。
