---
name: tc-5-review
description: "Use when project or task is wrapping up. Triggers: 'let us debrief', '收尾', 'wrap up', '写 case', 'project done', user marks completion criteria met. Generates a case file at cases/YYYY-MM-DD-<slug>.html with the 5 mandatory SOP v0.4 sections. Required for SOP non-negotiable #2 (every project/task ends with debrief)."
---

# Debrief / Case File Template

## Mandate
Document what actually happened, what we learned, what survives forward.
Not a status report. Not "and then we did X, and then Y." A causal chain
of key judgments.

## Filename
- Project: `cases/YYYY-MM-DD-<project-slug>.html`
- Task batch (lightweight): `cases/YYYY-MM-WW-tasks.html` (week-bucketed, append)

## 产出与发布(经 tc-render · 不再走 case_create MCP)

case 是 HTML,作为**评论**内联渲染(append-only),走共享地基 **tc-render**(`~/.claude/skills/tc-render/`):

1. **选定项目** `multica project list --full-id` 取**完整 UUID**(归到被复盘的那个项目;拿不准核对或问用户)。绝不建孤儿 issue(rule #6)。
2. **建/定位 case issue** `multica issue create --project <UUID> --title "复盘:<slug>" [--parent <plan-issue-id>]`(parent 指向被复盘的 plan,便于回溯/自动关闭)。
3. **产出+发布(一步 · 调脚本)** 把字段写成 `fields.json`(`goal` / `whatHappened` / `criteriaResults`[{criterion,met,notMetReason}] / `keyJudgments`[{title,context,options,chose,inHindsight,ancientImpossible}] / `ruleCandidates` / `slug`),调:
   `python3 ~/.claude/skills/tc-render/publish.py --type case --data fields.json --issue <case-issue-UUID> --out cases/<YYYY-MM-DD>-<slug>.html`
   脚本渲染 + 硬校验 + 命门A 发布 + 自检 attachments。先 `--dry-run` 预览。永不改附件/改描述。

> **硬校验(publish.py 内建 · exit 1 硬挡)**:关键判断 ≥1 个、关键判断段合计 **≥100 字符**(非占位;复盘的存在理由就是这段)、`--issue` 完整 UUID。违约脚本报错、发不出。完成标准每条标 met/not + 信号。

## The 5 mandatory sections

### 1. Goal (paste from plan)
Copy the original goal from the plan doc (HTML) verbatim.

### 2. What actually happened (≤ 200 words)
Compressed timeline. Not blow-by-blow. Just the structurally important
events. If it does not change the next person's mental model, cut it.

### 3. Completion criteria — met or not?
For each criterion from the plan:
- [x] / [ ] Criterion + observable signal
- If not met: explicit why (scope changed / blocker / etc.)

### 4. Key judgments (this section is the case file's reason to exist)

Not "what we did" but "what we decided, and why."
For each non-obvious decision:

#### Judgment: <one-line>
- **Context:** what was the choice?
- **Options:** what alternatives?
- **Chose:** what / why
- **In hindsight:** was this right? What would you change?
- **"Ancient impossible" check:** would this judgment have been impossible without AI Native?

Aim for 2-5 judgments. If you cannot find any, you did not have a real
project — it was a task. Move to the weekly task bucket instead.

### 5. General rule candidates
0-3 candidates. Each is a sentence that COULD become a CLAUDE.md rule.
DRI marks each: `[ ] needs DRI promotion decision`.

Promotion rule (SOP P-4): "does this apply to ALL future similar projects?"
- YES → DRI promotes to CLAUDE.md via `case_promote_rule` MCP tool
  (低频 · 写 CLAUDE.md 走月度 review · 本迭代**仍用 MCP 兜底**,迁移见迭代2;非 RPI 闭环工具)
- NO → leave in case file only

About 10% of candidates promote. 90% stay local.

## Anti-patterns
- ❌ Skip section 4 because "nothing notable happened"
  → if truly nothing, this was task-layer, write to weekly bucket
- ❌ Section 2 over 200 words (means you are narrating, not compressing)
- ❌ Section 5 candidates that name the project ("AI hiring uses X")
  → these are case-specific, not general rules
- ❌ Mark all 3 candidates for promotion without examining (most are not)

## 评审收尾状态转换(原 case_review MCP · 改用 CLI 原语)
case 经第二 session 评审通过后(section4≥100 已由 publish.py 硬挡):
```bash
multica issue label add    <case-issue> 复盘-已审
multica issue label remove <case-issue> 复盘-待审
multica issue status       <case-issue> done
PARENT=$(multica issue get <case-issue> --output json | jq -r '.parent_issue_id // empty')
[ -n "$PARENT" ] && multica issue status "$PARENT" done   # 连带关闭被复盘的 plan(§6 DRI auto)
```

## Hand-off
- Project layer: present at Friday Demo. Real artifact, not slides.
- Task layer: weekly case batch reviewed in Monthly Review.
