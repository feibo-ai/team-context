---
name: tc-review
description: "Runs the end-of-project/task debrief (复盘): produces the five-section case — goal, what happened, criteria met/not, key judgments, rule candidates — publishes it as an issue comment and routes sub-agent review to closeout. Use when the user says '复盘', '收尾', '写 case', 'debrief', 'wrap up', 'project done', or states completion criteria are met. Every project/task ends here. Not for reviewing code — use code-review; not for planning — use tc-plan."
---

# 复盘/Debrief

## Mandate
产出五段式 case，以 HTML 评论发到 case issue 并送审收口。不是流水账，是关键判断的因果链。

## Entry gates
- 有可对照的 plan（项目层文档/任务层 3 句 mini-plan）和完成判据。
- 找不出关键判断 → 任务层：写进周批 case。

## Steps
1. 选项目：`multica project list --full-id` 取完整 UUID，归被复盘项目，拿不准先问。绝不建孤儿 issue。
2. 建 case issue：`multica issue create --project <UUID> --title "复盘:<slug>" --assignee <当前用户> --parent <plan-issue>`（字段默认值：tc-render skill 的 references/multica-fields.md）。
3. 按 References 表读文件：写五段、核判据、组 fields.json。
4. 先 `--dry-run` 再 `python3 <skills-root>/tc-render/scripts/publish.py --type case --data fields.json --issue <case-issue> --out <归档路径>`。契约：tc-render skill 的 references/publish-contract.md；exit 2=评论已发但流转失败，按 stderr 补救，绝不重跑 publish。
5. 发布后当场派评审子 agent 拿 `VERDICT`（协议：references/debrief-contract.md）。
6. verdict 返回即执行：approved → `python3 <skills-root>/tc-render/scripts/transition.py case-finalize <case-issue>`（父 plan 有其他阶段加 `--keep-parent`），再复核 label/status；changes-requested → 修订重发（append-only）再审。

## References
| 文件 | 何时读 |
|---|---|
| references/debrief-contract.md | 动笔写 case 前 |
| references/case-template.md | 组织 fields.json、定文件名 |
| references/completion-criteria-check.md | 核对完成判据时 |

## Handoffs / Anti-patterns
项目层 → INVOKE tc-rhythm skill 演示（真实产物非 slides）；任务层周批进月度 review。
- ❌ 跳过关键判断段（没判断=任务层）
- ❌ 评审通过后不当场跑 case-finalize（留无主窗口）
- ❌ 手改 label/status/附件/描述（只走脚本 append-only）

> multica 不在 PATH → 提示安装/更新；unknown flag → 先 `multica update`，仍失败则停下问用户；
> 当前用户身份经 `multica auth status` + `multica user list` 运行时解析，绝不硬编码。
