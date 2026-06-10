#!/usr/bin/env python3
"""publish.py × transition.py 入口转换钩子测试(白盒 monkeypatch,不触网)。

契约:0 全成功 · 1 校验/发布失败 · 2 评论已发但转换失败(绝不重跑 publish,
stderr 给幂等补救命令)。--dry-run / --no-transition 均不触发转换。
"""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent
PUBLISH_PY = SKILL_DIR / "publish.py"
ISSUE = "e73befca-883b-421c-8b06-3a298da3675f"

VALID_PLAN = {
    "goal": "测试入口转换钩子的最小合法 plan 字段",
    "completionCriteria": ["钩子按契约触发"],
    "slug": "hook-test",
}
VALID_RESEARCH_FILLED = {"question": "q", "slug": "hook-test", "findings": "已有实质发现"}
VALID_RESEARCH_SKELETON = {"question": "q", "slug": "hook-test"}


def load_publish():
    spec = importlib.util.spec_from_file_location("tc_publish_hook", PUBLISH_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FakeTransition:
    """替身 transition 模块:记录 run_publish_init 调用,可注入失败。"""
    def __init__(self, raise_err=None):
        self.calls = []
        self.raise_err = raise_err

    def run_publish_init(self, issue, doc_type, findings_filled=False, **kw):
        self.calls.append((issue, doc_type, findings_filled))
        if self.raise_err:
            raise self.raise_err


def run_main(mod, monkeypatch, tmp_path, data, argv_extra, fake_tr=None, publish_ok=True):
    data_file = tmp_path / "fields.json"
    data_file.write_text(json.dumps(data, ensure_ascii=False))
    monkeypatch.chdir(tmp_path)
    if publish_ok:
        monkeypatch.setattr(mod, "publish",
                            lambda issue, doc, cap: {"comment_id": "c1", "attachment_id": "a1", "url": "/u"})
    if fake_tr is not None:
        monkeypatch.setattr(mod, "load_transition_module", lambda: fake_tr)
    else:
        def boom():
            raise AssertionError("此路径不应触发转换")
        monkeypatch.setattr(mod, "load_transition_module", boom)
    monkeypatch.setattr(sys, "argv",
                        ["publish.py", "--type", argv_extra.get("type", "plan"),
                         "--data", str(data_file), "--out", "o.html",
                         *argv_extra.get("flags", [])])
    mod.main()


def test_transition_ok_path(monkeypatch, tmp_path, capsys):
    mod, tr = load_publish(), FakeTransition()
    run_main(mod, monkeypatch, tmp_path, VALID_PLAN,
             {"flags": ["--issue", ISSUE]}, fake_tr=tr)
    assert tr.calls == [(ISSUE, "plan", False)]
    assert json.loads(capsys.readouterr().out)["transition"] == "ok"


def test_research_findings_filled_detection(monkeypatch, tmp_path, capsys):
    mod, tr = load_publish(), FakeTransition()
    run_main(mod, monkeypatch, tmp_path, VALID_RESEARCH_FILLED,
             {"type": "research", "flags": ["--issue", ISSUE]}, fake_tr=tr)
    assert tr.calls == [(ISSUE, "research", True)]
    mod2, tr2 = load_publish(), FakeTransition()
    run_main(mod2, monkeypatch, tmp_path, VALID_RESEARCH_SKELETON,
             {"type": "research", "flags": ["--issue", ISSUE]}, fake_tr=tr2)
    assert tr2.calls == [(ISSUE, "research", False)]  # 骨架占位 ≠ 发现已交付


def test_exit2_contract_on_transition_failure(monkeypatch, tmp_path, capsys):
    """评论已发 + 转换失败 → exit 2(≠1),stdout 出结果 JSON,stderr 给幂等补救并禁止重跑 publish。"""
    mod = load_publish()
    tr = FakeTransition(raise_err=RuntimeError("workspace 缺 label"))
    with pytest.raises(SystemExit) as ei:
        run_main(mod, monkeypatch, tmp_path, VALID_PLAN,
                 {"flags": ["--issue", ISSUE]}, fake_tr=tr)
    assert ei.value.code == 2
    out, err = capsys.readouterr()
    assert json.loads(out)["transition"] == "FAILED"
    assert json.loads(out)["comment_id"] == "c1"  # 评论确已发出,结果不吞
    assert "绝不重跑 publish" in err and "publish-init" in err and ISSUE in err


def test_no_transition_flag_skips(monkeypatch, tmp_path, capsys):
    mod = load_publish()
    run_main(mod, monkeypatch, tmp_path, VALID_PLAN,
             {"flags": ["--issue", ISSUE, "--no-transition"]}, fake_tr=None)
    assert "skipped" in json.loads(capsys.readouterr().out)["transition"]


def test_dry_run_never_transitions(monkeypatch, tmp_path, capsys):
    mod = load_publish()
    run_main(mod, monkeypatch, tmp_path, VALID_PLAN,
             {"flags": ["--dry-run"]}, fake_tr=None, publish_ok=False)
    out = json.loads(capsys.readouterr().out)
    assert out.get("dry_run") is True and "transition" not in out
