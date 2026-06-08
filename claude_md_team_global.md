# AI MIQ — team-global CLAUDE.md

跨项目规则，适用于所有团队工作。复制（或软链）到每个产品 repo 的 CLAUDE.md，或者通过 Claude Code 的 `CLAUDE.md` 继承机制叠加在它之上。

## 我们是谁
AI MIQ — 5 人 AI-Native 团队。以 SOP v0.4 参考 Handbook 为准。通才 + AI 杠杆，哑铃模型。

## 语言
**默认用简体中文回复用户。** 即使 skill / 文档正文是英文，也用中文跟用户对话、解释、汇报。代码、命令、标识符、文件名、专有名词保留原文。

## 怎么工作 · 6 条核心规则

1. **Research / Plan / Implement 是分离的 session。** 不要混。session 协议分别用 `tc-2-research`、`tc-3-plan`、`tc-4-build` 三个 skill。
2. **Context pollution → 调 `tc-handoff` skill → /clear。** 不要原地修。
3. **每个项目 / 任务都要以 `cases/YYYY-MM-DD-*.html` 复盘收尾**（方案A HTML · 经 `case_create` 发为 issue 评论），用 `tc-5-review` skill。5 个必填段落。SOP 不可妥协 #2。
4. **写代码前必须有 plan 文档（方案A HTML），并由第二个 session 评审。** 用 `tc-3-plan` skill。SOP 不可妥协 #1。
5. **底线规则：每段 AI 生成的 diff 在 commit 前都要过人眼。** 你来 ship。
6. **每个 multica issue 必须挂在项目下。** 建 issue（plan / research / case）前先 `multica project list` 选定 projectId；**拿不准就问用户**（是不是这个项目？要不要 `multica project create` 新建？）；绝不建无项目的孤儿 issue。`plan_create` / `research_create` / `case_create` 的 `projectId` 已是必填参数。

## 跨项目技术规则
（团队标准成形后填进来。每条规则必须适用于所有未来同类项目；项目特有的规则去 `cases/`，不放这里。）

## Claude 不能再犯的错
（通过 `case_promote_rule` MCP 工具从 case file 提升上来。）

- 本机开发依赖(DB/Redis/端口)用 docker-compose 起时,默认改用非标准避让端口并写进 .env.example/compose 注释,避免与开发机上其他项目的运行服务冲突。(来源:case TEA-40 · actionow-foundation-week1)
- nullable 外键列的 add_column migration 必须显式命名 FK 约束——否则 Alembic autogen 的 downgrade 用 None 名无法 drop,迁移不可逆。(来源:case TEA-62 · actionow-hardening-phase-a)
- 高频表的 add_column + create_index migration 应评估 CONCURRENTLY,避免大表锁写(本期量小未做,沉淀为团队迁移规范)。(来源:case TEA-62 · actionow-hardening-phase-a)
- Tailwind v4 + next/font 接字体走 @theme inline 让 font-sans/font-mono 工具类直接内联 var(--font-xxx);在 :root 覆盖 --font-sans 不被 font-sans 工具类采纳(会静默回退默认栈)。(来源:case TEA-66 · actionow-admin-redesign)
- 前端工程禁止使用任何 emoji(UI 文案、组件、代码、注释一律不得出现)——用图标组件或纯文字替代。(来源:团队前端规范)

## 怎么叫起其他 Claude session

| 需求 | Skill |
| --- | --- |
| 启动新项目 (Phase 01) | `tc-1-start` |
| Research | `tc-2-research` |
| Plan | `tc-3-plan` |
| Implement | `tc-4-build` |
| Debrief | `tc-5-review` |
| 认领角色 | `tc-roles` |
| 冲突 / 分歧 | `tc-conflict` |
| 周一对齐 / 周五 demo+betting | `tc-monday` / `tc-friday` |
| 自检 | `tc-self-check` |
| 污染扫描 | `tc-health-check` |
| /clear 之前 | `tc-handoff` |

## 卡住的时候
- 30 分钟没进展 → 调 `tc-handoff` skill
- 同一个问题 3 次 handoff → 升级到 greenfield playbook (PB1)
- 单周 5 次 handoff → 月度 review 时标 burnout 信号

## 去哪儿找具体 context

| 什么 | 在哪 |
| --- | --- |
| 跨项目 Skills | `~/.claude/skills/`（从 team-context repo 同步） |
| 项目内 plans | `<project>/docs/plans/` |
| 项目内 research | `<project>/docs/research/` |
| 项目 cases (L2) | `<project>/cases/YYYY-MM-DD-*.html` |
| 团队 SOP | team-context repo，`sop/group_sop_v0.4.html` |
| 团队标准 | team-context repo，`standards/` |
| 架构决策 | `<project>/decisions/` + team-context `decisions/` |
| Multica workspace | `team-context`（server URL：跑 `multica config show`） |
| Multica CLI 参考 | `multica --help` 或 `~/.claude/skills/multica-cli/` |
