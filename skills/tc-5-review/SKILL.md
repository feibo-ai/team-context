---
name: tc-5-review
description: "Use when project or task is wrapping up. Triggers: 'let us debrief', '收尾', 'wrap up', '写 case', 'project done', user marks completion criteria met. Generates a case file at cases/YYYY-MM-DD-<slug>.html with the 5 mandatory SOP v0.4 sections. Required for SOP non-negotiable #2 (every project/task ends with debrief)."
owner: 曾振华
last_reviewed_at: 2026-06-10
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
3. **产出+发布(一步 · 调脚本)** 把字段写成 `fields.json`(`goal` / `whatHappened`(均收 string 或 string[],数组逐项成段) / `criteriaResults`[{criterion,met,notMetReason}](met 全真→结论格「标准全数达成」) / `keyJudgments`[{title,context,options,chose,inHindsight,ancientImpossible}](title 进首屏「要点提示」) / `ruleCandidates` / `slug`),调:
   `python3 ~/.claude/skills/tc-render/publish.py --type case --data fields.json --issue <case-issue-UUID> --out cases/<YYYY-MM-DD>-<slug>.html`
   脚本渲染 + 硬校验 + 命门B 发布 + 自检 attachments + **入口状态转换**(自动 +`复盘-待审` · status `in_review`;exit 2 = 评论已发但转换失败,按 stderr 补救,绝不重跑 publish)。先 `--dry-run` 预览。永不改附件/改描述。

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
- YES → DRI promotes to CLAUDE.md(去本地MCP · 原 case_promote_rule,手动做):
  ① 确认规则文本与 case「规则候选」段某条**匹配**(防晋升错字/臆造);
  ② 追加到 `claude_md_team_global.md` 的「## Claude 不能再犯的错」段末,带来源 `(来源:case <id> · <project>)`;
  ③ 在 case 文件把该候选标为「已晋升」;④ commit。改 CLAUDE.md 走月度 review · **红线文件仅在此处碰**。
- NO → leave in case file only

About 10% of candidates promote. 90% stay local.

## Anti-patterns
- ❌ Skip section 4 because "nothing notable happened"
  → if truly nothing, this was task-layer, write to weekly bucket
- ❌ Section 2 over 200 words (means you are narrating, not compressing)
- ❌ Section 5 candidates that name the project ("AI hiring uses X")
  → these are case-specific, not general rules
- ❌ Mark all 3 candidates for promotion without examining (most are not)

## 评审收尾(子 agent 评审 → 编排 session 当场转换 · 不留无主窗口)

**「第二个 session」= 评审子 agent**:case 发布后,当前(编排)session 立即派评审子
agent(全新上下文,role = DRI 代理/staff engineer),只给 case HTML + plan 文档路径,
要求重点审 section 4(关键判断)并输出 `VERDICT: approved | changes-requested`。

**verdict 返回点 = 收尾执行点**(由拿到 verdict 的编排 session **当场**执行——
旧版「等第二 session 评审通过后(再找人跑)」的无主窗口即 TEA-95/70 漂移根因):
```bash
python3 ~/.claude/skills/tc-render/transition.py case-finalize <case-issue>
# phase case(父 plan 还有其他阶段在进行,如 phase-a 复盘)→ 加 --keep-parent
```
原子做完并复核(P-7):+`复盘-已审` · −`复盘-待审` · status `done` ·
父 plan `done`+清未决流程 label(保留已批准)· 祖父 research 尽力关闭。
changes-requested → 修订 fields 后 `publish.py` 再发一版(append-only),重新派审。

## Hand-off
- Project layer: present at Friday Demo. Real artifact, not slides.
- Task layer: weekly case batch reviewed in Monthly Review.
