#!/usr/bin/env python3
"""transition.py 测试 · mock CLI runner(FakeWorkspace),不触网。

覆盖(plan v3 测试矩阵):决策逻辑(每条转换边)/ 幂等 / keep-parent /
解析失败降级 / 无父 case 优雅跳过父链(TEA-12/13/33 型)/ 后置复核暴露插队 /
dry-run 不写 / cancel 摘除集精确性 / publish-init 守卫(重发不回退)。

跑:  python3 -m pytest skills/tc-render/tests/ -q
"""
import importlib.util
import json
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent
TRANSITION_PY = SKILL_DIR / "transition.py"

spec = importlib.util.spec_from_file_location("tc_transition", TRANSITION_PY)
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)

# 测试用 label UUID(仅存在于 FakeWorkspace —— 生产代码禁止硬编码 UUID,测试模拟 workspace 数据)
LABEL_IDS = {
    "计划-草稿": "11111111-0000-0000-0000-000000000001",
    "计划-评审中": "11111111-0000-0000-0000-000000000002",
    "计划-已批准": "11111111-0000-0000-0000-000000000003",
    "计划-已升级": "11111111-0000-0000-0000-000000000004",
    "复盘-待审": "11111111-0000-0000-0000-000000000005",
    "复盘-已审": "11111111-0000-0000-0000-000000000006",
    "研究": "11111111-0000-0000-0000-000000000007",
    "古法不可能": "11111111-0000-0000-0000-000000000008",
}
ID2NAME = {v: k for k, v in LABEL_IDS.items()}


class FakeWorkspace:
    """内存版 multica:issues 可变,writes 真改状态 → verify_post 走真路径。"""

    def __init__(self, issues, labels=None, mutate_on_write=True):
        self.issues = issues          # ref → {status, labels:set, parent_issue_id, title}
        self.labels = labels if labels is not None else dict(LABEL_IDS)
        self.mutate = mutate_on_write # False = ACK 但不改(模拟并发插队/静默失败)
        self.writes = []              # 记录全部写 argv(断言 dry-run / 操作序列)

    def _find(self, ref):
        if ref in self.issues:
            return ref
        for k, v in self.issues.items():
            if v.get("id") == ref:
                return k
        raise KeyError(ref)

    def __call__(self, argv):
        assert argv[0] == "multica"
        if argv[1] == "label" and argv[2] == "list":
            rows = [{"id": i, "name": n, "color": "#000000"} for n, i in self.labels.items()]
            return 0, json.dumps(rows), ""
        if argv[1] == "issue" and argv[2] == "get":
            try:
                k = self._find(argv[3])
            except KeyError:
                return 1, "", "issue not found: %s" % argv[3]
            d = self.issues[k]
            return 0, json.dumps({
                "id": d.get("id", k), "identifier": k, "status": d["status"],
                "labels": [{"id": LABEL_IDS.get(n, "x"), "name": n} for n in sorted(d["labels"])],
                "parent_issue_id": d.get("parent_issue_id"), "title": d.get("title", ""),
            }), ""
        if argv[1] == "issue" and argv[2] == "label":
            self.writes.append(argv)
            k = self._find(argv[4])
            name = ID2NAME.get(argv[5])
            assert name, "label 写操作必须用 UUID(收到 %r)—— 名称直传是 bug" % argv[5]
            if self.mutate:
                (self.issues[k]["labels"].add if argv[3] == "add"
                 else self.issues[k]["labels"].discard)(name)
            return 0, "ok", ""
        if argv[1] == "issue" and argv[2] == "status":
            self.writes.append(argv)
            k = self._find(argv[3])
            if self.mutate:
                self.issues[k]["status"] = argv[4]
            return 0, "Issue %s status changed to %s." % (k, argv[4]), ""
        raise AssertionError("FakeWorkspace 不认识:%r" % (argv,))


def mk(status="todo", labels=(), parent=None, title="", id_=None):
    return {"status": status, "labels": set(labels), "parent_issue_id": parent,
            "title": title, "id": id_ or "00000000-0000-0000-0000-00000000abcd"}


def cli_for(ws):
    return T.Cli(runner=ws)


# ============ 决策层:每条边 ============

def test_publish_init_plan_fresh_adds_draft():
    ops, post, _ = T.compute_publish_init(mk_state(labels=()), "plan")
    assert ("label-add", "计划-草稿") in ops and ("has-label", "计划-草稿") in post
    assert not any(k == "status" for k, _ in ops)  # plan 发布不动 status(todo 默认)


def mk_state(status="todo", labels=(), parent=None, title=""):
    return {"identifier": "TEA-X", "id": "x", "status": status,
            "labels": set(labels), "parent_issue_id": parent, "title": title}


def test_publish_init_plan_republish_does_not_readd_draft():
    """已批准的 plan 重发 v2(记 verdict/handoff 同步)绝不重打 草稿。"""
    for present in ("计划-已批准", "计划-评审中", "计划-草稿", "计划-已升级"):
        ops, _, _ = T.compute_publish_init(mk_state(labels=(present,)), "plan")
        assert ops == [], present


def test_publish_init_research_skeleton_vs_filled():
    ops, _, _ = T.compute_publish_init(mk_state(), "research")
    assert ops == [("label-add", "研究")]
    ops, post, _ = T.compute_publish_init(mk_state(), "research", findings_filled=True)
    assert ("status", "done") in ops and ("status", "done") in post


def test_publish_init_case_fresh_and_finalized_guard():
    ops, _, _ = T.compute_publish_init(mk_state(), "case")
    assert ("label-add", "复盘-待审") in ops and ("status", "in_review") in ops
    ops, _, _ = T.compute_publish_init(mk_state(labels=("复盘-已审",), status="done"), "case")
    assert ops == []  # 已审结 case 重发勘误不回退


def test_publish_init_handoff_noop():
    assert T.compute_publish_init(mk_state(), "handoff") == ([], [], [])


def test_request_review_and_warning():
    ops, post, w = T.compute_plan_request_review(mk_state(labels=("计划-草稿",)))
    assert ("label-add", "计划-评审中") in ops and ("status", "in_review") in ops and w == []
    _, _, w = T.compute_plan_request_review(mk_state(labels=()))
    assert w  # 无草稿/已升级 → warn 不阻断


def test_approve_removes_upgraded_too():
    """B2:approve 摘除集必须含 计划-已升级,否则并存漂移再生(TEA-79/28/22/14 型)。"""
    state = mk_state(status="in_review", labels=("计划-评审中", "计划-已升级", "计划-草稿"))
    ops, post, _ = T.compute_plan_approve(state)
    assert ("label-remove", "计划-已升级") in ops
    assert ("label-remove", "计划-草稿") in ops and ("label-remove", "计划-评审中") in ops
    assert ("label-add", "计划-已批准") in ops and ("status", "todo") in ops  # 批准=待启动,非 in_progress
    assert ("no-label", "计划-已升级") in post


def test_approve_idempotent():
    state = mk_state(status="todo", labels=("计划-已批准",))
    ops, _, _ = T.compute_plan_approve(state)
    assert ops == []


def test_upgrade_swaps_approved_for_draft():
    state = mk_state(status="in_progress", labels=("计划-已批准",))
    ops, _, _ = T.compute_plan_upgrade(state)
    assert set(ops) == {("label-add", "计划-已升级"), ("label-add", "计划-草稿"),
                        ("label-remove", "计划-已批准"), ("status", "todo")}


def test_build_start():
    ops, _, w = T.compute_build_start(mk_state(status="todo", labels=("计划-已批准",)))
    assert ops == [("status", "in_progress")] and w == []
    ops, _, _ = T.compute_build_start(mk_state(status="in_progress", labels=("计划-已批准",)))
    assert ops == []  # 续作 build session 幂等
    _, _, w = T.compute_build_start(mk_state(status="done", labels=()))
    assert len(w) == 2  # 无已批准 + status 意外,都只 warn


def test_parent_close_variants():
    ops, post, _ = T.compute_parent_close(mk_state(status="in_progress", labels=("计划-已批准", "计划-草稿")))
    assert ("status", "done") in ops and ("label-remove", "计划-草稿") in ops
    assert ("label-remove", "计划-已批准") not in ops  # 保留已批准(历史事实)
    ops, _, _ = T.compute_parent_close(mk_state(status="done", labels=("计划-评审中",)))
    assert ops == [("label-remove", "计划-评审中")]  # 已 done 只清未决
    ops, _, w = T.compute_parent_close(mk_state(status="cancelled", labels=("计划-草稿",)))
    assert ops == [] and w  # 绝不复活 cancelled


def test_grandparent_close_only_research_and_open():
    ops, _, _ = T.compute_grandparent_close(mk_state(status="todo", labels=("研究",)))
    assert ops == [("status", "done")]
    ops, _, _ = T.compute_grandparent_close(mk_state(status="todo", labels=(), title="研究:xx"))
    assert ops == [("status", "done")]  # title 前缀兜底(legacy 零 label · 半角冒号)
    ops, _, _ = T.compute_grandparent_close(mk_state(status="todo", labels=(), title="研究：xx"))
    assert ops == [("status", "done")]  # 全角冒号同样认
    assert T.compute_grandparent_close(mk_state(status="done", labels=("研究",)))[0] == []
    assert T.compute_grandparent_close(mk_state(status="todo", labels=(), title="计划:xx"))[0] == []
    # 收窄防误伤:以「研究」开头但非 研究: 前缀的普通 issue 绝不被强制 done
    assert T.compute_grandparent_close(mk_state(status="todo", labels=(), title="研究小组周报"))[0] == []


def test_cancelled_guard_blocks_revival():
    """cancelled 终态防复活:显式子命令对 cancelled issue 一律硬拒(cancel 本身除外)。"""
    ws = FakeWorkspace({"TEA-DEAD": mk(status="cancelled", labels=())})
    with pytest.raises(T.TransitionError, match="绝不复活"):
        T.run_publish_init("TEA-DEAD", "case", cli=cli_for(ws))
    with pytest.raises(T.TransitionError, match="绝不复活"):
        T.run_simple("TEA-DEAD", T.compute_build_start, cmd_name="build-start", cli=cli_for(ws))
    with pytest.raises(T.TransitionError, match="绝不复活"):
        T.run_case_finalize("TEA-DEAD", cli=cli_for(ws))
    assert ws.writes == []  # 全程零写


def test_cancel_on_cancelled_cleans_labels():
    """cancel 对已 cancelled 的残留 label 修复路径(TEA-75/69 型)不被防复活门挡。"""
    ws = FakeWorkspace({"TEA-75X": mk(status="cancelled", labels=("计划-草稿", "计划-评审中"))})
    T.run_simple("TEA-75X", T.compute_cancel, cmd_name="cancel", cli=cli_for(ws))
    assert ws.issues["TEA-75X"]["labels"] == set() and ws.issues["TEA-75X"]["status"] == "cancelled"


def test_cancel_removes_only_present_process_labels():
    state = mk_state(status="in_review", labels=("计划-草稿", "计划-评审中", "古法不可能"))
    ops, post, _ = T.compute_cancel(state)
    assert ("label-remove", "计划-草稿") in ops and ("label-remove", "计划-评审中") in ops
    assert not any(v == "古法不可能" for _, v in ops)  # 非流程 label 不摘
    assert ("status", "cancelled") in ops
    assert all(("no-label", n) in post for n in T.PROCESS_LABELS)  # 后置:全部流程 label 必不在


# ============ 集成:FakeWorkspace 全链路 ============

def test_case_finalize_full_chain():
    """case done+已审,父 plan done+清未决保留已批准,祖父 research done。"""
    ws = FakeWorkspace({
        "TEA-CASE": mk(status="in_review", labels=("复盘-待审",), parent="p-uuid"),
        "TEA-PLAN": mk(status="in_progress", labels=("计划-已批准", "计划-评审中"),
                       parent="g-uuid", id_="p-uuid"),
        "TEA-RES": mk(status="todo", labels=("研究",), title="研究:x", id_="g-uuid"),
    })
    T.run_case_finalize("TEA-CASE", cli=cli_for(ws))
    assert ws.issues["TEA-CASE"]["status"] == "done"
    assert ws.issues["TEA-CASE"]["labels"] == {"复盘-已审"}
    assert ws.issues["TEA-PLAN"]["status"] == "done"
    assert ws.issues["TEA-PLAN"]["labels"] == {"计划-已批准"}
    assert ws.issues["TEA-RES"]["status"] == "done"


def test_case_finalize_keep_parent():
    """phase case(TEA-62 型):--keep-parent 跳过父链,父 plan 不被动。"""
    ws = FakeWorkspace({
        "TEA-CASE": mk(status="done", labels=("复盘-待审",), parent="p-uuid"),
        "TEA-PLAN": mk(status="in_progress", labels=("计划-已批准",), id_="p-uuid"),
    })
    T.run_case_finalize("TEA-CASE", keep_parent=True, cli=cli_for(ws))
    assert ws.issues["TEA-CASE"]["labels"] == {"复盘-已审"}
    assert ws.issues["TEA-PLAN"]["status"] == "in_progress"
    assert not any(a[3:5] == ["TEA-PLAN", "done"] for a in ws.writes)


def test_case_finalize_parentless_graceful():
    """无父 case(TEA-12/13/33 型):warn 后正常完成,不报错。"""
    ws = FakeWorkspace({"TEA-CASE": mk(status="todo", labels=("复盘-待审",), parent=None)})
    T.run_case_finalize("TEA-CASE", cli=cli_for(ws))
    assert ws.issues["TEA-CASE"]["status"] == "done"


def test_case_finalize_parent_unresolvable_graceful():
    """父 UUID 指向不存在 issue(dfddf545 误判教训的反向防护):warn 继续,case 本体已完成。"""
    ws = FakeWorkspace({"TEA-CASE": mk(status="todo", labels=("复盘-待审",), parent="ghost-uuid")})
    T.run_case_finalize("TEA-CASE", cli=cli_for(ws))
    assert ws.issues["TEA-CASE"]["status"] == "done"


def test_label_resolution_failure_hard_stop():
    """workspace 缺标准 label → TransitionError(指向 create-labels.sh),绝不静默跳过。"""
    ws = FakeWorkspace({"TEA-P": mk(status="todo", labels=())},
                       labels={"研究": LABEL_IDS["研究"]})  # 只有 研究,缺 计划-草稿
    with pytest.raises(T.TransitionError, match="create-labels.sh"):
        T.run_publish_init("TEA-P", "plan", cli=cli_for(ws))


def test_verify_post_exposes_silent_failure():
    """写操作 ACK 但状态未变(并发插队/静默失败)→ 后置复核 exit:P-7 真验证。"""
    ws = FakeWorkspace({"TEA-P": mk(status="todo", labels=("计划-草稿",))}, mutate_on_write=False)
    with pytest.raises(T.TransitionError, match="后置复核失败"):
        T.run_simple("TEA-P", T.compute_plan_request_review, cli=cli_for(ws))


def test_dry_run_no_writes():
    ws = FakeWorkspace({"TEA-P": mk(status="todo", labels=("计划-草稿",))})
    T.run_simple("TEA-P", T.compute_plan_request_review, cli=cli_for(ws), dry_run=True)
    assert ws.writes == [] and ws.issues["TEA-P"]["status"] == "todo"


def test_idempotent_noop_run():
    ws = FakeWorkspace({"TEA-P": mk(status="in_review", labels=("计划-草稿", "计划-评审中"))})
    T.run_simple("TEA-P", T.compute_plan_request_review, cli=cli_for(ws))
    assert ws.writes == []  # 已在目标态:零写操作


def test_writes_use_uuid_not_name():
    """label 写操作必须经 name→UUID 解析(FakeWorkspace 内部已断言收到 UUID)。"""
    ws = FakeWorkspace({"TEA-P": mk(status="todo", labels=())})
    T.run_publish_init("TEA-P", "plan", cli=cli_for(ws))
    label_writes = [a for a in ws.writes if a[2] == "label"]
    assert label_writes and all(a[5] in ID2NAME for a in label_writes)
