Build session 的实现循环纪律：开工卡骨架、scope lock、人审 diff、commit 节奏、卡死处理、子 agent 分工。

# 开工：状态转换 + 开工卡（同时机）

`python3 <skills-root>/tc-render/scripts/transition.py build-start <plan-issue>` 把 plan issue
从 `todo`（批准后的待启动）转为 `in_progress`。**这是 in_progress 的唯一设置点**——
计划批准时不设（见 tc-plan skill「批准 ≠ 开工」）；每日 kickoff 广播的「进行中/待启动」
分桶依赖此语义。转换幂等，续作 session 重跑无害。语义细节见 tc-render skill 的
references/issue-label-state-rules.md；流转只走 transition.py，绝不手改 label/status。

仅**该计划的首个** build session 发开工卡；handoff/`/clear` 后重启的续作 session 不重发。
用 remote MCP 工具 `notify_team({ card: ... })` 发到团队飞书群。
tcmcp-remote 未连接 → 明确告诉用户没有发送并给出手动文案，绝不谎称已广播。

开工卡骨架（header = `blue`）：
- 标题：`任务开工 · <任务短名> · MM-DD`
- 概览 fields：DRI / 体量 / 计划（<issue-id> + 已批准）/ 分支
- 内容段：「目标」一句话
- note 页脚：`build session 已开工 · 完成后有复盘 · 进度看 <issue-id>`

# Scope lock（本 session 不做什么）
- ❌ 改 plan——plan 错了就回 Plan session，不在这里改
- ❌ 加 plan 之外的 scope
- ❌ 「顺手优化一下」——另立 plan
- ❌ 「就这一次」跳过人审 diff

# 30 秒规则（人监督 AI）
每段 AI 工具调用序列的前 30 秒：读它的思路（chain-of-thought）。方向错了立刻 ESC 打断，
不要"看看它能走到哪"任其沿错误路径继续。

# Sanity 规则（不可跳过）
AI 的每一处代码改动，commit 前必须有人眼看过 diff。多 agent、过夜跑、批量跑一律适用。
责任规则：AI generated, but YOU ship it——发布出去的是你，出问题算你的。

# Commit 节奏
- 每到测试全绿的边界就 commit（对齐 TDD）
- 绝不超过 30 分钟不 commit（让 tc-handoff 的成本足够低）
- Commit message 引用 plan 小节（如 `feat: criterion 2 — p99 <400ms`）

# 卡死处理
- **Stuck-30**：30 分钟没有任何测试通过、没有进展 → INVOKE tc-handoff skill，推倒重来。
  不要继续硬修——重来胜过修补。
- **3-strike**：同一任务 `/clear` 3 次 → 这已不是任务层问题。升级为项目层，
  从头重走 Research → Plan（从 tc-kickoff / tc-research skill 走完整流程）。

# 子 agent 杠杆（评审/测试/执行 = 独立 session）
「另开 session」类工作默认派**子 agent**承担——全新上下文天然独立，不污染本 session：
- **评审/验证**（测试矩阵、独立复算、red-team 自查）：子 agent 只产出结论/verdict
- **任务层执行**（实现本身）：mini-plan 自批后，派执行子 agent 按精确改动说明动手；
  编排 session 只做 pre-flight、审 diff、跑 transition.py、commit
规则不变：**状态转换与 commit 权始终归本（编排）session**；verdict/交付返回点即动作点。
项目层实现仍走完整流程：plan 评审 → 设计评审门 → build session。
