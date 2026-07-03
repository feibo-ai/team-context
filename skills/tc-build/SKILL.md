---
name: tc-build
description: "Enforces implement-session (build) discipline against an approved plan: pre-flight gate, build-start status transition, kickoff card broadcast, scope lock, commit rhythm, pollution-signal and stuck-30 handoff rules. Use when the user says '执行', '开工', '开始写代码', '实现', 'implement', 'start coding', or when a session is about to write or run code against an approved plan. Not for planning/debrief — tc-plan/tc-review;只给 issue id 阶段不明 — tc-router first."
---

# Build Session — 按批准的 plan 执行

## Mandate
按已批准的 plan 精确执行。本 session 绝不重新研究、重新规划、重新决策；发现方案本身不对 → INVOKE tc-handoff skill，回 Plan session。

## Entry gates
逐项核对 references/build-preflight.md（plan 已读、批准标记、项目层设计评审门、能复述目标/完成判据/scope）。任一 No → INVOKE tc-handoff skill → `/clear` 回 Plan，不得写码。

## Steps
1. Pre-flight 全过后、写第一行代码前跑：
   `python3 <skills-root>/tc-render/scripts/transition.py build-start <plan-issue>`
   幂等，续作 session 重跑无害。label/status 状态机见 tc-render skill 的 references/issue-label-state-rules.md；流转只走 transition.py，绝不手改。
2. 该计划的首个 build session 同时机发「任务开工」卡（骨架见 references/implementation-loop.md）；handoff/`/clear` 后的续作 session 不重发。
3. 进入实现循环：scope lock、人审 diff、commit 节奏、子 agent 分工与卡死规则，读 references/implementation-loop.md。
4. 全程监控污染信号（references/pollution-signals.md）；任一命中立即 INVOKE tc-handoff skill，不要试图"拉回来"。
5. 完成判据全满足 + tests green + diff 已人审 + push → INVOKE tc-review skill。

## References
| 文件 | 什么时候读 |
|---|---|
| references/build-preflight.md | 写第一行代码之前 |
| references/implementation-loop.md | build-start 之后、写码全程 |
| references/pollution-signals.md | 怀疑 session 变笨/答非所问时 |

## Handoffs / Anti-patterns
交接：污染或卡死 → tc-handoff；设计门未过 → tc-design-review；完成 → tc-review。
- ❌ 本 session 改 plan 或加 scope（"顺手优化" = 另立 plan）
- ❌ 跳过人审 diff"就这一次"
- ❌ 卡住 30 分钟仍硬修（推倒重来胜过修补）
- ❌ 同一任务 `/clear` 3 次后仍当任务层做（升级项目层，重走 Research→Plan）

> multica 不在 PATH → 提示安装/更新；unknown flag → 先 `multica update`，仍失败则停下问用户；
> 当前用户身份经 `multica auth status` + `multica user list` 运行时解析，绝不硬编码。
