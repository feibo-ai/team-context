#!/usr/bin/env python3
"""issue invariants — multica issue label↔status 不变量巡检(全量分页)。

状态机语义单源 = tc-render skill 的 references/issue-label-state-rules.md(不变量表);
修复一律经 tc-render skill 的 scripts/transition.py。
本脚本只读、零写:输出 markdown 违规清单,供月度健康报告 / backfill 验收用。

8 条硬性不变量(适用于带流程 label 的 issue;零 label 轻任务不在审计内):
  1. 复盘-已审   ⇒ status done
  2. 复盘-待审   ⇒ status in_review
  3. 计划-评审中 ⇒ status in_review
  4. 计划-已批准 ⇒ status ∈ {todo, in_progress, done};设计-待审 在场时另允许 in_review
     (carve-out:设计评审中 = 已批准+in_review 合法 · TEA-99 评审 B1)
  5. cancelled  ⇒ 无任何流程 label
  6. 计划-已升级 ⊕ 计划-已批准 互斥
  7. 设计-待审   ⇒ status in_review
  8. 设计-待审   ⊕ 设计-已审 互斥(复审应作废旧批准,由 design-request-review 保证)

3 档警告(不算违规,提示人看):
  - staleness:计划-评审中 / 设计-待审 / 复盘-待审 且 issue updated_at 超 48h(以
    updated_at 近似 label 挂上时间——编排 session 在 verdict 后死亡的残留态信号)
  - 盲区:标题前缀 计划:/研究:/复盘: 却无任何入口 label(流程 label ∪ 研究)——
    入口转换缺失(TEA-90/82 型;cancelled 终态除外;正在调研中的空 research issue
    会命中,属预期信号:研究没发布就是没交付)
  - 研究未关:带 研究 label 但 status≠done(研究发布即 done 语义;legacy 滞留)

分页硬要求:--limit/--offset 循环至 has_more=false。默认一页 50 条——只看第一页
曾把 91 个 issue 看成 50 个(TEA-97 plan v1 评审 B1 实证)。

运行渠道:已编入 monthly-health autopilot(report-only,随月度健康卡推飞书);
--strict 模式保留给 backfill 验收 / CI(autopilot 不用 --strict)。

用法:
  python3 issue_invariants.py            # markdown 报告,exit 0
  python3 issue_invariants.py --strict   # 有硬性违规则 exit 1(backfill 验收/CI 用)
"""
import argparse
import datetime
import json
import subprocess
import sys

PROCESS_LABELS = {
    "计划-草稿", "计划-评审中", "计划-已批准", "计划-已升级",
    "设计-待审", "设计-已审",
    "复盘-待审", "复盘-已审",
}
ENTRY_LABELS = PROCESS_LABELS | {"研究"}  # 盲区豁免:研究 issue 的入口 label 是 研究
TITLE_PREFIXES = tuple(w + c for w in ("计划", "研究", "复盘") for c in (":", "："))  # 半角+全角冒号都认
STALE_HOURS = 48
PAGE = 50


def fetch_all_issues():
    """全量分页拉取(has_more=false 才停 · 不变量 #0:巡检自己不许被截断)。"""
    issues, offset = [], 0
    while True:
        p = subprocess.run(
            ["multica", "issue", "list", "--output", "json",
             "--limit", str(PAGE), "--offset", str(offset)],
            capture_output=True, text=True)
        if p.returncode != 0:
            print("ERROR · multica issue list 失败:%s" % (p.stderr or p.stdout)[:200],
                  file=sys.stderr)
            sys.exit(1)
        page = json.loads(p.stdout)
        batch = page.get("issues") or []
        issues.extend(batch)
        if not page.get("has_more") or not batch:
            return issues
        offset += len(batch)


def check(issues, now=None):
    now = now or datetime.datetime.now(datetime.timezone.utc)
    violations, warnings = [], []
    for it in issues:
        ident = it.get("identifier") or it.get("id", "?")[:8]
        status = it.get("status")
        labels = {l.get("name") for l in (it.get("labels") or []) if isinstance(l, dict)}
        plabels = labels & PROCESS_LABELS
        title = it.get("title") or ""

        if plabels:
            if "复盘-已审" in labels and status != "done":
                violations.append((1, ident, "复盘-已审 但 status=%s(应 done)" % status))
            if "复盘-待审" in labels and status != "in_review":
                violations.append((2, ident, "复盘-待审 但 status=%s(应 in_review)" % status))
            if "计划-评审中" in labels and status != "in_review":
                violations.append((3, ident, "计划-评审中 但 status=%s(应 in_review)" % status))
            ok4 = ("todo", "in_progress", "done", "in_review") if "设计-待审" in labels \
                else ("todo", "in_progress", "done")  # carve-out:设计评审中合法(B1)
            if "计划-已批准" in labels and status not in ok4:
                violations.append((4, ident, "计划-已批准 但 status=%s" % status))
            if status == "cancelled":
                violations.append((5, ident, "cancelled 但残留流程 label:%s" % "、".join(sorted(plabels))))
            if "计划-已升级" in labels and "计划-已批准" in labels:
                violations.append((6, ident, "计划-已升级 与 计划-已批准 并存(approve 漏摘)"))
            if "设计-待审" in labels and status != "in_review":
                violations.append((7, ident, "设计-待审 但 status=%s(应 in_review)" % status))
            if "设计-待审" in labels and "设计-已审" in labels:
                violations.append((8, ident, "设计-待审 与 设计-已审 并存(复审应作废旧批准)"))

            if labels & {"计划-评审中", "设计-待审", "复盘-待审"} and status != "cancelled":
                ts = it.get("updated_at")
                try:
                    upd = datetime.datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
                    hours = (now - upd).total_seconds() / 3600
                    if hours > STALE_HOURS:
                        warnings.append((ident, "评审挂起 %.0fh(>%dh):%s — verdict 后编排 session 死亡?"
                                         % (hours, STALE_HOURS, "、".join(sorted(labels & {"计划-评审中", "设计-待审", "复盘-待审"})))))
                except (TypeError, ValueError):
                    pass

        if "研究" in labels and status != "done" and status != "cancelled":
            warnings.append((ident, "研究 label 但 status=%s(研究发布即 done 语义;legacy 滞留?)" % status))
        if (not (labels & ENTRY_LABELS) and title.startswith(TITLE_PREFIXES)
                and status != "cancelled"):
            warnings.append((ident, "标题像流程 issue(%s…)却无入口 label —— 入口转换缺失?" % title[:12]))
    return violations, warnings


def main():
    ap = argparse.ArgumentParser(description="multica issue label↔status 不变量巡检(只读)")
    ap.add_argument("--strict", action="store_true", help="有硬性违规则 exit 1")
    a = ap.parse_args()

    issues = fetch_all_issues()
    violations, warnings = check(issues)

    print("# Issue 不变量巡检 — %s" % datetime.date.today().isoformat())
    print("\n扫描:%d 个 issue(分页拉全)· 硬性违规 %d · 警告 %d\n"
          % (len(issues), len(violations), len(warnings)))
    if violations:
        print("## 硬性违规(漂移,需 transition.py 修复)")
        for num, ident, msg in sorted(violations):
            print("- [不变量#%d] %s:%s" % (num, ident, msg))
    else:
        print("## 硬性违规\n(无 —— 8 条不变量全部成立 ✅)")
    if warnings:
        print("\n## 警告(不算违规,人工看一眼)")
        for ident, msg in warnings:
            print("- %s:%s" % (ident, msg))

    if a.strict and violations:
        sys.exit(1)


if __name__ == "__main__":
    main()
