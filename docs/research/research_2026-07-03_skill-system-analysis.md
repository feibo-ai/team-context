# team-context Skill 体系深度分析报告

> 日期：2026-07-03 · 方法：38 个 agent 并行 —— 15 个 skill 对照官方 Agent Skills 标准逐一审计；team-context 分发管线 / tc-multica / team-context-mcp 三路源码级探查；官方文档核实；3 个独立迁移方案 + 评审合成；15 条关键事实对抗性验证（12 确认 / 3 驳倒修正）。

## 0. 结论

**目录形态已是标准格式**（`skills/<name>/SKILL.md` + 可选资源），"切换标准格式"不是根因。真正病灶：

1. **description 被实现细节污染** —— description 是 agent 发现 skill 的唯一入口（会话启动只加载 name+description），却塞满 CLI 用法、迁移变更日志、内部黑话
2. **body 超预算且 lint 假门** —— `len(text.split())*1.3` 对无空格中文失效（1500 个中文字符 ≈ 1 token），13/15 超预算未被拦截
3. **可移植性断裂** —— 仓库相对路径（`standards/*.md`）与混用的相对/绝对跨 skill 脚本路径，同步后引用全断
4. **分发"三条真相"** —— repo symlink / `~/.claude/skills` 物理副本 / multica registry 三处各自过期无信号；registry 推送截断 description 到 480 字符；Codex 靠含本机绝对路径的 skills-index.md hack

**推荐**：Multica-Registry 为分发面（git 为编写面，评分 8.0），按最小改动方案（7.5）的顺序执行第一周纯内容手术，嫁接 Plugin 方案（6.5）的 CI lint 规范。Plugin 保留为烘焙期后仍触发不佳时的升级路径。

## 1. 逐 skill 审计（可发现性评分 0-10）

| Skill | 评分 | 判词摘要 |
|---|---|---|
| tc-render | 5 | tc-render is a well-engineered shared "library skill" (two solid Python scripts with real schema validation, atomic state transitions, bundled CSS, contract YAM |
| tc-1-start | 7 | tc-1-start is a well-structured 6-step kickoff wizard with strong trigger phrases and clear step ordering, but it fails the standard on three fronts: (1) the de |
| tc-2-research | 6.5 | A well-intentioned, mostly imperative Research-phase skill with strong bilingual trigger phrases, but it violates the standard in three big ways: (1) the descri |
| tc-3-plan | 7 | tc-3-plan is a well-intentioned RPI Plan-phase skill with a serviceable description but a badly non-portable, over-budget body |
| tc-4-build | 7 | tc-4-build is a well-conceived discipline skill for the RPI Implement phase with genuinely useful, imperative rules (pre-flight checklist, scope lock, commit rh |
| tc-5-review | 7 | tc-5-review is a well-thought-out debrief/case-file skill with genuinely good trigger coverage in its description, but it fails the standard on three fronts: (1 |
| tc-handoff | 8 | tc-handoff has excellent trigger design (front-loaded bilingual trigger phrases, clear WHEN, concrete WHAT) and a well-structured imperative checklist with good |
| tc-ops | 6 | A well-built utility skill (three self-documented Python scripts replacing two low-frequency local MCP tools) with solid imperative body instructions, but three |
| tc-monday | 6.5 | tc-monday is a compact, single-file skill (/Users/mac/zzh/team-context/skills/tc-monday/SKILL.md, body 1216 chars — within the team's 1500-char budget) that enc |
| tc-friday | 7 | A well-scoped, genuinely useful ritual skill (Friday 30-min demo + 15-min betting table) with bilingual trigger phrases and a mostly-imperative, time-boxed body |
| tc-roles | 7 | A focused, genuinely useful skill (role taxonomy + assignment rules + a concrete output template) with good bilingual trigger coverage, but it has four audit-re |
| tc-conflict | 7.5 | A well-scoped, genuinely useful skill with one of the better descriptions in the standard's terms — clear WHEN clause plus front-loaded bilingual trigger keywor |
| tc-design-review | 6 | A dense, well-thought-out process-gate skill whose core problem is that it treats the description field as a second body: the 408-char description is stuffed wi |
| tc-health-check | 7 | A well-conceived self-monitoring skill with genuinely good bones: strong bilingual trigger phrases, a concrete 4-signal rubric inlined in the body (not just cit |
| tc-self-check | 7 | One of the most portable skills in this repo: the entire payload (the 10 anti-patterns, 3 red lines, and an explicit OK/FLAG/? output contract) is inlined, so i |

### 重写后的 description（15 条草稿，Week 1 PR 起点）

> 采用 YAML 折叠块（`>-`）写法，内嵌引号无需转义，可直接粘贴进 frontmatter。

#### tc-render
```yaml
description: >-
  Shared rendering and publishing base for RPI documents. Renders plan/research/case/handoff 文档为受控样式 HTML(方案A),经硬校验后作为内联评论发布到 multica issue,并原子流转 issue 状态(请审/批准/开工/收尾/取消)。Use when 需要生成或发布 plan/research/case/handoff 文档、将 HTML 内联渲染进 multica issue 评论、或变更 issue 的流程 label/status(publish, render, issue status transition)。Typically invoked by tc-2-research / tc-3-plan / tc-5-review / tc-handoff; use directly only for standalone status transitions instead of hand-typing multica issue label/status commands.
```

#### tc-1-start
```yaml
description: >-
  Guides Phase 01 kickoff of a new project-layer effort (an independent direction: 3+ days, has a DRI) through the team's 6 steps in order: intent broadcast, research session, plan session, independent review, DRI decision, kickoff broadcast. Use when the user says "启动新项目", "我想做一个新项目", "新项目立项", "kickoff", "start a new project", or "Phase 01". Not for small task-layer work — route that to tc-3-plan task-mode instead.
```

#### tc-2-research
```yaml
description: >-
  Research-phase orchestrator (RPI step 2). Use when the user says 'start research', 'Research session', '调研', '研究一下', '开始调研', or kicks off a new feature, new project, or unfamiliar problem domain that needs investigation before any plan or code exists. Spawns parallel subagents to map existing code, prior art, pitfalls, and constraints, then delivers a findings report with open questions and candidate approaches. Produces findings and options only — never plans, decisions, or code.
```

#### tc-3-plan
```yaml
description: >-
  Generates the Plan document for the Plan phase of the RPI workflow (after Research, before Build) — goal, completion criteria, who does what, and appetite — then routes it through a mandatory second-session review before any coding. Project layer gets a full plan doc; task layer a 3-sentence mini-plan. Use when the user says "write a plan", "let's plan", "Plan session", "写计划", "做个 plan", "制定计划", "规划一下", or when research is complete and planning should begin.
```

#### tc-4-build
```yaml
description: >-
  Enforces implement-phase (build session) discipline in the team's RPI workflow: pre-flight checks against the approved plan, build-start status transition and kickoff card, scope lock, commit rhythm, pollution-signal and stuck-30 handoff rules. Use when the user says '执行', '开工', '开始写代码', 'implement', or 'start coding', or when a session begins writing/running code against an approved plan. Hands off to tc-handoff on context pollution and tc-5-review on completion.
```

#### tc-5-review
```yaml
description: >-
  Runs the end-of-project or end-of-task debrief (复盘) and writes the team's five-section case file — goal recap, what happened, completion criteria met/not, key judgments, and rule candidates — then publishes it and routes it for review. Use when a project or task is wrapping up. Triggers: "复盘", "收尾", "写 case", "debrief", "wrap up", "project done", or the user states the completion criteria are met. Every project/task must end with this debrief.
```

#### tc-handoff
```yaml
description: >-
  Captures handoff state before /clear or starting a new Claude/Codex session — commits WIP and records last commit, next action, and dead ends to the plan doc and the tracking issue, so a fresh session can resume cold without losing work or repeating dead ends. Use when the user says '/clear', 'new session', 'start over', 'restart', 'I am stuck', '重开', '走偏了', '换个 session', '浑浊了', or when the current session is looping, context-polluted, or stalled with no measurable progress.
```

#### tc-ops
```yaml
description: >-
  团队运维脚本集(月度/低频):① 生成团队健康月报(CLAUDE.md token、本月规则改动、skill lint、wip 重启次数);② 全量巡检 multica issue 的 label↔status 不变量漂移;③ 按 SOP PB-04 校验 autopilot YAML guardrails。Use when 做月度 review/健康月报、backfill 或状态机改动后验收 issue 一致性、或新增/修改 autopilot YAML 之前。Triggers: "月度健康", "monthly health report", "issue 巡检", "label 漂移", "issue invariants", "autopilot lint", "校验 autopilot", "PB-04".
```

#### tc-monday
```yaml
description: >-
  Facilitates the team's weekly Monday kickoff — a 30-minute plan-alignment meeting. Use when the user mentions '周一 kickoff', 'Monday kickoff', '本周计划对齐', 'Monday meeting', or asks to run, prepare, or time-box the weekly kickoff. Guides the DRI through the timed protocol: silent reading of the week's plan roundup, per-plan walkthrough, cross-plan boundary check, and close — without re-presenting content the written plans already cover.
```

#### tc-friday
```yaml
description: >-
  Facilitates the Friday afternoon double-session: 30-min demo plus 15-min betting table. Use when the user mentions "Friday demo", "周五 demo", "周五演示", "betting table", "下周做什么", or asks to run the end-of-week demo/planning ritual. Guides the DRI through pre-flight review of cases awaiting debrief, live demos of real working artifacts (no slides, no status reports), and a betting round that decides next week's work — un-voted candidates are dropped, never moved to a backlog.
```

#### tc-roles
```yaml
description: >-
  Assigns project roles using the team's 4 role types (DRI / EXEC / COLLAB / REVIEW) and 6 assignment rules, then generates the plan doc's "How to split" section. Use when a project is kicking off and roles need to be claimed, assigned, or clarified. Triggers: 认领角色, 认领, 分工, 谁做什么, DRI 是谁, role assignment, assign roles, who is the DRI, who does what.
```

#### tc-conflict
```yaml
description: >-
  Resolves disagreements between team members over a project decision (冲突, 分歧, 意见不合, 谁说了算, conflict, disagree, deadlock, who decides). Walks the parties through four principles — debate the issue not the person, evidence over preference, the DRI makes the final call — then records the outcome, the evidence for each option, and any dissent as a dated decision document. Use when two or more members genuinely disagree on a consequential project choice or ask who has final say.
```

#### tc-design-review
```yaml
description: >-
  设计评审 / design review gate — runs between plan approval and build start, the second of three SOP review gates (①plan ②design ③code). Use when the user says '设计评审', 'design review', '方案过一下', when a project-layer plan was just approved and build has not started, or when tc-3-plan / tc-4-build point here. Mandatory at project layer, skippable at task layer. Guides the request-review transition, an independent reviewer subagent verdict, and the approve transition on the same issue.
```

#### tc-health-check
```yaml
description: >-
  Scans the current session transcript for context-pollution signals — over-agreement loops, re-proposing rejected solutions, answering the wrong question, fixing phantom issues — and outputs a per-signal report with a continue/warn/handoff verdict. Use when the conversation is going in circles, the model seems confused or too agreeable, or the user says '走偏了', '感觉不对', '怎么回事', 'going in circles', 'something feels off', or keeps rejecting the same proposed fix.
```

#### tc-self-check
```yaml
description: >-
  Self-check / 自检 / 反模式 ('反 pattern') audit: reviews the current session's working approach against the team's 10 SOP anti-patterns (self-reviewing own code, agent sprawl, CLAUDE.md bloat, capability-frontier overreach, burnout, missing DRI, etc.) plus 3 team red lines, reporting OK/FLAG/? per item. Use mid-task or at any moment of doubt — when the user asks 'am I doing this right', says '自检' or 'self check', reports something feels off, during monthly review, or whenever uncertain about the meta-approach.
```

### 完整审计明细

<details><summary><b>tc-render</b>（评分 5）</summary>

tc-render is a well-engineered shared "library skill" (two solid Python scripts with real schema validation, atomic state transitions, bundled CSS, contract YAML, and a genuine test suite) whose SKILL.md packaging fights the Agent Skills standard: the frontmatter carries two non-standard fields (owner, last_reviewed_at); the 526-char description is half implementation noise (exit codes, 命门B, P-7, file inventory) with buried triggers, unresolvable team jargon, and an already-stale subcommand count; the body is ~1989 chars against the team's own ≤1500 budget and duplicates contracts that live in PUBLISH.md/docstrings (with visible drift — it lists 7 transition subcommands while transition.py has 9, and a future-tense line contradicts the already-implemented gate-B path). Portability is the biggest risk: the dir hard-depends on the multica CLI ≥v0.4.11 and ~/.multica/config.json (acceptable, documented), but also references repo-relative standards/labels.md and scripts/create-labels.sh that vanish after sync to ~/.claude/skills/, hardcodes the ~/.claude/skills/tc-render path in usage, and ships tests that reach into sibling skill dirs (tc-handoff etc.) and a separate tc-multica repo. As a base skill mostly name-referenced by four consumer skills it will usually trigger fine, but the description should be rewritten to front-load bilingual triggers and drop mechanism detail, the body trimmed under budget, and the out-of-dir references either bundled or clearly marked as optional/non-portable.

**Frontmatter 问题**
- Non-standard extra fields present: 'owner: 曾振华' and 'last_reviewed_at: 2026-06-10'. The official standard recognizes only 'name' and 'description' (plus a small allowed set like 'allowed-tools'/'license' in some tooling); loaders may warn or reject on unknown keys. These are governance metadata, better kept in a repo-level registry/CODEOWNERS or an HTML comment in the body — flag for relocation unless the team's CI lint explicitly whitelists them.
- 'name: tc-render' is compliant: lowercase-hyphen, 9 chars ≤64, matches the directory name tc-render.
- 'description' is 526 chars — within the ≤1024 limit — and is quoted YAML, syntactically valid; quality problems are covered under description_issues.

**Description 问题**
- Severely polluted with implementation detail that belongs in the body/reference files: exit-code semantics ('exit 1', 'exit 2=评论已发但转换失败'), internal mechanisms ('命门B 收口发布', '自检 attachments', 'name→UUID 运行时解析', '后置复核 P-7'), and a file inventory ('assets/style.css(约 9KB CSS 单源)、PUBLISH.md(调用契约 + 命门A 灾备契约)'). None of this helps triggering.
- Unresolvable internal jargon at discovery time: '方案A', '命门B', '命门A', 'RPI', 'P-7' are team codewords a fresh agent cannot map to anything before the body loads — the description is not self-contained.
- Trigger phrases are not front-loaded: the WHEN clause ('Use when 生成 plan/research/case/handoff 的方案A HTML 文档并作为 multica issue 评论内联渲染发布…') is buried after a 'Shared … 地基,被 … 引用' architecture preamble.
- Internal tension for the triggering agent: it gives a 'Use when …' clause but ends with '通常由 4 个 tc-* 文档 skill 调用,不单独触发' — simultaneously inviting and discouraging direct invocation without saying when direct use IS correct (e.g. standalone status transitions).
- Factually stale: '七子命令' — transition.py now has nine subcommands (design-request-review and design-approve are missing). Baking a count into the discovery string guarantees drift.
- English-side trigger keywords are thin: 'plan/research/case/handoff', 'HTML', 'multica issue' appear, but common verbs an agent might match on ('publish', 'render', 'issue status transition', 'label') are absent in English.
- At 526 chars it is within the 1024 limit, but roughly half of it is implementation noise; the signal-to-noise ratio for a routing decision is poor.

**Body 问题**
- Body length ~1989 chars (stripped) vs team budget in skills/README.md: '目标 ≤ 1500 字（约 2000 tokens）。CI lint 强制执行硬上限。' — if 字 counts all characters the body is ~33% over budget; only if 字 counts CJK-only (442) is it compliant. Likely non-compliant; should be trimmed.
- Stale subcommand list: SKILL.md says transition.py has '七个子命令' ('publish-init / plan-request-review / plan-approve / plan-upgrade / build-start / case-finalize[--keep-parent] / cancel 七个子命令') but transition.py's docstring documents NINE, including 'design-request-review <issue>' and 'design-approve <issue>'. The body (and description) undercount and omit the design-review gate entirely.
- Stale future-tense sentence contradicts current state: line 33 '迭代2 A→B 切换后 publish.py 可改为内部调 `multica ... --inline`' reads as a pending change, but line 16 (and publish.py's docstring) say the script already 'commits 内部 exec `multica issue comment add --inline`'. Confusing to an agent deciding what to run.
- Hardcoded absolute usage path in body: '`python3 ~/.claude/skills/tc-render/publish.py ...`' assumes the synced install location; breaks when the skill is exercised from the team-context repo copy (PUBLISH.md itself hedges: 'TCR=~/.claude/skills/tc-render          # 或 team-context/skills/tc-render'). Should use a path relative to the skill directory.
- History/rationale noise consuming budget: 'TEA-103 定稿', '命门A/命门B' naming lore, '零 emoji 零 rotate', 'P-7', 'rule #6' are internal shorthand with no in-file expansion — belongs in PUBLISH.md or code docstrings, not the ≤1500-char body.
- Progressive disclosure is otherwise good (field contracts live in PUBLISH.md, disaster-recovery in publish-contract-v1.yaml), but the body still duplicates the exit-code contract, entry-transition mapping, and validation thresholds that are already in publish.py --help/docstring and PUBLISH.md — pure duplication that will drift (it already has, see the 七/九 subcommand drift).
- Body references an unresolvable external source of truth: '语义单源 = 本脚本 docstring + standards/labels.md 不变量表' — standards/labels.md is not bundled, so the claimed '单源' is unreadable after sync (see coupling).

**耦合/可移植性**
- SKILL.md line 17: 'standards/labels.md 不变量表' — repo-relative path outside the skill dir; unresolvable once synced to ~/.claude/skills/tc-render/.
- PUBLISH.md line 21: '语义单源见其 docstring + standards/labels.md' — same broken repo-relative reference.
- transition.py line 389: argparse description '(语义见模块 docstring 与 standards/labels.md)' — same reference baked into runtime --help.
- transition.py docstring: '解析失败 exit 1 并提示跑 scripts/create-labels.sh' — repo-relative scripts/ path that does not exist relative to the synced skill dir.
- SKILL.md line 23: '`python3 ~/.claude/skills/tc-render/publish.py ...`' — hardcodes the sync destination; PUBLISH.md line 15 hedges with 'TCR=~/.claude/skills/tc-render          # 或 team-context/skills/tc-render'.
- Hard runtime dependency on the multica CLI, version-gated: publish.py execs 'multica issue comment add <issue> --inline <doc>'; transition.py raises '找不到 multica CLI;先安装/更新 multica(≥v0.4.11)'; PUBLISH.md: '需 **multica CLI v0.4.11+**(`--inline` v0.4.11 · `skill pull` v0.4.12 · `skill lint` v0.4.13)' and cleanup command 'multica issue comment delete <comment_id>'; transition.py resolves labels via 'multica label list'.
- User-home state files: token read implicitly from '~/.multica/config.json' ('token 由 CLI 自管(读 `~/.multica/config.json`),绝不进脚本 argv'); publish.py writes GATE_COUNTS_PATH = os.path.expanduser("~/.multica/gate-counts.json") annotated '命门B 成功率计数(daemon 心跳读 · ⑪)' — implies an external daemon consumer.
- Cross-skill sibling coupling in tests: tests/test_publish.py sets SKILLS_ROOT = SKILL_DIR.parent, DOC_SKILLS = ["tc-2-research", "tc-3-plan", "tc-5-review", "tc-handoff"], and reads '(SKILLS_ROOT / "tc-handoff" / "SKILL.md").read_text()' — the test suite fails if the dir is copied truly standalone without its sibling skill dirs.
- Cross-REPO coupling in tests: tests/test_contract_probe.py probes 'SKILL_DIR.parents[2] / "tc-multica" / "packages/ui/markdown/file-cards.ts"' and 'Path.home() / "feibo/tc-multica/packages/ui/markdown/file-cards.ts"', overridable via env var 'FILE_CARDS_TS' (os.environ.get("FILE_CARDS_TS")); skips when unreachable, so soft coupling.
- publish-contract-v1.yaml: '权威来源:前端渲染器 packages/ui/markdown/file-cards.ts' and 'CI 探针在两仓并置(或设 FILE_CARDS_TS)时断言一致' — documentation-level pointer into another repo.
- Cross-skill behavioral references: description and body name 'tc-3-plan / tc-2-research / tc-5-review / tc-handoff'; SKILL.md line 30 delegates a validation gate: 'handoff 的 confirmDiscard 门…由 tc-handoff skill 把关'.
- cwd assumption: PUBLISH.md line 29 '`--out` 须 `.html` 且落在 CWD 允许根内(路径白名单 · 拒 `../` 与绝对逃逸)' — output path validity depends on the caller's working directory.
- Positive note: '无需 MCP 服务器' is accurate — no MCP tool coupling found; publish.py imports same-dir transition.py and assets/style.css via pathlib relative to __file__, which survives the sync correctly.

</details>

<details><summary><b>tc-1-start</b>（评分 7）</summary>

tc-1-start is a well-structured 6-step kickoff wizard with strong trigger phrases and clear step ordering, but it fails the standard on three fronts: (1) the description's tail is polluted with implementation/migration noise ("去本地MCP:用 multica CLI(project/issue create + label/status)+ tc-render/publish.py 手动编排,不再依赖 project_kickoff MCP") that belongs in the body; (2) the body is ~4,349 chars — roughly 2.9x the team's own ≤1500 字 budget stated in skills/README.md, with zero bundled reference files (everything inline, no progressive disclosure); (3) it is heavily coupled to its repo context — repo-relative paths (standards/multica-fields.md, standards/feishu-card-style.md), a mixed pair of cross-skill script paths (relative "tc-render/publish.py" vs absolute "~/.claude/skills/tc-render/transition.py" — at most one can resolve in any given deployment), the multica CLI, a remote notify_team MCP tool, and unresolvable SOP/team-global rule references. Frontmatter also carries two non-standard fields (owner, last_reviewed_at). Discovery itself works well — the WHEN and bilingual triggers are front-loaded — so triggering accuracy is good despite the noise.

**Frontmatter 问题**
- Non-standard field `owner: 曾振华` — not part of the Agent Skills spec (only name/description are standard). Ownership metadata belongs in the repo (CODEOWNERS, git history, or skills/README.md registry), not in frontmatter that may be loaded into agent context.
- Non-standard field `last_reviewed_at: 2026-06-11` — review bookkeeping belongs in CI/lint tooling or a repo-level manifest, not SKILL.md frontmatter.
- `name: tc-1-start` is compliant: lowercase-hyphen, 10 chars ≤64, exactly matches the directory name /Users/mac/zzh/team-context/skills/tc-1-start/.
- `description` is 353 unicode chars — within the 1024 limit — but has quality problems (see description_issues).
- No `allowed-tools` even though the skill drives Bash (multica CLI, python3 scripts) and a remote MCP tool (notify_team) — optional, but would document the tool surface.

**Description 问题**
- Implementation detail polluting the discovery surface: '去本地MCP:用 multica CLI(project/issue create + label/status)+ tc-render/publish.py 手动编排,不再依赖 project_kickoff MCP。' — CLI names, a cross-skill script path (tc-render/publish.py), and a migration changelog note ('不再依赖 project_kickoff MCP') are meaningless to an agent at discovery time and will rot; all of this belongs in the body.
- Not third person at the start: opens with imperative 'Use when starting…' and 'Walks through…' has no subject. Standard prefers e.g. 'Guides the user through…'.
- Unresolvable internal jargon at discovery time: 'SOP v0.4 P-3 Phase 01' and 'DRI 拍板' — the agent cannot resolve SOP/P-3 before the body loads; only 'Phase 01' earns its place as a trigger keyword.
- 'PROJECT-LAYER' is team jargon; a fresh agent can't distinguish it from e.g. 'create a new code project'. The pre-check heuristic (3+ days, has DRI) that defines project-layer sits only in the body — one clarifying clause in the description would reduce false triggers.
- Positives worth keeping: bilingual triggers ('启动新项目', 'kickoff', 'new project', 'phase 01', '我想做一个新项目') are present and front-loaded; the 6-step summary '5min intent → Research → Plan → review → DRI 拍板 → broadcast' concisely states WHAT.

**Body 问题**
- Over budget ~2.9x: body is ~4,349 unicode chars (5,615 bytes) vs the team convention in /Users/mac/zzh/team-context/skills/README.md: '目标 ≤ 1500 字（约 2000 tokens）。CI lint 强制执行硬上限。' — this file would fail the stated hard cap.
- No progressive disclosure: the directory contains only SKILL.md (no supporting *.md files), yet inlines long reference material that belongs in bundled files — the full `multica project create` flag walkthrough with defaults/confirmation protocol (Step 3 blockquote), the Feishu card layout spec for Step 6 (标题/概览 fields/内容段/note 页脚), and the entire '真验证 (SOP P-7)' checklist section.
- Historical/changelog content inline: '📌 旧实测:这些都曾静默失败(返回成功 · 产物没到位)' and the whole '⚠️ kickoff 是手动编排,不是一个工具' section largely re-explains a past migration ('没有 `project_kickoff` 单一工具了','本期删的是本地 MCP') rather than giving forward-looking instructions.
- Version-fragile instruction: '(`--start-date/--due-date/--priority` 需含项目日期字段的 CLI 版本;报 `unknown flag` 先 `multica update`。)' — couples the skill text to a specific multica CLI release state.
- Unexplained jargon an agent cannot resolve: '命门B 内联渲染评论', 'TEA-xx' issue-key format, '(team-global rule #6)' and 'SOP non-negotiable #1 gate' / '(SOP P-7)' — cite documents (claude_md_team_global.md, sop/group_sop_v0.4.md) that are neither bundled nor path-referenced.
- Mixed imperative/narrative register and dense CN/EN interleaving inside single sentences (e.g. Step 2's one-line span from 'INVOKE tc-2-research skill' through '(命门B 内联渲染评论 + 自动 `研究` label;findings 非空即 status `done`,research issue 不挂账)') hurts skimmability; steps would benefit from one-command-per-line imperatives.
- Good parts: clear pre-check gate, numbered steps run in order, an explicit Anti-patterns section, and hand-off instructions — the skeleton is right, it just needs the reference matter extracted.

**耦合/可移植性**
- Repo-relative standards paths (break when dir is copied alone to ~/.claude/skills/tc-1-start/): 'standards/feishu-card-style.md §5' (Step 1), 'standards/multica-fields.md' (Step 2: '当前用户运行时解析,不问 · standards/multica-fields.md'), '字段默认值(单源 standards/multica-fields.md)' (Step 3), 'standards/feishu-card-style.md §2/§3' (Step 6). These resolve only from the team-context repo root, which is neither the skill dir nor a guaranteed cwd.
- Cross-skill script, relative form: 'tc-render/publish.py --type research' (Step 2) and '走 `tc-render/publish.py --type plan`' (Step 3), plus '`multica project/issue create` + `tc-render/publish.py` 编排' (verification section) — resolves only if cwd is skills/ (in-repo) or ~/.claude/skills/ (post-sync); inconsistent with the absolute form used for transition.py.
- Cross-skill script, absolute form: 'python3 ~/.claude/skills/tc-render/transition.py plan-request-review <plan-issue>' (Step 4), 'python3 ~/.claude/skills/tc-render/transition.py plan-approve <plan-issue>' and 'python3 ~/.claude/skills/tc-render/transition.py cancel <plan-issue>' (Step 5) — works only after sync-to-local.sh has run and only on machines where skills live at ~/.claude/skills/; broken when working directly in the repo. Note: the relative publish.py path and the absolute transition.py path cannot both be valid in the same execution context.
- multica CLI availability assumed, exact commands: 'multica issue create --project <UUID> --title "研究:<topic>" --assignee "$ME_NAME"' (Step 2); 'multica issue create --project <UUID> --parent <research-issue> --assignee "$ME_NAME"' (Step 3); 'multica project list --full-id' ; 'multica project create --title "<意图>" --dri "$ME_UID" --lead "$ME_NAME" --start-date <YYYY-MM-DD> --due-date <YYYY-MM-DD> --priority <urgent|high|medium|low|none>' ; 'multica project update <id> --start-date … --due-date … --priority …' ; '`multica auth status`+`user list`' ; '报 `unknown flag` 先 `multica update`'.
- Runtime-resolved placeholders/env vars: '$ME_NAME' and '$ME_UID' — '当前用户经 `multica auth status`+`user list` 运行时解析,绝不硬编码'.
- Remote MCP tool assumed connected: 'notify_team({ text: "【意向】…" })' (Step 1), '`notify_team({ card: ... })` 发送' (Step 6), with the explicit note '(`notify_team` 走 **remote** MCP,非本地 —— 本期删的是本地 MCP)'.
- Removed local MCP referenced by name (historical): '不再依赖 project_kickoff MCP' (frontmatter description) and '没有 `project_kickoff` 单一工具了' (body).
- Cross-skill invocations (require sibling skills to be synced): 'INVOKE tc-2-research skill' (Step 2), 'INVOKE tc-3-plan skill' (Step 3), '用 tc-3-plan 的 task-mode' (pre-check), 'invoke tc-handoff → /clear → start Implementation per tc-4-build skill' (Hand-off), '开工时才 in_progress,见 tc-4-build' (Step 5).
- cwd/project-layout assumptions for outputs: 'Output: docs/research/research_<date>_<topic>.html' (Step 2) and 'Output: docs/plans/plan_<date>_<topic>.html' (Step 3) — assume a docs/ tree in the current working repo.
- Unbundled document references by name only: 'SOP v0.4 P-3 Phase 01' (description), '(SOP P-7)', 'SOP non-negotiable #1 gate', '(team-global rule #6)' — live in /Users/mac/zzh/team-context/sop/group_sop_v0.4.md and /Users/mac/zzh/team-context/claude_md_team_global.md, unreachable from a standalone copy.
- Platform assumption: Feishu team group as broadcast channel ('发到团队飞书群', '发「项目开工」卡到团队飞书群') via the remote notify_team MCP.

</details>

<details><summary><b>tc-2-research</b>（评分 6.5）</summary>

A well-intentioned, mostly imperative Research-phase skill with strong bilingual trigger phrases, but it violates the standard in three big ways: (1) the description is polluted with implementation and publishing internals ("tc-render 命门B (publish.py 内部 exec `comment add --inline`)", output file paths, SOP citations) that are unresolvable at discovery time; (2) the body is ~3,320 chars (~2,827 excluding whitespace), more than double the team's stated ≤1500 budget in skills/README.md, largely due to a dense inline publishing procedure that belongs in a bundled reference file or in tc-render itself; (3) it is heavily coupled to its home repo and machine — repo-relative paths (standards/multica-fields.md, docs/research/), a hardcoded cross-skill script path (~/.claude/skills/tc-render/publish.py), the multica CLI, $ME_NAME, and cross-references to tc-handoff and SOP documents — several of which break when the directory is copied standalone. The skill has only SKILL.md (no bundled files), so every external reference is a portability risk. Frontmatter also carries non-standard fields (owner, last_reviewed_at).

**Frontmatter 问题**
- Non-standard top-level fields present: `owner: 曾振华` and `last_reviewed_at: 2026-06-11`. The official standard recognizes only name, description (plus optional license/allowed-tools/metadata). These are team-governance data, not agent-facing context; move them under a `metadata:` map or into a team registry/README so lint and loaders stay spec-clean.
- name `tc-2-research` is compliant: lowercase-hyphen, 13 chars (<=64), and matches the directory name /Users/mac/zzh/team-context/skills/tc-2-research/.
- description is 569 chars, within the 1024 limit, but see description issues — length is spent on implementation noise rather than triggers.
- description mixes voice: opens with imperative 'Use when entering Research phase…' rather than consistent third person; also contains parenthetical Chinese implementation notes mid-sentence, e.g. '(publish.py 内部 exec `comment add --inline`)'.

**Description 问题**
- Implementation detail pollutes the discovery surface: 'Output: a local skeleton at docs/research/research_YYYY-MM-DD_topic.html; filled findings are published as an issue COMMENT via tc-render 命门B (publish.py 内部 exec `comment add --inline`) — never auto-uploaded to the description.' None of this helps an agent decide WHEN to trigger; it belongs in the body.
- Unresolvable references at discovery time (body not yet loaded): 'RPI framework', 'SOP v0.4 P-3 Phase 01', 'Phase 01 step 2', 'tc-render 命门B', 'publish.py'. An agent with only name+description cannot resolve any of these.
- Trigger keywords exist and are bilingual ('start research', 'let us understand', '调研', '研究一下', 'Research session') — good — but they are not front-loaded; the description leads with 'Use when entering Research phase of the RPI framework', which requires already knowing what RPI is.
- 'user explicitly invokes Phase 01 step 2' is team jargon, not a phrase a user would type; it wastes trigger budget.
- 'Required for SOP v0.4 P-3 Phase 01' is a compliance note, not a trigger or capability statement; also creates a stale-version hazard (SOP version pinned in a description).
- Mentions '命门B' — internal codename with no meaning outside the team repo; violates self-containment.

**Body 问题**
- Over the team budget: body is 3,320 characters (2,827 excluding whitespace) vs the /Users/mac/zzh/team-context/skills/README.md rule '目标 ≤ 1500 字（约 2000 tokens）。CI lint 强制执行硬上限。' — more than 2x over.
- No progressive disclosure: the dense publishing procedure (the blockquote starting '文档怎么进 issue（经 tc-render · 不再走 research_create / doc_publish MCP · append-only 评论制）' through 'projectId 一律完整 UUID（8 位短 ID 报 400 · rule #6）') is ~1,100 chars of reference material inlined into SKILL.md. It should be a separate bundled file (e.g. publishing.md) or, better, owned solely by the tc-render skill and referenced by name — the dir currently contains only SKILL.md.
- Duplicates the tc-render publish contract (dry-run flow, auto 'label' add, status→done rule, 'exit 2 = 评论已发但转换失败…绝不重跑 publish'), creating drift risk with /Users/mac/zzh/team-context/skills/tc-render/PUBLISH.md and publish-contract-v1.yaml.
- Internal contradiction in Output: the section shows a Markdown-style skeleton ('# Research: <topic>' etc.) for a file named docs/research/research_YYYY-MM-DD_<topic>.html, while step 3 of the blockquote says the HTML skeleton is generated by publish.py --dry-run. Two competing flows for producing the same artifact.
- Unexplained jargon in body: 'SOP ❌6 anti-pattern', 'rule #6' (cited twice), 'DRI', '命门B', '反白格', '不挂账' — none defined or linked in a resolvable way.
- Uncited statistic presented as fact: 'using AI beyond frontier raises error rate by 19 percentage points — BCG 2024' with no bundled source.
- Positives: instructions are otherwise imperative and well-structured (Mandate, Entry criteria, mandatory first question, dispatch pattern, 30-40% context budget, explicit NOT-do list, hand-off), which matches the standard's style guidance.

**耦合/可移植性**
- Repo-relative path (breaks when synced standalone to ~/.claude/skills/tc-2-research/): '配方与字段默认值见 standards/multica-fields.md' — resolves only inside /Users/mac/zzh/team-context/.
- Cross-skill hardcoded script path: '调 `python3 ~/.claude/skills/tc-render/publish.py --type research --data fields.json --dry-run --out docs/research/research_<YYYY-MM-DD>_<topic>.html`' — assumes tc-render is synced to ~/.claude/skills/tc-render/ and python3 is on PATH.
- Cross-skill invocation: 'When done: invoke tc-handoff skill → `/clear` → open Plan session' — assumes the tc-handoff skill is installed.
- multica CLI commands (assumes CLI installed + authenticated): '`multica project list --full-id` 取完整 UUID', '或 `multica project create`', '`multica issue create --project <UUID> --title "研究:<topic>" --assignee "$ME_NAME"`', plus the description's 'publish.py 内部 exec `comment add --inline`'.
- Env var assumption: '--assignee "$ME_NAME"（当前用户运行时解析、不问…）' — requires $ME_NAME to be set in the runtime environment.
- cwd assumption: output paths 'docs/research/research_YYYY-MM-DD_<topic>.html' (description and body) and 'Output target: a section in docs/research/research_<date>_<topic>.html' assume the session cwd is a project repo containing docs/research/; 'fields.json' is written relative to cwd.
- External SOP document references not bundled: 'Required for SOP v0.4 P-3 Phase 01' (description) and 'Reason: SOP ❌6 anti-pattern' (body) — live in /Users/mac/zzh/team-context/sop/, unreachable from a standalone copy.
- External rule-set reference: '绝不建孤儿 issue（rule #6）' and '（8 位短 ID 报 400 · rule #6）' — 'rule #6' is defined somewhere outside the skill dir (team global CLAUDE.md), unresolvable standalone.
- tc-render behavioral contract dependency: '脚本渲染 + 命门B 发评论（内联渲染 · 自检 attachments）+ 入口状态转换' and 'exit 2 = 评论已发但转换失败，按 stderr 补救，绝不重跑 publish' — depends on tc-render publish.py/transition.py semantics staying exactly as described.
- Description itself couples to tc-render: 'published as an issue COMMENT via tc-render 命门B (publish.py 内部 exec `comment add --inline`)' — the discovery surface breaks if tc-render changes.

</details>

<details><summary><b>tc-3-plan</b>（评分 7）</summary>

tc-3-plan is a well-intentioned RPI Plan-phase skill with a serviceable description but a badly non-portable, over-budget body. The frontmatter carries two non-standard fields (owner, last_reviewed_at). The description front-loads phase context and some triggers but is second-person ("Use when..."), leans on unresolvable internal jargon ("Phase 01 step 3", "SOP v0.4", "SOP non-negotiable #1"), and offers only one Chinese trigger phrase. The body is 5,457 chars — roughly 3.6x the team's own ≤1,500-char budget stated in skills/README.md, which claims CI lint enforces a hard cap — with zero progressive disclosure: two full templates, the entire multica publish runbook, review-gate protocol, and status-transition rules are all inline, salted with change-log narration about retired MCP tools. Portability is the critical failure: the skill hard-depends on the multica CLI, the $ME_NAME env var, the sister skill tc-render at ~/.claude/skills/tc-render/ (publish.py, transition.py), the repo-relative standards/multica-fields.md (unresolvable once the dir is synced to ~/.claude/skills/tc-3-plan/), cwd-relative docs/research/ and docs/plans/ paths, and four other skills (tc-handoff, tc-design-review, tc-4-build, daily-kickoff). Copied standalone, steps 1-4 of its core workflow cannot execute without the whole ecosystem in place, and nothing in the body states these prerequisites or a fallback.

**Frontmatter 问题**
- Non-standard fields present: `owner: 曾振华` and `last_reviewed_at: 2026-06-11`. The Agent Skills spec recognizes only name, description, and optional fields like license/allowed-tools/metadata. These add discovery-time context weight with zero trigger value. Move them under a `metadata:` map if team tooling needs them, or track ownership/review dates in git history or a team registry instead.
- name `tc-3-plan` is compliant: lowercase-hyphen, 9 chars, matches directory name.
- description is 449 chars — within the 1024-char spec limit (content issues listed separately).

**Description 问题**
- Not third person: opens with imperative second-person 'Use when entering Plan phase of RPI framework' instead of describing what the skill does.
- Unresolvable internal reference at discovery time: 'user invokes Phase 01 step 3' — an agent that has only loaded name+description cannot know what 'Phase 01 step 3' refers to; it depends on team docs the agent may never load.
- Version-pinned internal jargon that will go stale and has low trigger value: 'SOP v0.4', 'Required for SOP non-negotiable #1 (Plan Mode — never vibe code)'.
- Implementation detail leaking in: the field enumeration '(goal / completion criteria / who does what / appetite)' and output format '(HTML)' belong in the body, not the discovery surface.
- Thin bilingual coverage: only one Chinese trigger ('做个 plan'); missing common phrases like 写计划, 制定计划, 规划, 写个方案 that Chinese-speaking teammates would actually type.
- Trigger phrases are not front-loaded — the WHAT ('Generates a plan doc') arrives in the third sentence, after framework context and the trigger list.
- Understates the skill's real effect: it also creates a multica plan issue, publishes as an issue comment, and drives a review state machine — the description says only 'Generates a plan doc (HTML)'. (Minor; full mechanics rightly belong in the body, but 'and routes it through review' would set expectations.)

**Body 问题**
- Body is 5,457 chars (4,667 excluding whitespace) — ~3.6x the team's stated budget in skills/README.md ('目标 ≤ 1500 字（约 2000 tokens）。CI lint 强制执行硬上限'). This skill should fail the team's own CI lint.
- No progressive disclosure despite the dir supporting bundled files: both markdown templates (project + task layer), the full 4-step multica publish runbook, the review-gate protocol, and the approval state-transition rules are all inline. Templates and the publish/transition procedures should be split into supporting files (e.g. templates.md, publishing.md) loaded on demand.
- Change-log/deprecation narration wastes budget and confuses fresh agents: heading '## 产出与发布(经 tc-render · 不再走 plan_create MCP)', '**更新(原 plan_upgrade)**', '(脚本原子收口 · 取代散文 bash 块)' — references to retired MCP tools mean nothing to an agent that never saw the old version.
- Language flips from English (Mandate through templates) to dense Chinese (publish/review/transition sections) mid-document; the Chinese steps use deeply nested parentheticals (e.g. step 2 and step 3 of 产出与发布) that are hard to execute reliably.
- Duplication: handoff appears both inside the project template ('Current State (handoff slot — see tc-handoff skill)') and in '## Hand-off to Implement'; approval mechanics are split across '## Review gate' and '### 批准状态转换'.
- Scope creep into other skills' territory: task-layer execution policy ('任务层执行默认派执行子 agent…编排 session 审 diff、跑状态转换、commit') belongs to tc-4-build, and the design-review gate paragraph ('批准后下一道门:设计评审…') belongs to tc-design-review — both duplicated here.
- No prerequisite/fallback statement: the body assumes tc-render is installed, multica CLI is on PATH, and $ME_NAME is set, but never says so or tells the agent what to do if they are missing.
- Positive: instructions are largely imperative, the good/bad examples for Goal and Completion criteria are effective, and the Anti-patterns section is concise.

**耦合/可移植性**
- Line 17-18 (cwd-relative input path): 'Read `docs/research/research_<date>_<topic>.html` as input' — assumes cwd is the project repo.
- Line 66 (template, cwd-relative path): 'docs/research/research_YYYY-MM-DD_<topic>.html'
- Line 76 / 152 (cross-skill): 'Current State (handoff slot — see tc-handoff skill)' and 'invoke tc-handoff → `/clear` → open Implement session'
- Line 91 (retired MCP tool reference): '不再走 plan_create MCP'; line 100: '(原 plan_upgrade)'
- Line 93 (cross-skill at fixed install path): '走共享地基 **tc-render**(`~/.claude/skills/tc-render/`)' — depends on the sync script having installed the sibling skill to that exact location.
- Line 95 (multica CLI): '`multica project list --full-id` 取**完整 UUID** 作 projectId' and '要不要 `multica project create` 新建?'
- Line 96 (multica CLI + env var): '`multica issue create --project <UUID> --title "计划:<slug>" --assignee "$ME_NAME" [--parent <research-issue-id>]`' — requires multica on PATH and $ME_NAME resolved at runtime.
- Line 96 (repo-relative doc outside skill dir): '配方见 standards/multica-fields.md' — resolves only from the team-context repo root (/Users/mac/zzh/team-context/standards/multica-fields.md); breaks from ~/.claude/skills/tc-3-plan/ and from any project cwd.
- Line 98 (cross-skill script + cwd-relative output): '`python3 ~/.claude/skills/tc-render/publish.py --type plan --data fields.json --issue <issue-UUID> --out docs/plans/plan_<YYYY-MM-DD>_<slug>.html`' — tc-render script at fixed home path, fields.json in cwd, docs/plans/ repo-relative.
- Line 100 (bare cross-skill script name): '先 `transition.py plan-upgrade`(摘已批准 · 加已升级+草稿 · 回 todo)'
- Line 112 (cross-skill script): '`python3 ~/.claude/skills/tc-render/transition.py plan-request-review <plan-issue>`'
- Line 133 (cross-skill script): '`python3 ~/.claude/skills/tc-render/transition.py plan-approve <plan-issue>`'
- Lines 136-138 (cross-skill + external routine): '`in_progress` 由 build session 开工时 `transition.py build-start` 设置(见 tc-4-build)——daily-kickoff 的「待启动」桶(`计划-已批准`+`todo`)依赖此语义' — couples to tc-4-build and a daily-kickoff routine.
- Lines 141-143 (cross-skill): '写码前走 `tc-design-review` skill(`design-request-review` → 设计评审子 agent → `design-approve`),通过后才到 tc-4-build `build-start`'
- Lines 95-139 (workspace label/status schema): label names `计划-草稿`, `计划-评审中`, `计划-已批准`, `计划-已升级` and statuses `todo`/`in_review`/`in_progress` — depend on the multica workspace schema documented in the repo's standards/labels.md, external to this skill dir.

</details>

<details><summary><b>tc-4-build</b>（评分 7）</summary>

tc-4-build is a well-conceived discipline skill for the RPI Implement phase with genuinely useful, imperative rules (pre-flight checklist, scope lock, commit rhythm, pollution signals, handoff points), but it fails the standard on three fronts. Frontmatter carries two non-standard fields (owner, last_reviewed_at). The body is 3,366 chars — roughly 2.2x the team's own ≤1500-char budget stated in skills/README.md — with zero bundled reference files, so all detail is inline or delegated to repo-external docs. Most critically, the skill is not portable: it hard-depends on a sibling skill's script (~/.claude/skills/tc-render/transition.py, which itself requires the multica CLI ≥v0.4.11), a remote MCP tool (notify_team), repo-relative docs (standards/feishu-card-style.md, sop/ playbooks), multica workspace labels/statuses, and four other tc-* skills — none of which travel with the directory when synced standalone. The description is serviceable (444 chars, has bilingual triggers) but front-loads team jargon ("RPI framework") instead of trigger phrases, includes only one Chinese trigger, and leaks mechanism names ("30-second CoT supervision, ESC patterns") that belong in the body.

**Frontmatter 问题**
- `name: tc-4-build` is compliant: lowercase-hyphen, matches directory name, ≤64 chars.
- `description` is 444 chars, within the ≤1024 limit.
- Non-standard field `owner: 曾振华` — not part of the official Agent Skills frontmatter (name + description, plus optionally allowed-tools/license/metadata). Agents never see it; strict validators may reject unknown top-level keys. Belongs under a `metadata:` map or in repo governance (README/CODEOWNERS), not as a top-level field.
- Non-standard field `last_reviewed_at: 2026-06-11` — same problem; review provenance is repo/CI metadata, not skill frontmatter. Move to a metadata map or a team manifest that the sync script strips.

**Description 问题**
- Trigger keywords are not front-loaded: the description opens with 'Use during Implement phase of RPI framework' — 'RPI framework' is team jargon an agent cannot resolve at discovery time; the actual triggers ('执行', 'implement', 'start coding') only appear mid-string.
- Only one Chinese trigger ('执行') despite the body being built around '开工' — missing '开工', '开始写代码', '实现' as trigger phrases.
- Implementation detail leaks into the discovery surface: 'Enforces 30-second CoT supervision, ESC patterns, pollution signal detection' names internal mechanisms meaningless before the body loads; 'approved plan doc (HTML) loaded' is a format detail that belongs in the body's pre-flight section.
- Not self-contained: 'Pairs with tc-handoff skill on context pollution' references a sibling skill the agent may not have installed and cannot resolve at discovery time.
- Voice is inconsistent: starts imperative ('Use during...') and shifts to second person ('or you are in a Claude Code session...') rather than consistent third person.
- Positive: it does state both WHAT (enforces implement-session discipline) and WHEN (execution session against an approved plan), and includes concrete trigger words — better than most.

**Body 问题**
- Body is 3,366 characters — over 2x the team's stated budget in skills/README.md ('目标 ≤ 1500 字（约 2000 tokens）。CI lint 强制执行硬上限。'). Non-compliant with the team's own convention.
- No progressive disclosure: the directory contains only SKILL.md (no bundled reference files). Long procedural material (the 开工卡 Feishu card skeleton, transition semantics, SOP rules) is either inline or delegated to repo-external files ('骨架与纪律见 standards/feishu-card-style.md §2/§3') that do not travel with the skill.
- Mixed audience: several rules instruct the human operator, not the agent — 'First 30s of every Claude tool-call sequence: read the chain-of-thought. If direction is wrong, hit ESC' and 'a human eye must see the diff before commit' are things Claude cannot execute about itself. A skill body is agent-facing prompt material; human-operator SOP belongs in the sop/ docs.
- Mid-document language switching (English sections 'Mandate'/'30-second rule' interleaved with Chinese sections '开工:状态转换 + 广播'/'子 agent 杠杆') makes the body harder to lint and inconsistent in register.
- Unresolvable citations with no bundled source: 'SOP "AI generated but YOU ship it" liability', 'SOP P-4 "start over beats fix"', 'greenfield playbook (PB1)'.
- Positives: instructions are largely imperative and checklist-shaped; the 'What this session does NOT do' anti-scope section and explicit handoff points (tc-handoff, tc-5-review) are good practice.

**耦合/可移植性**
- Cross-skill script (hard runtime dependency): 'python3 ~/.claude/skills/tc-render/transition.py build-start <plan-issue>' — assumes the tc-render skill dir is synced alongside; transition.py in turn requires the multica CLI ('找不到 multica CLI;先安装/更新 multica(≥v0.4.11)') plus standards/labels.md label definitions.
- Second reference to the same script in the 子 agent section: '编排 session 只做 pre-flight、审 diff、跑 transition.py、commit'.
- Repo-relative doc path, absent from skill dir: '骨架与纪律见 standards/feishu-card-style.md §2/§3'.
- Remote MCP tool: '`notify_team({ card: ... })` 发送' — provided by the tcmcp-remote Feishu MCP server (per docs/SYNC.md), must be configured in the client.
- Cross-skill reference: 'invoke tc-handoff' (appears 4x in body, plus 'Pairs with tc-handoff skill' in the description).
- Cross-skill reference: '设计评审门已过 · 见 tc-design-review'.
- Cross-skill reference: '批准时不设(见 tc-3-plan「批准 ≠ 开工」)'.
- Cross-skill reference: 'invoke tc-5-review skill' (Hand-off to Debrief).
- Autopilot coupling: 'daily-kickoff「进行中/待启动」两桶依赖此语义' — depends on autopilots/daily-kickoff.yaml behavior in the parent repo.
- multica workspace label/status semantics baked in: 'work issue 带 `设计-已审`', '`设计-待审` 在场 = 评审中,不得开工', 'plan issue `todo`(批准后的待启动)→ `in_progress`' — labels defined in standards/labels.md, statuses in the multica workspace.
- multica issue-prefix assumption: 'TEA-xx + 已批准' and '进度看 TEA-xx' in the kickoff card template.
- SOP doc references (sop/ dir, not bundled): 'SOP "AI generated but YOU ship it" liability', 'SOP P-4 "start over beats fix"', 'Upgrade to greenfield playbook (PB1)'.
- Claude Code harness command assumption: '`/clear`' (acceptable for the target platform, noted for completeness).
- Artifact-format assumption: 'Plan doc (HTML) is loaded' — presumes the tc-render/publish.py HTML publishing flow produced the plan.

</details>

<details><summary><b>tc-5-review</b>（评分 7）</summary>

tc-5-review is a well-thought-out debrief/case-file skill with genuinely good trigger coverage in its description, but it fails the standard on three fronts: (1) non-standard frontmatter fields (owner, last_reviewed_at); (2) a body at ~4390 chars, nearly 3x the team's own stated ≤1500-char budget with zero progressive disclosure (single SKILL.md, no bundled reference files, dense one-line fields.json schema, historical changelog noise about deprecated MCP tools and past incidents TEA-95/70); and (3) heavy, portability-breaking coupling — it hard-depends on the sibling tc-render skill's publish.py/transition.py at ~/.claude/skills/tc-render/, the multica CLI, a $ME_NAME env var, repo-relative paths (cases/, standards/multica-fields.md, claude_md_team_global.md), and unresolvable SOP section references. The cross-skill ~/.claude path survives the sync-to-local copy but silently breaks in the multica-workspace sync or any standalone copy; the repo-relative paths break the moment cwd is not the team-context repo root. The description's biggest discovery gap is omitting '复盘' — the exact Chinese term the body itself uses for the deliverable.

**Frontmatter 问题**
- Non-standard field `owner: 曾振华` — not part of the Agent Skills frontmatter standard (only name/description plus a small allowed set). Team-governance metadata; belongs in skills/README.md, a CODEOWNERS-style file, or a `metadata:` map if the harness tolerates one — not as a top-level frontmatter key.
- Non-standard field `last_reviewed_at: 2026-06-11` — same problem; review bookkeeping should live outside frontmatter (git history already records it).
- `name: tc-5-review` is compliant (lowercase-hyphen, ≤64 chars, matches directory name) but semantically opaque: 'review' here means post-project debrief, yet the name reads like code review and collides conceptually with the built-in /review and /code-review skills. Since only name+description are loaded at discovery, the name contributes zero useful keywords; the description must carry everything.
- Description is 316 chars — within the ≤1024 limit; the quoted-string YAML is valid.

**Description 问题**
- Missing the single most likely Chinese trigger word: '复盘'. The body uses it everywhere ('复盘:<slug>', '复盘-待审', '复盘-已审') but the description's trigger list is 'let us debrief', '收尾', 'wrap up', '写 case', 'project done' — a user saying '来复盘一下' may not trigger the skill.
- Implementation detail pollution: 'Generates a case file at cases/YYYY-MM-DD-<slug>.html' bakes an exact repo-relative output path into the discovery surface; the path belongs in the body.
- Unresolvable references at discovery time: 'the 5 mandatory SOP v0.4 sections' and 'Required for SOP non-negotiable #2' point at an SOP document the agent has not loaded and cannot resolve when scanning descriptions; the version pin 'v0.4' will also rot.
- WHAT is stale/partial relative to the body: the description says it generates a file at cases/, but per the body the primary deliverable is an HTML case published as an append-only comment on a multica issue via tc-render (the file is a --out side artifact) plus a review handoff — the description undersells/misstates the action.
- Opens with 'Use when...' (WHEN before WHAT, imperative rather than third person); the WHAT ('Generates a case file...') only arrives mid-description. Acceptable in practice but not the third-person WHAT-first form the standard asks for.

**Body 问题**
- Budget violation: body is ~4390 characters (~3751 non-whitespace) vs the team's stated budget in skills/README.md ('目标 ≤ 1500 字（约 2000 tokens）。CI lint 强制执行硬上限。') — roughly 2.9x over.
- No progressive disclosure: the directory contains only SKILL.md. The fields.json schema, publish/transition procedure, hard-validation rules, promotion procedure, and reviewer-subagent protocol are all inline; the standard (and the over-budget size) call for moving reference material to bundled files — especially since tc-render already ships PUBLISH.md and publish-contract-v1.yaml that this body partially duplicates, creating drift risk.
- The entire fields.json contract is crammed into one parenthetical run-on line (line 25: `goal` / `whatHappened`(均收 string 或 string[]...) / `criteriaResults`[{criterion,met,notMetReason}] ... / `keyJudgments`[{title,context,options,chose,inHindsight,ancientImpossible}] ...) — extremely dense, error-prone to parse; should be a code block/table or deferred to the tc-render contract file.
- Historical/changelog noise a fresh agent cannot use: '不再走 case_create MCP', '去本地MCP · 原 case_promote_rule,手动做', and '旧版「等第二 session 评审通过后(再找人跑)」的无主窗口即 TEA-95/70 漂移根因' reference deprecated tools and past incident IDs (TEA-95, TEA-70) from an external tracker.
- Re-states validation rules that are declared to live in publish.py ('硬校验(publish.py 内建 · exit 1 硬挡)') — duplicating enforced-by-script rules in prose invites drift; the body should state the intent and point at the script as source of truth.
- Inconsistent bilingual voice: template/section content in English, all operational pipeline sections in dense Chinese with heavy inline symbols (· ①②③) — legal but hurts maintainability and skimmability.
- Positives worth keeping: instructions are largely imperative, the 5-section template with anti-patterns and the ≥100-char key-judgments floor are concrete and testable, and exit-code recovery guidance (exit 2 = comment posted but transition failed, never re-run publish) is exactly the right kind of body content.

**耦合/可移植性**
- Cross-skill dependency (line 21): '走共享地基 **tc-render**(`~/.claude/skills/tc-render/`)' — assumes the sibling skill tc-render is synced to ~/.claude/skills/; breaks in any environment where only tc-5-review is copied.
- Cross-skill script call (line 26): 'python3 ~/.claude/skills/tc-render/publish.py --type case --data fields.json --issue <case-issue-UUID> --out cases/<YYYY-MM-DD>-<slug>.html' — depends on tc-render's publish.py AND on cwd being the team-context repo root (repo-relative --out cases/... and fields.json written to cwd).
- Cross-skill script call (line 90): 'python3 ~/.claude/skills/tc-render/transition.py case-finalize <case-issue>' (plus '--keep-parent' variant, line 91).
- multica CLI availability (line 23): 'multica project list --full-id'.
- multica CLI + env var (line 24): 'multica issue create --project <UUID> --title "复盘:<slug>" --assignee "$ME_NAME" [--parent <plan-issue-id>]' — assumes `multica` on PATH and `$ME_NAME` set in the environment.
- Repo-relative reference doc (line 24): 'standards/multica-fields.md' — resolves only from the team-context repo root; dead path from ~/.claude/skills/tc-5-review/.
- Repo-relative output paths (lines 16-17 and description): 'cases/YYYY-MM-DD-<project-slug>.html' and 'cases/YYYY-MM-WW-tasks.html' — assume cwd = team-context repo.
- Repo-root file mutation (line 67): '追加到 `claude_md_team_global.md` 的「## Claude 不能再犯的错」段末' — repo-relative path to a red-line file outside the skill dir.
- SOP document references not bundled: 'SOP v0.4 sections' (frontmatter description), 'SOP non-negotiable #2' (description), 'Promotion rule (SOP P-4)' (line 64), '原子做完并复核(P-7)' (line 93), '绝不建孤儿 issue(rule #6)' (line 23) — all point at sop/ content that does not travel with the skill.
- Deprecated/removed MCP tools referenced by name: 'case_create MCP' (line 19, '不再走 case_create MCP') and 'case_promote_rule' (line 66, '去本地MCP · 原 case_promote_rule') — historical coupling to tooling that no longer exists.
- External issue-tracker IDs (line 88): 'TEA-95/70 漂移根因' — unresolvable without the team's tracker.
- Harness capability assumption (lines 83-85): '当前(编排)session 立即派评审子 agent(全新上下文,role = DRI 代理/staff engineer)' — assumes the runtime can spawn sub-agents with fresh context.
- Upstream artifact dependency: 'Copy the original goal from the plan doc (HTML) verbatim' (line 34) and '只给 case HTML + plan 文档路径' (line 84) — depends on tc-3-plan's HTML plan output existing and being locatable.

</details>

<details><summary><b>tc-handoff</b>（评分 8）</summary>

tc-handoff has excellent trigger design (front-loaded bilingual trigger phrases, clear WHEN, concrete WHAT) and a well-structured imperative checklist with good anti-patterns — but it fails the team's own body budget by ~2.5x (≈3,915 chars vs ≤1500 字 hard cap), carries two non-standard frontmatter fields (owner, last_reviewed_at), pollutes the description tail with unresolvable SOP compliance codes, and is critically non-portable: it hard-depends on the tc-render skill being installed at ~/.claude/skills/tc-render/publish.py, on the multica CLI, on a docs/plans/ repo layout, and on internal jargon ("命门B", "防 ③ 回归", "PB1", "session_handoff MCP") that a standalone copy cannot resolve. The fix is mechanical: strip frontmatter extras, cut the SOP clause from the description, move the Current State template and the publish.py contract details into bundled reference files (progressive disclosure), and replace the inline duplication of tc-render's contract with a pointer plus a graceful fallback when tc-render/multica are absent.

**Frontmatter 问题**
- Non-standard field `owner: 曾振华` — not part of the Agent Skills frontmatter spec (name/description [+ allowed-tools]); belongs in the team's skills/README registry or a `metadata:` map, not top-level frontmatter.
- Non-standard field `last_reviewed_at: 2026-06-09` — same problem; review metadata should live outside frontmatter (registry, git history, or metadata map). Also unquoted, so YAML parses it as a date object, not a string — a lint hazard.
- `name: tc-handoff` is compliant: lowercase-hyphen, 10 chars ≤64, matches directory name /Users/mac/zzh/team-context/skills/tc-handoff/.
- `description` is 434 chars (≤1024, compliant on length) but opens in second-person imperative ('Use BEFORE running /clear…') instead of third person as the standard requires.
- Description ends with 'Required for AI MIQ SOP v0.4 P-2 / P-4 / Daily 02 / Daily 03 compliance.' — internal compliance codes that are unresolvable at discovery time and add no triggering value; belongs in the body if anywhere.

**Description 问题**
- Voice: 'Use BEFORE running /clear, starting a new Claude/Codex session…' is imperative/second person; the standard wants third person ('Captures…', 'Use when…' pattern applied to the skill, not the reader).
- Unresolvable reference at discovery time: 'Required for AI MIQ SOP v0.4 P-2 / P-4 / Daily 02 / Daily 03 compliance.' — an agent seeing only name+description cannot resolve 'AI MIQ SOP v0.4', 'P-2', 'P-4', 'Daily 02/03'; pure noise on the discovery surface.
- Minor implementation leak: 'Captures handoff state to the plan doc (HTML) + the multica issue' — the '(HTML)' file-format detail belongs in the body, not the description.
- Strengths (keep these): trigger phrases are bilingual and front-loaded ('I am stuck', '走偏了', '换个 session', '重开', 'start over', 'restart', '浑浊了', 'new session', '/clear'); WHAT ('Captures handoff state… commits WIP') and WHY ('so the new session can resume without losing work or repeating dead ends') are both stated. A code agent would trigger this correctly in most restart scenarios.
- The trigger list is buried inside a parenthetical mid-sentence; splitting WHEN triggers from WHAT would scan better, but this is stylistic.

**Body 问题**
- Body budget violation: ≈3,915 chars including whitespace (3,241 non-whitespace) vs the team's stated hard cap in skills/README.md ('目标 ≤ 1500 字（约 2000 tokens）。CI lint 强制执行硬上限。') — roughly 2.4–2.6x over; per the README this should fail CI lint.
- No progressive disclosure despite over-budget body: the directory contains ONLY SKILL.md. The Current State template block (step 4) and the entire publish.py invocation contract in step 5 (fields.json schema, --type flags, idempotency gate) are prime candidates for bundled reference files (e.g. handoff-template.md, publish-howto.md).
- Step 5 duplicates tc-render's publish contract inline ('把 `{slug, at, lastCommit, branch, done, nextAction, deadEnds, pollutionSignal}` 写成 `fields.json`（done/nextAction 收 string 或 string[]…）') — this schema is owned by tc-render (publish-contract-v1.yaml / PUBLISH.md) and will drift; should be a pointer, not a copy.
- Dangling internal jargon a fresh agent cannot resolve: '命门B 收口', '净损失须复刻', '防 ③ 回归' (what is ③?), '原 session_handoff <60s 幂等门' — historical provenance notes referencing a retired 'session_handoff MCP' appear three times and bloat the operational checklist without being actionable.
- 'Look in `docs/plans/` for the .html file with most recent mtime' — assumes every target repo has a docs/plans/ layout and cwd = repo root; only fallback is 'ask'.
- Escalation section references 'greenfield playbook (PB1)', 'Research session', 're-Plan' with no path or link — resolvable only by someone who knows the team's tc-1..tc-5 skills and sop/ docs.
- The <60s idempotency gate is specified to the second ('若是，拒绝重复 handoff…refusing duplicate within 60s') but gives no concrete command for how to check the last handoff timestamp.
- Positives: instructions are imperative and ordered (Checklist 1–6); the anti-patterns and cost-reminder sections are genuinely useful; the git-hygiene guidance ('绝不 `git add -A`', discard-only-with-confirmation) is precise and safe.

**耦合/可移植性**
- Cross-skill hard dependency (breaks if tc-handoff is synced alone): '调 `python3 ~/.claude/skills/tc-render/publish.py --type handoff --data fields.json --issue <id>`' — requires the tc-render skill to be installed at ~/.claude/skills/tc-render/ with its publish.py present.
- Second use of the same script: '用 `publish.py --type plan` **再发一条新 plan 评论**' — same tc-render dependency.
- Prohibition that only makes sense with tc-render present: '**禁止**用裸 markdown 评论绕开 publish.py 硬校验（无快捷旁路 · 防 ③ 回归）' — no fallback path if publish.py is unavailable.
- multica platform dependency: '### 5. Persist to the multica issue（经 tc-render 命门B 收口 · 不再走 session_handoff MCP）' — assumes work is tracked in multica and issue IDs are available ('`--issue` 一律完整 UUID').
- multica CLI availability: '`multica issue runs <id>` will show the pattern' — assumes the multica CLI is on PATH in the target environment.
- Retired MCP tool referenced for provenance (unresolvable standalone): '不再走 session_handoff MCP', '原 session_handoff <60s 幂等门 · 净损失须复刻', '原 session_handoff 重生成 plan 行为 · 可选'.
- Repo-layout assumption: 'Look in `docs/plans/` for the .html file with most recent mtime matching this work' — repo-relative path, assumes cwd is a project root using this convention.
- SOP document dependency (lives in team-context/sop/, not bundled): frontmatter 'Required for AI MIQ SOP v0.4 P-2 / P-4 / Daily 02 / Daily 03 compliance' and body 'SOP v0.4 makes this the most common operation'.
- Playbook/workflow references with no bundled source: 'upgrade to greenfield playbook (PB1), re-do Research session, re-Plan from scratch' — resolvable only via the team's other skills (tc-2-research, tc-3-plan) or sop/ docs.
- tc-render contract jargon: '命门B' (gate B) — defined in tc-render's PUBLISH.md / publish-contract-v1.yaml, not in this skill dir.
- Team process reference: 'Touch CLAUDE.md here (CLAUDE.md changes go through monthly review)' — assumes knowledge of the team's monthly-review process.
- Scratch-file assumption: '把 …写成 `fields.json`' — writes fields.json with no specified location, implicitly assuming a writable cwd.

</details>

<details><summary><b>tc-ops</b>（评分 6）</summary>

A well-built utility skill (three self-documented Python scripts replacing two low-frequency local MCP tools) with solid imperative body instructions, but three real defects: (1) the description completely omits issue_invariants.py — a third of the skill and the one marked "月度 review 必跑" — so an agent asked to audit issue label/status consistency would never discover it; (2) the SKILL.md body has drifted from the code: it claims "6 条硬性不变量" and "2 档警告" while issue_invariants.py implements 8 invariants and 3 warnings, and the "边界" section still says "这俩" (these two) despite three scripts; (3) the body is 1817 chars, over the team's stated ≤1500-char budget, and is dense with coupling: hardcoded ~/.claude/skills/tc-ops/ invocation paths, repo-relative references (standards/labels.md, skills/tc-render/transition.py, scripts/_autopilot-common.sh, .github/workflows/lint.yml), a hard multica CLI runtime dependency in issue_invariants.py, a PyYAML import in autopilot_lint.py, and a fragile multica-registry/symlink sync ritual that must be run after any file change. Portability standalone is partial: monthly_health.py and autopilot_lint.py run anywhere (given PyYAML), but issue_invariants.py is dead without the multica CLI, and all documented repair/reference paths break outside the team-context repo.

**Frontmatter 问题**
- Non-standard extra fields `owner: 曾振华` and `last_reviewed_at: 2026-06-10` — not part of the official Agent Skills frontmatter spec (only name/description required; license/allowed-tools/metadata optional). They are however required by the team's own lint (monthly_health.py warns on 'missing owner' / 'missing last_reviewed_at'), so they can't simply be deleted; spec-compliant fix is nesting them under a `metadata:` map, which would require updating the monthly_health.py lint regexes in lockstep.
- name 'tc-ops' is compliant: lowercase-hyphen, 6 chars, matches directory name tc-ops.
- description is 320 chars — within the 1024-char limit; quoted correctly as a YAML string despite containing colons.

**Description 问题**
- CRITICAL coverage gap: the description never mentions issue_invariants.py — the issue label↔status invariant audit ('issue label↔status 不变量巡检'). The body calls it '月度 review 必跑' yet an agent reading only the description ('月度健康报告 + autopilot YAML 校验') has zero trigger surface for requests like 'issue 巡检', 'label 漂移', 'check issue invariants', or 'backfill 验收'.
- Implementation noise: '取代本地 MCP 的 monthly_health_report / autopilot_lint —— agent 直接调脚本,无需 MCP 服务器' is migration history/architecture detail that belongs in the body, not the discovery surface (~90 of 320 chars spent on it).
- Trigger keywords ('月度健康','monthly health','autopilot lint','校验 autopilot','health report') are placed at the END of the description rather than front-loaded, and the set is incomplete (no invariant/巡检 triggers).
- Unresolvable-at-discovery reference: 'SOP PB-04 guardrails' assumes the reader knows the team's SOP numbering; harmless as a trigger keyword but opaque as an explanation of WHAT the lint enforces.
- Report-metric enumeration '(团队健康月报:CLAUDE.md token / 本月规则改动 / skill lint / wip 重启次数)' is borderline body material, though it does double as trigger vocabulary.
- Mixed-voice phrasing ('Use when 做月度 review(...)或 新增/修改... 前校验') is functional but awkward; WHAT and WHEN are present, which is good.

**Body 问题**
- Over team budget: body is 1817 chars vs the skills/README.md rule '目标 ≤ 1500 字（约 2000 tokens）。CI lint 强制执行硬上限。' (1817 > 1500). Note the enforcing lint in monthly_health.py estimates tokens via whitespace split (`len(text.split()) * 13 // 10`), which massively undercounts CJK text (this body scores ~267 'tokens'), so the CI hard cap silently fails to enforce the char budget for Chinese-heavy skills.
- Body↔code drift in the issue_invariants.py section: SKILL.md says '输出 6 条硬性不变量违规' and '2 档警告', but issue_invariants.py implements 8 hard invariants ('8 条硬性不变量', including #7 设计-待审⇒in_review and #8 设计-待审⊕设计-已审互斥, plus the 设计-待审 carve-out on #4) and 3 warning tiers (staleness / 盲区 / 研究未关). SKILL.md omits invariants 7-8 and the 研究未关 warning entirely.
- Stale count in '## 边界': '这俩是**低频**工具' ('these two') — there are now three scripts; also arguably issue_invariants.py ('月度 review 必跑' + CI --strict mode) is no longer purely low-frequency.
- Invariant semantics are inlined in the body AND duplicated in the script docstring — progressive disclosure says keep the body to 'run X when Y' and point to the script docstring (or standards/labels.md) as the single reference; deduplicating would also solve the budget overrun.
- Invocation examples hardcode the deploy path `~/.claude/skills/tc-ops/monthly_health.py` instead of a skill-dir-relative instruction ('run monthly_health.py bundled in this skill directory'), which breaks when the agent is working from the repo checkout or a multica workspace copy.
- Positive: instructions are imperative, each script section states when to run + exact command + exit-code contract, and the '边界' section correctly scopes the skill out of the RPI loop.

**耦合/可移植性**
- SKILL.md: `python3 ~/.claude/skills/tc-ops/monthly_health.py <team-context-repo> [<project-repo> ...]` — hardcodes the synced install path; wrong when running from the repo working tree or a non-default CLAUDE_CONFIG_DIR.
- SKILL.md: `python3 ~/.claude/skills/tc-ops/issue_invariants.py [--strict]` — same hardcoded path.
- SKILL.md: `python3 ~/.claude/skills/tc-ops/autopilot_lint.py <yaml-path> [<yaml-path> ...]` — same hardcoded path.
- SKILL.md: '内联复刻 `multica skill lint`' — references the multica CLI subcommand (informational, not a runtime dep).
- SKILL.md: '语义单源 = standards/labels.md 不变量表' — repo-relative path; unresolvable once the dir is copied standalone to ~/.claude/skills/tc-ops/.
- SKILL.md: '修复用 `skills/tc-render/transition.py`,绝不手敲 label/status 命令' — cross-skill repo-relative reference to the tc-render skill; breaks standalone (would need to be ~/.claude/skills/tc-render/transition.py post-sync, and breaks entirely if tc-render isn't synced).
- SKILL.md: '`multica skill files upsert tc-ops --path <file> --content "$(cat <file>)"`' — mandatory post-edit sync ritual requiring the multica CLI.
- SKILL.md: 'monthly-health autopilot 每次跑 `multica skill pull tc-ops` 会经 `~/.claude/skills/tc-ops` 软链把 registry 旧版写回 repo 工作树' — assumes ~/.claude/skills/tc-ops is a SYMLINK into the repo working tree (contradicting the copy/sync model) and depends on multica registry state.
- SKILL.md + description: 'SOP PB-04' — reference to a team SOP document (presumably under sop/ in the repo) not bundled with the skill.
- issue_invariants.py:57-59: `subprocess.run(["multica", "issue", "list", "--output", "json", "--limit", str(PAGE), "--offset", str(offset)], ...)` — HARD runtime dependency on the multica CLI being on PATH and authenticated; script exits 1 without it, so this file is non-functional standalone.
- issue_invariants.py docstring: '状态机语义单源 = standards/labels.md(不变量表)+ skills/tc-render/transition.py' — repo-relative + cross-skill references.
- issue_invariants.py docstring: '运行渠道:已编入 monthly-health autopilot(report-only,随月度健康卡推飞书)' — couples to the monthly-health autopilot and Feishu delivery infra (informational).
- issue_invariants.py:134 output text: '硬性违规(漂移,需 transition.py 修复)' — directs repair to the cross-skill tc-render/transition.py.
- autopilot_lint.py:15: `import yaml` — requires PyYAML installed in the ambient python3 (not stdlib); undeclared dependency, crashes with ModuleNotFoundError on a clean machine.
- autopilot_lint.py docstring: '三处 lint 同步: .github/workflows/lint.yml / 这里 / scripts/_autopilot-common.sh ac_lint_yaml' — logic duplicated across two repo-relative files that cannot be seen from the standalone skill dir.
- autopilot_lint.py docstring: '身份 agent assistant-bot-<scope> 由 _autopilot-common.sh 派生' — repo script reference.
- autopilot_lint.py docstring: '改本文件必须同步 multica registry(multica skill files upsert tc-ops),否则 monthly-health autopilot 的 `multica skill pull tc-ops` 会经 ~/.claude/skills 软链把旧版写回 repo' — multica CLI + symlink write-back hazard duplicated from SKILL.md.
- autopilot_lint.py:35-37: checks sibling `_agent-instructions.md` next to the TARGET yaml — relative to lint input, not the skill dir; portable, but encodes the autopilots/ directory convention of the team repo.
- monthly_health.py:21: shells out to `git` (`["git", "-C", repo, "log", ...]`) — assumes git on PATH; repo path is a CLI arg, so acceptable.
- monthly_health.py:37: `os.path.join(repo, "claude_md_team_global.md")` and :59 `os.path.join(repo, "skills")` — encodes the team-context repo layout (filename claude_md_team_global.md, skills/ subdir); degrades gracefully with '(not found)' messages.
- monthly_health.py:74-77: lint enforces the team's non-standard frontmatter fields (`owner:`, `last_reviewed_at:`) across all skills — coupling between this script and every SKILL.md in the repo.

</details>

<details><summary><b>tc-monday</b>（评分 6.5）</summary>

tc-monday is a compact, single-file skill (/Users/mac/zzh/team-context/skills/tc-monday/SKILL.md, body 1216 chars — within the team's 1500-char budget) that encodes a 30-minute Monday kickoff meeting protocol. Its structure is sound and the body is appropriately terse and imperative, but the description opens with a confusing, imperative first sentence ("Use Monday 09:30 for...") that reads like scheduling advice rather than stating what the skill does, buries the bilingual trigger phrases in the second sentence, and leaks protocol/implementation detail ("read autopilot-generated plan roundup → DRI aligns priorities/boundaries → end") and design rationale ("Designed to NOT repeat...") that belong in the body. Frontmatter carries two non-standard fields (owner, last_reviewed_at). Portability is the weakest area: the body references the repo-relative path autopilots/monday-kickoff.yaml, an unresolvable "SOP P-6 Daily" citation, a cross-skill hop to tc-1-start, and assumes Feishu autopilot infrastructure and a '计划-已批准' issue label exist — all of which dangle when the dir is synced standalone to ~/.claude/skills/tc-monday/.

**Frontmatter 问题**
- Non-standard field `owner: 曾振华` — not part of the official Agent Skills frontmatter (name/description). Ownership tracking belongs in a repo-level manifest, CODEOWNERS, or an optional `metadata` map, not as a top-level frontmatter key.
- Non-standard field `last_reviewed_at: 2026-06-09` — same problem; review freshness is repo-governance data, not skill-loading data. Harmless to Claude Code (extra keys are ignored) but pollutes the standard format and invites lint drift.
- `name: tc-monday` is compliant: lowercase-hyphen, ≤64 chars, matches the directory name tc-monday/.
- Description is 287 chars — well under the 1024 limit — but is written in the imperative ('Use Monday 09:30...') rather than third person as the standard requires.

**Description 问题**
- Opening sentence 'Use Monday 09:30 for the weekly 30-min kickoff meeting.' is ambiguous and misleading at discovery time — it reads as advice about when to hold a meeting, not what the skill does. An agent scanning name+description could conclude this is a scheduling note rather than a meeting-facilitation protocol.
- Not third person: 'Use Monday 09:30...' is imperative. Should be e.g. 'Guides the DRI through...' or 'Facilitates...'.
- Trigger phrases ('周一 kickoff', 'Monday kickoff', '本周计划对齐', 'Monday meeting') are present and bilingual — good — but not front-loaded; they sit in the second sentence behind the confusing opener.
- Implementation detail pollution: 'Guides DRI through 30-min protocol: read autopilot-generated plan roundup → DRI aligns priorities/boundaries → end.' The arrow-flow of protocol steps is body material; only the one-line WHAT belongs here.
- Design rationale pollution: 'Designed to NOT repeat what plans already say.' — this is a philosophy note for the body, not a discovery cue.
- Not fully self-contained: 'autopilot-generated plan roundup' presumes the reader knows the team's autopilot infrastructure; 'DRI' is jargon (acceptable, but combined with 'autopilot' the description leans on context the agent cannot resolve at discovery time).

**Body 问题**
- Body is 1216 chars — compliant with the team's ≤1500-char budget stated in /Users/mac/zzh/team-context/skills/README.md.
- The body is written as a human meeting runbook, not agent instructions: it never tells the agent what to DO (e.g., verify the autopilot roundup posted, generate the walkthrough order, time-box the phases, remind the DRI of the anti-patterns). Section 'Setup (autopilot does this)' is purely informational.
- Grammar/clarity: 'By 09:30, `autopilots/monday-kickoff.yaml` posted to feishu:' is missing a verb ('has posted' / 'is posted') and conflates a config file with the message it produces.
- Unresolvable citation with no path: '❌ Daily standup format (dead — see SOP P-6 Daily)' — no bundled file or path lets an agent follow this.
- No progressive disclosure files exist, but none are needed at this length — the single-file layout is appropriate.
- Minor: emoji bullets (❌) are stylistic noise; plain 'Do NOT' bullets read the same to a model and lint-cleaner.

**耦合/可移植性**
- Repo-relative path (line 11): 'By 09:30, `autopilots/monday-kickoff.yaml` posted to feishu:' — resolves to /Users/mac/zzh/team-context/autopilots/monday-kickoff.yaml, which does NOT travel when the dir is synced to ~/.claude/skills/tc-monday/. Breaks standalone.
- Cross-repo doc reference (line 32): 'Daily standup format (dead — see SOP P-6 Daily)' — points at the sop/ directory (sop/group_sop_v0.4.md) with no path; unresolvable from the synced skill dir.
- Cross-skill reference (line 35): 'Brainstorm new projects (those go through tc-1-start)' — depends on the sibling skill /Users/mac/zzh/team-context/skills/tc-1-start/ also being synced to ~/.claude/skills/; dangles if synced selectively.
- External-system label assumption (line 12): 'All issues with label `计划-已批准` from this week' — assumes the team's issue tracker (multica workspace, per skills/README.md sync target) defines this label; no multica CLI command is invoked, but the workflow is inert without that system.
- Infrastructure assumption (lines 3, 10-11): 'autopilot-generated plan roundup' / 'posted to feishu' — presumes the Feishu bot + autopilot scheduler from /Users/mac/zzh/team-context/autopilots/ is running; the skill has no fallback if the roundup was never posted.
- No multica CLI commands, no MCP tool references, no env vars, and no cwd assumptions beyond the repo-relative autopilots/ path — the coupling surface is entirely the five items above.

</details>

<details><summary><b>tc-friday</b>（评分 7）</summary>

A well-scoped, genuinely useful ritual skill (Friday 30-min demo + 15-min betting table) with bilingual trigger phrases and a mostly-imperative, time-boxed body — but it has real standard-compliance and portability problems. The description opens in the imperative ("Use Friday afternoon...") instead of third person and is polluted with implementation/governance noise (the `betting_table_capture` remote-MCP note "非本地,本期保留" is maintenance metadata an agent cannot act on at discovery time). The frontmatter carries two non-standard fields (owner, last_reviewed_at). The body is 1598 chars, over the team's stated ≤1500 目标 in skills/README.md, partly due to a changelog-style digression explaining why an old multica query was wrong. Most critically for a dir that syncs standalone to ~/.claude/skills/, it hard-couples to the multica CLI and its workspace label/status schema, to the sibling tc-render skill's transition.py (exact path + flags), and to a remote MCP tool with no fallback instructions.

**Frontmatter 问题**
- name: 'tc-friday' is compliant — lowercase-hyphen, ≤64 chars, matches directory name /Users/mac/zzh/team-context/skills/tc-friday/.
- Non-standard field `owner: 曾振华` — not part of the official Agent Skills frontmatter schema (name/description, plus license/allowed-tools/metadata). Team-governance data; belongs in a team registry, CODEOWNERS, or a `metadata:` sub-map if tooling supports it, not as a top-level frontmatter key.
- Non-standard field `last_reviewed_at: 2026-06-10` — same problem; review bookkeeping does not belong in skill frontmatter loaded into agent context. Also unquoted, so YAML parses it as a date object rather than a string, which some validators reject.
- description is 312 chars (within the 1024 limit) but written in the imperative mood ('Use Friday afternoon for...') rather than third person as the standard requires.
- description embeds Markdown bold inside YAML — `(**remote** MCP · 非本地,本期保留)` — which renders as literal asterisks in the discovery surface.

**Description 问题**
- Not third person: opens 'Use Friday afternoon for the 30-min demo + 15-min betting table double-session' — imperative, and the first sentence describes the meeting's schedule rather than WHAT the skill does (guide/facilitate the session).
- Trigger phrases are present and bilingual ('周五 demo', 'Friday demo', 'betting table', '周五演示', '下周做什么') — good — but they sit in the second sentence behind scheduling prose instead of being front-loaded.
- Implementation detail pollution: 'Pairs with `betting_table_capture`(**remote** MCP · 非本地,本期保留)' — an MCP tool name plus an internal governance note ('kept for this period') that belongs in the body or a team doc, not the discovery surface.
- Not self-contained: `betting_table_capture` and the note 非本地/本期保留 reference infrastructure and team decisions the agent cannot resolve at discovery time.
- Stylistic noise: parenthetical shorthand '(real artifacts not slides)', all-caps 'NO backlog', and the interpunct '·' make it read like internal notes rather than a description; the WHAT/WHEN content itself ('Guides DRI through demo + betting, decide next week's work') is otherwise adequate.

**Body 问题**
- Body is 1598 unicode characters — exceeds the team budget stated in /Users/mac/zzh/team-context/skills/README.md ('目标 ≤ 1500 字（约 2000 tokens）。CI lint 强制执行硬上限。'). Over the stated 目标; whether it trips the CI hard cap is unverifiable since the cap value is not stated.
- Changelog-style rationale inline in Pre-flight: '（label 即真值,不附加 status 条件——按状态机语义,待审 case 的 status 是 `in_review`,审完才 `done`,旧查询 `--status done --label 复盘-待审` 是永空集）' — explaining why an OLD query was wrong is history, not instruction; it burns ~100 chars of the budget and belongs in a commit message or bundled reference file (progressive disclosure).
- The 'Setup' section names `betting_table_capture` (remote MCP) but the 5 numbered steps describe human meeting mechanics (proposing, silent thinking, voting) — it never says what the agent actually calls or records with the tool, and gives no fallback if the remote MCP is unavailable despite flagging it as 非本地.
- No bundled supporting files at all — acceptable for this size, but the multica state-machine explanation and the tc-render finalize procedure are exactly the kind of reference material the standard says to push into separate files.
- Instructions are otherwise appropriately imperative, time-boxed, and include good anti-patterns; heading '45-min protocol' is consistent with the description's 30+15 split.

**耦合/可移植性**
- multica CLI required: `multica issue list --label 复盘-待审` (Pre-flight) — breaks anywhere multica is not installed/configured.
- multica workspace schema coupling: label `复盘-待审`, status values `in_review` / `done`, and the referenced legacy query `--status done --label 复盘-待审`; also issue-type semantics 'case', 'phase case', 'plan' with parent-child closing behavior.
- Cross-skill file reference: `python3 ~/.claude/skills/tc-render/transition.py case-finalize <case-issue>` with flag `--keep-parent` — depends on the sibling tc-render skill being synced to ~/.claude/skills/ AND on tc-render's internal file layout (transition.py exists in the repo at /Users/mac/zzh/team-context/skills/tc-render/transition.py today, but the reference silently breaks if tc-render is renamed, restructured, or not synced).
- Remote MCP tool dependency: `betting_table_capture`(**remote** MCP · 非本地,本期保留) — referenced in both frontmatter description and body 'Setup: Use `betting_table_capture`(remote MCP)'; requires a connected remote MCP server, no local fallback given.
- No repo-relative paths (no standards/ or sop/ references) and no cwd assumptions found — the only path used is home-anchored (~/.claude/skills/...), which survives the copy only if the sibling skill ships too.

</details>

<details><summary><b>tc-roles</b>（评分 7）</summary>

A focused, genuinely useful skill (role taxonomy + assignment rules + a concrete output template) with good bilingual trigger coverage, but it has four audit-relevant defects: (1) two non-standard frontmatter fields (owner, last_reviewed_at); (2) a description that is not third-person and embeds a version-pinned internal reference ("SOP v0.4 P-5") that an agent cannot resolve at discovery time and that will go stale; (3) a body of ~1950 characters, exceeding the team's stated ≤1500-char budget in skills/README.md; (4) three references that break when the directory is synced standalone to ~/.claude/skills/tc-roles/ — the SOP citations ("SOP P-5", "SOP ❌10", resolving to /Users/mac/zzh/team-context/sop/group_sop_v0.4.md, not bundled) and the repo-relative path "decisions/". The skill dir contains only SKILL.md, so there are no bundled-file issues, and it uses no CLI tools or MCP dependencies — coupling is documentary rather than executable, making the fixes cheap.

**Frontmatter 问题**
- Non-standard fields present: `owner: 曾振华` and `last_reviewed_at: 2026-06-09`. Neither is part of the official Agent Skills frontmatter spec (name + description, plus a small allowed set). Strict validators/linters may reject or silently drop them. This governance metadata belongs in a team registry, the skills/README.md, or a `metadata:` sub-map if the toolchain tolerates one — not as top-level frontmatter keys.
- `name: tc-roles` is compliant: lowercase-hyphen, 8 chars (≤64), exactly matches the directory name tc-roles/.
- `description` is 250 chars (≤1024 limit, compliant on length) but violates the third-person convention — it opens with the imperative "Use when starting a project and assigning roles" instead of describing what the skill does.
- No `allowed-tools` or similar fields — fine, none needed for this skill.

**Description 问题**
- Not third person: opens with imperative "Use when starting a project and assigning roles" rather than stating what the skill does (e.g., "Assigns project roles...").
- Unresolvable internal reference at discovery time: "Walks through SOP v0.4 P-5" — at session start the agent sees only name+description and has no way to resolve "SOP v0.4" or "P-5"; it is provenance/implementation detail that belongs in the body. The version pin "v0.4" is also a staleness hazard: when the SOP bumps to v0.5 this description silently lies.
- WHAT is back-loaded: the trigger list and SOP citation come before the actual capability statement ("4 role types ... 6 assignment rules ... Generates the 'How to split' section"). Best practice front-loads WHAT+trigger keywords together.
- "Generates the 'How to split' section of the plan doc" presupposes the team's plan-doc convention (produced by the sibling tc-3-plan skill); an agent without that context cannot fully resolve "the plan doc" — minor, since it still communicates output shape.
- The bare trigger '认领' is very broad (means "claim" generically) and risks false-positive triggering on unrelated claim/pickup contexts.
- Missing some natural trigger phrases: 分工, 责任人, "who does what", "assign roles", "who is the DRI" (English form). Bilingual coverage is otherwise good — this is the description's main strength.

**Body 问题**
- Over the team body budget: body is ~1950 characters including whitespace (~1619 excluding), versus skills/README.md's stated "目标 ≤ 1500 字（约 2000 tokens）。CI lint 强制执行硬上限。" — roughly 30% over target and plausibly over the CI hard cap.
- No progressive disclosure despite being over budget: the "Special situation: 实习生 DRI" and "Anti-patterns" sections are secondary reference material that could move to a bundled supporting .md (the dir currently contains only SKILL.md), which would bring the body under 1500 chars.
- Largely declarative reference (role-type definitions) rather than imperative procedure: there is no step-by-step workflow (e.g., 1. ask 自愿认领 → 2. confirm exactly one DRI or refuse → 3. write the How to split section into the plan doc). Imperatives exist only sporadically ("Refuse to start", "Ask 'who wants what?'").
- Opaque shorthand citations "SOP P-5" (line: "实习生 can be DRI (SOP P-5)") and "SOP ❌10" (line: "❌ No DRI (most common AI Native failure — SOP ❌10)") are never expanded or linked; after the dir is copied standalone the reader cannot consult the SOP at all.
- The output template is good and concrete (the ```markdown How to split``` block) — this is the body's best feature and should stay inline.

**耦合/可移植性**
- Frontmatter description: "Walks through SOP v0.4 P-5" — references the team SOP living at /Users/mac/zzh/team-context/sop/group_sop_v0.4.md, which is NOT bundled in the skill dir; unresolvable after sync to ~/.claude/skills/tc-roles/.
- Body: "实习生 can be DRI (SOP P-5)." — same unbundled SOP reference.
- Body: "❌ No DRI (most common AI Native failure — SOP ❌10)" — same unbundled SOP reference (item ❌10 of the SOP's anti-pattern list).
- Body: "Decisions recorded in decisions/ even if seniors disagree." — repo-relative path `decisions/` (exists at /Users/mac/zzh/team-context/decisions/) assumes cwd is the team-context repo root; breaks when the skill runs from ~/.claude/skills/tc-roles/ or any other cwd. Should be an absolute/anchored description (e.g., "the team-context repo's decisions/ directory").
- Body + description: "the plan doc's 'How to split' section" / "Generates the 'How to split' section of the plan doc" — implicit coupling to the team's plan-doc convention (established by the sibling skill tc-3-plan); no file path, so it degrades gracefully, but it is undefined for a standalone reader.
- No multica CLI commands, no MCP tool references, no explicit cross-skill file references (e.g., no tc-render/publish.py-style paths), no env vars. Context only: skills/README.md states dirs are synced via `scripts/sync-to-local.sh` (to ~/.claude/skills/) and `scripts/sync-to-multica.sh` (to multica workspace), which is why the above references break.

</details>

<details><summary><b>tc-conflict</b>（评分 7.5）</summary>

A well-scoped, genuinely useful skill with one of the better descriptions in the standard's terms — clear WHEN clause plus front-loaded bilingual trigger keywords — but it has three concrete defects: (1) the frontmatter carries two non-standard fields (owner, last_reviewed_at) that don't belong in the spec's frontmatter; (2) the body is 1859 chars, ~24% over the team's own ≤1500 budget stated in skills/README.md (the ~600-char output template should be extracted to a bundled template.md); and (3) it is coupled to the team-context repo in two ways that silently break once the directory is synced standalone to ~/.claude/skills/tc-conflict/: the write target `decisions/YYYY-MM-DD-<topic>.md` is a repo-root-relative path that resolves against whatever cwd the agent happens to have, and the description/body cite "SOP v0.4 P-5" / "SOP P-5", a document living in the repo's sop/ directory that is not bundled and not resolvable at discovery time (and the pinned "v0.4" will go stale). The description also leaks that file path and SOP version into the discovery surface where they add noise without aiding triggering.

**Frontmatter 问题**
- Non-standard field `owner: 曾振华` — not part of the Agent Skills frontmatter spec (only name/description plus a small allowed set); belongs in a team registry, the skills/README.md, or a `metadata:` block if the team's tooling supports one, not as a top-level frontmatter key.
- Non-standard field `last_reviewed_at: 2026-06-09` — same problem; review metadata is CI/registry concern, not skill frontmatter. Some strict parsers ignore or reject unknown keys.
- `name: tc-conflict` is compliant: lowercase-hyphen, 11 chars, matches the directory name exactly.
- `description` is 240 chars — well under the 1024 limit; length is fine (issues with its content are listed separately).
- Description opens imperative/second-person ("Use when team members disagree...") then shifts to third person ("Walks through... Writes resolution...") — inconsistent voice; the standard prefers consistent third person.

**Description 问题**
- Contains an unresolvable internal reference at discovery time: "Walks through SOP v0.4 P-5 conflict 4 principles" — an agent seeing only name+description cannot resolve 'SOP v0.4 P-5', and the pinned version 'v0.4' will rot as the SOP evolves. Says nothing useful for triggering; move to body.
- Leaks implementation detail into the discovery surface: "Writes resolution to decisions/YYYY-MM-DD-<topic>.md regardless of outcome." The exact output path/filename convention is body material; worse, `decisions/` is a repo-relative path that is meaningless outside the team-context repo.
- Trigger keywords are good and bilingual ('冲突', '分歧', 'conflict', 'disagree', '意见不合', '谁说了算') but sit in the second sentence; they are close enough to the front to work, though English coverage is thin (missing e.g. 'deadlock', 'who decides', 'tie-break').
- WHEN is stated clearly ("team members disagree on a project decision") but WHAT the skill actually does is only conveyed via the opaque SOP reference — a reader who doesn't know the SOP learns 'walks through 4 principles' without knowing what kind of principles (adjudication? escalation? voting?). Should say plainly: evidence-over-preference, DRI decides, decision gets documented.
- Mixed voice: starts "Use when..." (imperative) rather than consistent third person.

**Body 问题**
- Body length 1859 characters (measured, excluding frontmatter) — exceeds the team's stated budget in skills/README.md: "目标 ≤ 1500 字（约 2000 tokens）。CI lint 强制执行硬上限。" Over target by ~24%.
- No progressive disclosure: the skill dir contains only SKILL.md. The ~600-char '## Output template' markdown block (lines 40-69) is exactly the kind of reference material the standard says to move to a bundled file (e.g. decision-template.md referenced from the body); extracting it would bring the body under the 1500 budget.
- Instruction "Write `decisions/YYYY-MM-DD-<topic>.md`" (line 30) never says where `decisions/` is — it implicitly assumes the agent's cwd is the team-context repo root. The body should state the anchor explicitly (e.g. 'in the team-context repo root' or an env-var/config lookup) or the file lands in an arbitrary cwd.
- Line 74 anti-pattern cites "(SOP P-5 forbids)" — a reference to a document (sop/ in the parent repo) that is not bundled with the skill and cannot be followed after sync.
- Tone/imperativeness is otherwise good: short imperative rules, concrete anti-patterns, a review-trigger field in the template. Section '## When to invoke' (lines 10-11) duplicates the description's WHEN — minor redundancy but acceptable as a precision refinement ('not casual taste — real consequence').

**耦合/可移植性**
- Description, line 3: "Writes resolution to decisions/YYYY-MM-DD-<topic>.md regardless of outcome." — repo-relative path; `decisions/` exists at /Users/mac/zzh/team-context/decisions/ but not relative to ~/.claude/skills/tc-conflict/ or an arbitrary cwd.
- Body, line 30: "Write `decisions/YYYY-MM-DD-<topic>.md`:" — same repo-relative path with an implicit cwd assumption (agent must be running inside the team-context repo).
- Body, line 38: "Without file, decision didn't happen." — makes the unresolvable decisions/ path load-bearing: the skill's non-negotiable output depends on the broken path.
- Description, line 3: "Walks through SOP v0.4 P-5 conflict 4 principles." — references the un-bundled SOP document (lives under /Users/mac/zzh/team-context/sop/), version-pinned to v0.4.
- Body, line 74: "❌ 'I told you so' later when dissent turns out right (SOP P-5 forbids)" — second reference to the external, un-bundled SOP.
- No multica CLI commands, no MCP tool references, no cross-skill references (e.g. no tc-render/publish.py usage), no env vars — coupling is limited to the two items above (decisions/ path and SOP P-5 citations).

</details>

<details><summary><b>tc-design-review</b>（评分 6）</summary>

A dense, well-thought-out process-gate skill whose core problem is that it treats the description field as a second body: the 408-char description is stuffed with transition commands, label names, and status values that only make sense after reading three other skills and the team SOP, while the genuinely good trigger phrases ('设计评审', 'design review', '方案过一下') are buried mid-string. Frontmatter carries two non-standard fields (owner, last_reviewed_at). The body (1,952 chars incl. whitespace, 1,698 excl.) exceeds the team's stated ≤1500 字 budget either way. Portability is the critical failure: the skill is inoperable standalone — both of its executable steps shell out to a hard-coded sibling-skill path (~/.claude/skills/tc-render/transition.py), and it leans on unbundled invariant docs (不变量 #4/#8), team SOP, tc-3-plan/tc-4-build transitions, and the issue tracker's label/status taxonomy, none of which travel with the directory.

**Frontmatter 问题**
- Non-standard field `owner: 曾振华` — not part of the Agent Skills standard frontmatter (name/description plus optionally license/allowed-tools/metadata); strict validators may reject unknown top-level keys. Belongs in a `metadata:` map, a CODEOWNERS-style file, or the team README, not top-level frontmatter.
- Non-standard field `last_reviewed_at: 2026-06-10` — same problem; review bookkeeping is repo metadata, not skill-discovery data. Move under `metadata:` or track it outside SKILL.md.
- `name: tc-design-review` is compliant (lowercase-hyphen, 16 chars, matches directory name) — no issue.
- description is 408 chars, within the 1024 limit — no length violation, but see description issues for content problems.
- description is not written in third person: it opens with the imperative "Use between plan approval and build start" rather than stating what the skill does.

**Description 问题**
- Trigger keywords are not front-loaded: the string opens with "Use between plan approval and build start — 设计评审门(SOP 三道评审门之②,①计划批准 ③代码评审)" and only then lists "Triggers: '设计评审', 'design review', plan 刚被 plan-approve 且为项目层, '方案过一下'". The strongest match terms should lead.
- Heavy implementation pollution — the entire second half is body material, not discovery material: "transition.py design-request-review(+设计-待审 · in_review)→ 设计评审子 agent 出 verdict → 编排 session 当场 design-approve(+设计-已审 · todo)" (CLI script names, label names, status values) and "MVP 设计载体 = plan approach 段或 issue 评论,不新增 doc 类型。" None of this helps an agent decide WHETHER to invoke.
- Not self-contained at discovery time: "SOP 三道评审门之②" references team SOP docs the agent has not loaded; "堵不变量"-style label semantics and "plan 刚被 plan-approve" assume knowledge of tc-3-plan's transition vocabulary; "编排 session"/"转换边"/"同构" are internal jargon unresolvable from the description alone.
- Written as instructions to the reader ("Use between…", "把…收口成…"), not third-person ("Runs the design review gate…").
- Positives worth preserving in a rewrite: it DOES state WHEN precisely (between plan approval and build start; 项目层必走、任务层可跳), gives bilingual triggers, and disambiguates against the other two review gates (①计划批准 ③代码评审), reducing confusion with tc-3-plan and tc-5-review.

**Body 问题**
- Over the team budget: body is 1,952 chars including whitespace (1,698 excluding), vs. skills/README.md's "目标 ≤ 1500 字（约 2000 tokens）。CI lint 强制执行硬上限。" — over by ~13–30% depending on how 字 is counted, so it plausibly trips the CI hard cap.
- No progressive disclosure, and worse — key reference material is neither inline nor bundled: "堵不变量 #8" and "不变量 #4 的 carve-out 由巡检承认" cite invariants defined somewhere else in the repo (standards/ or sop/) with no bundled excerpt, so a triggered agent cannot resolve them. Either bundle an invariants reference file or drop the numeric citations.
- Budget could be recovered via bundled files: the "机制盲区" blockquote, the "补审场景" edge case, and the Anti-patterns section are reference/edge material that could move to a supporting .md (README.md format explicitly allows "*.md optional supporting reference docs").
- Instructions are appropriately imperative and well-sequenced (三步 flow, verdict-return = transition-execution point) — this part is good.
- Dense bilingual jargon ("转换边", "原子换签", "两连勿断", "无主窗口") raises comprehension cost for an agent; each is used once without definition.
- The subagent output contract (VERDICT format, BLOCKING/NON-BLOCKING, 事实核查清单) is embedded prose; a reusable prompt template file would be more robust and shrink the body.

**耦合/可移植性**
- Cross-skill hard-coded script path (step 1): `python3 ~/.claude/skills/tc-render/transition.py design-request-review <work-issue>` — depends on the tc-render skill being synced to ~/.claude/skills; breaks if tc-design-review is copied standalone or run from the repo checkout before sync.
- Cross-skill hard-coded script path (step 3): `python3 ~/.claude/skills/tc-render/transition.py design-approve <work-issue>` — same dependency, second occurrence.
- Cross-skill script reference: "若将来需要独立设计稿(publish.py `--type design`)" — refers to tc-render/publish.py without path context.
- Cross-skill workflow dependency on tc-4-build: "tc-4-build pre-flight 会查 `设计-已审`" and "→ 接 tc-4-build `build-start`"; also `build-start` is invoked as a known transition throughout ("verdict 后必须 `design-approve` → `build-start` 两连").
- Cross-skill workflow dependency on tc-3-plan transitions: "时点:`plan-approve`(计划-已批准 · todo)之后" and "批准后实质改方案 → 先 `plan-upgrade` 重走计划评审".
- Frontmatter description cross-references: "tc-3-plan 批准后/tc-4-build 开工前的交叉引用指到这里" and "transition.py design-request-review … design-approve".
- Unbundled invariant documentation: "摘在场 `设计-已审`(复审作废旧批准,堵不变量 #8)" and "与 `计划-已批准` 共存(不变量 #4 的 carve-out 由巡检承认)" — invariant numbering lives outside the skill dir (team-context standards/sop), unresolvable after standalone copy.
- Team SOP reference in description: "设计评审门(SOP 三道评审门之②,①计划批准 ③代码评审)" — assumes team-context/sop docs.
- External patrol/monitoring process ("巡检", likely tc-health-check/tc-ops): "任务层:可跳——plan-approve 后直接 build-start 合法,巡检不报" and "巡检能抓的是:评审中开工(build-start 对 `设计-待审` 在场告警)、评审挂起(staleness >48h)".
- Issue-tracker taxonomy assumptions (multica workspace labels/statuses): labels `设计-待审`, `设计-已审`, `计划-已批准` and statuses `in_review`, `todo`, `in_progress`; plus schema assumption "issue 数据无 layer 字段,巡检无法区分项目/任务层". No direct `multica` CLI command appears in this file, but transition.py presumably wraps it.
- Published-artifact assumption: subagent inputs are "设计载体(plan HTML / 评论 URL)" — assumes the tc-render publish pipeline has produced a plan HTML page.
- Runtime assumption: `python3` on PATH and `~` expansion (no env vars otherwise; no MCP tools referenced).

</details>

<details><summary><b>tc-health-check</b>（评分 7）</summary>

A well-conceived self-monitoring skill with genuinely good bones: strong bilingual trigger phrases, a concrete 4-signal rubric inlined in the body (not just cited), a fixed output template, and sensible anti-patterns. Main defects: the description is written in second person ('Use when... you suspect'), buries the WHAT at the end in ungrammatical form ('recommends invoke tc-handoff'), and leaks unresolvable jargon ('SOP v0.4 dumb zone') into the discovery surface; the frontmatter carries two non-standard fields (owner, last_reviewed_at); the body is 1832 chars, exceeding the team's stated 1500-char budget (~22% over, will trip the CI lint hard cap); and the skill has a soft but real dependency on the sibling tc-handoff skill (referenced 4 times including in the output verdict vocabulary) plus a dead citation to sop/group_sop_v0.4.md section P-2 that resolves to nothing once the dir is copied standalone to ~/.claude/skills/. No file paths, CLI commands, MCP tools, env vars, or cwd assumptions — portability coupling is limited to cross-skill and SOP-jargon references.

**Frontmatter 问题**
- name 'tc-health-check' is valid: lowercase-hyphen, 15 chars, matches directory name — OK
- Non-standard field 'owner: 曾振华' — not part of the Agent Skills standard frontmatter; ownership belongs in the team README, git blame, or a standard 'metadata:' map, not as a bare top-level key
- Non-standard field 'last_reviewed_at: 2026-06-09' — same problem; review cadence is repo-process metadata, not skill frontmatter; move to a metadata map or track outside SKILL.md
- description is within the 1024-char limit (352 chars) — OK on length, but see description issues for content problems

**Description 问题**
- Not third person: opens 'Use when conversation shows signs...' and addresses the agent as 'you' ('or you suspect the session has entered...') — standard requires third-person WHAT+WHEN
- WHAT the skill does is buried at the very end and vague: 'Outputs explicit pollution signals detected and recommends invoke tc-handoff or continue' — an agent scanning descriptions sees WHEN before it sees WHAT
- Ungrammatical: 'recommends invoke tc-handoff or continue'
- Unresolvable jargon at discovery time: "SOP v0.4 'dumb zone'" — at session start only name+description are loaded; an agent has no way to resolve 'SOP v0.4' or 'dumb zone' (sop/group_sop_v0.4.md is not bundled and not even referenced by path)
- Cross-skill reference 'tc-handoff' in the description — resolvable only if that sibling skill happens to be installed; implementation/workflow detail that belongs in the body
- Positive: bilingual trigger phrases are present and reasonably front-loaded — '走偏了', '感觉不对', 'going in circles', '怎么回事', plus behavioral triggers ('repeated rejected solutions', 'model agreeing too readily') — this is the strongest part of the description and should be preserved

**Body 问题**
- Body is 1832 chars — exceeds the team budget in skills/README.md ('目标 ≤ 1500 字（约 2000 tokens）。CI lint 强制执行硬上限。') by ~22% if the 1500 figure is read as a character cap; trim candidates: the Mandate prose and the Anti-patterns section can be compressed
- Heading '## The 4 signals (SOP v0.4 P-2)' cites an external SOP section that does not exist inside the skill dir — dead citation after standalone sync; either drop the citation or bundle a reference file (note: the signal content itself IS inlined, which is good practice)
- Aggregation-rule wording vs output-template vocabulary is inconsistent: aggregation says 'tell user, recommend tc-handoff, let user decide' while the verdict enum is 'continue | mention | tc-handoff-now' — the mapping from 'recommend, let user decide' to 'mention' must be inferred
- H1 title 'Context Pollution Detector' does not match the skill name 'tc-health-check' — minor, but the mismatch makes cross-referencing ('health check' vs 'pollution detector') harder
- Instructions are appropriately imperative and the fixed output block is good; no progressive-disclosure violation at this size (no bundled files needed) — noted as compliant

**耦合/可移植性**
- Frontmatter description: "you suspect the session has entered SOP v0.4 'dumb zone'" — references the repo doc sop/group_sop_v0.4.md, which is NOT bundled in the skill dir and unresolvable after sync to ~/.claude/skills/tc-health-check/
- Frontmatter description: 'recommends invoke tc-handoff or continue' — cross-skill reference to sibling skill skills/tc-handoff/, only resolvable if that skill is synced alongside
- Body line 15: '## The 4 signals (SOP v0.4 P-2)' — citation of SOP v0.4 section P-2; dead reference standalone (content is inlined, so functional impact is low)
- Body line 46: 'Any signal POLLUTED → invoke tc-handoff skill' — hard behavioral dependency on the tc-handoff skill being installed
- Body line 47: 'Two signals "noted" → tell user, recommend tc-handoff, let user decide' — cross-skill reference
- Body line 59 (output template): 'Verdict: continue | mention | tc-handoff-now' — verdict vocabulary embeds the tc-handoff skill name
- No repo-relative file paths, no multica CLI commands, no MCP tool references, no env vars, no cwd assumptions found — coupling is limited to the tc-handoff sibling skill and the SOP v0.4 citation

</details>

<details><summary><b>tc-self-check</b>（评分 7）</summary>

One of the most portable skills in this repo: the entire payload (the 10 anti-patterns, 3 red lines, and an explicit OK/FLAG/? output contract) is inlined, so it survives a standalone copy to ~/.claude/skills/ with no multica CLI, MCP, env-var, or cross-skill file dependencies. Its problems are hygiene-level rather than structural: the body (~2041 chars) exceeds the team's stated ≤1500 字 CI hard cap; the frontmatter carries non-standard 'owner'/'last_reviewed_at' fields (self-consistent with the team's own anti-pattern ❌5, but off-spec — should nest under 'metadata:'); the description is second-person imperative rather than third person and leans on jargon ('SOP v0.4', 'AI MIQ', 'red lines') unresolvable at discovery time; the '(SOP v0.4 P-7)' label has drifted from the SOP's actual section naming ('07 / # 10 条反 pattern'); and one instruction ('monthly burnout check 3 questions') references a checklist that is defined nowhere in the bundled skill. The hand-copied anti-pattern list also carries silent-drift risk when the SOP moves past v0.4.

**Frontmatter 问题**
- Non-standard extra fields 'owner: 曾振华' and 'last_reviewed_at: 2026-06-09' are not part of the official Agent Skills frontmatter (name, description, license, allowed-tools, metadata). Notably the skill's own anti-pattern ❌5 mandates them ('Fix: add owner + last_reviewed_at fields'), so they are deliberate team convention — but to stay spec-compliant they should be nested under a 'metadata:' map rather than sitting as top-level keys a strict validator may reject.
- 'name: tc-self-check' is compliant: lowercase-hyphen, 13 chars, matches the directory name.
- 'description' is 367 chars (within the 1024 limit) but is written in second person ('Use mid-work ... to check yourself') instead of third person, violating the standard's phrasing convention.
- 'last_reviewed_at: 2026-06-09' has no defined review cadence in the skill or README; the field asserts freshness without a mechanism (minor — a lint/CI check would make it meaningful).

**Description 问题**
- Second-person/imperative voice: 'Use mid-work or at any moment of doubt to check yourself' — the standard requires third person describing what the skill does.
- Trigger phrases are present but mid-loaded, not front-loaded: the quoted triggers ('am I doing this right', '反 pattern', 'self check') only appear after the opening clause 'Use mid-work or at any moment of doubt...'.
- Unresolvable jargon at discovery time: 'SOP v0.4 10 anti-patterns' and 'the 3 red lines specific to AI MIQ team' assume knowledge the agent does not have when only name+description are loaded (no path, no gloss of what the anti-patterns cover, e.g. agent sprawl, burnout, missing DRI).
- Thin bilingual coverage: the only Chinese-adjacent trigger is the mixed-script '反 pattern' (which does match the SOP's own vocabulary); pure-Chinese phrases a teammate would actually type — '自检', '反模式' — are absent.
- Output-format detail leaking into the discovery surface: 'Returns explicit OK/FLAG/? per anti-pattern + status on the 3 red lines' is borderline — it usefully signals the contract but could be compressed; it is the least harmful of the issues.
- Good elements worth preserving: behavioral triggers 'user reports feeling something is off', 'monthly review', and 'any time the model feels uncertain about the meta-approach' are concrete and agent-matchable.

**Body 问题**
- Over the team body budget: body is ~2041 characters versus skills/README.md's '目标 ≤ 1500 字（约 2000 tokens）。CI lint 强制执行硬上限。' — roughly 36% over if the lint counts characters (it is within the ~2000-token intent for English text, but the stated hard cap is 1500 字).
- Stale/mismatched SOP label: the title '# Anti-Pattern Self-Check (SOP v0.4 P-7)' cites 'P-7', but the string 'P-7' appears nowhere in /Users/mac/zzh/team-context/sop/group_sop_v0.4.md — the SOP's section is '# 10 条反 pattern' (referenced as '07' at line 161). The label has already drifted.
- Unresolvable instruction: '❌9 ... Fix: monthly burnout check 3 questions' — the 3 questions are defined nowhere in the skill directory and no pointer is given; an agent (or human) running this skill standalone cannot execute the fix.
- Silent-drift risk: the 10 anti-patterns are hand-copied from sop/group_sop_v0.4.md (section starting line 771). Inlining is the right portability call, but there is no sync note beyond the version tag in the title; when SOP moves to v0.5 the copies will diverge invisibly.
- Bare unlocated reference: '(SOP — these need DRI intervention without waiting for monthly review)' cites 'SOP' with no version or location.
- Org-specific names embedded in the reusable body: 'Aaron's underlying-algorithm work especially', '2 fullstack devs on routine tasks', 'interns especially' — appropriate for a team skill but these go stale with staffing changes and would be better isolated in a clearly-marked team-specific section (which the '3 red lines' section partially is).
- Positives: instructions are imperative ('Read this list', 'report one of', 'End with...'), the output contract (OK / FLAG: <why> / ?) is explicit and machine-checkable, and no progressive-disclosure violation exists — the inline list IS the payload and is short enough that bundled reference files are unnecessary.

**耦合/可移植性**
- description: 'check yourself against SOP v0.4 10 anti-patterns' — conceptual dependency on /Users/mac/zzh/team-context/sop/group_sop_v0.4.md; no path given and content is inlined, so it does not break at runtime, but it is unresolvable jargon when the dir is copied standalone.
- Body title: '# Anti-Pattern Self-Check (SOP v0.4 P-7)' — same SOP dependency; 'P-7' does not match the SOP's actual section labeling ('07' / '# 10 条反 pattern').
- '(SOP — these need DRI intervention without waiting for monthly review)' — bare reference to the SOP document, not bundled.
- 'Hint: high seat usage but .claude/skills/ empty' — cwd-relative path assumption; refers to the current project's .claude/skills/ directory (works as a heuristic anywhere, but is the only literal path in the skill).
- '❌4 CLAUDE.md as junk drawer (> 3k tokens)' — references the generic CLAUDE.md convention; portable across any Claude Code setup.
- 'Fix: add owner + last_reviewed_at fields' — depends on the team's non-standard frontmatter convention (documented only implicitly, via this skill and other skills in team-context/skills/).
- 'Fix: monthly burnout check 3 questions' — references a checklist that lives (presumably) in the SOP and is not bundled; unresolvable standalone.
- Org/person coupling: '3 red lines for AI MIQ specifically', "Aaron's underlying-algorithm work especially", '2 fullstack devs on routine tasks', 'interns especially', owner '曾振华'.
- Notably ABSENT (clean): no multica CLI commands, no MCP tool references, no cross-skill file references (e.g. no tc-render/publish.py style paths), no repo-relative paths like standards/... or sop/..., no env vars. This skill survives the sync to ~/.claude/skills/ intact.

</details>

## 2. 分发管线 / tc-multica / remote MCP 探查

<details><summary><b>team-context 分发管线</b></summary>

### team-context skill distribution pipeline — complete map

Repo: `/Users/mac/zzh/team-context`. 14 skill directories under `skills/` (tc-1-start … tc-self-check, tc-ops, tc-render, tc-design-review), each a `SKILL.md` + optional bundled files (tc-render additionally has `publish.py`, `transition.py`, `PUBLISH.md`, `publish-contract-v1.yaml`, `assets/`, `tests/`).

#### 1 · How a skill travels from repo → member machine

There are **four live paths plus one designed-but-greenfield path**:

##### Path A — `scripts/sync-team-config.sh` (unified entry, canonical; README.md:23 tells every member to run it on first clone)

- **Step 1 (Claude Code, lines 90–98): SYMLINK, whole directory.** `ln -sfn "$d" "$HOME/.claude/skills/$(basename "$d")"` (line 95) links each `skills/tc-*` **directory** (not just SKILL.md — bundled scripts included) into `~/.claude/skills/`. Claude Desktop's local-agent-mode skills-plugin reuses the same directory (line 98 comment).
- **Step 2 (global rules, lines 100–104): SYMLINK.** `~/.claude/CLAUDE.md → claude_md_team_global.md` (line 103) and `~/.codex/AGENTS.md → claude_md_team_global.md` (line 104). Edit source → all UIs instantly current.
- **Step ⑥ (Codex discovery, lines 62–86, 107–109): GENERATED FILE.** `_gen_codex_index` writes `~/.codex/skills-index.md` (atomic tmp+mv, line 85) because "Codex 无原生 skill 机制" (line 105 comment; docs/SYNC.md:34,39). The index lists each tc-* name + description and the **absolute path** to its SKILL.md on that machine (`正文: $d/SKILL.md`, line 83), plus the shared publish entry `python3 $SKILLS_DIR/tc-render/publish.py …` (lines 73–74) so Claude and Codex converge on the same Bash publish choke-point ("命门B").
- **Step 3 (multica registry push, lines 111–169): CLI PUSH.** Create-or-update each skill in the multica registry (details in §4 below). Registry is explicitly a "派生只读投影" (derived read-only projection, line 112 comment; check-registry-sync.sh:6) — truth lives in the repo, dev machines use the git symlink.
- **What it does NOT do:** MCP config (per-user token) is deliberately excluded (line 9; docs/SYNC.md:43–64 — configured manually per UI).
- Flags: `--no-multica`, `--dry-run` (lines 11–13, 20–27).

##### Path B — `scripts/sync-to-local.sh` (older subset script)

Symlinks every `skills/*/` dir into `~/.claude/skills/` (lines 19–35). If the target exists as a symlink it is replaced (lines 24–25); if it exists as a **real file/dir it is skipped with a WARN** ("handle manually", line 27) — a physical copy shadows the repo source. Claude Code only; no Codex, no registry, no global md.

##### Path C — `scripts/sync-to-multica.sh` (DRI, legacy import route)

Runs `multica skill import --url "${REPO_URL}"` (line 29) after auth/daemon preflight, then chains `team-autopilot.sh all codex` (line 33). **This route is historically broken for this repo**: `multica skill import` expects exactly one SKILL.md at the URL root and the repo is private → raw.githubusercontent 404 (standards/multica-sync-results.md:11–14); the actual 12-skill import was done per-skill with `multica skill create` (multica-sync-results.md:16). README.md:38 still lists it as the DRI step; the modern replacement is sync-team-config.sh step 3.

##### Path D — member pull from registry: `multica skill pull --all`

docs/SYNC.md:16–22 defines the member-facing flow: skills (including bundled scripts like tc-render/publish.py) are pulled from the registry into `~/.claude/skills/`, **overwriting old versions — a physical COPY, not a symlink**. All four UIs (Claude Code / Claude Desktop / Codex CLI / Codex app) read the same `~/.claude/skills/` (SYNC.md:34). New-member flow (SYNC.md:69): `multica login` → DRI adds to workspace → `multica skill pull --all` → configure tcmcp-remote → `sync-team-config.sh` for global-rule symlinks.

##### Path E — designed future: signed bundle + daemon auto-write (greenfield)

`.github/workflows/skill-bundle-release.yml`: pushing a `skills-v*` tag (lines 11–14) → provenance merge-gate (lines 36–53) → deterministic `git archive` of **git-blob bytes** of `skills/` + `claude_md_team_global.md` (lines 62–64, EOL pinned by `.gitattributes:4–5` `-text`) → keyless OIDC attestation (`actions/attest-build-provenance`, lines 68–71) → GitHub release asset (lines 73–84). The daemon side (offline sigstore verification, byte-for-byte write to `~/.claude/skills`) is **not implemented** — mini-ADR v4 §7 (line 95) declares the whole pipeline "全栈净新" (greenfield).

#### 2 · Failure modes

1. **Member forgets `git pull` + re-sync.** Symlinked machines go stale until `git pull` (content) — and a **new** skill dir needs re-running the sync script to get its symlink. Registry-pull machines stay frozen at pull time until someone re-runs `multica skill pull --all` (SYNC.md:28,67 — the update flow is entirely manual: edit → push → "各机 pull 取最新"). Nothing verifies member machines; CI only reconciles repo→registry.
2. **Symlink vs copy staleness / shadowing.** Two mechanisms write the same `~/.claude/skills/`: git symlinks (dev machines) and registry-pull physical copies. decisions/2026-06-08-drop-local-mcp.md:14 names this the "三份真相" problem — "软链脏态(物理 SKILL.md 遮蔽)". sync-to-local.sh:27 skips-with-WARN when a physical dir shadows; mini-ADR v2 §3.1 (line 83) flags pre-placed symlinks as an attack/freeze vector, and v4 invariant #6 (line 19) mandates that dev-symlink vs daemon-write machines be **mutually exclusive by verifiable config** (`MULTICA_DAEMON_SKILL_WRITE`), not convention.
3. **Registry pull is lossy / truncated.** decisions/2026-06-09-rpi…:86 records the measured defect: `multica skill pull` rebuilds frontmatter and **drops `owner` / `last_reviewed_at`** ("自伤 lint" — the pulled copy then fails the team's own skill lint). Registry description is truncated to 480 chars (sync-team-config.sh:127) — tc-render's very long CJK description (skills/tc-render/SKILL.md:3) is cut in registry vs source. Bundled `tests/`, `__pycache__`, `*.pyc` are excluded from files[] (lines 49–51), so CI assets never reach pull-based machines (intended, but means repo and pulled dirs differ). `files upsert` failures are swallowed per-file (line 164 prints ✗ and continues). Also `_skill_desc` only matches a **single-line** `description:`; a YAML folded/multi-line description would silently yield an empty registry description.
4. **Repo-relative / machine-relative references break after sync.** `~/.codex/skills-index.md` embeds **absolute repo paths of the machine that generated it** (sync-team-config.sh:73,83) — moving the clone breaks the index until regenerated. claude_md_team_global.md:66 tells Codex/other agents to read team-context `skills/tc-render/` directly (assumes a clone exists), and line 65 references `~/.claude/skills/multica-cli/`, a skill not in this repo. tc-render's own usage (SKILL.md:23) uses `~/.claude/skills/tc-render/publish.py`, which works under both symlink and copy.
5. **Codex vs Claude Code format gap.** Codex has no skill mechanism (SYNC.md:34,39): it gets the same file as `AGENTS.md` (behavioral rules) + the generated skills-index; skills are read as "流程描述" prose, not auto-triggered. Claude Desktop has no CLAUDE.md mechanism at all — global rules must be **manually pasted** into custom instructions (SYNC.md:36,40). tc-* triggering therefore only actually works natively in Claude Code/Desktop.
6. **Import-path incompatibilities** (Path C): private repo 404 + one-SKILL.md-per-URL expectation (multica-sync-results.md:11–14).

#### 3 · claude_md_team_global.md — distribution & skill-discovery role

- **Distribution:** symlinked to `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md` by sync-team-config.sh:103–104 (also SYNC.md:25); Claude Desktop = manual paste (SYNC.md:36); it is also inside the signed bundle for future daemon distribution to `~/.claude`/`~/.codex` (skill-bundle-release.yml:63; mini-ADR v4 §2.3 line 64).
- **Role:** it is the L1 layer auto-loaded into **every** session (README.md:143–145, hard cap 3k tokens enforced by CI lint.yml:48–57; monthly ≤2800-word check README.md:170). Its **skill table** "怎么叫起其他 Claude session" (lines 34–46) maps 12 scenarios (启动新项目→tc-1-start … /clear 之前→tc-handoff) to skill names — this is the discovery/dispatch mechanism that makes the synced skills get invoked. The "去哪儿找具体 context" table points at `~/.claude/skills/` "(从 team-context repo 同步)" (line 57) and directs Codex to read `skills/tc-render/` in the repo (line 66). The 6 core rules (lines 13–18) hard-wire tc-2-research/tc-3-plan/tc-4-build/tc-handoff/tc-5-review into the workflow.

#### 4 · What the multica registry push contains (sync-team-config.sh step 3, lines 111–169)

- **name**: frontmatter `name:` via awk, fallback = dir basename (lines 125–126).
- **description**: `_skill_desc` (lines 53–61) — Python reads SKILL.md line-by-line, regex `^description:\s*(.*)$`, takes the **whole rest of the line** (internal colons safe), strips surrounding quotes, then **character-slices to a max** (`v[:mx]`) — called with **480** (line 127, comment: "按字符截 480(CJK 安全)"). Character (not byte) slicing avoids splitting CJK codepoints; long descriptions are silently truncated mid-sentence in the registry.
- **content**: SKILL.md **body only** — awk strips YAML frontmatter, printing everything after the second `---` (line 129).
- **owner**: frontmatter `owner:` (a display name, e.g. `曾振华`) resolved to a user UUID via `multica user list --output json` (lines 39–45, 130–141); if user-list unavailable or name not found → owner left empty with a warning (lines 119–121, 140).
- **create-or-update**: id looked up by name in `multica skill list --output json` (lines 32–37, 131); update via `multica skill update "$id" --description --content [$owner_flag]` (line 152), else `multica skill create` and parse returned id (lines 155–157).
- **files[]**: `_each_skill_file` (lines 49–51) = every file in the skill dir **except SKILL.md** (body goes via --content), **`tests/`** (CI assets, not runtime), **`__pycache__`/`*.pyc`**; pushed skill-relative via `multica skill files upsert "$id" --path "$rel" --content "$(cat "$d/$rel")"` (idempotent upsert, lines 161–165). So tc-render's publish.py/transition.py/PUBLISH.md/assets travel to the registry; its tests do not.
- **CI reconciliation**: `scripts/check-registry-sync.sh` fails (exit 1) if any repo tc-* skill name is missing from the registry (lines 29–37) — but it checks **name presence only, not content parity**, and honestly SKIPs (exit 0) when multica CLI/token is absent (lines 14–22), which is the case on the GitHub runner (lint.yml:154–158).

#### 5 · Versioning / staleness signals

- **No automatic update mechanism exists today.** Symlinked machines refresh via `git pull`; pull-based machines require a manual `multica skill pull --all` (SYNC.md:28,67). No skill version numbers — only `last_reviewed_at` frontmatter.
- Staleness detection is **review-staleness, not distribution-staleness**: `multica skill lint --dir ~/.claude/skills` flags frontmatter gaps + 90-day-stale reviews (ONBOARDING-DRI.md:299; README.md:169), and `skills/tc-ops/monthly_health.py` (line 76 checks missing `last_reviewed_at`) runs via the monthly-health autopilot (autopilots/README.md:44). A member whose local copy lags the repo gets **no signal** unless CI's repo→registry check fires (and that only covers missing names).
- The **intended** versioning mechanism is the `skills-v*` release tags (skill-bundle-release.yml:11–14) + monotonic `manifest_version` with anti-rollback (daemon rejects lower-than-installed versions) and validity windows (expiry only demotes "latest", never bricks) per mini-ADR v4 §3.1 (line 71) / v2 §2.4 (lines 59–60) — daemon side unimplemented.

#### 6 · Decision records — intended future architecture

##### 2026-06-09 rpi-publish-architecture-redeliberation (decided)
A 5-agent review + 3 independent architects (evolve / Go-single-core / server-side) **converged**: do a "no-split lightweight convergence" now, defer the "where does the core live" decision. **Phase 1 (plan-of-record, lines 54–66)**: single publish choke-point (publish.py internally exec `multica issue comment add --inline`); fields JSON Schema (`additionalProperties:false`); delete tc-handoff's markdown bypass; **fix distribution** — `buildSkillMd` restore owner, sync becomes create-or-**update** + push files[] + CI repo→registry reconciliation, **registry demoted to derived read-only projection, dev machines use git symlinks** (line 61 — this is exactly what sync-team-config.sh + check-registry-sync.sh now implement); `multica doctor` preflight; Codex symmetry (same Bash entry + generated skills-index). **Phase 2 (deferred, lines 66–69)**: Go CLI single-core vs server-side sink, triggered only by high-frequency contract churn / team ≥15 / authz-audit needs.

##### 2026-06-10 seamless-distribution-security mini-ADRs v1→v4 (v4 = APPROVED design)
Goal: **true zero-touch updates** — the CLI auto-updates itself (binary, ⑨) and the daemon silently verifies-and-writes skills + md (⑩) into `~/.claude/skills` / `~/.claude` / `~/.codex`, human-not-in-loop, built as a "secure software distribution subsystem" (v3 line 5). Evolution: v1 (CI-signed content manifests, daemon verifies before write) was broken by review (5 blockers: unprotected tag-triggered signing; empty install.sh trust anchor; server-reassembled bytes unsignable); v2 pivoted to minisign + sign-source-bytes + no-unsigned-fallback; v3 made 7 binding decisions (v3 lines 14–22); **v4 final direction** (10 implInvariants, lines 14–23):
- **Trust anchor**: binaries = `feibo-ai/tc-multica`; **skills = `feibo-ai/team-context`** via this repo's skill-bundle-release.yml (its header comment, lines 3–8). Daemon rejects any attestation whose OIDC subject triple (repo AND workflow AND `refs/tags/skills-v*`) doesn't match — including upstream forks' same-named artifacts.
- **Signing**: keyless OIDC `actions/attest-build-provenance` (no long-lived keys); daemon verifies **offline** via sigstore-go + embedded TUF root; expired root = fail-closed.
- **Sign git tracked-blob raw bytes; daemon writes byte-for-byte** (identity write — no server `buildSkillMd` reassembly; mutable metadata `owner_user_id`/`last_reviewed_at` stay in the registry DB, outside the signature) so "评审对象 == 落盘字节" (what reviewers approved is exactly what lands on disk). `.gitattributes` `-text` pins already landed for this (lines 1–5).
- **Fail-closed everywhere**: no unsigned/SHA-only fallback branch exists in code; monotonic versions (anti-rollback), configurable expiry (anti-freeze, never bricks), signed revocation lists with monotonic counters.
- **Write-path safety**: EvalSymlinks on every parent dir, `O_NOFOLLOW|O_EXCL` create / lstat+temp+rename update; a pre-existing symlink target = **deterministic refusal + local alert** (never silently skip, never follow); **dev-machine git-symlink workflow and consumer-machine daemon write-loop are mutually exclusive** via `MULTICA_DAEMON_SKILL_WRITE` (self-host default off) — the daemon refuses to start its write loop if sync-managed symlinks exist.
- **Provenance merge gate**: originally "signing only on ≥2-human-review merged main"; **DRI later explicitly relaxed it** (v4 line 6) to "release tag must be the merge_commit_sha of a PR merged into main, self-review allowed" — B1 single-member-poisoning risk explicitly accepted for a 5-person team. The shipped workflow implements exactly the relaxed gate (skill-bundle-release.yml:52–53).
- Honest residual risks: install.sh first hop = pure TOFU; local same-user compromise defeats everything; CI compromise inherent. **Everything daemon-side is greenfield** (v4 §7).

**Summary of decided direction**: today's pipeline (git clone + symlink + manual registry push/pull, registry as derived projection) is the interim Phase-1 state; the decided end-state is signed `skills-v*` bundles of git-blob bytes released from this repo, cryptographically verified offline by the multica daemon and silently written byte-for-byte onto consumer machines, with dev machines keeping the symlink workflow and the two modes made mutually exclusive by config.

**关键事实**
- sync-team-config.sh symlinks each whole skills/tc-* DIRECTORY (bundled scripts included) into ~/.claude/skills via `ln -sfn "$d" "$HOME/.claude/skills/$(basename "$d")"` — scripts/sync-team-config.sh:95; Claude Desktop reuses the same dir (line 98 comment)
- sync-team-config.sh symlinks claude_md_team_global.md to BOTH ~/.claude/CLAUDE.md and ~/.codex/AGENTS.md — scripts/sync-team-config.sh:103-104
- Codex has no native skill mechanism; sync-team-config.sh generates ~/.codex/skills-index.md listing each tc-* name+description+absolute SKILL.md path and the shared publish.py entry — scripts/sync-team-config.sh:62-86,108; docs/SYNC.md:34,39
- The generated Codex skills-index embeds machine-specific absolute repo paths ($SKILLS_DIR/...) — scripts/sync-team-config.sh:73,83 — breaking if the clone moves until regenerated
- Registry push is create-or-update: id looked up by name in `multica skill list --output json`, then `multica skill update --description --content` or `multica skill create` — scripts/sync-team-config.sh:131,151-157
- Registry description is extracted by _skill_desc: python regex ^description:\s*(.*)$ on a SINGLE line, quotes stripped, character-sliced v[:mx] — scripts/sync-team-config.sh:53-61 — and called with a 480-char cap at line 127 ('按字符截 480(CJK 安全)')
- Registry content is the SKILL.md BODY only — awk strips YAML frontmatter (everything after the second ---) — scripts/sync-team-config.sh:129
- Bundled files pushed to registry via `multica skill files upsert --path --content` EXCLUDE SKILL.md, tests/, __pycache__, *.pyc — scripts/sync-team-config.sh:49-51,161-165; per-file failures are swallowed (✗ + continue, line 164)
- Skill owner frontmatter (display name e.g. 曾振华) is resolved to a user UUID via `multica user list`; unknown/unavailable → owner left empty with warning — scripts/sync-team-config.sh:39-45,130-141
- MCP config (per-user token) is deliberately NOT in sync-team-config.sh; configured manually per UI per docs/SYNC.md — scripts/sync-team-config.sh:9; docs/SYNC.md:43-64
- sync-to-local.sh symlinks every skills/*/ dir into ~/.claude/skills (Claude Code only); replaces existing symlinks but SKIPS with WARN if a real file/dir shadows the link — scripts/sync-to-local.sh:19-32 (WARN at line 27)
- sync-to-multica.sh runs `multica skill import --url <github-url>` then chains team-autopilot.sh — scripts/sync-to-multica.sh:29,33 — but this import route failed for this repo: import expects exactly one SKILL.md at URL root and the private repo 404s on raw.githubusercontent — standards/multica-sync-results.md:11-14
- Member pull path is `multica skill pull --all` → PHYSICAL COPY (incl. bundled scripts) into ~/.claude/skills, overwriting old versions; all 4 agent UIs read that dir — docs/SYNC.md:16-22,34
- Updates are fully manual: edit repo skills/tc-*/ → `multica skill push`/sync-team-config.sh → each machine re-runs `multica skill pull --all` — docs/SYNC.md:28,67; no mechanism notifies members their local copies are stale
- `multica skill pull` was measured to be LOSSY: it rebuilds frontmatter dropping owner/last_reviewed_at, self-breaking skill lint — decisions/2026-06-09-rpi-publish-architecture-redeliberation.md:86 (fix ordered at line 61: registry demoted to derived read-only projection, dev machines use git symlinks)
- The 'three truths' staleness problem (repo vs physical ~/.claude/skills vs registry; physical SKILL.md shadowing symlinks) is documented — decisions/2026-06-08-drop-local-mcp.md:14; drop-local-mcp also set distribution = repo single source + registry via skill update/files upsert + `multica skill pull --all` (lines 24-25)
- check-registry-sync.sh CI-fails (exit 1) if any repo tc-* skill NAME is missing from the registry, but checks name presence only (grep -qx) — scripts/check-registry-sync.sh:29-37 — and honestly SKIPs exit 0 without multica CLI/token (lines 14-22), which is the case on the GitHub runner (lint.yml:154-158)
- claude_md_team_global.md is the auto-loaded L1 layer (hard 3k-token CI cap, .github/workflows/lint.yml:48-57) containing the skill-dispatch table '怎么叫起其他 Claude session' mapping 12 scenarios to tc-* skills — claude_md_team_global.md:34-46 — plus pointers to ~/.claude/skills '(从 team-context repo 同步)' (line 57) and repo skills/tc-render/ for Codex (line 66)
- Staleness signals are review-based not distribution-based: `multica skill lint` flags 90-day-stale last_reviewed_at (docs/ONBOARDING-DRI.md:299; README.md:169) and skills/tc-ops/monthly_health.py checks missing last_reviewed_at (line 76) via the monthly-health autopilot (autopilots/README.md:44)
- CI lint enforces SKILL.md name+description frontmatter and ~2000-token skill body cap — .github/workflows/lint.yml:15-46
- Future path: .github/workflows/skill-bundle-release.yml, triggered by skills-v* tags (lines 11-14), builds a deterministic git-blob-byte bundle of skills/ + claude_md_team_global.md via `git archive` + gzip -n (lines 62-64), signs with keyless OIDC actions/attest-build-provenance (lines 68-71), publishes as a GitHub release asset (lines 73-84); .gitattributes:4-5 pins skills/** and claude_md_team_global.md -text for byte-identity
- The skill-bundle provenance gate was RELAXED by DRI decision: tag commit must be the merge_commit_sha of a PR merged into main, but independent review is no longer required (self-review allowed) — skill-bundle-release.yml:52-53; decisions/2026-06-10-seamless-distribution-security-mini-adr-v4.md:6 (B1 single-member-poisoning risk explicitly accepted)
- mini-ADR v4 (APPROVED) end-state: daemon silently verifies keyless OIDC attestations OFFLINE (sigstore-go + embedded TUF root, asserting repo/workflow/ref triple), then writes git tracked-blob bytes byte-for-byte into ~/.claude/skills and md into ~/.claude/~/.codex; fail-closed with no unsigned fallback; monotonic anti-rollback + expiry-only-demotes-latest; signed revocation — decisions/...mini-adr-v4.md:14-23 (10 implInvariants)
- mini-ADR v4 invariant #5/#6: daemon write loop uses EvalSymlinks parent-chain + O_NOFOLLOW/O_EXCL; symlink target = deterministic refusal + local alert (never skip/follow); dev-machine git-symlink workflow vs consumer daemon write-loop are mutually exclusive via MULTICA_DAEMON_SKILL_WRITE config, daemon refuses to start if sync-managed symlinks exist — mini-adr-v4.md:18-19
- mini-ADR v4 keeps server mutable metadata (owner_user_id/last_reviewed_at) OUT of the signed bundle (stays in registry DB); reviewed git diff == bytes landed on disk — mini-adr-v4.md:52-55; the whole daemon distribution side is declared greenfield (§7 line 95: '全栈净新')
- 2026-06-09 RPI redeliberation decision: 3 independent architects converged on Phase 1 'no-split lightweight convergence' (single publish choke-point, JSON schema, delete bypass, fix lossy distribution, doctor preflight, Codex symmetry) with Phase 2 core-sink (Go CLI single-core vs server-side) deferred until high-frequency contract churn / team ≥15 / authz needs — decisions/2026-06-09-rpi-publish-architecture-redeliberation.md:54-69
- Onboarding: members clone the repo and run `bash scripts/sync-team-config.sh` as the single entry (README.md:18-24); DRI runs sync-to-multica.sh (README.md:38); new members get tokens via their own `multica login`, never DM'd by DRI — docs/SYNC.md:41,69; docs/ONBOARDING-DRI.md:61-78

</details>

<details><summary><b>tc-multica 能力面</b></summary>

### tc-multica: Skills & CLI Integration Report

#### 1. Skill Registry — YES, full-featured

Multica has a **workspace-scoped skill registry** stored in Postgres, exposed via REST API, with a complete CLI surface under `multica skill`.

##### Storage model
- `server/migrations/008_structured_skills.up.sql` creates three tables:
  - `skill` — `id`, `workspace_id`, `name` (UNIQUE per workspace), `description`, `content` (the SKILL.md body), `config JSONB`, `created_by`, timestamps.
  - `skill_file` — `skill_id`, `path` (UNIQUE per skill), `content` — the **files[] bundle** (scripts, assets).
  - `agent_skill` — many-to-many agent↔skill binding.
- `server/migrations/110_skill_owner_and_review.up.sql` adds `owner_user_id` (accountable human, distinct from `created_by`) and `last_reviewed_at` (backs the 90-day stale check, "SOP ❌5").
- API response shape (`server/internal/handler/skill.go:41-52`): `id, name, description, content, config, owner_user_id, last_reviewed_at`; skill detail includes `files []SkillFileResponse` (skill.go:105).

##### REST API (`server/cmd/server/router.go:943-956`)
`GET/POST /api/skills`, `GET /api/skills/search`, `POST /api/skills/import`, per-skill `GET/PUT/DELETE`, `POST /{id}/touch-reviewed`, `GET /{id}/files`, `PUT /{id}/files` (upsert), `DELETE /{id}/files/{fileId}`.

##### CLI surface (`server/cmd/multica/cmd_skill.go`)
- `multica skill list [--stale] [--output table|json]` (flags at cmd_skill.go:145-146)
- `multica skill get <id> [--output json|table]` — includes files (149)
- `multica skill create --name (required) --description --content|--content-stdin|--content-file --config <json> --owner <user-uuid> --output` (161-168)
- `multica skill update <id>` — same flags; `--owner ""` clears owner (171-178)
- `multica skill delete <id> [--yes]` (181)
- `multica skill import --url <clawhub.ai|skills.sh|github.com URL> --on-conflict fail|overwrite|rename|skip --output` (184-186; endpoint `POST /api/skills/import`)
- `multica skill touch-reviewed <id>` — resets 90-day stale clock (66-71, 189)
- `multica skill search <query> [--output]` — searches installable skills via `GET /api/skills/search?q=` (92-97, 874)
- **`multica skill pull [<name-or-id>] [--all] [--dir] [--output]`** (73-81, 152-154)
- `multica skill lint [--dir] [--output]` — local frontmatter + 2000-token budget check (83-90, 157-158)
- `multica skill files list <skill-id>`, `multica skill files upsert <skill-id> --path --content|--content-stdin|--content-file`, `multica skill files delete <skill-id> <file-id>` (101-125, 195-202)
- Agent binding: `multica agent skills list|set|add` with `--skill-ids` (cmd_agent.go:82-127, 217, 221; API `GET/PUT /api/agents/{id}/skills`, `POST .../skills/add`, router.go:922-924).

##### PULL paths — agents/member machines get skills from the registry in THREE ways
1. **`multica skill pull`** (cmd_skill.go:363-464): downloads one skill or `--all` from the workspace registry and reconstructs `<dir>/<name>/SKILL.md` (rebuilding YAML frontmatter with name/description/owner/last_reviewed_at, cmd_skill.go:335-361) **plus every bundled file at its stored path** (files[] loop at 435-455, with path-traversal safety). Default dir is `~/.claude/skills` (373-378). CLI_AND_DAEMON.md:572-576 calls this "the **self-update channel for skills**, mirroring `multica update` for the CLI binary."
2. **Per-task injection by the daemon**: when an agent claims a task, the daemon writes the agent's bound skills into the task workdir at provider-native locations — Claude Code → `.claude/skills/{name}/SKILL.md`, Codex → `CODEX_HOME/skills/`, OpenCode/Pi/Cursor/Copilot equivalents, fallback `.agent_context/skills/` (docs/product-overview.md:370-377; implementation `server/internal/daemon/execenv/context.go:407-423 writeSkillFiles`, `execenv.go:421-436 hydrateCodexSkills`). Built-in platform skills (`server/internal/service/builtin_skills.go:24`, dirs under `server/internal/service/builtin_skills/` with `multica-` prefixes) are embedded at compile time and layered on every agent.
3. **Daemon `skillSyncLoop`** — see section 4.
- Reverse direction also exists: **local→registry import** via daemon relay (`server/internal/handler/runtime_local_skills.go`; routes `POST /api/.../local-skills`, `.../local-skills/import` at router.go:1051-1054 and daemon result reporting at 555-556) — the web UI can list skills on a member machine and import one into the registry.

#### 2. skills-lock.json (repo root)

`/Users/mac/zzh/tc-multica/skills-lock.json` is a **lockfile for dev-time agent skills installed into this repo itself** — not part of the multica product runtime. It pins 4 skills (`frontend-design` from anthropics/skills, `shadcn` from shadcn/ui, `ui-ux-pro-max` from nextlevelbuilder/ui-ux-pro-max-skill, `web-design-guidelines` from vercel-labs/agent-skills) each with `source`, `sourceType: github`, optional `skillPath`, and a `computedHash` (skills-lock.json:1-26). It matches the lockfile format of the external `skills` installer CLI (e.g. `npx skills add`); the installed artifact lives at `.agents/skills/web-design-guidelines/SKILL.md` (authored by vercel). **No code in the repo reads skills-lock.json** (grep across .go/.ts/.sh/Makefile finds zero consumers). Notably, the built-in skill `multica-skill-importing` (server/internal/service/builtin_skills/multica-skill-importing/SKILL.md) explicitly warns agents: "Do not finish with `npx skills add`. That installs into an external/local skill environment, not the Multica workspace DB" — i.e., the repo distinguishes the external skills-lock ecosystem from its own registry.

#### 3. CLI surface that team-context skills depend on — ALL VERIFIED

- **`project create`** (cmd_project.go:143-153): `--title` (required), `--description`, `--status`, `--icon`, **`--lead`** (147), **`--dri`** (148, user UUID, SOP P-5), **`--priority`** (149, urgent/high/medium/low/none), **`--start-date`** (150, YYYY-MM-DD), **`--due-date`** (151), `--repo` (repeatable), `--output`. Also `project update` mirrors all (189-198), `project assign-dri <project-id> <user-uuid>` (63-64), `project list --full-id` (135), `--status` filter (136), `--without-dri` (137), `project status <id> <status>` (56-57), `project resource add/update/remove/list` (70-97).
- **`issue create`** (cmd_issue.go:288-302): `--title` (required), `--description[-stdin|-file]`, `--status`, `--priority`, **`--assignee`** (294, fuzzy name) / `--assignee-id` (295), **`--parent`** (296), **`--project`** (297), `--start-date`/`--due-date` (298-299), `--allow-duplicate`, `--attachment`. `issue update` mirrors (305-316). `issue list` filters: `--status --priority --assignee[-id] --project --metadata --label --labels-mode --limit --offset --updated-after --full-id` (267-279). `issue assign --to/--to-id/--unassign` (323-325), `issue status <id> <status>` (134-135).
- **`skill list --output json`** — cmd_skill.go:145. ✔
- **`auth status`** — cmd_auth.go:49-50; prints Server/User/Token after validating against `/api/me` (451-480). ✔ Also `auth logout` (55) and `auth issue-token --user-email --name --expires-in-days` (61-62, 80-83, admin-only PAT issuance).
- **`user list`** — cmd_user.go:52-53 ("List workspace users with id / name / email / role"), `--output table|json` (79). Plus `user create --email --name --role` (81-83, admin-only) and `user profile get/update`. ✔
- **`label`** commands (cmd_label.go): `label list [--full-id]` (63-64), `label get`, `label create --name --color` (67-68), `label update`, `label delete`; per-issue: `issue label list/add/remove <issue-id> <label-id>` with `--full-id` (cmd_issue_label.go:17-52).
- **Comment/publish**: `issue comment add <issue-id> --content|--content-stdin|--content-file --parent --attachment` and **`--inline <path-to-HTML>`** which uploads a local HTML doc bound to the issue and embeds it as `!file[name](url)` so it **renders inline** under the comment (cmd_issue.go:354-361). `issue comment list` has thread-aware reads: `--since --thread --tail --recent --roots-only --summary --before/--before-id` (330-337).
- Other agent-relevant commands: `issue metadata list/get/set/delete --key --value --type` (cmd_issue_metadata.go:62-112), `issue runs`, `issue run-messages --since`, `issue rerun`, `issue cancel-task`, `issue search`, `issue subscriber add/remove`, `workspace list --full-id`, `multica doctor`, `multica update`.

#### 4. Daemon auto-sync of skills to member machines — YES (two mechanisms)

**A. `skillSyncLoop`** (`server/internal/daemon/skill_sync.go:62-104`), started unconditionally as a goroutine at daemon start (`server/internal/daemon/daemon.go:674`) but **opt-in gated**:
- Enabled only when `SkillWriteEnabled` is true — env `MULTICA_DAEMON_SKILL_WRITE` (default **OFF** everywhere; config.go:114, 516). Poll interval from `MULTICA_DAEMON_SKILL_SYNC_INTERVAL` (default 6h — same as auto-update; config.go:115, 524).
- Each cycle (`trySkillSync`, skill_sync.go:112-173): fetch → anti-rollback → verify → revocation check → safe write:
  1. `FetchLatestSkillBundle` pulls the newest `skills-v*` prerelease's `skill-bundle.tar.gz` from GitHub repo **`feibo-ai/team-context`** (the "trust anchor" skill source repo; `server/internal/cli/skillsync.go:31-73`).
  2. Anti-rollback via persisted tag in `~/.multica/skill-sync-version` (skill_sync.go:129-137, 185-194).
  3. `VerifySkillBundleAttestation` — offline sigstore keyless verification, SAN regex pinned to `feibo-ai/team-context/.github/workflows/skill-bundle-release.yml@refs/tags/skills-v*` (`server/internal/cli/attestation.go:45-52, 248-256`); fail-closed, no fallback.
  4. `CheckArtifactRevocation` against CI-signed `revocations.json` (repo root; skill_sync.go:153-156, `server/internal/cli/revocation.go`).
  5. `ExtractSkillBundleSafely` writes byte-for-byte into `~/.claude/skills/` with hard path-safety (typeflag whitelist, parent-chain EvalSymlinks, O_EXCL|O_NOFOLLOW, deterministic symlink rejection — skillsync.go:154-169 header comments).
- **Dev/consumer mutual exclusion**: `SkillWriteGuard` (skillsync.go:474-478) refuses to run on developer boxes where `~/.claude/skills` is a git-symlink layout ("the team installs skills as symlinks", cmd_skill.go:533), so the daemon never clobbers a dev setup.
- Note: this loop syncs from **team-context (GitHub)**, not from the multica workspace registry; the workspace-registry pull path is the manual `multica skill pull`.

**B. Per-task injection** (section 1, pull path #2) — every task run rehydrates the agent's registry-bound skills into the task workdir, so agents always execute with the current registry contents even without machine-level sync.

Related: the daemon also has `autoUpdateLoop` for the CLI binary (`MULTICA_DAEMON_AUTO_UPDATE`, daemon.go:673), and RELEASES.md:48 (TEA-113) describes a DRI-triggered "fleet one-click update" nudge that pushes daemons to self-check immediately — explicitly noting "本期纯 CLI 维度, skill 一键更新切后续独立 task" (this release covers CLI only; one-click **skill** fleet update is deferred to a follow-up task).

#### 5. Skill-distribution plans in docs/decisions/cases

- `decisions/` (1 file: 2026-06-03-local-log-privacy.md) and `cases/` contain **no skill-distribution content**.
- The distribution plan lives in **RELEASES.md** (v0.4.15, "⑩ skill/md 无感分发", lines 145-150): trust anchor = team-context repo; daemon `skillSyncLoop` pulls a signed skill bundle → offline attestation verification → write-path-safe extraction; gated behind `MULTICA_DAEMON_SKILL_WRITE` default off; stage-4 revocation via `revocations.json`; referenced design doc is "mini-ADR v4 ⑩c" (cited at skill_sync.go:52 and skillsync.go:3 — the ADR itself is not in this repo, likely in team-context).
- RELEASES.md:48 (TEA-113): fleet one-click **skill** update is planned as a separate future task.
- `docs/product-overview.md` §3.6 (lines 350-405) documents the skill concept, data shape (name/description/content/files), lifecycle (create in Settings→Skills or import from clawhub.ai/skills.sh; mount to agent; daemon injects at claim time; CLI-native discovery), and a note that "AI distilling skills from past tasks" is a possible future, not current, feature.
- `CLAUDE.md` (repo conventions) mandates that built-in skills under `server/internal/service/builtin_skills/*` are "source-traced contracts shipped to agents" — any CLI/API change a built-in skill documents must update that skill's SKILL.md and its `references/*-source-map.md` in the same PR.
- CLI_AND_DAEMON.md:542-640 is the canonical Skills CLI doc; it does **not** document the daemon `MULTICA_DAEMON_SKILL_WRITE` sync (that's only in RELEASES.md + code).

#### Integration takeaways for team skills
- The registry natively stores exactly what a skill needs (SKILL.md body + files[] + owner + review date), and `multica skill pull --all` already reconstructs runnable skills into `~/.claude/skills` — a team-skill sync can be a cron/loop over that command, or the signed-bundle daemon path if the team publishes `skills-v*` releases to team-context.
- All CLI commands a team-context skill would invoke (project/issue/label/user/auth/comment with inline HTML publishing) exist with JSON output modes and `--full-id` escapes for UUID plumbing.
- Governance hooks are built in: `--owner`, `touch-reviewed`, `skill list --stale`, `skill lint` (2000-token budget, owner/review warnings) — matching an SOP the team already encodes as "SOP ❌5" and "SOP P-5".

**关键事实**
- Skill registry exists: tables skill/skill_file/agent_skill created in server/migrations/008_structured_skills.up.sql (skill has name, description, content, config JSONB, created_by, UNIQUE(workspace_id,name); skill_file has path+content per skill)
- server/migrations/110_skill_owner_and_review.up.sql adds skill.owner_user_id and skill.last_reviewed_at backing `multica skill list --stale` and the 90-day review SOP (❌5)
- REST API for skills at server/cmd/server/router.go:943-956: GET/POST /api/skills, GET /api/skills/search, POST /api/skills/import, GET/PUT/DELETE /api/skills/{id}, POST /{id}/touch-reviewed, GET/PUT /{id}/files, DELETE /{id}/files/{fileId}
- CLI skill commands in server/cmd/multica/cmd_skill.go: list (--stale --output, :145-146), get, create (--name --description --content|--content-stdin|--content-file --config --owner --output, :161-168), update (:171-178), delete (--yes, :181), import (--url --on-conflict fail|overwrite|rename|skip, :184-186), touch-reviewed (:66-71), search (:92-97), pull (:73-81), lint (:83-90), files list/upsert/delete (:101-125)
- PULL command exists: `multica skill pull [<name-or-id>|--all] [--dir]` (cmd_skill.go:363-464) downloads skills from the workspace registry and reconstructs <dir>/<name>/SKILL.md (frontmatter rebuilt at :335-361) plus all bundled files[] at stored paths (:435-455); default dir ~/.claude/skills (:373-378); CLI_AND_DAEMON.md:572-576 calls it the self-update channel for skills
- Daemon auto-sync exists: skillSyncLoop (server/internal/daemon/skill_sync.go:62-104) started at daemon.go:674, gated by MULTICA_DAEMON_SKILL_WRITE (default OFF, config.go:114,516) with 6h interval via MULTICA_DAEMON_SKILL_SYNC_INTERVAL (config.go:115,524)
- skillSyncLoop pulls signed skill-bundle.tar.gz from GitHub repo feibo-ai/team-context skills-v* releases (server/internal/cli/skillsync.go:31-73), verifies sigstore attestation pinned to team-context skill-bundle-release.yml (attestation.go:45-52,248-256), checks revocations.json (skill_sync.go:153-156), and safely extracts into ~/.claude/skills with symlink/traversal defenses; SkillWriteGuard (skillsync.go:474-478) refuses dev boxes using git-symlink skill layouts
- Per-task skill injection: daemon writes agent-bound registry skills into task workdir at provider-native paths (.claude/skills/{name}/SKILL.md for Claude Code, CODEX_HOME/skills, .opencode, .pi, .cursor, .github, fallback .agent_context) — docs/product-overview.md:370-377, implementation server/internal/daemon/execenv/context.go:407-423 writeSkillFiles
- Built-in platform skills embedded at compile time and given to every agent: server/internal/service/builtin_skills.go:24 + server/internal/service/builtin_skills/ (multica-autopilots, multica-skill-importing, multica-working-on-issues, etc.)
- Local→registry import relay: web UI can list/import skills from a member machine via daemon (server/internal/handler/runtime_local_skills.go; routes at router.go:1051-1054 and 555-556)
- skills-lock.json at repo root pins 4 dev-time agent skills (frontend-design/anthropics, shadcn, ui-ux-pro-max, web-design-guidelines/vercel-labs) with source+computedHash; no code in the repo consumes it; installed artifact at .agents/skills/web-design-guidelines/SKILL.md; built-in skill multica-skill-importing/SKILL.md explicitly says `npx skills add` is NOT a Multica install
- project create flags verified at cmd_project.go:143-152: --title --description --status --icon --lead(:147) --dri(:148) --priority(:149) --start-date(:150) --due-date(:151) --repo; project list --full-id at :135; project assign-dri at :63-64; project update mirrors at :189-198
- issue create flags verified at cmd_issue.go:288-302: --title --description[-stdin|-file] --status --priority --assignee(:294)/--assignee-id(:295) --parent(:296) --project(:297) --start-date/--due-date(:298-299) --attachment(:302)
- auth status verified at cmd_auth.go:49-50 (impl :451-480, validates token via /api/me, prints Server/User/Token); user list verified at cmd_user.go:52-53 with --output at :79; label CRUD at cmd_label.go:24-75; issue label add/remove at cmd_issue_label.go:22-52
- Comment inline publish: `multica issue comment add --inline <html-path>` uploads a local HTML doc bound to the issue and embeds `!file[name](url)` to render inline under the comment (cmd_issue.go:354-361); thread-aware comment list flags --thread --tail --recent --roots-only --summary --before/--before-id (:330-337)
- skill lint enforces SKILL.md frontmatter name/description (ERROR), 2000-token body budget estimated floor(words*1.3) (ERROR), owner/last_reviewed_at presence and 90-day freshness (WARN), follows symlinked skill dirs (cmd_skill.go:507-590)
- Skill-distribution plan documented in RELEASES.md v0.4.15 section '⑩ skill/md 无感分发' (lines 145-150, references mini-ADR v4 ⑩c which is not in this repo); RELEASES.md:48 (TEA-113) defers fleet one-click skill update to a future task; decisions/ and cases/ contain no skill-distribution content; CLI_AND_DAEMON.md does not document MULTICA_DAEMON_SKILL_WRITE
- CLAUDE.md rule: changes to CLI commands/flags documented by built-in skills must update the corresponding SKILL.md and references/*-source-map.md in the same PR (built-in skills are source-traced contracts shipped to agents)

</details>

<details><summary><b>team-context-mcp 工具面</b></summary>

### team-context-mcp — Full Tool Surface & Skill-Relationship Map

#### 0. Repo shape

`/Users/mac/zzh/team-context-mcp` is a pnpm monorepo (v0.3.0, "remote-only · control plane edition") shipping a single deployable: **`@tcmcp/remote`**, a remote MCP server at `https://mcp.teamctx.actionow.ai/mcp` (README.md:6). Packages:

- `packages/remote` — the MCP server (express + `@modelcontextprotocol/sdk` StreamableHTTP), tools, auth, /health, DeploymentTracker
- `packages/feishu` — `FeishuClient` (lark SDK wrapper; messages, DM, doc import, wiki, chat search)
- `packages/config` — `ConfigSource` abstraction: `EnvConfigSource`, `MulticaConfigSource` (WS + poll), `LayeredConfigSource`, `MulticaControlPlaneClient`
- `packages/shared` — `MulticaClient` (issues/comments/labels/upload REST client), markdown/git/tokens helpers

The former `@tcmcp/local` (13 stdio doc-flow tools) was deleted in 0.3.0; its functions moved to team-context skills + the `multica` CLI (README.md:8-13, decision doc `/Users/mac/zzh/team-context/decisions/2026-06-08-drop-local-mcp.md`).

#### 1. Complete MCP tool surface (10 tools)

Authoritative registration is `buildToolDefs()` in `packages/remote/src/server.ts:242-340`. All are plain **tools** (no prompts/resources). Zod schemas are converted to JSON Schema by a hand-rolled walker (`server.ts:349-448`) that forces root `type:'object'` and flattens unions (Anthropic API rejects root `oneOf`).

##### multica-touching tools (write issues/comments/labels via `MulticaClient` with the *service token*)

| Tool | Description (registered) | Params (zod) | Backend |
|---|---|---|---|
| `plan_request_review` | "Label plan under-review + post reviewer prompt." (server.ts:246) | `multicaIssueId: string`, `reviewer: string` (plan_request_review.ts:4-7) | multica: `addLabel(计划-评审中)` + reviewer-prompt comment (plan_request_review.ts:17-33) |
| `betting_table_capture` | "Friday 投注表 issue (open / close / tally)." (server.ts:255) | discriminatedUnion on `action`: open → `weekOf`, `proposals[]{id,title,proposer,oneLiner?}` (1-20); close → `bettingIssueId`, `votes: Record<email,string[]>`, `topK` 1-10 default 5 (betting_table_capture.ts:4-21) | multica: `createIssue(labels:['投注表'])` / tally comment |
| `burnout_check_distribute` | "Monthly anonymized burnout check (distribute / collect)." (server.ts:266) | union on `action`: distribute → `teamEmails[]`, `month YYYY-MM`; collect → `month`, `teamContextRepo`, `responses[]?{q1,q2,q3: yes/no}`, `teamEmails[]?`, `driEmail` (burnout_check_distribute.ts:16-31) | Feishu DM + `msgHistoryP2P` scrape + local file write + multica alert issue (`倦怠预警`) |
| `should_i_use_ai` | "METR-aligned decision aid: use-ai / write-directly / borderline." (server.ts:277) | `taskDescription (≥5)`, `devExperienceYears`, `isFamiliarCodebase`, `taskEstimateMinutes` (should_i_use_ai.ts:3-8) | **pure function** — no multica, no Feishu (handler passes `undefined` deps, server.ts:279-280) |
| `code_review_request` | "Block self-review (❌1). Assign a reviewer + 代码评审 label." (server.ts:285) | `implementerAgentId`, `reviewerAgentId`, `commitHash /^[a-f0-9]{7,40}$/`, `prUrl?`, `context (≥10)` (code_review_request.ts:4-10) | multica: refuses self-review, `createIssue(labels:['代码评审'], assigneeType:'agent')` (code_review_request.ts:18-53) |

##### Feishu-only tools

| Tool | Description | Params | Feishu call |
|---|---|---|---|
| `notify_team` | "Send text or interactive card to the team Feishu chat (config: feishu_team_chat_id)." (server.ts:295-296) | `z.union([{text}, {card: record}])` (notify_team.ts:10-13) | `im.message.create` text/interactive to chat resolved from multica config key `feishu_team_chat_id` (notify_team.ts:19-22) |
| `dm_member` | "Send a P2P direct message to a member by email." (server.ts:306) | `email`, `text?`, `card?` (refine: one required) (dm_member.ts:8-14) | `dmSendByEmail` (`receive_id_type:'email'`) |
| `archive_to_wiki` | "Import a local markdown file as a Feishu docx, then link it under a wiki node." (server.ts:312-313) | `markdownPath`, `title`, `wikiSpaceId?`, `parentNodeToken?` (fall back to config `feishu_wiki_space_id` / `feishu_wiki_default_parent`) (archive_to_wiki.ts:13-18,25-26) | drive.media.uploadAll → importTask → wiki.spaceNode.create (feishu/client.ts:137-251) |
| `search_chat` | "Search Feishu workspace chats by query string (maintenance helper)." (server.ts:323) | `query (≥1)` (search_chat.ts:10-12) | `im.chat.search` |
| `read_member_dm` | "Read recent P2P chat history for one team member (used by burnout_check_distribute collect)." (server.ts:331-332) | `email (/^.+@.+$/)`, `sinceISO`, `limit? ≤200` (read_member_dm.ts:13-20) | contact.batchGetId → im.chat.search → im.message.list |

##### Skill-related tools: **none**

There is no skill fetch/serve/lint/pull tool in the MCP surface. `MulticaClient.listSkills()` (`GET /api/skills`, shared/src/multica-client.ts:291-293) and `getIssueRuns()` (:295-297) exist in the shared client but are **not wired to any registered tool** (grep confirms no non-test usage). Skill distribution is entirely `multica skill pull --all` via the CLI (INSTALL.md:58-62); skill lint is `multica skill lint` (README.md:75).

**Identity note:** per-user bearer auth resolves `req.userEmail` (auth.ts:100-113), but `ToolDeps` (server.ts:65-70) carries no user context — every multica write is made with the server's `MULTICA_SERVICE_TOKEN` (server.ts:504-508). Per-user auth is gate-only; SMOKE.md:91-93 confirms "per-tool authorization is not in v0.3.0".

#### 2. How team members connect

- **Transport**: Streamable HTTP (`StreamableHTTPServerTransport`) mounted on express at `POST/GET/DELETE /mcp` (server.ts:214-216), with **per-session transports** keyed by the `mcp-session-id` header — a fresh `{Server, transport}` pair per `initialize` (server.ts:149-212; fixes P1 Bug B single-client lockout, scripts/SMOKE-P1.md:79-97). A `stdio` mode also exists via `MCP_TRANSPORT` env (server.ts:457, 230-231). MCP protocol version 2024-11-05 (SMOKE.md:4).
- **Auth**: `Authorization: Bearer <multica token>` on `/mcp` (server.ts:140). Tokens are validated against multica `GET /api/me` and cached in-memory for 5 minutes per token (auth.ts:37-38, 53-93). 401 without/with invalid token (SMOKE.md:38-40). `/health` is unauthenticated (server.ts:139).
- **Per-user config**: each member runs `multica login` and copies the `token` field from `~/.multica/config.json` (INSTALL.md:23-26); tokens are per-user for audit (team-context docs/SYNC.md:41 "不是 DRI 私信(per-user 审计)").
- **Claude Code / Desktop**: INSTALL.md:29-40 shows `claude_desktop_config.json` → `mcpServers.tcmcp-remote = { url, headers: { Authorization: Bearer … } }`. team-context docs/SYNC.md:50-56 shows the Claude Code form (`~/.claude.json` or project `.mcp.json`): `"tcmcp-remote": {"type":"http","url":"https://mcp.teamctx.actionow.ai/mcp","headers":{"Authorization":"Bearer mul_…"}}`. No `claude mcp add` command is documented — both repos document manual JSON edits.
- **Codex CLI**: `codex mcp add-http tcmcp-remote <url> --header "Authorization: Bearer …"` (INSTALL.md:47-50) or `~/.codex/config.toml` `[mcp_servers.tcmcp-remote]` with `bearer_token_env_var = "TCMCP_AGENT_TOKEN"` (SYNC.md:59-61).
- **`TCMCP_REMOTE_URL` / `TCMCP_AGENT_TOKEN`**: these env vars are **not defined in team-context-mcp itself** — they're team-context conventions. `TCMCP_REMOTE_URL` defaults to `https://mcp.teamctx.actionow.ai/mcp` in `/Users/mac/zzh/team-context/scripts/_autopilot-common.sh:25`; autopilot **agents** get exactly 4 custom_env keys `TCMCP_REMOTE_URL / TCMCP_AGENT_TOKEN / AUTOPILOT_SCOPE / AUTOPILOT_SCOPE_NAME` (ONBOARDING-DRI.md:201,218; autopilots/README.md:14) and are forbidden to read `~/.multica/config.json` (autopilots/_agent-instructions.md:60). `TCMCP_AGENT_TOKEN` doubles as the Codex bearer env var (SYNC.md:59-61). In-repo smoke tooling uses different names: `TCMCP_URL` / `TCMCP_TOKEN` (packages/remote/scripts/smoke-p1.mjs:11-13).
- Expected verification: 10 tools visible from `tcmcp-remote` (INSTALL.md:64-68, SMOKE.md:30-36).

#### 3. MCP prompts / resources capabilities — NO

The server declares `capabilities: { tools: {} }` only, in both the top-level Server and each per-session Server (server.ts:132, 169). Only `ListToolsRequestSchema` and `CallToolRequestSchema` handlers are registered (server.ts:107-123). A repo-wide grep finds no `prompts`, `resources`, `GetPrompt`, `ListResources`, or `ReadResource` anywhere in non-test source. **The server cannot serve skills/instructions/prompts to agents over MCP today.** Skill/instruction delivery is out-of-band: multica skill registry (`multica skill pull --all` → `~/.claude/skills`), agent `instructions` injected from `autopilots/_agent-instructions.md` by the autopilot scripts, and repo softlinks (SYNC.md:66-70).

#### 4. Deployment model & multica integration

- **Zeabur**: service `tcmcp-remote-gres` (id 6a1805b332700e299b750370), project `teamctx` (6a1800dd7ba640a55b20bf41), public domain `mcp.teamctx.actionow.ai` routing `web` → container 8080 (DEPLOY.md:37-44). CD = Zeabur native git-trigger on `main` building the repo `Dockerfile`; CI = GitHub Actions `build-test` required check (DEPLOY.md:12-34). No image registry; rollback = redeploy older commit.
- **Docker**: multi-stage `node:22-alpine`, pnpm 11.0.9, builds shared→config→feishu→remote, runtime runs `node /app/packages/remote/dist/server.js` under tini as non-root (Dockerfile:18-94). `docker-compose.yml` is local-debug only (docker-compose.yml:1-4).
- **Bootstrap env** (Zeabur): `MCP_TRANSPORT=http`, `MCP_HTTP_PORT=8080`, `MULTICA_URL=http://multica-backend.zeabur.internal:8080`, `MULTICA_SERVICE_TOKEN` (admin/owner), `MULTICA_WORKSPACE_ID`, `INTEGRATION_NAME=team-context-mcp`, `INTEGRATION_KIND=mcp-server` (DEPLOY.md:59-67; server.ts:456-473).
- **multica as config/secret plane**: `MulticaConfigSource.start()` pulls the `mcp-server` integration named `team-context-mcp` (config keys like `feishu_team_chat_id`, `feishu_wiki_space_id`; INSTALL.md:121-129), subscribes to WS `integration:config-changed` events with exponential-backoff reconnect (5s→60s) and a 30s poll safety net (config/src/multica.ts:28-158). Secrets (`FEISHU_APP_ID`, `FEISHU_APP_SECRET`) are fetched per-key with a 5-min cache; every cache-miss writes a multica `secret:read` audit row (multica.ts:164-185, SMOKE.md:66-75). Rotation is reactive — `FeishuClient` drops its lark SDK on config-change and rebuilds against new secrets on next call, no redeploy (feishu/client.ts:12-33, README.md:45). Secret reads require an **admin/owner** service token (403 for members — INSTALL.md:95-117).
- **Degraded mode**: control-plane 404 → env-only `LayeredConfigSource([EnvConfigSource])` and `/health` reports `multica_control_plane_enabled:false` (server.ts:484-495; multica.ts:57-68).
- **DeploymentTracker**: registers via `POST /api/deployments` and heartbeats every 30s with applied config version; best-effort, stats surfaced in `/health.deployment` (deployment.ts:1-60, health.ts:113-122).
- **Health**: `/health` reports status/version(git sha)/config_version/config_source/multica_control_plane_enabled/multica_reachable/feishu_ready/deployment; `degraded` iff multica unreachable (health.ts:60-124). *Observation*: health.ts:107-110 sets `feishu_ready = typeof ping === 'function'` and ignores ping's boolean return — since `FeishuClient.ping()` catches internally and returns `false` instead of throwing (feishu/client.ts:42-54), `feishu_ready` can read `true` even when Feishu creds are broken, contradicting INSTALL.md:176's semantics.

#### 5. Overlap analysis: MCP tools vs team skills / multica CLI / publish.py

##### Where the split is clean (no duplication)
- **Doc flow (plan/research/case/handoff)** lives exclusively in `team-context/skills/tc-render/publish.py` (render + hard validation + 命门B inline publish via `multica issue comment add --inline`) — the 13 local MCP tools that did this were deleted; replacement map in README.md:66-84. `@tcmcp/remote` never had these.
- **`notify_team`** — sole broadcast channel; used by skills `tc-1-start` (SKILL.md:20,60,65: "notify_team 走 remote MCP,非本地"), `tc-4-build` (SKILL.md:41), and all 5 autopilots (daily-kickoff.yaml:60, monday-kickoff.yaml:50, daily-summary.yaml:57, wednesday-stats.yaml:48, monthly-health.yaml:63). No CLI/script equivalent — genuine unique value (server holds the Feishu secret; agents never see it, team-context/README.md:47).
- **`betting_table_capture`** — used by tc-friday skill (SKILL.md:3,37). MCP-only.
- **`dm_member`/`read_member_dm`** — MCP-only Feishu P2P; autopilot agents are explicitly forbidden from `dm_member` (autopilots/_agent-instructions.md:25).

##### Confirmed duplication (double-writer risk, documented deprecation)
- **`plan_request_review` (MCP) vs `transition.py plan-request-review`**: both add label `计划-评审中`. team-context `standards/labels.md:26` explicitly says the remote MCP's **label write path is deprecated** — "请审统一走 transition.py plan-request-review,避免双写者打架" — yet the tool is still registered on the server (server.ts:244-252). Behavior also diverges: the MCP tool adds the label + posts a reviewer-prompt comment but never sets `status=in_review` (plan_request_review.ts:17-33), while transition.py sets label **and** status (transition.py:185-191, compute_plan_request_review). tc-3-plan skill invokes transition.py, not the MCP tool (tc-3-plan/SKILL.md:111-113).
- **Issue label/status transitions generally**: transition.py implements 7+ atomic subcommands (publish-init/plan-request-review/plan-approve/plan-upgrade/build-start/design-request-review/design-approve/case-finalize/cancel) over the same multica label/status primitives that `MulticaClient.addLabel/removeLabel/updateIssue` wraps in TS (shared/multica-client.ts:205-289). Two independent implementations of the state machine glue exist (Python skill-side authoritative; TS server-side vestigial for the 3 MCP tools that still write labels 投注表/倦怠预警/代码评审 — labels.md:21-23 assigns those three to "remote MCP").
- **Inline doc publish**: `MulticaClient.publishDoc()` (upload → `!file[](url)` embed comment, shared/multica-client.ts:152-167, fileEmbed :14-16) implements exactly the 命门A mechanism that `publish.py` (命门B via CLI `--inline`) now owns. No registered remote tool calls `publishDoc` — it's leftover from the deleted `@tcmcp/local` and duplicates publish.py's core.
- **`code_review_request`**: creates a 代码评审 issue with self-review refusal (❌1). In practice the skills' third review gate (代码评审, tc-3-plan/SKILL.md:143) is run through orchestrated 评审子 agents; `tc-4-build/SKILL.md` never references the tool. Duplication of process with weak adoption — labels.md:23 still credits the label to the MCP tool.
- **`should_i_use_ai`**: pure heuristic with zero platform deps (should_i_use_ai.ts:20-102); the same METR ❌8/❌9 guidance lives as prose in `tc-self-check/SKILL.md:35-48`. Could be a skill; no skill invokes the tool.
- **skill lint**: former `skill_lint` tool → `multica skill lint` CLI, but `tc-ops/SKILL.md:18` says its script "内联复刻 multica skill lint" — a third copy of lint logic.

##### Gaps (broken or missing seams)
- **Filesystem mismatch after local→remote move**: `archive_to_wiki` reads `markdownPath` with `readFile` **on the server** (feishu/client.ts:143), but `monthly-health.yaml:52-55` has the agent write `/tmp/monthly-health-{{date}}.md` on the **agent's machine** and then call the remote tool with that path — the file does not exist on the Zeabur container. Same class: `burnout_check_distribute` collect writes its report to `join(teamContextRepo, 'health/burnout', month.md)` on the server container (burnout_check_distribute.ts:131-133) — ephemeral storage, and the alert issue body references that container-local path (:137-141). These tools' file I/O semantics predate the remote-only move.
- **No MCP prompts/resources → no skill serving**: agents that only have MCP access (no multica CLI) cannot fetch tc-* skills or instructions; distribution requires the CLI (`multica skill pull --all`) and shell rc setup (ONBOARDING-AGENT.html:394-402). The MCP server could close this via resources/prompts but currently declares tools-only (server.ts:132).
- **Unused client surface**: `MulticaClient.listSkills()`/`getIssueRuns()` (shared/multica-client.ts:291-297) and `publishDoc/uploadFile` have no tool consumers — dead weight or future hooks (the partially-voided cap-hardening plan, docs/plans/plan_2026-06-05_cap-hardening-mcp.html, proposed ≤8 more thin-façade remote tools like design_review/delivery_metrics, explicitly noting local-side items are void).
- **Attribution gap**: all multica writes from MCP tools use the service token, so issues/comments created via `plan_request_review`/`betting_table_capture`/`code_review_request` are not attributed to the calling user despite per-user bearer auth (server.ts:504-508, SMOKE.md:91-93). The skills' CLI path (`multica issue create --assignee "$ME_NAME"`) *is* per-user.

**关键事实**
- The remote MCP server registers exactly 10 tools in buildToolDefs(): plan_request_review, betting_table_capture, burnout_check_distribute, should_i_use_ai, code_review_request, notify_team, dm_member, archive_to_wiki, search_chat, read_member_dm — packages/remote/src/server.ts:242-340
- Server declares capabilities { tools: {} } only — no MCP prompts or resources handlers anywhere; only ListToolsRequestSchema and CallToolRequestSchema are registered — packages/remote/src/server.ts:132,169 and :107-123
- No skill-related MCP tools exist; MulticaClient.listSkills() (GET /api/skills) and getIssueRuns() are defined but unused by any registered tool — packages/shared/src/multica-client.ts:291-297
- Feishu-only tools: notify_team (chat from config key feishu_team_chat_id, notify_team.ts:19), dm_member, archive_to_wiki (md→docx import→wiki node, archive_to_wiki.ts:30-40), search_chat, read_member_dm; multica-writing tools: plan_request_review, betting_table_capture, burnout_check_distribute (also Feishu), code_review_request; should_i_use_ai is a pure function with no deps — should_i_use_ai.ts:20-23
- Transport is Streamable HTTP on express POST/GET/DELETE /mcp with per-session transports keyed by mcp-session-id header (plus optional stdio via MCP_TRANSPORT env) — packages/remote/src/server.ts:136-231
- Auth: Bearer multica token validated against multica GET /api/me, cached in-memory 5 minutes per token (TTL_MS = 5*60_000); 401 otherwise — packages/remote/src/auth.ts:37-93; per-tool RBAC explicitly absent in v0.3.0 — SMOKE.md:91-93
- Team members connect by adding mcpServers.tcmcp-remote = { url: https://mcp.teamctx.actionow.ai/mcp, headers: { Authorization: Bearer <token from multica login → ~/.multica/config.json> } } — INSTALL.md:23-40; Claude Code form (~/.claude.json or project .mcp.json with type:http) — /Users/mac/zzh/team-context/docs/SYNC.md:50-54; Codex uses codex mcp add-http or config.toml bearer_token_env_var=TCMCP_AGENT_TOKEN — INSTALL.md:47-50, SYNC.md:59-61
- TCMCP_REMOTE_URL and TCMCP_AGENT_TOKEN are team-context (sister repo) conventions, not read by team-context-mcp code: default URL set in /Users/mac/zzh/team-context/scripts/_autopilot-common.sh:25; injected as agent custom_env (4 keys with AUTOPILOT_SCOPE/AUTOPILOT_SCOPE_NAME) — /Users/mac/zzh/team-context/docs/ONBOARDING-DRI.md:218, autopilots/README.md:14; repo's own smoke script uses TCMCP_URL/TCMCP_TOKEN instead — packages/remote/scripts/smoke-p1.mjs:11-13
- Deployment: Zeabur service tcmcp-remote-gres in project teamctx, CD via Zeabur git-trigger on main building the Dockerfile (node:22-alpine multi-stage, tini, non-root); CI is GitHub Actions build-test required check — DEPLOY.md:12-44, Dockerfile:18-94
- Config/secrets come from a multica mcp-server integration named team-context-mcp: MulticaConfigSource pulls config, subscribes WS integration:config-changed with 5s→60s backoff and 30s poll fallback; FEISHU_APP_ID/FEISHU_APP_SECRET fetched as secrets with 5-min cache, each cache-miss writing a multica secret:read audit row; rotation is reactive with no redeploy — packages/config/src/multica.ts:28-185, packages/feishu/src/client.ts:12-33, DEPLOY.md:110-116
- On control-plane 404 the server falls back to env-only LayeredConfigSource and /health reports multica_control_plane_enabled:false; status degrades only when multica is unreachable — packages/remote/src/server.ts:484-495, packages/remote/src/health.ts:60-124
- All multica writes from MCP tools use the server's MULTICA_SERVICE_TOKEN (admin/owner), not the calling user's token; auth resolves req.userEmail but ToolDeps carries no user context — packages/remote/src/server.ts:65-70,504-508
- Duplication: plan_request_review (MCP) and skills/tc-render/transition.py plan-request-review both add label 计划-评审中; team-context standards/labels.md:26 declares the MCP label path deprecated ('避免双写者打架') yet the tool remains registered; the MCP version also omits status=in_review that transition.py sets — team-context-mcp plan_request_review.ts:17-33 vs team-context/skills/tc-render/transition.py:185-191
- Duplication: MulticaClient.publishDoc/fileEmbed implements the same upload + !file inline-comment publish mechanism as team-context skills/tc-render/publish.py (命门B via multica issue comment add --inline) but has no tool consumer since @tcmcp/local was deleted — packages/shared/src/multica-client.ts:14-16,152-167; README.md:66-84 replacement map
- Gap: archive_to_wiki reads markdownPath server-side via readFile (packages/feishu/src/client.ts:143) but monthly-health autopilot passes /tmp/monthly-health-{{date}}.md written on the agent's machine — path cannot exist on the Zeabur container — /Users/mac/zzh/team-context/autopilots/monthly-health.yaml:44-55
- Gap: burnout_check_distribute collect writes its report to join(teamContextRepo,'health/burnout',<month>.md) on the server container's ephemeral filesystem and references that path in the alert issue — packages/remote/src/tools/burnout_check_distribute.ts:131-141
- Skills actually consuming MCP tools: tc-1-start and tc-4-build use notify_team (tc-1-start/SKILL.md:20,60,65; tc-4-build/SKILL.md:41), tc-friday uses betting_table_capture (tc-friday/SKILL.md:3,37), all 5 autopilots use notify_team and monthly-health uses archive_to_wiki; code_review_request and should_i_use_ai have no skill callers (code review runs via 评审子 agents, METR guidance duplicated as prose in tc-self-check/SKILL.md:35-48)
- Health endpoint bug-class observation: health.ts sets feishu_ready = typeof ping === 'function' ignoring ping()'s boolean result, and FeishuClient.ping() returns false instead of throwing, so feishu_ready can report true with broken Feishu creds — packages/remote/src/health.ts:107-110 vs packages/feishu/src/client.ts:42-54
- Former local MCP replacement map: doc_publish/plan_create/research_create/case_create/session_handoff/plan_upgrade → skills/tc-render/publish.py; skill_lint → multica skill lint; skill self-update → multica skill pull; plan_approve/case_review → skill-driven multica CLI; project_kickoff → tc-1-start skill; monthly_health_report/autopilot_lint → tc-ops scripts — README.md:66-84, decision /Users/mac/zzh/team-context/decisions/2026-06-08-drop-local-mcp.md

</details>

<details><summary><b>官方标准（Agent Skills / Plugin / Codex）</b></summary>

### Claude Code Agent Skills & Team-Scale Distribution — Current Official Standard (as of 2026-07-03)

Sources consulted (all fetched live today):
- https://code.claude.com/docs/en/skills (official)
- https://code.claude.com/docs/en/plugins (official)
- https://code.claude.com/docs/en/plugins-reference (official)
- https://code.claude.com/docs/en/plugin-marketplaces (official)
- https://code.claude.com/docs/en/discover-plugins (official)
- https://code.claude.com/docs/en/settings (official)
- https://code.claude.com/docs/en/memory (official)
- https://agentskills.io/specification (the open Agent Skills spec Claude Code follows)
- https://developers.openai.com/codex/skills and https://developers.openai.com/codex/guides/agents-md (OpenAI official, via fetch/search)

---

#### 1. SKILL.md format

There are two layers: the **open Agent Skills standard** (agentskills.io) and **Claude Code's extensions** of it. The Claude Code docs state verbatim: "Claude Code skills follow the Agent Skills open standard... Claude Code extends the standard with additional features like invocation control, subagent execution, and dynamic context injection."

##### 1a. The open standard (agentskills.io/specification)

A skill is a directory containing at minimum `SKILL.md` (YAML frontmatter + Markdown body). Spec frontmatter:

| Field | Required | Constraints |
|---|---|---|
| `name` | Yes | 1–64 chars; lowercase `a-z`, `0-9`, hyphens only; no leading/trailing hyphen; no consecutive `--`; **must match the parent directory name** |
| `description` | Yes | 1–1024 chars, non-empty; what it does + when to use it |
| `license` | No | License name or reference to bundled license file |
| `compatibility` | No | 1–500 chars; environment requirements (product, packages, network). "Most skills do not need" it |
| `metadata` | No | Arbitrary string→string map for client-specific extras; "make your key names reasonably unique" |
| `allowed-tools` | No | Space-separated pre-approved tool string. **Experimental**; "support may vary between agent implementations" |

Body: no format restrictions; recommended sections are step-by-step instructions, input/output examples, edge cases. Optional conventional dirs: `scripts/` (executable code), `references/` (on-demand docs), `assets/` (templates/images/data). Progressive disclosure has three levels: (1) metadata (~100 tokens: name+description) loaded at startup for all skills; (2) instructions (SKILL.md body, <5,000 tokens recommended) loaded on activation; (3) resources loaded only as needed. Keep SKILL.md under 500 lines; keep file references one level deep, relative to the skill root. Validation: `skills-ref validate ./my-skill` (github.com/agentskills/agentskills, skills-ref library).

##### 1b. Claude Code's frontmatter (superset)

In Claude Code, **all frontmatter fields are optional; only `description` is recommended** (if omitted, the first paragraph of body is used). `name` is a display label defaulting to the directory name — the command name comes from the directory/file name, except for a plugin-root SKILL.md where frontmatter `name` sets the invocation name. Full field list (official docs):

- `name`, `description`, `when_to_use` (extra trigger context appended to description; combined description+when_to_use is truncated at **1,536 chars** in the skill listing, configurable via `skillListingMaxDescChars`)
- `argument-hint`, `arguments` (named positional args for `$name` substitution)
- `disable-model-invocation` (true = only the user can invoke; skill's description is **not** loaded into context; also blocks preloading into subagents and, ≥v2.1.196, scheduled-task invocation)
- `user-invocable` (false = hidden from the `/` menu; Claude can still invoke)
- `allowed-tools` (permission **grant** while skill is active — does NOT restrict the tool pool; accepts space/comma-separated string or YAML list; for project skills takes effect only after the workspace trust dialog)
- `disallowed-tools` (removes tools from the pool while active; clears on your next message)
- `model` (model override for the rest of the turn; same values as `/model` or `inherit`; values excluded by an org's `availableModels` allowlist are ignored)
- `effort` (`low`|`medium`|`high`|`xhigh`|`max`)
- `context: fork` (run in a forked subagent) and `agent` (which subagent type: `Explore`, `Plan`, `general-purpose`, or custom)
- `hooks` (hooks scoped to the skill lifecycle), `paths` (glob patterns limiting auto-activation to matching files), `shell` (`bash`|`powershell` for `!`command`` injection)

**Extra/unknown fields:** the open spec provides `license`, `compatibility`, `metadata` as legal; Claude Code's docs don't list them in its frontmatter table but nothing documents rejection — malformed YAML causes the skill to load with *empty* metadata (body still works via `/skill-name`); `claude plugin validate` reports frontmatter YAML parse errors. (Inference: unknown frontmatter keys are tolerated/ignored rather than rejected; only malformed YAML degrades the skill.)

**Dynamic features (Claude Code-specific):** `$ARGUMENTS`, `$ARGUMENTS[N]`, `$N`, named `$name` args, `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}`, `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PROJECT_DIR}` (≥v2.1.196) substitutions; `` !`command` `` inline and ```` ```! ```` block dynamic-context injection (shell runs BEFORE Claude sees the content; disable org-wide with `disableSkillShellExecution: true`, most useful in managed settings). Scripts can be bundled and executed (reference them via `${CLAUDE_SKILL_DIR}/scripts/...`); executable files are executed, not loaded into context.

**Note:** custom commands have been merged into skills — `.claude/commands/deploy.md` and `.claude/skills/deploy/SKILL.md` both create `/deploy`; commands support the same frontmatter; if both exist with one name, the skill wins.

---

#### 2. Discovery mechanics in Claude Code

**What loads at session start:** the names of ALL skills are always listed; descriptions load into context so Claude knows what's available (skills with `disable-model-invocation: true` are excluded from the listing). Full body loads only on invocation. The listing has a context budget of **1% of the model's context window** (raise via `skillListingBudgetFraction` setting or `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var); on overflow, descriptions of least-invoked skills are dropped first; `/doctor` shows shortened/dropped skills.

**Lifecycle:** once invoked, the rendered SKILL.md enters the conversation as a single message and stays for the session (not re-read on later turns). On auto-compaction, the most recent invocation of each skill is re-attached, keeping the first 5,000 tokens of each within a combined 25,000-token budget (most-recent-first).

**Triggering:** Claude auto-invokes based on `description` matching (via the Skill tool), or the user types `/skill-name [args]`. Access control: deny `Skill` tool entirely, or use permission rules `Skill(name)` / `Skill(name *)`. Per-skill visibility can also be overridden without editing SKILL.md via the `skillOverrides` setting (`"on"` | `"name-only"` | `"user-invocable-only"` | `"off"`); plugin skills are exempt from skillOverrides (manage via `/plugin`).

**Locations & precedence (official table):**
| Level | Path | Applies to |
|---|---|---|
| Enterprise | via managed settings (settings-files section) | all users in the org |
| Personal | `~/.claude/skills/<name>/SKILL.md` | all your projects |
| Project | `.claude/skills/<name>/SKILL.md` | that project |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | wherever plugin is enabled |

Same-name conflict rule (verbatim): "enterprise overrides personal, and personal overrides project." A skill at any of these levels also overrides a **bundled** skill of the same name (e.g., a project `code-review` replaces bundled `/code-review`). **Plugin skills are always namespaced `plugin-name:skill-name` so they cannot conflict** with other levels.

**Nested/monorepo discovery:** project skills load from `.claude/skills/` in the starting directory and every parent up to the repo root; nested `.claude/skills/` in subdirectories are discovered on demand when Claude works with files there. Name clashes with nested skills keep both, with the nested one under a directory-qualified name like `/apps/web:deploy`. Symlinked skill directories are followed (deduped if reachable twice). `--add-dir`/`/add-dir` directories DO load their `.claude/skills/` (an explicit exception; `permissions.additionalDirectories` in settings does not). Live change detection: SKILL.md edits under watched skill dirs take effect mid-session; creating a brand-new top-level skills dir requires restart; plugin-component changes need `/reload-plugins`.

---

#### 3. Plugins as team distribution

**Plugin structure:** a self-contained directory. Only `plugin.json` lives in `.claude-plugin/`; everything else at the plugin root:
- `.claude-plugin/plugin.json` — manifest (**optional**; if present, `name` is the only required field; kebab-case)
- `skills/<name>/SKILL.md` (or a single root `SKILL.md` for one-skill plugins, ≥v2.1.142; frontmatter `name` sets its invocation name)
- `commands/` (flat .md skills; legacy — "Use skills/ for new plugins")
- `agents/` (subagent .md files: `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `isolation`; `hooks`/`mcpServers`/`permissionMode` NOT supported for plugin agents for security)
- `hooks/hooks.json`, `.mcp.json` (MCP servers — **yes, plugins ship MCP config**), `.lsp.json`, `output-styles/`, `themes/` (experimental), `monitors/monitors.json` (experimental), `bin/` (executables added to Bash PATH while enabled), `settings.json` (default settings; only `agent` and `subagentStatusLine` keys supported currently)

**Can a plugin ship a CLAUDE.md-like context file? No.** Verbatim: "A CLAUDE.md file at the plugin root is not loaded as project context... To ship instructions that load into Claude's context, put them in a skill." (A `user-invocable: false` skill is the idiomatic substitute for always-relevant background knowledge — inference.)

`plugin.json` fields: `name` (required), `displayName`, `version` (pins updates — if set, users only update when you bump it; if omitted, git commit SHA = version so every commit is an update), `description`, `author {name,email,url}`, `homepage`, `repository`, `license`, `keywords`, `defaultEnabled` (≥2.1.154), component-path overrides (`skills` adds to default scan; `commands`/`agents`/`outputStyles` replace defaults), `mcpServers`/`hooks`/`lspServers` (inline or path), `userConfig` (prompts users for config at enable time, `sensitive` values go to keychain), `channels`, `dependencies`. Unrecognized top-level fields are ignored (warnings only) — so one manifest can double as package.json/VS Code manifest. Paths must be relative starting `./`. Use `${CLAUDE_PLUGIN_ROOT}` (install dir, changes each update), `${CLAUDE_PLUGIN_DATA}` (persistent across updates, `~/.claude/plugins/data/<id>/`), `${CLAUDE_PROJECT_DIR}`.

**marketplace.json** at `<repo>/.claude-plugin/marketplace.json`. Required: `name` (kebab-case; reserved names like `claude-plugins-official`, `anthropic-*` etc. blocked), `owner {name, email?}`, `plugins[]`. Optional: `$schema`, `description`, `version`, `metadata.pluginRoot`, `allowCrossMarketplaceDependenciesOn`, `renames` (≥2.1.193, rename/removal migration map). Each plugin entry: required `name` + `source`; sources: relative path `"./plugins/x"` (resolved against the marketplace root), `{"source":"github","repo":"owner/repo","ref?","sha?"}`, `{"source":"url","url":...}` (any git host), `{"source":"git-subdir","url","path","ref?","sha?"}` (sparse clone for monorepos), `{"source":"npm","package","version?","registry?"}`. Entries may also carry `displayName`, `version`, `author`, `homepage`, `repository`, `license`, `keywords`, `category`, `tags`, `strict` (false = marketplace entry is the whole plugin definition), `relevance`, `defaultEnabled`, and component-config fields (`skills`, `commands`, `agents`, `hooks`, `mcpServers`, `lspServers`).

**Team publish/install flow (official):**
1. Publisher: create repo with `.claude-plugin/marketplace.json` + plugins (in-repo via relative paths or external sources); validate with `claude plugin validate .`; push to GitHub/GitLab/any git host (GitHub recommended). Private repos supported (interactive ops use git credential helpers; background auto-update needs `GITHUB_TOKEN`/`GH_TOKEN`, `GITLAB_TOKEN`/`GL_TOKEN`, or `BITBUCKET_TOKEN` in env).
2. Members: `/plugin marketplace add owner/repo` (or `claude plugin marketplace add <source> [--scope user|project|local] [--sparse ...]`; append `@ref` to GitHub shorthand or `#ref` to git URL to pin), then `/plugin install name@marketplace` (or `claude plugin install ... --scope ...`). Installed plugins are **copied to a versioned cache** at `~/.claude/plugins/cache` (can't reference `../` outside the plugin; symlinks within the same marketplace are dereferenced into the cache; old versions garbage-collected after ~7 days). Marketplace state lives in `~/.claude/plugins/known_marketplaces.json` (per-user).
3. Zero-friction team default: put in the repo's `.claude/settings.json`: `"extraKnownMarketplaces": {"company-tools": {"source": {"source":"github","repo":"your-org/claude-plugins"}}}` plus `"enabledPlugins": {"code-formatter@company-tools": true}`. When teammates trust the folder, Claude Code prompts them to install. (Note: as of v2.1.195, externally-sourced plugins enabled only by project settings still require the one-time `claude plugin install` the prompt shows.) `claude plugin marketplace add <src> --scope project` writes this for you. There is no `extraDirectories` mechanism for this — the settings keys are `extraKnownMarketplaces` and `enabledPlugins`.

**Updates/auto-update:** `/plugin marketplace update [name]` refreshes catalogs; `claude plugin update <plugin>` updates a plugin. Auto-update runs at startup per marketplace: enabled by default for official Anthropic marketplaces, **disabled by default for third-party/local marketplaces** (toggle in `/plugin` → Marketplaces); admins can set `"autoUpdate": true` on an `extraKnownMarketplaces` entry in managed settings. `DISABLE_AUTOUPDATER=1` kills all auto-updates; add `FORCE_AUTOUPDATE_PLUGINS=1` to keep plugin auto-updates while freezing the CLI. Version resolution order: plugin.json `version` → marketplace-entry `version` → git commit SHA → `unknown`. Release channels = two marketplaces pinned to different refs, assigned to user groups via managed settings.

**Other distribution surfaces:** `--plugin-dir ./dir` (session-only; also accepts .zip ≥v2.1.128; local copy shadows same-name installed plugin), `--plugin-url https://.../plugin.zip` (session-only CI artifacts), skills-directory plugins (any folder under `~/.claude/skills/` or `<cwd>/.claude/skills/` containing `.claude-plugin/plugin.json` auto-loads as `<name>@skills-dir` — no marketplace/install; scaffold via `claude plugin init`; project-scope ones gate on workspace trust, their MCP servers need per-server approval, monitors don't load), and `CLAUDE_CODE_PLUGIN_SEED_DIR` for containers/CI (pre-baked read-only plugin cache mirroring `~/.claude/plugins`; build with `CLAUDE_CODE_PLUGIN_CACHE_DIR`). Anthropic-run distribution: `claude-plugins-official` (curated, auto-registered) and `claude-community` (`anthropics/claude-plugins-community`, submission via claude.ai admin form — requires Team/Enterprise org + directory access — or platform.claude.com/plugins/submit; approved plugins pinned to commit SHAs, CI bumps pins, nightly catalog sync).

---

#### 4. Organization-wide distribution (recommended, mid-2026)

Layered picture from official docs:

1. **Team/repo scale → plugin marketplace + project settings.** Host `marketplace.json` in a (private) git repo; commit `extraKnownMarketplaces` + `enabledPlugins` to the repo's `.claude/settings.json`. Trust-dialog-gated prompt installs for every collaborator. Simplest alternative for skills only: commit `.claude/skills/` to the repo (docs list "Project skills: Commit .claude/skills/ to version control" as a first-class sharing option).
2. **Organization scale → managed settings.** Delivery mechanisms: file at `/Library/Application Support/ClaudeCode/managed-settings.json` (macOS), `/etc/claude-code/managed-settings.json` (Linux/WSL), `C:\Program Files\ClaudeCode\managed-settings.json` (Windows); MDM (macOS `com.anthropic.claudecode` plist domain; Windows `HKLM\SOFTWARE\Policies\ClaudeCode` registry); a `managed-settings.d/` drop-in directory; or **server-managed settings delivered at sign-in from the claude.ai admin console / self-hosted gateway** (the newest mechanism). Managed settings are top-precedence and non-overridable. In them, admins: register org marketplaces (`extraKnownMarketplaces`, optionally with `"autoUpdate": true`), force-enable plugins (`enabledPlugins` at managed scope — read-only to users, shows as "managed" scope), lock down sources (`strictKnownMarketplaces` allowlist incl. `hostPattern`/`pathPattern` regex entries; `[]` = full lockdown; `blockedMarketplaces` denylist wins; pair with `disableSideloadFlags` to reject `--plugin-dir`/`--plugin-url` sideloading), allowlist plugin suggestions (`pluginSuggestionMarketplaces`), disable skill shell injection (`disableSkillShellExecution`), and disable bundled skills (`disableBundledSkills`). The skills doc's location table also lists an **Enterprise skills level** deployed "through managed settings" that overrides personal and project same-name skills.
3. **MCP to the whole team:** project-level `.mcp.json` committed to the repo (per-server user approval, or `enableAllProjectMcpServers`); plugin-bundled `.mcp.json` (starts when plugin enabled — so a marketplace plugin is the recommended vehicle to ship skills+MCP together); org level via **`managed-mcp.json`** in the managed-settings directory (exclusive control; `allowAllClaudeAiMcps` to also allow claude.ai connectors) plus `allowedMcpServers` / `deniedMcpServers` / `allowManagedMcpServersOnly` policy settings (denylist wins).
4. **Org-wide context:** managed CLAUDE.md at the managed-policy path (or inline via the `claudeMd` key inside managed-settings.json); cannot be excluded by users.
5. **Containers/CI:** `CLAUDE_CODE_PLUGIN_SEED_DIR` (read-only seed; seed entries take precedence; composes with `extraKnownMarketplaces`).

Practical recommendation the docs converge on (light inference from the above): package skills + MCP + hooks + agents as plugins in a single private-git marketplace; use project `.claude/settings.json` for per-repo opt-in and managed settings for org mandates/lockdown; omit `version` for SHA-based continuous updates or bump `version` for release discipline; set the auth token env var so private-marketplace auto-update works.

Caveat: a secondary summarization of the settings page labeled `extraKnownMarketplaces`/`enabledPlugins` "managed only" — that is contradicted by the primary marketplace/plugins-reference pages, which explicitly document both in project/user/local settings; only `strictKnownMarketplaces`/`blockedMarketplaces`/`pluginSuggestionMarketplaces` are managed-settings-only enforcement.

---

#### 5. Codex (OpenAI) compatibility — serving one repo to both

Official doc-level facts (developers.openai.com):
- Codex Agent Skills "build on the open agent skills standard" (agentskills.io) — the same standard Claude Code follows. A Codex skill is a directory with `SKILL.md`; frontmatter requires `name` and `description`; description drives implicit triggering ("front-load the key use case and trigger words").
- **Codex scans different paths than Claude Code:** `.agents/skills` in the cwd and each directory up to the repo root, `$HOME/.agents/skills` (user), `/etc/codex/skills` (admin), plus OpenAI-bundled skills. Codex has an optional per-skill `agents/openai.yaml` metadata file (`interface` display fields, `policy.allow_implicit_invocation` default true, `dependencies.tools`). Invocation: implicit by description match, or explicit via `/skills` / `$skillname`. Skills listing capped at ~2% of context (8,000 chars when window unknown). Curated installs via `$skill-installer`.
- **AGENTS.md:** Codex reads `AGENTS.override.md`, then `AGENTS.md`, then `project_doc_fallback_filenames`, walking from project root down to cwd. **Claude Code explicitly does NOT read AGENTS.md**: "Claude Code reads CLAUDE.md, not AGENTS.md." The officially documented bridge: create a CLAUDE.md containing `@AGENTS.md` (import) optionally followed by Claude-specific sections, or `ln -s AGENTS.md CLAUDE.md`; `/init` in a repo with AGENTS.md incorporates it.

Dual-tool repo recipe (inference from the above doc facts):
- Context: keep `AGENTS.md` canonical; add a one-line `CLAUDE.md` = `@AGENTS.md` (+ Claude-specific extras). Works natively in both tools.
- Skills: author to the portable agentskills.io subset (`name` matching dir, `description` ≤1024 chars, `license`/`metadata`/`compatibility`; `scripts/`/`references/`/`assets/` layout; SKILL.md <500 lines). Maintain one canonical skill tree and expose it at both scan roots — e.g., `.claude/skills/<name>` and `.agents/skills/<name>` via symlinks (Claude Code documents following skill symlinks; Codex symlink behavior is not documented — verify). Keep Claude-only frontmatter (`context: fork`, `hooks`, `paths`, `model`, `disable-model-invocation`) and Claude-only body features (`!`cmd`` injection, `$ARGUMENTS`, `${CLAUDE_SKILL_DIR}`) out of shared skills or expect them to be inert/literal in Codex; put Codex-specific config in `agents/openai.yaml`, which Claude Code will simply not read. `allowed-tools` is experimental in the spec and portable in name only.
- Plugins/marketplaces are Claude Code-only distribution; for Codex users the same repo's raw `.agents/skills` tree (or `$skill-installer`) is the distribution channel.

**关键事实**
- [official: agentskills.io/specification] SKILL.md frontmatter requires `name` (1-64 chars, lowercase alphanumerics+hyphens, no leading/trailing/consecutive hyphens, must match parent directory name) and `description` (1-1024 chars); optional fields are `license`, `compatibility` (1-500 chars), `metadata` (arbitrary string map), and experimental `allowed-tools` (space-separated string).
- [official: agentskills.io/specification] Progressive disclosure levels: metadata (~100 tokens, name+description loaded at startup for all skills), instructions (<5000 tokens recommended, loaded on activation), resources (scripts/, references/, assets/ loaded as needed); keep SKILL.md under 500 lines; validate with `skills-ref validate`.
- [official: code.claude.com/docs/en/skills] In Claude Code all SKILL.md frontmatter fields are optional (only `description` recommended); Claude Code extensions include `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context: fork`, `agent`, `hooks`, `paths`, `shell`.
- [official: code.claude.com/docs/en/skills] Combined `description`+`when_to_use` text is truncated at 1,536 characters in the skill listing; the whole listing has a budget of 1% of the model context window (configurable via `skillListingBudgetFraction` or `SLASH_COMMAND_TOOL_CHAR_BUDGET`); least-invoked skills' descriptions drop first; `/doctor` reports shortening.
- [official: code.claude.com/docs/en/skills] At session start only skill names+descriptions load into context; full SKILL.md loads on invocation as a single message and persists; after compaction each invoked skill is re-attached keeping its first 5,000 tokens within a combined 25,000-token budget.
- [official: code.claude.com/docs/en/skills] Skill locations: Enterprise (via managed settings), Personal `~/.claude/skills/`, Project `.claude/skills/`, Plugin `<plugin>/skills/`; on name conflict 'enterprise overrides personal, and personal overrides project'; any level overrides a bundled skill of the same name; plugin skills are namespaced `plugin-name:skill-name` and cannot conflict.
- [official: code.claude.com/docs/en/skills] Custom commands are merged into skills: `.claude/commands/deploy.md` and `.claude/skills/deploy/SKILL.md` both create `/deploy`; a skill takes precedence over a same-named command; project skills also load from parent directories up to repo root and on-demand from nested `.claude/skills/` (monorepo support, `/apps/web:deploy` qualified names).
- [official: code.claude.com/docs/en/skills] `allowed-tools` in a skill grants permission without restricting the tool pool, and for project skills only takes effect after the workspace trust dialog; `disable-model-invocation: true` removes the skill's description from Claude's context entirely; `!`command`` dynamic context injection runs shell before Claude sees content and can be disabled org-wide with `disableSkillShellExecution: true`.
- [official: code.claude.com/docs/en/plugins-reference] plugin.json is optional; if present `name` is the only required field; unrecognized top-level fields are ignored (validation warnings only, `--strict` to fail); component dirs (skills/, commands/, agents/, hooks/, output-styles/, bin/, .mcp.json, .lsp.json, monitors/, settings.json) must be at plugin root, not inside .claude-plugin/.
- [official: code.claude.com/docs/en/plugins-reference] Plugins CAN ship skills, commands, agents, hooks, MCP servers (.mcp.json), LSP servers (.lsp.json), output styles, themes, monitors, bin/ executables (added to Bash PATH), and a settings.json (only `agent` and `subagentStatusLine` keys); a CLAUDE.md at the plugin root is NOT loaded as project context — docs say to use a skill instead.
- [official: code.claude.com/docs/en/plugin-marketplaces] marketplace.json lives at `.claude-plugin/marketplace.json`; required fields `name`, `owner{name}`, `plugins[]`; plugin entry requires `name`+`source`; source types: relative path './...', github {repo,ref?,sha?}, url (any git host), git-subdir {url,path} (sparse clone), npm {package,version?,registry?}; names like `claude-plugins-official`/`anthropic-*` are reserved.
- [official: code.claude.com/docs/en/plugin-marketplaces] Team flow: publisher pushes marketplace repo; members run `/plugin marketplace add owner/repo` then `/plugin install name@marketplace`; committing `extraKnownMarketplaces` and `enabledPlugins` to the repo's `.claude/settings.json` prompts teammates to install on folder trust; `claude plugin marketplace add <src> --scope project` writes this; there is no 'extraDirectories' setting for this purpose.
- [official: code.claude.com/docs/en/discover-plugins] Auto-update runs at startup per marketplace: enabled by default for official Anthropic marketplaces, disabled by default for third-party/local ones; admins can set `"autoUpdate": true` per `extraKnownMarketplaces` entry in managed settings; `DISABLE_AUTOUPDATER=1` disables everything and `FORCE_AUTOUPDATE_PLUGINS=1` re-enables plugin updates only.
- [official: code.claude.com/docs/en/plugins-reference] Version resolution: plugin.json `version` → marketplace entry `version` → git commit SHA → `unknown`; setting `version` pins the plugin (commits alone do not update users); omitting it makes every commit a new version — recommended for internal team plugins.
- [official: code.claude.com/docs/en/plugins-reference] Installed marketplace plugins are copied to `~/.claude/plugins/cache` (cannot reference `../` outside plugin root; in-marketplace symlinks are dereferenced into the cache; old versions cleaned after ~7 days); `${CLAUDE_PLUGIN_ROOT}` = install dir, `${CLAUDE_PLUGIN_DATA}` = persistent dir surviving updates.
- [official: code.claude.com/docs/en/plugins-reference] Skills-directory plugins: any folder under `~/.claude/skills/` or `<cwd>/.claude/skills/` containing `.claude-plugin/plugin.json` auto-loads as `<name>@skills-dir` with no install step (`claude plugin init` scaffolds one); project-scope ones require workspace trust and their monitors don't load.
- [official: code.claude.com/docs/en/settings + plugin-marketplaces] Managed settings paths: macOS `/Library/Application Support/ClaudeCode/managed-settings.json`, Linux/WSL `/etc/claude-code/managed-settings.json`, Windows `C:\Program Files\ClaudeCode\managed-settings.json`, plus MDM plist/registry, a managed-settings.d drop-in dir, and server-managed settings delivered at sign-in from the claude.ai admin console; managed scope is top precedence and non-overridable.
- [official: code.claude.com/docs/en/plugin-marketplaces + settings] Org enforcement: `strictKnownMarketplaces` (managed-only allowlist; `[]` = lockdown; supports hostPattern/pathPattern regex), `blockedMarketplaces` denylist, managed-scope `enabledPlugins` (read-only 'managed' plugins), `pluginSuggestionMarketplaces`, `disableSideloadFlags`; MCP org controls: `managed-mcp.json`, `allowedMcpServers`/`deniedMcpServers`/`allowManagedMcpServersOnly`; project MCP via committed `.mcp.json`.
- [official: code.claude.com/docs/en/skills] Documented skill-sharing scopes: 'Project skills: Commit .claude/skills/ to version control; Plugins: Create a skills/ directory in your plugin; Managed: Deploy organization-wide through managed settings'.
- [official: code.claude.com/docs/en/memory] 'Claude Code reads CLAUDE.md, not AGENTS.md'; the documented bridge is a CLAUDE.md containing `@AGENTS.md` import (optionally plus Claude-specific sections) or `ln -s AGENTS.md CLAUDE.md`; `/init` incorporates an existing AGENTS.md.
- [official: developers.openai.com/codex/skills] Codex skills build on the agentskills.io open standard; SKILL.md requires `name` and `description`; Codex scans `.agents/skills` from cwd up to repo root, `$HOME/.agents/skills`, `/etc/codex/skills`, and bundled skills; optional `agents/openai.yaml` adds interface/policy/dependencies metadata; skills list capped at ~2% of context (8,000 chars fallback); explicit invocation via `/skills` or `$skillname`.
- [official: developers.openai.com/codex/guides/agents-md] Codex reads AGENTS.override.md, then AGENTS.md, then project_doc_fallback_filenames, walking from project root down to cwd, before doing any work.
- [inference] To serve one repo to both tools: keep AGENTS.md canonical with CLAUDE.md = `@AGENTS.md`; author shared skills to the portable agentskills.io field subset and mirror one skill tree into both `.claude/skills/` and `.agents/skills/` (symlinks documented as followed by Claude Code; Codex symlink handling is not documented); Claude-only features ($ARGUMENTS, !`cmd` injection, context: fork, hooks) should be avoided in shared skills; plugins/marketplaces are Claude-Code-only distribution.
- [inference, resolving a fetch conflict] A secondary summary of the settings page labeled extraKnownMarketplaces/enabledPlugins as 'managed only', but the primary marketplace and plugins-reference pages explicitly document both keys in project/user/local settings (install scopes write enabledPlugins to `~/.claude/settings.json`, `.claude/settings.json`, `.claude/settings.local.json`); only strictKnownMarketplaces/blockedMarketplaces/pluginSuggestionMarketplaces are managed-settings-only.
- [official: code.claude.com/docs/en/plugins] Community distribution: `claude-plugins-official` (curated by Anthropic, auto-registered) and `claude-community` (anthropics/claude-plugins-community; submissions via claude.ai admin form requiring Team/Enterprise org, or platform.claude.com/plugins/submit; approved plugins pinned to commit SHAs with CI-bumped pins); `claude plugin validate` should be run before submission.
- [official: code.claude.com/docs/en/plugin-marketplaces] Container/CI distribution: `CLAUDE_CODE_PLUGIN_SEED_DIR` points at a read-only pre-populated mirror of `~/.claude/plugins` (build with `CLAUDE_CODE_PLUGIN_CACHE_DIR`); seed entries take precedence and auto-updates are disabled for seed marketplaces.

</details>

## 3. 三个候选方案与评分

### Plugin-First (tc plugin in private marketplace + Codex mirror) — 6.5/10

Discovery: excellent (9/10) — description rewrites plus native plugin listing, tc:* namespacing kills the /review collision. Install/update: 7/10 — one-time install is clean, but private-marketplace auto-update requires every member to toggle autoUpdate AND keep a GH_TOKEN in env; without both, updates are silently manual, recreating the staleness problem it claims to solve. Maintenance: 6/10 — it does NOT eliminate dual channels: Codex still needs git symlinks into ~/.agents/skills, the multica registry must still be maintained for autopilot per-task injection, and a version-bump-discipline CI gate is added on top. Three distribution mechanisms persist (plugin cache, Codex symlinks, registry). Robustness: 7/10 — plugin cache is a physical copy (offline-safe), but ${userConfig.*} header interpolation into MCP config is version-uncertain (the design itself admits a fallback env var, i.e., the manual step the plugin was meant to remove), and the migration-window double-triggering risk (legacy symlinks vs plugin) is real. Fit with multica control plane: 5/10 — it routes the team's primary artifact around the control plane they already operate (registry, per-task injection, fleet heartbeat, TEA-113 nudge), parks the partially-built signed-bundle/daemon work, and spreads GitHub PATs onto every laptop. Best-in-class ideas worth grafting: the CI lint spec (grep bans, description-quality checks, version gate), the ≤450-char description cap, single-sourcing contracts under tc-render, and the explicit escalation path if description-driven routing still fails. Over-engineered for 5 people relative to what it buys over the registry the team already runs.

### Multica-Registry-First (registry = distribution plane, git = authoring plane) — 8/10

Discovery: 9/10 — same description-rewrite core, plus `multica skill pull --all --dir ~/.agents/skills` gives Codex native description-driven triggering and deletes the absolute-path skills-index hack. Install/update: 8/10 — clone-less onboarding (multica login + one pull), hourly cron makes updates near-zero-touch; the only friction is that rollout is gated on tc-multica CLI fixes (lossy pull, non-atomic writes, 480-char truncation) — all verified live defects that would corrupt migrated skills if pushed today. Maintenance: 7/10 — mostly reuses infra the team operates (verified: skill/skill_file tables, owner/review columns, touch-reviewed, --stale, per-task injection, skillSyncLoop all exist in tc-multica); costs are the permanent git↔registry parity discipline and a dev-symlink mode to keep supporting. The build-skills.sh generated-fragment-injection is its one over-engineered piece — Design 3's move-shared-docs-into-tc-render/references is simpler and equally correct since every consumer already hard-depends on tc-render. Robustness: 7.5/10 — physical copies work fully offline; partial-push corruption and single-CI-token fleet poisoning are real but mitigable (verify-after-write hash, least-privilege token); registry outage only freezes updates, not usage. Fit with multica: 9/10 — this is the only design under which daemon-run agents, member machines, and governance (owner_user_id, last_reviewed_at, fleet staleness via doctor/heartbeat) all converge on one object, and it aligns with the team's own 2026-06-09 Phase-1 decision rather than abandoning it. Winner on architecture; needs Design 3's sequencing to de-risk week 1.

### Minimal-Change / Discovery-First (content surgery + routing layer, keep pipes) — 7.5/10

Discovery: 8.5/10 — correctly identifies that the description surface is the load-bearing failure and fixes all 15, plus the 3-line ~/.agents/skills symlink patch that gives Codex native triggering; the canned-utterance trigger-eval CI script is the best cheap regression net of the three designs. Install/update: 6/10 — honestly does not solve distribution staleness: updates remain git pull + re-sync with no signal to stale members, which is the documented failure mode; acceptable at 5 people only as an interim state. Maintenance: 8/10 — smallest diff, 2-4 focused days, no new systems; keeps a temporary two-linter inconsistency (multica skill lint still WARNs on removed frontmatter fields) and keeps the registry push script alive. Robustness: 6.5/10 — symlinks work offline, and removing owner/last_reviewed_at from frontmatter neutralizes the lossy-pull bug as a side effect; but the documented three-truths shadowing problem (stale physical dirs silently shadowing fresh symlinks, sync-to-local.sh only WARNs) is explicitly left unsolved. Fit with multica: 7.5/10 — nothing conflicts with the registry or the signed-bundle end-state; it simply defers the distribution question. Its real value: the content plan is a near-strict subset of Design 2's, has zero external dependencies, and can land in week 1 over existing pipes — making it the correct FIRST WEEK of the winning plan rather than a competing end-state. Its own honest scope-limit framing (escalate to packaging only if content fixes don't move triggering) is the right decision discipline.

<details><summary><b>三个方案完整设计文档</b></summary>

### Plugin-First: ship the 15 tc-* skills as one official Claude Code plugin ("tc") in a private marketplace, with a Codex mirror via ~/.agents/skills and a demoted multica registry kept only for autopilot task-injection

**架构**

#### 1. Target repo layout (team-context stays the single source of truth; the repo becomes its own marketplace)

```
team-context/                              # private GitHub repo feibo-ai/team-context
├── .claude-plugin/
│   └── marketplace.json                   # marketplace catalog "aimiq"
├── plugins/
│   └── tc/                                # THE team plugin — the only distributable unit
│       ├── .claude-plugin/plugin.json     # name "tc", semver version, userConfig, pointers
│       ├── .mcp.json                      # tcmcp-remote HTTP MCP server config
│       ├── hooks/hooks.json               # SessionStart hook → injects rules/team-rules.md
│       ├── rules/team-rules.md            # slimmed claude_md_team_global.md (≤3k tokens, CI-capped)
│       ├── bin/                           # on Bash PATH while plugin enabled (Claude Code)
│       │   ├── tc-publish                 # → exec python3 <plugin>/skills/tc-render/scripts/publish.py
│       │   └── tc-transition              # → exec python3 <plugin>/skills/tc-render/scripts/transition.py
│       ├── CHANGELOG.md
│       └── skills/
│           ├── tc-1-start/SKILL.md        # names UNCHANGED (dir == frontmatter name, spec rule);
│           ├── tc-2-research/SKILL.md     #   invocation becomes /tc:tc-2-research; auto-trigger via description
│           ├── tc-3-plan/
│           │   ├── SKILL.md
│           │   └── references/templates.md          # extracted project+task plan templates
│           ├── tc-4-build/
│           │   ├── SKILL.md
│           │   └── references/kickoff-card.md       # Feishu 开工卡 skeleton (from standards/feishu-card-style.md §2/§3)
│           ├── tc-5-review/
│           │   ├── SKILL.md
│           │   └── references/case-template.md      # 5-section template + fields.json schema pointer
│           ├── tc-conflict/references/decision-template.md
│           ├── tc-design-review/references/reviewer-prompt.md
│           ├── tc-friday/  tc-monday/  tc-roles/  tc-self-check/  tc-health-check/  tc-ops/
│           ├── tc-handoff/references/handoff-template.md
│           └── tc-render/                 # the LIBRARY skill — single source for all shared assets
│               ├── SKILL.md
│               ├── scripts/publish.py  scripts/transition.py
│               ├── references/PUBLISH.md
│               ├── references/publish-contract-v1.yaml
│               ├── references/labels.md               # moved from standards/ (invariant table single source)
│               ├── references/multica-fields.md       # moved from standards/
│               ├── references/feishu-card-style.md    # moved from standards/
│               └── assets/style.css
├── tests/                                 # tc-render tests MOVED OUT of the skill dir (they cross skill
│   └── render/…                           #   boundaries and reach into tc-multica; run in CI, never shipped)
├── sop/  cases/  decisions/  autopilots/  docs/   # unchanged, NOT part of the plugin
├── standards/                             # shrinks to repo-governance docs only (integration-overview etc.)
└── scripts/
    ├── install.sh                         # replaces sync-team-config.sh member path (Claude + Codex, see below)
    └── push-registry.sh                   # CI-only: repo → multica registry (autopilot injection channel)
```

##### Exact manifests

`.claude-plugin/marketplace.json`:
```json
{
  "name": "aimiq",
  "owner": { "name": "AI MIQ", "email": "wydraleandro@gmail.com" },
  "plugins": [
    {
      "name": "tc",
      "source": "./plugins/tc",
      "description": "AI MIQ team workflow: RPI skills, rituals, multica + Feishu integration",
      "category": "workflow",
      "strict": true
    }
  ]
}
```

`plugins/tc/.claude-plugin/plugin.json`:
```json
{
  "name": "tc",
  "displayName": "AI MIQ Team Context",
  "version": "1.0.0",
  "description": "Team RPI workflow skills (research/plan/build/review), rituals, and ops",
  "author": { "name": "AI MIQ" },
  "mcpServers": "./.mcp.json",
  "hooks": "./hooks/hooks.json",
  "userConfig": {
    "multicaToken": {
      "type": "string",
      "sensitive": true,
      "description": "multica token — run `multica login`, copy token from ~/.multica/config.json"
    }
  }
}
```
`version` is deliberately SET (not omitted): updates ship only on an explicit bump — release discipline replaces the skills-v* signed-bundle flow for humans.

`plugins/tc/.mcp.json` (per-user token via userConfig; if the installed Claude Code version doesn't interpolate userConfig into headers, fall back to `"Authorization": "Bearer ${TCMCP_AGENT_TOKEN}"` and have install.sh export it in shell rc — verify on v2.1.19x during step 9 of migration):
```json
{
  "mcpServers": {
    "tcmcp-remote": {
      "type": "http",
      "url": "https://mcp.teamctx.actionow.ai/mcp",
      "headers": { "Authorization": "Bearer ${userConfig.multicaToken}" }
    }
  }
}
```

`plugins/tc/hooks/hooks.json` — plugin-native replacement for the ~/.claude/CLAUDE.md symlink:
```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "cat \"${CLAUDE_PLUGIN_ROOT}/rules/team-rules.md\"" } ] }
    ]
  }
}
```

`plugins/tc/bin/tc-publish` (kills every `~/.claude/skills/tc-render/publish.py` and `tc-render/publish.py` literal in skill bodies):
```bash
#!/usr/bin/env bash
exec python3 "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/skills/tc-render/scripts/publish.py" "$@"
```

##### Exact frontmatter template (all 15 skills)
```yaml
---
name: tc-3-plan
description: "Generates the Plan document for the team's Plan phase (after Research, before Build) — goal, completion criteria, who does what, appetite — then routes it through a mandatory second-session review before any coding. Use when the user says 写计划 / 做个 plan / 制定计划 / 规划一下 / 'write a plan' / 'let's plan' / 'Plan session', or when research is complete and planning should begin. Project layer gets a full plan doc; task layer a 3-sentence mini-plan."
metadata:
  owner: "曾振华"
  last-reviewed: "2026-07-03"
---
```
Rules: third person, WHAT first, bilingual triggers front-loaded, ≤450 chars (safe under the 1,536-char listing truncation and the registry's 480-char slice), zero SOP-version pins, zero script/tool/path names, cross-skill mentions by skill name only. `owner`/`last_reviewed_at` move under the spec-legal `metadata:` map (top-level extras banned by CI); monthly_health.py and `multica skill lint` expectations updated in lockstep. No Claude-only frontmatter (`context: fork`, `hooks`, `paths`, `!`cmd``, `$ARGUMENTS`) in shared skills — they must stay inert-safe for Codex.

#### 2. Distribution flow

**Claude Code (all 5 members):**
```
claude plugin marketplace add feibo-ai/team-context     # private repo — git credential helper handles auth
claude plugin install tc@aimiq
```
Plus zero-friction default committed to every product repo's `.claude/settings.json`:
```json
{
  "extraKnownMarketplaces": { "aimiq": { "source": { "source": "github", "repo": "feibo-ai/team-context" } } },
  "enabledPlugins": { "tc@aimiq": true }
}
```
Trusting the folder prompts install automatically. The plugin is copied into `~/.claude/plugins/cache` (versioned, GC'd) — this structurally eliminates the "three truths / symlink shadowing" problem: no more ~/.claude/skills/tc-* symlinks at all.

**Update flow (Claude):** DRI bumps `version` in plugin.json + tags `tc-vX.Y.Z` → members' `claude plugin update tc` or startup auto-update. Auto-update is OFF by default for third-party marketplaces: each member toggles it once in `/plugin → Marketplaces → aimiq → autoUpdate`, and exports `GH_TOKEN` (fine-grained PAT, repo read) so background updates of the private repo work. For a 5-person team this one-time toggle replaces the entire mini-ADR-v4 daemon/sigstore machinery on Claude machines.

**Codex CLI/app:** Codex natively scans `$HOME/.agents/skills` (agentskills.io standard — same SKILL.md). `scripts/install.sh` on a Codex machine does:
```bash
git -C "$REPO" pull
mkdir -p ~/.agents/skills ~/.local/bin
for d in "$REPO"/plugins/tc/skills/*/; do ln -sfn "$d" ~/.agents/skills/"$(basename "$d")"; done
ln -sfn "$REPO"/plugins/tc/rules/team-rules.md ~/.codex/AGENTS.md          # rules channel for Codex
ln -sfn "$REPO"/plugins/tc/bin/tc-publish "$REPO"/plugins/tc/bin/tc-transition ~/.local/bin/
codex mcp add-http tcmcp-remote https://mcp.teamctx.actionow.ai/mcp --header "Authorization: Bearer $TCMCP_AGENT_TOKEN"
rm -f ~/.codex/skills-index.md                                              # retire the generated index hack
```
Codex updates = `git pull` (symlinks stay live); optionally wired to the existing daily autopilot. If Codex's symlink-following proves unreliable (undocumented), install.sh switches `ln -sfn` to `rsync -a --delete`. Per-repo `AGENTS.md` in product repos gets a one-line `CLAUDE.md` bridge (`@AGENTS.md`) where needed. install.sh also DELETES legacy `~/.claude/skills/tc-*` symlinks and warns if `MULTICA_DAEMON_SKILL_WRITE=1` (the daemon skill-write loop must stay off on plugin machines).

#### 3. claude_md_team_global.md
Slimmed and moved to `plugins/tc/rules/team-rules.md`; the 12-row skill-dispatch table shrinks to 3 lines ("workflow skills are installed as tc:* — trust their descriptions; when stuck →tc-handoff; every project ends with tc-5-review") because rewritten descriptions now carry discovery. Keeps: 6 core rules, language rule, 「Claude 不能再犯的错」red-line list (still appended via tc-5-review promotion, now editing the plugin file → version bump → distributed). Delivery: SessionStart hook (Claude) + `~/.codex/AGENTS.md` symlink (Codex). The 3k-token CI cap is retargeted at this file. tc-5-review's "append to claude_md_team_global.md" instruction becomes "append to rules/team-rules.md in the team-context repo (ask for the repo path if not in it)".

#### 4. Cross-skill assets & bundling strategy
One plugin = one atomic unit; nothing is ever copied standalone, so cross-skill references inside the plugin are legal — but they still go through two sanctioned indirections only: (a) executables via `tc-publish`/`tc-transition` on PATH (never a filesystem path in prose); (b) shared reference docs live once in `tc-render/references/` and consumer skills cite them as "see tc-render's references/multica-fields.md" — an agent resolves this via the Skill tool or `${CLAUDE_PLUGIN_ROOT}/skills/tc-render/references/…` (Claude) / `~/.agents/skills/tc-render/references/…` (Codex, stated once in team-rules.md, not per skill). Contracts (fields.json schemas, exit codes, label state machine) exist in exactly one place — PUBLISH.md/publish-contract-v1.yaml/labels.md under tc-render — consumer skills carry a ≤3-line summary plus the one recovery rule (exit 2 = comment posted, never re-run publish).

#### 5. Division of labor
- **SKILL.md bodies (≤1500 chars, CI-enforced with corrected CJK counting)**: WHEN + decision gates + ordered imperative steps + anti-patterns. No contracts, no history, no flag walkthroughs.
- **multica CLI**: the entire data plane — `project list/create --full-id --dri --lead --start-date --due-date --priority`, `issue create --project <UUID> --assignee`, labels, comments, `auth status`+`user list` (replaces $ME_NAME env assumption: skills say "resolve current user via `multica auth status`"), `multica update` self-update, and `skill lint` in CI. Phase-2 option (per the 2026-06-09 decision): promote publish/transition into `multica publish`/`multica transition` subcommands, at which point bin/ wrappers become shims.
- **Plugin scripts (tc-render)**: rendering, hard validation, atomic label/status transitions — invoked only as `tc-publish` / `tc-transition`.
- **Remote MCP (tcmcp-remote)**: ONLY server-secret/identity operations — notify_team, dm_member, betting_table_capture, burnout_check_distribute, archive_to_wiki (with its server-side file-path bug fixed to accept content inline), search_chat/read_member_dm. Delete `plan_request_review` (deprecated double-writer vs tc-transition), delete `should_i_use_ai` and `code_review_request` (fold into tc-self-check / review-subagent prose). MCP config ships inside the plugin; no manual JSON edits for Claude users.
- **multica skill registry**: demoted to one job — per-task injection into headless autopilot/daemon agents (the daemon writes agent-bound skills into task workdirs; plugins can't reach those). CI keeps a `push-registry.sh` (create-or-update + files upsert) run on tag; registry stays a derived read-only projection; `multica skill pull` is no longer a human channel; the skills-v* signed-bundle daemon path is parked (optional future Codex-fleet channel).

#### 6. Versioning & CI
- Semver in plugin.json; git tag `tc-vX.Y.Z`; CHANGELOG.md; CI gate fails PRs touching `plugins/tc/**` without a version bump.
- lint.yml jobs: ① `claude plugin validate .` ② `skills-ref validate plugins/tc/skills/*` ③ team lint (python): body ≤1500 unicode chars via `len(body)` (fixes the `words*1.3` CJK undercount), description ≤450 chars + must contain ≥3 CJK and ≥3 English trigger phrases + third-person opener heuristic, `name` == dirname, only spec-legal top-level frontmatter keys ④ grep bans: `~/.claude/skills/`, `standards/`, `sop/`, `SOP v0\.`, `docs/plans/` without anchor phrase, retired tool names (`session_handoff|plan_create|case_create|project_kickoff|doc_publish|plan_upgrade MCP`), `/Users/`, direct `publish.py|transition.py` invocations (must use tc-publish/tc-transition) ⑤ cross-skill name refs must match an existing skill dir ⑥ rules/team-rules.md ≤3k tokens ⑦ check-registry-sync on tags ⑧ existing render test suite from `tests/`.

**迁移步骤**
- 1. Freeze skill edits; branch `plugin-migration` in team-context. Scaffold `plugins/tc/{.claude-plugin,skills,bin,rules,hooks}` and `git mv skills/* plugins/tc/skills/` (names unchanged — no retraining, global-rules refs stay valid; only invocation gains the tc: namespace).
- 2. Move `standards/{labels.md,multica-fields.md,feishu-card-style.md}` → `plugins/tc/skills/tc-render/references/`; move tc-render `PUBLISH.md`/`publish-contract-v1.yaml` into `references/`, scripts into `scripts/`; relocate `skills/tc-render/tests/` → repo-root `tests/render/` (they cross skill and repo boundaries and must not ship).
- 3. Add `bin/tc-publish` and `bin/tc-transition` wrappers; sweep every skill body replacing `python3 ~/.claude/skills/tc-render/publish.py|transition.py` and relative `tc-render/publish.py` forms with `tc-publish …` / `tc-transition …`.
- 4. Rewrite all 15 descriptions using the audit's suggested_description set (third person, front-loaded bilingual triggers, ≤450 chars, no SOP pins/paths/tool names); move `owner`/`last_reviewed_at` under `metadata:`; update `skills/tc-ops/monthly_health.py` regexes and note the `multica skill lint` warning change.
- 5. Body diet pass: extract templates/card skeletons/reviewer prompts into per-skill `references/*.md`; delete all migration narration (不再走 X MCP, TEA-95/70, 命门 lore → decisions/); fix known drift (tc-render: 9 transition subcommands incl. design-request-review/design-approve; tc-ops: 8 invariants + 3 warnings, '这俩'→'这三个'; tc-5-review: add 复盘 trigger); enforce ≤1500 chars.
- 6. Author manifests: `.claude-plugin/marketplace.json` (aimiq), `plugins/tc/.claude-plugin/plugin.json` (version 1.0.0, userConfig.multicaToken sensitive), `plugins/tc/.mcp.json` (tcmcp-remote HTTP), `plugins/tc/hooks/hooks.json` (SessionStart cat rules).
- 7. Slim `claude_md_team_global.md` → `plugins/tc/rules/team-rules.md` (drop the 12-row dispatch table, keep 6 rules + red lines); leave a stub at the old path pointing to the new location until step 12 completes.
- 8. Rewrite `.github/workflows/lint.yml`: `claude plugin validate .`, `skills-ref validate`, CJK-correct char lint, grep bans, description-quality checks, version-bump gate, 3k-token rules cap; keep check-registry-sync on tag pushes.
- 9. Local verification: `claude plugin validate .` then `claude --plugin-dir ./plugins/tc` smoke session — confirm all 15 skills list, MCP connects with userConfig token (if `${userConfig.*}` header interpolation fails on the current CLI version, switch .mcp.json to `${TCMCP_AGENT_TOKEN}` and add the export to install.sh), SessionStart hook injects rules, `tc-publish --dry-run` works from a scratch repo; run `tests/render/`.
- 10. Write `scripts/install.sh` (two modes): Claude — `claude plugin marketplace add feibo-ai/team-context && claude plugin install tc@aimiq`, remove legacy `~/.claude/skills/tc-*` symlinks and `~/.claude/CLAUDE.md` symlink, remind to toggle marketplace autoUpdate + export GH_TOKEN; Codex — symlink (or rsync) plugin skills into `~/.agents/skills/`, symlink rules → `~/.codex/AGENTS.md`, link bin wrappers into `~/.local/bin`, `codex mcp add-http`, delete `~/.codex/skills-index.md`. Deprecate sync-to-local.sh / sync-to-multica.sh; reduce sync-team-config.sh to CI-only `push-registry.sh`.
- 11. Merge, tag `tc-v1.0.0`; CI pushes skills to the multica registry (autopilot-injection channel only, declared derived read-only) — verify autopilot agents still get injected skills on next task claim.
- 12. Commit `extraKnownMarketplaces` + `enabledPlugins: {"tc@aimiq": true}` to every product repo's `.claude/settings.json`; rollout day: all 5 members run install.sh, verify via `/doctor`, `/plugin`, and a `/tc:tc-self-check` dry run; confirm `MULTICA_DAEMON_SKILL_WRITE` is off everywhere.
- 13. Post-migration cleanup (2nd week): delete the old repo-root `skills/` stub and skills-index generator; park skill-bundle-release.yml (keep for a possible Codex-fleet signed channel); file the Phase-2 issue for promoting publish/transition into multica CLI subcommands; add a monthly `claude plugin update tc` reminder to the monday autopilot until autoUpdate adoption is confirmed.

**skill 优化**
- Adopt all 15 audited suggested_descriptions verbatim as the starting point: third-person WHAT-first, bilingual trigger phrases front-loaded (add the missing ones — 复盘 to tc-5-review, 开工/开始写代码/实现 to tc-4-build, 写个方案/制定计划 to tc-3-plan, issue 巡检/label 漂移 to tc-ops), and strip every SOP-version pin, output path, exit code, script name, and 命门/RPI-internal codeword from the discovery surface.
- Cap descriptions at 450 chars so they survive both Claude's 1,536-char listing truncation and the registry's 480-char slice without mid-sentence cuts; CI-enforce.
- Move `owner`/`last_reviewed_at` to a spec-legal `metadata:` map in every skill; update monthly_health.py + registry push script in the same PR so the team's own lint doesn't self-break (the documented `multica skill pull` lossiness becomes irrelevant for humans since pull is no longer a human channel).
- Replace every filesystem coupling with the two sanctioned indirections: executables via plugin-PATH wrappers `tc-publish`/`tc-transition` (works identically in repo checkout, plugin cache, and Codex ~/.agents symlink), and shared docs via tc-render/references/ cited by skill name — zero `~/.claude/skills/…`, zero repo-relative `standards/…` after migration (CI grep-banned).
- Single-source all contracts in tc-render: consumer skills (tc-2/3/5, tc-handoff) drop their inlined publish runbooks and fields.json schemas, keeping only a 3-line invocation summary + the exit-2 recovery rule; this alone brings tc-2-research and tc-handoff under the 1500-char budget and eliminates the already-observed drift (7-vs-9 subcommand count, 6-vs-8 invariants).
- Progressive disclosure for every over-budget skill: tc-3-plan → references/templates.md; tc-4-build → references/kickoff-card.md; tc-5-review → references/case-template.md; tc-conflict → references/decision-template.md; tc-design-review → references/reviewer-prompt.md (also gives the reviewer subagent a reusable prompt file); tc-handoff → references/handoff-template.md; tc-1-start → references/kickoff-card.md + CLI-flag notes.
- Delete all historical/changelog narration from bodies (不再走 plan_create/case_create/session_handoff/project_kickoff MCP, TEA-95/70 incident lore, 旧实测 notes, version-fragile 'unknown flag→multica update' hints) — provenance lives in decisions/; this is ~30-40% of the over-budget mass in tc-1-start/tc-2-research/tc-5-review/tc-handoff.
- Anchor every output path: 'docs/research/…' and 'docs/plans/…' become 'in the current project repo's docs/ tree (create if missing)'; tc-conflict/tc-roles 'decisions/' becomes 'the team-context repo's decisions/ dir — ask for its path if not already there'; replace `$ME_NAME`/`$ME_UID` env assumptions with 'resolve the current user once via `multica auth status` + `multica user list`'.
- Inline the minimum SOP payload instead of citing it: where a skill needs a rule (tc-health-check's 4 signals already do this correctly), copy the 1-3 line rule and drop the 'SOP v0.4 P-x' citation; where it doesn't, delete the citation outright — CI grep-bans `SOP v0\.`.
- Fix agent-vs-human register in tc-4-build and tc-monday: rewrite human-operator SOP lines ('read the CoT, hit ESC') as agent-executable checks or move them to rules/team-rules.md; give tc-monday actual agent steps (verify roundup posted, produce walkthrough order, time-box) instead of a meeting description.
- Align tc-health-check's aggregation wording with its verdict enum (continue | mention | tc-handoff-now) and retitle the H1 to match the skill name; keep its fully-inlined signal rubric as the model for all future skills.
- Standardize body style across the set: imperative, one command per line, consistent single language per section (CN operational, EN headers ok), no emoji bullets, explicit prerequisite line at top of every CLI-touching skill ('needs: multica CLI ≥v0.4.11 on PATH, logged in — else run `multica update` / `multica login`'), explicit fallback ('if tc-publish not found: plugin not enabled — run /plugin').
- Rules-file synergy: with descriptions carrying discovery, shrink team-rules.md's dispatch table to 3 lines and spend the reclaimed token budget on the red-line list, keeping the always-loaded layer well under the 3k cap.

**优点**
- Official, zero-custom-infra install/update: `claude plugin marketplace add` + project-settings `enabledPlugins` gives every teammate a trust-prompt install, and a version bump propagates via built-in auto-update — replaces the unbuilt mini-ADR-v4 sigstore daemon for all Claude machines.
- Structurally kills the 'three truths' problem: plugins live in a versioned cache, legacy ~/.claude/skills symlinks are removed, and physical-copy shadowing / lossy `multica skill pull` frontmatter drops disappear from the human path.
- One atomic unit: skills, shared scripts, standards references, MCP config, rules injection, and bin wrappers travel together — every cross-skill/standards coupling flagged in the 15 audits becomes an intra-plugin reference that cannot break.
- MCP token onboarding drops from manual JSON edits per UI to a single userConfig prompt at plugin-enable time (sensitive value in keychain).
- bin/-on-PATH wrappers (tc-publish/tc-transition) eliminate every hardcoded path in skill prose and work unchanged in repo checkout, plugin cache, and Codex symlink layouts.
- Plugin namespacing (tc:*) prevents collisions with bundled skills (tc-5-review vs /review) and personal skills, and plugin skills are exempt from accidental skillOverrides.
- Versioned releases (plugin.json semver + tags + CHANGELOG + CI bump-gate) finally give distribution-staleness a signal — today staleness is only review-based.
- The rewrite is forced through the audit fixes anyway; packaging and content optimization land as one migration with CI lint locking the new invariants (char budget with correct CJK counting, grep bans, description quality).

**缺点**
- Plugins/marketplaces are Claude-Code-only: Codex needs a parallel channel (git symlinks into ~/.agents/skills + AGENTS.md symlink + manual PATH/MCP setup), so two distribution mechanisms persist — though the Codex side is now native skills instead of the skills-index.md prose hack.
- Private-repo auto-update requires each member to (a) toggle autoUpdate on for the aimiq marketplace (off by default for third-party) and (b) keep a GH_TOKEN in their environment; without both, updates are manual `claude plugin update tc` — for 5 people this is acceptable but it is real friction the old always-live symlinks didn't have.
- Plugin cache path changes on every update, so any residual hardcoded path breaks — the bin/-wrapper migration must be 100% complete before cutover (CI grep ban is mandatory, not optional).
- SessionStart-hook rules injection executes shell and would be disabled by an org setting `disableSkillShellExecution`-style lockdowns or fail silently if hooks misconfigure — the ~/.codex/AGENTS.md symlink remains a second rules channel to keep in sync.
- The multica skill registry doesn't fully die (autopilot per-task injection still needs it), so a derived-projection sync and its CI reconciliation must be maintained — a smaller but nonzero residual dual-source.
- `${userConfig.*}` interpolation into MCP headers is a newer plugin feature; if the team's CLI version doesn't support it, the fallback is an env var (TCMCP_AGENT_TOKEN), which is exactly the manual step the plugin was supposed to remove.
- Invocation names get longer (/tc:tc-3-plan) since dir names keep the tc- prefix for Codex flat-namespace safety; purely cosmetic but visible daily.
- Sunk cost: the signed-bundle release workflow and daemon skillSyncLoop (mini-ADR v4, partially implemented in tc-multica) are parked; if the team later needs fleet-managed Codex machines, that work must be revived and retargeted.

**风险**
- Migration-window double-triggering: if legacy ~/.claude/skills/tc-* symlinks survive alongside the installed plugin, both copies list (different names, tc-1-start vs tc:tc-1-start) and agents may follow the stale one — install.sh must delete legacy links, and /doctor verification is a required rollout step.
- Daemon clobbering: any machine with MULTICA_DAEMON_SKILL_WRITE=1 would write old-format skills back into ~/.claude/skills; SkillWriteGuard only protects symlink layouts, which we're removing — install.sh must assert the flag is off and the team should not enable the skill-write loop on plugin machines.
- Codex symlink handling into ~/.agents/skills is undocumented by OpenAI; if broken, the fallback is rsync copies, which reintroduces manual-staleness on Codex machines (mitigate: wire `git pull && install.sh --codex` into the daily autopilot).
- Registry-projection drift: check-registry-sync.sh only verifies name presence, not content parity, and skips without a token in CI — autopilot agents could run stale skill content for weeks; add a content-hash comparison to push-registry.sh or accept the gap explicitly.
- userConfig→header interpolation, single-root-SKILL.md, and defaultEnabled behaviors vary across recent CLI versions (≥2.1.14x–2.1.19x features); pin a minimum Claude Code version in team-rules.md and test the exact manifest on every member's version before cutover, or the MCP server silently 401s.
- Description-driven discovery is the load-bearing fix: if the rewritten descriptions regress (e.g., someone re-adds SOP jargon), auto-triggering fails again with no dispatch table to fall back on — the CI description-quality lint and a quarterly trigger-phrase smoke test (ask each trigger phrase in a fresh session, expect the right skill) are the guardrails.
- Version-bump discipline is a single-DRI process: forgetting the bump means members silently never update (version pins updates); the CI bump-gate on plugins/tc/** diffs must be blocking, not advisory.
- Deleting the deprecated plan_request_review MCP tool while any autopilot YAML or muscle memory still calls it would break flows at runtime — grep autopilots/ and announce in the Friday demo before removal.
- GH_TOKEN on every laptop for private-marketplace auto-update widens local credential surface (a fine-grained read-only PAT scoped to team-context mitigates); token leakage grants read of the whole team-context repo including cases/decisions.

### Multica-Registry-First: registry as the distribution plane, git as the authoring plane, standard skill dirs on every machine

**架构**

#### Core principle

Split "source of truth" into two planes and make each authoritative for exactly one thing:

- **Authoring/review plane = git** (`/Users/mac/zzh/team-context`). Humans review skill changes as PRs; CI lints; nothing else writes here.
- **Distribution plane = multica skill registry** (Postgres `skill` + `skill_file` tables, already live). CI is the ONLY writer (create-or-update on merge to main). Member machines, daemon task workdirs, and Codex all consume from the registry. `check-registry-sync.sh` is upgraded from name-presence to content-hash parity, so drift between planes is CI-detectable.

This inverts today's stance where the registry is a "derived read-only projection" and dev symlinks are the real channel: dev symlinks become a DRI-only authoring convenience (already made mutually exclusive with daemon writes via `MULTICA_DAEMON_SKILL_WRITE` + `SkillWriteGuard`, skillsync.go:474-478), and the registry becomes what everyone actually runs.

#### Target repo layout (team-context)

```
team-context/
├── claude_md_team_global.md        # L1 rules, trimmed ≤2k tokens (dispatch table removed — see below)
├── sop/group_sop_v0.4.md           # unchanged, authoring-only
├── standards/                      # CANONICAL shared fragments, authoring-only, never referenced by path from skills
│   ├── multica-fields.md
│   ├── labels.md
│   └── feishu-card-style.md
├── skills/                         # authored skills, standard agentskills.io layout
│   ├── tc-render/                  # the ONE skill that owns scripts + contracts
│   │   ├── SKILL.md
│   │   ├── scripts/publish.py
│   │   ├── scripts/transition.py
│   │   ├── references/publish-contract.md      # was PUBLISH.md + publish-contract-v1.yaml
│   │   ├── references/labels.md                # GENERATED from standards/labels.md (header: DO NOT EDIT)
│   │   ├── assets/style.css
│   │   ├── agents/openai.yaml                  # Codex metadata (policy.allow_implicit_invocation: false)
│   │   └── tests/                              # stays in git; excluded from registry push (already is)
│   ├── tc-1-start/
│   │   ├── SKILL.md                            # ≤1500 chars body
│   │   └── references/
│   │       ├── kickoff-steps.md                # extracted flag walkthrough, verification checklist
│   │       ├── feishu-card.md                  # GENERATED §2/§3/§5 excerpt of standards/feishu-card-style.md
│   │       └── multica-fields.md               # GENERATED from standards/
│   ├── tc-2-research/ … tc-self-check/         # same pattern: SKILL.md + references/ (+ scripts/ for tc-ops)
├── dist/skills/                    # build output = exactly what gets pushed (gitignored)
└── scripts/
    ├── build-skills.sh             # inject standards/ fragments into references/, stamp source-commit
    ├── push-skills-to-registry.sh  # replaces sync-to-multica.sh (import route is dead anyway)
    ├── check-registry-parity.sh    # sha256(dist body+files) vs `multica skill get --output json`
    └── sync-team-config.sh         # kept for: global-md symlinks + DRI dev-symlink mode only
```

Every skill dir is a **self-contained standard package** (SKILL.md + references/ + scripts/ + assets/), valid under `skills-ref validate`, portable when copied alone. The 15 skills stay 15 (they have distinct trigger surfaces); "single team package" is realized at the distribution layer: one atomic push, one `multica skill pull --all`, one version counter.

#### Exact frontmatter (spec-clean; governance moves to registry DB columns)

```yaml
---
name: tc-1-start
description: "Guides Phase 01 kickoff of a new project-layer effort (independent direction: 3+ days, has a DRI) through the team's 6 ordered steps: intent broadcast → research → plan → independent review → DRI decision → kickoff broadcast. Use when the user says \"启动新项目\"、\"我想做一个新项目\"、\"新项目立项\"、\"kickoff\"、\"start a new project\"、\"Phase 01\". Not for small task-layer work — route that to tc-3-plan task mode."
license: Proprietary
metadata:
  source-commit: "{{GIT_SHA}}"        # stamped by build-skills.sh
---
```

`owner` and `last_reviewed_at` are DELETED from frontmatter. The registry already has first-class columns (`skill.owner_user_id`, `skill.last_reviewed_at`, migration 110) plus `multica skill touch-reviewed` and `skill list --stale`. Governance queries hit the registry, not YAML. This simultaneously kills the audits' #1 frontmatter finding AND the known lossy-pull bug (pull rebuilding frontmatter dropped exactly these fields — decisions/2026-06-09 line 86): there is nothing left to lose. Ownership in git via `skills/README.md` registry table + CODEOWNERS.

#### Distribution flow (repo → registry → machines)

**Push (CI only, on merge to main):**
```bash
scripts/build-skills.sh                       # standards→references injection, stamp SHA, CJK-aware lint
scripts/push-skills-to-registry.sh            # per skill:
  id=$(multica skill list --output json | jq -r ".[]|select(.name==\"$name\").id")
  multica skill update "$id" \
      --description "$(python3 scripts/frontmatter.py desc "$f")" \
      --content-file "dist/skills/$name/BODY.md" \
      --config "{\"source_commit\":\"$SHA\",\"skills_rev\":$REV}"
  # else: multica skill create --name "$name" ... --owner "$OWNER_UUID"
  for rel in $(files); do multica skill files upsert "$id" --path "$rel" --content-file "dist/skills/$name/$rel"; done
scripts/check-registry-parity.sh || exit 1    # verify-after-write; per-file failures are NO LONGER swallowed
```
`skills_rev` is a monotonic counter (git commit count on skills/**) written into `skill.config` JSONB — this is the versioning mechanism the registry lacks today, with zero schema change.

**Pull (member machines):**
```bash
multica skill pull --all                          # → ~/.claude/skills/<name>/SKILL.md + files[] (standard dirs)
multica skill pull --all --dir ~/.agents/skills   # → Codex native discovery root
```
Claude Code sees plain standard-format skill dirs at `~/.claude/skills/` — physical copies, no symlinks, no plugin machinery, exactly what its Personal-skills scanner expects. Codex sees the SAME standard dirs at `~/.agents/skills` per the agentskills standard it now implements natively — this **deletes the generated `~/.codex/skills-index.md` hack** and its machine-absolute-path fragility. `multica skill pull` gets three small fixes: (a) emit spec-clean frontmatter (name/description/license/metadata incl. source-commit from config JSONB); (b) atomic per-skill write (temp dir + rename) so an interrupted pull never leaves a half skill; (c) `--check` flag comparing local skills_rev vs registry (wired into `multica doctor`).

**Auto-update:** two tiers.
1. Interim (this week): launchd/cron on each machine: `*/60 * * * * multica skill pull --all --quiet && multica skill pull --all --dir ~/.agents/skills --quiet`. Idempotent; offline runs no-op and keep the last-pulled copies.
2. End-state: extend the existing daemon `skillSyncLoop` with `MULTICA_DAEMON_SKILL_SOURCE=registry` (default stays the signed-bundle GitHub path). Registry mode reuses the loop's anti-rollback (persisted skills_rev instead of tag), write-path safety (EvalSymlinks/O_NOFOLLOW), and `SkillWriteGuard` dev-box refusal. TEA-113's deferred "fleet one-click skill update" becomes: DRI nudge → daemons pull immediately.
3. Daemon-run agents need nothing: per-task injection (`writeSkillFiles` → task-workdir `.claude/skills/{name}`) already hydrates registry-bound skills at claim time — with the registry as the real distribution plane this path is always current by construction.

**Offline behavior:** skills are physical files; discovery + instructions work fully offline. What needs network offline-degrades explicitly: each skill body gains one standard preflight line ("requires `multica` CLI + auth; if `multica auth status` fails, stop and tell the user") and tc-render's scripts already fail loudly. Staleness while offline is bounded by the cron interval and surfaced by `multica doctor` (local rev vs registry rev) once back online; daemon heartbeat additionally reports installed skills_rev so the DRI can see fleet staleness in the multica UI — a capability the git-symlink model never had.

#### Comparison with today's git-pull+symlink

Symlink model: freshness requires every member to `git pull` (nothing nudges them); new skills need re-running the sync script; the "three truths" shadowing problem (repo vs physical ~/.claude/skills vs registry) is documented as a live failure; Codex needed a generated index with absolute paths; daemon task workdirs and clone-less machines are unserved. Registry model: one artifact plane the team already operates as its control plane (secrets, integrations, autopilots, config WS-push), clone-less onboarding (`multica login` → `multica skill pull --all` → done), per-task injection for agents, native fleet observability, and governance (owner/touch-reviewed/--stale) attached to the same object being distributed. DRI dev boxes keep git symlinks for edit-test loops; the mutual exclusion is already enforced in code, so the two modes can't fight over `~/.claude/skills`.

#### Global rules file (claude_md_team_global.md)

Stays in git; NOT moved into the registry (the registry stores skills; CLAUDE.md/AGENTS.md must exist as real files at fixed paths, and a plugin/skill cannot ship always-loaded context per the official docs). Distribution unchanged short-term: `sync-team-config.sh` symlinks it to `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`; end-state it rides the already-designed signed skills-v* bundle (it's already in the archive) via the daemon. Content changes: (1) DELETE the 12-row skill-dispatch table — with rewritten descriptions, native description-matching does this job in both Claude Code and Codex, and the table is a second copy that drifts; keep the 6 core rules, `$ME_NAME`/`$ME_UID` resolution rule, and ONE definition that all skills lean on: "**skills root** = `~/.claude/skills` (or the task workdir's `.claude/skills` under multica daemon; `~/.agents/skills` for Codex). Cross-skill scripts are invoked as `python3 <skills-root>/tc-render/scripts/<script>.py`." (2) Add the rule "issue label/status transitions go ONLY through tc-render transition.py — never hand-typed multica label/status commands, never the remote MCP plan_request_review tool."

#### Cross-skill and standards/ references after migration (bundling strategy)

- **Shared standards**: single canonical source in `standards/`; `build-skills.sh` injects the needed sections into each consumer skill's `references/` with a generated-file header. No skill ever references `standards/...` by path again. Drift is impossible (generated), duplication is a distribution artifact not an authoring one.
- **Cross-skill scripts**: only tc-render owns executables. All consumers use the single skills-root phrase defined in the global rules (works under symlink, pull-copy, task-workdir injection, and Codex because pull installs ALL skills together — enforce with a lint rule that any tc-* referencing tc-render scripts is only pushed if tc-render is pushed). CLI enhancement (small, high-value): `multica skill exec tc-render publish -- --type plan ...` resolves the installed skill path itself, making invocations location-independent; bodies can then shorten to one command.
- **SOP citations**: never cite "SOP v0.4 P-x" from a description; in bodies, either inline the 1-2 load-bearing sentences (tc-self-check pattern) or point to a bundled `references/sop-excerpt.md` generated from sop/.
- **Contracts**: fields.json schemas, exit-code semantics, transition subcommand list live ONLY in tc-render's `references/publish-contract.md` + script docstrings; consumer skills say "contract: see tc-render publish-contract" and nothing more.

#### Division of labor (skill text vs multica CLI vs remote MCP)

- **SKILL.md body**: WHEN to act, decision logic, step ordering, anti-patterns, handoffs. ≤1500 chars. Zero contract duplication, zero changelog.
- **multica CLI (direct)**: reads and simple creates an agent does inline — `project list --full-id`, `issue create --project <UUID> --assignee "$ME_NAME"`, `issue comment list`, `auth status`, `user list`, `skill pull`. Anything a human could audit as one command.
- **tc-render scripts (CLI-wrapping)**: everything multi-step or invariant-bearing — HTML render + validation + inline publish (命门B), all 9 state transitions. Scripts are the enforcement layer; skills must not paraphrase their internals.
- **remote MCP (tcmcp-remote)**: ONLY cross-boundary side effects requiring the server-held Feishu secret — notify_team, dm_member, betting_table_capture, archive_to_wiki, search_chat, read_member_dm, burnout_check_distribute. DELETE `plan_request_review` (deprecated double-writer vs transition.py, and it omits status=in_review) and `code_review_request` (no skill caller; code review runs via reviewer subagents). Fold `should_i_use_ai` heuristics into tc-self-check `references/` and retire the tool. Fix `archive_to_wiki` to accept `markdownContent` inline (the server can't read agent-local paths — monthly-health autopilot is currently broken by this).

#### CI lint (single job, replaces/extends .github/workflows/lint.yml)

1. `skills-ref validate dist/skills/<name>` for every skill (spec conformance incl. name↔dir match).
2. Frontmatter whitelist: only name/description/license/metadata; FAIL on owner/last_reviewed_at.
3. Description rules: ≤450 chars (safety margin under the push path's 480 cap until it's raised to 1024); must start with a third-person verb (regex); must contain ≥3 quoted CJK trigger phrases and ≥2 English ones; FAIL on banned tokens: `SOP v`, `命门`, `MCP`, `publish.py`, `transition.py`, `docs/`, `standards/`, `~/.claude`, `不再`, `原 `.
4. Body budget with CJK-aware counting: `cjk_chars + non_cjk_words*1.3 ≤ 2000 tokens` hard cap (fixes monthly_health.py's whitespace-split estimator that silently passes Chinese bodies).
5. Path lint on bodies: FAIL any `standards/`, `sop/`, `~/.claude/skills/` literal, or `docs/plans|research` without the skills-root phrase; FAIL references to files not present in the skill dir.
6. Drift probes: transition.py subcommand list vs any body mentioning counts; issue_invariants.py invariant count vs tc-ops body (or ban counts in bodies outright).
7. Registry parity: `check-registry-parity.sh` (content-hash, not name-presence) — runs post-push in the deploy job with the CI service token, still SKIPs honestly on PR runs without a token.
8. `claude plugin validate` is NOT needed (no plugin packaging); keep the 3k-token cap check on claude_md_team_global.md.

**迁移步骤**
- Fix multica CLI first (tc-multica repo, gates everything): (a) `multica skill pull` emits spec-clean frontmatter (name/description/license/metadata with source-commit read from skill.config JSONB) instead of rebuilding with owner/last_reviewed_at; (b) atomic per-skill write (temp dir + os.rename); (c) add `--content-file` to `skill create/update/files upsert`; (d) raise the push description cap from 480 to the spec's 1024; (e) add `multica skill pull --check` + wire into `multica doctor`.
- Restructure skill dirs in team-context: move publish.py/transition.py under skills/tc-render/scripts/, merge PUBLISH.md + publish-contract-v1.yaml into references/publish-contract.md, create references/ in every over-budget skill and extract templates/checklists/card specs into it (tc-1-start, tc-2-research, tc-3-plan, tc-4-build, tc-5-review, tc-handoff, tc-conflict, tc-design-review, tc-roles, tc-self-check).
- Write scripts/build-skills.sh: inject standards/{multica-fields,labels,feishu-card-style}.md sections into consumer skills' references/ with DO-NOT-EDIT headers, stamp metadata.source-commit and skill.config skills_rev, output to dist/skills/.
- Rewrite all 15 frontmatters: delete owner/last_reviewed_at (record ownership in skills/README.md + CODEOWNERS; backfill registry owner_user_id + touch-reviewed via one-off script), apply the audited suggested_description rewrites (third person, WHAT first, front-loaded bilingual triggers, no SOP codes/paths/tool names/changelog).
- Rewrite bodies to ≤1500 chars: delete all deprecation narration (project_kickoff/plan_create/session_handoff/case_create MCP, TEA-95/70, 不再走…), replace every `~/.claude/skills/tc-render/...` and relative `tc-render/publish.py` call with the single skills-root invocation phrase, replace standards/ and sop/ citations with bundled references or inline excerpts, fix known drift (tc-render 7→9 subcommands: remove the count; tc-ops 6→8 invariants: point at script docstring; tc-self-check P-7 label).
- Update the lint stack in lockstep: rewrite .github/workflows/lint.yml per the 8-point CI spec (skills-ref validate, frontmatter whitelist, description regexes, CJK-aware body cap, path lint, parity hash); fix skills/tc-ops/monthly_health.py to stop requiring owner/last_reviewed_at frontmatter and to use CJK-aware counting; update `multica skill lint` in tc-multica to warn (not require) on the removed fields.
- Replace sync-to-multica.sh with scripts/push-skills-to-registry.sh (create-or-update + files upsert with verify-after-write, no swallowed per-file failures) and add it as a CI deploy job on merge to main using a CI-scoped service token; upgrade check-registry-sync.sh to content-hash parity.
- Trim claude_md_team_global.md: remove the 12-row skill-dispatch table and the '~/.claude/skills/multica-cli' dead pointer; add the skills-root definition and the transitions-only-via-transition.py rule; keep symlink distribution via sync-team-config.sh (drop its Codex skills-index generation, step ⑥ — no longer needed).
- Roll out member machines: everyone runs `multica skill pull --all` and `multica skill pull --all --dir ~/.agents/skills`, deletes any stale physical copies shadowing old symlinks, installs the hourly launchd/cron pull; DRI boxes opt into dev-symlink mode explicitly (sync-team-config.sh) and are excluded from cron by SkillWriteGuard semantics.
- Clean up the remote MCP surface (team-context-mcp): unregister plan_request_review and code_review_request, retire should_i_use_ai (content moves to tc-self-check references/), change archive_to_wiki to accept inline markdown content and fix the monthly-health autopilot yaml accordingly; delete dead MulticaClient.publishDoc/listSkills client surface or mark future-only.
- Verify end-to-end: fresh machine test (multica login → pull → Claude Code /doctor shows all 15 with full descriptions → Codex /skills lists them from ~/.agents/skills → run tc-3-plan happy path incl. transition.py via skills-root phrase → offline test: disconnect, confirm skills still trigger and preflight fails loudly).
- End-state (separate task, after 2-4 weeks of stable pulls): implement MULTICA_DAEMON_SKILL_SOURCE=registry in skillSyncLoop reusing anti-rollback/write-safety/SkillWriteGuard, add daemon heartbeat reporting of installed skills_rev for fleet staleness, and wire the TEA-113 one-click nudge to trigger immediate pulls; keep the signed-bundle path as the hardened alternative if the team ever needs cryptographic provenance for skills.

**skill 优化**
- All 15 descriptions rewritten to one template: [third-person WHAT, 1 sentence] + [WHEN with front-loaded bilingual quoted triggers] + [negative scope/disambiguation vs sibling skills] — using the audit's suggested_description drafts as the starting text; hard-ban SOP version pins, 命门/RPI-unexplained jargon, file paths, MCP/CLI tool names, and migration notes from the description surface.
- Missing-trigger fixes with outsized discovery ROI: add 复盘 to tc-5-review; add 开工/开始写代码/实现 to tc-4-build; add 写计划/制定计划/规划 to tc-3-plan; add issue 巡检/label 漂移/invariants to tc-ops (its description currently omits a third of the skill); add 自检/反模式 to tc-self-check; add 分工/责任人/who does what to tc-roles.
- Progressive disclosure for every over-budget skill: SKILL.md keeps only mandate, entry criteria, ordered imperative steps, anti-patterns, handoff; templates (plan/case/decision/handoff Current-State), Feishu card skeletons, fields.json schemas, review-gate protocols, and verification checklists move to references/*.md loaded on demand — this alone brings tc-1-start (4349), tc-3-plan (5457), tc-5-review (4390), tc-handoff (3915) under the 1500-char cap.
- Single-ownership of contracts: tc-render's references/publish-contract.md + script docstrings become the only place exit codes, fields.json schemas, label/status semantics, and transition subcommands are written; tc-2/3/5/handoff replace their inlined copies with one pointer sentence — eliminating the already-observed drift (7 vs 9 subcommands, 6 vs 8 invariants).
- One canonical cross-skill invocation phrase defined once in claude_md_team_global.md ('python3 <skills-root>/tc-render/scripts/X.py'), used verbatim by all consumer skills — removes the current impossible mix of relative tc-render/publish.py and absolute ~/.claude/skills paths that can never both resolve.
- Bundle-by-generation for shared standards: build-skills.sh injects the exact sections of standards/multica-fields.md, labels.md, feishu-card-style.md each skill needs into its references/, so every skill dir is standalone-portable while standards/ stays single-source in git.
- Delete all historical/changelog content from bodies (project_kickoff, plan_create, session_handoff, case_create MCP references; TEA-95/70 incident lore; 旧实测 notes; version-fragile 'if unknown flag run multica update' lines) — pure token recovery with zero instruction loss.
- Register-consistency fixes: pick one language per section (EN for mandate/steps skeleton, CN for team ritual specifics), one command per line in numbered steps, and replace human-operator instructions in tc-4-build (30s CoT reading, ESC) with an explicit '(operator discipline — for the human)' block or move them to sop/ so agent-facing text stays executable.
- tc-monday/tc-friday made agent-actionable: add concrete agent verbs (verify the autopilot roundup posted via `multica issue list --label 计划-已批准 --updated-after <monday>`; state the exact fallback when the roundup/betting MCP is unavailable) instead of pure human meeting runbooks.
- Codex parity per skill: add optional agents/openai.yaml (interface display + policy.allow_implicit_invocation) and keep shared skills free of Claude-only features ($ARGUMENTS, !`cmd` injection, context: fork, hooks) so one skill tree serves both harnesses unmodified.
- tc-render description rewritten to resolve its self-contradiction: state it is normally invoked by the 4 doc skills AND that direct use is correct for standalone status transitions — plus English trigger verbs (publish, render, status transition) it currently lacks.
- SOP inlining pattern standardized: any SOP rule an agent must enforce at runtime gets its 1-2 sentence excerpt inlined or bundled (tc-self-check already does this correctly); bare 'SOP P-x' / 'rule #6' citations are lint-banned.

**优点**
- Leans on infrastructure the team already operates as its control plane — registry tables, skill pull, files[], owner/review columns, touch-reviewed, --stale, per-task injection all exist and are verified in code; the migration is mostly deletion and small CLI fixes, not new systems.
- Clone-less onboarding and updates: a member machine needs only `multica login` + `multica skill pull --all`; no git clone, no sync script, no knowledge of repo layout — collapses the documented 'three truths' staleness/shadowing problem to one write path per machine class.
- Codex becomes a first-class citizen: pulling the same standard dirs into ~/.agents/skills gives native description-based triggering, deleting the generated skills-index.md with its machine-absolute paths — the single biggest fix for 'agents fail to discover skills' on the Codex side.
- Daemon-run agents are always current by construction: per-task injection hydrates registry skills into the task workdir at claim time, something the git-symlink model never covered.
- Fleet observability the symlink model cannot have: skills_rev in config JSONB + daemon heartbeat + `multica doctor --check` lets the DRI see exactly which machine is stale, and TEA-113's one-click nudge gives push-button fleet refresh.
- Governance attaches to the distributed object: owner_user_id, last_reviewed_at, stale flags live where the skill lives, so removing the non-standard frontmatter fields loses nothing — it fixes spec compliance and the lossy-pull bug in one move.
- Claude Code needs zero configuration changes: pulled skills are plain standard-format personal skills at ~/.claude/skills — no plugins, no marketplaces, no settings.json churn, full offline function once pulled.
- Atomic team-wide releases: one CI push updates 15 skills + bundled files consistently (parity-verified), versus 5 people git-pulling at different times against a moving main.

**缺点**
- Two planes must be reconciled forever: git (review) and registry (distribution) can drift if anyone writes the registry directly via web UI/API or a local `multica skill create`; only CI discipline plus the parity check (which needs a token and is honestly skipped on PR runs) holds the line.
- Hard dependency on multica CLI + auth + server availability for every update path; a registry outage freezes skill updates for the whole team (though installed skills keep working offline), whereas git-pull had no single runtime service in the loop.
- Weaker supply-chain posture than the already-designed signed-bundle path: registry content is protected only by token auth and Postgres integrity — no offline attestation, no anti-tamper on the artifact itself; the sigstore/TUF design is bypassed for the primary channel.
- Blocked on tc-multica CLI work before any rollout: lossy pull frontmatter rebuild, non-atomic writes, swallowed per-file upsert failures, and the 480-char description truncation are all live defects that would corrupt or truncate the migrated skills if pushed today.
- Registry has no native content versioning; the skills_rev-in-config-JSONB scheme is a convention, not a schema guarantee — nothing in the server enforces monotonicity until the daemon registry-source mode implements it client-side.
- Freshness is poll-bounded (hourly cron / 6h daemon interval) rather than instant-after-git-pull for a DRI iterating on a skill — hence keeping the dev-symlink mode, which preserves a second machine-class to support and explain.
- Generated duplication of standards/ fragments across skill dirs increases pushed bytes and makes ad-hoc greps show multiple copies; correctness is preserved by generation, but casual editors may patch a generated references/ file and be silently overwritten.

**风险**
- Partial-push corruption: today `files upsert` failures print ✗ and continue, so a mid-push network blip leaves a skill whose body and bundled scripts disagree (e.g., new SKILL.md calling a transition.py subcommand not yet upserted); mitigation = verify-after-write parity hash in push script and refusing to bump skills_rev until all files verify.
- Single-token fleet poisoning: the CI service token (admin/owner) can rewrite every skill for every machine; compromise = silent fleet-wide prompt injection with no signature to detect it. Mitigate with a dedicated least-privilege token, config.source_commit audit against git, and eventually routing the daemon path through the signed bundle.
- Shadowing during cutover: existing symlinks (dev mode) vs pull copies vs old physical copies can interleave per machine; a missed cleanup leaves a member running pre-migration skill text indefinitely with no error. Mitigate with an explicit one-time cleanup step and `multica doctor` flagging symlink/copy mixtures (SkillWriteGuard logic reused as a check).
- Description-truncation regression: until the CLI's 480-char cap is raised, any rewritten description over 480 chars is silently cut mid-sentence in the registry — destroying exactly the trigger phrases the rewrite added; CI must assert pushed-description == source-description length until the cap fix ships.
- Codex path assumptions: ~/.agents/skills discovery and the ~2%-of-context listing cap are documented but unvalidated for this team's 15 CJK-heavy descriptions; if the listing overflows, Codex silently drops skills. Mitigate by measuring total description bytes in CI (budget ~8000 chars) and testing on one Codex machine before rollout.
- Skills-root phrase is a convention, not a mechanism: an agent in a task workdir or unusual CLAUDE_CONFIG_DIR can still resolve the wrong root for cross-skill scripts; the real fix is `multica skill exec`, which is new CLI work — until it ships, tc-render invocation failures remain possible and must fail loudly (transition.py already does).
- Lint/tooling lockstep hazard: monthly_health.py and `multica skill lint` currently REQUIRE the owner/last_reviewed_at fields the migration deletes; if the field removal lands before the lint updates, the team's own tooling red-flags every skill (the 'self-inflicted lint' failure already observed once with lossy pull) — sequencing in the migration steps is load-bearing.
- Autopilot/remote-MCP coupling breaks if cleanup is skipped: deleting plan_request_review while some flow still calls it, or fixing archive_to_wiki's signature without updating monthly-health.yaml, trades one double-writer bug for a runtime 404; grep all autopilot YAMLs + skills for tool names as a CI gate during the MCP surface cleanup.

### Minimal-Change / Discovery-First: fix skill content + routing layer, keep existing pipes

**架构**

#### Thesis

The distribution plumbing (symlink sync + registry push/pull + Codex index + signed-bundle future) already matches the team's own Phase-1 decision (2026-06-09 redeliberation) and mostly works. What fails is the DISCOVERY SURFACE: at session start an agent sees only name+description for each skill, and today those 15 descriptions are polluted with migration changelogs, SOP version pins, script paths, and internal codenames (命门B, P-7, rule #6), while trigger phrases are buried. Bodies are 2–3.6x over budget and full of repo-relative paths that break post-sync. The fix is content surgery plus a tightened routing layer — no new package format, no marketplace, no daemon.

#### Target repo layout (team-context, diff-minimal)

```
team-context/
├── claude_md_team_global.md            # REWRITTEN routing layer (see below), still symlinked to
│                                       #   ~/.claude/CLAUDE.md and ~/.codex/AGENTS.md
├── skills/
│   ├── README.md                       # + REGISTRY TABLE: skill | owner | last_reviewed_at | one-line scope
│   ├── tc-1-start/
│   │   ├── SKILL.md                    # ≤1500 chars body, clean 2-field frontmatter
│   │   └── references/
│   │       ├── kickoff-runbook.md      # extracted: project-create flag walkthrough, 真验证 checklist
│   │       └── feishu-cards.md         # extracted: 意向卡/开工卡 skeletons (copied from standards §2/§3/§5)
│   ├── tc-2-research/
│   │   └── SKILL.md                    # publish procedure DELETED — replaced by pointer to tc-render/PUBLISH.md
│   ├── tc-3-plan/
│   │   ├── SKILL.md
│   │   └── references/templates.md     # project + task-layer plan templates
│   ├── tc-4-build/ SKILL.md + references/kickoff-card.md
│   ├── tc-5-review/ SKILL.md + references/fields-schema.md
│   ├── tc-conflict/ SKILL.md + references/decision-template.md
│   ├── tc-design-review/ SKILL.md + references/reviewer-prompt.md
│   ├── tc-friday/ tc-handoff/ tc-health-check/ tc-monday/ tc-roles/ tc-self-check/  (SKILL.md only)
│   ├── tc-ops/  SKILL.md + 3 scripts (unchanged) 
│   └── tc-render/                      # promoted to explicit "shared base"
│       ├── SKILL.md
│       ├── publish.py / transition.py / PUBLISH.md / publish-contract-v1.yaml / assets/ / tests/
│       └── references/
│           ├── multica-fields.md       # MOVED here from standards/ (canonical copy)
│           ├── labels.md               # MOVED here from standards/ (canonical copy — transition.py cites it)
│           └── sop-excerpts.md         # 1-paragraph verbatim excerpts: P-2 signals, P-5 principles,
│                                       #   P-7 verification, ❌-list — the ONLY SOP text skills may cite
├── standards/
│   ├── multica-fields.md → 5-line pointer stub ("moved to skills/tc-render/references/…")
│   ├── labels.md         → pointer stub
│   └── feishu-card-style.md (stays; autopilots read it; skills use their bundled excerpts)
├── sop/  decisions/  autopilots/       # unchanged
└── scripts/                            # sync-team-config.sh kept, 3 small patches (below)
```

Rationale for the bundling strategy: every doc-flow skill already hard-depends on `~/.claude/skills/tc-render/` for publish.py/transition.py, and that directory travels on ALL distribution paths (symlink sync copies the whole dir; `multica skill files upsert` pushes bundled files; `skill pull` reconstructs them; the signed bundle archives them). So shared standards move INTO tc-render/references/ — one canonical copy that is guaranteed reachable wherever any consumer skill is installed. Cross-skill references standardize on exactly one form: `~/.claude/skills/tc-render/<file>` (the form that already works under both symlink and pull-copy). All relative forms (`tc-render/publish.py`, `standards/multica-fields.md`) are banned by CI lint.

#### Package format: stay on the plain Agent Skills standard

Each skill dir = standard-format package: SKILL.md (name+description frontmatter only) + optional `references/` + scripts. This IS the requested "standard-format team SKILL package" — the open agentskills.io layout, portable to Claude Code and Codex, no plugin manifest needed. Exact frontmatter after migration (example, tc-5-review):

```yaml
---
name: tc-5-review
description: "Runs the end-of-project/task debrief (复盘) and writes the team's five-section case file — goal recap, what happened, criteria met/not, key judgments, rule candidates — then publishes it to the tracking issue and routes it for review. Use when wrapping up: \"复盘\", \"收尾\", \"写 case\", \"debrief\", \"wrap up\", \"project done\", or completion criteria are met. Not for code review — that is a separate gate."
---
```

Rules: third-person WHAT first; front-loaded bilingual triggers; a disambiguating "Not for…" clause where names collide; ≤480 chars (so the registry's 480-char truncation can never cut it); single-line quoted YAML (so `_skill_desc`'s single-line regex always extracts it); zero SOP pins, zero script/tool names, zero changelog. `owner` and `last_reviewed_at` LEAVE frontmatter and move to the skills/README.md registry table — this simultaneously makes the frontmatter spec-clean and neutralizes the documented `multica skill pull` lossiness (nothing left to drop).

#### Distribution flow (kept, 3 patches)

1. Member machines: `bash scripts/sync-team-config.sh` — unchanged: whole-dir symlinks into `~/.claude/skills/`, `claude_md_team_global.md` → `~/.claude/CLAUDE.md` + `~/.codex/AGENTS.md`, registry create-or-update push.
   - Patch 1: owner for the registry push is read from the skills/README.md registry table instead of frontmatter (awk on the table row), keeping registry governance data intact.
   - Patch 2: `_gen_codex_index` writes `~/.claude/skills/<name>/SKILL.md` paths (stable on every machine) instead of the generating machine's absolute repo path.
   - Patch 3 (cheap, high-value Codex fix): add a second symlink loop `ln -sfn "$d" "$HOME/.agents/skills/$(basename "$d")"` — Codex natively scans `$HOME/.agents/skills` per the official standard, giving Codex real description-driven triggering instead of a prose index. The index is kept as belt-and-braces for older Codex versions.
2. Non-dev members: `multica skill pull --all` — unchanged; now lossless because frontmatter is only name/description.
3. Update flow: unchanged (edit → PR → merge → members `git pull` + re-run sync, or `multica skill pull --all`). The already-designed `skills-v*` signed-bundle + daemon path remains the future auto-update answer; nothing in this design blocks it — content fixes ride the same `git archive` bytes.

#### claude_md_team_global.md as routing layer (rewrite, keep ≤3k-token CI cap)

- The dispatch table grows from 12 rows to 15 (add tc-design-review, tc-ops; note tc-render as "被其他 skill 调用,一般不直接叫") and gains a 触发词 column with 2–3 bilingual phrases per row — this primes the model even when the skill listing budget drops descriptions.
- Add one priming rule above the table: "遇到下表任一场景,先调对应 skill 再动手;拿不准就打开 skill 看 description。"
- STRIP mechanics that duplicate skill bodies: rule #3/#6 lose the publish.py/命门A/UUID plumbing (they say "用 tc-5-review / tc-render skill" and stop); line 65's dangling `~/.claude/skills/multica-cli/` reference is deleted; line 66's "Codex 直读 repo 目录" becomes "Codex 同样装载 ~/.agents/skills 下的同名 skill"。
- The "去哪儿找 context" table updates standards/ pointers to the new tc-render/references/ locations.

#### Division of labor (codified as a lint-enforced convention, stated in skills/README.md)

- SKILL.md body = decision logic only: entry criteria, ordered steps, gates, anti-patterns, handoffs. ≤1500 chars. Never duplicates a contract that a script enforces — it points at the script/PUBLISH.md as source of truth.
- multica CLI = ALL issue/project/label/status state. Direct `multica` commands allowed only for reads and creates (`project list --full-id`, `issue create --project <UUID> --assignee "$ME_NAME"`); every状态/label transition goes through `~/.claude/skills/tc-render/transition.py <verb>`; every doc publish through `publish.py` (命门B). Skills state the command verbatim on one line each, plus the standard fallback: "报 unknown flag/not found → `multica update`,再失败 → 停下问用户"。
- remote MCP (tcmcp-remote) = Feishu side effects only — notify_team, betting_table_capture, dm_member — i.e., anything requiring team secrets the agent must never hold. Skills reference these by tool name with a one-line degradation rule: "tcmcp-remote 未连接 → 明确告知用户未发送,给出手动文案;绝不谎称已广播。" The deprecated `plan_request_review` MCP tool should be deregistered server-side (it is a documented double-writer against transition.py), but skills stop mentioning it either way.

#### Versioning + CI lint

- Content version = git SHA (and `skills-v*` tags when bundle releasing starts). Review freshness = registry table `last_reviewed_at`, checked by CI, surfaced by tc-ops monthly_health.py (patched to read the table).
- lint.yml gains a `skill-content-lint` job (single python script, runs on every PR touching skills/):
  1. frontmatter: exactly {name, description}; name == dirname; description 100–480 unicode chars, single line, contains ≥2 CJK and ≥2 ASCII trigger phrases (heuristic: quoted strings), and matches NONE of the forbidden regexes `SOP v0\.\d|MCP|publish\.py|transition\.py|命门|不再走|去本地|docs/(plans|research)/`.
  2. body ≤1500 unicode CHARS (replacing monthly_health.py's word-split estimate that undercounts CJK ~10x — the reason 13 of 15 skills silently violate the "enforced" cap today).
  3. path lint on body: ban `standards/`, `sop/`, bare `tc-render/`; allow only `~/.claude/skills/tc-render/…`, own-dir `references/…`, and skill names.
  4. registry table row exists per skill dir, last_reviewed_at ≤90 days.
  5. `skills-ref validate` (open-standard validator) as a portability smoke check.
- A 30-line trigger-eval script (scripts/skill-trigger-eval.sh) keeps 4–6 canned user utterances per skill (from the descriptions' trigger lists) and greps that each utterance's keywords appear in exactly one skill's description — a cheap regression net for description edits.

**迁移步骤**
- Step 0 — land the gate first: add skill-content-lint to .github/workflows/lint.yml (frontmatter whitelist {name,description}, ≤1500-unicode-char body counted by len(chars) not words*1.3, forbidden-token regexes on description, path lint, registry-table check). Also patch skills/tc-ops/monthly_health.py to the same char counting and to read owner/last_reviewed_at from skills/README.md instead of frontmatter. Merge with the lint in warn-only mode.
- Step 1 — bundle shared assets: `git mv standards/multica-fields.md standards/labels.md skills/tc-render/references/`; leave 5-line pointer stubs at the old paths; create skills/tc-render/references/sop-excerpts.md with verbatim one-paragraph excerpts of P-2 pollution signals, P-5 conflict/DRI principles, P-7 verification checklist, and the ❌ anti-pattern list; copy the two Feishu card skeletons needed by tc-1-start/tc-4-build into their own references/ files; update transition.py docstring + argparse text and scripts/create-labels.sh comments to the new labels.md location.
- Step 2 — rewrite all 15 descriptions in one PR using the audits' suggested_description drafts as the base, applying the house rules (third-person WHAT first, front-loaded bilingual triggers, ≤480 chars single-line quoted YAML, add missing triggers: 复盘 to tc-5-review, 开工/开始写代码 to tc-4-build, 分工/责任人 to tc-roles, issue 巡检/label 漂移 to tc-ops, a 'Not for…' disambiguator on tc-5-review vs code review and tc-1-start vs task layer). Delete owner/last_reviewed_at from every frontmatter and write the skills/README.md registry table in the same PR.
- Step 3 — body diets, one PR per skill (reviewable): extract over-budget reference material into references/*.md (tc-1-start runbook + cards, tc-3-plan templates, tc-5-review fields schema, tc-conflict decision template, tc-design-review reviewer prompt); delete ALL changelog narration (不再走 X MCP / 原 session_handoff / TEA-95/70 lore); replace every inline copy of the publish contract (tc-2/3/5/handoff) with one line: '发布与状态转换按 ~/.claude/skills/tc-render/PUBLISH.md 执行,exit 2 处理规则见该文件'; normalize every cross-skill path to the ~/.claude/skills/... form; replace SOP citations with either one inlined sentence or a pointer to tc-render/references/sop-excerpts.md; fix tc-render's stale 7-vs-9 subcommand count and tc-ops' 6-vs-8 invariant drift by DELETING the counts from prose (script --help is the source of truth).
- Step 4 — rewrite claude_md_team_global.md: 15-row dispatch table with a bilingual trigger-phrase column, priming rule above it, mechanics stripped from rules #3/#6, dead multica-cli skill reference removed, context table updated to new reference locations; verify the 3k-token CI cap still passes.
- Step 5 — patch scripts/sync-team-config.sh: (a) owner extraction from the registry table, (b) _gen_codex_index emits ~/.claude/skills/<name>/SKILL.md paths, (c) add the ~/.agents/skills symlink loop for Codex-native discovery; run `bash scripts/sync-team-config.sh` on the DRI machine and verify `multica skill pull --all` round-trips a skill byte-identically (lossiness gone).
- Step 6 — flip skill-content-lint from warn to fail; add scripts/skill-trigger-eval.sh (canned utterances → unique-skill keyword match) to CI; announce in the team Feishu group: everyone `git pull && bash scripts/sync-team-config.sh` once; Codex users confirm skills appear via /skills.
- Step 7 (follow-ups explicitly out of minimal scope, tracked as issues): deregister the deprecated plan_request_review MCP tool server-side; fix archive_to_wiki/burnout server-side file I/O; resume the skills-v* signed-bundle daemon work for true zero-touch updates.

**skill 优化**
- Cross-skill: one description template enforced everywhere — [Third-person WHAT, 1 sentence] + [Use when + front-loaded bilingual trigger list] + [optional 'Not for X — use Y' disambiguator]. Ban list in descriptions: SOP version pins, MCP/tool/script names, file paths, changelog phrases, 命门/P-x/rule-#n codenames.
- Cross-skill: publish/transition contract exists in exactly ONE place (tc-render/PUBLISH.md + script --help). tc-2-research, tc-3-plan, tc-5-review, tc-handoff each shrink by ~800–1500 chars by replacing their inlined copies with a single pointer line — this alone brings most bodies under budget and kills the already-observed drift (7 vs 9 subcommands).
- Cross-skill: standard prerequisite/fallback block (3 lines) appended to every CLI-using skill: multica 不在 PATH → 装/更新; unknown flag → multica update; tcmcp-remote 未连接 → 告知未发送并给手动文案。Today zero skills state fallbacks.
- tc-1-start: adopt audit's suggested description (defines project-layer inline: 3+ days, has DRI; routes task-layer to tc-3-plan task-mode); move the multica project create flag walkthrough, Feishu card specs and 真验证 checklist to references/; delete the '⚠️ kickoff 是手动编排' migration essay; unify the mixed relative/absolute script paths to ~/.claude/skills/tc-render/….
- tc-2-research: resolve the internal contradiction (markdown skeleton vs publish.py --dry-run HTML) by keeping only the dry-run flow; drop 'RPI framework' as the description opener in favor of triggers 调研/研究一下/start research; delete the uncited BCG statistic.
- tc-3-plan: add missing Chinese triggers 写计划/制定计划/规划/写个方案; extract both templates to references/templates.md; delete task-layer execution policy (belongs to tc-4-build) and the design-gate paragraph (belongs to tc-design-review) — replace each with one pointer sentence.
- tc-4-build: add 开工/开始写代码/实现 triggers; move human-operator SOP lines (30s CoT rule, human-eye-on-diff) into a clearly marked '给操作者' subsection or the SOP doc; kickoff card skeleton to references/.
- tc-5-review: add 复盘 as the FIRST trigger (the body's own vocabulary, absent from today's description); fields.json one-line schema becomes references/fields-schema.md with a real code block; delete TEA-95/70 incident lore.
- tc-design-review: front-load 设计评审/design review/方案过一下; keep the excellent ①②③ gate disambiguation but drop transition command strings and label names from the description; reviewer-subagent prompt to references/reviewer-prompt.md.
- tc-handoff: keep its already-strong triggers; delete the three 原 session_handoff provenance notes and the fields.json schema copy; give the <60s idempotency gate a concrete check command (multica issue comment list --tail 1 + timestamp compare) or drop the precision.
- tc-health-check: align verdict vocabulary (continue | mention | tc-handoff-now) with the aggregation-rule prose; retitle H1 to match the skill name; drop 'SOP v0.4 dumb zone' from the description.
- tc-ops: description must name all THREE scripts including issue_invariants.py with triggers issue 巡检/label 漂移/invariants (today a third of the skill is undiscoverable); fix 6→8 invariant and 这俩→这三 drift by deleting counts from prose; invocation examples switch to 'run <script> bundled in this skill dir' phrasing.
- tc-render: adopt audit's suggested description (front-loaded publish/render/transition keywords, 'typically invoked by the 4 doc skills; use directly only for standalone transitions'); delete the stale future-tense 迭代2 sentence; body keeps only WHAT+entry commands, everything else defers to PUBLISH.md.
- tc-monday / tc-friday / tc-conflict / tc-roles / tc-self-check: light-touch — description rewrites per audits (fix imperative openers, add 分工/责任人/自检/反模式 triggers), tc-conflict's decision template to references/ and anchor decisions/ path explicitly to the team-context repo, tc-self-check keeps its inlined anti-pattern list (correct portability call) but gains a sync note naming the SOP source section.

**优点**
- Smallest possible diff for the largest discovery win: descriptions are the ONLY thing agents see at session start, and every one of the 15 is rewritten; nothing about the working symlink/registry/index plumbing changes, so zero re-onboarding for the 5 members beyond one re-sync.
- Fully standard-compliant packages fall out for free: 2-field frontmatter + references/ layout is the exact agentskills.io format, portable to Claude Code AND Codex, and the ~/.agents/skills symlink patch gives Codex native description-driven triggering with ~3 lines of shell.
- Neutralizes three documented bugs as side effects: multica skill pull lossiness (no frontmatter left to drop), registry 480-char description truncation (lint caps at 480), and the CJK token-undercount that made the 'enforced' body cap fictional.
- Kills the drift engine: single-sourcing the publish contract in tc-render/PUBLISH.md and moving shared standards into tc-render/references/ means the observed 7-vs-9 and 6-vs-8 drifts cannot recur, and every reference resolves identically in-repo, post-symlink, post-pull, and in the future signed bundle.
- Forward-compatible: nothing conflicts with the approved mini-ADR v4 signed-bundle/daemon end-state — the same git-blob bytes get better, and the relaxed frontmatter makes byte-identity between review and disk easier to keep.
- Cheap to verify: the trigger-eval script plus CI lint give a regression net; total effort is roughly 2–4 focused days for one person plus review, versus weeks for a plugin/marketplace or daemon build-out.

**缺点**
- Does not solve distribution staleness: updates remain manual (git pull + re-sync or skill pull); a member on a 3-week-old copy still gets no signal. That is honestly deferred to the already-designed skills-v* daemon path.
- Codex parity is still partial: even with ~/.agents/skills, Codex lacks Claude-only affordances (skill re-attachment on compaction, allowed-tools, /doctor visibility), and the AGENTS.md symlink means Codex loads the same routing file without the skill-listing mechanism backing it — triggering quality in Codex will lag Claude Code.
- No plugin/marketplace packaging: the team forgoes namespacing, versioned install/update UX, enabledPlugins-based zero-friction onboarding, and MCP-config-shipped-with-skills that a Claude Code plugin would give — acceptable at 5 people, a real gap at 15.
- multica's own `skill lint` (CLI, cmd_skill.go) still WARNs on missing owner/last_reviewed_at frontmatter; until the CLI is updated the team must ignore those WARNs or carry a small CLI patch — a temporary two-linter inconsistency.
- Content surgery touches every live workflow skill at once; even with per-skill PRs there is a window where muscle-memory phrases ('走 plan_create'-era wording, old paths in members' heads and in autopilot prompts) mismatch the new text.
- The 1500-char body cap forces real information out of SKILL.md into references/ that load only on demand — if an agent skips opening the reference file, it may execute with less guidance than today's bloated-but-inline bodies provided.

**风险**
- Description rewrites can change auto-trigger behavior in unanticipated ways (false negatives on phrases the old noisy text accidentally matched). Mitigation: the canned-utterance trigger-eval in CI plus a one-week bake where members report missed triggers; keep old trigger phrases as a superset where possible.
- Moving standards/multica-fields.md and labels.md breaks unaudited consumers (autopilot YAML prompts, scripts/create-labels.sh, docs, member bookmarks). Mitigation: pointer stubs at old paths + repo-wide grep for 'standards/(multica-fields|labels)' in the same PR; stubs stay for 90 days.
- Registry/pull round-trip regressions: sync-team-config.sh's owner-from-table patch and the registry's frontmatter rebuild must be tested together or the push could write empty owners / the pull could still mutate bytes. Mitigation: Step 5 includes an explicit byte-identity round-trip check before announcing.
- Dual-writer hazard persists until the deprecated plan_request_review MCP tool is deregistered server-side — an agent that discovers the tool via MCP listing can still race transition.py (label without status). Content fixes reduce but cannot eliminate this; it needs the follow-up server change.
- The symlink-vs-physical-copy 'three truths' shadowing problem remains: a member with a stale physical ~/.claude/skills/tc-x dir silently shadows the fresh symlink (sync-to-local.sh only WARNs). Mitigation: sync-team-config.sh could fail loudly on shadowed dirs, but true resolution is the daemon's mutual-exclusion design — out of minimal scope.
- Honest scope limit: if after the content fixes agents still fail to invoke skills, the residual cause is model routing behavior / listing-budget drops rather than content — at that point the escalation is packaging (plugin with when_to_use, disable-model-invocation tuning, skillListingBudgetFraction) and this minimal-change bet should be revisited rather than doubled down on.

</details>

## 4. 最终推荐

Winner: Design 2 (Multica-Registry-First) as the target architecture, executed with Design 3's sequencing. Rationale: all three designs share ~80% of the actual work — the 15 description rewrites, body diets to ≤1500 chars, references/ extraction, single-sourcing the publish/transition contract under tc-render, and spec-clean frontmatter. The only real differentiator is the distribution plane, and for this team the registry wins on every axis that matters at 5 people: it is infrastructure they already operate (verified: skill/skill_file/agent_skill tables, owner_user_id/last_reviewed_at columns, skill pull --all --dir, touch-reviewed/--stale, per-task workdir injection, and a daemon skillSyncLoop all exist in tc-multica); it is the ONLY plane that serves all three consumer classes (Claude Code personal skills, Codex ~/.agents/skills, and daemon task-workdir injection) from one artifact; and it gives clone-less onboarding plus fleet staleness observability that neither git-symlinks nor a Claude-only plugin marketplace can. Design 1's plugin is rejected as the primary channel because it is Claude-Code-only (Codex needs a parallel git channel anyway), its private-repo auto-update needs per-member autoUpdate toggles plus GH_TOKENs on every laptop, and it routes around rather than through the team's control plane — but it stays on file as the explicit escalation if, after the content fixes bake, auto-triggering still fails for routing/listing-budget reasons. Grafts into the winner: from Design 3 — week-1-first content surgery over existing pipes with zero dependencies, moving shared standards INTO tc-render/references/ (one canonical travelling copy) instead of Design 2's build-time fragment generation (simpler, no DO-NOT-EDIT generated duplication to police), pointer stubs at old standards/ paths, the ~/.agents/skills symlink patch as the interim Codex fix, and the trigger-eval canned-utterance CI script; from Design 1 — the hard CI lint spec (frontmatter whitelist, CJK-correct len() char counting, ≤450-char single-line descriptions, grep bans on paths/SOP pins/retired tool names), the prerequisite/fallback block in every CLI-touching skill, and the MCP surface cleanup (delete plan_request_review after grepping autopilots, retire should_i_use_ai and code_review_request, fix archive_to_wiki to accept inline content — its file-path signature is verifiably broken since the remote-only move). Correctness non-negotiables preserved: lint-tooling lockstep (patch monthly_health.py and multica skill lint in the same change that deletes owner/last_reviewed_at from frontmatter, or the team red-flags itself); descriptions capped at 450 chars until the CLI's 480-char truncation is raised to 1024; verify-after-write content-hash parity in the registry push (per-file upsert failures are currently swallowed); bind tc-render to every agent bound to any doc skill so per-task injection never hydrates a consumer without its base; DRI dev boxes keep git symlinks with SkillWriteGuard-enforced mutual exclusion. Week 1 = content + lint + Codex symlinks over existing pipes (Design 3 verbatim). Weeks 2-4 = tc-multica CLI fixes, then registry cutover with hourly pull cron. Later/optional = daemon registry-source mode and the parked signed-bundle path only if cryptographic provenance is ever actually needed; plugin packaging only as the documented escalation."}

### 目标架构

AUTHORING PLANE = git (team-context repo, PR-reviewed, CI-linted). DISTRIBUTION PLANE = multica skill registry (CI is the only writer; content-hash parity enforced). Repo layout:

team-context/
├── claude_md_team_global.md          # ≤3k tokens; dispatch table shrunk to compact 15-row name+2-trigger list during 4-week bake, then 3 lines; adds the single skills-root definition ("~/.claude/skills, or task-workdir .claude/skills under the daemon, or ~/.agents/skills for Codex") and the transitions-only-via-transition.py rule; still symlinked to ~/.claude/CLAUDE.md and ~/.codex/AGENTS.md
├── sop/  decisions/  autopilots/  cases/   # unchanged, authoring-only
├── standards/feishu-card-style.md    # stays (autopilots read it); labels.md + multica-fields.md become 5-line pointer stubs (90 days)
├── skills/                            # 15 standard agentskills.io packages; frontmatter = name + description (+optional license/metadata.source-commit) ONLY
│   ├── tc-render/                     # the ONE base skill owning scripts + contracts
│   │   ├── SKILL.md
│   │   ├── scripts/publish.py  scripts/transition.py
│   │   ├── references/publish-contract.md   # merged PUBLISH.md + publish-contract-v1.yaml; sole home of exit codes, fields.json schemas, 9-subcommand transition list
│   │   ├── references/labels.md  references/multica-fields.md  references/sop-excerpts.md   # MOVED canonical copies (git mv from standards/), travel with tc-render on every channel
│   │   ├── assets/style.css
│   │   └── (tests/ relocated to repo-root tests/render/ — excluded from distribution)
│   ├── tc-1-start/ … tc-self-check/   # SKILL.md ≤1500 unicode chars + per-skill references/ (templates, card skeletons, reviewer prompts)
│   └── README.md                      # ownership registry table: skill | owner | last_reviewed_at | scope (frontmatter fields deleted; registry DB columns owner_user_id/last_reviewed_at + touch-reviewed are the runtime source)
└── scripts/
    ├── push-skills-to-registry.sh     # CI-only on merge to main: create-or-update + files upsert + verify-after-write sha256 parity; stamps skills_rev (git commit count on skills/**) into skill.config JSONB; refuses rev bump on any file failure
    ├── check-registry-sync.sh         # upgraded from name-presence to content-hash parity
    ├── skill-trigger-eval.sh          # canned bilingual utterances → keywords match exactly one description
    └── sync-team-config.sh            # reduced to: global-md symlinks + DRI dev-symlink mode + (interim) ~/.agents/skills symlink loop; Codex skills-index generation deleted

DISTRIBUTION FLOW: merge to main → CI lints (skills-ref validate; frontmatter whitelist; ≤450-char single-line description with ≥3 CJK + ≥2 EN quoted triggers and banned-token regexes; body ≤1500 via len(chars); path lint; cross-skill name check; parity hash) → CI pushes to registry with least-privilege service token → member machines run `multica skill pull --all` (→ ~/.claude/skills) and `multica skill pull --all --dir ~/.agents/skills` (→ Codex native discovery), hourly via launchd/cron; `multica skill pull --check` wired into `multica doctor` surfaces staleness. Daemon-run agents get skills via existing per-task injection (always-current by construction); every agent bound to a doc skill is also bound to tc-render. DRI boxes keep git symlinks for the edit loop; SkillWriteGuard/MULTICA_DAEMON_SKILL_WRITE mutual exclusion prevents clobbering. Requires four tc-multica CLI fixes first: lossless spec-clean pull frontmatter, atomic per-skill temp-dir+rename writes, --content-file flags on create/update/files-upsert, and raising the 480-char description cap to the spec's 1024.

DIVISION OF LABOR: SKILL.md body = WHEN + decision gates + ordered imperative steps + anti-patterns + handoffs, nothing else. multica CLI direct = reads and one-line creates (project list --full-id, issue create --assignee resolved via `multica auth status`+`user list`, comment list, skill pull). tc-render scripts = ALL doc publishing (publish.py, 命门B) and ALL label/status transitions (transition.py, 9 subcommands) — invoked via the one skills-root phrase defined in global rules. Remote MCP (tcmcp-remote) = ONLY server-secret Feishu side effects: notify_team, dm_member, betting_table_capture, burnout_check_distribute, archive_to_wiki (fixed to accept inline markdown), search_chat, read_member_dm; plan_request_review deleted (deprecated double-writer that omits status=in_review), should_i_use_ai and code_review_request retired into skill prose. Registry stays authoritative for governance (owner, review dates, staleness). Offline: skills are physical files, fully functional; each CLI-touching skill carries a 3-line prerequisite/fallback block; staleness bounded by cron and surfaced by doctor. Parked, not deleted: signed skills-v* bundle + daemon skillSyncLoop as the future hardened channel; Claude Code plugin/marketplace as the documented escalation if description-driven routing still underperforms after the bake.

### 迁移计划

1. WEEK 1, day 1 — land the gate first (warn-only): add skill-content-lint to .github/workflows/lint.yml — frontmatter whitelist {name, description, license?, metadata?}, body ≤1500 unicode chars counted by len() not words*1.3, description ≤450 chars single-line quoted with ≥3 CJK + ≥2 English quoted trigger phrases, banned-token regexes (SOP v0\., 命门, MCP tool names, publish\.py, transition\.py, ~/.claude/skills, standards/, docs/(plans|research)/, 不再走, 原 ), cross-skill references must name an existing skill dir, plus skills-ref validate. In the same PR patch skills/tc-ops/monthly_health.py to len()-based counting and to read owner/last_reviewed_at from the skills/README.md table (lockstep rule: tooling updates land WITH or BEFORE the field removal, never after).
2. WEEK 1 — bundle shared assets into the base skill: git mv standards/labels.md and standards/multica-fields.md → skills/tc-render/references/ (5-line pointer stubs at old paths, kept 90 days); merge PUBLISH.md + publish-contract-v1.yaml → references/publish-contract.md; create references/sop-excerpts.md with the verbatim P-2/P-5/P-7/❌-list paragraphs; relocate skills/tc-render/tests/ → repo-root tests/render/; update transition.py docstring/argparse text and scripts/create-labels.sh comments to the new labels.md location; repo-wide grep for 'standards/(labels|multica-fields)' in the same PR (autopilot YAMLs, docs).
3. WEEK 1 — rewrite all 15 descriptions in one PR from the audits' suggested_description drafts: third-person WHAT first, front-loaded bilingual quoted triggers, 'Not for X — use Y' disambiguators, ≤450 chars single line; add the missing high-ROI triggers (复盘→tc-5-review, 开工/开始写代码/实现→tc-4-build, 写计划/制定计划/规划→tc-3-plan, issue 巡检/label 漂移/invariants→tc-ops, 自检/反模式→tc-self-check, 分工/责任人→tc-roles); delete owner/last_reviewed_at from every frontmatter and write the skills/README.md ownership table in the same PR; backfill registry owner_user_id + touch-reviewed via one-off script; patch sync-team-config.sh owner extraction to read the table.
4. WEEK 1 — body diets, one PR per skill (reviewable): extract templates/card skeletons/reviewer prompts/fields schemas into per-skill references/*.md (tc-1-start runbook+cards, tc-3-plan templates, tc-4-build kickoff-card, tc-5-review case template+fields schema, tc-conflict decision template, tc-design-review reviewer prompt, tc-handoff template); delete ALL changelog/deprecation narration (不再走 X MCP, 原 session_handoff, TEA-95/70 lore); replace inlined publish-contract copies in tc-2/3/5/handoff with one pointer line + the exit-2 recovery rule; fix drift by DELETING counts from prose (7-vs-9 subcommands, 6-vs-8 invariants, 这俩→这三个); normalize every cross-skill invocation to the single skills-root phrase; replace $ME_NAME assumptions with 'resolve current user via multica auth status + user list'; append the standard 3-line prerequisite/fallback block to every CLI-touching skill.
5. WEEK 1 — rewrite claude_md_team_global.md: shrink the dispatch table to a compact 15-row name + 2-trigger-word list (bake insurance, removed after week 6 trigger-eval passes), delete the dead ~/.claude/skills/multica-cli pointer, add the skills-root definition and the 'transitions only via transition.py, never hand-typed label/status commands, never the MCP plan_request_review tool' rule; strip publish mechanics from rules #3/#6; verify the 3k-token CI cap.
6. WEEK 1 — interim Codex fix + one team re-sync: add the ~/.agents/skills symlink loop to sync-team-config.sh, delete _gen_codex_index and ~/.codex/skills-index.md; flip skill-content-lint from warn to fail; add scripts/skill-trigger-eval.sh (4-6 canned utterances per skill → keywords match exactly one description) to CI; announce: everyone runs git pull && bash scripts/sync-team-config.sh once; Codex users confirm skills list via /skills; Claude users verify via /doctor; start the trigger-bake — members report missed/false triggers for a week.
7. WEEKS 2-3 — tc-multica CLI fixes (gates the registry cutover, file as one tracked issue): (a) `multica skill pull` emits spec-clean frontmatter (name/description/license/metadata.source-commit from config JSONB) instead of rebuilding with owner/last_reviewed_at; (b) atomic per-skill write via temp dir + rename; (c) --content-file on skill create/update/files upsert; (d) raise the push/pull description cap from 480 to the spec's 1024 (CI keeps asserting pushed == source length until deployed); (e) `multica skill pull --check` comparing local skills_rev vs registry, wired into `multica doctor`; (f) update `multica skill lint` to stop warning on the removed frontmatter fields.
8. WEEKS 2-3 — registry push pipeline: write scripts/push-skills-to-registry.sh (create-or-update + files upsert, NO swallowed per-file failures, verify-after-write sha256 of body+files against `multica skill get --output json`, skills_rev stamped into skill.config only after full verification) as a CI deploy job on merge to main using a dedicated least-privilege service token; upgrade check-registry-sync.sh from name-presence to content-hash parity (still honest-SKIP on tokenless PR runs); measure total description bytes in CI against Codex's ~8000-char listing budget.
9. WEEK 4 — member-machine cutover: each member runs `multica skill pull --all` and `multica skill pull --all --dir ~/.agents/skills`; delete legacy symlinks and any stale physical copies on non-DRI machines (one-time cleanup script; `multica doctor` flags symlink/copy mixtures using SkillWriteGuard logic); install the hourly launchd/cron pull; DRI boxes explicitly opt into dev-symlink mode via sync-team-config.sh and are excluded from cron; verify byte-identical round-trip (push → pull → diff) on one skill before announcing; bind tc-render to every agent bound to any tc-* doc skill and add a CI check for it; verify daemon per-task injection hydrates the new-format skills on the next autopilot task claim.
10. WEEK 4 — remote MCP surface cleanup (team-context-mcp): grep autopilots/ and all skills for tool names FIRST, then unregister plan_request_review and code_review_request, retire should_i_use_ai (heuristics → tc-self-check references/), change archive_to_wiki to accept inline markdownContent and fix autopilots/monthly-health.yaml in the same change (its /tmp file-path call is currently broken); delete or future-flag the unused MulticaClient.publishDoc/listSkills client surface; announce removals at the Friday demo before merging.
11. WEEK 5-6 — verification + bake close-out: fresh-machine test (multica login → pull → Claude /doctor shows 15 full descriptions → Codex /skills lists 15 → tc-3-plan happy path incl. transition via skills-root phrase → offline test: disconnect, skills still trigger, preflight fails loudly); run the trigger-eval against real phrasing collected during the bake; if triggering is fixed, shrink the global-md dispatch table to 3 lines; if NOT fixed, open the escalation decision (plugin packaging / skillListingBudgetFraction tuning) per Design 3's honest scope limit — do not double down on content.
12. LATER (explicitly deferred, only on demonstrated need): implement MULTICA_DAEMON_SKILL_SOURCE=registry in the daemon skillSyncLoop (reusing anti-rollback, write-path safety, SkillWriteGuard) + heartbeat reporting of installed skills_rev + TEA-113 one-click fleet nudge; revive the parked signed skills-v* bundle path only if cryptographic provenance becomes a real requirement; `multica skill exec tc-render publish -- …` as the location-independent invocation replacing the skills-root phrase; Phase-2 promotion of publish/transition into native multica subcommands per the 2026-06-09 decision's triggers (contract churn / team ≥15).

### Skill 重写规范（CI 可执行）

DESCRIPTION TEMPLATE (all 15, CI-enforced): "[Third-person WHAT, one sentence, opens with a verb — Guides/Runs/Generates/Enforces/Facilitates]. [WHEN: 'Use when the user says' + front-loaded quoted bilingual triggers, ≥3 CJK + ≥2 English, plus behavioral triggers]. [Optional: 'Not for X — use Y' disambiguator against sibling skills]." Hard limits: ≤450 unicode chars (safety margin under the registry's 480-char slice until the CLI cap is raised to 1024, and far under Claude's 1,536-char listing truncation), single-line quoted YAML (the push script's _skill_desc regex only matches single-line descriptions). BAN LIST in descriptions (CI regex): SOP version pins (SOP v0\\.\\d), internal codenames (命门, P-\\d, rule #\\d, RPI as unexplained opener), file paths (docs/, standards/, ~/.claude, cases/, decisions/), script/tool names (publish.py, transition.py, MCP tool names), and changelog phrases (不再, 原 , 去本地). Start from the audits' suggested_description drafts; add the audited missing triggers (复盘, 开工/开始写代码, 写计划/制定计划, issue 巡检/label 漂移, 自检/反模式, 分工/责任人).

BODY BUDGET: ≤1500 unicode characters counted by len(body) — never whitespace-split word counts (the current words*1.3 estimator undercounts CJK ~10x, which is why 13 of 15 skills silently violate the 'enforced' cap). Body contains ONLY: mandate (1-2 lines), entry criteria/gates, ordered imperative steps (one command per line), anti-patterns, handoffs. Everything else — templates, card skeletons, fields schemas, flag walkthroughs, reviewer prompts, verification checklists — moves to per-skill references/*.md loaded on demand. Delete ALL historical narration (retired MCP tool names, TEA-incident lore, 旧实测 notes, version-fragile 'unknown flag → multica update' hints beyond the standard fallback block); provenance lives in decisions/. One language per section (EN skeleton headers OK, CN operational detail OK; no mid-sentence flips). Human-operator SOP lines (read the CoT, hit ESC, human eye on diff) either move to sop/ or sit in a clearly marked 给操作者 block — agent-facing text must be agent-executable.

BUNDLING: contracts exist in exactly ONE place — tc-render/references/publish-contract.md + script docstrings own exit codes, fields.json schemas, the transition subcommand set, and label/status semantics; consumer skills carry one pointer line plus the single load-bearing recovery rule (exit 2 = comment posted, NEVER re-run publish). Shared standards (labels, multica-fields, SOP excerpts) live canonically in tc-render/references/ and travel with it on every channel; consumer skills cite them by skill name + relative filename, never by repo path. Never bake counts into prose (subcommand counts, invariant counts) — script --help is the source of truth; counts are the drift engine already observed twice. SOP rules an agent must enforce at runtime get their 1-2 sentences inlined (tc-self-check pattern) or a pointer to sop-excerpts.md; bare 'SOP P-x' citations are lint-banned.

CROSS-SKILL INVOCATION: exactly one phrase, defined once in claude_md_team_global.md and used verbatim — "python3 <skills-root>/tc-render/scripts/<script>.py …" where skills-root = ~/.claude/skills | task-workdir .claude/skills | ~/.agents/skills. No relative tc-render/publish.py forms, no hardcoded ~/.claude/skills literals in skill prose (both CI-banned; the current mixed relative/absolute pair can never both resolve). Output paths anchored in prose, not bare: 'the current project repo's docs/plans/ (create if missing)', 'the team-context repo's decisions/ dir — ask for its path if not there'.

CLI-vs-MCP DIVISION (state it, don't blur it): direct multica CLI only for reads and one-line creates (project list --full-id, issue create --project <full UUID> --assignee, comment list, auth status, user list); every label/status transition ONLY via transition.py; every doc publish ONLY via publish.py; remote MCP tools ONLY for Feishu side effects (notify_team, dm_member, betting_table_capture) with a mandatory degradation line: 'tcmcp-remote 未连接 → tell the user it was NOT sent and provide manual copy — never claim it was broadcast.' Every CLI-touching skill ends with the standard 3-line prerequisite/fallback block: multica not on PATH → install/update; unknown flag → multica update, then stop and ask; identity via multica auth status + user list, never hardcoded.

FRONTMATTER: exactly {name (== dirname), description}, optionally license and metadata.source-commit (CI-stamped). owner/last_reviewed_at DELETED from frontmatter — ownership lives in skills/README.md + CODEOWNERS, runtime governance in the registry's owner_user_id/last_reviewed_at columns via touch-reviewed. No Claude-only features in shared skills ($ARGUMENTS, !`cmd` injection, context: fork, hooks, paths) — they must stay inert-safe for Codex; Codex-specific metadata goes in optional agents/openai.yaml which Claude Code ignores.

## 5. 事实验证结果（对抗性）

| 结论 | 判定 |
|---|---|
| team-context/skills/tc-render/transition.py defines exactly 9 subcommands — publish-init, plan-request-review, plan-approve, plan-… | **CONFIRMED** |
| team-context/scripts/sync-team-config.sh truncates each skill description to 480 characters when pushing to the multica registry (… | **CONFIRMED** |
| sync-team-config.sh symlinks each whole skills/tc-* directory into ~/.claude/skills via `ln -sfn` and symlinks claude_md_team_glob… | **CONFIRMED** |
| team-context/skills/tc-ops/monthly_health.py estimates skill body tokens as len(text.split()) * 13 // 10 (whitespace split, line ~… | **REFUTED** |
| Measured SKILL.md body lengths confirm the over-budget audits: tc-3-plan ≈5458 chars, tc-1-start ≈4350, tc-handoff ≈3916, tc-2-res… | **CONFIRMED** |
| The multica CLI has `multica skill pull [<name>\|--all] [--dir]` (tc-multica server/cmd/multica/cmd_skill.go, ~lines 363-464) that … | **CONFIRMED** |
| `multica skill pull` currently rebuilds SKILL.md frontmatter on pull and was measured to drop owner/last_reviewed_at, self-breakin… | **REFUTED** |
| The multica daemon injects agent-bound registry skills into each task workdir at provider-native paths (.claude/skills/{name}/SKIL… | **CONFIRMED** |
| The daemon's skillSyncLoop is gated behind MULTICA_DAEMON_SKILL_WRITE which defaults OFF everywhere (tc-multica server/internal/da… | **CONFIRMED** |
| The remote MCP server (team-context-mcp packages/remote/src/server.ts buildToolDefs, lines ~242-340) registers exactly 10 tools an… | **CONFIRMED** |
| archive_to_wiki reads its markdownPath argument with readFile on the server container (team-context-mcp packages/feishu/src/client… | **CONFIRMED** |
| Per OpenAI's official docs (developers.openai.com/codex/skills), Codex natively implements the agentskills.io standard and scans .… | **CONFIRMED** |
| Per official Claude Code docs (code.claude.com/docs/en/skills and /discover-plugins): all skill names+descriptions load at session… | **REFUTED** |
| Per the agentskills.io specification, legal SKILL.md frontmatter is name (must match the directory name), description (1-1024 char… | **CONFIRMED** |
| team-context/scripts/check-registry-sync.sh verifies only that each repo tc-* skill NAME exists in the registry (grep -qx) and exi… | **CONFIRMED** |

### 3 处驳倒修正（对计划的影响）

- **team-context/skills/tc-ops/monthly_health.py estimates skill body tokens as len(text.split()) * 13 // 10 (whitespace spl…**
  - The mechanics are confirmed but the conclusion rests on a false premise. Confirmed: monthly_health.py:16 is exactly `return len(text.split()) * 13 // 10  # 空白分割 · 复刻 MCP estimateTokens`, and it drastically undercounts CJK (empirically: 1500 spaceless CJK chars → 1 estimated token). REFUTED part: there is no "stated ≤1500-char body cap". skills/README.md:15 calls 1500字 a 目标 (target): "目标 ≤ 1500 字（约 2000 tokens）。CI lint 强制执行硬上限。", and docs/plans/plan_2026-06-05_cap-hardening-team-context.html:37 explicitly states "skill_lint 硬门=2000 token 非 1500 字" (hard gate = 2000 tokens, NOT 1500 chars), with line 68 adding the ≤1500字 is a self-set 软目标 (soft target) "两者不同" (the two are different). What is actually enforced — by monthly_health.py:79 (`if tok > 2000`) and CI .github/workflows/lint.yml:34-42 — is a 2000-token hard cap, never a character cap; a char cap would be tokenizer-independent anyway. The true residual issue (not what the claim asserts) is that the enforced 2000-token gate is itself toothless for CJK-heavy bodies because the same whitespace heuristic is used in lint.yml:40, team-context-mcp/packages/shared/src/tokens.ts:7-8, and tc-multica/server/cmd/multica/cmd_skill.go:469.

- **`multica skill pull` currently rebuilds SKILL.md frontmatter on pull and was measured to drop owner/last_reviewed_at, se…**
  - The "currently drops" part is false; only the historical documentation is real. (1) Doc citation is accurate: team-context/decisions/2026-06-09-rpi-publish-architecture-redeliberation.md:86 "关键实测:`multica skill pull` 重建 frontmatter 丢 owner/last_reviewed_at(问题④根因)" and :15 "buildSkillMd pull 丢 owner → 自伤 lint". (2) But the bug was fixed the same day: tc-multica commit f7724337c (2026-06-09, "buildSkillMd owner"); current code tc-multica/server/cmd/multica/cmd_skill.go:345-349 writes both fields on pull: `if v := strVal(skill, "owner_user_id"); v != "" { b.WriteString("owner: " + v + "\n") }` and `if v := strVal(skill, "last_reviewed_at"); v != "" { b.WriteString("last_reviewed_at: " + v + "\n") }`; TestBuildSkillMd (cmd_skill_test.go:26-36) asserts both appear; repo HEAD is 2026-07-01. (3) Even historically, "drop owner/last_reviewed_at" overstates: the team's own plan (team-context/docs/plans/plan_2026-06-09_dropmcp-phase1-converge-seamless_v2.html) corrects it — "现 :259 只写 name/desc/last_reviewed_at...last_reviewed_at 已写、只缺 owner" (last_reviewed_at was already written; only owner was dropped). What is actually true: pull does rebuild frontmatter (buildSkillMd, cmd_skill.go:331-361), the lint does check owner/last_reviewed_at (cmd_skill.go:549-556), and the drop-owner bug existed on 2026-06-09 but is fixed in current code.

- **Per official Claude Code docs (code.claude.com/docs/en/skills and /discover-plugins): all skill names+descriptions load …**
  - The claim is a conjunction; one conjunct is false, so the whole claim fails. CONFIRMED parts: (1) code.claude.com/docs/en/skills: "Skill descriptions are loaded into context so Claude knows what's available. All skill names are always included, but if you have many skills, descriptions are shortened to fit the character budget... The budget scales at 1% of the model's context window" (nuance: names always load; descriptions can be shortened/dropped within the 1% budget). (2) Same page: "the combined `description` and `when_to_use` text is truncated at 1,536 characters in the skill listing to reduce context usage" (cap configurable via skillListingMaxDescChars). (3) code.claude.com/docs/en/discover-plugins: "Official Anthropic marketplaces have auto-update enabled by default. Third-party and local development marketplaces have auto-update disabled by default." (4) GITHUB_TOKEN/GH_TOKEN requirement is real but documented on code.claude.com/docs/en/plugin-marketplaces (Private repositories), not /discover-plugins: "Background auto-updates run at startup without credential helpers... To enable auto-updates for private marketplaces, set the appropriate authentication token in your environment: GitHub — GITHUB_TOKEN or GH_TOKEN." REFUTED part: "plugin/marketplace distribution is Claude-Code-only" — no such exclusivity statement exists on either cited page, and official Anthropic docs show the opposite is actually true: support.claude.com/en/articles/13837440 ("Use plugins in Claude"): "You can install and use plugins in chat on the web, the Chat tab in Claude Desktop, and Claude Cowork," including marketplaces ("add other Anthropic-built marketplaces, like Financial Services or Legal, or add one from a GitHub repository"), and support.claude.com/en/articles/13837433 documents org-level plugin marketplaces managed through claude.ai admin settings (manual upload or GitHub sync). The skills doc also notes skills follow the Agent Skills open standard "which works across multiple AI tools." Hooks/sub-agents running only in Cowork is a component-level limitation, not Claude-Code-only distribution.

## 6. 顺带发现的活 bug（建议单独修）

1. **`archive_to_wiki` 自远程化后即坏**：server 端 `readFile(markdownPath)`（team-context-mcp packages/feishu/src/client.ts:143），但 monthly-health autopilot 让 agent 在本机写 `/tmp/monthly-health-{{date}}.md` 再传路径——Zeabur 容器上不存在该文件。应改为接受 inline markdown content。
2. **`plan_request_review` MCP 工具与 transition.py 双写分歧**：MCP 版只加 `计划-评审中` label 不设 `status=in_review`；standards/labels.md:26 已声明 MCP 写路径 deprecated 但工具仍注册。
3. **health 端点假阳性**：`feishu_ready = typeof ping === "function"` 只检查函数存在，忽略 `ping()` 返回值。
