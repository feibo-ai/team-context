---
name: tc-conflict
description: "Adjudicates genuine team disagreements over a consequential project decision: frame options not people, weigh evidence over preference, the DRI makes the final call, and every outcome is recorded as a dated decision record with evidence and dissent. Use when the user says '冲突' / '分歧' / '意见不合' / '谁说了算' / 'conflict' / 'disagree' / 'deadlock' / 'who decides', or two members are stuck on a real choice. Not for casual taste calls with no consequence."
---

# tc-conflict · 冲突裁决

## Mandate
当团队成员对一个有实际后果的项目决策产生真实分歧时，按四原则裁决，并把结果落成书面决策记录。

## Entry gates
- 两人及以上对同一决策有真实不同意见，且选错有真实代价（不是口味之争）。
- 只是随口偏好、无后果 → 不启动本 skill，任选其一即可。

## Steps
1. 读 references/conflict-principles.md，按四原则依次执行：
   1) 对事不对人 — 重述成「两个选项」；复述不了对方论点就先退回去听懂。
   2) 依据优先于偏好 — 逐项列证据（数据/测试/先例/行业参照）；双方都没证据就明说「这是 judgment call」。
   3) DRI 最终决定权 — 有共识则记录；仍分歧则 DRI 拍板，哪怕 DRI 更资浅、哪怕可能错（照样执行并观察结果）。
   4) 决策必须落档 — 无论结果如何都要写记录。
2. 按 references/decision-record-template.md 写 `YYYY-MM-DD-<topic>.md`，放进 team-context 仓库根目录下的 `decisions` 目录（先定位仓库，勿假设当前 cwd 就在仓库里）。
3. 记录必须含：背景、候选选项、各自证据、DRI 决定、异议人及理由、复审触发条件。没有文件 = 决策没发生。

## References
| 文件 | 什么时候读 |
|---|---|
| references/conflict-principles.md | 开始裁决前，四原则完整判据与反模式 |
| references/decision-record-template.md | 写决策记录时 |

## Handoffs / Anti-patterns
- 分歧根源是「DRI 到底是谁」没定 → 先 INVOKE tc-plan skill 定角色/DRI，再回来裁决。
- ❌ 「投票表决」— DRI 模型是 DRI 拍板，不是多数决
- ❌ 「会上说清楚了就不用写文件」— 不落档等于没决策
- ❌ 异议方事后「我早说过」— 异议已记录在案，不翻旧账
- ❌ 资深成员越过实习生 DRI 改决定却不落档
