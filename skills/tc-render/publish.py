#!/usr/bin/env python3
"""tc-render publish — 渲染 + 硬校验 + 命门B 收口发布 RPI 四类文档(方案A)。

agent **调用本脚本**(确定性 + 硬校验),取代手跑 PUBLISH.md 的 prose curl。
本地 MCP 的 zod 约束在此复刻为 HARD CHECK(违约 exit 1),无需 MCP 服务器。

发布走**命门B**:内部 exec `multica issue comment add <issue> --inline <doc>`,
唯一发布路径。token 由 multica CLI 自管(读 ~/.multica/config.json),绝不进
本脚本 argv → `ps` 不可见。命门A(raw upload→comment HTTP)降为契约化灾备,
见 publish-contract-v1.yaml(对齐前端 file-cards.ts:NEW_FILE_CARD_RE + CI 探针)。

用法:
  publish.py --type {plan|research|case|handoff} --data FIELDS.json --issue <UUID> \
             [--caption STR] [--out PATH] [--dry-run]

  --data    JSON 文件,字段按 SCHEMAS[type] 硬校验(additionalProperties:false +
            required + 阈值派生自 schema minLength/minItems,无硬编码魔数)
  --issue   目标 issue 完整 UUID(--dry-run 时可省)
  --out     本地 html 落盘路径(须 .html 且在 CWD 允许根内 · 路径白名单);省略则按 type+date+slug 默认
  --dry-run 只渲染+校验+落盘,不发布(评审用)

成功打印 JSON {comment_id, attachment_id, url, doc_path};校验失败 exit 1。
"""
import argparse, json, os, sys, re, subprocess, html, datetime, pathlib

HERE = pathlib.Path(__file__).resolve().parent
CSS = (HERE / "assets" / "style.css").read_text()
UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
SLUG_RE = re.compile(r"^[A-Za-z0-9._-]+$")   # 无 / 无 .. 无空格 → 阻断 slug 路径穿越


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def fail(msg):
    # 唯一对外错误出口:友好 ERROR,绝不泄露裸 Python traceback(red-team)。
    print("VALIDATION FAILED · " + msg, file=sys.stderr)
    sys.exit(1)


def today():
    return datetime.date.today().isoformat()  # YYYY-MM-DD


def now_min():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


# ======================================================================
# 字段 JSON Schema(单一事实源)· 校验阈值从此派生,renderer 不再硬编码魔数
# ======================================================================
_PYT = {"string": str, "array": list, "object": dict, "boolean": bool,
        "integer": int, "number": (int, float)}

_KEY_JUDGMENT = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "title": {"type": "string"}, "context": {"type": "string"},
        "options": {"type": "array", "items": {"type": "string"}},
        "chose": {"type": "string"}, "inHindsight": {"type": "string"},
        "ancientImpossible": {"type": "string"},
    },
}
_CRITERION_RESULT = {
    "type": "object", "additionalProperties": False, "required": ["criterion"],
    "properties": {
        "criterion": {"type": "string"}, "met": {"type": "boolean"},
        "notMetReason": {"type": "string"},
    },
}

SCHEMAS = {
    "plan": {
        "type": "object", "additionalProperties": False,
        "required": ["goal", "completionCriteria", "slug"],
        "properties": {
            "goal": {"type": "string", "minLength": 10},
            "completionCriteria": {"type": "array", "minItems": 1, "items": {"type": "string"}},
            "slug": {"type": "string"},
            "layer": {"type": "string", "enum": ["project", "task"]},
            "dri": {"type": "string"},
            "exec": {"type": "array", "items": {"type": "string"}},
            "collab": {"type": "array", "items": {"type": "string"}},
            "reviewer": {"type": "string"},
            "appetite": {"type": "string"},
            "approach": {"type": "string"},
        },
    },
    "research": {
        "type": "object", "additionalProperties": False,
        "required": ["question", "slug"],
        "properties": {
            "question": {"type": "string", "minLength": 1},
            "slug": {"type": "string"},
            "findings": {"type": "string"},
            "openQuestions": {"type": "string"},
        },
    },
    "case": {
        "type": "object", "additionalProperties": False,
        "required": ["goal", "whatHappened", "slug", "keyJudgments"],
        # 关键判断段(section4)实质内容下限 —— 跨字段约束,JSON Schema 无法表达,
        # 阈值在此声明、由 validate_fields 读取(仍派生自 schema,非散落魔数)。
        "x-section4-min-chars": 100,
        "properties": {
            "goal": {"type": "string"}, "whatHappened": {"type": "string"},
            "slug": {"type": "string"},
            "criteriaResults": {"type": "array", "items": _CRITERION_RESULT},
            "keyJudgments": {"type": "array", "minItems": 1, "items": _KEY_JUDGMENT},
            "ruleCandidates": {"type": "array", "items": {"type": "string"}},
        },
    },
    "handoff": {
        "type": "object", "additionalProperties": False,
        "required": ["slug", "done", "nextAction"],
        "properties": {
            "slug": {"type": "string"}, "lastCommit": {"type": "string"},
            "branch": {"type": "string"}, "done": {"type": "string"},
            "nextAction": {"type": "string"},
            "deadEnds": {"type": "array", "items": {"type": "string"}},
            "pollutionSignal": {"type": "string"}, "at": {"type": "string"},
        },
    },
}


# 零宽字符:str.split() 不折叠它们(.isspace()==False),会被当实质内容撑过下限 → 显式剔除
# U+200B 零宽空格 / U+200C ZWNJ / U+200D ZWJ / U+2060 word-joiner / U+FEFF BOM
_ZERO_WIDTH = dict.fromkeys((0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF), None)


def _folded(v):
    """折叠空白(含零宽字符)后的实质字符数(纯空格/零宽占位 → 0)。"""
    if isinstance(v, str):
        return len("".join(v.split()).translate(_ZERO_WIDTH))
    if isinstance(v, list):
        return sum(_folded(x) for x in v)
    return 0


def _validate(value, schema, path):
    """递归硬校验:type(类型断言)/ required / additionalProperties:false /
    enum / minItems(非空项)/ minLength(折叠空白后)。违约 fail() exit 1。"""
    t = schema.get("type")
    if t:
        py = _PYT[t]
        # bool 是 int 子类:integer/number 不接受 boolean
        if t in ("integer", "number") and isinstance(value, bool):
            fail("%s 类型应为 %s,不能是 boolean" % (path or "顶层", t))
        if not isinstance(value, py):
            fail("%s 类型应为 %s(类型断言)" % (path or "顶层", t))
    if "enum" in schema and value not in schema["enum"]:
        fail("%s 取值须属 %s" % (path or "顶层", schema["enum"]))
    if t == "object":
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = sorted(set(value) - set(props))
            if extra:
                fail("%s 未知字段(拼错?additionalProperties:false 拒):%s" % (path or "顶层", ", ".join(extra)))
        for r in schema.get("required", []):
            if r not in value or value.get(r) is None or (isinstance(value.get(r), str) and not value[r].strip()):
                fail("%s 缺必填字段(或为空):%s" % (path or "顶层", r))
        for k, sub in props.items():
            if k in value and value[k] is not None:
                _validate(value[k], sub, (path + "." if path else "") + k)
    elif t == "array":
        nonblank = [x for x in value if not (isinstance(x, str) and not x.strip())]
        if "minItems" in schema and len(nonblank) < schema["minItems"]:
            fail("%s 须 ≥%d 个非空项(当前 %d · 阈值派生自 schema.minItems)"
                 % (path or "顶层", schema["minItems"], len(nonblank)))
        sub = schema.get("items")
        if sub:
            for i, x in enumerate(value):
                _validate(x, sub, "%s[%d]" % (path or "", i))
    elif t == "string" and "minLength" in schema:
        n = _folded(value)
        if n < schema["minLength"]:
            fail("%s 实质内容(折叠空白后)须 ≥%d 字符,当前 %d(阈值派生自 schema.minLength)"
                 % (path or "顶层", schema["minLength"], n))


def validate_fields(doc_type, data):
    """顶层硬校验入口:schema 校验 + slug 路径安全 + case section4 实质内容下限。"""
    if not isinstance(data, dict):
        fail("fields 顶层须为 JSON object")
    _validate(data, SCHEMAS[doc_type], "")
    slug = data.get("slug")
    if slug is not None and not SLUG_RE.match(str(slug)):
        fail("slug 仅允许字母/数字/.-_(阻断路径穿越);得到:%r" % slug)
    if doc_type == "case":
        threshold = SCHEMAS["case"]["x-section4-min-chars"]
        total = sum(_folded(v) for j in data.get("keyJudgments", []) for v in j.values())
        if total < threshold:
            fail("case 关键判断(section4)折叠空白后实质内容须 ≥%d 字符,当前 %d" % (threshold, total))


# ======================================================================
# 渲染(纯渲染 · 校验已前移到 validate_fields)
# ======================================================================

def shell(title, eyebrow, meta_items, sections_html, footer):
    meta = "".join('<span>%s <b>%s</b></span>' % (esc(l), esc(v)) for l, v in meta_items)
    return (
        '<!DOCTYPE html>\n<html lang="zh-CN"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        '<title>%s</title>\n<style>%s</style></head>\n<body>\n'
        '<div class="eyebrow">%s</div>\n<h1>%s</h1>\n<div class="meta">%s</div>\n'
        '%s\n<footer>%s</footer>\n</body></html>\n'
    ) % (esc(title), CSS, esc(eyebrow), esc(title), meta, sections_html, esc(footer))


def render_plan(d):
    goal = (d.get("goal") or "").strip()
    crits = [c for c in (d.get("completionCriteria") or []) if str(c).strip()]
    slug = d.get("slug") or "plan"
    layer = d.get("layer") or "project"
    exec_ = "、".join(d.get("exec") or []) or "(未分配)"
    collab = "、".join(d.get("collab") or []) or "(无)"
    reviewer = d.get("reviewer") or "(待指派)"
    dri = d.get("dri") or "(指派)"
    appetite = d.get("appetite") or "(设定)"
    crit_li = "".join("<li>%s</li>" % esc(c) for c in crits)
    secs = [
        '<h2>目标</h2><div class="field"><div class="field-label">Goal</div>%s</div>' % esc(goal),
        '<h2>完成标准</h2><div class="field crit"><ul>%s</ul></div>' % crit_li,
        '<h2>分工</h2><div class="field"><div class="field-label">Roles</div>'
        'DRI <code>%s</code> · EXEC <code>%s</code> · COLLAB <code>%s</code> · REVIEW <code>%s</code></div>'
        % (esc(dri), esc(exec_), esc(collab), esc(reviewer)),
        '<h2>投入预算</h2><div class="callout"><b>%s</b> · 超时触发升版强制重审。</div>' % esc(appetite),
    ]
    if (d.get("approach") or "").strip():
        secs.append('<h2>方案</h2><div class="field">%s</div>' % esc(d["approach"]))
    doc = shell(slug, "PLAN · 计划 · %s" % layer,
                [("DRI", d.get("dri") or "—"), ("Layer", layer), ("Appetite", d.get("appetite") or "—")],
                "\n".join(secs), "team-context · RPI Plan phase · multica issue 内渲染")
    return doc, "docs/plans/plan_%s_%s.html" % (today(), slug)


def render_research(d):
    q = (d.get("question") or "").strip()
    slug = d.get("slug") or "research"
    findings = d.get("findings") or "(待 fresh session 深度调研填充)"
    openq = d.get("openQuestions") or "(research 过程中浮现的开放问题)"
    secs = "\n".join([
        '<h2>问题</h2><div class="field"><div class="field-label">Question</div>%s</div>' % esc(q),
        '<h2>发现</h2><div class="field"><div class="field-label">Findings</div>%s</div>' % esc(findings),
        '<h2>待解问题</h2><div class="field">%s</div>' % esc(openq),
    ])
    doc = shell(slug, "RESEARCH · 研究", [("Phase", "RPI Research")], secs,
                "team-context · RPI Research phase · multica issue 内渲染")
    return doc, "docs/research/research_%s_%s.html" % (today(), slug)


def render_case(d):
    kj = d.get("keyJudgments") or []
    slug = d.get("slug") or "case"
    crit_li = ""
    for c in (d.get("criteriaResults") or []):
        mark = "✅" if c.get("met") else "❌"
        reason = (" — %s" % esc(c["notMetReason"])) if (not c.get("met") and c.get("notMetReason")) else ""
        crit_li += "<li>%s %s%s</li>" % (mark, esc(c.get("criterion")), reason)
    j_html = "\n".join(
        ('<div class="field"><div class="field-label">判断:%s</div>\n'
         '<b>背景</b> %s<br>\n<b>选项</b> %s<br>\n<b>选择</b> %s<br>\n'
         '<b>事后看</b> %s<br>\n<b>古法不可能</b> %s</div>')
        % (esc(j.get("title")), esc(j.get("context")), esc(" / ".join(j.get("options") or [])),
           esc(j.get("chose")), esc(j.get("inHindsight")), esc(j.get("ancientImpossible")))
        for j in kj)
    rules = d.get("ruleCandidates") or []
    rules_html = ("<ul>%s</ul>" % "".join("<li>%s</li>" % esc(r) for r in rules)) if rules else "_(无)_"
    secs = "\n".join([
        '<h2>1 · 目标</h2><div class="field">%s</div>' % esc(d.get("goal")),
        '<h2>2 · 实际发生</h2><div class="field">%s</div>' % esc(d.get("whatHappened")),
        '<h2>3 · 完成标准</h2><div class="field crit"><ul>%s</ul></div>' % crit_li,
        '<h2>4 · 关键判断</h2>%s' % j_html,
        '<h2>5 · 规则候选</h2><div class="field">%s</div>' % rules_html,
    ])
    doc = shell(slug, "CASE · 复盘", [("Phase", "RPI Debrief")], secs,
                "team-context · RPI Debrief · SOP 非妥协 #2 · multica issue 内渲染")
    return doc, "cases/%s-%s.html" % (today(), slug)


def render_handoff(d):
    slug = d.get("slug") or "handoff"
    at = d.get("at") or now_min()
    dead = d.get("deadEnds") or []
    dead_html = ("<ul>%s</ul>" % "".join("<li>%s</li>" % esc(x) for x in dead)) if dead else "(无)"
    sec = ("<h2>当前状态 · handoff @ %s</h2>\n<div class=\"callout\">\n"
           '<div class="field-label">Last commit</div><code>%s</code> · <code>%s</code>\n'
           '<div class="field-label">What\'s done</div>%s\n'
           '<div class="field-label">Next action</div>%s\n'
           '<div class="field-label">Dead ends — do NOT retry</div>%s\n'
           '<div class="field-label">Pollution signal</div>%s\n</div>'
           ) % (esc(at), esc(d.get("lastCommit")), esc(d.get("branch")), esc(d.get("done")),
                esc(d.get("nextAction")), dead_html, esc(d.get("pollutionSignal")))
    doc = shell(slug, "HANDOFF · 交接", [("Phase", "RPI Handoff")], sec,
                "team-context · RPI handoff · multica issue 内渲染")
    return doc, "docs/plans/handoff_%s_%s.html" % (today(), slug)


RENDERERS = {"plan": render_plan, "research": render_research, "case": render_case, "handoff": render_handoff}


# ======================================================================
# 路径白名单 + 命门B 发布
# ======================================================================

def safe_out_path(out_str):
    """red-team:--out / 默认路径必须落在 CWD 允许根内(拒 ../ 与绝对逃逸)且 .html
    (命门B --inline 只内联 text/html MIME)。违约 fail()。返回 resolved 绝对路径。"""
    root = pathlib.Path.cwd().resolve()
    resolved = (root / out_str).resolve()   # 绝对 out 会替换 root,随后被 relative_to 拒
    try:
        resolved.relative_to(root)
    except ValueError:
        fail("--out 路径越权:%s 不在允许根 %s 内(red-team 路径白名单)" % (out_str, root))
    if resolved.suffix.lower() != ".html":
        fail("--out 须 .html(命门B --inline 只内联 text/html);得到后缀 %r" % resolved.suffix)
    return resolved


def build_publish_argv(issue, doc_path, caption):
    """命门B 发布命令(纯函数 · 便于断言 argv 无凭据)。

    token 由 multica CLI 自管(读 ~/.multica/config.json),绝不出现在此 argv →
    `ps` 不可见(red-team:token 移出 argv)。"""
    return ["multica", "issue", "comment", "add", str(issue),
            "--inline", str(doc_path), "--content", caption, "--output", "json"]


def publish(issue, doc_path, caption):
    """命门B 收口:exec `multica issue comment add --inline`,解析 JSON,自检 attachments。"""
    argv = build_publish_argv(issue, doc_path, caption)
    try:
        proc = subprocess.run(argv, capture_output=True, text=True)
    except FileNotFoundError:
        fail("找不到 multica CLI(命门B 收口入口);先安装/更新 multica(≥v0.4.11)再发布")
    if proc.returncode != 0:
        fail("命门B 发布失败(multica exit %d):%s"
             % (proc.returncode, (proc.stderr or proc.stdout or "").strip()[:300]))
    try:
        r = json.loads(proc.stdout)
    except Exception:
        fail("命门B 输出非 JSON: %s" % (proc.stdout or proc.stderr or "")[:200])
    atts = r.get("attachments") or []
    if not atts:
        # 命门 自检:绑定真信号 = attachments 非空(不看 url 前缀)。脏评论需撤回。
        fail("attachments 未绑定 → 无渲染脏评论。撤回:multica issue comment delete %s" % r.get("id"))
    a0 = atts[0] if isinstance(atts[0], dict) else {}
    return {"comment_id": r.get("id"), "attachment_id": a0.get("id"), "url": a0.get("url")}


def main():
    ap = argparse.ArgumentParser(description="tc-render 渲染+硬校验+命门B 发布")
    ap.add_argument("--type", required=True, choices=list(RENDERERS))
    ap.add_argument("--data", required=True, help="JSON 字段文件")
    ap.add_argument("--issue", default="", help="目标 issue 完整 UUID")
    ap.add_argument("--caption", default="文档(方案A · 下方渲染)")
    ap.add_argument("--out", default="", help="本地 html 落盘路径(.html · CWD 允许根内)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not a.dry_run:
        if not a.issue:
            fail("--issue 必填(非 --dry-run);projectId/issueId 一律完整 UUID")
        if not UUID_RE.fullmatch(a.issue):   # fullmatch:拒尾随换行等(`$` 会放过 uuid+\n)
            fail("--issue 须为完整 UUID,不能用 8 位短 ID(rule #6)")

    # 友好读取 --data:坏 JSON / 缺文件 → 友好 ERROR,不泄露裸 traceback(red-team)
    try:
        with open(a.data, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        fail("--data 文件不存在:%s" % a.data)
    except json.JSONDecodeError as e:
        fail("--data 不是合法 JSON(第%d行第%d列:%s);请检查字段文件" % (e.lineno, e.colno, e.msg))
    except OSError as e:
        fail("--data 读取失败:%s" % e)

    validate_fields(a.type, data)                # 硬校验前移(schema + slug + section4)
    doc, default_path = RENDERERS[a.type](data)  # 纯渲染
    out = safe_out_path(a.out or default_path)   # 路径白名单 + .html MIME 守卫
    if not doc.startswith("<!DOCTYPE html"):     # 内联 MIME 守卫(防御纵深)· 写盘前拒
        fail("渲染产物非 HTML,拒绝内联发布")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc)

    result = {"doc_path": str(out), "bytes": len(doc), "type": a.type}
    if a.dry_run:
        result["dry_run"] = True
    else:
        result.update(publish(a.issue, str(out), a.caption))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
