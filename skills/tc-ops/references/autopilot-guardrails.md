autopilot_lint.py 强制执行的 autopilot YAML guardrail 规则(PB-04),写/改 autopilot YAML 或解读 lint 报错时对照。

## 硬校验(违反 → ERROR,exit 1,挡住提交)
- `name`、`description`、`prompt` 必填非空。
- `mode` 必须是 `run_only` 或 `create_issue`,别无其他合法值。
- `trigger.cron` 与 `trigger.timezone` 必填。
- YAML 文件无法解析本身即 ERROR。
- YAML 同目录必须存在**非空**的 `_agent-instructions.md`(agent 通用约束单源;agent 身份不写进 YAML 字段,由 autopilot 运行框架按 scope 派生)。
- `guardrails` 段必填,且:
  - `forbidden_commands`:list 且 ≥5 条,必须包含 "git push" 与 "npm publish"(子串匹配,大小写不敏感);
  - `forbidden_paths`:list 且 ≥1 条;
  - `max_budget_usd`:必须是数字(bool 不算),且 ≤150 硬上限;
  - `max_runtime_minutes`:必须是正数。

## 警告(WARN,不挡但需人工确认)
- `max_budget_usd` >80:属大批量预算区间,DRI 应明示批准后再上。

## 维护规则
- 同一套校验在三处内联实现,改规则必须三处同步:team-context 仓库的 CI workflow lint、本 skill 的 scripts/autopilot_lint.py、autopilot 公共 shell 库 `_autopilot-common.sh` 的 `ac_lint_yaml`。
- 改完脚本记得按 references/ops-commands.md 的例行运维命令同步 multica registry。
