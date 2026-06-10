#!/usr/bin/env python3
"""tc-render transition — multica issue 状态机原子转换(label+status+父链)收口脚本。

原本地 MCP(plan_approve / case_review / project_kickoff)内置的原子状态转换,
去本地MCP 后散落为 skill 散文 bash 块 → 边无主、漏执行(TEA-95/70 实证)。
本脚本把每条转换边收口为一个子命令:前置校验 → 执行 → issue get 复核后置状态
(P-7 真验证内建),不符 exit 1。与 publish.py 同目录共库,publish.py 发布成功后
import 本模块做入口转换(publish-init)。

子命令(语义单源 = 本文件 + standards/labels.md 不变量表):
  publish-init <issue> --doc-type {plan|research|case|handoff} [--findings-filled]
      plan     → +计划-草稿(仅当无任何 计划-* label)
      research → +研究;--findings-filled 时 status done(发现已交付)
      case     → +复盘-待审(仅当无 复盘-已审)+ status in_review
      handoff  → 不动(no-op)
  plan-request-review <issue>   → +计划-评审中 · status in_review
  plan-approve <issue>          → +计划-已批准 · −{计划-草稿,计划-评审中,计划-已升级} · status todo(待启动;in_progress 由 build-start 设)
  plan-upgrade <issue>          → +{计划-已升级,计划-草稿} · −计划-已批准 · status todo(再走 request-review)
  build-start <issue>           → status in_progress(首个 build session · 与开工卡同时机)
  case-finalize <issue> [--keep-parent]
      → +复盘-已审 · −复盘-待审 · status done;
        默认连带:父 plan status done + 清父未决流程 label(草稿/评审中/已升级,保留已批准),
        祖父 research 尽力 done(legacy 链兜底);--keep-parent 跳过全部父链操作
        (phase case 专用:如 TEA-62 是 phase-a 复盘,父 TEA-57 整体 plan 仍在进行)。
  cancel <issue>                → status cancelled · −全部流程 label(精确集合见 PROCESS_LABELS)

通用语义:
  * label 引用一律名称,经 `multica label list` 运行时解析为 UUID;禁止硬编码 UUID
    (UUID 是 workspace 数据,labels.md 才是单源,create-labels.sh 重建后 UUID 会变)。
    解析失败 exit 1 并提示跑 scripts/create-labels.sh,绝不静默跳过。
  * 幂等:执行前 issue get 预读,『label 已存在/已是目标 status』直接跳过(不解析
    duplicate-add 报错文案 —— CLI 报错串无契约保证)。全部为跳过 = 已在目标态,成功。
  * 并发:last-writer-wins;后置复核(issue get 重读断言)会以 exit 1 暴露被插队。
  * 前置态意外(如 approve 时无 评审中)只 warn 不阻断 —— 保证存量漂移可修。
  * 父链:parent 缺失/不可解析 → warn 后继续(无父 case 合法,如 TEA-12/13/33);
    parent 已 done/cancelled → 不动(绝不复活 cancelled)。
  * --dry-run:只做只读调用(label list / issue get),打印将执行的写命令,不写。

exit code:0 成功(含幂等空转) · 1 校验/解析/后置复核失败。
"""
import argparse
import json
import subprocess
import sys

# 流程 label 全集(cancel 的摘除集 = 与现场的交集;不含 研究/古法不可能/投注表/代码评审/倦怠预警)
PROCESS_LABELS = [
    "计划-草稿", "计划-评审中", "计划-已批准", "计划-已升级",
    "复盘-待审", "复盘-已审",
]
PLAN_LABELS = ["计划-草稿", "计划-评审中", "计划-已批准", "计划-已升级"]
PLAN_PENDING_LABELS = ["计划-草稿", "计划-评审中", "计划-已升级"]  # 父链清理:保留 已批准


class TransitionError(Exception):
    """转换失败(publish.py 捕获后走 exit 2 契约;本脚本 CLI 入口捕获后 exit 1)。"""


def warn(msg):
    print("WARN · " + msg, file=sys.stderr)


# ======================================================================
# CLI 适配层(可注入 runner 供测试 mock;真实 runner 走 subprocess)
# ======================================================================

def real_runner(argv):
    """跑 multica CLI,返回 (returncode, stdout, stderr)。token 由 CLI 自管,不进 argv。"""
    try:
        p = subprocess.run(argv, capture_output=True, text=True)
    except FileNotFoundError:
        raise TransitionError("找不到 multica CLI;先安装/更新 multica(≥v0.4.11)")
    return p.returncode, p.stdout, p.stderr


class Cli:
    def __init__(self, runner=real_runner):
        self.runner = runner

    def run_json(self, argv):
        code, out, err = self.runner(argv)
        if code != 0:
            raise TransitionError("`%s` exit %d:%s" % (" ".join(argv), code, (err or out).strip()[:300]))
        try:
            return json.loads(out)
        except Exception:
            raise TransitionError("`%s` 输出非 JSON:%s" % (" ".join(argv), (out or err)[:200]))

    def run_ok(self, argv):
        code, out, err = self.runner(argv)
        if code != 0:
            raise TransitionError("`%s` exit %d:%s" % (" ".join(argv), code, (err or out).strip()[:300]))
        return out


def fetch_labels(cli):
    """workspace label name→UUID 解析表(运行时单源,禁止硬编码 UUID)。"""
    rows = cli.run_json(["multica", "label", "list", "--output", "json"])
    if not isinstance(rows, list):
        raise TransitionError("label list 输出形状非数组(CLI 升版漂移?对照 test_contract_probe)")
    return {r["name"]: r["id"] for r in rows if isinstance(r, dict) and r.get("name") and r.get("id")}


def resolve_label(label_ids, name):
    if name not in label_ids:
        raise TransitionError(
            "label %r 不存在于 workspace —— 不静默跳过;先跑 scripts/create-labels.sh 重建标准 label 集" % name)
    return label_ids[name]


def fetch_issue(cli, ref):
    """issue 现场:status / labels(名称集合)/ parent_issue_id / identifier / title。"""
    d = cli.run_json(["multica", "issue", "get", str(ref), "--output", "json"])
    if not isinstance(d, dict) or "status" not in d:
        raise TransitionError("issue get 输出形状异常(CLI 升版漂移?对照 test_contract_probe)")
    return {
        "id": d.get("id"),
        "identifier": d.get("identifier") or str(ref),
        "status": d.get("status"),
        "labels": {l.get("name") for l in (d.get("labels") or []) if isinstance(l, dict)},
        "parent_issue_id": d.get("parent_issue_id"),
        "title": d.get("title") or "",
    }


# ======================================================================
# 纯决策层:据现场算出最小操作集(幂等由构造保证)+ 后置断言
# ops 元素:("label-add", name) / ("label-remove", name) / ("status", value)
# post   :("has-label", name) / ("no-label", name) / ("status", value)
# ======================================================================

def _ops_to(state, add=(), remove=(), status=None):
    ops = []
    for n in add:
        if n not in state["labels"]:
            ops.append(("label-add", n))
    for n in remove:
        if n in state["labels"]:
            ops.append(("label-remove", n))
    if status is not None and state["status"] != status:
        ops.append(("status", status))
    return ops


def _post_to(add=(), remove=(), status=None):
    post = [("has-label", n) for n in add] + [("no-label", n) for n in remove]
    if status is not None:
        post.append(("status", status))
    return post


def compute_publish_init(state, doc_type, findings_filled=False):
    """发布即入口转换。返回 (ops, post, warnings)。"""
    w = []
    if doc_type == "plan":
        if any(n in state["labels"] for n in PLAN_LABELS):
            return [], [], w  # 已在 plan 流程中(如 v2 重发):不重打草稿,不动现场
        return _ops_to(state, add=["计划-草稿"]), _post_to(add=["计划-草稿"]), w
    if doc_type == "research":
        status = "done" if findings_filled else None
        return (_ops_to(state, add=["研究"], status=status),
                _post_to(add=["研究"], status=status), w)
    if doc_type == "case":
        if "复盘-已审" in state["labels"]:
            return [], [], w  # 已审结的 case 重发(如勘误)不回退
        return (_ops_to(state, add=["复盘-待审"], status="in_review"),
                _post_to(add=["复盘-待审"], status="in_review"), w)
    if doc_type == "handoff":
        return [], [], w
    raise TransitionError("未知 doc_type:%r" % doc_type)


def compute_plan_request_review(state):
    w = []
    if not any(n in state["labels"] for n in ("计划-草稿", "计划-已升级")):
        w.append("%s 请审时既无 计划-草稿 也无 计划-已升级(意外现场,继续)" % state["identifier"])
    return (_ops_to(state, add=["计划-评审中"], status="in_review"),
            _post_to(add=["计划-评审中"], status="in_review"), w)


def compute_plan_approve(state):
    w = []
    if "计划-评审中" not in state["labels"]:
        w.append("%s 批准时无 计划-评审中(未经请审?意外现场,继续)" % state["identifier"])
    # 摘除集含 计划-已升级:不摘则 upgrade→re-approve 后并存漂移再生(v1 评审 B2 · TEA-79/28/22/14)
    return (_ops_to(state, add=["计划-已批准"], remove=PLAN_PENDING_LABELS, status="todo"),
            _post_to(add=["计划-已批准"], remove=PLAN_PENDING_LABELS, status="todo"), w)


def compute_plan_upgrade(state):
    return (_ops_to(state, add=["计划-已升级", "计划-草稿"], remove=["计划-已批准"], status="todo"),
            _post_to(add=["计划-已升级", "计划-草稿"], remove=["计划-已批准"], status="todo"), [])


def compute_build_start(state):
    w = []
    if "计划-已批准" not in state["labels"]:
        w.append("%s 开工时无 计划-已批准(plan 未批准就 build?意外现场,继续)" % state["identifier"])
    if state["status"] not in ("todo", "in_progress"):
        w.append("%s 开工前 status=%s(预期 todo;意外现场,继续)" % (state["identifier"], state["status"]))
    return _ops_to(state, status="in_progress"), _post_to(status="in_progress"), w


def compute_case_finalize(state):
    return (_ops_to(state, add=["复盘-已审"], remove=["复盘-待审"], status="done"),
            _post_to(add=["复盘-已审"], remove=["复盘-待审"], status="done"), [])


def compute_parent_close(parent_state):
    """case-finalize 连带:父 plan done + 清未决流程 label(保留 计划-已批准)。
    父已 done → 只清未决 label;父 cancelled → 完全不动(绝不复活)。"""
    if parent_state["status"] == "cancelled":
        return [], [], ["父 %s 已 cancelled,不动(绝不复活)" % parent_state["identifier"]]
    status = None if parent_state["status"] == "done" else "done"
    return (_ops_to(parent_state, remove=PLAN_PENDING_LABELS, status=status),
            _post_to(remove=PLAN_PENDING_LABELS, status=status or "done"), [])


def compute_grandparent_close(gp_state):
    """祖父 research 尽力关闭(legacy 链兜底;新链 research 在发布时已 done)。"""
    is_research = "研究" in gp_state["labels"] or gp_state["title"].startswith("研究")
    if not is_research or gp_state["status"] in ("done", "cancelled"):
        return [], [], []
    return _ops_to(gp_state, status="done"), _post_to(status="done"), []


def compute_cancel(state):
    present = [n for n in PROCESS_LABELS if n in state["labels"]]
    return (_ops_to(state, remove=present, status="cancelled"),
            _post_to(remove=PROCESS_LABELS, status="cancelled"), [])


# ======================================================================
# 执行 + 后置复核(P-7 真验证)
# ======================================================================

def execute_ops(cli, ref, ops, label_ids, dry_run=False):
    for op in ops:
        kind, val = op
        if kind == "label-add":
            argv = ["multica", "issue", "label", "add", str(ref), resolve_label(label_ids, val)]
        elif kind == "label-remove":
            argv = ["multica", "issue", "label", "remove", str(ref), resolve_label(label_ids, val)]
        elif kind == "status":
            argv = ["multica", "issue", "status", str(ref), val]
        else:
            raise TransitionError("未知 op:%r" % (op,))
        if dry_run:
            print("DRY-RUN · " + " ".join(argv))
        else:
            cli.run_ok(argv)


def verify_post(cli, ref, post):
    """后置复核:重读 issue 断言目标态。CLI success ≠ 做对了(P-7)。"""
    if not post:
        return
    state = fetch_issue(cli, ref)
    bad = []
    for kind, val in post:
        if kind == "has-label" and val not in state["labels"]:
            bad.append("缺 label %s" % val)
        elif kind == "no-label" and val in state["labels"]:
            bad.append("残留 label %s" % val)
        elif kind == "status" and state["status"] != val:
            bad.append("status=%s ≠ %s" % (state["status"], val))
    if bad:
        raise TransitionError("%s 后置复核失败(可能被并发插队):%s"
                              % (state["identifier"], ";".join(bad)))


def apply_transition(cli, ref, ops, post, warnings, label_ids, dry_run=False):
    for m in warnings:
        warn(m)
    if not ops:
        print("OK · %s 已在目标态(幂等空转)" % ref)
        return
    execute_ops(cli, ref, ops, label_ids, dry_run=dry_run)
    if dry_run:
        return
    verify_post(cli, ref, post)
    print("OK · %s → %s" % (ref, ", ".join("%s:%s" % (k, v) for k, v in ops)))


# ======================================================================
# 子命令编排
# ======================================================================

def run_publish_init(issue, doc_type, findings_filled=False, cli=None, dry_run=False):
    """publish.py 发布成功后调用的入口转换(也可独立补救调用,幂等)。"""
    cli = cli or Cli()
    label_ids = fetch_labels(cli)
    state = fetch_issue(cli, issue)
    ops, post, w = compute_publish_init(state, doc_type, findings_filled)
    apply_transition(cli, issue, ops, post, w, label_ids, dry_run=dry_run)


def run_simple(issue, compute, cli=None, dry_run=False):
    cli = cli or Cli()
    label_ids = fetch_labels(cli)
    state = fetch_issue(cli, issue)
    ops, post, w = compute(state)
    apply_transition(cli, issue, ops, post, w, label_ids, dry_run=dry_run)


def run_case_finalize(issue, keep_parent=False, cli=None, dry_run=False):
    cli = cli or Cli()
    label_ids = fetch_labels(cli)
    state = fetch_issue(cli, issue)
    ops, post, w = compute_case_finalize(state)
    apply_transition(cli, issue, ops, post, w, label_ids, dry_run=dry_run)
    if keep_parent:
        print("OK · --keep-parent:跳过父链(phase case)")
        return
    pid = state["parent_issue_id"]
    if not pid:
        warn("%s 无父 issue,跳过父链(合法:无父 case)" % state["identifier"])
        return
    try:
        parent = fetch_issue(cli, pid)
    except TransitionError as e:
        warn("父 issue %s 不可解析,跳过父链:%s" % (pid, e))
        return
    p_ops, p_post, p_w = compute_parent_close(parent)
    apply_transition(cli, pid, p_ops, p_post, p_w, label_ids, dry_run=dry_run)
    gpid = parent.get("parent_issue_id")
    if not gpid:
        return
    try:
        gp = fetch_issue(cli, gpid)
        g_ops, g_post, g_w = compute_grandparent_close(gp)
        apply_transition(cli, gpid, g_ops, g_post, g_w, label_ids, dry_run=dry_run)
    except TransitionError as e:
        warn("祖父 research 收口尽力而为,失败不阻断:%s" % e)


def main(argv=None):
    ap = argparse.ArgumentParser(description="multica issue 状态机原子转换(语义见模块 docstring 与 standards/labels.md)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("publish-init", help="发布即入口转换(publish.py 自动调;可独立幂等补救)")
    p_init.add_argument("issue")
    p_init.add_argument("--doc-type", required=True, choices=["plan", "research", "case", "handoff"])
    p_init.add_argument("--findings-filled", action="store_true", help="research findings 非空(发现已交付→done)")

    for name in ("plan-request-review", "plan-approve", "plan-upgrade", "build-start", "cancel"):
        sp = sub.add_parser(name)
        sp.add_argument("issue")

    p_fin = sub.add_parser("case-finalize", help="评审通过后由编排 session 立即执行(verdict 返回点)")
    p_fin.add_argument("issue")
    p_fin.add_argument("--keep-parent", action="store_true",
                       help="跳过父链连带(phase case:父 plan 还有其他阶段在进行)")

    ap.add_argument("--dry-run", action="store_true", help="只读取现场并打印将执行的写命令")
    a = ap.parse_args(argv)

    simple = {
        "plan-request-review": compute_plan_request_review,
        "plan-approve": compute_plan_approve,
        "plan-upgrade": compute_plan_upgrade,
        "build-start": compute_build_start,
        "cancel": compute_cancel,
    }
    try:
        if a.cmd == "publish-init":
            run_publish_init(a.issue, a.doc_type, a.findings_filled, dry_run=a.dry_run)
        elif a.cmd == "case-finalize":
            run_case_finalize(a.issue, keep_parent=a.keep_parent, dry_run=a.dry_run)
        else:
            run_simple(a.issue, simple[a.cmd], dry_run=a.dry_run)
    except TransitionError as e:
        print("TRANSITION FAILED · %s" % e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
