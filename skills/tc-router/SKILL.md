---
name: tc-router
description: "Routes ambiguous work-continuation requests to the right tc-* skill by reading a multica issue's labels, status and doc comments to decide the current phase. Use when the user says '接手'/'继续'/'下一步'/'干活'/'卡住了' / 'pick up'/'what next', or gives only an issue id/project with no clear phase; router only routes, never does the work. Not for clearly-phased asks (调研→tc-research, 写方案→tc-plan, 执行→tc-build, 收尾→tc-review) — those trigger directly."
---

# tc-router · 团队工作入口路由

## Mandate
把模糊的「继续干活」类请求路由到正确的 tc-* skill:定位 context → 判定阶段 → INVOKE 目标 skill 并说明理由。Router 绝不自己做目标 skill 的工作(不写文档、不转状态、不写代码)。

## Entry gates
- 用户意图模糊(接手/继续/下一步/开始/卡住),或只给了 issue id / 项目名。
- 用户明确点名了阶段或 skill → 直接 INVOKE 那个 skill,本 skill 到此为止。

## Steps
1. 定位 context:话里有 issue id/URL 吗?没有 → `multica project list` + `multica issue list --project <完整UUID>` 圈候选(分页拉全:`--limit/--offset` 循环至 `has_more=false`);仍不确定就问用户,绝不猜。
2. `multica issue show <id>`:读 labels + status + 评论区已发布的文档(plan/research/case HTML 评论)。
3. 读 references/issue-state-detection.md 判定当前阶段(label 驱动,勿用裸 status)。
4. 读 references/routing-table.md 选目标 skill;向用户宣布「当前阶段 = X,证据 = <labels/文档>,交给 <skill>」,然后 INVOKE <skill> skill。
5. 判不出或多个候选并列 → 列出证据问用户,不要硬选。

## References
| 文件 | 什么时候读 |
|---|---|
| references/issue-state-detection.md | 拿到 issue 后判阶段 |
| references/routing-table.md | 阶段→skill 映射;不确定去向时 |
| references/real-user-prompts.md | 触发吃不准时对照语料 |

## Handoffs / Anti-patterns
- 路由后立刻交棒,不替目标 skill 干活;label/status 流转一律由目标 skill 经 tc-render 执行。
- 不凭对话记忆判阶段,以 issue 实际 labels 为准。
- 卡住 30 分钟没进展 → INVOKE tc-handoff skill;同一问题 3 次 handoff → 升级到 greenfield playbook。
- 绝不建无项目的孤儿 issue;projectId 拿不准就问用户。

> multica 不在 PATH → 提示安装/更新;unknown flag → 先 `multica update`,仍失败则停下问用户;
> 当前用户身份经 `multica auth status` + `multica user list` 运行时解析,绝不硬编码。
