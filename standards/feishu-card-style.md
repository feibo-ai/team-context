# 飞书群消息设计规范(v1 · 2026-06-10)

团队所有发到飞书群的消息(定时 autopilot 卡 + 事件广播)的单一规范。
传输边界:`notify_team({card})` 把对象**原样** `JSON.stringify` 后以 `msg_type: "interactive"`
走官方 SDK(见 team-context-mcp `packages/remote/src/tools/notify_team.ts`),
所以 card 必须是**飞书互动卡片 card 1.0 JSON**;可用元素仅:
header(预设 template 色)/ `div`(`lark_md`/`plain_text`)/ 双列 `fields` / `hr` / `note`。
没有自定义字体与颜色 —— 设计完全靠结构、预设色与排版纪律。

## 1 · 命名(线上对象)

| 对象 | 格式 | 例 |
| --- | --- | --- |
| agent | `助理·<范围名>` | 助理·曾振华 · 助理·全队 |
| autopilot | `<任务名>·<范围名>` | 每日开工·全队 · 周三体检·xieyu |

- **范围名 = multica member 显示名**(单源,`multica workspace member list` 的 `name`;team 固定「全队」)。
  显示名是拼音就用拼音(qiuhaoqi/xieyu)——不维护硬编码映射,避免漂移源。
- 分隔符:间隔号 `·`,无空格。
- kind(文件名/代码标识)保持英文;kind→任务名映射单源在 `scripts/_autopilot-common.sh` 的 `ac_kind_cn()`。

## 2 · 卡片家族与 header 色语义

| 模版 | header template | 触发 | 数据要点 |
| --- | --- | --- | --- |
| 每日开工 | `wathet` | cron 工作日 09:00 | 进行中/待启动/待评审/卡住 |
| 每日总结 | `indigo` | cron 工作日 18:00 | 提交/issue 更新/重启信号/未写复盘 |
| 周一计划 | `green` | cron 周一 09:30 | 本周已批准/跨项目边界 |
| 周三体检 | `orange` | cron 周三 09:00 | claude_md 改动/skill 健康/缺 owner |
| 月度健康 | `carmine` | cron 每月 1 日 10:00 | 复盘/debrief 候选/交接/提交 |
| 项目开工 | `turquoise` | tc-1-start Step 6 | DRI/体量/计划 issue/评审 verdict + 目标/完成标准 |
| 任务开工 | `blue` | tc-4-build 开工 | DRI/体量/计划 issue/分支 + 目标 |
| 意向声明 | (纯文本,无卡) | tc-1-start Step 1 | 见 §5 |

颜色即类型:群里扫一眼 header 色即知消息种类。新增群消息必须从未用的预设色里取
(剩余:yellow / red / violet / purple / grey;red 仅留给真告警类)。

## 3 · 卡片骨架(固定五段 · 缺段省略)

```json
{
  "config": { "wide_screen_mode": true },
  "header": {
    "template": "<§2 的色>",
    "title": { "tag": "plain_text", "content": "任务名 · 范围名 · MM-DD" }
  },
  "elements": [
    { "tag": "div", "fields": [
      { "is_short": true, "text": { "tag": "lark_md", "content": "标签\n**值**" } }
    ]},
    { "tag": "hr" },
    { "tag": "div", "text": { "tag": "lark_md",
      "content": "**「段名」**\n▸ 条目 — 负责人 · 补充\n▸ 条目二" } },
    { "tag": "div", "text": { "tag": "lark_md",
      "content": "⚠ **「卡住」**\n▸ <告警条目>" } },
    { "tag": "note", "elements": [
      { "tag": "plain_text", "content": "助理·范围名 · 数据截至 HH:MM · 仅推送不写库" }
    ]}
  ]
}
```

1. **概览 fields**(双列,`is_short: true`):`标签\n**值**`;概览永远在,0 也显示。
2. **hr** 分隔概览与正文。
3. **内容段 ≤3 个**:段名用 `**「段名」**` 独占一行;条目 `▸ ` 前缀,一条一行,
   语法 `标题 — 负责人 · 补充`;每段 ≤5 条,溢出末行收 `…另有 N 条`。
4. **告警段**(可选):全卡**唯一**允许的 emoji 是此处的 `⚠`。
5. **note 页脚**:`<发送者> · 数据截至 HH:MM · <模式说明>`(run_only 写「仅推送不写库」;
   create_issue 写「已建周计划 issue」之类)。

## 4 · 文案纪律

- **语言**:全中文;英文仅留不可译标识符(issue 号 TEA-93、文件路径、分支名、CLI 命令)。
- **emoji**:全卡至多 1 个(告警段 `⚠`)。禁止彩色圆点(🔵🟡🟣)、装饰 emoji;
  分类语义靠 header 色 + 粗体段名。
- **标题**:`任务名 · 范围名 · MM-DD`(plain_text,零 emoji);事件卡的「任务名」位放事件名
  (项目开工/任务开工),「范围名」位放项目/任务短名。
- **数字**:概览值加粗;不依赖字体颜色表达告警(card 1.0 lark_md 字体色支持不稳),
  告警一律落 ⚠ 段。
- **日期**:MM-DD;时间 HH:MM(24 小时制,Asia/Shanghai)。

## 5 · 意向声明(纯文本模版)

刻意比卡片轻(意向≠承诺,与 Step 6 的卡片形成轻重对比):

```
【意向】<人名>:想做 <X>,因为 <Y>。仅通气、非承诺,有想法直接回。
```

发送:`notify_team({ text: "..." })`。

## 6 · 落地位置(改哪里)

| 内容 | 单源位置 |
| --- | --- |
| 骨架 JSON + 文案纪律(所有 autopilot 共享) | `autopilots/_agent-instructions.md` |
| 各定时卡的 fields/段落定义 | `autopilots/<kind>.yaml` 的 prompt |
| 项目开工卡 + 意向文本 | `skills/tc-1-start/SKILL.md` Step 1 / Step 6 |
| 任务开工卡 | `skills/tc-4-build/SKILL.md` 开工广播段 |
| 命名派生 | `scripts/_autopilot-common.sh` |

改骨架/纪律 → 改 `_agent-instructions.md` 一处,成员重跑 `my-autopilot.sh` 同步;
改单卡内容 → 改对应 YAML。本规范是设计依据,不被运行时读取。
