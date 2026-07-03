# skills/ — 团队 skill pack

13 个平级标准 skill（agentskills.io 格式）。`tc-router` 是唯一推荐的人类入口
（说「接手 issue / 继续任务 / 卡住了」它来判断下一步）；专业 skill 也允许明确触发；
`tc-render` 是工具型基座，通常由 tc-plan / tc-review / tc-handoff 调它的脚本。

包级元数据（owner / last_reviewed_at / 版本）在仓库根 [skill-pack.yaml](../skill-pack.yaml)，
包级测试在 `evals/`（skill 目录内的文件会随分发下发给 agent，测试不放进来）。

## Format（标准 skill 目录）

```
skills/<skill-name>/
├── SKILL.md              (必须: frontmatter 只有 name + description)
├── agents/openai.yaml    (Codex 界面元数据)
├── references/*.md       (长 SOP/模板/状态机表 —— body 只放指针)
├── scripts/*.py          (可执行工具, 仅 tc-render / tc-ops)
└── assets/               (静态资源, 仅 tc-render)
```

## 硬规则（CI: `python3 evals/validate-skills.py`）

- frontmatter 白名单 `{name, description}`；name == 目录名。owner 等治理字段**不进 frontmatter**
- description：单行 ≤450 字符，第三人称 WHAT + "Use when…" 双语触发词（≥2 中文 + ≥2 英文引号短语），
  禁实现细节/路径/脚本名/内部代号/变更叙事
- body ≤1500 unicode **字符**（`len(chars)` 计数——`wc -w` 对中文失效，别再用）
- 禁仓库相对路径（standards/、sop/、docs/plans/…）：skill 目录会被单独同步，仓库引用必断
- 跨 skill 脚本调用唯一写法：`python3 <skills-root>/tc-render/scripts/<script>.py …`
- 单一真相在 tc-render/references/（issue-label-state-rules / multica-fields / publish-contract），
  其他 skill 指针引用，禁复制

## 分发

- 成员机：`bash scripts/sync-team-config.sh`（软链到 `~/.claude/skills` + `~/.agents/skills`，
  Claude Code 与 Codex 同一份标准目录，无需 index 文件）
- registry：同脚本推 multica skill registry（daemon per-task 注入 + `multica skill pull` 的源）
