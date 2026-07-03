# publish-contract — tc-render 发布契约单源:publish 脚本调用契约(exit code、fields.json 字段)、transition 子命令语义、HTTP 灾备契约。

**主路径:调 `scripts/publish.py`(一条命令搞定渲染+硬校验+发布+入口状态转换),禁止手拼 curl / 手打 HTTP。**
脚本把本地 MCP 时代的 zod 约束复刻成 HARD CHECK(违约 exit 1),无需 MCP 服务器。
发布收口为**唯一路径**:脚本内部 exec `multica issue comment add --inline`;
**token 由 multica CLI 自管(读 `~/.multica/config.json`),绝不进脚本 argv**(`ps` 不可见)。

---

## 1 · 主路径:调 publish 脚本

agent 把文档字段写成 JSON,调脚本;脚本**渲染 + 硬校验 + 内联发布 + 自检 attachments 非空 + 入口状态转换**:

```bash
TCR=<skills-root>/tc-render        # skills-root 定义见团队全局规则
python3 "$TCR/scripts/publish.py" --type {plan|research|case|handoff} \
  --data fields.json --issue <完整UUID> [--caption "标题(下方渲染)"] [--out 本地落盘路径.html] [--dry-run] [--no-transition]
```

- 成功 → stdout 打印 JSON `{comment_id, attachment_id, url, doc_path, transition}`(doc_path = git/离线副本)。
- **入口状态转换**(发布即流转,由 `scripts/transition.py` 承担):
  plan→+`计划-草稿`(仅当无 计划-* label,重发 v2 不重打) / research→+`研究`(findings 非空即 status done) /
  case→+`复盘-待审`+status in_review(仅当无 复盘-已审) / handoff→不动。`--no-transition` 逃生口。
- **exit code 契约:0 全成功 · 1 校验/发布失败(评论未发出,可改后重跑) · 2 评论已发但转换失败**
  ——exit 2 时**绝不重跑 publish**(会重复发评论),按 stderr 给出的 `transition.py publish-init` 幂等命令单独补转换。
- 后续流转(请审/批准/设计评审/开工/收尾/取消)全部走 transition 子命令(见 §4);
  **手敲 `multica issue label/status` 跑不通**——`label add` 只收 UUID,不收名称。
- **校验不过 → exit 1 + 明确报错**(改不动就发不出)。阈值**派生自 `publish.py:SCHEMAS`**(单一事实源 · 无散落魔数):
  `additionalProperties:false` + `required` + `minLength`/`minItems`;计数前折叠空白(含零宽字符)+ 类型断言;
  拼错 key / 类型不符 / 纯空格占位 → exit 1。
- `--issue` 须**完整 UUID**(8 位短 ID 服务端报 400)。
- `--out` 须 `.html` 且落在 CWD 允许根内(路径白名单 · 拒 `../` 与绝对逃逸);省略则按 type+日期+slug 生成默认路径。
- `--dry-run`:只渲染+校验+落盘,不发布不转换(评审/预览用 · 不依赖 CLI)。
- 发布凭据:multica CLI 自动读 `~/.multica/config.json`,脚本不碰 token。

## 2 · 各 type 的 fields.json 字段(权威 = `publish.py:SCHEMAS`)

- **plan**:`goal`(≥10) · `completionCriteria`[](≥1) · `slug` · `layer`(project|task) · `dri` · `exec`[] · `collab`[] · `reviewer` · `appetite` · `approach`?◆ · `keyDecisions`[]?(首屏「拍板要点」数据源;缺省降级为完成标准前 3 条) · `risks`[]?
- **research**:`question` · `slug` · `findings`?◆(空=骨架占位;**数组时前 3 条进首屏「发现要点」框**) · `openQuestions`?◆ · `verdict`?(总体裁决一句话;缺省两态=骨架「调研中 · 待回填」/已回填「已回填 · 裁决待对账」)
- **case**:`goal`◆ · `whatHappened`◆ · `slug` · `criteriaResults`[{`criterion`,`met`(bool),`notMetReason`?}](结论格三态:「已收尾 · 标准全数达成」/「已收尾 · n/m 达成」/缺省「复盘存档」) · `keyJudgments`[{`title`,`context`,`options`[],`chose`,`inHindsight`,`ancientImpossible`}](≥1 · section4 折叠空白后合计 ≥100 字;title 非空项进首屏「要点提示」) · `ruleCandidates`[]?
- **handoff**:`slug` · `lastCommit` · `branch` · `done`◆ · `nextAction`◆(数组时条款数进首屏「实现项」格) · `deadEnds`[](进「禁区」表) · `pollutionSignal` · `at`?(默认当前时间)

> **◆ = 双形态正文(anyOf)**:收 `string`(单段)或**非空 string 数组**(逐项渲染为段落,化解长文压平)。
> 示例:`"done": ["第一段", "第二段"]` 与 `"done": "一整段"` 等价收取,前者逐项成段;`"nextAction": ["导语", "第一批…", "第二批…"]` 首条作下一步导语。
> `[]` 与 `[""]` 一律拒收(required×空数组同空白 string);数组项必须是 string(类型污染 exit 1)。
> 渲染为「受控文档」样式:受控条+审批栏+类别方章+统计格+要点框,标签全中文、零 emoji、零 rotate,
> 重点前置 480px 内联首屏;类别主色 计划暗朱/研究藏青/复盘墨绿/交接赭棕;CSS 单源 = `assets/style.css`。

字段集 `additionalProperties:false` —— 多/拼错一个 key 即 exit 1(防静默吞)。
`slug` 仅允许字母/数字/`.-_`(阻断路径穿越)。

新增/改文档类型:加 `render_<type>` + schema 到 publish.py,并更新本文件字段契约;样式只改 `assets/style.css`(单源)。

## 3 · 更新 / 再发版(plan 升级、勘误)= 再调一次脚本

换新 `--out` 文件名(`_v2`/`_v3`…),append-only 再发一条评论;永不改附件、永不改 issue 描述。

## 4 · transition 子命令语义(状态机原子转换收口)

`python3 "$TCR/scripts/transition.py" <子命令> <issue> [--dry-run]`;子命令清单以 `--help` 为准。语义:

- `publish-init <issue> --doc-type {plan|research|case|handoff} [--findings-filled]` — 发布即入口转换(publish 脚本自动调;exit 2 后可独立幂等补救)。
- `plan-request-review <issue>` — +计划-评审中 · status in_review。
- `plan-approve <issue>` — +计划-已批准 · −{计划-草稿,计划-评审中,计划-已升级} · status todo(待启动;in_progress 由 build-start 设;不碰 设计-*)。
- `plan-upgrade <issue>` — +{计划-已升级,计划-草稿} · −计划-已批准 · status todo(再走 request-review)。
- `design-request-review <issue>` — +设计-待审 · −设计-已审(复审作废旧批准) · status in_review。设计评审门:plan-approve 之后、build-start 之前,挂同一 work issue;与 计划-已批准 共存。项目层必走、任务层可跳(执行约束见 tc-design-review / tc-build)。
- `design-approve <issue>` — +设计-已审 · −设计-待审 · status todo(回待启动;issue 已在建时补审,verdict 后须 design-approve→build-start 两连)。
- `build-start <issue>` — status in_progress(首个 build session,与开工卡同时机;设计-待审 在场时告警「设计评审未完成就开工」)。
- `case-finalize <issue> [--keep-parent]` — +复盘-已审 · −复盘-待审 · status done;默认连带:父 plan status done + 清父未决流程 label(草稿/评审中/已升级/设计-待审,保留 已批准/设计-已审);祖父 research 尽力 done(legacy 链兜底)。`--keep-parent` 跳过全部父链操作(phase case 专用:父 plan 整体仍在进行)。
- `cancel <issue>` — status cancelled · −全部流程 label。

通用语义:
- label 引用一律名称,经 `multica label list` 运行时解析为 UUID;**禁止硬编码 UUID**(UUID 是 workspace 数据,重建后会变)。解析失败 exit 1 并指向 references/issue-label-state-rules.md 的 create-labels.sh,绝不静默跳过。
- 幂等:执行前 issue get 预读,「label 已存在/已是目标 status」直接跳过;全部为跳过 = 已在目标态,成功。
- 后置复核:写完 issue get 重读断言目标态(CLI success ≠ 做对了),不符 exit 1(暴露并发插队)。
- cancelled 终态防复活:除 cancel 外一切转换硬拒;父链遇 cancelled 完全不动。
- 前置态意外(如 approve 时无 评审中)只 warn 不阻断——保证存量漂移可修。
- exit code:0 成功(含幂等空转) · 1 校验/解析/后置复核失败。

## 5 · HTTP 灾备契约(不是手跑兜底路径)

CLI 不可用时,HTTP 级该怎么调的**逐字契约**固化在下方**本文件唯一的 yaml 代码块**(机器可读,CI 契约探针解析并守护;勿在本文件新增第二个 yaml 代码块)。
其 `inline_marker.url_pattern` 对齐前端权威 `file-cards.ts:FILE_CARD_URL_PATTERN`,两仓并置(或设 `FILE_CARDS_TS`)时断言无漂移。
灾备时读契约对照,**不要**绕开脚本手拼 curl(那是可被手跑、绕开硬校验的旁路)。

```yaml
version: 1

# ── 唯一发布路径(publish 脚本内部 exec)──────────────────────────────
gate_b:
  command:
    - multica
    - issue
    - comment
    - add
    - '<issue-uuid>'
    - --inline
    - '<doc.html>'
    - --content
    - '<caption>'
    - --output
    - json
  token: 'multica CLI 自管(读 ~/.multica/config.json),绝不进调用方 argv → ps 不可见'
  success_signal: '返回评论 JSON 的 attachments 非空(绑定真信号 · 不看 url 前缀)'

# ── HTTP 灾备契约(CLI 不可用时的参考 · 非手跑兜底路径)────────────────
gate_a_disaster_recovery:
  upload:
    method: POST
    path: /api/upload-file
    headers:
      Authorization: 'Bearer <token>'
      X-Workspace-ID: '<workspace-uuid>'
    multipart:
      file: '@<doc.html>;type=text/html'   # MIME 必须 text/html
      issue_id: '<issue-uuid>'             # 必须绑 issue,否则附件不绑定
    returns: { id: '<attachment-uuid>', url: '<relative-url>' }
  comment:
    method: POST
    path: /api/issues/<issue-uuid>/comments
    headers:
      Authorization: 'Bearer <token>'
      X-Workspace-ID: '<workspace-uuid>'
      Content-Type: application/json
    body:
      content: "<caption>\n\n!file[<name>](<url>)"   # url 用 upload 返回的相对 url 原样
      attachment_ids: ['<attachment-uuid>']
    success_signal: '响应 attachments 非空'

# ── 内联标记契约 · 必须对齐前端权威正则(file-cards.ts)───────────────
inline_marker:
  template: '!file[<name>](<url>)'
  # 逐字复制自 file-cards.ts:FILE_CARD_URL_PATTERN.source(权威源)· CI 探针守护漂移
  url_pattern: '\/uploads\/[^)]*|https?:\/\/[^)]+'
  # 逐字复制自 file-cards.ts:NEW_FILE_CARD_RE(整行锚定 · 内嵌 url_pattern)
  line_pattern: '^!file\[([^\]]*)\]\((\/uploads\/[^)]*|https?:\/\/[^)]+)\)$'
  samples_must_match:
    - '!file[plan_2026-06-09_x.html](/uploads/workspaces/abc/plan.html)'
    - '!file[case.html](https://multica-static.example.ai/case.html)'
  samples_must_reject:
    - '!file[x](javascript:alert(1))'   # 协议注入
    - '!file[x](//evil.host/x)'         # 协议相对
    - '!file[x](/api/issues/1/comments)' # 越带 API 路径
```

## 6 · 失败/脏评论撤回

```bash
multica issue comment delete <comment_id>     # 可删,修正后重发
```

发布自检失败信号:返回评论的 `attachments` 为空 = 未绑定的无渲染脏评论,须撤回后重发。

## 7 · CLI 版本门槛(脚本硬依赖 CLI)

发布需 **multica CLI v0.4.11+**(`--inline` v0.4.11 · `skill pull` v0.4.12 · `skill lint` v0.4.13)。
旧版无 `--inline` → 先 `multica update`。`--dry-run`(只渲染校验落盘)不依赖 CLI。

## 8 · Dead ends —— 不要再试

- `multica issue comment add --attachment <本地文件>` **会**上传绑定附件,但**不会**在正文注入 `!file[name](url)` 内联标记——是「附件」形态,不是正文内联渲染。**要正文内联渲染**:用 publish 脚本(或直接 `comment add --inline`)。
- 带/不带 issue_id 的 upload url 都是 /uploads/workspaces/ 前缀;失败模式是 attachment_ids 没绑(comment.attachments 空),不是 url 前缀。
- 别再调研「local 改 HTTP transport」/「doc_publish 纯 CLI 单命令复现内联渲染」——均已证不行。
