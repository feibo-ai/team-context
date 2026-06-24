# 跨工具桥 · CROSS-TOOL —— 任何工具照着做就能跑团队 SOP 的发文档/流转

这是一页、工具无关、自包含的照做手册。团队多工具混用(Codex / Opencode / Hermes / Claude
等),**非 Claude 工具不会自动加载 `~/.claude/skills/tc-*`**,但发文档/流转的两脚本
(`publish.py` / `transition.py`)是纯 Python、工具无关——任何工具能 `python3` 就能跑。

> **分工**:**Claude 用户走 `tc-*` skill**(tc-3-plan / tc-2-research / tc-5-review / tc-handoff /
> 各转换 skill,它们内部调这两脚本)。**Codex / Opencode / Hermes / 其他工具直读本文件照做**——
> 同一套脚本、同一套契约,只是入口不同。本文件是「指针 + 照做序列」,字段/语义的权威单源仍在
> `PUBLISH.md`、`standards/multica-fields.md`、`transition.py` docstring、`standards/labels.md`,
> 本文件不复制它们(避免多源漂移),只告诉你去哪查、按什么顺序跑。

约定:下文 `<repo>` = team-context 仓库根(本机一般是 `/Users/feibo/feibo/team-context`)。

---

## 0 · 何时要走全流程

判定规则单源 = `<repo>/standards/layer-tiering.md`。一句话:一个 issue 命中**任一**触发器
(① 写/改代码或配置且会合进 main · ② 跨 session/跨人交接 · ③ 对外或影响他人产出 · ④ 预计 > 半天)
即判【项目层】,走全流程(plan HTML 文档 + 评审门 + label 状态机);**都不命中**才落任务层走轻量
(3 句 mini-plan 自批、执行派子 agent)。**拿不准当项目层处理(宁严勿松)。** 全流程要发 plan/
research/case 文档,就走下面 §1;期间流转状态走 §2。

---

## 1 · 发一份 plan / research / case HTML 文档

主路径**只有一条**:写 `fields.json` → 调 `publish.py`(它一条命令搞定渲染 + 硬校验 + 命门B 内联
发布 + 入口状态转换)。**不要**手跑 curl、不要手敲 `multica issue comment add`。

### 步骤

1. **凑字段写成 `fields.json`**。各 type 的字段配方(权威 = `publish.py:SCHEMAS`,人读版在
   `PUBLISH.md §1`「各 type 的 fields.json 字段」)。人字段(dri/exec/reviewer 等)的默认值与
   解析配方见 `<repo>/standards/multica-fields.md`(默认当前用户、运行时解析、绝不询问;`--dri`
   取 `.user_id` 不是 `.id`)。要点:
   - `plan`:`goal`(≥10 字) · `completionCriteria`[](≥1 条) · `slug` · `layer`(project|task) ·
     `dri` · `exec`[] · `collab`[] · `reviewer` · `appetite`;可选 `approach` / `keyDecisions`[] / `risks`[]。
   - `research`:`question` · `slug`;可选 `findings`[](空=骨架占位,非空即视为已交付) /
     `openQuestions` / `verdict`。
   - `case`:`goal` · `whatHappened` · `slug` · `criteriaResults`[] · `keyJudgments`[](≥1 条,
     关键判断段合计 ≥100 字) · 可选 `ruleCandidates`[]。
   - 字段集 `additionalProperties:false`——**多/拼错一个 key 即 exit 1**;纯空格占位也算空 → exit 1。

2. **先 dry-run 预览**(只渲染+校验+落盘,不发布、不依赖 CLI):

   ```bash
   python3 <repo>/skills/tc-render/publish.py --type <plan|research|case> \
     --data fields.json --issue <完整UUID> --out <path>.html --dry-run
   ```

3. **正式发布**(去掉 `--dry-run`):

   ```bash
   python3 <repo>/skills/tc-render/publish.py --type <plan|research|case> \
     --data fields.json --issue <完整UUID> [--caption "标题(方案A · 下方渲染)"] --out <path>.html
   ```

   - `--issue` 必须是**完整 UUID**(8 位短 ID 会 400)。`--out` 须 `.html` 且落在 CWD 允许根内(拒 `../`)。
   - 凭据由 multica CLI 自管(读 `~/.multica/config.json`),**token 绝不进脚本 argv**——你不用碰 token。
   - 需要 **multica CLI v0.4.11+**(`--inline`);旧版先 `multica update`。`--dry-run` 不依赖 CLI。

### 成功判据(对抗验收,别只看 exit 0 的字面)

- 脚本打印 JSON,其中 **`attachment_id` 非空**(自检 attachments 已绑);
- 去对应 multica issue 看评论,**正文出现 `!file[...html](...)` 内联标记并渲染出文档卡片**。
- 满足这两条才算发出去了。只上传成附件、正文没有 `!file[..]` 标记 = 没成功(见 §4 红线)。

### exit code 契约

- `0` = 全成功(渲染+发布+入口转换都成)。
- `1` = 校验/发布失败,**评论未发出**——改 `fields.json` 后可放心重跑。
- `2` = **评论已发但入口状态转换失败**——**绝不重跑 publish**(会重复发评论)。按 stderr 给出的
  `transition.py publish-init ...` 幂等命令单独补转换。

### 再发版 / 更新

换个新 `--out` 文件名(`_v2`/`_v3`…)再调一次脚本,append-only 多发一条评论;**永不改附件、
永不改 issue 描述**。脏评论可 `multica issue comment delete <comment_id>` 删后重发。

---

## 2 · 流转 issue 状态(label + status + 父链)

状态转换**只走 `transition.py` 子命令**——它把每条转换边收口为一个子命令(运行时把 label 名解析为
UUID、幂等预读、后置复核)。**不要手敲 `multica issue label add/status`**(label add 只收 UUID,
按名称的手敲命令跑不通,且漏父链)。语义权威单源 = `transition.py` 顶部 docstring + `standards/labels.md`。

```bash
python3 <repo>/skills/tc-render/transition.py <子命令> <issue完整UUID> [选项] [--dry-run]
```

子命令一览(各一句话语义,细节读 docstring):

| 子命令 | 干什么 |
|---|---|
| `publish-init <issue> --doc-type {plan\|research\|case\|handoff} [--findings-filled]` | 发布后的入口转换(publish.py 内部已调;exit 2 补救时手动跑这条幂等命令)。plan→+计划-草稿 / research→+研究(findings 已填则 status done)/ case→+复盘-待审+in_review / handoff→不动 |
| `plan-request-review <issue>` | 计划请审:+计划-评审中 · status in_review |
| `plan-approve <issue>` | 计划批准:+计划-已批准 · 摘计划未决态 · status todo(待启动) |
| `plan-upgrade <issue>` | 计划升级再发版:+计划-已升级/草稿 · −计划-已批准(再走 request-review) |
| `design-request-review <issue>` | 设计请审(项目层必走、任务层可跳):+设计-待审 · status in_review |
| `design-approve <issue>` | 设计批准:+设计-已审 · −设计-待审 · status todo |
| `build-start <issue>` | 开工:status in_progress(设计-待审 在场会告警「设计评审未完成就开工」) |
| `case-finalize <issue> [--keep-parent]` | 收尾:+复盘-已审 · status done · 连带父 plan/research done(`--keep-parent` 跳过父链,phase case 专用) |
| `cancel <issue>` | 取消:status cancelled · 摘全部流程 label |

- exit:`0` 成功(含幂等空转) · `1` 校验/解析/后置复核失败。`--dry-run` 只做只读调用打印将执行的写命令。
- 典型项目层全链:`publish-init`(发 plan 时自动)→ `plan-request-review` → `plan-approve` →
  `design-request-review` → `design-approve` → `build-start` →(收尾)`case-finalize`。

---

## 3 · multica issue 建在哪(发文档前提)

每个 issue 必须挂在项目下,绝不建孤儿 issue。建 issue 前先 `multica project list` 选定 projectId
(完整 UUID);**拿不准就问用户**(是不是这个项目?要不要新建?)。字段默认值(assignee/dri/lead 等)
全部走 `standards/multica-fields.md` 配方,不询问、不硬编码。`--issue` / `--project` 一律用完整 UUID。

---

## 4 · 红线(任何工具都不许越)

- **别手敲 `multica issue label add` / `multica issue status` 散文命令**——走 `transition.py`。
- **别把文档正文塞进 issue description**——文档一律走评论内联(命门B,publish.py)。description 留空或一句话指针。
- **别绕开 publish.py 硬校验**手拼 curl / 手跑 `comment add --inline`——硬校验(字段 required/minLength/
  类型/anyOf 双形态)是质量闸门,绕过去就是发脏文档。CLI 不可用的灾备契约在
  `publish-contract-v1.yaml`(机读,对照用,**不是**手跑兜底)。
- **`comment add --attachment <本地文件>` 不等于内联渲染**——它只绑附件、不在正文注入 `!file[..]` 标记。
  要正文内联渲染只能用 publish.py。
- **exit 2 绝不重跑 publish**(会重复发评论)——只补跑 `transition.py publish-init`。
- **零 emoji**(文档、UI、代码、注释一律不得出现);**每段 AI 生成的 diff commit 前过人眼**。

---

## 5 · 谁读这份 · 谁走 skill

- **Claude Code 用户**:走 `tc-*` skill(`tc-3-plan` / `tc-2-research` / `tc-5-review` / `tc-handoff` /
  `tc-design-review` 等),它们内部调上面两脚本。**不用读本文件**。
- **Codex / Opencode / Hermes / 其他非 Claude 工具**:直读本文件照做。仓库根的 `AGENTS.md` 是 Codex /
  Opencode 的入口指针,指向这里。
