---
name: tc-render
description: "Shared 方案A HTML 渲染 + 内联发布地基,被 RPI 四类文档 skill(tc-3-plan / tc-2-research / tc-5-review / tc-handoff)引用。Use when 生成 plan/research/case/handoff 的方案A HTML 文档并作为 multica issue 评论内联渲染发布(命门A:upload-file 带 issue_id + raw POST 评论带 !file + attachment_ids)。提供 assets/style.css(1775B CSS 单源)、templates/{plan,research,case,handoff}.html、PUBLISH.md(逐字发布序列)。通常由 4 个 tc-* 文档 skill 调用,不单独触发。"
owner: 曾振华
last_reviewed_at: 2026-06-09
---

# tc-render · 方案A 渲染 + 内联发布地基

RPI 四类文档(plan / research / case / handoff)的**共享**渲染逻辑单源。视觉与
team-context-mcp 的 `render/*` 一致(CSS、骨架、动态注入逐字复刻),发布走命门A(agent raw HTTP)。

## 构成
- `assets/style.css` — 1775B CSS **单源**(衡线公文 · 零外链 · 系统字体)。别复制进模板,产出时内联。
- `templates/plan.html` · `research.html` · `case.html` · `handoff.html` — 四类 HTML 骨架,
  含 `{{占位}}` + 注释标注两处动态注入。
- `PUBLISH.md` — 命门A 发布序列(upload 带 issue_id + raw POST 评论带 !file + attachment_ids),**逐字写死**。

## 用法(消费 skill 按此产出 + 发布)
1. 选 `templates/<type>.html`,填 `{{...}}` 占位(内容)。
2. **两处动态注入**(漏了空字段渲染与 MCP 版有 diff):
   - ① **日期**:文件名用今天日期 `date -u +%F`(如 `docs/plans/plan_2026-06-09_<slug>.html`;
     handoff 时间戳 `date -u +'%F %H:%M'`)。
   - ② **空列表→(无)**:collab / deadEnds / ruleCandidates 等列表为空时渲染字面 `(无)`
     (case 规则候选空 → `_(无)_`;exec 空 → `(未分配)`;reviewer 空 → `(待指派)`)。具体见各模板尾注释。
3. **CSS 内联 + 发布**:照 `PUBLISH.md` —— 把 `__STYLE__` 字面替换为 style.css、去模板说明注释,
   再走命门A 两步(配置读 `~/.multica/config.json`)。成功真信号 = 返回评论 `attachments` 非空。

## 边界
- 发布**不是** `multica issue comment add --attachment`(CLI 拒 url 形;见 PUBLISH.md Dead ends)。能力收口走命门B `--inline`(迭代尾)。
- projectId / issueId 一律**完整 UUID**,不用 8 位短 ID。
- **净损失护栏**(对抗验收,非 grep)由各消费 skill 自带,不在本地基:
  plan goal≥10 / 完成标准≥1;case keyJudgments≥1 / 复盘第4段≥100 字符;
  handoff 的 confirmDiscard 门(discard 前用户显式确认)+ <60s 防重复 handoff 警告;projectId 完整 UUID。
