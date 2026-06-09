#!/usr/bin/env python3
"""对抗测试 · tc-render publish.py 硬校验 + red-team(TEA-89 批次1 ①②③⑦)。

净损失(校验强度)用**对抗输入**证明,不是 grep:每条喂一个攻击/畸形输入,
断言 publish.py 拒绝(exit 1)。RED→GREEN:对当前 publish.py 多数应 FAIL,
实现收口/schema/red-team 后转 PASS。

跑:  python3 -m pytest skills/tc-render/tests/ -q
"""
import importlib.util
import inspect
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent          # skills/tc-render
SKILLS_ROOT = SKILL_DIR.parent                               # skills/
PUBLISH_PY = SKILL_DIR / "publish.py"
CONFIG_PATH = Path.home() / ".multica" / "config.json"

# ---- baselines:刚好合法,改一处就该被拒(隔离变量) ----
VALID_PLAN = {
    "goal": "完成 dropmcp Phase 1 收口并验证四类文档发布无第二路径",
    "completionCriteria": ["命门B 收口", "schema 消魔数"],
    "slug": "redteam-baseline",
    "layer": "project",
}
# case section4 合计 ≥100 真字符(用乘法构造,确定性地越过下限,不靠手数边界)
_LONG = "关键判断的背景说明需要足够长" * 8   # 14 字 × 8 = 112 ≥ 100
VALID_CASE = {
    "goal": "g", "whatHappened": "w", "slug": "redteam-baseline",
    "keyJudgments": [{
        "title": "判断一", "context": _LONG, "options": ["A", "B"],
        "chose": "A", "inHindsight": "事后看 A 对", "ancientImpossible": "古法做不到",
    }],
}


def run(doc_type, data, extra=None, cwd=None, raw=None):
    """--dry-run 调 publish.py(不触网),返回 CompletedProcess。

    data: dict 写成 fields.json;raw: 原样写入(测坏 JSON)。
    cwd:  工作目录(测 --out 路径白名单时用临时目录当允许根)。
    """
    cwd = Path(cwd)
    data_file = cwd / "fields.json"
    data_file.write_text(raw if raw is not None else json.dumps(data, ensure_ascii=False))
    cmd = [sys.executable, str(PUBLISH_PY), "--type", doc_type,
           "--data", str(data_file), "--dry-run", *(extra or [])]
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)


def load_publish_module():
    """白盒:把 publish.py 当模块导入(main() 在 __main__ 守卫内,不会跑)。"""
    spec = importlib.util.spec_from_file_location("tc_publish", PUBLISH_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ============ 正路冒烟:合法输入必须过(GREEN 不能误杀) ============

def test_valid_plan_passes(tmp_path):
    r = run("plan", VALID_PLAN, ["--out", "ok.html"], cwd=tmp_path)
    assert r.returncode == 0, f"合法 plan 不该被拒\nSTDERR:{r.stderr}"


def test_valid_case_passes(tmp_path):
    r = run("case", VALID_CASE, ["--out", "ok.html"], cwd=tmp_path)
    assert r.returncode == 0, f"合法 case 不该被拒\nSTDERR:{r.stderr}"


# ============ ② schema 消魔数:拼错 key / 类型混淆 / 纯空格占位 ============

def test_unknown_key_rejected(tmp_path):
    """additionalProperties:false —— 多一个未知键(含拼错的可选字段)即拒。"""
    bad = {**VALID_PLAN, "aproach": "拼错的 approach,当前被静默吞掉"}
    r = run("plan", bad, ["--out", "x.html"], cwd=tmp_path)
    assert r.returncode == 1, "拼错/多余 key 应被 additionalProperties:false 拒(当前静默吞)"


def test_type_confusion_string_as_list_rejected(tmp_path):
    """completionCriteria 必须是数组;给字符串当前被逐字符当成多条标准。"""
    bad = {**VALID_PLAN, "completionCriteria": "abcdefghij"}
    r = run("plan", bad, ["--out", "x.html"], cwd=tmp_path)
    assert r.returncode == 1, "字符串冒充数组应被类型断言拒(当前逐字符=10条)"


def test_whitespace_padding_rejected(tmp_path):
    """纯空格占位:case section4 用空白把字符数撑过 100，应折叠空白后判空被拒。"""
    pad = " " * 60
    bad = {"goal": "g", "whatHappened": "w", "slug": "ws",
           "keyJudgments": [{"title": pad, "context": pad, "options": [],
                             "chose": pad, "inHindsight": pad, "ancientImpossible": pad}]}
    r = run("case", bad, ["--out", "x.html"], cwd=tmp_path)
    assert r.returncode == 1, "空白占位应在折叠空白后判空被拒(当前 len 计原始空格=过)"


def test_threshold_from_schema_not_magic(tmp_path):
    """阈值派生自 schema(plan goal minLength)——边界恰好不达标即拒,且非硬编码 10。"""
    bad = {**VALID_PLAN, "goal": "短"}   # 1 字符,任何合理下限都不达标
    r = run("plan", bad, ["--out", "x.html"], cwd=tmp_path)
    assert r.returncode == 1, "goal 过短应被 schema 派生阈值拒"


# ============ ⑦ red-team 四项 ============

def test_redteam_out_relative_traversal_rejected(tmp_path):
    """--out 路径白名单:../ 越权写出允许根之外应拒。"""
    r = run("plan", VALID_PLAN, ["--out", "../escape.html"], cwd=tmp_path)
    assert r.returncode == 1, "--out ../escape.html 应被路径白名单拒(当前可越权写)"
    assert not (tmp_path.parent / "escape.html").exists(), "越权文件不该被写出"


def test_redteam_out_absolute_escape_rejected(tmp_path):
    """--out 绝对路径逃逸允许根应拒。"""
    target = tmp_path.parent / "abs_escape.html"
    r = run("plan", VALID_PLAN, ["--out", str(target)], cwd=tmp_path)
    assert r.returncode == 1, "--out 绝对逃逸路径应被拒"
    assert not target.exists(), "越权文件不该被写出"


def test_redteam_slug_traversal_rejected(tmp_path):
    """slug 注入 ../ 经默认路径模板逃逸应拒。"""
    bad = {**VALID_PLAN, "slug": "../../evil"}
    r = run("plan", bad, cwd=tmp_path)   # 不给 --out,走默认路径模板
    assert r.returncode == 1, "slug=../../evil 应被拒(当前经默认路径越权)"


def test_redteam_bad_json_friendly_no_traceback(tmp_path):
    """坏 JSON → 友好 ERROR,不泄露裸 Python traceback。"""
    r = run("plan", None, ["--out", "x.html"], cwd=tmp_path, raw="{ not valid json,,, ")
    assert r.returncode != 0, "坏 JSON 应失败"
    assert "Traceback" not in r.stderr, "不该泄露裸 traceback(应友好 ERROR)"
    assert "json.decoder" not in r.stderr, "不该泄露 json.decoder 栈帧"


def test_redteam_missing_data_file_friendly(tmp_path):
    """--data 指向不存在文件 → 友好 ERROR,不泄露 FileNotFoundError traceback。"""
    cmd = [sys.executable, str(PUBLISH_PY), "--type", "plan",
           "--data", str(tmp_path / "nope.json"), "--dry-run", "--out", "x.html"]
    r = subprocess.run(cmd, cwd=str(tmp_path), capture_output=True, text=True)
    assert r.returncode != 0
    assert "Traceback" not in r.stderr, "缺文件应友好报错,不泄露裸 traceback"


def test_redteam_mime_non_html_out_rejected(tmp_path):
    """--inline 非 text/html:--out 落到非 .html 后缀应被 MIME/扩展名守卫拒。"""
    r = run("plan", VALID_PLAN, ["--out", "doc.txt"], cwd=tmp_path)
    assert r.returncode == 1, "非 .html 输出应被 MIME 守卫拒(命门B --inline 只收 text/html)"


# ============ ⑦ token 移出 argv + ① 命门B 收口(白盒:发布 argv 是纯函数) ============

def test_publish_argv_is_gate_b_cli():
    """① 命门B:发布走 `multica issue comment add <issue> --inline <doc>`,不再 raw curl。"""
    mod = load_publish_module()
    builder = getattr(mod, "build_publish_argv", None)
    assert builder is not None, "应存在纯函数 build_publish_argv(便于断言 argv 无密钥)"
    argv = builder("11111111-1111-1111-1111-111111111111", "/tmp/doc.html", "cap")
    assert argv[:5] == ["multica", "issue", "comment", "add",
                        "11111111-1111-1111-1111-111111111111"], f"非命门B 收口入口:{argv[:6]}"
    assert "--inline" in argv, "命门B 必须用 --inline 内联发布"
    assert not any("curl" in str(a) for a in argv), "命门B 不该再 shell curl"


def test_redteam_token_never_in_argv():
    """token 移出 argv:发布命令行不含任何凭据(当前 raw curl 把 Bearer token 放 argv → ps 可见)。"""
    mod = load_publish_module()
    builder = getattr(mod, "build_publish_argv", None)
    assert builder is not None, "需 build_publish_argv 才能断言 argv 无 token"
    argv = builder("11111111-1111-1111-1111-111111111111", "/tmp/doc.html", "cap")
    joined = " ".join(map(str, argv))
    assert "Authorization" not in joined and "Bearer" not in joined, "argv 不该含 Authorization/Bearer"
    if CONFIG_PATH.exists():
        tok = json.loads(CONFIG_PATH.read_text()).get("token", "")
        if tok:
            assert tok not in joined, "真实 token 绝不该出现在发布命令 argv"


# ============ ③ 无旁路 + ① 无第二发布路径(结构守卫) ============

DOC_SKILLS = ["tc-2-research", "tc-3-plan", "tc-5-review", "tc-handoff"]


def test_no_handoff_markdown_bypass():
    """③:tc-handoff 不得文档化绕过 publish.py 硬校验的『快捷 markdown』入口。"""
    txt = (SKILLS_ROOT / "tc-handoff" / "SKILL.md").read_text()
    assert "--content-file" not in txt, "tc-handoff 仍有 --content-file 旁路(绕过 publish.py 硬校验)"
    assert "快捷=纯 markdown" not in txt, "tc-handoff 仍有『快捷=纯 markdown』旁路口"


def test_no_second_publish_path_in_doc_skills():
    """①:四类文档 skill 正文不得有第二条发布路径(裸 curl 打 /api/issues 评论)。"""
    offenders = []
    for s in DOC_SKILLS:
        p = SKILLS_ROOT / s / "SKILL.md"
        if p.exists() and "/api/issues/" in p.read_text():
            offenders.append(s)
    assert not offenders, f"这些 skill 仍含裸 /api/issues 发布路径:{offenders}"


def test_publish_md_no_raw_curl_bypass():
    """①:PUBLISH.md 删除 §2 可执行的 raw-HTTP runbook(绕过 publish.py 硬校验的旁路)。

    查的是**可执行的 curl 命令签名**,不是禁词 —— 散文里『不要手拼 curl』这类禁令措辞允许。
    """
    txt = (SKILL_DIR / "PUBLISH.md").read_text()
    assert "curl -" not in txt, "PUBLISH.md 仍含可执行 curl 命令(疑似 §2 手跑 raw-HTTP 旁路未删)"
    assert "/api/upload-file" not in txt, "PUBLISH.md 仍含裸 upload 端点 runbook(旁路)"


# ============ 评审补充:对抗盲区(②③⑦ 的守卫此前正确但无测试) ============

def test_empty_array_rejected_plan(tmp_path):
    """②minItems:completionCriteria:[] 应被拒(原无测试 · mutation 关掉 minItems 也全绿)。"""
    r = run("plan", {**VALID_PLAN, "completionCriteria": []}, ["--out", "x.html"], cwd=tmp_path)
    assert r.returncode == 1, "completionCriteria:[] 应被 schema.minItems 拒"


def test_all_whitespace_items_rejected_plan(tmp_path):
    """②:完成标准全是空白项 → 折叠后非空项=0,应被拒。"""
    r = run("plan", {**VALID_PLAN, "completionCriteria": ["  ", "\t", "　"]}, ["--out", "x.html"], cwd=tmp_path)
    assert r.returncode == 1, "全空白项 completionCriteria 应按『非空项』计数被拒"


def test_empty_keyjudgments_rejected_case(tmp_path):
    """②minItems:case keyJudgments:[] 应被拒。"""
    r = run("case", {**VALID_CASE, "keyJudgments": []}, ["--out", "x.html"], cwd=tmp_path)
    assert r.returncode == 1, "keyJudgments:[] 应被 schema.minItems 拒"


def test_required_blank_slug_rejected(tmp_path):
    """②required-非空:slug 空串/纯空格应被拒(用 slug 当探针 · goal 会被 minLength 顺手挡住测不到此分支)。"""
    for bad in ["", "   "]:
        r = run("plan", {**VALID_PLAN, "slug": bad}, ["--out", "x.html"], cwd=tmp_path)
        assert r.returncode == 1, f"slug={bad!r} 应被 required-非空 拒"


def test_required_null_goal_rejected(tmp_path):
    """②required:goal:null 应被拒。"""
    r = run("plan", {**VALID_PLAN, "goal": None}, ["--out", "x.html"], cwd=tmp_path)
    assert r.returncode == 1, "goal:null 应被 required 拒"


def test_nested_criterion_missing_required(tmp_path):
    """②嵌套 required:criteriaResults 项缺 criterion 应被拒。"""
    bad = {**VALID_CASE, "criteriaResults": [{"met": True}]}
    r = run("case", bad, ["--out", "x.html"], cwd=tmp_path)
    assert r.returncode == 1, "criteriaResults 项缺 criterion 应被嵌套 required 拒"


def test_nested_keyjudgment_unknown_key(tmp_path):
    """②嵌套 additionalProperties:false:keyJudgment 拼错键应被拒。"""
    kj = dict(VALID_CASE["keyJudgments"][0])
    kj["ctx_typo"] = "拼错的键"
    r = run("case", {**VALID_CASE, "keyJudgments": [kj]}, ["--out", "x.html"], cwd=tmp_path)
    assert r.returncode == 1, "keyJudgment 拼错键应被嵌套 additionalProperties:false 拒"


def test_zero_width_padding_rejected_case(tmp_path):
    """②折叠空白:零宽字符(U+200B,非 str.isspace)占位应被剔除后判空拒。"""
    zw = "\u200b" * 60
    bad = {"goal": "g", "whatHappened": "w", "slug": "zw",
           "keyJudgments": [{"title": zw, "context": zw, "options": [],
                             "chose": zw, "inHindsight": zw, "ancientImpossible": zw}]}
    r = run("case", bad, ["--out", "x.html"], cwd=tmp_path)
    assert r.returncode == 1, "零宽字符占位应被 _ZERO_WIDTH 剔除后判空拒"


def test_xss_fields_escaped_in_rendered_html(tmp_path):
    """⑦XSS:用户字段注入的 <script> 必须在渲染 HTML 中被转义(发布到富文本评论的安全属性)。"""
    payload = "<script>alert(1)</script>"
    data = {**VALID_PLAN, "goal": payload + " 这是合法长度的目标描述补足下限", "dri": payload}
    r = run("plan", data, ["--out", "x.html"], cwd=tmp_path)
    assert r.returncode == 0, f"注入字段不该让合法 plan 失败\n{r.stderr}"
    out = (tmp_path / "x.html").read_text()
    assert "<script>alert(1)</script>" not in out, "原始 <script> 未转义 → 富文本评论 XSS"
    assert "&lt;script&gt;" in out, "应转义为 &lt;script&gt;"


def test_caption_is_single_argv_element_no_shell():
    """⑦:caption 作单个 argv 元素传入(subprocess 列表形式 · 无 shell=True),注入无效。"""
    mod = load_publish_module()
    evil = "; rm -rf ~ #"
    argv = mod.build_publish_argv("11111111-1111-1111-1111-111111111111", "/tmp/d.html", evil)
    assert evil in argv, "caption 应原样作为单个 argv 元素(不被 shell 拆解)"
    assert argv[argv.index(evil) - 1] == "--content", "caption 应紧跟 --content 作其值"


def test_unicode_slug_rejected(tmp_path):
    """⑦:ASCII-only SLUG_RE 拒 unicode / RTL override / 斜杠 / 换行(阻断路径穿越 · 显式化是有意为之)。"""
    for bad in ["计划", "plan\u202e", "a/b", "a\nb"]:
        r = run("plan", {**VALID_PLAN, "slug": bad}, ["--out", "x.html"], cwd=tmp_path)
        assert r.returncode == 1, f"slug={bad!r} 应被 ASCII-only SLUG_RE 拒"


def test_single_publish_path_white_box():
    """①单一发布路径(代码级证据,非文档 grep):publish.py 不引入第二出网客户端,
    唯一发布出口是命门B `multica` 子进程。"""
    src = PUBLISH_PY.read_text()
    for lib in ("import urllib", "from urllib", "import requests", "import http.client",
                "import httplib", "import socket", "from http"):
        assert lib not in src, f"publish.py 引入了疑似第二出网路径:{lib!r}"
    mod = load_publish_module()
    argv = mod.build_publish_argv("11111111-1111-1111-1111-111111111111", "/tmp/d.html", "cap")
    assert argv[0] == "multica", "唯一发布出口应是 multica CLI 子进程"


def _read_keys(src, var):
    """从 renderer 源码抽取 var.get("K") 与 var["K"] 读取的 key。"""
    keys = set(re.findall(r'%s\.get\(["\']([^"\']+)["\']' % var, src))
    keys |= set(re.findall(r'%s\[["\']([^"\']+)["\']\]' % var, src))
    return keys


def test_schema_covers_all_renderer_read_keys():
    """②防雷(C6):每个 renderer 实读的 key 必须在 SCHEMAS 里 —— 否则
    additionalProperties:false 会**静默拒掉**用到该字段的合法文档。把手工不变量自动化。"""
    mod = load_publish_module()
    for typ, fname in [("plan", "render_plan"), ("research", "render_research"),
                       ("case", "render_case"), ("handoff", "render_handoff")]:
        src = inspect.getsource(getattr(mod, fname))
        missing = _read_keys(src, "d") - set(mod.SCHEMAS[typ]["properties"])
        assert not missing, f"{fname} 读取了不在 SCHEMAS[{typ}] 的 key:{missing}(会被 additionalProperties:false 误杀)"
    # 嵌套:render_case 读 keyJudgment(j)与 criteriaResult(c)子字段
    case_src = inspect.getsource(mod.render_case)
    kj = set(mod.SCHEMAS["case"]["properties"]["keyJudgments"]["items"]["properties"])
    cr = set(mod.SCHEMAS["case"]["properties"]["criteriaResults"]["items"]["properties"])
    assert _read_keys(case_src, "j") <= kj, f"keyJudgment 子字段越出 schema:{_read_keys(case_src, 'j') - kj}"
    assert _read_keys(case_src, "c") <= cr, f"criteriaResult 子字段越出 schema:{_read_keys(case_src, 'c') - cr}"
