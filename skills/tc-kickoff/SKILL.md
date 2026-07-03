---
name: tc-kickoff
description: "Guides Phase 01 kickoff of a new project-layer effort (an independent direction: 3+ days, has a DRI) through 6 steps in order: intent broadcast, research session, plan session, independent review, DRI decision, kickoff broadcast. Use when the user says '启动新项目', '我想做一个新项目', '新项目立项', 'kickoff', 'start a new project', or 'Phase 01'. Not for small task-layer work — use tc-plan task-mode instead."
---

# tc-kickoff — Phase 01 六步开工

## Mandate
把一个 project-layer 新方向从想法带到"已批准并广播开工"。kickoff 是手动编排(multica CLI + tc-render 脚本 + 飞书广播),没有单一工具。

## Entry gates
- 先做 project-layer 判定(判据见 references/project-layer-check.md):是 → 继续;否 → task-layer,INVOKE tc-plan skill(task-mode),不走本流程。

## Steps(严格按序;每步命令、模版、确认协议见 references/kickoff-flow.md)
1. 5 分钟意向声明:纯文本发团队飞书群。只通气,不承诺。
2. Research session(fresh session):INVOKE tc-research skill;建 research issue 并经 tc-render 发布。
3. Plan session(另开 fresh session):INVOKE tc-plan skill,读研究产出;建 plan issue(必挂 project;新建 project 逐字段确认)并经 tc-render 发布。
4. 独立评审:transition.py plan-request-review 后,派全新上下文子 agent(role=staff engineer)输出 `VERDICT: approved | changes-requested`,等 verdict。
5. DRI 拍板(verdict 返回点当场执行):proceed → plan-approve;revise → append-only 再发一版,回第 4 步;kill → cancel。唯一需要人类专注思考的一步;未批准不开工。
6. 开工广播:「项目开工」卡发团队飞书群,24h 默许窗口。
每步产物真验证:CLI success ≠ 做对了 —— issue 真挂 project、评论真内联渲染(attachments 非空)、飞书真收到。

## References
| 文件 | 何时读 |
| --- | --- |
| references/project-layer-check.md | Entry gate 判定拿不准时 |
| references/kickoff-flow.md | 执行任何一步之前(命令/模版/卡片骨架) |

## Handoffs / Anti-patterns
6 步完成后:INVOKE tc-handoff skill → /clear → 按 tc-build skill 进入 Implementation。
- ❌ 跳过 Step 1(Step 6 时全队惊讶)
- ❌ Research 与 Plan 同一个 session
- ❌ 自评(Step 4 必须是不同 session)
- ❌ 把 Step 5 当走流程
- ❌ 跳过 Step 6("大家都知道"——24h 默许需要广播)

> multica 不在 PATH → 提示安装/更新;unknown flag → 先 `multica update`,仍失败则停下问用户;
> 当前用户身份经 `multica auth status` + `multica user list` 运行时解析,绝不硬编码。
