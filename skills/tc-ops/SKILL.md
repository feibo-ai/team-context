---
name: tc-ops
description: "生成团队健康月报(CLAUDE.md 体量/本月规则改动/skill lint/wip 重启次数)、全量巡检 multica issue 的 label↔status 不变量漂移、并按 PB-04 guardrails 校验 autopilot YAML —— 三个低频运维脚本,agent 直接运行。Use when the user says '月度健康'/'健康月报'/'issue 巡检'/'label 漂移'/'校验 autopilot' / 'monthly health report'/'issue invariants'/'autopilot lint',或做月度 review、backfill/状态机改动后验收、新增/改 autopilot YAML 之前。Not for 修复漂移/流转 label/status 或发布文档 — use tc-render。"
---

# tc-ops · 团队运维脚本

## Mandate
低频运维三件套:团队健康月报、multica issue label↔status 不变量巡检、autopilot YAML guardrail 校验。全部是本 skill scripts/ 下的确定性脚本,agent 直接运行,无需 MCP 服务器。

## Entry gates
- 月度 review / 要健康月报 → monthly_health.py
- backfill、状态机改动后验收,或怀疑 label 漂移 → issue_invariants.py
- 新增/修改 autopilot YAML **之前** → autopilot_lint.py
- 日常 RPI 闭环(调研/方案/执行)不走本 skill。

## Steps
1. 读 references/ops-commands.md 拿完整命令、运行时机与 exit code 契约。
2. 月报:`python3 <skills-root>/tc-ops/scripts/monthly_health.py <team-context-repo> [<project-repo> ...]`,输出 markdown,经 tc-render 发布或直接贴月度 review。
3. 巡检:`python3 <skills-root>/tc-ops/scripts/issue_invariants.py [--strict]`,全量分页拉 issue;--strict 有硬性违规 exit 1(验收/CI 用)。
4. 校验:`python3 <skills-root>/tc-ops/scripts/autopilot_lint.py <yaml> [...]`,有 error exit 1,修到通过再提交;规则明细读 references/autopilot-guardrails.md。
5. 巡检出漂移 → 用 `python3 <skills-root>/tc-render/scripts/transition.py ...` 修复,绝不手敲 label/status 命令。

## References
| 文件 | 什么时候读 |
|---|---|
| references/ops-commands.md | 跑任一脚本前 |
| references/autopilot-guardrails.md | 写/改 autopilot YAML 或解读 lint 报错时 |

## Handoffs / Anti-patterns
- label/status 修复与文档发布交给 tc-render skill;本 skill 只读不写。
- 别用手工 `multica issue list` 替代巡检脚本——只看第一页会截断样本。
- 不复述校验规则的具体数量,以脚本 --help 与源码为准。
- 改动本 skill 文件后按 references/ops-commands.md 同步 registry,防旧版写回。

> multica 不在 PATH → 提示安装/更新;unknown flag → 先 `multica update`,仍失败则停下问用户;
> 当前用户身份经 `multica auth status` + `multica user list` 运行时解析,绝不硬编码。
