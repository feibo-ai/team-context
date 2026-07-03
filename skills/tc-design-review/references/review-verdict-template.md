# review-verdict-template

设计评审子 agent 的启动要求与 verdict 输出模板（子 agent 的输出契约）。

## 子 agent 启动要求
- 全新上下文（天然独立）；role = staff engineer。
- 输入只给：设计载体（plan HTML 或 issue 评论 URL）+ 相关 research 材料。
- **不带实现方的对话记忆**；不给转换权限——子 agent 只产出 verdict，不碰 issue 状态。

## Verdict 输出模板
```text
VERDICT: approved | changes-requested

## BLOCKING
- <必须解决才能开工的问题>

## NON-BLOCKING
- <建议改进但不阻塞开工的问题>

## 事实核查清单
- <设计中的关键声称> — <子 agent 实际验证了什么 / 未验证>
```

## 判读规则
- 存在任一 BLOCKING 项 → verdict 必须是 `changes-requested`。
- BLOCKING / NON-BLOCKING 清单覆盖三类关注点：架构取舍、与现有系统的兼容、风险盲区。
- 事实核查清单区分「声称」与「实际验证」——未验证的声称如实标注，不默认为真。
- verdict 交回编排 session 后由其执行转换；子 agent 不运行任何 transition 命令。
