#!/usr/bin/env python3
"""monthly health report — 团队健康月报。

用法:  monthly_health.py <team-context-repo> [<project-repo> ...]
markdown 报告输出到 stdout。指标:CLAUDE.md 字符量 / 本月 claude-md 改动 /
skill lint(body 体量 + 治理字段;owner/last_reviewed_at 读 repo 根 skill-pack.yaml
治理表,缺文件则跳过并警告)/ wip: 重启次数 / case 污染(人工 grep)。
"""
import sys
import os
import re
import subprocess
import datetime

# 体量口径 = unicode 字符数 len(text),与 CI lint 完全一致
# (旧的空白分割 token 估算对 CJK 文本严重低估,已移除)。
CLAUDE_MD_CHAR_LIMIT = 4000   # CLAUDE.md 硬上限:4000 unicode 字符,与 CI 同口径
SKILL_BODY_CHAR_LIMIT = 1500  # SKILL.md body 硬上限:1500 unicode 字符,与 CI 同口径


def char_count(text):
    return len(text)  # unicode 字符数,与 CI lint 同口径


def load_ownership(repo):
    """读 repo 根 skill-pack.yaml 治理表(skills: [{name, owner, last_reviewed_at}])。

    治理字段(owner/last_reviewed_at)的仓库侧单源是 skill-pack.yaml,
    不在各 SKILL.md frontmatter(frontmatter 只留标准字段 name+description)。
    文件缺失 → 返回 None,调用方打 warning 并跳过治理检查。零依赖行解析。
    """
    path = os.path.join(repo, "skill-pack.yaml")
    if not os.path.isfile(path):
        return None
    table, cur, in_skills = {}, None, False
    for raw in open(path):
        line = raw.rstrip("\n")
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not in_skills:
            if re.match(r"^skills:\s*$", line):
                in_skills = True
            continue
        if not line[:1].isspace():  # 顶格新 key → skills 块结束
            break
        m = re.match(r"^-\s+name:\s*(\S.*?)\s*$", stripped)
        if m:
            cur = m.group(1).strip("'\"")
            table[cur] = {}
            continue
        m = re.match(r"^(owner|last_reviewed_at):\s*(\S.*?)\s*$", stripped)
        if m and cur is not None:
            table[cur][m.group(1)] = m.group(2).strip("'\"")
    return table


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

    # 1: CLAUDE.md size (unicode chars, CI 同口径)
    cmd_path = os.path.join(repo, "claude_md_team_global.md")
    L.append("## CLAUDE.md size (unicode chars)")
    if os.path.exists(cmd_path):
        c = char_count(open(cmd_path).read())
        L.append("- team-global: %d chars %s"
                 % (c, "⚠️ OVER %d" % CLAUDE_MD_CHAR_LIMIT if c > CLAUDE_MD_CHAR_LIMIT else "✅"))
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

    # 3-4: skill lint (body 体量 + skill-pack.yaml 治理表)
    skills_dir = os.path.join(repo, "skills")
    ownership = load_ownership(repo)
    L.append("## Skill lint (size + governance gaps)")
    if ownership is None:
        print("WARN: skill-pack.yaml not found at repo root — owner/last_reviewed_at checks skipped",
              file=sys.stderr)
        L.append("- ⚠️ _skill-pack.yaml not found at repo root — owner/last_reviewed_at checks skipped_")
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
            if ownership is not None:
                meta = ownership.get(name)
                if meta is None:
                    warns.append("not listed in skill-pack.yaml skills table")
                else:
                    if not meta.get("owner"):
                        warns.append("missing owner in skill-pack.yaml")
                    if not meta.get("last_reviewed_at"):
                        warns.append("missing last_reviewed_at in skill-pack.yaml")
            chars = char_count(body)
            if chars > SKILL_BODY_CHAR_LIMIT:
                errs.append("body %d chars >%d" % (chars, SKILL_BODY_CHAR_LIMIT))
            tag = "❌" if errs else ("⚠️" if warns else "✅")
            L.append("- %s **%s** (%d chars)" % (tag, name, chars))
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
