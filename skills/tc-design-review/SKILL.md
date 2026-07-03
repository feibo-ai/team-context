---
name: tc-design-review
description: "Runs the design review gate (second of three review gates: ①plan ②design ③code) between plan approval and build start: request-review, independent reviewer subagent verdict, then approve. 项目层必走，任务层可跳。Use when the user says '设计评审', '方案过一下', '过设计门' / 'design review', 'review the design', or a project-layer plan was just approved and build has not started. Not for plan approval — use tc-plan; not for code review — use tc-review."
---

# tc-design-review · 设计评审门

## Mandate
在计划批准之后、开工之前，对同一个 work issue 走设计评审门：请审转换 → 独立评审子 agent 出 verdict → 编排 session 当场批准转换。本门只管评审与流转，不新增 doc 类型。

## Entry gates
- 项目层必走（tc-build pre-flight 检查设计已审）；任务层可跳，批准后直接开工合法。
- 时点：plan 批准之后、build 开工之前；挂同一个 work issue，不建新 issue。
- 设计载体 = plan 的 approach 段或一条 issue 评论；批准后实质改方案 → 先走 tc-plan 的 plan-upgrade 重审计划。

## Steps
1. 读 references/design-review-flow.md（完整门流程：时点、载体、补审、机制盲区）。
2. 请审：`python3 <skills-root>/tc-render/scripts/transition.py design-request-review <work-issue>`
3. 派设计评审子 agent（全新上下文、role = staff engineer、不带实现方对话记忆），只给设计载体 + 相关 research；输出契约读 references/review-verdict-template.md。
4. verdict 返回点 = 转换执行点，当场跑：approved → `python3 <skills-root>/tc-render/scripts/transition.py design-approve <work-issue>` → 接 tc-build 的 build-start；changes-requested → 修订后回第 3 步。

## References
| 文件 | 什么时候读 |
|---|---|
| references/design-review-flow.md | 走门之前；补审、changes-requested、机制盲区 |
| references/review-verdict-template.md | 起评审子 agent 时，作为其输出契约 |
| tc-render skill 的 references/issue-label-state-rules.md | 需要 label/status 状态机精确语义时 |

## Handoffs / Anti-patterns
- approved 后交接 tc-build skill（build-start）；方案实质变更交接 tc-plan skill（plan-upgrade）。
- ❌ 子 agent 直接跑 design-approve——转换权归编排 session。
- ❌ 评审未过就硬开工。
- ❌ 手动贴/摘评审 label——一律走 transition.py。
- ❌ 为设计稿新建 issue 或改写 issue 描述。

> multica 不在 PATH → 提示安装/更新；unknown flag → 先 `multica update`，仍失败则停下问用户；
> 当前用户身份经 `multica auth status` + `multica user list` 运行时解析，绝不硬编码。
