#!/usr/bin/env python3
"""validate-skills.py — skill pack 的 CI lint（单源，lint.yml 调用）。

规则（与 skills/README.md 同步）：
  frontmatter  只允许 name + description；name == 目录名
  description  单行、≤450 unicode 字符、≥2 个含 CJK 的引号触发词 + ≥2 个纯 ASCII
               引号触发词、禁 token（路径/脚本名/内部代号/变更叙事）
  body         ≤1500 unicode 字符（len(chars)，不是 wc -w —— 中文无空格）
  全文件        禁仓库相对路径（skill 目录同步走之后引用会断）
  一致性        提到的 tc-* skill 必须在包内；SKILL.md 提到的 references/ 文件必须存在；
               skill-pack.yaml 与 skills/ 目录一一对应且 owner 非空
退出码：0 = 全过；1 = 有 ERROR。WARN 不拦截。
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"
PACK = REPO / "skill-pack.yaml"

DESC_MAX = 450
BODY_MAX = 1500

# description 禁 token：发现面必须干净（去实现细节 / 内部代号 / 变更叙事）
DESC_BANNED = [
    (r"SOP v0\.\d", "SOP 版本号"),
    (r"命门", "内部代号"),
    (r"(?<![A-Za-z0-9])P-\d", "SOP 章节代号"),
    (r"rule #\d", "team-global 规则编号"),
    (r"publish\.py|transition\.py", "脚本名"),
    (r"不再|去本地", "变更叙事"),
    (r"standards/|docs/plans/|docs/research/|sop/|cases/|decisions/", "仓库路径"),
    (r"~/\.claude", "本机路径"),
]
# skill 目录内所有分发文件的禁 token：目录被单独同步后这些引用必断
FILE_BANNED = [
    (r"(?<![\w/])standards/", "仓库相对路径 standards/（单源在 tc-render/references/）"),
    (r"(?<![\w/])sop/group_sop", "仓库相对路径 sop/"),
    # docs/plans|research 是产品仓库的落盘约定:同行有"仓库"锚定词或 <skills-root> 命令上下文则放行
    (r"docs/plans/|docs/research/", "仓库相对路径 docs/（应写'当前工作仓库的 docs/…'这类锚定表述）"),
    (r"~/\.claude/skills", "写死的 skills 根路径（应使用 <skills-root> 占位符）"),
    (r"旧实测", "历史轶事（归 decisions/）"),
]

FM_ALLOWED = {"name", "description"}


def frontmatter(text: str):
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return None, text
    fm = {}
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if km:
            fm[km.group(1)] = km.group(2).strip()
    return fm, m.group(2)


def quoted_spans(desc: str):
    # 词内撇号(team's/week's)会打乱引号配对 → 先去掉再抽取
    desc = re.sub(r"(?<=[A-Za-z])'(?=[A-Za-z])", "", desc)
    return re.findall(r"[\"'‘“]([^\"'’”]{1,60})[\"'’”]", desc)


def main() -> int:
    errors, warns = [], []
    err = lambda s: errors.append(s)
    warn = lambda s: warns.append(s)

    skill_dirs = sorted(d for d in SKILLS.iterdir() if d.is_dir())
    names = {d.name for d in skill_dirs}

    # ---- skill-pack.yaml ↔ skills/ 一致性 ----
    if PACK.exists():
        pack_names = re.findall(r"^\s+- name:\s*(\S+)", PACK.read_text(), re.M)
        owners = dict(
            re.findall(r"- name:\s*(\S+)\s*\n\s*owner:\s*(\S*)", PACK.read_text())
        )
        for n in pack_names:
            if n not in names:
                err(f"skill-pack.yaml 声明了 {n} 但 skills/{n}/ 不存在")
            if not owners.get(n):
                err(f"skill-pack.yaml: {n} 缺 owner")
        for n in sorted(names - set(pack_names)):
            err(f"skills/{n}/ 存在但 skill-pack.yaml 未声明")
    else:
        err("skill-pack.yaml 缺失")

    for d in skill_dirs:
        sk = d / "SKILL.md"
        if not sk.exists():
            err(f"{d.name}: 缺 SKILL.md")
            continue
        text = sk.read_text(encoding="utf-8")
        fm, body = frontmatter(text)
        if fm is None:
            err(f"{d.name}: 无 YAML frontmatter")
            continue

        # frontmatter 白名单
        extra = set(fm) - FM_ALLOWED
        if extra:
            err(f"{d.name}: 非标准 frontmatter 字段 {sorted(extra)}（owner 等治理字段归 skill-pack.yaml）")
        if fm.get("name") != d.name:
            err(f"{d.name}: frontmatter name='{fm.get('name')}' ≠ 目录名")

        # description
        desc = fm.get("description", "").strip().strip("\"'")
        if not desc:
            err(f"{d.name}: 缺 description")
        else:
            if len(desc) > DESC_MAX:
                err(f"{d.name}: description {len(desc)} 字符 > {DESC_MAX}")
            spans = quoted_spans(desc)
            cjk_spans = [s for s in spans if re.search(r"[一-鿿]", s)]
            ascii_spans = [s for s in spans if not re.search(r"[一-鿿]", s)]
            if len(cjk_spans) < 2:
                err(f"{d.name}: description 含 CJK 的引号触发词 {len(cjk_spans)} 个 < 2")
            if len(ascii_spans) < 2:
                err(f"{d.name}: description 纯英文引号触发词 {len(ascii_spans)} 个 < 2")
            for pat, why in DESC_BANNED:
                m = re.search(pat, desc)
                if m:
                    err(f"{d.name}: description 含禁 token '{m.group(0)}'（{why}）")

        # body 预算（unicode 字符数）
        if len(body) > BODY_MAX:
            err(f"{d.name}: body {len(body)} 字符 > {BODY_MAX}（长材料移 references/）")

        # 分发文件禁 token + 引用存在性（逐行,便于放行锚定表述并给出行号）
        for f in sorted(d.rglob("*")):
            if not f.is_file() or f.suffix not in {".md", ".yaml", ".yml"}:
                continue
            for ln, line in enumerate(
                f.read_text(encoding="utf-8", errors="replace").splitlines(), 1
            ):
                for pat, why in FILE_BANNED:
                    m = re.search(pat, line)
                    if not m:
                        continue
                    if pat.startswith("docs/") and (
                        "仓库" in line or "<skills-root>" in line
                    ):
                        continue  # 产品仓库锚定路径 / 命令 cwd 相对输出,合法
                    err(f"{d.name}/{f.relative_to(d)}:{ln}: 禁 token '{m.group(0)}'（{why}）")

        # SKILL.md 里提到的本地 references/scripts 文件必须存在
        for rel in set(re.findall(r"(?:references|scripts|assets)/[\w.\-]+\.\w+", text)):
            # 指针引用其他 skill 的 references 用 "tc-render skill 的 references/x.md" 表述，
            # 判定：若本地不存在且同一行提及别的 skill 名则放行
            if not (d / rel).exists():
                lines = [l for l in text.splitlines() if rel in l]
                if any(re.search(r"tc-[a-z-]+", l.replace(rel, "")) for l in lines):
                    continue
                err(f"{d.name}: SKILL.md 引用 {rel} 但文件不存在")

        # 提到的 tc-* 必须在包内（以包内 skill 名为前缀的复合词如 verdict 枚举 tc-handoff-now 放行）
        for ref in set(re.findall(r"tc-[a-z][a-z-]*[a-z]", text)):
            if ref not in names and not any(
                ref.startswith(n + "-") for n in names
            ):
                err(f"{d.name}: 引用了包内不存在的 skill '{ref}'")

        # agents/openai.yaml（Codex 元数据）
        if not (d / "agents" / "openai.yaml").exists():
            warn(f"{d.name}: 缺 agents/openai.yaml（Codex 界面元数据）")

    for s in warns:
        print(f"WARN  {s}")
    for s in errors:
        print(f"ERROR {s}")
    print(f"\n{len(skill_dirs)} skills · {len(errors)} errors · {len(warns)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
