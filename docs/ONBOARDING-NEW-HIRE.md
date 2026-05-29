# 新人入职 · 第一周指南

> **Audience**: 第一次加入 AI MIQ 团队的人
> **Goal**: 5 天后你独立跑通一个 mini 项目，走完 tc-1-start 全流程 + 写出自己的第一个 case file
> **Companion**: 你的角色文档 `onboarding/<role>.md`（DRI / Plan 1-3 EXEC 各一份）

> **v2 (W5+) · control plane edition**: 不需要本地装飞书命令行 · 不需要扫码 · 不需要开 scope · 不需要拿 chat_id。
> 远程 MCP server (`tcmcp-remote` · 云端 Zeabur 跑) 处理一切飞书相关 · 你只需要 multica bearer token + 一份本地 MCP local server。
> 接入时间从 30 min 降到 ~5 min。
> 详见 `decisions/2026-05-29-multica-control-plane.md` · `standards/integration-overview.md`。

---

## Step 0 · DRI 提前做（在你到岗前 30 分钟）

DRI 在你来之前：
- 加你到 GitHub org `feibo-ai`（grant access：`team-context` + `team-context-mcp` + `tc-multica`）
- 加你到 AI MIQ 飞书群 + 拿到你的飞书邮箱
- multica workspace 创建你的 user（DRI 跑 `multica` 后台 / web UI 拉人 · 拿你的 user UUID）
- 选 1 个 starter 跟车项目（Day 2-3 用）+ 1 个 mini project-layer 任务（Day 4-5 用）
- 把欢迎飞书私聊推给你含 5 个链接：本指南 / SOP v0.4 / 快速速查卡 / 你的角色 onboarding / 团队 cases 入口

---

## Day 1 · 上午 90 分钟 · 环境就位

### 09:00–10:30 · 跟 `ONBOARDING-MEMBER.md` 走完 5 步

打开 [`ONBOARDING-MEMBER.md`](./ONBOARDING-MEMBER.md) · 按它走:

| step | 干嘛 | 期望时间 |
|---|---|---|
| Step 0 | brew 装 multica/jq/node | 3 min |
| Step 1 | 连云 multica · `multica auth status` 三行匹配 | 1 min |
| Step 2 | tcmcp-local build · stdio tools/list = 12 | 5 min (含 pnpm install 网络等) |
| Step 3 | sync 12 skill 到 `~/.claude/skills/` | 1 min |
| Step 4a/4b | Codex 或 Claude Code MCP config | 2 min |
| Step 5 | e2e 冒烟 `search_chat` 返 `oc_035c...` | 30 sec |

**前置 (DRI 在你来之前应该已经做的):**
- 飞书 DM 发给你: 你的 email · PAT (`mul_xxx`) · workspace_id (UUID)
- 把你加进 GitHub org `feibo-ai` ·`team-context-mcp` (public · clone OK) ·`team-context` (private · 你**不用**仓库权限 · skill 走 multica API)
- 把你加进 AI MIQ 飞书群 (「Team Context」)

任一前置缺 · 立即飞书 @ DRI · **不要硬扛**。

### 10:30–10:45 · Verify

`ONBOARDING-MEMBER.md` Step 5 那个 e2e 冒烟通过 = 你完毕。再做下面 1 个新人专属检查:

```bash
# 测 SOP skill auto-trigger (Claude Code only · Codex 暂不支持 fuzzy match)
```
新 Claude Code session · 输入 "I want to /clear" → 期望: `tc-handoff` skill 自动激活 (frontmatter description 在「context restart」三字附近 fuzzy match)。

不激活 · `ls ~/.claude/skills/tc-handoff/SKILL.md` 看文件在不在; Claude Code 设置里 skills 功能没禁用。

---

## Day 1 · 下午 3 小时 · 必读

### 13:30–14:30 · SOP v0.4 + 三件套（60 min）

按顺序：
1. `team-context/sop/team_manifesto.md` — 团队 WHY（5 min）
2. `team-context/sop/group_sop_v0.4.html` — 操作 SOP（45 min 浏览器打开看完）
3. `team-context/sop/team_context_constitution.md` — Agent 规则（5 min）

**特别记住**：
- **2 条非妥协**: ① Plan Mode（不许 vibe code）② Debrief（项目结束必写 case）
- **3 条红线**: ❌6 能力前沿外 / ❌8 熟练 dev 在熟悉代码反慢 19% / ❌9 burnout
- **RPI 三阶段**: Research / Plan / Implement 必须是 **discrete sessions**
- **5-10 active baseline**: 不是越多越好 · 50+ 反而崩

### 14:30–15:00 · 角色文档 + 速查卡（30 min）

```bash
# 你的角色（DRI 会告诉你是 DRI / Plan 1-3 EXEC 中哪个）
open /Users/feibo/multica/docs/onboarding/<your-role>.md

# 命令速查 · 8 个 starter 命令 + state machine + 常见错误
open /Users/feibo/multica/docs/quick-reference.md
```

### 15:00–16:30 · 读最近 5 个 case（90 min · 最重要）

```bash
ls -t ~/team-context/cases/ 2>/dev/null | head -10
# 或 跟 DRI 要 3-5 个具体项目 cases 链接
```

**重点读 Section 4「Key judgments」** —— 这是 SOP 的核心：DRI 怎么避免「场面话」、怎么写「ancient impossible check」、哪些判断如果重来会改。读完你脑子里应该有 5 个具体的"古法不可能"事件。

### 16:30–17:00 · Dogfood 工具链

在 Claude Code 新 session 试 5 个 skill 触发：

| 输入 | 期望激活 |
|---|---|
| "I am stuck" | `tc-handoff` |
| "let's plan" | `tc-3-plan` |
| "am I doing this right" | `tc-self-check` |
| "going in circles" | `tc-health-check` |
| "let's debrief" | `tc-5-review` |

跑通后 17:00 飞书报 "Day 1 setup OK, ready for Day 2 shadow"。

---

## Day 2–3 · 跟车 shadow mode（1.5 天）

DRI 让你跟一个正跑的项目当 **COLLAB**（不是 DRI · 不背决策）。3 件事：

### 跟车 1 · 看完整 Phase 01 6 步

DRI 启动一个新项目时拉你旁观（屏幕共享 + 飞书广播）。看：
- 5-min intent 怎么写
- Research session 跟 Plan session 怎么切分
- reviewer 怎么选 + 怎么 verdict
- DRI 怎么拍板

观察重点：**DRI 怎么判断「这是 project layer 还是 task layer」+「这个 reviewer 选他还是另一人」**。

### 跟车 2 · 看一个 Debrief 收尾

找一个本周接近 close 的 issue 旁观 DRI 跑 `case_create` + `case_review`：
- 5 mandatory sections 怎么填
- Section 4 怎么避免「场面话」
- DRI 自己 case_review 签 section 4 是什么感觉

### 跟车 3 · 自己接一个 task-layer 任务

DRI 给你一个 1-3 小时 task-layer 修复（不是 project-layer）。流程：
1. 写 3 句话 mini-plan（task-layer 不强求 full plan markdown）
2. 自己实施
3. 完工写到周合并 case `cases/YYYY-MM-WW-tasks.md`（追加一段）
4. 飞书报一句完成

不需要走 `plan_approve` / `case_review` 全套（task-layer 不需要），但仍要 `git commit + push` + 飞书报。

---

## Day 4–5 · 第一个自己的项目（你当 DRI）

DRI 给你一个 project-layer 任务（3 天 - 1 周 appetite）。**你自己当 DRI**（实习生也可以是 DRI · SOP P-5）。

### 用 `tc-1-start` skill 走完 6 步

在 Claude Code 输入 "I want to start a new project" → 自动激活 `tc-1-start` skill → 按 6 步：

```
Step 1 · 5-min 飞书声明意图
   调 MCP `notify_team` (remote):
     text="I'm thinking about starting [X], because [Y]."
   (这步是「让团队知道」,不是「committing to do it」)
   (chat_id 由 tcmcp-remote 从 multica integration 配置中解析 · 你不需要拿 chat_id)

Step 2 · Research session (fresh Claude Code session)
   调 MCP `research_create`:
     slug=<short-slug>
     question="<one paragraph: what we are trying to understand>"
   写 docs/research/research_YYYY-MM-DD_<slug>.md
   (花 1-3 小时 · 用 subagent 并行调研多维度)

Step 3 · Plan session (yet another fresh session)
   调 MCP `plan_create`:
     slug=<same-slug>
     layer=project
     dri=<your-email>
     goal="<specific verifiable>"
     completionCriteria=["<signal 1>", "<signal 2>"]
     appetite="1 week"

Step 4 · Request review
   调 MCP `plan_request_review`:
     multicaIssueId=<from step 3>
     reviewer=<senior teammate email>
   等 reviewer 在 issue 上 comment "approved" 或 "changes-requested"

Step 5 · DRI 拍板(你自己!)
   调 MCP `plan_approve`:
     multicaIssueId=<id>
     planPath=<path>
     reviewer=<reviewer email>
   (软 gate: 没 reviewer verdict 也能 approve · 但你应该等他)

Step 6 · Broadcast
   调 MCP `project_kickoff` · 返回 broadcastSuggestion (一段建议文案)
   你自己评估 + 调 `notify_team` 推飞书 (含 step 1-5 全部信息)
   或手动飞书发 "Starting [project]. Plan: [link]. DRI: me. Appetite: [X]."
   24h 默认通过窗口 (无人反对就开干)
```

### Implement 阶段（`tc-4-build` skill 守护）

每天遵守：
- 任务前 30s 监督 CoT（chain of thought · Claude 的"心想"）· 方向不对立刻 ESC
- 卡 30 分钟 → 触发 `tc-handoff` skill → 调 `plan_upgrade` (bump v1.x · 强制重新 review) → /clear
- 每天 ≥ 3 次 `git commit + push`
- 见 "You're absolutely right" 立即 /clear（context 浑浊信号）

### Debrief 阶段（`tc-5-review` skill + `case_create` 工具）

完工后：

```
1. 调 MCP `case_create`:
     slug=<same-slug>
     goal=<paste from plan>
     whatHappened="<≤ 200 words compressed timeline>"
     criteriaResults=[{criterion:"...", met:true|false}, ...]
     keyJudgments=[{
       title:"...", context:"...", options:["A","B"],
       chose:"A — reason",
       inHindsight:"...",
       ancientImpossible:"yes/no — explanation"
     }, ...]   # 2-5 个非 obvious decisions
     ruleCandidates=["<0-3 candidates>"]
   写 cases/YYYY-MM-DD-<slug>.md (5 sections 强制)

2. 调 MCP `case_review`:
     casePath=<path from step 1>
     multicaIssueId=<original project issue>
     reviewerEmail=<你自己 · 因为你是 DRI>
   工具会强制 Section 4 ≥ 100 chars (反"场面话")
   通过后自动 addLabel `复盘-已审`

3. close 项目对应的 multica issue
   (`复盘-已审` label 是 close 前置 · 没签字关不掉)

4. 飞书广播 case file 链接给团队 · demo + 庆祝
```

**Day 5 末**：你应该独立走完 tc-1-start 全 6 步 + 一个 case file + Section 4 ≥ 100 字真实成败分析 + DRI（你自己）签字 + close。

---

## 第二周起 · 你算入组成熟

| 时刻 | 自动发生 |
|---|---|
| 每个工作日 18:00 | `daily-summary` autopilot 自动写当日团队 summary 推飞书 · 你 30 秒过目 |
| 周一 09:30 | `monday-kickoff` autopilot 自动汇总本周 计划-已批准 列表 + 飞书 · 你参与 10:00 30-min Monday Kickoff |
| 周三 09:00 | `wednesday-stats` autopilot 跑 skill_lint + CLAUDE.md 周变更 · 你看下 stale skill |
| 周五 15:00 | 30-min Friday Demo · 你来 demo 你的产物 (没 PPT · 是真东西) |
| 周五 15:30 | 15-min Friday Betting Table · 你提案下周做啥 · 5 人投票 |
| 每月 1 号 10:00 | `monthly-health` autopilot 生成月度报告 + 推飞书 · 全员 30 min 解读 |
| 每月末 | `burnout_check_distribute` 匿名 3 问问卷 · 你诚实回 |

---

## 卡住怎么办（升级路径）

| 信号 | 动作 |
|---|---|
| Day 1 setup 卡 30 分钟 | 飞书 @ DRI · **不要硬扛** |
| Day 2-3 跟车看不懂 | 飞书 @ DRI · 让他 5 min 口头讲一遍 |
| Day 4-5 实施卡 30 分钟 | 触发 `tc-handoff` → 调 `plan_upgrade` → /clear · **不要 fix** |
| 同一 issue /clear 3 次 | 升级到 greenfield playbook · re-Research · re-Plan |
| 一周内 /clear 5 次 | 跟 DRI 报 · 可能 burnout 早期信号 |
| 觉得累 | 直接说 · **不等月度 burnout check** |
| 跟 DRI 意见不一致 | 触发 `tc-conflict` skill · 走 4 原则 · 写到 `decisions/` |

---

## 一句话总结

**5 天后你的可见产出：**

- ✅ 4 工具装完 + multica token 拿到 + tcmcp-remote /health 通 + 22 个 MCP 工具齐
- ✅ SOP v0.4 通读 1 遍
- ✅ 5 个 case 读完 (Section 4 重点)
- ✅ 跟车 1 个 Phase 01 + 1 个 Debrief
- ✅ task-layer mini-fix 1 个完工 (跟周 case)
- ✅ project-layer mini-project 1 个走完 tc-1-start 全 6 步
- ✅ 第一个自己的 case file · Section 4 ≥ 100 字真实分析 · DRI（你自己）签字

不需要装啥都懂 · 只需要会走 SOP 的 RPI + Debrief 全流程**一次**。其他靠每周 case 累积。

---

## 给 DRI · 接新人 checklist

| Day | DRI 要做 |
|---|---|
| Day -1 | GitHub org + 飞书群 + multica user + starter project 准备好 |
| Day 1 上午 | 旁站着帮新人过 setup · 4 工具 + token + tcmcp /health · 任一不过立刻一起 debug |
| Day 1 下午 | 16:30 跟新人 15 min sync · 看 dogfood 5 skill 测试是否过 |
| Day 2 上午 | 让新人跟车看你启动一个新项目（Phase 01 6 步） |
| Day 2 下午 | 给新人 1 个 task-layer 任务 · 看他写 3 句 mini-plan |
| Day 3 | 让新人跟车看你跑一个 Debrief（5 sections + case_review）· 让新人完成 task-layer 任务收尾 |
| Day 4 | 给新人 1 个 project-layer mini-project · DRI 是新人自己 · 你当 reviewer 不当 DRI |
| Day 4 末 | 在 plan_request_review 后给新人 verdict · 看他 Section 1-4 写得对不对 |
| Day 5 | 让新人跑完全流程 · 你只在 plan_approve / case_review 两个 gate 时出现 |
| Day 5 末 | 跟新人 30 min 复盘第一周 · 写一条 case file（关于"接新人"这件事 · 提升候选） |

---

**本文件版本**: v0.1 · 2026-05-28 · 接住第一个新人后写 case 修订
**Owner**: DRI
**Last reviewed**: 2026-05-28
