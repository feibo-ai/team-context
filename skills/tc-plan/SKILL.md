---
name: tc-plan
description: "Generates the RPI Plan-phase doc — goal, completion criteria, how to split (DRI/EXEC/COLLAB/REVIEW role assignment), appetite — and routes it through a mandatory second-session review before coding. Project layer: full plan doc; task layer: 3-sentence mini-plan. Use when the user says '写计划', '做个 plan', '认领角色', '分工', '谁做什么', '责任人/DRI 是谁', 'write a plan', 'role assignment', or when research is done. Not for research itself — use tc-research."
---

# RPI · Plan

## Mandate
产出可评审、可留存的 plan 文档——人与人、session 与 session 之间的契约；并完成角色分工（How to split）。

## Entry gates
- Research 已完成，拿到 research HTML（tc-research 产出；没有就问用户）。本 session 不带 Research 对话记忆——重读该 HTML，不信转述。
- 判层级：project 还是 task（见 references/task-vs-project-plan.md）。

## Steps
1. 重读 research HTML。
2. 写 4 必填字段与分工、起草文档（按下表读前三个 references）。
3. `multica project list --full-id` 取完整 UUID 作 projectId（短 ID 报 400；拿不准问用户；绝不建孤儿 issue）。
4. `multica issue create --project <UUID> --title "计划:<slug>" --assignee "$ME_NAME" [--parent <research-issue-id>]`。
5. 写 fields.json（schema 与 exit code 处置见 tc-render skill 的 references/publish-contract.md），先 `--dry-run` 再：
   `python3 <skills-root>/tc-render/scripts/publish.py --type plan --data fields.json --issue <issue-UUID> --out <plan文档目录>/plan_<YYYY-MM-DD>_<slug>.html`
6. 评审门（写码前必过）：流程见 references/plan-contract.md。
7. 更新：换新 `--out`（`_v2`…）再发，append-only；永不改附件或 issue 描述。

## References
| 文件 | 什么时候读 |
|---|---|
| plan-contract.md | 写字段前；评审门/状态转换 |
| plan-template.md | 起草 plan 文档时 |
| role-assignment.md | 认领角色/分工/定 DRI 时 |
| task-vs-project-plan.md | 判层级；写任务层 mini-plan |

## Handoffs / Anti-patterns
批准后项目层必走 INVOKE tc-design-review skill，再到 tc-build 开工；交接用 INVOKE tc-handoff skill。
- ❌ 写完 plan 直接写码（跳过评审）
- ❌ 缺 4 字段之一（"目标在我脑子里"）
- ❌ 没有 DRI 就开工
- ❌ Research 和 Plan 混在同一 session

> multica 不在 PATH → 提示安装/更新；unknown flag → 先 `multica update`，仍失败则停下问用户；
> 当前用户身份经 `multica auth status` + `multica user list` 运行时解析，绝不硬编码。
