---
name: tc-research
description: "Orchestrates the Research phase for a project-layer goal: spawns parallel subagents to map existing code, prior art, pitfalls and constraints, then delivers findings with open questions and candidate approaches — options only, never plans or code. Use when the user says '调研', '研究一下', '开始调研' / 'start research', 'Research session', or kicks off a new feature or unfamiliar problem domain. Not for picking an approach or architecture — use tc-plan."
---

# tc-research · Research Session

## Mandate
Map the territory BEFORE planning. 只产出发现与选项，绝不做规划决策、架构决策或写代码——那是 Plan / Build session 的事。Research 与 Plan 是离散 session，不重叠。

## Entry gates
- 项目层大方向（非任务层小改动）
- 新 feature / 新项目 / 陌生问题域，且未知项尚未摸清
- 必答首问："这在 AI 能力边界内吗？" 是 → 继续；否/不确定 → 上报 DRI，不硬推（判据读 references/capability-frontier.md）

## Steps
1. 并行派发 2-4 个独立 subagent，各领一个研究维度；只报发现、不提方案（维度与派发规格读 references/capability-frontier.md）
2. subagent 写盘，你只读摘要；自己上下文用到 30-40% 即停——再往后，消费你产出的 Plan session 也装不下
3. 按 references/research-template.md 汇总成研究文档
4. 建研究 issue 并把文档发成 issue 评论：读 references/research-contract.md 执行（文件命名、fields.json、publish.py 调用都在里面）

## References
| 文件 | 什么时候读 |
|---|---|
| references/capability-frontier.md | 入场首问判定、派发 subagent 前 |
| references/research-template.md | 起草研究文档时 |
| references/research-contract.md | 建 issue、渲染与发布时 |

## Handoffs / Anti-patterns
- 完成后 INVOKE tc-handoff skill → `/clear` → 开 Plan session（tc-plan），以研究文档为主输入
- ❌ 选方案 / 定架构（Plan 的事）；❌ 写代码（Build 的事）
- ❌ 上下文超 40% 还继续——换更锐利的问题重开
- ❌ 把文档塞进 issue 描述或改附件——发布只走 publish.py 发评论

> multica 不在 PATH → 提示安装/更新；unknown flag → 先 `multica update`，仍失败则停下问用户；
> 当前用户身份经 `multica auth status` + `multica user list` 运行时解析，绝不硬编码。
