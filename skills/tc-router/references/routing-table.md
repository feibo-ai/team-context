# routing-table.md — 情境 → 目标 skill 映射表(tc-router 判定阶段后按此表交棒)

原则:话语明确匹配某专家 skill → 那个 skill 直接触发,不经 router;router 只处理阶段模糊的入口。
INVOKE 目标 skill 时同时向用户说明判定理由(阶段 + 证据)。

| 情境 | 目标 skill | 触发话语示例 |
|---|---|---|
| 全新项目层大方向启动(3 天以上、有 DRI、值得复盘) | tc-kickoff | 「我想做一个新项目」「启动新项目」"kickoff" "new project" "phase 01" |
| 调研 / 摸底 / 理解不熟悉的问题域(写 plan 之前) | tc-research | 「调研一下 X」「研究一下」"start research" "let us understand" |
| 写方案 / 计划(项目层全量 plan 或任务层 3 句话 mini-plan) | tc-plan | 「做个 plan」「写个方案」"write a plan" "let us plan" |
| plan 已批准、开工之前的设计评审门(项目层必走,任务层可跳) | tc-design-review | 「设计评审」「方案过一下再开工」"design review" |
| 按已批准 plan 写码执行(Implement session) | tc-build | 「执行」「开始写码」"implement" "start coding" |
| 项目 / 任务收尾复盘,写 case 并发布 | tc-review | 「收尾」「写 case」"wrap up" "let us debrief" "project done" |
| /clear 之前的交接;卡住 30 分钟没进展;context 需要重启 | tc-handoff | 「卡住了」「重开」「换个 session」「浑浊了」"I am stuck" "start over" "restart" |
| 怀疑 session 跑偏 / 兜圈子 / 模型顺从过头(污染扫描),或对照团队反模式清单自检(工作中途 / 月度 review) | tc-health | 「走偏了」「感觉不对」「怎么回事」"going in circles"「self check」「反 pattern」"am I doing this right" |
| 项目启动时分角色、定 DRI/EXEC/COLLAB/REVIEW(plan 的 How to split 段) | tc-plan | 「认领角色」「谁做什么」「DRI 是谁」"role assignment" |
| 成员对项目决策有真实分歧,需要仲裁 | tc-conflict | 「出分歧了」「冲突」「谁说了算」「意见不合」"we disagree" |
| 周一 09:30 的 30 分钟对齐会;周五下午 demo + betting table 双会 | tc-rhythm | 「周一 kickoff」「本周计划对齐」「周五 demo」「betting table」「下周做什么」「周会」"Monday kickoff" "Friday demo" |
| 月度健康报告 / autopilot YAML 校验等运维脚本 | tc-ops | 「月度健康」「autopilot lint」"monthly health" "health report" |
| 渲染发布 plan/research/case/handoff 文档;流转 issue label/status(基础设施,通常由文档类 skill 间接调用,极少单独触发) | tc-render | 「把这个 plan 发到 issue 上」「流转一下状态」 |
| 阶段不明 / 只有 issue id / 「继续」「接手」类模糊请求 | tc-router(本 skill) | 「接手 TEA-88」「继续昨天的任务」"pick up where we left off" |

## 边界判定提示
- 「周会」→ tc-rhythm(周一对齐与周五 demo/betting 都归它,按今天星期几走对应段,拿不准问用户)。
- 「修个 bug」而无已批准 plan → 先 tc-plan 任务层 mini-plan,再 tc-build(先 plan 后 code 是团队非妥协规则)。
- 「卡住了」优先 tc-handoff(交接重启);若用户只是怀疑跑偏、还想原地继续 → tc-health 先诊断。
- 「收尾」但 issue 上已有 `复盘-待审` → 是 case 评审收尾,仍归 tc-review 流程处理。
