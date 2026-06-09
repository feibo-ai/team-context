#!/usr/bin/env python3
"""tc-render publish — 渲染 + 硬校验 + 命门A 内联发布 RPI 四类文档(方案A)。

agent **调用本脚本**(确定性 + 硬校验),取代手跑 PUBLISH.md 的 prose curl。
本地 MCP 的 zod 约束在此复刻为 HARD CHECK(违约 exit 1),无需 MCP 服务器。

用法:
  publish.py --type {plan|research|case|handoff} --data FIELDS.json --issue <UUID> \
             [--caption STR] [--out PATH] [--dry-run]

  --data    JSON 文件,字段见各 type 的 render_* / 校验(agent 写内容,脚本渲染+校验)
  --issue   目标 issue 完整 UUID(--dry-run 时可省)
  --out     本地 html 落盘路径(git/离线副本);省略则按 type+date+slug 默认
  --dry-run 只渲染+校验+落盘,不发布(评审用)

配置读 ~/.multica/config.json(server_url / workspace_id / token)。
成功打印 JSON {comment_id, attachment_id, url, doc_path};校验失败 exit 1。
"""
import argparse, json, os, sys, re, subprocess, html, datetime, pathlib

HERE = pathlib.Path(__file__).resolve().parent
CSS = (HERE / "assets" / "style.css").read_text()
UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def fail(msg):
    print("VALIDATION FAILED · " + msg, file=sys.stderr)
    sys.exit(1)


def today():
    return datetime.date.today().isoformat()  # YYYY-MM-DD


def now_min():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def shell(title, eyebrow, meta_items, sections_html, footer):
    meta = "".join('<span>%s <b>%s</b></span>' % (esc(l), esc(v)) for l, v in meta_items)
    return (
        '<!DOCTYPE html>\n<html lang="zh-CN"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        '<title>%s</title>\n<style>%s</style></head>\n<body>\n'
        '<div class="eyebrow">%s</div>\n<h1>%s</h1>\n<div class="meta">%s</div>\n'
        '%s\n<footer>%s</footer>\n</body></html>\n'
    ) % (esc(title), CSS, esc(eyebrow), esc(title), meta, sections_html, esc(footer))


# ---- 渲染 + 硬校验(复刻 team-context-mcp render/*.ts + 各 zod) ----

def render_plan(d):
    goal = (d.get("goal") or "").strip()
    if len(goal) < 10:
        fail("plan goal 须 ≥10 字符且具体可验(原 plan_create zod: goal.min(10))")
    crits = [c for c in (d.get("completionCriteria") or []) if str(c).strip()]
    if len(crits) < 1:
        fail("plan 完成标准 须 ≥1 条非空(原 zod: completionCriteria.min(1))")
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
    if not q:
        fail("research question 不能为空")
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
    if len(kj) < 1:
        fail("case keyJudgments 须 ≥1(原 case_create zod: keyJudgments.min(1))")
    s4_chars = sum(len(str(v)) for j in kj for v in j.values())
    if s4_chars < 100:
        fail("case 关键判断(section4)实质内容 须 ≥100 字符,当前 %d(原 case_review MIN_SECTION_4_CHARS)" % s4_chars)
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


def publish(issue, doc_path, caption):
    cfg = json.load(open(os.path.expanduser("~/.multica/config.json")))
    server, ws, tok = cfg["server_url"], cfg["workspace_id"], cfg["token"]
    name = os.path.basename(doc_path)
    up = subprocess.run(
        ["curl", "-sS", "--retry", "2", "-X", "POST", server + "/api/upload-file",
         "-H", "Authorization: Bearer " + tok, "-H", "X-Workspace-ID: " + ws,
         "-F", "file=@%s;type=text/html" % doc_path, "-F", "issue_id=" + issue],
        capture_output=True, text=True)
    try:
        u = json.loads(up.stdout)
    except Exception:
        fail("upload 响应非 JSON: %s" % (up.stdout or up.stderr)[:200])
    aid, aurl = u.get("id"), u.get("url")
    if not aurl:
        fail("upload 响应无 url(无法内联渲染)id=%s" % aid)
    body = json.dumps({"content": caption + "\n\n!file[%s](%s)" % (name, aurl), "attachment_ids": [aid]})
    resp = subprocess.run(
        ["curl", "-sS", "--retry", "2", "-X", "POST", server + "/api/issues/%s/comments" % issue,
         "-H", "Authorization: Bearer " + tok, "-H", "X-Workspace-ID: " + ws,
         "-H", "Content-Type: application/json", "--data-binary", "@-"],
        input=body, capture_output=True, text=True)
    try:
        r = json.loads(resp.stdout)
    except Exception:
        fail("comment 响应非 JSON: %s" % (resp.stdout or resp.stderr)[:200])
    if not (r.get("attachments")):
        # 命门A 自检:绑定失败 = 无渲染脏评论
        fail("attachments 未绑定 → 无渲染脏评论。撤回:multica issue comment delete %s" % r.get("id"))
    return {"comment_id": r.get("id"), "attachment_id": aid, "url": aurl}


def main():
    ap = argparse.ArgumentParser(description="tc-render 渲染+硬校验+命门A 发布")
    ap.add_argument("--type", required=True, choices=list(RENDERERS))
    ap.add_argument("--data", required=True, help="JSON 字段文件")
    ap.add_argument("--issue", default="", help="目标 issue 完整 UUID")
    ap.add_argument("--caption", default="文档(方案A · 下方渲染)")
    ap.add_argument("--out", default="", help="本地 html 落盘路径")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not a.dry_run:
        if not a.issue:
            fail("--issue 必填(非 --dry-run);projectId/issueId 一律完整 UUID")
        if not UUID_RE.match(a.issue):
            fail("--issue 须为完整 UUID,不能用 8 位短 ID(rule #6)")

    data = json.load(open(a.data))
    doc, default_path = RENDERERS[a.type](data)  # 渲染前/中做硬校验,违约 exit 1
    out = a.out or default_path
    p = pathlib.Path(out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(doc)

    result = {"doc_path": str(p), "bytes": len(doc), "type": a.type}
    if a.dry_run:
        result["dry_run"] = True
    else:
        result.update(publish(a.issue, str(p), a.caption))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
