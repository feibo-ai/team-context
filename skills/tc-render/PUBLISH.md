# tc-render · PUBLISH — 渲染 + 硬校验 + 方案A 内联发布

**主路径:调 `publish.py`(一条命令搞定渲染+硬校验+发布)。** 不再手跑 prose curl。
脚本把本地 MCP 的 zod 约束复刻成 HARD CHECK(违约 exit 1),无需 MCP 服务器。

---

## 1 · 主路径:调脚本

agent 把文档字段写成 JSON,调脚本;脚本**渲染 + 硬校验 + 命门A 发布 + 自检 attachments**:

```bash
TCR=~/.claude/skills/tc-render          # 或 team-context/skills/tc-render
python3 "$TCR/publish.py" --type {plan|research|case|handoff} \
  --data fields.json --issue <完整UUID> [--caption "标题(方案A · 下方渲染)"] [--out 本地落盘路径] [--dry-run]
```

- 成功 → 打印 JSON `{comment_id, attachment_id, url, doc_path}`(doc_path = git/离线副本)。
- **校验不过 → exit 1 + 明确报错**(改不动就发不出):
  plan goal≥10 / 完成标准≥1;case keyJudgments≥1 / 关键判断段≥100 字符;--issue 须完整 UUID。
- `--dry-run`:只渲染+校验+落盘,不发布(评审/预览用)。
- 配置(server_url/workspace_id/token)自动读 `~/.multica/config.json`。

### 各 type 的 fields.json 字段
- **plan**:`goal`(≥10) · `completionCriteria`[](≥1) · `slug` · `layer`(project|task) · `dri` · `exec`[] · `collab`[] · `reviewer` · `appetite` · `approach`?
- **research**:`question` · `slug` · `findings`?(空=骨架占位) · `openQuestions`?
- **case**:`goal` · `whatHappened` · `slug` · `criteriaResults`[{`criterion`,`met`(bool),`notMetReason`?}] · `keyJudgments`[{`title`,`context`,`options`[],`chose`,`inHindsight`,`ancientImpossible`}](≥1·合计≥100字) · `ruleCandidates`[]?
- **handoff**:`slug` · `lastCommit` · `branch` · `done` · `nextAction` · `deadEnds`[] · `pollutionSignal` · `at`?(默认当前时间)

### 更新(原 plan_upgrade / 再发版)= 再调一次脚本
换新 `--out` 文件名(`_v2`/`_v3`…),append-only 再发一条评论;永不改附件、永不改 issue 描述。

---

## 2 · 内部/兜底:命门A 两步(脚本内部就是这个;无 python 时手跑)

脚本 `publish()` 内部对每条文档做的,就是命门A 两步 raw HTTP:

```bash
CFG=~/.multica/config.json
SERVER=$(jq -r .server_url "$CFG"); WS=$(jq -r .workspace_id "$CFG"); TOK=$(jq -r .token "$CFG")
# 步骤1 upload(必须带 issue_id + X-Workspace-ID)
UP=$(curl -sS --retry 2 -X POST "$SERVER/api/upload-file" \
  -H "Authorization: Bearer $TOK" -H "X-Workspace-ID: $WS" \
  -F "file=@$DOC;type=text/html" -F "issue_id=$ISSUE")
AID=$(printf '%s' "$UP" | jq -r .id); AURL=$(printf '%s' "$UP" | jq -r .url)
# 步骤2 发评论(content 带 !file 相对 url 原样 + attachment_ids;body 用 python json.dumps 严格转义)
BODY=$(python3 -c 'import json,sys;cap,name,url,a=sys.argv[1:5];print(json.dumps({"content":cap+"\n\n!file["+name+"]("+url+")","attachment_ids":[a]}))' "$CAPTION" "$(basename "$DOC")" "$AURL" "$AID")
RESP=$(printf '%s' "$BODY" | curl -sS --retry 2 -X POST "$SERVER/api/issues/$ISSUE/comments" \
  -H "Authorization: Bearer $TOK" -H "X-Workspace-ID: $WS" -H "Content-Type: application/json" --data-binary @-)
# 自检:成功真信号 = 返回评论 attachments 非空(不是 url 形态)
printf '%s' "$RESP" | jq -e '.attachments|length>0' >/dev/null && echo OK || echo "FAIL → 见 §3 撤回"
```

## 3 · 失败/脏评论撤回
```bash
multica issue comment delete <comment_id>     # 实测可删,修正后重发
```

## 硬要求(逐字 · 脚本已内建,手跑时漏一条就脏评论)
1. upload 与 comment 两请求都带 `-H "X-Workspace-ID: $WS"`。
2. upload multipart 带 `-F "issue_id=$ISSUE"`。
3. `!file[name](url)` 用步骤1 返回的**相对 url 原样**,不拼 $SERVER 域名。
4. 成功自检看返回评论 `attachments` **非空**(绑定真信号),不看 url 前缀。

## CLI 版本门槛
命门B `comment add --inline`、`multica skill pull`、`multica skill lint` 需 **multica CLI v0.4.11+**(--inline v0.4.11 · pull v0.4.12 · lint v0.4.13)。旧版(如 v0.4.10 dev-build)无这些命令 → 先 `multica update`。命门A(publish.py raw HTTP)与版本无关,任何版本可用。

## Dead ends —— 不要再试
- `multica issue comment add --attachment <本地文件>` **会**上传并绑定附件(comment.attachments 非空),但**不会**在正文注入 `!file[name](url)` 内联标记 —— 是「附件」形态,**不是命门A 的正文内联渲染**。`--attachment <url>`(url 形)才被直接拒。**要正文内联渲染**:用 publish.py(命门A)或 `comment add --inline`(命门B,v0.4.11+)。
- 实测:此 workspace token 下,带/不带 issue_id upload url 都是 /uploads/workspaces/;失败模式是 attachment_ids 没绑(comment.attachments 空),不是 url 前缀。
- 别再调研 local 改 HTTP transport / doc_publish 纯 CLI 单命令复现内联渲染(均已证不行)。
