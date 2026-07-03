#!/usr/bin/env python3
"""tc-render publish — 渲染 + 硬校验 + 命门B 收口发布 RPI 四类文档(方案A)。

agent **调用本脚本**(确定性 + 硬校验),调用契约见 references/publish-contract.md。
本地 MCP 的 zod 约束在此复刻为 HARD CHECK(违约 exit 1),无需 MCP 服务器。

发布走**命门B**:内部 exec `multica issue comment add <issue> --inline <doc>`,
唯一发布路径。token 由 multica CLI 自管(读 ~/.multica/config.json),绝不进
本脚本 argv → `ps` 不可见。命门A(raw upload→comment HTTP)降为契约化灾备,
见 references/publish-contract.md 的 yaml 契约块(对齐前端
file-cards.ts:NEW_FILE_CARD_RE + CI 探针)。

用法:
  publish.py --type {plan|research|case|handoff} --data FIELDS.json --issue <UUID> \
             [--caption STR] [--out PATH] [--dry-run] [--no-transition]

  --data    JSON 文件,字段按 SCHEMAS[type] 硬校验(additionalProperties:false +
            required + 阈值派生自 schema minLength/minItems,无硬编码魔数)
  --issue   目标 issue 完整 UUID(--dry-run 时可省)
  --out     本地 html 落盘路径(须 .html 且在 CWD 允许根内 · 路径白名单);省略则按 type+date+slug 默认
  --dry-run 只渲染+校验+落盘,不发布也不转换(评审用)
  --no-transition 发布后跳过入口状态转换(逃生口;默认开启转换)

发布成功后自动做**入口状态转换**(transition.py publish-init,语义单源见该脚本):
  plan→+计划-草稿(仅当无 计划-* label) / research→+研究(findings 非空时 status done)
  / case→+复盘-待审(仅当无 复盘-已审)+status in_review / handoff→不动。

exit code:0 全成功 · 1 校验/发布失败(评论未发出) · 2 评论已发但入口转换失败
(**绝不重跑 publish** —— 会重复发评论;按 stderr 给出的幂等补救命令单独补转换)。
"""
import argparse, json, os, sys, re, subprocess, html, datetime, pathlib

SKILL_ROOT = pathlib.Path(__file__).resolve().parent.parent   # scripts/ 的上一级 = skill 根
SCRIPTS_DIR = SKILL_ROOT / "scripts"
CSS = (SKILL_ROOT / "assets" / "style.css").read_text()
UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
SLUG_RE = re.compile(r"^[A-Za-z0-9._-]+$")   # 无 / 无 .. 无空格 → 阻断 slug 路径穿越
GATE_COUNTS_PATH = os.path.expanduser("~/.multica/gate-counts.json")  # 命门B 成功率计数(daemon 心跳读 · ⑪)


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


def _dual(**string_extra):
    """正文字段双形态(plan v4 D1):string(旧路径)或非空 string 数组(段落/条款)。

    anyOf 任一子 schema 通过即通过;数组侧 minItems:1 按非空项计数,
    [] 与 [""] 一律拒 —— required×空数组拒收由此承担。"""
    return {"anyOf": [
        {"type": "string", **string_extra},
        {"type": "array", "items": {"type": "string"}, "minItems": 1},
    ]}

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
            "approach": _dual(),
            "keyDecisions": {"type": "array", "items": {"type": "string"}},
            "risks": {"type": "array", "items": {"type": "string"}},
        },
    },
    "research": {
        "type": "object", "additionalProperties": False,
        "required": ["question", "slug"],
        "properties": {
            "question": {"type": "string", "minLength": 1},
            "slug": {"type": "string"},
            "findings": _dual(),
            "openQuestions": _dual(),
            "verdict": {"type": "string"},
        },
    },
    "case": {
        "type": "object", "additionalProperties": False,
        "required": ["goal", "whatHappened", "slug", "keyJudgments"],
        # 关键判断段(section4)实质内容下限 —— 跨字段约束,JSON Schema 无法表达,
        # 阈值在此声明、由 validate_fields 读取(仍派生自 schema,非散落魔数)。
        "x-section4-min-chars": 100,
        "properties": {
            "goal": _dual(), "whatHappened": _dual(),
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
            "branch": {"type": "string"}, "done": _dual(),
            "nextAction": _dual(),
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


class _Invalid(ValueError):
    """schema 违约(内部信号);validate_fields 统一转 fail() 友好 ERROR,绝不裸 traceback。"""


def _invalid(msg):
    raise _Invalid(msg)


def _validate(value, schema, path):
    """递归硬校验:anyOf(任一子 schema 通过即通过,全败报首条)/ type(类型断言)/
    required(空白 string 与空/全空白 array 同拒)/ additionalProperties:false /
    enum / minItems(非空项)/ minLength(折叠空白后)。违约抛 _Invalid。"""
    if "anyOf" in schema:
        first = None
        for sub in schema["anyOf"]:
            try:
                _validate(value, sub, path)
                return
            except _Invalid as e:
                if first is None:
                    first = e
        raise first if first is not None else _Invalid("%s anyOf 子 schema 为空" % (path or "顶层"))
    t = schema.get("type")
    if t:
        py = _PYT[t]
        # bool 是 int 子类:integer/number 不接受 boolean
        if t in ("integer", "number") and isinstance(value, bool):
            _invalid("%s 类型应为 %s,不能是 boolean" % (path or "顶层", t))
        if not isinstance(value, py):
            _invalid("%s 类型应为 %s(类型断言)" % (path or "顶层", t))
    if "enum" in schema and value not in schema["enum"]:
        _invalid("%s 取值须属 %s" % (path or "顶层", schema["enum"]))
    if t == "object":
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = sorted(set(value) - set(props))
            if extra:
                _invalid("%s 未知字段(拼错?additionalProperties:false 拒):%s" % (path or "顶层", ", ".join(extra)))
        for r in schema.get("required", []):
            v = value.get(r)
            blank_str = isinstance(v, str) and not v.strip()
            # 空数组 / 全是空白字符串的数组,与空白 string 同等拒收(required×双形态)
            blank_list = isinstance(v, list) and (not v or all(
                isinstance(x, str) and not x.strip() for x in v))
            if r not in value or v is None or blank_str or blank_list:
                _invalid("%s 缺必填字段(或为空):%s" % (path or "顶层", r))
        for k, sub in props.items():
            if k in value and value[k] is not None:
                _validate(value[k], sub, (path + "." if path else "") + k)
    elif t == "array":
        nonblank = [x for x in value if not (isinstance(x, str) and not x.strip())]
        if "minItems" in schema and len(nonblank) < schema["minItems"]:
            _invalid("%s 须 ≥%d 个非空项(当前 %d · 阈值派生自 schema.minItems)"
                     % (path or "顶层", schema["minItems"], len(nonblank)))
        sub = schema.get("items")
        if sub:
            for i, x in enumerate(value):
                _validate(x, sub, "%s[%d]" % (path or "", i))
    elif t == "string" and "minLength" in schema:
        n = _folded(value)
        if n < schema["minLength"]:
            _invalid("%s 实质内容(折叠空白后)须 ≥%d 字符,当前 %d(阈值派生自 schema.minLength)"
                     % (path or "顶层", schema["minLength"], n))


def validate_fields(doc_type, data):
    """顶层硬校验入口:schema 校验 + slug 路径安全 + case section4 实质内容下限。"""
    if not isinstance(data, dict):
        fail("fields 顶层须为 JSON object")
    try:
        _validate(data, SCHEMAS[doc_type], "")
    except _Invalid as e:
        fail(str(e))
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

TYPE_META = {
    "plan":     {"cls": "t-plan",     "cn": "计划", "seal": "计<br>划", "rule": "流程依据:SOP v0.4 非妥协 #1"},
    "research": {"cls": "t-research", "cn": "研究", "seal": "研<br>究", "rule": "流程依据:SOP v0.4 · 研究阶段"},
    "case":     {"cls": "t-case",     "cn": "复盘", "seal": "复<br>盘", "rule": "流程依据:SOP v0.4 非妥协 #2"},
    "handoff":  {"cls": "t-handoff",  "cn": "交接", "seal": "交<br>接", "rule": "流程依据:SOP v0.4 非妥协 #1"},
}

_CN_NUM = "一二三四五六七八九十"


def cn_idx(i):
    """1-based 中文序号(判断一/判断二…);超出十回退阿拉伯数字。"""
    return _CN_NUM[i - 1] if 1 <= i <= len(_CN_NUM) else str(i)


def _items(v):
    """双形态值 → 非空项列表(string 视为单项;None/空 → [])。"""
    raw = [v] if isinstance(v, str) else list(v or [])
    return [str(x) for x in raw if str(x or "").strip()]


def paras(v, blank=""):
    """双形态正文 → <p> 序列(D1):string=单段(旧路径),array=逐项一段;空→占位段。"""
    items = _items(v) or ([blank] if blank else [])
    return "".join("<p>%s</p>" % esc(x) for x in items)


def appr_grid(doc_type, row1, row2):
    """审批栏:左方章跨两行 + 两行各 4 格。row*: [(label, value, vcls)]。"""
    def cell(c, extra):
        label, value, vcls = c
        return ('<div class="ac%s"><div class="al">%s</div><div class="av%s">%s</div></div>'
                % (extra, esc(label), (" " + vcls) if vcls else "", esc(value)))
    cells = [cell(c, " last" if i == 3 else "") for i, c in enumerate(row1)]
    cells += [cell(c, " ac2 last" if i == 3 else " ac2") for i, c in enumerate(row2)]
    return ('<div class="appr"><div class="sealcell"><div class="sq">%s</div></div>%s</div>'
            % (TYPE_META[doc_type]["seal"], "".join(cells)))


def tc(num_html, label, cls="", small=False):
    """统计格单元;num_html 由调用方负责转义(允许 <small> 结构)。"""
    return ('<div class="tc%s"><div class="n%s">%s</div><div class="l">%s</div></div>'
            % ((" " + cls) if cls else "", " sm" if small else "", num_html, esc(label)))


def tally(cells, c3=False):
    return '<div class="tally%s">%s</div>' % (" c3" if c3 else "", "".join(cells))


def keypoints(title, items):
    """要点提示框;无非空项 → 空串(整框不渲染)。"""
    items = _items(items)
    if not items:
        return ""
    lis = "".join('<li><span class="kn">%d</span>%s</li>' % (i + 1, esc(x))
                  for i, x in enumerate(items))
    return '<div class="keypoints"><div class="kt">%s</div><ol>%s</ol></div>' % (esc(title), lis)


def h2(num, title, danger=False):
    return ('<h2%s><span class="num">%s</span>%s</h2>'
            % (' class="danger"' if danger else "", esc(num), esc(title)))


def shell(doc_type, slug, h1_text, sub, appr_html, mid_html, body_html):
    """受控文档骨架(顺序齐定稿原型):sheet 框线 + 受控条 + 审批栏 + 标题区
    + 首屏件(tally/问题框/要点)+ 正文。标签全中文;默认落盘路径不在此层。"""
    m = TYPE_META[doc_type]
    sub_html = ('<div class="sub">%s</div>' % esc(sub)) if sub else ""
    return (
        '<!DOCTYPE html>\n<html lang="zh-CN"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        '<title>%s</title>\n<style>%s</style></head>\n<body class="%s">\n'
        '<div class="sheet">\n'
        '<div class="ctrl"><span>受控文档 · <b>%s</b></span><span>%s</span></div>\n'
        '%s\n'
        '<div class="titlebar"><h1>%s</h1>%s</div>\n'
        '%s\n'
        '<div class="body">\n%s\n</div>\n'
        '</div>\n'
        '<footer>AI MIQ 团队 · 受控文档 · %s · multica issue 内联渲染</footer>\n'
        '</body></html>\n'
    ) % (esc(h1_text), CSS, m["cls"], esc(slug), esc(m["rule"]), appr_html,
         esc(h1_text), sub_html, mid_html, body_html, esc(m["cn"]))


def render_plan(d):
    slug = d.get("slug") or "plan"
    layer_cn = "任务层" if (d.get("layer") or "project") == "task" else "项目层"
    crits = _items(d.get("completionCriteria"))
    decisions = _items(d.get("keyDecisions"))
    risks = _items(d.get("risks"))
    dri = d.get("dri") or "(指派)"
    reviewer = d.get("reviewer") or "(待指派)"
    appetite = d.get("appetite") or "(设定)"
    exec_ = "、".join(_items(d.get("exec"))) or "(未分配)"
    collab = "、".join(_items(d.get("collab"))) or "(无)"

    appr = appr_grid("plan",
                     [("文档类别", "实施计划", "t"), ("编号", slug, ""),
                      ("层级", layer_cn, ""), ("阶段", "送审待批", "")],
                     [("拟制", dri, ""), ("评审", reviewer, ""),
                      ("批准", "待负责人拍板", ""), ("日期", today(), "")])
    cells = tally([
        tc("%d<small> 条</small>" % len(crits), "完成标准"),
        tc(("%d<small> 项</small>" % len(decisions)) if decisions else "—", "已拍决策"),
        tc(("%d<small> 项</small>" % len(risks)) if risks else "—", "风险"),
        tc(esc(appetite), "投入预算 · 超时升版重审", cls="v", small=True),
    ])
    kp = keypoints("拍板要点", decisions or crits[:3])

    crit_rows = "".join(
        '<tr><td class="c">2.%d</td><td>%s</td>'
        '<td class="c"><span class="mk wait">☐ 待验</span></td></tr>'
        % (i + 1, esc(c)) for i, c in enumerate(crits))
    roles_rows = "".join(
        '<tr><td class="c">%s</td><td>%s</td></tr>' % (esc(r), esc(v))
        for r, v in [("负责人", dri), ("执行", exec_), ("协作", collab), ("评审", reviewer)])
    secs = [
        h2("1", "目标"), paras(d.get("goal")),
        h2("2", "完成标准(送审 · 待验)"),
        '<table class="formal"><tr><th style="width:44px">序号</th><th>完成标准</th>'
        '<th style="width:92px">核验</th></tr>%s</table>' % crit_rows,
        h2("3", "分工"),
        '<table class="formal"><tr><th style="width:96px">角色</th><th>承担</th></tr>%s</table>' % roles_rows,
        h2("4", "投入预算"),
        '<div class="appetite"><div class="at">预算上限</div><div class="av2">%s'
        '<small>　超时即触发升版强制重审,不带病延期。</small></div></div>' % esc(appetite),
    ]
    if _folded(d.get("approach")) or decisions or risks:
        secs.append(h2("5", "方案要点"))
        secs.append(paras(d.get("approach")))
        secs += ['<div class="dgrid"><dt>D%d</dt><dd>%s</dd></div>' % (i + 1, esc(x))
                 for i, x in enumerate(decisions)]
        secs += ['<div class="dgrid"><dt>R%d</dt><dd>%s</dd></div>' % (i + 1, esc(x))
                 for i, x in enumerate(risks)]
    doc = shell("plan", slug, slug, None, appr, cells + kp, "\n".join(secs))
    return doc, "docs/plans/plan_%s_%s.html" % (today(), slug)


def render_research(d):
    slug = d.get("slug") or "research"
    filled = _folded(d.get("findings")) > 0
    has_open = _folded(d.get("openQuestions")) > 0
    verdict = (d.get("verdict") or "").strip()
    # 裁决格缺省两态:骨架态(发现未回填)/已回填未出裁决
    vtext = verdict or ("已回填 · 裁决待对账" if filled else "调研中 · 待回填")

    appr = appr_grid("research",
                     [("文档类别", "研究报告", "t"), ("编号", slug, ""),
                      ("层级", "—", ""), ("阶段", "调研完成" if filled else "调研中", "")],
                     [("拟制", "调研子 agent", ""), ("对账", "负责人", ""),
                      ("复核", "与前轮对照", ""), ("日期", today(), "")])
    q = ('<div class="question"><div class="qt">研究问题</div><p>%s</p></div>'
         % esc((d.get("question") or "").strip()))
    cells = tally([
        tc("已填充" if filled else "待填充", "发现", small=True),
        tc("已记录" if has_open else "无", "待解问题", small=True),
        tc(esc(vtext), "总体裁决", cls="v", small=True),
    ], c3=True)
    f = d.get("findings")
    kp = keypoints("发现要点", _items(f)[:3] if isinstance(f, list) else [])

    secs = [
        h2("1", "发现"), paras(f, blank="(待 fresh session 深度调研填充)"),
        h2("2", "待解问题"), paras(d.get("openQuestions"), blank="(研究过程中浮现的开放问题)"),
    ]
    doc = shell("research", slug, slug, None, appr, q + cells + kp, "\n".join(secs))
    return doc, "docs/research/research_%s_%s.html" % (today(), slug)


def render_case(d):
    slug = d.get("slug") or "case"
    kj = d.get("keyJudgments") or []
    crs = [c for c in (d.get("criteriaResults") or []) if str(c.get("criterion") or "").strip()]
    met = sum(1 for c in crs if c.get("met"))
    rules = _items(d.get("ruleCandidates"))
    # 结论格三态(v4):全数达成 / n/m 达成 / 未提供逐项核验
    if crs and met == len(crs):
        vtext = "已收尾 · 标准全数达成"
    elif crs:
        vtext = "已收尾 · %d/%d 达成" % (met, len(crs))
    else:
        vtext = "复盘存档"

    appr = appr_grid("case",
                     [("文档类别", "复盘报告", "t"), ("编号", slug, ""),
                      ("层级", "—", ""), ("阶段", "复盘收尾", "")],
                     [("拟制", "tc-review session", ""), ("评审", "复盘评审子 agent", ""),
                      ("批准", "负责人拍板", ""), ("日期", today(), "")])
    cells = tally([
        tc(("%d<small> / %d</small>" % (met, len(crs))) if crs else "—", "完成标准"),
        tc(str(len(kj)), "关键判断"),
        tc(str(len(rules)) if rules else "—", "规则候选"),
        tc(esc(vtext), "结论", cls="v", small=True),
    ])
    kp = keypoints("要点提示", [j.get("title") for j in kj])

    crit_rows = ""
    for i, c in enumerate(crs):
        if c.get("met"):
            mark = '<span class="mk ok">✓ 达成</span>'
        else:
            reason = (c.get("notMetReason") or "").strip()
            mark = ('<span class="mk bad">× 未达成</span>%s'
                    % ((" — %s" % esc(reason)) if reason else ""))
        crit_rows += ('<tr><td class="c">3.%d</td><td>%s</td><td>%s</td></tr>'
                      % (i + 1, esc(c.get("criterion")), mark))
    crit_html = ('<table class="formal"><tr><th style="width:44px">序号</th><th>完成标准</th>'
                 '<th style="width:128px">核验结果</th></tr>%s</table>' % crit_rows
                 ) if crs else '<p class="note">(未提供逐项核验)</p>'

    j_blocks = []
    for i, j in enumerate(kj):
        rows = ""
        for label, v in [("背景", j.get("context")),
                         ("选项", " ／ ".join(_items(j.get("options")))),
                         ("选择", j.get("chose"))]:
            if str(v or "").strip():
                rows += ('<div class="jrow"><dt>%s</dt><dd>%s</dd></div>' % (esc(label), esc(v)))
        hind = ('<div class="hind"><dt>事后看 · 核心收获</dt><dd>%s</dd></div>'
                % esc(j.get("inHindsight"))) if str(j.get("inHindsight") or "").strip() else ""
        aux = ('<div class="aux"><dt>古法不可能</dt><dd>%s</dd></div>'
               % esc(j.get("ancientImpossible"))) if str(j.get("ancientImpossible") or "").strip() else ""
        j_blocks.append(
            '<div class="judge"><div class="judge-h"><span class="ji">判断%s</span>'
            '<span class="jt">%s</span></div><div class="judge-b">%s%s%s</div></div>'
            % (cn_idx(i + 1), esc(j.get("title") or "(未命名判断)"), rows, hind, aux))

    rules_html = ('<table class="formal"><tr><th>候选规则</th><th style="width:84px">状态</th></tr>%s</table>'
                  % "".join('<tr><td>%s</td><td class="c"><span class="pend">待提级</span></td></tr>'
                            % esc(r) for r in rules)) if rules else '<p class="note">(无)</p>'

    secs = [
        h2("1", "目标"), paras(d.get("goal")),
        h2("2", "实际发生"), paras(d.get("whatHappened")),
        h2("3", "完成标准核验"), crit_html,
        h2("4", "关键判断"), "\n".join(j_blocks),
        h2("5", "规则候选"), rules_html,
    ]
    doc = shell("case", slug, slug, None, appr, cells + kp, "\n".join(secs))
    return doc, "cases/%s-%s.html" % (today(), slug)


def render_handoff(d):
    slug = d.get("slug") or "handoff"
    at = d.get("at") or now_min()
    dead = _items(d.get("deadEnds"))
    pol = (d.get("pollutionSignal") or "").strip()
    na = d.get("nextAction")
    na_items = _items(na)
    n_impl = len(na_items) if isinstance(na, list) else 0

    appr = appr_grid("handoff",
                     [("文档类别", "交接单", "t"), ("编号", slug, ""),
                      ("层级", "—", ""), ("阶段", "转下一 session", "")],
                     [("移交", "本 session", ""), ("接收", "下一 session", ""),
                      ("污染信号", pol or "无 · 洁净", "warn" if pol else "ok"),
                      ("时点", at, "")])
    cells = tally([
        tc("下一 session", "接收", small=True),
        tc(("%d<small> 项</small>" % n_impl) if n_impl else "—", "实现项"),
        tc(str(len(dead)), "禁区", cls="warn" if dead else ""),
        tc("唯一输入 · 见下一步", "开工指引", cls="v", small=True),
    ])

    if na_items:
        next_body = ('<div class="lead">%s</div>' % esc(na_items[0])
                     ) + "".join("<p>%s</p>" % esc(x) for x in na_items[1:])
    else:
        next_body = '<div class="lead">(待补充)</div>'
    dead_html = ('<table class="formal"><tr><th class="danger" style="width:42px">标记</th>'
                 '<th class="danger">已证伪的路线与原因</th></tr>%s</table>'
                 % "".join('<tr><td class="c"><span class="mk bad">×</span></td><td>%s</td></tr>'
                           % esc(x) for x in dead)) if dead else '<p class="note">(无)</p>'
    archive = (
        '<div class="clause"><dt>末次提交</dt><dd><code>%s</code> · 分支 <code>%s</code></dd></div>'
        '<div class="clause"><dt>已完成</dt><dd>%s</dd></div>'
    ) % (esc(d.get("lastCommit") or "—"), esc(d.get("branch") or "—"),
         paras(d.get("done")))

    secs = [
        h2("1", "下一步(接收方照此开工)"), '<div class="next">%s</div>' % next_body,
        h2("2", "禁区(已证伪路线 · 勿重试)", danger=True), dead_html,
        h2("3", "交接时点存档"), archive,
    ]
    doc = shell("handoff", slug, slug, None, appr, cells, "\n".join(secs))
    return doc, "docs/plans/handoff_%s_%s.html" % (today(), slug)


RENDERERS = {"plan": render_plan, "research": render_research, "case": render_case, "handoff": render_handoff}


def load_transition_module():
    """scripts/ 下的 transition.py 按路径加载(不依赖 sys.path;白盒测试同款手法)。"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("tc_transition", SCRIPTS_DIR / "transition.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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


def record_gate(ok, path=GATE_COUNTS_PATH):
    """命门B 发布结果的 bare pass/fail 计数(counts-only · 隐私:不写 error 串/路径/内容)。
    best-effort:遥测绝不打断发布,任何异常吞掉。daemon 心跳读它上报命门成功率(⑪)。"""
    try:
        p = pathlib.Path(path)
        counts = {"pass": 0, "fail": 0}
        if p.exists():
            try:
                cur = json.loads(p.read_text())
                counts["pass"] = int(cur.get("pass", 0))
                counts["fail"] = int(cur.get("fail", 0))
            except Exception:
                pass  # 损坏 → 重置,绝不向上抛
        counts["pass" if ok else "fail"] += 1
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(p.suffix + ".tmp")
        tmp.write_text(json.dumps(counts))  # 只写 pass/fail 整数 —— 无 error/路径/内容
        os.replace(tmp, p)                  # 原子替换:daemon 心跳并发读不会读到半截 JSON
    except Exception:
        pass  # 遥测 best-effort,绝不打断发布


def publish(issue, doc_path, caption):
    """命门B 收口:exec `multica issue comment add --inline`,解析 JSON,自检 attachments。"""
    argv = build_publish_argv(issue, doc_path, caption)
    try:
        proc = subprocess.run(argv, capture_output=True, text=True)
    except FileNotFoundError:
        record_gate(False)
        fail("找不到 multica CLI(命门B 收口入口);先安装/更新 multica(≥v0.4.11)再发布")
    if proc.returncode != 0:
        record_gate(False)
        fail("命门B 发布失败(multica exit %d):%s"
             % (proc.returncode, (proc.stderr or proc.stdout or "").strip()[:300]))
    try:
        r = json.loads(proc.stdout)
    except Exception:
        record_gate(False)
        fail("命门B 输出非 JSON: %s" % (proc.stdout or proc.stderr or "")[:200])
    atts = r.get("attachments") or []
    if not atts:
        # 命门 自检:绑定真信号 = attachments 非空(不看 url 前缀)。脏评论需撤回。
        record_gate(False)
        fail("attachments 未绑定 → 无渲染脏评论。撤回:multica issue comment delete %s" % r.get("id"))
    record_gate(True)
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
    ap.add_argument("--no-transition", action="store_true",
                    help="发布后跳过入口状态转换(逃生口;默认自动转换)")
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
        print(json.dumps(result, ensure_ascii=False))
        return

    result.update(publish(a.issue, str(out), a.caption))
    if a.no_transition:
        result["transition"] = "skipped(--no-transition)"
        print(json.dumps(result, ensure_ascii=False))
        return

    # 入口状态转换(发布即流转 · 语义单源 = transition.py)。失败走 exit 2 契约:
    # 评论已发成功,绝不重跑 publish(会重复发评论);补救 = 幂等的 transition.py 单独调用。
    # findings 双形态:string 非空白 或 array 含 ≥1 非空白项(_folded 两者通吃)
    findings_filled = bool(a.type == "research" and _folded(data.get("findings")))
    try:
        tr = load_transition_module()
        tr.run_publish_init(a.issue, a.type, findings_filled=findings_filled)
        result["transition"] = "ok"
    except Exception as e:
        result["transition"] = "FAILED"
        print(json.dumps(result, ensure_ascii=False))
        remedy = "python3 %s publish-init %s --doc-type %s%s" % (
            SCRIPTS_DIR / "transition.py", a.issue, a.type,
            " --findings-filled" if findings_filled else "")
        print("PARTIAL · 评论已发布成功,但入口状态转换失败:%s" % e, file=sys.stderr)
        print("补救(幂等 · 绝不重跑 publish):%s" % remedy, file=sys.stderr)
        sys.exit(2)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
