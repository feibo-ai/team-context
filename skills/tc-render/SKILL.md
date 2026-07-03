---
name: tc-render
description: "Renders plan/research/case/handoff 文档为受控样式 HTML,经硬校验后作为内联评论发布到 multica issue,并原子流转 issue 的流程 label 与 status(请审/批准/开工/收尾/取消)。Use when the user says '发布文档到 issue' / '流转 issue 状态' / '请审/批准/开工/收尾' or 'publish doc to multica issue' / 'issue status transition'. 通常由 tc-plan / tc-research / tc-review / tc-handoff 调用;仅当只需独立流转 issue 状态时直接使用。Not for 撰写文档内容本身 — use 对应文档 skill;issue 状态乱了要诊断 — use tc-router(本 skill 只执行明确指定的流转)。"
---

# tc-render · 渲染+硬校验+发布+状态流转

## Mandate
RPI 四类文档(plan/research/case/handoff)的共享渲染+校验+发布单源,外加 multica issue 流程 label/status 的原子转换收口。文档内容由调用方 skill 负责。

## Entry gates
- 要发布文档 → 走 publish 脚本(渲染+校验+发布+入口转换)。
- 只需流转 label/status → 走 transition 脚本;绝不手敲 `multica issue label/status`(label add 只收 UUID,手敲跑不通)。
- `--issue` 须完整 UUID,短 ID 会被拒。

## Steps
1. 按 references/publish-contract.md §字段契约凑齐字段,写成 fields.json。
2. `python3 <skills-root>/tc-render/scripts/publish.py --type <type> --data fields.json --issue <UUID> [--caption ...] [--out x.html]`;先加 `--dry-run` 可只渲染校验不发布。
3. exit 0 → 打印 {comment_id, attachment_id, url, doc_path};exit 1 → 校验/发布失败,评论未发出,改字段后重跑;exit 2 → 评论已发但状态转换失败:绝不重跑 publish(会重复发评论),按 stderr 给出的幂等 transition 命令单独补转换。
4. 后续流转(请审/批准/设计评审/开工/收尾/取消):`python3 <skills-root>/tc-render/scripts/transition.py <子命令> <issue>`,子命令清单以 `--help` 为准,语义见 references/issue-label-state-rules.md。

## References
| 文件 | 什么时候读 |
|---|---|
| references/publish-contract.md | 凑 fields.json、exit code 契约、transition 子命令语义、灾备 |
| references/issue-label-state-rules.md | label 全集、状态机、谁写什么、不变量 |
| references/multica-fields.md | 建/改 project 或 issue 时的字段默认值与当前用户解析 |

## Handoffs / Anti-patterns
- handoff 的 confirmDiscard 确认门(discard 前用户显式确认 + <60s 防重复)由 tc-handoff skill 把关。
- 禁:exit 2 后重跑 publish;绕开 publish 脚本手拼 HTTP 发布;改样式不改 assets/style.css 单源;硬编码 label UUID。

> multica 不在 PATH → 提示安装/更新;unknown flag → 先 `multica update`,仍失败则停下问用户;
> 当前用户身份经 `multica auth status` + `multica user list` 运行时解析,绝不硬编码。
