Case 文档骨架——文件名与归属约定、五段到 fields.json 的字段映射、可直接套用的草稿模板。

# 文件名与归属

- **项目层**：`<YYYY-MM-DD>-<project-slug>.html`，一个项目一份，输出到团队仓库的 case 归档目录（即 publish.py 的 `--out` 参数指向处）。
- **任务层（轻量）**：`<YYYY-MM-WW>-tasks.html`，按周分桶，同一周的任务复盘追加进同一份。

# 五段 → fields.json 字段映射

| 段 | fields.json 字段 |
|---|---|
| 1. Goal | `goal` |
| 2. What actually happened | `whatHappened` |
| 3. Completion criteria | `criteriaResults`（逐条含判据、met 标注、未达成原因） |
| 4. Key judgments | `keyJudgments`（逐条含 judgment 模板的六个要素） |
| 5. General rule candidates | `ruleCandidates` |
| 文件名/标题用 | `slug` |

字段类型、渲染行为与完整 schema 以 tc-render skill 的 references/publish-contract.md 为准，此处只做映射。

# 草稿骨架（先按此写内容，再填入 fields.json）

```markdown
# Case: <project-slug>（<YYYY-MM-DD>）

## 1. Goal
<从 plan HTML 逐字粘贴原始目标>

## 2. What actually happened（≤ 200 词）
<压缩时间线：只写结构上重要的事件>

## 3. Completion criteria — met or not?
- [x] <判据原文> — 信号：<可观测证据>
- [ ] <判据原文> — 未达成：<明确原因（scope 变了 / blocker / 主动砍掉…）>

## 4. Key judgments（2–5 条）
### Judgment: <一行概括>
- **Context:** <当时面对什么选择>
- **Options:** <备选方案>
- **Chose:** <选了什么 / 为什么>
- **In hindsight:** <事后看对吗，会改什么>
- **"Ancient impossible" check:** <没有 AI Native 是否不可能>

## 5. General rule candidates（0–3 条）
- [ ] needs DRI promotion decision — <一句话的一般化规则，不带项目名>
```

各段的写作门槛与反模式见同目录 debrief-contract.md；第 3 段核对方法见同目录 completion-criteria-check.md。
