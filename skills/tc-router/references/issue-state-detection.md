# issue-state-detection.md — 从 multica issue 判定当前阶段(labels + status + 文档评论三路证据)

权威状态机与不变量单源 = 见 tc-render skill 的 references/issue-label-state-rules.md;
本文件只做**只读判定**(阶段 → 路由),任何转换动作交给目标 skill 经 tc-render 执行。

## 读取步骤
1. `multica issue show <id>` → labels、status、标题前缀(计划:/研究:/复盘:)。
2. 读评论区:已发布文档 = 内联 HTML 评论(plan / research / case / handoff),文档在场与否是 label 之外的第二路证据。
3. 列表查询一律 **label 驱动**,勿用裸 `--status` 过滤(in_review 有多种语义,按上述单源文件区分);
   `multica issue list` 默认一页 50 条,必须 `--limit/--offset` 循环拉到 `has_more=false`,否则漏 issue。

## 判定表(label 即真值)
| 观察到的 labels / status | 阶段判定 | 路由 |
|---|---|---|
| 无任何流程 label、评论区无文档 | 未启动:research/plan 都没做 | 项目层新方向→tc-kickoff;明确先摸底→tc-research;小任务→tc-plan(任务层 mini-plan) |
| `研究` | research 已发布(findings 非空即 status done,不挂账) | 下一步写方案→tc-plan |
| `计划-草稿` | plan 已发布、未请审 | tc-plan 走请审(转换经 tc-render) |
| `计划-评审中`(status in_review) | plan 评审中,等评审子 agent verdict | 编排评审收 verdict;approved 后当场批准(经 tc-render) |
| `计划-已批准`(status todo) | 已批准 · **待启动**(开工另有动作) | 项目层→tc-design-review(设计门必走);任务层可跳,直接 tc-build |
| `计划-已升级` | plan 中途升级,需重新评审 | tc-plan 重走请审 |
| `设计-待审`(status in_review) | 设计评审中 — **不得开工**(评审中开工会被告警) | 等 verdict;通过后 tc-build |
| `设计-已审` | 设计评审通过,可开工(与 `计划-已批准` 共存是合法历史事实) | tc-build |
| status `in_progress`(label 不变) | build 进行中 | 继续执行→tc-build;卡住 30 分钟→tc-handoff |
| `复盘-待审`(status in_review) | case 已发布、待评审 | tc-review 的评审段;通过后收尾转换(经 tc-render,可连带关父链) |
| `复盘-已审`(status done) | 已收尾关闭 | 无可路由;新工作另起 issue |
| status `cancelled` 且零流程 label | 已取消 | 与用户确认后另起新工作 |

## 非流程 label(判「未启动」之前先查)
`投注表` / `代码评审` / `倦怠预警` / `古法不可能` 是非流程 label(语义见 tc-render skill 的 references/issue-label-state-rules.md):issue 只带这类 label ≠ 未启动,勿套判定表首行 — 如 `投注表` issue 属周五 betting 流程(tc-rhythm),`代码评审` issue 是 code review 请求。

## label 语义与异常(单源指针,不复制)
- in_review 的多语义、label 互斥/共存不变量、staleness/入口盲区/研究未关等告警判据:一律按 tc-render skill 的 references/issue-label-state-rules.md 解释 label,本文件不复制其内容。
- 判定中发现 label 违规或命中警告档(如评审态挂太久)→ 列出证据如实报告,建议重新派评审、走 tc-handoff 或由目标 skill 经 tc-render 补转换;router 绝不自己动手修。
- issue 数据无 layer 字段:项目层/任务层无法从数据判定,拿不准就问用户(是否独立大方向、3 天以上、有 DRI、值得复盘)。

## 项目归属检查
每个 issue 必须挂在项目下。发现孤儿 issue → 提示用户归属到哪个 project(`multica project list` 给候选);路由前先解决归属,绝不在孤儿 issue 上继续叠工作。
