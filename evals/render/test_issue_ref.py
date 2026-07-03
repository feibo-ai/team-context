"""test_issue_ref.py — publish.py 的 issue 引用运行时解析(key/前缀 → 完整 UUID)。

命门不变式:进 API 的一律完整 UUID;非 UUID 输入必须解析成功才继续,
解析失败/输出可疑 → exit 1,绝不带着可疑引用发布。
用假 multica(PATH 前置)驱动,不触网。
"""
import importlib.util
import json
import os
import stat
import subprocess
import sys
from pathlib import Path

RENDER = Path(__file__).resolve().parent.parent.parent / "skills/tc-render/scripts"
PUBLISH_PY = RENDER / "publish.py"
GOOD_UUID = "12345678-abcd-4ef0-9876-543210fedcba"


def _load():
    spec = importlib.util.spec_from_file_location("tc_publish_ref", PUBLISH_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _fake_multica(tmp_path, body):
    """写一个假 multica 可执行到 tmp bin,返回带 PATH 前置的 env。"""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    exe = bin_dir / "multica"
    exe.write_text("#!/bin/sh\n" + body + "\n")
    exe.chmod(exe.stat().st_mode | stat.S_IEXEC)
    env = dict(os.environ)
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    return env


def test_resolve_key_to_uuid(tmp_path, monkeypatch):
    env = _fake_multica(tmp_path, f"echo '{{\"id\": \"{GOOD_UUID}\", \"key\": \"TEA-88\"}}'")
    monkeypatch.setenv("PATH", env["PATH"])
    mod = _load()
    assert mod.resolve_issue_ref("TEA-88") == GOOD_UUID


def test_resolve_failure_exits_1(tmp_path, monkeypatch):
    env = _fake_multica(tmp_path, "echo 'no issue found' >&2; exit 1")
    monkeypatch.setenv("PATH", env["PATH"])
    mod = _load()
    try:
        mod.resolve_issue_ref("TEA-404")
        raise AssertionError("解析失败必须硬失败")
    except SystemExit as e:
        assert e.code == 1


def test_resolve_non_uuid_id_rejected(tmp_path, monkeypatch):
    # 服务端返回的 id 本身不是 UUID(数据异常)→ 拒绝,命门不放行可疑值
    env = _fake_multica(tmp_path, "echo '{\"id\": \"short-id\"}'")
    monkeypatch.setenv("PATH", env["PATH"])
    mod = _load()
    try:
        mod.resolve_issue_ref("TEA-9")
        raise AssertionError("非 UUID 解析结果必须被拒")
    except SystemExit as e:
        assert e.code == 1


def test_main_resolves_key_before_publish(tmp_path):
    """端到端:--issue TEA-9 非 UUID → main 先解析;假 multica 让 comment add 失败,
    断言解析确实发生(stderr 有解析回显)且失败发生在发布阶段而非引用校验阶段。"""
    fields = tmp_path / "fields.json"
    fields.write_text(json.dumps({
        "goal": "目标至少十个字符长度够", "completionCriteria": ["c1"],
        "appetite": "a", "slug": "ref-e2e", "layer": "task",
    }, ensure_ascii=False))
    body = (
        'case "$1 $2" in\n'
        f'  "issue show") echo \'{{"id": "{GOOD_UUID}"}}\' ;;\n'
        '  *) echo "publish blocked by fake" >&2; exit 7 ;;\n'
        'esac'
    )
    env = _fake_multica(tmp_path, body)
    r = subprocess.run(
        [sys.executable, str(PUBLISH_PY), "--type", "plan", "--data", str(fields),
         "--issue", "TEA-9", "--out", "ref-e2e.html"],
        cwd=str(tmp_path), capture_output=True, text=True, env=env,
    )
    assert "issue 引用已解析:TEA-9 → " + GOOD_UUID in r.stderr, r.stderr
    assert r.returncode == 1  # 失败点在命门B 发布(假 CLI exit 7),不是引用校验
    assert "命门B 发布失败" in r.stderr


def test_dry_run_skips_resolution(tmp_path):
    """--dry-run 不触 CLI:PATH 里根本没有 multica 也必须成功。"""
    fields = tmp_path / "fields.json"
    fields.write_text(json.dumps({
        "goal": "目标至少十个字符长度够", "completionCriteria": ["c1"],
        "appetite": "a", "slug": "ref-dry", "layer": "task",
    }, ensure_ascii=False))
    env = dict(os.environ)
    env["PATH"] = str(tmp_path / "empty-bin")
    (tmp_path / "empty-bin").mkdir()
    r = subprocess.run(
        [sys.executable, str(PUBLISH_PY), "--type", "plan", "--data", str(fields),
         "--issue", "TEA-9", "--dry-run", "--out", "ref-dry.html"],
        cwd=str(tmp_path), capture_output=True, text=True, env=env,
    )
    assert r.returncode == 0, r.stderr
