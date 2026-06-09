# tc-render · PUBLISH — 渲染 + 硬校验 + 方案A 内联发布

**主路径:调 `publish.py`(一条命令搞定渲染+硬校验+发布)。** 不再手跑 prose curl。
脚本把本地 MCP 的 zod 约束复刻成 HARD CHECK(违约 exit 1),无需 MCP 服务器。
发布走**命门B**(`multica issue comment add --inline`)收口为**唯一路径**,脚本内部
exec CLI;**token 由 CLI 自管(读 `~/.multica/config.json`),绝不进脚本 argv**(`ps` 不可见)。

---

## 1 · 主路径:调脚本

agent 把文档字段写成 JSON,调脚本;脚本**渲染 + 硬校验 + 命门B 收口发布 + 自检 attachments**:

```bash
TCR=~/.claude/skills/tc-render          # 或 team-context/skills/tc-render
python3 "$TCR/publish.py" --type {plan|research|case|handoff} \
  --data fields.json --issue <完整UUID> [--caption "标题(方案A · 下方渲染)"] [--out 本地落盘路径] [--dry-run]
```

- 成功 → 打印 JSON `{comment_id, attachment_id, url, doc_path}`(doc_path = git/离线副本)。
- **校验不过 → exit 1 + 明确报错**(改不动就发不出)。阈值**派生自 `publish.py:SCHEMAS`**(单一事实源 · 无散落魔数):
  `additionalProperties:false` + `required` + `minLength`/`minItems`;计数前折叠空白 + 类型断言;拼错 key / 类型不符 / 纯空格占位 → exit 1。
- `--out` 须 `.html` 且落在 CWD 允许根内(路径白名单 · 拒 `../` 与绝对逃逸)。
- `--dry-run`:只渲染+校验+落盘,不发布(评审/预览用 · 不依赖 CLI)。
- 发布凭据:命门B 由 multica CLI 自动读 `~/.multica/config.json`(脚本不碰 token)。

### 各 type 的 fields.json 字段(权威 = `publish.py:SCHEMAS`)
- **plan**:`goal`(≥10) · `completionCriteria`[](≥1) · `slug` · `layer`(project|task) · `dri` · `exec`[] · `collab`[] · `reviewer` · `appetite` · `approach`?
- **research**:`question` · `slug` · `findings`?(空=骨架占位) · `openQuestions`?
- **case**:`goal` · `whatHappened` · `slug` · `criteriaResults`[{`criterion`,`met`(bool),`notMetReason`?}] · `keyJudgments`[{`title`,`context`,`options`[],`chose`,`inHindsight`,`ancientImpossible`}](≥1 · section4 折叠空白后 ≥100 字) · `ruleCandidates`[]?
- **handoff**:`slug` · `lastCommit` · `branch` · `done` · `nextAction` · `deadEnds`[] · `pollutionSignal` · `at`?(默认当前时间)

字段集 `additionalProperties:false` —— 多/拼错一个 key 即 exit 1(防静默吞)。

### 更新(原 plan_upgrade / 再发版)= 再调一次脚本
换新 `--out` 文件名(`_v2`/`_v3`…),append-only 再发一条评论;永不改附件、永不改 issue 描述。

---

## 2 · 命门A 灾备契约(不是手跑兜底路径)

命门B(CLI)不可用时,HTTP 级该怎么调的**逐字契约**固化在
[`publish-contract-v1.yaml`](./publish-contract-v1.yaml)(机器可读 + CI 探针守护)。
其 `inline_marker.url_pattern` 对齐前端权威 `file-cards.ts:FILE_CARD_URL_PATTERN`,
`tests/test_contract_probe.py` 在两仓并置(或设 `FILE_CARDS_TS`)时断言无漂移。

> 旧版 §2 的散文 raw-HTTP runbook 已删除 —— 它是「可被手跑、绕开 publish.py 硬校验」的旁路。
> 灾备时读 yaml 契约对照,**不要**绕开脚本手拼 curl。

## 3 · 失败/脏评论撤回
```bash
multica issue comment delete <comment_id>     # 实测可删,修正后重发
```

## CLI 版本门槛(命门B 收口后 · 脚本硬依赖 CLI)
`publish.py` 经命门B 发布,需 **multica CLI v0.4.11+**(`--inline` v0.4.11 · `skill pull` v0.4.12 · `skill lint` v0.4.13)。
旧版(如 v0.4.10 dev-build)无 `--inline` → 先 `multica update`。`--dry-run`(只渲染校验落盘)不依赖 CLI。

## Dead ends —— 不要再试
- `multica issue comment add --attachment <本地文件>` **会**上传绑定附件,但**不会**在正文注入 `!file[name](url)` 内联标记 —— 是「附件」形态,不是正文内联渲染。**要正文内联渲染**:用 publish.py(命门B 收口)或直接 `comment add --inline`。
- 实测:此 workspace token 下,带/不带 issue_id upload url 都是 /uploads/workspaces/;失败模式是 attachment_ids 没绑(comment.attachments 空),不是 url 前缀。
- 别再调研 local 改 HTTP transport / doc_publish 纯 CLI 单命令复现内联渲染(均已证不行)。
