# Skill 冒烟测试结果 — 2026-05-27

在全新的 Claude Code 会话里手工测试：粘贴触发短语，确认对应的 skill 被调用。标 PASS 或 FAIL。

| Skill | 触发短语 | 状态 |
| --- | --- | --- |
| pre-clear | "I want to /clear" | PENDING |
| rpi-research | "Let's research X" | PENDING |
| rpi-plan-template | "Write a plan for X" | PENDING |
| rpi-implement-discipline | "Let's start implementing" | PENDING |
| debrief-template | "Project done, debrief" | PENDING |
| anti-pattern-self-check | "Am I doing this right?" | PENDING |
| context-pollution-detector | "We're going in circles" | PENDING |
| phase-01-kickoff | "启动新项目" / "kickoff new project" | PENDING |
| monday-kickoff-protocol | "周一 kickoff" / "Monday meeting" | PENDING |
| friday-demo-protocol | "周五 demo" / "betting table" | PENDING |
| role-assignment-protocol | "认领角色" / "role assignment" | PENDING |
| conflict-adjudication | "冲突" / "意见不合" | PENDING |

**同步状态（机械检查，不含主观判断）：**
- `~/team-context/scripts/sync-to-local.sh` 于 2026-05-27 14:10 执行完毕，12 个 skills 全部 symlink 到 `~/.claude/skills/`。
- 验证：`ls -la ~/.claude/skills/ | grep team-context` 应该显示 12 条软链，指向 `/Users/feibo/feibo/team-context/skills/*`。

**测试方法：**
1. 在任意项目中打开一个全新的 Claude Code 会话（比如 `cd /tmp && claude`）。
2. 对每个 skill：逐字粘贴触发短语。模型应在首次响应中通过 `Skill` 工具调用对应 skill。
3. 把 `PENDING` 替换为 `PASS` 或 `FAIL`。若 FAIL，打开 `SKILL.md` 把 `description:` 字段打磨得更锋利（补上漏掉的触发词、收紧用例描述），再重测。

**关于 description 字段**：`description:` 的每一行都占用模型的 attention budget。别用正文内容把它塞满。用 1-3 句话收尾时附上明确的触发短语；模型把这些当作子串匹配在用。
