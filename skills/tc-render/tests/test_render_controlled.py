#!/usr/bin/env python3
"""受控文档模版断言 · TEA-103(计划 v4)完成标准 1/2/3 的对抗验收。

覆盖:四类结构锚点 / 要点框按类型适用 / 双形态正文(anyOf)渲染与拒收 /
旧版纯 string fields 回归 / 封闭词表英文标签 / emoji 封闭码点集 / 零 rotate /
overflow-wrap 与超长字段。

跑:  python3 -m pytest skills/tc-render/tests/ -q
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent
PUBLISH_PY = SKILL_DIR / "publish.py"
STYLE_CSS = SKILL_DIR / "assets" / "style.css"

# ---- 全中文 baseline(封闭词表断言要求字段内容不携带英文标签词) ----
PLAN = {
    "goal": "把四类文档渲染换成受控文档样式并扩展字段契约的目标描述",
    "completionCriteria": ["四类渲染含结构锚点", "校验引擎支持双形态", "封闭断言三连通过"],
    "slug": "kongzhi-yangben",
    "layer": "task",
    "dri": "负责人甲",
    "reviewer": "评审子代理",
    "appetite": "一天(单次收口)",
}
_LONG = "关键判断的背景说明需要足够长" * 8
CASE = {
    "goal": "目标一句话", "whatHappened": "实际发生一句话", "slug": "kongzhi-yangben",
    "keyJudgments": [{
        "title": "判断标题甲", "context": _LONG, "options": ["甲", "乙"],
        "chose": "甲", "inHindsight": "事后看甲对", "ancientImpossible": "古法做不到",
    }],
}
RESEARCH = {"question": "核心问题一句话", "slug": "kongzhi-yangben"}
HANDOFF = {"slug": "kongzhi-yangben", "done": "已完成一句话", "nextAction": "下一步一句话"}

BASELINES = [("plan", PLAN), ("research", RESEARCH), ("case", CASE), ("handoff", HANDOFF)]


def run(doc_type, data, cwd, out="x.html"):
    data_file = Path(cwd) / "fields.json"
    data_file.write_text(json.dumps(data, ensure_ascii=False))
    cmd = [sys.executable, str(PUBLISH_PY), "--type", doc_type,
           "--data", str(data_file), "--dry-run", "--out", out]
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)


def render(doc_type, data, tmp_path):
    r = run(doc_type, data, tmp_path)
    assert r.returncode == 0, f"合法 {doc_type} 渲染失败:\n{r.stderr}"
    return (tmp_path / "x.html").read_text()


# ============ 完成标准 1 · 四类结构锚点 ============

@pytest.mark.parametrize("doc_type,data", BASELINES)
def test_controlled_doc_anchors(doc_type, data, tmp_path):
    """四类产物均含受控文档共同锚点:受控条/审批栏/方章/统计格。"""
    out = render(doc_type, data, tmp_path)
    for anchor in ('class="ctrl"', 'class="appr"', 'class="sq"', '<div class="tally'):
        assert anchor in out, f"{doc_type} 缺结构锚点 {anchor}"
    assert 'class="sheet"' in out and "受控文档" in out


def test_type_color_class_per_type(tmp_path):
    """类别主色由 body 类注入,四类各不相同。"""
    for doc_type, data in BASELINES:
        out = render(doc_type, data, tmp_path)
        assert f'<body class="t-{doc_type}">' in out, f"{doc_type} 缺类别主色 body 类"


def test_keypoints_applicability_per_type(tmp_path):
    """要点框按类型适用(v4 标准 1):计划必有(缺省降级前 3 条标准)、复盘条件渲染、
    研究仅 findings 为数组时、交接不渲染。"""
    out = render("plan", PLAN, tmp_path)
    assert 'class="keypoints"' in out and "四类渲染含结构锚点" in out, "计划要点框应降级为完成标准前 3 条"
    out = render("plan", {**PLAN, "keyDecisions": ["拍板甲", "拍板乙"]}, tmp_path)
    assert "拍板甲" in out, "计划要点框应优先取 keyDecisions"

    out = render("case", CASE, tmp_path)
    assert 'class="keypoints"' in out and "判断标题甲" in out, "复盘要点框应取判断标题"
    blank_title = {**CASE, "keyJudgments": [{**CASE["keyJudgments"][0], "title": "  "}]}
    out = render("case", blank_title, tmp_path)
    assert 'class="keypoints"' not in out, "判断标题全空时复盘要点框应整框不渲染"

    out = render("research", {**RESEARCH, "findings": ["发现甲", "发现乙", "发现丙", "发现丁"]}, tmp_path)
    kp = re.search(r'<div class="keypoints">.*?</ol></div>', out, re.S)
    assert kp and "发现丙" in kp.group(0) and "发现丁" not in kp.group(0), \
        "研究要点框应取数组 findings 前 3 条(第 4 条只出现在正文)"
    out = render("research", {**RESEARCH, "findings": "一整段发现"}, tmp_path)
    assert 'class="keypoints"' not in out, "string findings 不渲染研究要点框"

    out = render("handoff", HANDOFF, tmp_path)
    assert 'class="keypoints"' not in out, "交接不渲染要点框"


def test_case_verdict_three_states(tmp_path):
    """复盘结论格三态(v4):全数达成 / n,m 达成 / 复盘存档。"""
    crs2 = [{"criterion": "标准甲", "met": True}, {"criterion": "标准乙", "met": True}]
    out = render("case", {**CASE, "criteriaResults": crs2}, tmp_path)
    assert "已收尾 · 标准全数达成" in out and "✓ 达成" in out
    crs_part = [{"criterion": "标准甲", "met": True},
                {"criterion": "标准乙", "met": False, "notMetReason": "缺活体验证"}]
    out = render("case", {**CASE, "criteriaResults": crs_part}, tmp_path)
    assert "已收尾 · 1/2 达成" in out and "× 未达成" in out and "缺活体验证" in out
    out = render("case", CASE, tmp_path)
    assert "复盘存档" in out and "(未提供逐项核验)" in out


def test_research_verdict_default_two_states(tmp_path):
    """研究裁决格缺省两态:骨架态 / 已回填未出裁决;verdict 给定时原样。"""
    out = render("research", RESEARCH, tmp_path)
    assert "调研中 · 待回填" in out
    out = render("research", {**RESEARCH, "findings": "已有发现"}, tmp_path)
    assert "已回填 · 裁决待对账" in out
    out = render("research", {**RESEARCH, "findings": "已有发现", "verdict": "可行 · 仅一处命门"}, tmp_path)
    assert "可行 · 仅一处命门" in out


def test_handoff_tally_and_danger(tmp_path):
    """交接首屏:实现项=数组条款数(string 为「—」),禁区计数,下一步框/禁区表存在。"""
    out = render("handoff", HANDOFF, tmp_path)
    assert 'class="next"' in out and "唯一输入 · 见下一步" in out
    data = {**HANDOFF, "nextAction": ["第一步", "第二步", "第三步"], "deadEnds": ["死路甲", "死路乙"]}
    out = render("handoff", data, tmp_path)
    assert "3<small> 项</small>" in out, "实现项应=nextAction 数组条款数"
    assert ">2</div>" in out and "死路甲" in out, "禁区计数与禁区表应渲染"


# ============ 完成标准 2 · 双形态(anyOf)渲染与拒收 ============

def test_dualform_array_renders_paragraphs(tmp_path):
    """数组正文逐项渲染为段落(化解 esc 压平)。"""
    out = render("case", {**CASE, "goal": ["目标段甲", "目标段乙"]}, tmp_path)
    assert "<p>目标段甲</p>" in out and "<p>目标段乙</p>" in out
    out = render("handoff", {**HANDOFF, "done": ["完成甲", "完成乙"]}, tmp_path)
    assert "<p>完成甲</p>" in out and "<p>完成乙</p>" in out


def test_dualform_string_legacy_path(tmp_path):
    """string 正文走旧路径(单段),四类纯 string 旧 fields 全部照常通过。"""
    legacy = [
        ("plan", {**PLAN, "approach": "一整段方案"}),
        ("research", {**RESEARCH, "findings": "一整段发现", "openQuestions": "一整段待解"}),
        ("case", CASE),
        ("handoff", HANDOFF),
    ]
    for doc_type, data in legacy:
        out = render(doc_type, data, tmp_path)
        assert "<p>" in out, f"{doc_type} string 正文应渲染为段落"


@pytest.mark.parametrize("doc_type,data,what", [
    ("handoff", {**HANDOFF, "done": []}, "required×空数组"),
    ("case", {**CASE, "goal": [""]}, "required×全空白数组"),
    ("plan", {**PLAN, "approach": [123]}, "optional×类型污染"),
])
def test_dualform_adversarial_rejected(doc_type, data, what, tmp_path):
    """对抗负面三连(v4 标准 2):拒收且友好 ERROR,绝不裸 traceback。"""
    r = run(doc_type, data, tmp_path)
    assert r.returncode == 1, f"{what} 应被拒"
    assert "VALIDATION FAILED" in r.stderr, f"{what} 应报友好 ERROR"
    assert "Traceback" not in r.stderr, f"{what} 泄露裸 traceback"


# ============ 完成标准 3 · 封闭词表 / emoji 码点集 / 零 rotate ============

# 封闭词表(v4 标准 3①):旧模版全部英文界面标签 + eyebrow 大写类型词 + RPI 短语
BANNED_LABELS = [
    "Goal", "Roles", "Question", "Findings", "Last commit", "What&#x27;s done",
    "What's done", "Next action", "Dead ends", "Pollution signal",
    "DRI", "EXEC", "COLLAB", "REVIEW", "Layer", "Appetite", "Phase",
    "PLAN", "RESEARCH", "CASE", "HANDOFF", "RPI",
]
# emoji 禁集(v4 标准 3②):U+1F000–U+1FFFF 全区段 + Dingbats/杂项符号区中的 emoji 码点
BANNED_EMOJI_EXPLICIT = {0x2705, 0x274C, 0x274E, 0x2728, 0x270A, 0x270B, 0x26A0,
                         0x2B50, 0x2B55, 0x2757, 0x2753, 0x267B, 0x2614, 0x26BD}


def _strip_code(html):
    return re.sub(r"<code>.*?</code>", "", html, flags=re.S)


@pytest.mark.parametrize("doc_type,data", BASELINES)
def test_no_english_ui_labels(doc_type, data, tmp_path):
    """封闭词表零命中(code 元素豁免;fixture 字段为全中文,命中即模版残留)。"""
    out = _strip_code(render(doc_type, data, tmp_path))
    for w in BANNED_LABELS:
        assert w not in out, f"{doc_type} 残留英文界面标签:{w!r}"


@pytest.mark.parametrize("doc_type,data", BASELINES)
def test_no_emoji_codepoints(doc_type, data, tmp_path):
    """emoji 封闭码点集零命中;✓(U+2713)/×(U+00D7)等白名单字符不在禁集。"""
    out = render(doc_type, data, tmp_path)
    hits = [hex(ord(ch)) for ch in out
            if 0x1F000 <= ord(ch) <= 0x1FFFF or ord(ch) in BANNED_EMOJI_EXPLICIT]
    assert not hits, f"{doc_type} 含 emoji 码点:{hits}"


def test_check_mark_is_whitelisted_char(tmp_path):
    """对勾用 ✓(U+2713)字符着色——白名单图形字符,非 emoji、非 rotate 图元。"""
    crs = [{"criterion": "标准甲", "met": True}]
    out = render("case", {**CASE, "criteriaResults": crs}, tmp_path)
    assert "✓" in out and "✅" not in out


def test_no_rotate_anywhere(tmp_path):
    """零倾斜(v4 标准 3③):style.css 与四类渲染产物均无 transform:rotate。"""
    assert "rotate" not in STYLE_CSS.read_text(), "style.css 残留 rotate"
    for doc_type, data in BASELINES:
        assert "rotate" not in render(doc_type, data, tmp_path), f"{doc_type} 渲染产物残留 rotate"


def test_overflow_wrap_and_long_string(tmp_path):
    """溢出防护(v4 标准 1/N2):CSS 含 overflow-wrap;超长 code 串渲染通过且落于 code 容器。"""
    assert "overflow-wrap" in STYLE_CSS.read_text()
    long = "x" * 300
    out = render("handoff", {**HANDOFF, "lastCommit": long}, tmp_path)
    assert ("<code>%s</code>" % long) in out
