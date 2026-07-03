周五下午 45 分钟双会(30 分钟 demo + 15 分钟 betting table)的完整流程:pre-flight、demo 格式、betting 记录工具与降级话术。

# Pre-flight(DRI 会前 1 小时)

1. 查待复盘评审的 cases:
   `multica issue list --label 复盘-待审`
   只按 label 查,不要附加 status 过滤——按状态机语义,待审 case 的 status 是 `in_review`,
   评审通过收尾后才变 `done`;若加 `--status done` 条件会得到空集。
   状态机语义单源见 tc-render skill 的 references/issue-label-state-rules.md。
2. 为每个 case 找出可演示的真产物:已上线的功能、完成的迁移、能跑的原型。
3. 评审通过的 case 当场收尾:
   `python3 <skills-root>/tc-render/scripts/transition.py case-finalize <case-issue>`
   phase case 加 `--keep-parent`;不加时会连带关闭其父 plan。
   子命令语义与 exit codes 见 tc-render skill 的 references/publish-contract.md。

# Demo · 30 分钟(庆祝,不是汇报)

## 0-25 分钟 — 演示
3-5 个 demo,每个约 5 分钟,格式:
- 30 秒:这是什么
- 3 分钟:现场演示真东西在跑(live,不是 slides)
- 1 分钟:我们学到了什么
- 30 秒:鼓掌
绝不允许:PowerPoint、截图、status update。

## 25-30 分钟 — 庆祝
最好有真的吃喝。把这一周标记为完成。

# Betting Table · 15 分钟(决定下周)

用 remote MCP 工具 `betting_table_capture` 记录全过程(候选、票数、结果):
1. 任何人可提名候选,总数 ≤ 5,每个一句话
2. 5 分钟静默思考
3. 每人投票 ≤ 3 个候选
4. 得票最高者成为下周的 plan-candidates(之后按体量走 tc-kickoff 或 tc-plan skill 立项)
5. 所有未得票候选直接丢弃——不进 backlog

降级:tcmcp-remote 未连接 → 明确告诉用户本轮结果没有被记录,把候选/票数/结果整理成文本
交给用户手动留档,绝不谎称已记录。

# 这套协议强制什么
- Demo 是庆祝,不是 reporting
- Betting 取代 backlog grooming(Shape Up 原则)
- "重要的事会再浮上来"——没人投票 = 本周不紧急

# 反模式
- Demo 变成 status update 或 roadmap 演讲
- 把未得票候选挪进 backlog "以后再说"
- 没东西可演示就跳过周五(改成讲 "本周学到了什么"——但不许跳过)
