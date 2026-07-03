Build session 开工前的 pre-flight 核对清单——针对已批准的 plan 逐项确认，任一 No 即停。

# Pre-flight（写第一行代码之前，全部打勾）

- [ ] Plan 文档（HTML）已在本 session 加载并**读过**（不是"上个 session 读过"）
- [ ] Plan 带「已批准 / approved」标记；任务层则为 3 句 mini-plan 且已过目
- [ ] **项目层：work issue 带 `设计-已审`**——设计评审门已过（见 tc-design-review skill）。
      任务层可跳过此项。`设计-待审` 在场 = 评审进行中，**不得开工**，
      `transition.py build-start` 会对此告警。
      label/status 状态机以 tc-render skill 的 references/issue-label-state-rules.md 为准。
- [ ] 不回看文档，能复述本次目标与完成判据
- [ ] 能说清什么在 scope 内、什么在 scope 外

## 任一 No
停下，不写任何代码：INVOKE tc-handoff skill → `/clear` → 回 Plan session。
不要"边写边补齐前提"。
