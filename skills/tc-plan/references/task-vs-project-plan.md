用途：判断 plan 属于任务层还是项目层，以及两层在字段、评审、执行方式上的差异。

# 任务层 vs 项目层

## 判层级
- **项目层**：多人/多模块/需要分工与独立评审的工作；appetite 以 days / week / month 计。
- **任务层**：单人可完成的小块工作；appetite 以小时计；默认 DRI 就是你自己。
- 拿不准 → 按项目层处理（宁可多一道评审）。

## 差异对照

| | 项目层 | 任务层 |
|---|---|---|
| 文档 | 完整 plan 文档（骨架见 references/plan-template.md） | 3 句 mini-plan（What / Done when / Boundary） |
| How to split | DRI + EXEC + COLLAB + REVIEW | 就是你（默认 DRI） |
| Appetite | days / week / month（投入上限，非估算） | 小时数 |
| 评审 | 必须第二 session 批准，写进 "## Review" 段 | 可自批，但写码前必须明说 |
| 设计评审 | 必走 | 可跳 |

## 任务层同样要走的流程
- mini-plan 同样经 publish.py 发布、同样适用 `plan-request-review` 转换（见 references/plan-contract.md）。
- **任务层执行默认派执行子 agent**——编排 session 不亲自动手：派单含精确改动说明 → 子 agent 改完报告 → 编排 session 审 diff、跑状态转换、commit。与评审子 agent 同一权力结构：子 agent 产出工作，裁量与状态权始终归编排 session（build 阶段细节见 tc-build skill）。

## 项目层专属
- plan 批准后必须走设计评审（INVOKE tc-design-review skill），通过后才进 build。
- plan 文档的 Current State 段留作 handoff 槽位（见 tc-handoff skill）。
