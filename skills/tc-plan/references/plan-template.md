用途：plan 文档骨架——项目层完整模板与任务层 3 句 mini-plan 模板。

# Plan 文档模板

输出文件命名：`plan_<YYYY-MM-DD>_<slug>.html`（更新版换新文件名 `_v2`…，append-only）。HTML 由 publish.py 渲染；下面的 markdown 骨架是字段的组织方式，对应 fields.json 的内容。

## 项目层模板

```markdown
# Plan: <topic>

**Created:** YYYY-MM-DD
**DRI:** <name>
**Layer:** project

## Goal
<specific, verifiable>

## Completion criteria
- [ ] Signal 1: ...
- [ ] Signal 2: ...

## How to split
- DRI: <name>
- EXEC: <names>
- COLLAB: <names + scope>
- REVIEW: <second Claude session or person>

## Appetite
<days / week / month>

## Research input
<research HTML 路径（tc-research 的产出）>

## Approach
<3-10 paragraphs explaining the chosen direction>

## Review
- Reviewer: <agent or person>
- Reviewed: <YYYY-MM-DD>
- Verdict: pending / approved / changes-requested

## Current State (handoff slot — see tc-handoff skill)
(empty until first handoff)
```

## 任务层模板（3 句起）

```markdown
# Plan: <short topic>

**Layer:** task
**What:** <1 sentence>
**Done when:** <1 sentence>
**Boundary:** <what is out of scope, 1 sentence>
```
