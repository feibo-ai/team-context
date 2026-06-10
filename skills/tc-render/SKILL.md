---
name: tc-render
description: "Shared 方案A HTML 渲染 + 硬校验 + 内联发布地基,被 RPI 四类文档 skill(tc-3-plan / tc-2-research / tc-5-review / tc-handoff)引用。Use when 生成 plan/research/case/handoff 的方案A HTML 文档并作为 multica issue 评论内联渲染发布,或需要流转 issue 状态(请审/批准/开工/收尾/取消)。核心两脚本:publish.py(渲染+硬校验 exit 1+命门B 收口发布+自检 attachments+入口状态转换;exit 2=评论已发但转换失败)与 transition.py(label+status+父链原子转换七子命令 · name→UUID 运行时解析 · 后置复核 P-7;取代手敲 multica issue label/status)。无需 MCP 服务器。提供 publish.py、transition.py、assets/style.css(1775B CSS 单源)、PUBLISH.md(调用契约 + 命门A 灾备契约)。通常由 4 个 tc-* 文档 skill 调用,不单独触发。"
owner: 曾振华
last_reviewed_at: 2026-06-10
---

# tc-render · 方案A 渲染 + 硬校验 + 内联发布地基

RPI 四类文档(plan / research / case / handoff)的**共享**渲染+校验+发布逻辑单源。
视觉与 team-context-mcp 的 `render/*` 一致(CSS、骨架逐字复刻);本地 MCP 的 zod 约束复刻为**脚本硬校验**。

## 构成
- `publish.py` — **核心**。`--type` + `--data fields.json` + `--issue <UUID>` → 渲染 + 硬校验(违约 exit 1)+ 命门B 收口发布(内部 exec `multica issue comment add --inline`;token 由 CLI 自管不进 argv)+ 自检 attachments 非空 + **入口状态转换**(plan→+计划-草稿 / research→+研究·findings 非空即 done / case→+复盘-待审+in_review;`--no-transition` 跳过;exit 2 = 评论已发但转换失败,按 stderr 幂等补救,**绝不重跑 publish**)。`--dry-run` 只渲染校验不发不转。
- `transition.py` — **状态机原子转换收口**(label+status+父链)。publish-init / plan-request-review / plan-approve / plan-upgrade / build-start / case-finalize[--keep-parent] / cancel 七个子命令;label name→UUID 运行时解析(禁硬编码)、幂等预读、后置复核(P-7)。语义单源 = 本脚本 docstring + standards/labels.md 不变量表。**不再手敲 `multica issue label/status` 散文命令。**
- `assets/style.css` — 1775B CSS **单源**(衡线公文 · 零外链 · 系统字体),脚本内联进每篇。
- `PUBLISH.md` — 调用契约(各 type 的 fields 字段)+ 命门A 灾备契约(CLI 不可用时的 HTTP 参考,**非主路径**;权威见 `publish-contract-v1.yaml`)。

## 用法(消费 skill 这样发布)
1. **凑字段** → 写成 `fields.json`(字段见 PUBLISH.md §1;agent 负责内容)。
2. **调脚本**:`python3 ~/.claude/skills/tc-render/publish.py --type <type> --data fields.json --issue <完整UUID> [--caption ...] [--out 落盘路径]`。
3. 成功打印 `{comment_id, attachment_id, url, doc_path}`;**校验不过 exit 1 改不动就发不出**。`--dry-run` 先预览。

## 硬校验(脚本内建 · 复刻原 zod · 对抗验收非 grep)
- plan:`goal` ≥10 字符 · `completionCriteria` ≥1 条
- case:`keyJudgments` ≥1 · 关键判断段合计 ≥100 字符
- 通用:`--issue` 须**完整 UUID**(8 位短 ID 报 400 · rule #6)
- handoff 的 confirmDiscard 门(discard 前用户显式确认)+ <60s 防重复:属交互/状态,由 tc-handoff skill 把关(脚本只管渲染+发布那篇)。

## 边界
- 发布**不是** `multica issue comment add --attachment`(见 PUBLISH.md Dead ends)。能力收口=命门B `--inline`(v0.4.11+);迭代2 A→B 切换后 publish.py 可改为内部调 `multica ... --inline`。
- 新增/改文档类型:加 `render_<type>` + 校验到 publish.py,改 PUBLISH.md 字段契约。CSS 改只动 `assets/style.css`(单源)。
