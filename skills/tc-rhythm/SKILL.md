---
name: tc-rhythm
description: "Facilitates the team's weekly rhythm meetings: the Monday 30-min kickoff (plan alignment) and the Friday 30-min demo + 15-min betting table (decide next week's work). Use when the user says '周一 kickoff', '本周计划对齐', '周五 demo', '周五演示', '下周做什么', '周会', 'Monday kickoff', 'Friday demo', 'betting table', or asks to run or prepare either weekly meeting. Not for starting a new project — use tc-kickoff."
---

# tc-rhythm — 周一对齐 + 周五 demo/betting

## Mandate
运行团队每周节奏的两场例会:周一 09:30 的 30 分钟 kickoff(对齐本周已批准计划的优先级与边界),周五下午的 30 分钟 demo + 15 分钟 betting table(庆祝真产出,决定下周做什么)。

## Entry gates
- 周一对齐/本周计划 → Monday 分支;周五演示/下周排期 → Friday 分支。
- 要启动新项目或写计划本身 → 不走本 skill(见 Handoffs)。

## Steps
Monday(先读 references/monday-kickoff.md 再执行):
1. 确认飞书群已有本周 `计划-已批准` 计划汇总;没有则现场用 multica 查询补齐,交 DRI 发群。
2. 按 5/15/5/5 分钟时间盒协助 DRI:静读 → 逐计划过一遍 → 跨计划边界 → 收尾。只对齐,不复述计划内容。

Friday(先读 references/friday-demo-betting.md 再执行):
1. 会前 1 小时 pre-flight:`multica issue list --label 复盘-待审`,为每个 case 找可演示真产物;评审通过的用 tc-render 的 transition 脚本当场收尾。
2. Demo 30 分钟:3-5 个现场演示(live 真东西),最后 5 分钟庆祝。
3. Betting 15 分钟:提名 ≤5 → 静默 5 分钟 → 每人 ≤3 票 → 高票成为下周 plan-candidates;未得票直接丢弃。

## References
| 文件 | 何时读 |
| --- | --- |
| references/monday-kickoff.md | 执行周一对齐前(会前材料、时间盒、结束态) |
| references/friday-demo-betting.md | 执行周五双会前(pre-flight 命令、demo 格式、betting 记录与降级) |

## Handoffs / Anti-patterns
新项目想法 → INVOKE tc-kickoff skill;betting 胜出候选立项 → INVOKE tc-kickoff 或 tc-plan skill。
- ❌ 周一复述计划内容或变成逐人 status 汇报
- ❌ Demo 用 slides/截图/status update
- ❌ 未得票候选挪进 backlog
- ❌ 没产出就跳过周五(改讲 learnings,不许跳过)

> multica 不在 PATH → 提示安装/更新;unknown flag → 先 `multica update`,仍失败则停下问用户;
> 当前用户身份经 `multica auth status` + `multica user list` 运行时解析,绝不硬编码。
