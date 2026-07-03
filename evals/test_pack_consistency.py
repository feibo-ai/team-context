"""test_pack_consistency.py — 包级"脚本↔文档↔用例"对账（防单一真相漂移的自动化）。

守护的不变量:
  1. create-labels.sh 内嵌的 label 名/色 == tc-render/references/issue-label-state-rules.md 字典
  2. tc-ops/scripts/issue_invariants.py 引用的每个 label 都在字典里（脚本↔文档不脱钩）
  3. evals/routing-cases.yaml 的 expect/chain 目标全部是包内 skill
  4. routing-cases.yaml 用例数 == tc-router real-user-prompts.md 语料行数（生成物不悄悄落后）
  5. transition.py 的子命令集合 == publish-contract.md 语义表列出的子命令（数量漂移曾发生两次）
"""
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOC = REPO / "skills/tc-render/references/issue-label-state-rules.md"
SH = REPO / "scripts/create-labels.sh"


def _doc_labels():
    """字典表行: | `标签名` | `#hex` 色 | ..."""
    rows = re.findall(r"^\|\s*`([^`]+)`\s*\|\s*`(#[0-9a-fA-F]{6})`", DOC.read_text(), re.M)
    return dict(rows)


def _script_labels():
    text = SH.read_text()
    names = re.search(r"NAMES=\((.*?)\)", text, re.S).group(1).split()
    colors = re.findall(r'"(#[0-9a-fA-F]{6})"', re.search(r"COLORS=\((.*?)\)", text, re.S).group(1))
    return dict(zip(names, colors))


def test_labels_script_matches_doc():
    doc, script = _doc_labels(), _script_labels()
    assert set(script) == set(doc), (
        f"label 集漂移: 仅脚本有 {set(script) - set(doc)} · 仅文档有 {set(doc) - set(script)}"
    )
    diff = {n: (script[n], doc[n]) for n in script if script[n].lower() != doc[n].lower()}
    assert not diff, f"label 颜色漂移(脚本, 文档): {diff}"


def test_issue_invariants_labels_exist_in_doc():
    src = (REPO / "skills/tc-ops/scripts/issue_invariants.py").read_text()
    used = set(re.findall(r"[\"']((?:计划|设计|复盘)-[一-鿿]+|研究)[\"']", src))
    assert used, "issue_invariants.py 未解析出任何 label 引用(解析正则失效?)"
    unknown = used - set(_doc_labels())
    assert not unknown, f"issue_invariants.py 用了字典外的 label: {unknown}"


def _pack_names():
    return {d.name for d in (REPO / "skills").iterdir() if d.is_dir()}


def test_routing_cases_targets_in_pack():
    text = (REPO / "evals/routing-cases.yaml").read_text()
    names = _pack_names()
    targets = set(re.findall(r"^\s+expect:\s*(\S+)", text, re.M))
    for t in re.findall(r'^\s+chain:\s*"([^"]+)"', text, re.M):
        targets.update(x.strip() for x in re.split(r"[→>]", t))
    unknown = {t for t in targets if t.startswith("tc-")} - names
    assert not unknown, f"routing-cases.yaml 指向包外 skill: {unknown}"


def test_routing_cases_count_matches_corpus():
    corpus = (REPO / "skills/tc-router/references/real-user-prompts.md").read_text()
    corpus_rows = len(re.findall(r"^\|\s*\d+\s*\|", corpus, re.M))
    cases = len(re.findall(r"^\s+- utterance:", (REPO / "evals/routing-cases.yaml").read_text(), re.M))
    assert corpus_rows == cases, (
        f"语料 {corpus_rows} 行 vs routing-cases {cases} 条 — 生成物落后,重跑生成"
    )


def test_transition_subcommands_match_contract():
    out = subprocess.run(
        [sys.executable, str(REPO / "skills/tc-render/scripts/transition.py"), "--help"],
        capture_output=True, text=True,
    )
    # argparse 会把 {a,b,c} 折行 → 去掉空白再抽取
    help_text = re.sub(r"\s+", "", out.stdout + out.stderr)
    m = re.search(r"\{([a-z0-9,\-]+)\}", help_text)
    assert m, f"transition.py --help 未列出子命令: {out.stderr[:200]}"
    actual = set(m.group(1).split(","))
    assert len(actual) >= 9, f"子命令解析异常(只有 {len(actual)} 个): {actual}"
    contract = (REPO / "skills/tc-render/references/publish-contract.md").read_text()
    missing = {s for s in actual if not re.search(rf"`{re.escape(s)}\b", contract)}
    assert not missing, f"transition.py 有子命令未在 publish-contract.md 记录语义: {missing}"
