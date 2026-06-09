#!/usr/bin/env python3
"""monthly health report — 团队健康月报。取代本地 MCP 的 monthly_health_report。

用法:  monthly_health.py <team-context-repo> [<project-repo> ...]
markdown 报告输出到 stdout。指标:CLAUDE.md token / 本月 claude-md 改动 /
skill lint(stale+owner gaps,内联复刻)/ wip: 重启次数 / case 污染(人工 grep)。
"""
import sys
import os
import re
import subprocess
import datetime


def estimate_tokens(text):
    return len(text.split()) * 13 // 10  # 空白分割 · 复刻 MCP estimateTokens


def git_log_since(repo, since_iso):
    out = subprocess.run(
        ["git", "-C", repo, "log", "--since", since_iso, "--pretty=%H%x09%s"],
        capture_output=True, text=True,
    ).stdout
    return [line.split("\t", 1) for line in out.splitlines() if "\t" in line]


def main():
    if len(sys.argv) < 2:
        print("usage: monthly_health.py <team-context-repo> [project-repo ...]", file=sys.stderr)
        sys.exit(2)
    repo = sys.argv[1]
    date = datetime.date.today().strftime("%Y-%m")
    since = (datetime.datetime.now() - datetime.timedelta(days=30)).isoformat()
    L = ["# Monthly Health Report — %s" % date, ""]

    # 1: CLAUDE.md token count
    cmd_path = os.path.join(repo, "claude_md_team_global.md")
    L.append("## CLAUDE.md token count")
    if os.path.exists(cmd_path):
        t = estimate_tokens(open(cmd_path).read())
        L.append("- team-global: ~%d tokens %s" % (t, "⚠️ OVER 3K" if t > 3000 else "✅"))
    else:
        L.append("- _(no claude_md_team_global.md found)_")
    L.append("")

    commits = git_log_since(repo, since)

    # 2: CLAUDE.md commits this month
    cm = [c for c in commits if re.search(r"claude.?md", c[1], re.I)]
    L.append("## CLAUDE.md changes this month")
    if not cm:
        L.append("- _(none — possibly under-learning)_")
    else:
        for h, m in cm:
            L.append("- %s %s" % (h[:7], m))
    L.append("")

    # 3-4: skill lint (inline replicate of `multica skill lint`)
    skills_dir = os.path.join(repo, "skills")
    L.append("## Skill lint (stale + owner gaps)")
    if os.path.isdir(skills_dir):
        for name in sorted(os.listdir(skills_dir)):
            sf = os.path.join(skills_dir, name, "SKILL.md")
            if not os.path.isfile(sf):
                continue
            md = open(sf).read()
            m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", md, re.S)
            fm, body = (m.group(1), m.group(2)) if m else ("", md)
            errs, warns = [], []
            if not re.search(r"^name:", fm, re.M):
                errs.append("missing name")
            if not re.search(r"^description:", fm, re.M):
                errs.append("missing description")
            if not re.search(r"^owner:", fm, re.M):
                warns.append("missing owner")
            if not re.search(r"^last_reviewed_at:", fm, re.M):
                warns.append("missing last_reviewed_at")
            tok = estimate_tokens(body)
            if tok > 2000:
                errs.append("body ~%d tokens >2000" % tok)
            tag = "❌" if errs else ("⚠️" if warns else "✅")
            L.append("- %s **%s** (~%d tokens)" % (tag, name, tok))
            for e in errs:
                L.append("  - ERROR: %s" % e)
            for w in warns:
                L.append("  - WARN: %s" % w)
    else:
        L.append("- _(skills/ dir not found)_")
    L.append("")

    # 6: /clear (wip:) count
    wip = [c for c in commits if re.match(r"^wip:", c[1], re.I)]
    L.append("## /clear (wip:) count")
    L.append("- %d wip: commits in last 30 days%s" % (len(wip), " ⚠️ heavy restart, check burnout" if len(wip) > 50 else ""))
    for h, m in wip[:10]:
        L.append("  - %s %s" % (h[:7], m))
    L.append("")

    # 5: case-specific contamination (heuristic, manual)
    L.append("## case-specific contamination check")
    L.append("- _(heuristic: grep CLAUDE.md for project names — run manually)_")

    print("\n".join(L))


if __name__ == "__main__":
    main()
