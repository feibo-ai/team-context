---
name: tc-handoff
description: "Captures handoff state before /clear or a new Claude/Codex session — commits WIP, records last commit, next action and dead ends to the plan and multica issue, so a fresh session resumes cold without losing work or repeating dead ends. Use when the user says '重开' / '走偏了' / '换个 session' / '浑浊了' or '/clear' / 'new session' / 'start over' / 'I am stuck', or the session is looping, context-polluted, or stalled. Not for 无需重启的 plan 修订 — use tc-plan."
---

# tc-handoff

## Mandate
在 /clear 或开新 session 前捕获交接状态:提交 WIP、写 Current State、发布到 multica issue,让新 session 冷启动续做、避开死胡同。必须在 /clear 前执行,事后状态已丢。

## Entry gates
- 用户示意重启(/clear、new session、重开、走偏了等),或
- 上下文污染:"You're absolutely right" 循环、重复已否决方案、答非所问/解错层,或
- 约 30 分钟无可度量进展。
- 先自问:2 分钟重写 plan 能否救活?/clear ≈ 30-60s 预热 + prompt cache 丢失,并非总是最优。

## Steps
1. `git status --short` 向用户报告未提交内容;按 references/wip-git-policy.md 处置 WIP。
2. 定位当期 plan(issue 上最新 plan 评论);多份或没有则问用户。
3. 按 references/handoff-template.md 写 Current State 块。
4. 幂等门:issue/plan 已有 <60 秒内的 `handoff @` 标记 → 拒绝重发(提示 `last handoff <N>s ago`),跳到第 6 步。
5. 发布:凑 fields.json(字段契约见 tc-render skill 的 references/publish-contract.md),`python3 <skills-root>/tc-render/scripts/publish.py --type handoff --data fields.json --issue <完整 UUID>`。可选:快照并进当期 plan,`publish.py --type plan` 追加新 plan 评论(append-only)。禁止裸 markdown 评论绕开 publish 硬校验。
6. 展示更新后的 plan + commit hash +(若已发)评论 URL,用户确认后才真正 /clear。

## References
| 文件 | 什么时候读 |
|---|---|
| references/handoff-template.md | 写 Current State 前 |
| references/wip-git-policy.md | 处置 WIP 前 |

## Handoffs / Anti-patterns
- 同一 issue 交接 ≥3 次 → 已非任务层问题:INVOKE tc-research skill 重做研究,再 INVOKE tc-plan skill。
- 本周 ≥5 次 → 向用户点出(burnout 信号,`multica issue runs <id>` 可见模式)。
- 禁:带未提交的有效改动 /clear;漏写 Dead ends(重蹈覆辙 ≈ 2× 时间);Next action 空话(必须点名文件/函数);在本流程改 CLAUDE.md(其变更走月度评审)。

> multica 不在 PATH → 提示安装/更新;unknown flag → 先 `multica update`,仍失败则停下问用户;
> 当前用户身份经 `multica auth status` + `multica user list` 运行时解析,绝不硬编码。
