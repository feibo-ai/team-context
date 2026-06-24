# AGENTS.md — AI MIQ team-context

供 **Codex** 与 **Opencode** 读取的项目级入口(两者都以仓库根 `AGENTS.md` 为首选指令源;
Opencode 在无 `AGENTS.md` 时回退 `CLAUDE.md`,有本文件即以本文件为准)。
**Claude Code 用户不读这里**——走 `tc-*` skill。本文件只放指针,不内联整套步骤(避免多源漂移)。

## 语言
**默认用简体中文回复用户。** 即使脚本/文档正文是英文,也用中文跟用户对话、解释、汇报。
代码、命令、标识符、文件名、专有名词保留原文。

## 发文档 / 流转状态 → 读 CROSS-TOOL
团队 SOP 的发文档(plan / research / case HTML 内联发为 multica issue 评论)与状态流转
(label + status + 父链),**一律照 `skills/tc-render/CROSS-TOOL.md` 跑**。那是一页、工具无关、
自包含的照做手册:写 `fields.json` → `python3 skills/tc-render/publish.py ...`(先 `--dry-run`);
状态流转走 `python3 skills/tc-render/transition.py <子命令> ...`。字段/语义权威单源在
`PUBLISH.md`、`standards/multica-fields.md`、`transition.py` docstring、`standards/labels.md`。

## 项目层任务:先产 plan HTML 文档
判定一个 issue 走【项目层】全流程还是【任务层】轻量,规则单源 = `standards/layer-tiering.md`
(命中任一触发器即项目层:写/改代码且合 main · 跨 session/跨人 · 对外/影响他人 · > 半天;拿不准当
项目层)。**项目层在写码前必须先有 plan HTML 文档,并经第二个 session/独立上下文评审**——按 CROSS-TOOL §1
发 plan、§2 走 `plan-request-review` → `plan-approve` 等转换边。任务层 3 句 mini-plan 自批即可。

## 关键红线
- **零 emoji**:文档、UI、代码、注释一律不得出现。
- **每段 AI 生成的 diff,commit 前必须过人眼。**
- 状态流转**只走 `transition.py`**,别手敲 `multica issue label add` / `status`。
- 文档**只走 publish.py 内联发布**,别塞进 issue description、别绕开硬校验手拼 curl。
- 每个 issue 必须挂在项目下(完整 UUID),绝不建孤儿 issue;拿不准问用户。

## 去哪查
- 跨工具照做手册:`skills/tc-render/CROSS-TOOL.md`
- 发布契约 / 字段:`skills/tc-render/PUBLISH.md` · `standards/multica-fields.md`
- 状态机 / label 字典:`transition.py` docstring · `standards/labels.md`
- 分层判定:`standards/layer-tiering.md`
- 团队全局规则(权威):`claude_md_team_global.md`

---
**Opencode 同样适用本文件。** 依据:Opencode 项目级指令首选 `AGENTS.md`(与 Codex 同),
其次回退 `CLAUDE.md`;故仓库根这一份 `AGENTS.md` 即 Codex 与 Opencode 的共同入口,无需另建
Opencode 专属入口文件。
