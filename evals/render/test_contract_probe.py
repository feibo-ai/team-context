#!/usr/bin/env python3
"""CI 探针 · 命门A 灾备契约对齐前端权威正则(TEA-89 ① 契约化灾备)。

两层:
  1) 自洽:契约样本 must_match / must_reject 与契约自身 line_pattern 一致(始终跑)。
  2) 跨仓漂移:契约 url_pattern 与前端权威 file-cards.ts:FILE_CARD_URL_PATTERN 逐字一致
     —— 两仓并置(或设 FILE_CARDS_TS)时跑;不可达则 skip(CI 并置后自动启用)。
"""
import os
import re
from pathlib import Path

import pytest
import yaml

SKILL_DIR = Path(__file__).resolve().parents[2] / "skills" / "tc-render"
CONTRACT_DOC = SKILL_DIR / "references" / "publish-contract.md"
# 机器可读契约 = publish-contract.md 内唯一的 ```yaml 代码块
_BLOCKS = re.findall(r"```yaml\n(.*?)```", CONTRACT_DOC.read_text(), re.S)
_C = yaml.safe_load(_BLOCKS[0])
MARKER = _C["inline_marker"]


def test_contract_doc_has_exactly_one_yaml_block():
    """契约块唯一性:publish-contract.md 只允许一个 yaml 代码块(探针解析锚点)。"""
    assert len(_BLOCKS) == 1, f"publish-contract.md 应恰有 1 个 yaml 代码块,现有 {len(_BLOCKS)}"
    assert _C.get("version") == 1 and "gate_b" in _C and "inline_marker" in _C


def test_contract_samples_self_consistent():
    """样本必须与契约自己的 line_pattern 自洽(防契约内部失配)。"""
    line_re = re.compile(MARKER["line_pattern"])
    for s in MARKER["samples_must_match"]:
        assert line_re.match(s), f"契约样本应匹配 line_pattern 却不匹配:{s}"
    for s in MARKER["samples_must_reject"]:
        assert not line_re.match(s), f"契约样本应被拒却匹配了(注入面!):{s}"


def test_line_pattern_embeds_url_pattern():
    """line_pattern 必须内嵌同一 url_pattern(单一事实源,不得各写各的)。"""
    assert MARKER["url_pattern"] in MARKER["line_pattern"], "line_pattern 未内嵌 url_pattern"


def _locate_file_cards():
    env = os.environ.get("FILE_CARDS_TS")
    if env and Path(env).exists():
        return Path(env)
    candidates = [
        SKILL_DIR.parents[2] / "tc-multica" / "packages/ui/markdown/file-cards.ts",
        Path.home() / "feibo/tc-multica/packages/ui/markdown/file-cards.ts",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def test_contract_aligned_to_frontend_regex():
    """跨仓漂移:契约 url_pattern 必须与前端权威 FILE_CARD_URL_PATTERN 逐字一致。"""
    fc = _locate_file_cards()
    if not fc:
        pytest.skip("file-cards.ts 不可达(设 FILE_CARDS_TS 或并置 tc-multica 后启用跨仓漂移检测)")
    src = fc.read_text()
    m = re.search(r"FILE_CARD_URL_PATTERN\s*=\s*/(.+?)/\s*$", src, re.M)
    assert m, "未能在 file-cards.ts 提取 FILE_CARD_URL_PATTERN(前端结构变了?)"
    frontend = m.group(1)
    assert frontend == MARKER["url_pattern"], (
        "契约 url_pattern 与前端权威漂移 —— 命门A 灾备可能渲染失败:\n"
        f"  contract = {MARKER['url_pattern']!r}\n  frontend = {frontend!r}\n"
        f"  (源:{fc})")


def test_frontend_regex_accepts_real_inline_url():
    """端到端方向:前端正则确实接受契约样本的真实内联 url(并拒注入)。"""
    fc = _locate_file_cards()
    if not fc:
        pytest.skip("file-cards.ts 不可达")
    src = fc.read_text()
    m = re.search(r"FILE_CARD_URL_PATTERN\s*=\s*/(.+?)/\s*$", src, re.M)
    assert m
    url_re = re.compile("^(?:%s)$" % m.group(1))
    assert url_re.match("/uploads/workspaces/abc/plan.html"), "前端正则不接受合法 /uploads url"
    assert url_re.match("https://multica-static.example.ai/case.html"), "前端正则不接受合法 https url"
    assert not url_re.match("javascript:alert(1)"), "前端正则误收协议注入 url"


# ======================================================================
# transition.py 依赖的 CLI JSON 形状探针(防 multica 升版静默漂移)。
# 可达性同上层模式:CLI 不在/未登录则 skip,CI/本机并置时自动启用。
# ======================================================================
import json
import shutil
import subprocess


def _cli_json(argv):
    if not shutil.which("multica"):
        pytest.skip("multica CLI 不可达")
    p = subprocess.run(argv, capture_output=True, text=True)
    if p.returncode != 0:
        pytest.skip(f"multica 不可用(未登录/网络?):{(p.stderr or p.stdout)[:120]}")
    return json.loads(p.stdout)


def test_probe_label_list_shape():
    """transition.py 依赖:label list = [{id, name, ...}](name→UUID 运行时解析的根基)。"""
    rows = _cli_json(["multica", "label", "list", "--output", "json"])
    assert isinstance(rows, list) and rows, "label list 形状漂移:应为非空数组"
    assert all("id" in r and "name" in r for r in rows), "label list 行缺 id/name 键"


def test_probe_issue_list_and_get_shape():
    """transition.py 依赖:issue get 含 status/labels[{name}]/parent_issue_id;list 分页含 has_more。"""
    page = _cli_json(["multica", "issue", "list", "--limit", "1", "--output", "json"])
    assert "issues" in page and "has_more" in page, "issue list 分页形状漂移(invariants 巡检依赖 has_more)"
    if not page["issues"]:
        pytest.skip("workspace 无 issue")
    ref = page["issues"][0]["id"]
    d = _cli_json(["multica", "issue", "get", ref, "--output", "json"])
    for key in ("status", "labels", "parent_issue_id", "identifier"):
        assert key in d, f"issue get 缺 {key} 键(transition.py 决策输入)"
    assert isinstance(d["labels"], list)
    assert all("name" in l for l in d["labels"]), "issue get labels 行缺 name"
