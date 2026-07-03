# real-user-prompts.md — 真实用户话语语料(双语)→ 目标 skill,触发吃不准时对照本表校准

规则:话语明确指向专家 skill → 直接触发该 skill;话语模糊(只有 issue id / 「继续」类动词)→ 走 tc-router 读 issue 定阶段。

| # | 用户话语 | 路由 | 备注 |
|---|---|---|---|
| 1 | 接手 TEA-88 | tc-router | 读 issue labels 定阶段后交棒 |
| 2 | 继续昨天那个任务 | tc-router | 先定位是哪个 issue |
| 3 | 下一步干嘛? | tc-router | 按当前 issue 阶段判定 |
| 4 | 开始干活吧 | tc-router | 无阶段信息 |
| 5 | 开工吧,issue 是 TEA-102 | tc-router | 有 id 无阶段;若 `设计-已审` 在场则交 tc-build |
| 6 | pick up where we left off | tc-router | 定位最近 in_progress issue |
| 7 | what should I do next on this project? | tc-router | 项目内多 issue 时列证据 |
| 8 | take over the actionow issue | tc-router | 读 labels 再交棒 |
| 9 | 帮我看看这个项目到哪一步了 | tc-router | 只读汇报 + 建议下一个 skill |
| 10 | 我想做一个新项目,团队内部工具 | tc-kickoff | 项目层启动 6 步 |
| 11 | 启动新项目 | tc-kickoff | |
| 12 | kickoff a new direction for billing | tc-kickoff | |
| 13 | 调研一下 Stripe webhook 机制 | tc-research | |
| 14 | 研究一下这个库能不能用 | tc-research | |
| 15 | let's understand the problem space first | tc-research | |
| 16 | 做个 plan | tc-plan | |
| 17 | 写个方案发给大家评审 | tc-plan | 发布/请审由 tc-plan 经 tc-render 做 |
| 18 | write a plan for the DB migration | tc-plan | |
| 19 | 帮我修个 bug:登录接口 500 | tc-plan → tc-build | 任务层先 3 句话 mini-plan 再执行,先 plan 后 code |
| 20 | 方案批了,过一下设计再开工 | tc-design-review | 项目层设计门必走 |
| 21 | design review 走起 | tc-design-review | |
| 22 | 执行,按 plan 来 | tc-build | 前提:plan 已批准(项目层还需 `设计-已审`) |
| 23 | 开始写码 | tc-build | 无已批准 plan → 先转 tc-plan |
| 24 | implement the approved plan | tc-build | |
| 25 | 收尾吧 | tc-review | |
| 26 | 写 case 复盘这个项目 | tc-review | |
| 27 | wrap up, completion criteria are met | tc-review | |
| 28 | 复盘一下这周的任务 | tc-review | 任务批量周桶 case |
| 29 | 卡住了,半小时没进展 | tc-handoff | 交接 + /clear 重启 |
| 30 | 换个 session 重开 | tc-handoff | |
| 31 | I'm stuck, let's start over | tc-handoff | |
| 32 | context 感觉浑浊了 | tc-handoff | |
| 33 | 感觉走偏了,一直在兜圈子 | tc-health | 诊断污染信号;确认污染再转 tc-handoff |
| 34 | you keep agreeing with me, something is off | tc-health | |
| 35 | self check 一下,我们方法对吗 | tc-health | 反模式自检也归 tc-health |
| 36 | 认领角色,DRI 是谁? | tc-plan | 角色分工是 plan 的 How to split 段 |
| 37 | 出分歧了,谁说了算? | tc-conflict | |
| 38 | we disagree on the schema design | tc-conflict | |
| 39 | 周一 kickoff 开始 | tc-rhythm | 周一对齐段 |
| 40 | 本周计划对齐一下 | tc-rhythm | |
| 41 | 周五 demo + betting | tc-rhythm | 周五 demo+betting 段 |
| 42 | 下周做什么,定一下 | tc-rhythm | betting table 决定下周工作 |
| 43 | 开周会 | tc-rhythm | 周一/周五两会同归 tc-rhythm,按今天星期几走对应段,拿不准问 |
| 44 | 月度健康报告跑一下 | tc-ops | |
| 45 | 校验一下 autopilot 配置 | tc-ops | |
| 46 | 把这个 plan 发布到 issue 上 | tc-render | 通常由文档 skill 间接调;单独发布/流转才直触 |
| 47 | 这个 issue 状态不对,帮我理一下 | tc-router | 判定表 + 异常段如实报告,修复交 tc-render |
