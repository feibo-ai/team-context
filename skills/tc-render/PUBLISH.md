# tc-render · PUBLISH — 方案A 内联渲染发布序列(命门A · 逐字写死)

把一个 tc-render 模板产出的方案A HTML 文档,作为 **append-only 评论**发到 multica issue,
在评论下方**内联渲染**(`!file[name](url)` + attachment 绑定)。

来源:本序列 = 本 build session 端到端实测 + team-context-mcp `publishDoc`/`uploadFile`/`commentOnIssue`
(packages/shared/src/multica-client.ts)双重印证。**不是** `multica issue comment add`(见 Dead ends)。

---

## 0 · 配置(全读 ~/.multica/config.json,勿硬编码)

```bash
CFG=~/.multica/config.json
SERVER=$(jq -r .server_url   "$CFG")   # 实测 https://api.teamctx.actionow.ai(非 10.0.5.51)
WS=$(jq -r .workspace_id "$CFG")
TOK=$(jq -r .token       "$CFG")
```

---

## 1 · 从模板产出自包含 HTML(CSS 单源内联)

模板里 `<style>__STYLE__</style>` 的 `__STYLE__` 是占位;assets/style.css(1775B)是 CSS **单源**,
产出时内联进去(零外链,跑在 sandboxed iframe)。步骤:

1. 复制 `templates/<type>.html`,填掉所有 `{{...}}` 占位(内容),按注释处理两处动态注入
   (① 日期:文件名用 `date -u +%F`;② 空列表→`(无)`)。`<style>__STYLE__</style>` 原样保留。
2. 字面替换 `__STYLE__` ← style.css 全文,并删掉模板尾部 `<!-- … -->` 说明注释(MCP 产出不含它):

```bash
TCR="$(cd "$(dirname "$0")" && pwd)"            # tc-render 目录(或写绝对路径)
DOC=docs/plans/plan_$(date -u +%F)_<slug>.html  # 例;research_/case_/handoff 同理
python3 - "$DOC" "$TCR/assets/style.css" <<'PY'
import sys, re, pathlib
doc, css = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]).read_text()
t = doc.read_text()
t = t.replace('__STYLE__', css, 1)                       # 字面替换,CSS 特殊字符安全
t = re.sub(r'\n<!--\s*\n  tc-render .*?-->\s*$', '\n', t, flags=re.S)  # 去模板说明注释
doc.write_text(t)
PY
```

自检:`grep -c '__STYLE__' "$DOC"` 必须为 0;`grep -c ':root{--ink' "$DOC"` 必须为 1。

---

## 2 · 命门A — 两步 raw HTTP(严格按序)

```bash
ISSUE=<目标 issue 完整 UUID>              # projectId/issueId 一律完整 UUID,不用 8 位短 ID
NAME=$(basename "$DOC")
CAPTION="文档(方案A · 下方渲染)"          # 或自定义,如 '计划 v2(方案A · 下方渲染)'

# 步骤1 upload —— 必须带 issue_id;必须带 X-Workspace-ID。--retry 防 transient SSL 抖动。
UP=$(curl -sS --retry 2 -X POST "$SERVER/api/upload-file" \
  -H "Authorization: Bearer $TOK" -H "X-Workspace-ID: $WS" \
  -F "file=@$DOC;type=text/html" \
  -F "issue_id=$ISSUE")
AID=$(printf '%s' "$UP" | jq -r .id)
AURL=$(printf '%s' "$UP" | jq -r .url)   # 相对 url,形如 /uploads/workspaces/<ws>/<id>.html

# 步骤2 发评论 —— content 带 !file(相对 url 原样,不拼域名)+ attachment_ids。
# body 用 python json.dumps 构造:严格转义 \n(content 里 caption 与 !file 间空行),与 MCP JSON.stringify 一致;
# 别用 `jq -n --arg c "$cap"$'\n\n'...`(shell 拼真实换行 → body 含裸换行,靠 server 宽容才不报错,脆弱)。
BODY=$(python3 -c 'import json,sys; cap,name,url,a=sys.argv[1:5]; print(json.dumps({"content":cap+"\n\n!file["+name+"]("+url+")","attachment_ids":[a]}))' \
       "$CAPTION" "$NAME" "$AURL" "$AID")
RESP=$(printf '%s' "$BODY" | curl -sS --retry 2 -X POST "$SERVER/api/issues/$ISSUE/comments" \
  -H "Authorization: Bearer $TOK" -H "X-Workspace-ID: $WS" -H "Content-Type: application/json" \
  --data-binary @-)
CID=$(printf '%s' "$RESP" | jq -r .id)
```

---

## 3 · 自检(成功的真信号 = attachments 非空,**不是** url 形态)

```bash
printf '%s' "$RESP" | jq -e '.attachments | length > 0' >/dev/null \
  && echo "OK 绑定成功 comment=$CID att=$AID" \
  || echo "FAIL attachments 为空 → 无渲染脏评论,见 §4 撤回"
```

`attachments:[]` = 绑定失败 = 产了无渲染脏评论。

---

## 4 · 失败/脏评论撤回(实测可删)

```bash
multica issue comment delete <comment_id>     # 撤回脏评论,修正后重发
```

---

## 硬要求(逐字 · 漏一条就脏评论)

1. upload 与 comment **两个**请求都带 `-H "X-Workspace-ID: $WS"`。
2. upload multipart 带 `-F "issue_id=$ISSUE"`。
3. `!file[name](url)` 的 url 用步骤1 返回的**相对 url 原样**,**不拼 $SERVER 域名**前缀。
4. 成功自检看返回评论的 `attachments` 数组**非空**(绑定真信号),不看 url 前缀。

## Dead ends —— 不要再试(均已证不行)

- **不用** `multica issue comment add --attachment <url>`:CLI(cmd_issue.go)拒 url 形 attachment;
  `attachment_ids` 非用户 flag;且无法把 upload 后才知的 url 注入 content 的 `!file`。
  (能力收口走命门B:tc-multica fork 的 `multica issue comment add --inline <doc.html>`,见迭代尾。)
- 不带 issue_id 的 upload / 把绝对域名拼进 `!file` url —— 都会破坏渲染。
- 实测纠正:此 workspace `mul_` token 下,带/不带 issue_id,upload url **都是** /uploads/workspaces/;
  真正的失败模式是 attachment_ids 没绑(comment.attachments 空),不是 url 前缀变 /uploads/users/。
- 别再调研 local 改 HTTP transport / doc_publish 纯 CLI 单命令复现内联渲染(均已证不行)。
