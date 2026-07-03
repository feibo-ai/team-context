用途：研究产出的交付契约——文件命名、findings 字段要求、建 issue 配方、经 tc-render 的发布流程（append-only 评论制）。

## 文件命名与本地副本

- 本地研究文档：当前工作仓库的 `docs/research/research_<YYYY-MM-DD>_<topic>.html`。
- 每次内容更新 = 换一个新的 `--out` 文件名再渲染发布一次；本地 HTML 留作 git / 离线副本。

## findings / fields.json 要求

- fields.json 完整 schema（骨架最小字段、findings / verdict 语义与首屏展示规则）一律以 tc-render skill 的 references/publish-contract.md 为准，本文件不复制。

## 建研究 issue（multica）

1. `multica project list --full-id` 取**完整 UUID**（8 位短 ID 会报 400）；拿不准问用户，或 `multica project create`。issue 必须挂在项目下，**绝不建孤儿 issue**。
2. `multica issue create --project <UUID> --title "研究:<topic>" --assignee <当前用户>`——当前用户经 `multica auth status` + `multica user list` 运行时解析，不硬编码、不追问。字段默认值见 tc-render skill 的 references/multica-fields.md。

## 发布流程（只走 publish.py）

1. **本地骨架（dry-run，只渲染不发布）**：
   `python3 <skills-root>/tc-render/scripts/publish.py --type research --data fields.json --dry-run --out docs/research/research_<YYYY-MM-DD>_<topic>.html`
2. **填完 findings 后正式发布**：findings 写进 fields.json，去掉 `--dry-run`、加 `--issue <UUID>` 再调一次——脚本渲染并把文档以**内联评论**发到 issue，随后做入口状态转换。研究阶段的意图：发现已交付即闭环，研究 issue 不长期挂账。
3. label / status 的具体流转、exit codes 与失败补救，一律以 tc-render skill 的 references/publish-contract.md 为准；发布报错先读该契约按 stderr 补救，**绝不盲目重跑 publish**。
4. **永不**把文档写进 issue 描述、**永不**改附件——评论 append-only，每次更新发一条新评论。
