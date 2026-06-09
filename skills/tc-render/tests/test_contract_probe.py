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

SKILL_DIR = Path(__file__).resolve().parent.parent          # skills/tc-render
CONTRACT = SKILL_DIR / "publish-contract-v1.yaml"
_C = yaml.safe_load(CONTRACT.read_text())
MARKER = _C["inline_marker"]


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
