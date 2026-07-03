用途：Research 入场的能力边界判定，以及并行 subagent 的派发规格与常用研究维度（先例扫描清单）。

## 能力边界首问（必答，先于一切派发）

**"这在 AI 能力边界内吗？"**
- 是 → 继续 Research。
- 否 / 不确定 → 上报 DRI，绝不硬推。
- 理由：超出能力边界使用 AI 会显著推高错误率（BCG 2024 研究：约 19 个百分点的增幅）。宁可停下确认，不可带病推进。

## 并行 subagent 派发规格

同时派发 2-4 个**相互独立**的 subagent。每个 subagent 必须拿到：
- **明确 scope**：只负责一个研究维度
- **输出目标**：研究文档中属于它的一个 section
- **硬约束**：只报发现（findings），不提方案（solution）

subagent 一律写盘交付；orchestrator 只读摘要，不把 subagent 的完整上下文拉进自己的窗口。orchestrator 自身上下文用到 30-40% 即停止 Research——超过后，下游 Plan session 无法完整装下研究产出。

## 常用研究维度（按需取舍，可增删）

- **Existing codebase**：现状有什么、在哪里、怎么组织的
- **Industry / prior art**：别人怎么做的；关键论文、仓库、文档
- **Pitfalls**：已知失败模式、foot-guns、坑
- **Constraints**：团队规范、安全、合规、法务
