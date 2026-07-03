用途:tc-kickoff 六步的执行细节 —— 每步命令、意向文本模版、新建 project 字段确认协议、Step 6 开工卡骨架与文案纪律、每步真验证清单。

# Kickoff 六步执行细节

总原则:kickoff 是**手动编排**,不是单一工具 —— 6 步 = `multica project/issue create` + tc-render 脚本 + `notify_team` 逐步编排,每步产物都要真验证(见文末)。

所有飞书副作用只走 remote MCP 工具(`notify_team`)。降级话术:tcmcp-remote 未连接 → 明确告诉用户没有发送,并给出手动文案,绝不谎称已广播。

## Step 1 — 5 分钟意向声明(纯文本,非卡片)

发到团队飞书群,**纯文本**模版(刻意比卡片轻:意向 ≠ 承诺,与 Step 6 的卡片形成轻重对比):

```
notify_team({ text: "【意向】<人名>:想做 <X>,因为 <Y>。仅通气、非承诺,有想法直接回。" })
```

Goal: let the team know, NOT commit. No formal plan yet.

## Step 2 — Research session(fresh session)

- INVOKE tc-research skill。Output: `research_<date>_<topic>.html`(产出位置以 tc-research skill 为准)。
- 建 research issue:
  ```bash
  multica issue create --project <UUID> --title "研究:<topic>" --assignee "$ME_NAME"
  ```
  (当前用户运行时解析,不问;字段默认值单源见 tc-render skill 的 references/multica-fields.md。)
- 本地骨架 + 填充后发布:
  ```bash
  python3 <skills-root>/tc-render/scripts/publish.py --type research
  ```
  发布必须内联渲染评论(返回 `attachments` 非空)+ 自动打 `研究` label;findings 非空即 status `done`,research issue 不挂账。
- **Never update an attachment / rewrite the description**(更新 = append-only 新评论)。
- Critical: 与 Step 3 **分开**的 session。

## Step 3 — Plan session(又一个 fresh session)

- INVOKE tc-plan skill,读研究产出作为输入。Output: `plan_<date>_<topic>.html`,含全部 4 个必填字段。
- 建 plan issue:
  ```bash
  multica issue create --project <UUID> --parent <research-issue> --assignee "$ME_NAME"
  ```
- 产出 + 发布(含后续更新 = append-only 新评论):
  ```bash
  python3 <skills-root>/tc-render/scripts/publish.py --type plan
  ```
  (硬校验 goal≥10 / criteria≥1。)

### 每个 issue 必须挂项目(绝不建孤儿 issue)
- 先 `multica project list --full-id` 选定**完整 UUID** projectId(必填);拿不准问用户(对不对?要不要 `multica project create` 新建?)。
- 建 issue 一律带 `--assignee "$ME_NAME"`(不问);当前用户经 `multica auth status` + `multica user list` 运行时解析,绝不硬编码。

### 新建 project = 重要字段显式确认协议(勿静默留空)
解析本人 `$ME_UID` / `$ME_NAME` 后,逐字段确认 DRI/开始/截止/优先级,再执行创建;默认值单源见 tc-render skill 的 references/multica-fields.md project 表(含项目层显式确认例外)。

```bash
multica project create --title "<意图>" --dri "$ME_UID" --lead "$ME_NAME" \
  --start-date <YYYY-MM-DD> --due-date <YYYY-MM-DD> --priority <urgent|high|medium|low|none>
```

已建但缺字段的 project 用 `multica project update <id> --start-date … --due-date … --priority …` 补齐。

## Step 4 — 独立评审(= 评审子 agent)

1. 先做请审转换:
   ```bash
   python3 <skills-root>/tc-render/scripts/transition.py plan-request-review <plan-issue>
   ```
   (+`计划-评审中` label · status `in_review`。label/status 语义单源见 tc-render skill 的 references/issue-label-state-rules.md。)
2. 再派评审**子 agent**(role = staff engineer,全新上下文 = 天然独立 session):只给 plan HTML + research 输入,要求输出 `VERDICT: approved | changes-requested`。Wait for verdict。

## Step 5 — DRI 拍板(verdict 返回点 = 转换执行点,本 session 当场执行)

DRI reads review verdict. Final call: proceed / revise / kill。这是不可协商的门:**计划未批准,不进入实现**。

- **proceed** →
  ```bash
  python3 <skills-root>/tc-render/scripts/transition.py plan-approve <plan-issue>
  ```
  (+`已批准` · −`草稿`/`评审中`/`已升级` · status **todo** 待启动;开工时才 in_progress,见 tc-build skill。)
- **revise** → 修订后用 publish.py 再发一版(append-only),回 Step 4 重审。
- **kill** →
  ```bash
  python3 <skills-root>/tc-render/scripts/transition.py cancel <plan-issue>
  ```
  (status cancelled + 清全部流程 label,不留漂移尸体。)

## Step 6 — 开工广播卡

发「项目开工」卡到团队飞书群:`notify_team({ card: ... })`;发出后进入 **24 小时默许窗口**(默认通过,有异议群里提)。

### 传输约束
`notify_team({card})` 把对象**原样** JSON.stringify 后以 `msg_type: "interactive"` 发送,所以 card 必须是**飞书互动卡片 card 1.0 JSON**;可用元素仅:header(预设 template 色)/ `div`(`lark_md`/`plain_text`)/ 双列 `fields` / `hr` / `note`。没有自定义字体与颜色 —— 设计完全靠结构、预设色与排版纪律。

### 项目开工卡内容(header = `turquoise`,颜色即类型)
- **标题**:`项目开工 · <项目短名> · MM-DD`(plain_text,零 emoji;「任务名」位放事件名,「范围名」位放项目短名)
- **概览 fields**(双列 `is_short: true`,格式 `标签\n**值**`,值加粗;概览永远在):DRI / 体量 / 计划(<plan-issue key,如 TEA-xx> + 已批准) / 评审(独立 session 通过)
- **内容段**:「目标」一句话;「完成标准」`▸ ` 前缀一条一行,只放前 2 条,其余收 `…其余 N 条见计划 issue`(段名 `**「段名」**` 独占一行;每段 ≤5 条)
- **note 页脚**:`24 小时默许窗口 · 有异议群里提 · 计划全文见 <plan-issue key>`

### 卡片骨架(固定五段 · 缺段省略)
```json
{
  "config": { "wide_screen_mode": true },
  "header": {
    "template": "turquoise",
    "title": { "tag": "plain_text", "content": "项目开工 · <项目短名> · MM-DD" }
  },
  "elements": [
    { "tag": "div", "fields": [
      { "is_short": true, "text": { "tag": "lark_md", "content": "DRI\n**<人名>**" } },
      { "is_short": true, "text": { "tag": "lark_md", "content": "体量\n**<appetite>**" } },
      { "is_short": true, "text": { "tag": "lark_md", "content": "计划\n**<plan-issue key> · 已批准**" } },
      { "is_short": true, "text": { "tag": "lark_md", "content": "评审\n**独立 session 通过**" } }
    ]},
    { "tag": "hr" },
    { "tag": "div", "text": { "tag": "lark_md",
      "content": "**「目标」**\n<一句话>" } },
    { "tag": "div", "text": { "tag": "lark_md",
      "content": "**「完成标准」**\n▸ <条 1>\n▸ <条 2>\n…其余 N 条见计划 issue" } },
    { "tag": "note", "elements": [
      { "tag": "plain_text", "content": "24 小时默许窗口 · 有异议群里提 · 计划全文见 <plan-issue key>" }
    ]}
  ]
}
```

### 文案纪律
- **语言**:全中文;英文仅留不可译标识符(issue key、文件路径、分支名、CLI 命令)。
- **emoji**:全卡至多 1 个(仅告警段允许 `⚠`;开工卡通常一个不用)。禁止彩色圆点与装饰 emoji;分类语义靠 header 色 + 粗体段名。
- **数字**:概览值加粗;不依赖字体颜色表达告警(card 1.0 lark_md 字体色支持不稳)。
- **日期**:MM-DD;时间 HH:MM(24 小时制,Asia/Shanghai)。

## 每步真验证(全流程贯穿)

- research/plan 骨架是**空的** —— 真调研 / 真规划仍要各开 fresh session 跑 tc-research(Step 2)/ tc-plan(Step 3)深度填充。
- Step 1 / Step 6 广播要**手动**发(`notify_team` 走 remote MCP)。
- **CLI 返回 success ≠ 做对了。** 逐项查:issue 真挂到 project?research/plan issue 真在?评论真内联渲染(返回 `attachments` 非空)?飞书真收到 Step 1 / Step 6 广播?这些环节都可能静默失败(返回成功但产物没到位),必须逐项目验。
