AI MIQ · GROUP SOP · v0.4 · REFERENCE HANDBOOK

# 我们 5 个人 怎么共同工作

v0.4 是**参考式 Handbook** · 不是规章 · 也不是流程模板 · 规定*做什么* + *什么时候做* · 不规定*用什么工具* + *什么参数*。  
  
工具配置由团队成员根据习惯决定 · 具体场景沉淀到 cases 慢慢成型 · **真正不可妥协的只有 2 件事 · 其他都是参考**。

VERSION

v0.4

DATE

2026-05-25

不可妥协

2 件事

SUPERSEDES

v0.3(归档)

这份文档规定**做什么** · 不规定**用什么工具**。  
工具配置、模型选择、参数调试 · 团队成员自己决定。  
个人沉淀到自己的 cheat sheet · 团队共享沉淀到 cases。  
  
**真正不可妥协的只有 2 件事**:  
① 必有 Plan Model(不允许 vibe code)  
② 项目/任务结束必有 debrief(写到 cases/)  
  
其他都是参考路径 · 团队可以借鉴 · 不必照搬。

PRINCIPLES · 稳定层

## 8 个原则模块

每个模块 1-2 页 · 团队全员必读一遍 · 一旦定稿改动罕见。

[](#p-01)

01

7 条核心原则

2 件不可妥协 + 5 条工作纪律 · 所有动作的上位依据

~ 1.5 页 · 全员必读

[](#p-03)

02

RPI 框架 · 三阶段

Research → Plan → Implement · plan markdown 必备字段 · 不规定工具

~ 2 页 · 全员必读

[](#p-04)

03

沉淀三层 · L1 / L2 / L3

CLAUDE.md(高门槛抽象)+ cases/(无限累积具体)+ 中间层

~ 1.5 页 · 全员必读

[](#p-05)

04

DRI 模式 + 职责四类型

每个项目一个 DRI 全权 · 实习生也可以是 DRI · 冲突裁定原则

~ 1 页 · 全员必读

[](#p-06)

05

节奏 · 日 / 周 / 月

Agent 自动 summary · 周一 Kickoff + 周五 Demo + 月度 burnout check

~ 1 页 · 全员必读

[](#p-07)

06

10 条反 pattern

别人踩过的坑 · BCG / METR / HBR 真实研究数据 · 我们绕开

~ 1.5 页 · 全员必读

PLAYBOOKS · 参考示例

## 4 个场景参考

每个 playbook 是一个场景*参考示例* · 不是"必须按这样走" · 团队成员根据具体情况借鉴。

[](#pb-01)

PB · 01

新项目 · greenfield

完整 RPI 三阶段方法参考 · 适合启动 AI 招聘平台 / 要抱抱 这类大项目

~ 2 页 · 启动前读

[](#pb-02)

PB · 02

修 bug · 轻量任务

跳过 Research · 直接 Plan + Implement · 适合 debug / 小优化 / 反馈处理

~ 1 页 · 启动前读

[](#pb-03)

PB · 03

多 Agent 协同 · 示例

什么时候考虑多 agent · 一个真实启动示例 · 不是强制流程

~ 1 页 · 想试时读

[](#pb-04)

PB · 04

无人值守批量 · 示例

什么时候适合让 Claude 自己跑 · 一个真实启动示例

~ 1 页 · 想试时读

READING PATHS · 怎么读

## 3 条阅读路径

路径 1 · 第一次读 · 1.5 小时

README → 01(7 条原则) → 02(3 Levels) → 03(RPI) → 04(沉淀) → 05(DRI)

路径 2 · 启动新项目前 · 15 分钟

02(选 orchestration mode) → 对应的 playbook → 08(模型配置 + budget cap)

路径 3 · 规避坑 · 30 分钟

07(10 条反 pattern) → 04(沉淀健康度) → 月度 burnout check

v0.3 → v0.4

## 从规章式 SOP · 改成参考式 Handbook

[TABLE]

COEXISTENCE · 与其他文档关系

## 这份 SOP 与 Team Context 三件套

[TABLE]

**AI MIQ TEAM · GROUP SOP v0.3 · HANDBOOK + PLAYBOOK · INTERNAL**  
  
**v0.2.3 → v0.3 路径**:  
v0.1 讨论稿(4 章) → v0.2 evidence-based(10 section) → v0.2.1(5-10 baseline) → v0.2.2(全程 Opus + 铁律) → v0.2.3(2 非妥协 + debrief 流程) → **v0.3 模块化重构**  
  
**对标参考**:GitLab Handbook · Basecamp Shape Up · OpenAI 内部 sub-SOP  
  
**证据来源**:Anthropic 官方 / Boris Cherny / Dexter Horthy / Sulman Choudhry(OpenAI)/ Even Westvang(Sanity)/ Brian Emerick(Vercel)/ Cursor / METR / BCG / HBR / rody(0x\_rody · 2026-05-24)/ + 10+ 真实实践  
  
本文档与 team\_manifesto.md · team\_context\_constitution.md 协同存在 · 三者各司其职。

MODULE 01 · PRINCIPLES

# 7 条不可妥协的 核心原则

所有动作的上位依据 · 当 SOP 没覆盖某场景时,用这 7 条裁判 · 它们是**不可妥协的** —— 当具体动作和某条原则冲突时,以原则为准。

READ TIME · **~ 8 分钟** AUDIENCE · **全员必读** UPDATE · **罕见**

01

### Research / Plan / Implement 严格分离

不要让 Claude 在研究的同时规划 · 在规划的同时实施。三个 discrete sessions · 三个不同的 prompt · 中介是 **Markdown plan 文件**。

具体动作见 [03 · RPI 框架](#p-03)。

参考:Sam Brickman / Ambral CTO · Dexter Horthy · HumanLayer RPI 框架

02

### Context 浑浊时立刻重启 · 不要 fix

Claude 的 context window 用太满会进入 **"dumb zone"** · 输出质量下降 · 但自己感觉不到。*识别信号 + 立刻重启*是工作纪律。

**常见 context 浑浊信号**:

- Claude 开始说 `"You're absolutely right"` · 过度迎合
- 重复之前已经否定的方案
- 答非所问 · 或者抓不住重点
- 解决"上一个问题的衍生" · 而不是当前问题

看到任一信号 → **新开 session** · 把关键信息重新交付。具体的 context 阈值由个人判断(不同任务、不同工具默认不同)。

参考:Dex Horthy 100k+ session 分析 · AI Engineer Code Summit 2025

03

### 并行 Agent 是工作节奏 · 大致 5-10 active

不是"偶尔多开几个" · 是**同时 active 多个 Claude**(团队大致节奏)· 每个人可以配 worktree 长期挂着 · 按需启动。

5 人团队 = 25-50 个 Agent 单元并行运行 · 这是 AI Native 工作方式的基本物理量。

具体每个人开多少 · 按自己舒服的节奏。**避免极端**:1-2 个太少(没用上 AI Native)· 50+ 太多(质量崩溃)。

参考:Boris Cherny 个人日常 · HumanLayer CodeLayer · GitHub Issue \#42796

04

### "Start over" 优于 "fix"

当 Claude 走偏 → 中断 + 重启 · **不要试图纠正**。10-20% 的 session 直接放弃是健康的。

"卡 30 分钟还没进展 → start over" 是个有用的 reminder · 具体阈值按个人判断。

参考:Boris Cherny · Anthropic Data Science "slot machine" 模式

05

### CLAUDE.md 是高门槛抽象层 · cases/ 是无限累积具体层

沉淀分两个根本不同的世界:**抽象**(给 Agent · 必须精炼)vs **具体**(给人 + Agent 按需 · 可无限累积)。

CLAUDE.md 进入门槛:**这条规则适用于*未来所有*类似项目**(不是只这个项目的具体情况)· 建议控制在 2-3k token。

具体项目 debrief 写到 `cases/YYYY-MM-DD-name.md` · 无限累积 OK。

详见 [04 · 沉淀三层](#p-04)。

参考:Boris Cherny CLAUDE.md = 2.5k token · 每周更新多次 · Anthropic 内部团队 + Sanity 6 周实战

06

### Plan Mode 不可妥协 · 不允许 vibe code

每个非平凡任务**必须先生成 plan 文件**(Markdown · 可读 · 可审 · 可改)· 通过第二个 session 做 review · 只有 plan 通过才进入执行。

任务层至少 3 句话 plan · 项目层完整 plan markdown · **永远不允许 "vibe code"**。

这是 **2 个不可妥协之一**。

参考:Boris Cherny · Dex Horthy "Do Not Outsource The Thinking"

07

### 项目/任务结束必有 Debrief

项目或任务完成后**必须写 case file**(`cases/YYYY-MM-DD-name.md`) · 提炼出的*通用规则*才进 CLAUDE.md · 具体记录留 case。

"做完就走 · 不写 debrief" = 项目没结束。debrief 不是流水账复盘 · 是*拆解关键判断的因果链*。

具体动作见 [03 · RPI 框架](#p-03) 收尾阶段。

这是 **2 个不可妥协之二**。

参考:Sanity 工程团队 / Anthropic 内部 review 实践

**这 7 条里 · 真正不可妥协的只有 2 件事**:#6(Plan Mode · 不允许 vibe code)和 \#7(项目结束必有 debrief)。  
其他 5 条是*工作纪律 / 团队节奏* · 团队成员按自己习惯实践 · 实操中校准。  
  
**工具配置不在这里规定** —— 用什么 model / 什么 effort / 什么界面 · 团队成员自己决定 · 沉淀到 cases 慢慢成型。

MODULE 03 · PRINCIPLES

# RPI 框架 三阶段动作

Research → Plan → Implement 三个 discrete sessions · 不是一个长对话 · 中介是 Markdown plan 文件 · 这是 v0.3 SOP 的**骨干流程**。

READ TIME · **~ 12 分钟** AUDIENCE · **全员必读** UPDATE · **罕见**

## 两个非妥协 · 只有这 2 条

v0.2 之前我们写过 3 条非妥协 · v0.2.3 收敛到 2 条 · 其他都不再是"非妥协" · 是建议路径。

非妥协 1

必有 Plan Model

项目走完整 RPI(Research → Plan → 第二个 session review) · 任务至少有 3 句话 plan markdown · **永远不允许 vibe code**。

非妥协 2

项目/任务结束必有 debrief

写成 case file(`cases/YYYY-MM-DD-name.md`)· 提炼出的*通用规则*才进 CLAUDE.md · 具体记录留在 case 里。

沉淀的具体规则见 [04 · 沉淀三层](#p-04)。

## 两层粒度 · 项目 vs 任务

所有新事情先判断属于哪一层 —— **唯一的判断标准是:它是不是一个独立的大目标?**

[TABLE]

## Plan Markdown 必备字段

无论项目还是任务 · plan markdown 必须包含以下 **4 个字段**(替代 v0.1 的"6 问"):

[TABLE]

## 三阶段总图

所有事情走这三个阶段。**三阶段是骨架,每个阶段都是 discrete sessions,不是一个长对话。**

[TABLE]

## PHASE 01 · 启动 · 完整 6 步

"Don't make Claude do research while it's trying to plan, while it's trying to implement. Use discrete prompts and make those into discrete steps."

— Sam Brickman · Ambral CTO · YC W25

STEP 1 · 5 分钟

一句话声明意图

飞书群发一条消息:*"我想做 X · 因为 Y · 大概要 Z 时间 · 这是 \[项目/任务\]。"*

不需要详细思考 · 只是声明意图 · 让团队知道。

STEP 2 · Research

启动 Research session

启动一个新的 Claude Code session:

"请帮我研究 X · 先读 CLAUDE.md 和相关 skills/ · 然后用 subagent 并行研究:① 我们现有代码相关部分 ② 业界已有做法 ③ 潜在的坑。把结果写成 research\_\[date\]\_\[topic\].md · 放 docs/research/。"

这个 session **只做研究 · 不做规划** · Context 用到 30-40% 就结束。

STEP 3 · Plan

启动 Plan session · 全新 context

启动新的 Claude Code session(Opus 4.7 · xhigh · 全新):

"请阅读 docs/research/research\_\[date\]\_\[topic\].md · 用 Plan Mode 制定实施 plan · 分成 discrete phases · 每个 phase 有清晰输入/输出/验证标准 · 输出到 docs/plans/plan\_\[date\]\_\[topic\].md。"

**关键**:plan 文件是*人和 Agent 之间最重要的接口* · 人 review markdown · 改 markdown · Claude 后续基于 markdown 执行。

STEP 4 · Review

第二个 session · Plan 审查

在第二个 Claude Code session(Opus 4.7)运行:

"我刚做完一个 plan · 文件在 docs/plans/plan\_\[date\]\_\[topic\].md  
请你以 staff engineer 角色 review · 重点指出技术风险 / 不一致 / 被忽略的边界情况 / 过度工程"

**必须是第二个 Claude**(context 不同 · 会发现第一个 Claude 漏掉的问题)。

STEP 5 · 拍板

DRI 拍板 · 修订 plan

DRI 做最终决策:

- 看 research:这件事真的值得做吗?
- 看 plan:方案对吗?有没有走偏?
- 看 review:有没有漏掉的关键风险?

输出:plan markdown 修订到 v0.x · 标记"已批准 · 可执行" · 这是**整个启动阶段唯一需要人专注思考的环节**。

STEP 6 · 广播

广播 · 项目 vs 任务不同

**项目层**:DRI 在飞书群发简短消息 + plan 文件位置 · 24 小时内全员快速 review · 没有重大反馈 = 默认通过

**任务层**:Agent 自动登记到 Team Context · 不打扰其他人 · 直接进入执行

## PHASE 02 · 执行 · 每日 5 个动作

"I run 5 Claudes in parallel in my terminal. I number my tabs 1-5, and use system notifications to know when a Claude needs input."

— Boris Cherny · Claude Code 创建者 · 2026-01

DAILY 01 · 早上

启动 5-10 个 Claude

- 读自己负责的 plan markdown · 确认今天要做的 phases
- 用 git worktree 创建 10-15 个工作区(长期挂着 · 不是每天重建)
- 启动 5-10 个 active Claude(全员对齐 baseline)
- 给每个 Claude 派一个 phase · 启动 Claude Code session(全程不区分阶段)

orchestration mode 选择见 [02 · 3 Levels + Decision Matrix](#p-02) · Level 3 团队可用 Lead Opus + Teammates Sonnet 双轨。

DAILY 02 · 监督

监督 chain of thought · 手指放 ESC 上

**关键时刻:当 Claude 开始一个任务的前 30 秒**

- 盯它的 chain of thought · 看方向对不对
- 方向不对 → **立刻 ESC 中断** · 不要让它跑完错误方向
- 看到 "You're absolutely right" → 立刻 /clear 或新启 session

Vulcan CEO Tanner Jones · YC S25 · "前几次 tool call 抓到走偏比让 Claude 完整跑完错误省时间多了"

DAILY 03 · 卡住

遇到错误 · start over · 不要 fix

**当 Claude 第一次没做对时**:

- 不要"和它讨论怎么改对"
- /clear 或开新 session
- 把 plan markdown 改得更清楚
- 让新 session 重新执行

**10-20% 的 sessions 被放弃是健康的** · 这不是失败 · 是 AI Native 工作方式。

DAILY 04 · 微更新

中午 5 分钟 · CLAUDE.md 微更新

把上午发现的 Claude 反复犯错加进 CLAUDE.md · 立刻 git commit + push · 团队同步

格式:*"❌ 不要 X · 因为 Y · 应该 Z"*

注意:微更新前先判断 —— 这条是*通用规则*还是*这个项目独有的*?后者只进 case file · 不进 CLAUDE.md。详见 [04 · 沉淀三层](#p-04)。

DAILY 05 · 收工

傍晚 · Agent 写 daily summary

Agent 基于今天的决策日志 + commits 自动生成 daily summary · 写入 Team Context · 飞书群推送 · 人 30 秒过目。

包含:① 完成的 phases · ② 启动的 sessions · ③ 放弃的 · ④ 决策日志 · ⑤ 卡在哪里

原则:进度衡量来自**工作产物本身**(commit / decision log / 完成的 phase) · 不是"主动汇报"。

## PHASE 03 · 收尾 · debrief 流程

debrief 不是流水账复盘 · 不是"列出做了什么" ·  
是**拆解关键判断的因果链** · 提炼出下次能复用的东西。

每个项目/任务结束都要写 case file · 但**只有 10% 的发现会进 CLAUDE.md** · 90% 留在 case 文件作为具体记录。

STEP 1

Agent 自动生成 debrief 草稿

项目/任务完成时 · 启动一个新 Claude Code session:

"请阅读 docs/research/\[date\]\_\[topic\].md · docs/plans/\[date\]\_\[topic\].md · 这个项目相关 commits · 生成 debrief 草稿写到 cases/YYYY-MM-DD-\[project-name\].md。  
  
必须包含 5 个 section:  
① 目标(plan 里原始目标)  
② 实际做的事(压缩时间线 · 不超过 200 字)  
③ 完成标准 + 是否达成  
④ 关键判断分析 — 真实成败原因 · 不要场面话  
⑤ 通用规则候选 — 适用于未来所有类似项目?如有列出 + 标记'需要 DRI 决定是否提升'"

STEP 2

DRI review · 校准真实成败原因

DRI 读 Agent 生成的 case file 草稿 · 重点 review section ④:

- Agent 抓到的"成败原因"是真实的还是表面的?
- 有没有 Agent 没看到的关键判断点?
- "如果重来一次 · 哪个判断会改?"
- "古法不可能"在哪一步发生了?

这是**整个 debrief 唯一需要人专注思考的环节** · Agent 草稿不替代这一步。

STEP 3

DRI 决定:提升到 CLAUDE.md?

对 section ⑤ 的每个"通用规则候选" · DRI 用 1 个问题判断:

**这条规则适用于*未来所有*类似项目吗?**  
(不是只这个项目的具体情况)  
  
✅ YES → 提升到 CLAUDE.md · 同时保留 case file · 写成抽象规则(不带具体项目名) · 控制总 token &lt; 3k  
❌ NO → 只留 case file · 不进 CLAUDE.md · 累积无上限 OK

STEP 4

项目层:周五 demo

仅项目层需要 · 周五下午 30 分钟 · DRI demo 这个项目的结果 · 全员看 · 不需要 PPT · 直接演示真实产物。

原则:demo 是**对结果的庆祝** · 不是"汇报会" · task 级别不需要 demo。

**这份 RPI 不是僵化模板**:  
实操中可以跳过某些步骤(任务层跳 Research)、重新排序(先有 plan 雏形再回头研究)、并行同一阶段(5 个 agent 同时 implement) · 真正的非妥协只有上面 2 个 · 其他都是建议路径 · 团队按场景灵活组合。

MODULE 04 · PRINCIPLES

# 沉淀三层 L1 抽象 · L2 具体 · L3 中间

沉淀分两个根本不同的世界:**抽象**(给 Agent · 必须精炼)vs **具体**(给人 + Agent 按需 · 可无限累积)· v0.2 之前混在一起 · v0.3 严格分开。

READ TIME · **~ 10 分钟** AUDIENCE · **全员必读** UPDATE · **罕见**

## 三层架构 · 一张总图

[TABLE]

**核心区别**:L1 是高门槛 / 硬上限 / 给 Agent · L2 是低门槛 / 无上限 / 给人 · 这两层是 v0.3 沉淀架构的*根本设计* · 其他层是支撑。

## L1 · CLAUDE.md · 进入门槛是死的

只有一种内容能进 CLAUDE.md:  
**这条规则适用于未来*所有*类似项目**  
不是只这个项目的具体情况

— Boris Cherny · Anthropic 内部团队实践

✅ 应该进 CLAUDE.md

- "所有 SQL query 必须带 timezone"
- "完成标准必须可观测 · 不能是'做好为止'"
- "❌ 不要在 useEffect 里做 derived state"
- "DRI 拥有项目全权决策"

关键词:所有 · 通用 · 跨项目

❌ 不进 CLAUDE.md(留 case)

- "AI 招聘平台用了 X 库做能力评估"
- "要抱抱第 3 个按钮颜色 \#C73E1D"
- "5/15 试 prompt A 不好 · 换 B"

关键词:这一个 · 具体 · 这一次

### CLAUDE.md 推荐结构(2-3k token)

\# AI MIQ Team Context · CLAUDE.md  
  
\## Who we are · 30 words  
我们是一个 5 人 AI Native 团队 · 做 AI 招聘平台 / 要抱抱 / Team Context · 不在中国运营 · Claude 是默认协作伙伴  
  
\## How we work · 5 rules  
1. Research → Plan → Implement 严格分离 · 不要 vibe code  
2. Context 永远 &lt; 40% · 看到 "You're absolutely right" 立刻重启  
3. 卡 30 分钟 → start over,不要 fix  
4. 项目结束必有 debrief · 提炼出的通用规则才进这个文件  
5. 项目有 DRI · DRI 拥有全权  
  
\## Tech stack rules · 跨项目通用  
- Frontend: React + TypeScript + Tailwind · 不用 inline style  
- Database: PostgreSQL · 所有 query 必须带 timezone  
- ...  
  
\## Mistakes Claude must not repeat · 跨项目通用  
- ❌ 不要把 import 放在文件中间  
- ❌ 不要用 useEffect 处理简单 derived state  
  
\## How to call other Claude sessions · subagent patterns  
- Research: opus-4-7 + xhigh + 单一研究目标  
- Plan: opus-4-7 + xhigh + 读 research → 输出 markdown  
- Review: 启动第二个 session 做 review  
  
\## What to do when you're stuck  
不要 fix · /clear 重新开始 · 升级 plan markdown  
  
\## How to find specific context  
具体项目细节 → cases/YYYY-MM-DD-\*.md  
具体 prompt 模板 → .claude/skills/  
具体判断标准 → standards/

**关键设计**:最后一节 "How to find specific context" 告诉 Claude 去哪找具体内容 · CLAUDE.md 本身保持精炼 · 但 Agent 知道怎么按需查 cases/ 和 skills/。

## L2 · cases/ · 无上限累积层

每个项目/任务结束都写一个 case file · 不需要担心数量 · 累积 50 · 100 · 500 个都 OK · 因为它**不影响 Claude 的 context window**。

### 命名格式

cases/YYYY-MM-DD-project-name.md  
  
例:  
cases/2026-05-15-ai-hr-competency-prompt.md  
cases/2026-05-20-yaobao-onboarding-failed.md  
cases/2026-05-22-team-context-iteration-v3.md

### case file 必备 5 个 section

\# \[项目名\]  
日期 · DRI · 参与人  
  
\## 1. 目标  
\[plan 里写的原始目标\]  
  
\## 2. 实际做的事  
\[压缩时间线 · 200 字以内\]  
  
\## 3. 完成标准 + 是否达成  
- 标准:\[plan 里写的\]  
- 实际:\[达成 / 部分达成 / 未达成\]  
- 差距:\[如果有 · 写出来\]  
  
\## 4. 关键判断分析(真实成败原因)  
- 关键判断 1:\[做了什么\] · 对错 · 因果  
- 关键判断 2:...  
- 如果重来:\[哪个判断会改\]  
  
\## 5. 通用规则候选  
- \[候选 1\] · 需要 DRI 决定:提升到 CLAUDE.md?  
- \[候选 2\] · ...

### cases/ 的 3 个使用场景

- **月度 review** · 全员读上月所有 case · 看哪些项目"古法不可能" · 哪些失败可以避免
- **新人 onboarding** · 第一周读最近 10 个 case · 比读 SOP 学得快
- **Agent 按需主动查** · 类似项目启动时 · Agent 可以 prompt 加载相关 case

## 提升路径 · case → CLAUDE.md

每个项目 debrief 时 · DRI 判断 case 里的"通用规则候选"能否提升:

[TABLE]

**经验数据**:每个项目大约 **10% 的发现**会被提升到 CLAUDE.md · 90% 留在 case 文件作为具体记录 · 这是健康比例。

## CLAUDE.md 健康度 · 月度 review

每月最后日 · 1 小时全员 · 检查这 5 个指标:

[TABLE]

MODULE 05 · PRINCIPLES

# DRI 模式 + 职责四类型

没有层级关系 · 没有预设角色 · 每个项目一个 **DRI** 拥有全权 · 包括实习生可以是 DRI · 职责按任务认领 · 不按职位贴标签。

READ TIME · **~ 8 分钟** AUDIENCE · **全员必读** UPDATE · **罕见**

## DRI · Directly Responsible Individual

每个项目有一个 DRI ·  
DRI 拥有这个项目的**整个**可见性、决策权、最终结果责任 ·  
不像很多公司分"产品 DRI + 工程 DRI + 设计 DRI" —— 我们一个项目就一个 DRI。

— Sulman Choudhry · OpenAI ChatGPT 工程团队 · 2026-03

### DRI 的三个属性

[TABLE]

## 职责的四种类型

每个项目启动时 · 把工作按下面四种职责类型拆解 · 然后由团队成员认领。**同一人可承担多种职责 · 同一职责也可由多人共同承担**。

[TABLE]

## 职责认领 · 6 条规则

[TABLE]

## Generalist 优先 · 不要早早贴标签

OpenAI 内部用的是**哑铃模型**:  
一头是极端 generalist(跨 mobile / frontend / backend / 工程 / research 都能做)·  
一头是极端 specialist(某领域世界级专家) ·  
**中间地带是被替代的**。

对我们 5 人:

- **都应该是 generalist** · 不要把人贴标签为"前端 / 后端 / 设计 / HR"
- Aaron 的 HRBP 背景 + Claude Code = 可以直接迭代 AI HR 产品的核心逻辑 · 不需要等"工程师来实现"
- 研发也应该理解产品 · 实习生也应该参与决策
- **模糊 research / engineering / 产品的边界是优势 · 不是问题**

## 实习生也可以是 DRI

**这是我们和传统团队最大的区别之一**。  
实习生作为 DRI 时 · 他对项目的可见性最完整 · 不应该被 Aaron 的"经验"覆盖 · 否则就不是真正的 DRI · OpenAI 内部就是这个原则。

### 实习生作 DRI 时 · 如何避免 Aaron 不自觉接管

- Aaron 提供**判断材料** · 不替他做**判断本身**
- Aaron 表达**担心** · 不下**命令**
- 实习生 DRI 最终拍板 · 即使 Aaron 不同意 · 也记录在 decisions/ 里
- 如果 Aaron 真的认为这是个错误判断 · 提出 review · 但不强制改
- 项目复盘时 · 不论结果如何 · 都不能用"我早就说过"

## 认知行为的自负责

"对自己的认知行为负责"是我们工作的核心 · 它具体意味着:

[TABLE]

## 冲突如何裁定 · 4 条原则

[TABLE]

**为什么"即使 DRI 是实习生"也成立**:实习生作为 DRI 时 · 他对项目的可见性最完整 · 不应该被 Aaron 的"经验"覆盖 · 否则就不是真正的 DRI · OpenAI 内部就是这个原则。

MODULE 06 · PRINCIPLES

# 节奏 日 / 周 / 月

人不写每日报告 · Agent 自动生成 summary · 人 review 关键节点 · Daily Standup 已死 · 保留 Monday Kickoff + Friday Demo + 月度 burnout check。

READ TIME · **~ 6 分钟** AUDIENCE · **全员必读** UPDATE · **季度**

## 每日节奏

[TABLE]

**没有 Daily Standup**。  
传统团队的"昨天/今天/卡点"已经被 Agent 自动 summary 取代 · 不需要再开会。

## 每周节奏

[TABLE]

## 每月节奏

[TABLE]

## 月度 Burnout Check · 3 个问题

AI 用户 burnout 比非 user 高 88% · 每组织 $9M 浪费 ·  
我们 baseline 是 Boris Cherny 水平 · 认知负荷不低 · burnout 是 SOP 的红线。

每月最后 30 分钟 · 全员明确回答这 3 个问题:

1.  这个月跑 5-10 active Claude · 你觉得疲惫吗?
2.  有没有出现"看到通知就反感"的情况?
3.  下班后还在想 Claude session 状态吗?

**出现任何 yes** · 这个月先降到 3-5 active 调整 · 不要硬撑 · 恢复后再回到 5-10 baseline · 这是**刹车机制 · 不是后退**。

## "古法不可能"事件清点

每月最后 30 分钟 · 全员清点本月我们做的事 · 找出哪些在传统 5 人团队**古法不可能完成**:

- 5 人在 1 周内 ship 一个完整 feature(传统需要 1 个月)
- 实习生独立完成一个有商业价值的产品迭代
- 同时维护 3 个产品线 · 而且每个都在进步
- Aaron 一个人 prototype 完整 AI HR 工作流 · 不需要等工程师

**这是 AI Native 健康度的最终指标**。  
不是"用了多少 token"、"跑了多少 session" · 是 **"我们做了多少件古法不可能的事"**。

MODULE 07 · PRINCIPLES

# 10 条反 pattern 不要这样做

别人踩过的坑 · BCG / METR / HBR / Sanity / Digital Applied 真实研究数据 · 我们直接绕开 · 不重复试错。

READ TIME · **~ 8 分钟** AUDIENCE · **全员必读** UPDATE · **偶尔(新坑出现时)**

"The tool that makes good judgment better  
makes poor judgment catastrophically worse."

— BCG study · 2025-12 executive briefing

## 10 条反 pattern

❌ 01

让 Claude review 它自己的代码

找不到结构性 bug · 只能找到表面问题。必须用**第二个 Claude**· 或者人 review。

EVIDENCE · Sanity 工程团队 6 周实战

❌ 02

同一个 problem space 并行多个 Claude

会失去对不同 session 在解决什么问题的追踪 · 5-10 active 应该是**不同问题空间**。

EVIDENCE · Sanity / Even Westvang · 2026

❌ 03

让 50+ Agent 同时跑

"每一个 Agent 都变成白痴" · 10+ session 同时质量崩溃。我们 5-10 active 是**有意识的上限**。

EVIDENCE · GitHub Issue anthropics/claude-code#42796 · 2026-04

❌ 04

CLAUDE.md 当 "junk drawer"(超 3k token)

信息太多 Claude 读不进 context window · 反而降效。**case-specific 内容必须留 case file** · 不进 CLAUDE.md。

EVIDENCE · Digital Applied · 2026 / Anthropic 内部 prune 实践

❌ 05

skills/ 没有 owner · 加完就走

提交人离职后 skill 漂移 · 没人记得它是干什么的。每个 skill 必须有 owner + 上次 review 日期。

EVIDENCE · Digital Applied · 2026

❌ 06

用 AI 做"超出能力前沿"的事

错误率反而**上升 19 个百分点**。启动 Research session 时第一个问题:"这件事在 AI 的能力前沿内吗?"

EVIDENCE · BCG study · 2024

❌ 07

把"用户使用率高"当作 transformation

很多团队 95% 使用率但 .claude/skills/ 是空的 · 只是 autocomplete。**沉淀质量 &gt; 使用频率**。

EVIDENCE · Digital Applied · 2026

❌ 08

经验丰富的开发者在熟悉 codebase 上用 AI

METR RCT:**反而慢 19%**(虽然自我感觉快 20%)· 直接写比让 Claude 写更快的场景真实存在。

EVIDENCE · METR · Joel Becker et al · 2025-07

❌ 09

"效率至上" · 把 AI 能做的都给 AI 做

AI 用户 burnout 比非用户高 **88%** · 每组织 $9M 浪费。月度 burnout check 是 SOP 的红线。

EVIDENCE · HBR · "6 Things That Failed in 2025"

❌ 10

没有 DRI · 项目无主

Agent 不知道听谁的 · 决策推不动 · AI Native 团队**最常见的失败**。每个项目必须有且仅有一个 DRI。

EVIDENCE · Sulman Choudhry · OpenAI · 2026-03

## 3 条对我们最危险

这 10 条都重要 · 但下面 3 条是**我们 5 人团队最容易踩**:

[TABLE]

**这 3 条是*红线***:任何一条出现迹象 · DRI 必须立即介入 · 不要等月度 review。

PLAYBOOK 01 · GREENFIELD

# 新项目 · 参考示例

场景:启动一个独立的新项目(例:AI 招聘平台某个 feature · 要抱抱新模块 · Team Context 自身迭代)· 不确定性高 · 适合走完整 Research → Plan → Implement → Debrief。 下面是一种参考方式 · **不是必须按这个走**。

SCENARIO · **新项目 + 不确定性高** DURATION · **大致 3 天 - 2 周**

## 启动前 · 自检 4 项

这件事真的是**项目层**而不是任务层?(独立大目标 + 涉及整个团队)

这件事在 AI **能力前沿内**?(反 pattern ❌6)

我自己是 DRI · 还是另有人?

我能投入 **3 天-2 周** 的连续 attention?

## PHASE 1 · 启动(半天-1 天)

STEP 1 · 5 分钟

声明意图

飞书群发:*"我想做 X · 因为 Y · 这是**项目层** · 预计 N 天 · DRI 是我。"*

STEP 2 · 30 分钟 - 2 小时

Research session

启动新 Claude Code session:

"请研究 \[项目主题\]  
  
先读:  
- CLAUDE.md(团队 context)  
- standards/ 里相关判断  
- cases/ 里类似项目(过去 6 个月内)  
  
用 subagent 并行研究:  
1. 我们现有代码相关部分  
2. 业界已有做法(2024-2026)  
3. 潜在的坑  
4. 类似 case 的成败原因  
  
输出 docs/research/research\_\[date\]\_\[topic\].md  
结构:① 现状 ② 业界做法 ③ 潜在坑 ④ 推荐方向 ⑤ 风险  
每段不超过 150 字"

STEP 3 · 1-2 小时

Plan session(全新 context)

启动另一个新 Claude Code session(全新 context):

"请阅读 docs/research/research\_\[date\]\_\[topic\].md  
  
用 Plan Mode 制定实施 plan · 分成 discrete phases ·  
每个 phase 有清晰的:  
- 输入(从哪个 phase 来)  
- 输出(交付什么)  
- 验证标准(怎么知道完成)  
  
输出 docs/plans/plan\_\[date\]\_\[topic\].md  
必备 4 个字段:目标 / 完成标准 / 怎么分 / 时间盒"

STEP 4 · 30 分钟

第二个 session · Plan 审查

第二个 Claude session(Opus 4.7):

"我刚做完一个 plan · 文件在 docs/plans/plan\_\[date\]\_\[topic\].md  
请你以 staff engineer 角色 review · 重点指出:  
- 技术风险  
- 不一致  
- 被忽略的边界情况  
- 过度工程"

STEP 5 · 30-60 分钟

DRI 拍板

DRI 读 research + plan + review · 修订 plan markdown 到 v1.0 · 标记"已批准 · 可执行"。

STEP 6 · 5 分钟

广播

飞书群发简短消息 + plan 文件位置 · 24 小时内全员快速 review · 没反馈 = 默认通过。

## PHASE 2 · 执行(几天-1 周)

### 每天的标准动作

[TABLE]

### 如果遇到 plan 不对

1.  停下当前执行
2.  启动新 Claude session 重新 Plan(可能跳回 Research)
3.  升级 plan markdown 到 v1.x
4.  让第二个 session 重新审查
5.  DRI 拍板 · 继续执行

原则:plan 是*活的* · 但每次修订都走 review · 不要 "vibe code"。

## PHASE 3 · Debrief(半天)

STEP 1 · 30 分钟

Agent 生成 debrief 草稿

启动一个新 Claude Code session · 用 04 模块的 prompt 模板生成 `cases/YYYY-MM-DD-[project].md`

STEP 2 · 1-2 小时

DRI review · 校准 section 4

读草稿 · 校准 "关键判断分析" · 真实成败原因 · 不要场面话。

STEP 3 · 30 分钟

提升到 CLAUDE.md(如有)

对每个"通用规则候选"问:**适用于未来所有类似项目吗?** · YES 才进 CLAUDE.md。

STEP 4 · 30 分钟

周五 demo

DRI 在 周五下午全员 demo · 真实产物演示 · 不需要 PPT · 庆祝。

## 关键提醒 · 5 条

**1.** Research 和 Plan 必须是*不同 session* · 不要让 Claude 一边研究一边规划  
**2.** Code review 必须用*第二个 Claude* · 第一个 Claude 不能 review 自己  
**3.** 卡住时 *start over* 不要 fix · 10-20% 放弃率是健康的  
**4.** Case file 是必须的 · 不写 case = 项目没结束  
**5.** 只有 ~10% 发现进 CLAUDE.md · 90% 留 case · 不要塞 junk drawer

PLAYBOOK 02 · BUG FIX

# 修 bug · 参考示例

场景:debug 某个具体 bug / 小优化 / 处理用户反馈 / 单文件修复 · 可以跳过 Research · 直接 Plan + Implement · 大致 1-3 小时闭环。 下面是一种参考方式 · **不是必须按这个走**。

SCENARIO · **任务层 · 单一明确问题** DURATION · **大致 15 分钟 - 3 小时**

## 什么时候用这个 playbook

[TABLE]

**核心判断**:范围小(1-3 文件) + 问题明确(知道改什么) + 无跨模块依赖 → bug-fix playbook

## 4 步流程 · 总耗时 15 分钟 - 3 小时

STEP 1 · 2 分钟

写 mini-plan(3 句话)

飞书发自己留底 + 写到 plan 文件第一行:

任务:\[一句话说清楚\]  
完成标准:\[1 个可验证信号\]  
边界:\[不要碰什么\]

不是项目层 · 不需要广播 · 不需要 DRI 拍板 · 自己就是 DRI。但 mini-plan 必须有 · **不允许 vibe code**(非妥协 1)。

STEP 2 · 主体时间

单 session 执行 · Opus 4.7

启动 1 个普通 Claude Code session(*不需要* Agent View · 不需要 Level 3):

\[prompt 三条铁律 + 通用模板\]  
  
任务:\[mini-plan 第一行\]  
具体动作:\[动词+数字+具体值\]  
输出:\[diff / 修改的文件 / 测试通过\]  
边界:\[只改 X · 不要碰 Y · 发现别的问题写 TODO\]

不需要 subagent · 不需要并行。

STEP 3 · 5 分钟

人 review + 合并

读 diff · 跑测试 · 验证完成标准 · git commit · push。

不需要项目层那种 review · 但**人必须亲眼看 diff** · Claude ship 的代码就是你 ship 的(原则 Sanity)。

STEP 4 · 2 分钟

轻量 debrief(必须做)

非妥协 2 · 任务也要 debrief · 但**极简版**:

追加到 cases/YYYY-MM-WW-tasks.md(按周合并所有小任务):  
  
\## \[今天日期\] · \[任务标题\]  
- 做了什么:\[1 句话\]  
- 完成标准是否达成:\[YES / 部分 / NO\]  
- 通用规则候选:\[有 / 无 · 有的话列出\]

单独任务 &lt; 1 小时的 · 不开新 case file · 合并到当周 `cases/YYYY-MM-WW-tasks.md` · 月底 review。

## 卡住了怎么办

[TABLE]

**升级信号**:如果一个 bug-fix 任务跑超过 3 小时还没解决 · 说明它*不是任务层* · 应该升级成项目走 greenfield playbook。  
**不要硬撑** · 误判任务粒度是常见错。

## 容易踩的坑

- **不写 mini-plan 直接喂 Claude** → 反 pattern · 非妥协 1 违反 · "vibe code"
- **不亲眼看 diff 直接 merge** → 你 ship 的代码 · 错就是你的
- **跳过 debrief** → 一个月跑了 100 个小任务 · 一个学习都没沉淀
- **用 Agent View / Level 3 跑小 bug** → orchestration 错配 · 浪费时间 + token(见 02 模块 Decision Matrix)

PLAYBOOK 03 · 参考示例

# 多 Agent 协同 · 参考示例

当一个 feature 涉及多个独立模块、并且彼此有交付依赖时 · 可以考虑让多个 Claude session 并行 + 一个 lead session 协调。 下面是一个真实示例 · **不是必须按这个走** · 是给团队第一次想试时的起点参考。

SCENARIO · **多模块协同 feature** STATUS · **Aaron piloted · 团队还没正式用过**

## 什么时候*可以考虑*多 agent 协同

这不是规定 · 是*识别信号*:当下面几条都成立时 · 多 agent 协同*可能*比单 agent 顺序做更快。

- 一个 feature 涉及 **3-5 个相对独立的模块**(例:backend + frontend + tests + review)
- 模块之间有清晰的交付依赖(谁完成什么 · 谁等谁)
- 你能*说清楚*每个 agent 各自做什么(说不清楚就不是这个场景)
- 预计 1-4 小时能闭环 · 不是几天的大项目

**反信号**(说明该用别的方式):3 个独立 feature 没依赖 → 各自单 session 就行 / 单文件 bug → 直接修 / 不确定方向 → 走 greenfield。

## 一个真实启动示例 · Aaron piloted

下面是 Aaron 个人 pilot 过的一个启动方式 · *不是唯一对的方式* · 团队成员可以借鉴或者发明自己的方式。

示例 STEP 1

写一个简短的 team plan

不需要完整 plan markdown · 一段话说清楚每个 agent 做什么:

目标:\[feature 完成后能干什么\]  
完成标准:\[最关键的 1-2 个可验证信号\]  
分工:  
  Agent 1 (Backend): \[模块 · 关键 endpoint\]  
  Agent 2 (Frontend): \[组件 · 用户交互\]  
  Agent 3 (Tests): \[测试覆盖范围\]  
  Agent 4 (Review): 检查 1-3 的产出  
依赖关系:\[Agent 2 等 Agent 1 输出\]  
时间盒:\[小时数\]

示例 STEP 2

在 Claude Code 里描述 team

让 lead 自己拆 · 不要把分工写得太死:

"我需要 build \[完整 feature 描述\]  
  
请 spawn 一个 agent team:  
1. Backend agent: \[职责 · 模块 · 文件\]  
2. Frontend agent: \[职责\]  
3. Testing agent: \[职责\]  
4. Review agent: 检查 1-3 的产出  
  
每个 agent 在自己的 context 里工作 · 通过共享 task list 协调 · 开始依赖任务前先 flag 依赖。"

具体怎么启用 agent team · 团队成员自己查 Anthropic 文档 · SOP 不规定。

示例 STEP 3

监督 + 人 review · 不可省

- 不要每个 agent 都盯 · 看 lead 的协调输出
- 看到 teammate 走偏 → 中断那个 agent
- 全部完成后 → 读 lead 汇总 + 每个 teammate 的 diff
- 跑测试 · 验证完成标准 · 有问题启动新 session 修(**不要让原 team 改**)
- 合并代码 · 人手 git push
- 写 case file `cases/YYYY-MM-DD-[feature].md`(*这是不可妥协 \#7*)

## 团队现状 · 第一次跑怎么开始

**团队还没正式用过 agent team** · 只有 Aaron 个人 pilot 过。第一次跑的建议:  
① **Aaron + 1 个研发 + 1 个实习生**一起 · 边跑边学  
② 跑完写一个真实 case file · 沉淀团队第一手经验  
③ 第二次 / 第三次别人主导 · Aaron 不接管 · 让团队真正掌握  
④ 跑过 3-5 个真实 case 后 · 看是否需要更新 SOP / 写一个团队自己的 best-practice

## 容易踩的坑(参考)

- **无依赖任务硬用多 agent** → 单 session 顺序做反而更快
- **5+ agents 并行** → 质量集体下降(参考反 pattern ❌3)
- **不写 team plan 直接喂 prompt** → lead 拆得很糟糕
- **跳过人 review 直接 push** → 5 个 agent 的产出没看就 push · 风险大
- **用 Claude Desktop App 想跑 agent team** → 团队成员自己确认工具支持

PLAYBOOK 04 · 参考示例

# 无人值守批量任务 · 参考示例

当一批小任务*不需要人盯着*(批量 refactor / 文档更新 / 翻译 / 注释生成)· 可以让 Claude 自己跑 · 你做别的事 · 结束后人 review。 下面是一个真实示例 · **不是必须按这个走**。

SCENARIO · **低风险批量任务 + 你不在场** STATUS · **团队尚未正式用过**

## 什么时候*可以考虑*无人值守

[TABLE]

**核心判断**:如果某个任务失败了影响你睡得着觉吗?睡不着 → 不要 overnight · 睡得着 → 可以。

## 一个真实启动示例

下面是一种可以参考的启动方式 · *不是唯一对的方式*。

示例 STEP 1

睡前 30 分 · 挑 backlog + 写 task list

从飞书 backlog 挑 5-15 个适合无人值守的小任务 · 写到一个 markdown:

docs/plans/overnight\_\[date\].md  
  
\## 今晚跑的 backlog  
  
- \[ \] Task 1: 把所有 console.log 换成 logger · 文件:src/\*\*/\*.ts  
- \[ \] Task 2: 给 utils/date.ts 加测试 · 覆盖率到 90%  
- \[ \] Task 3: 翻译 zh-CN 的 5 个新 UI 字符串  
  
完成标准:每个 task 跑测试通过 + 不动 src/auth/ + 不 push

示例 STEP 2

设安全 guardrails

无人值守没人盯 · 必须有**明确的"不允许做什么"**:

- **不允许**:git push / npm publish / 改 .env / 改 .ssh / 数据库 migration
- **允许**:写 src/ / 写 tests/ / 写 docs/ / 跑测试
- **遇到不确定**:跳过 · 写到 results 文件 · 不要硬上

具体怎么配置 guardrails(settings.json 之类) · 团队成员自己查 Anthropic 文档。

示例 STEP 3

启动 + 设预算上限

让 Claude 按 task list 顺序执行 · 每个 task 写到 results 文件 · 任一 task 失败就跳过下一个。

**预算上限要设**(避免半夜烧光):

- 小 · 5 task → 建议 $10-15
- 中 · 10-15 task → 建议 $30-50
- 大 · 20+ task → 建议 $80-150

具体 CLI 参数怎么设(`-p` mode / `--max-budget-usd`)· 团队成员自己查文档。

示例 STEP 4

早上 review · 决定 merge / 丢弃

1.  读 results 文件 · 看每个 task 状态
2.  对每个完成的 task · 看 diff · 跑测试
3.  OK 的合并 · **人手 git push**(不要让 agent 自己 push)
4.  失败的单独处理 · 走 bug-fix playbook
5.  写 case file(*不可妥协 \#7*)· 记录:成功率 / 实际花费 / 节省的时间

## 容易踩的坑(参考)

- **没设预算上限** → 早上来发现 $300 没了
- **没禁止 git push** → agent 把错误代码 push 到 main
- **tasks 互相依赖** → 一个失败后面全错(应该改用多 agent 协同)
- **把生产敏感的事丢给无人值守** → 自找麻烦
- **不写 case file** → 没数据知道下次预算设多少
- **早上不亲眼看 diff 直接 merge** → 你 ship 的代码就是你的

## 衍生用法 · 不只是"隔夜"

"无人值守"不一定要"晚上跑" · 任何**你不需要全程盯**的批量任务都适用:

- 会议期间跑(2 小时会议 + 同时跑 10 task)
- 周末家庭时间跑
- 跨时区协作时跑
- 等其他项目 review 时跑

**AI MIQ TEAM · GROUP SOP v0.4 · REFERENCE HANDBOOK · INTERNAL**  
  
**v0.3 → v0.4 路径**:  
v0.1 讨论稿 → v0.2 evidence-based → v0.2.3(2 非妥协 + debrief) → v0.3 单文件版(8 原则 + 4 playbook · 规章式)→ **v0.4 参考式 Handbook(6 原则 + 4 playbook · 不规定工具)**  
  
**v0.4 关键变化**:  
① 删 2 章纯工具配置(原 02 Decision Matrix + 原 08 模型/工具)  
② 语气从"必须/默认/不可妥协"变成"可以考虑/一种参考"  
③ 真正不可妥协只有 2 件事:Plan Mode + Debrief  
④ 4 个 playbook 从"5 步流程"变成"参考示例" · 工具配置作为*举例*不是*规定*  
⑤ 修正 v0.3 中 5 处工具事实错误(rody 推文 + 印象拼凑) · 全部从 SOP 移除  
  
**证据来源**:Anthropic 官方文档 · Boris Cherny · Dex Horthy · Sulman Choudhry(OpenAI) · Even Westvang(Sanity) · METR · BCG · HBR  
  
本文档与 team\_manifesto.md · team\_context\_constitution.md 协同存在 · 三者各司其职。  
**SOP 规定*做什么* · 不规定*用什么工具*。工具配置由团队成员自己决定。**
