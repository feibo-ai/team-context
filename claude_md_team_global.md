# AI MIQ — team-global CLAUDE.md

跨项目规则，适用于所有团队工作。复制（或软链）到每个产品 repo 的 CLAUDE.md，或者通过 Claude Code 的 `CLAUDE.md` 继承机制叠加在它之上。

## 我们是谁
AI MIQ — 5 人 AI-Native 团队。以 SOP v0.4 参考 Handbook 为准。通才 + AI 杠杆，哑铃模型。

## 怎么工作 · 5 条核心规则

1. **Research / Plan / Implement 是分离的 session。** 不要混。session 协议分别用 `rpi-research`、`rpi-plan-template`、`rpi-implement-discipline` 三个 skill。
2. **Context pollution → 调 `pre-clear` skill → /clear。** 不要原地修。
3. **每个项目 / 任务都要以 `cases/YYYY-MM-DD-*.md` 复盘收尾**，用 `debrief-template` skill。5 个必填段落。SOP 不可妥协 #2。
4. **写代码前必须有 plan markdown，并由第二个 session 评审。** 用 `rpi-plan-template` skill。SOP 不可妥协 #1。
5. **底线规则：每段 AI 生成的 diff 在 commit 前都要过人眼。** 你来 ship。

## 跨项目技术规则
（团队标准成形后填进来。每条规则必须适用于所有未来同类项目；项目特有的规则去 `cases/`，不放这里。）

## Claude 不能再犯的错
（通过 `case_promote_rule` MCP 工具从 case file 提升上来。）

## 怎么叫起其他 Claude session

| 需求 | Skill |
| --- | --- |
| Research | `rpi-research` |
| Plan | `rpi-plan-template` |
| Implement | `rpi-implement-discipline` |
| Debrief | `debrief-template` |
| 自检 | `anti-pattern-self-check` |
| 污染扫描 | `context-pollution-detector` |
| /clear 之前 | `pre-clear` |

## 卡住的时候
- 30 分钟没进展 → 调 `pre-clear` skill
- 同一个问题 3 次 handoff → 升级到 greenfield playbook (PB1)
- 单周 5 次 handoff → 月度 review 时标 burnout 信号

## 去哪儿找具体 context

| 什么 | 在哪 |
| --- | --- |
| 跨项目 Skills | `~/.claude/skills/`（从 team-context repo 同步） |
| 项目内 plans | `<project>/docs/plans/` |
| 项目内 research | `<project>/docs/research/` |
| 项目 cases (L2) | `<project>/cases/YYYY-MM-DD-*.md` |
| 团队 SOP | team-context repo，`sop/group_sop_v0.4.html` |
| 团队标准 | team-context repo，`standards/` |
| 架构决策 | `<project>/decisions/` + team-context `decisions/` |
| Multica workspace | `team-context`（server URL：跑 `multica config show`） |
| Multica CLI 参考 | `multica --help` 或 `~/.claude/skills/multica-cli/` |
