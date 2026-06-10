# 新人入职 · 第一周指南

> **Audience**: 第一次加入 AI MIQ 团队的人
> **Goal**: 5 天后你独立跑通一个 mini 项目，走完 tc-1-start 全流程 + 写出自己的第一个 case file
> **Companion**: 你的角色文档（DRI / Plan 1-3 EXEC 各一份）—— 由 DRI 在欢迎私聊里把链接发给你（别去找本地路径,新人机器上没有）

> **v2 (W5+) · control plane edition**: 不需要本地装飞书命令行 · 不需要扫码 · 不需要开 scope · 不需要拿 chat_id。
> 远程 MCP server (`tcmcp-remote` · 云端 Zeabur 跑) 处理一切飞书相关 · 你只需要 multica bearer token + 远程 MCP。
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
| Step 0 | brew 装 jq/node · install.sh 装 multica(别 brew 装 multica) | 3 min |
| Step 1 | 连云 multica · `multica auth status` 三行匹配 | 1 min |
| Step 2 | `multica skill pull --all` 同步 skill(含脚本)+ 接入 remote MCP | 2 min |
| Step 3 | sync 12 skill 到 `~/.claude/skills/` | 1 min |
| Step 4a/4b | Codex 或 Claude Code MCP config | 2 min |
| Step 5 | e2e 冒烟 `search_chat` 返 `oc_035c...` | 30 sec |

**前置 (DRI 在你来之前应该已经做的):**
- 飞书 DM 发给你: workspace_id (UUID `fb23cf99-5f4c-4815-b2b3-8d5e323659f6` · slug `team-context`) + 群邀请 + 文档链接 —— **token 你自己 `multica login` 拿**(per-user · DRI 不发 token;DRI 侧只是 `multica user create` 把你加进 workspace。详见 MEMBER.md Step 1)
  - 域名(写进 `ONBOARDING-MEMBER.md` 的环境变量): web `https://teamctx.actionow.ai` · API `https://api.teamctx.actionow.ai` · remote MCP `https://mcp.teamctx.actionow.ai/mcp`
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

- **你的角色文档**（DRI 会告诉你是 DRI / Plan 1-3 EXEC 中哪个）：DRI 在欢迎私聊里把对应角色文档链接发给你 —— 这些文件在 DRI 机器上,新人本地没有,别自己拼路径。
- **命令速查卡**（8 个 starter 命令 + state machine + 常见错误）：同样由 DRI 提供链接。

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

找一个本周接近 close 的 issue 旁观 DRI 跑 `tc-5-review`+publish.py + `tc-5-review`收尾(`multica issue label/status`)：
- 5 mandatory sections 怎么填
- Section 4 怎么避免「场面话」
- DRI 自己做复盘评审(tc-5-review)签 section 4 是什么感觉

### 跟车 3 · 自己接一个 task-layer 任务

DRI 给你一个 1-3 小时 task-layer 修复（不是 project-layer）。流程：
1. 写 3 句话 mini-plan（task-layer 不强求 full plan doc）
2. 自己实施
3. 完工写到周合并 case `cases/YYYY-MM-WW-tasks.html`（追加一段）
4. 飞书报一句完成

不需要走 批准转换(`multica issue label/status`) / `tc-5-review`收尾(`multica issue label/status`) 全套（task-layer 不需要），但仍要 `git commit + push` + 飞书报。

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
   先 `multica project list` 选定项目 · 触发 `tc-2-research` skill · 它调 publish.py:
     projectId=<选定项目 id · 必填 · 拿不准问 DRI>
     slug=<short-slug>
     question="<one paragraph: what we are trying to understand>"
   tc-2-research 建研究 issue(`multica issue create`)+ 本地骨架,经 publish.py --type research(**填充后才发**)·
   发现填好后用 **tc-render skill 的 publish.py**(命门B 收口 · 内部 exec `comment add --inline`) 发为研究 issue 的**评论**(方案A · `!file` 内联渲染)
   (花 1-3 小时 · 用 subagent 并行调研多维度)

Step 3 · Plan session (yet another fresh session)
   触发 `tc-3-plan` skill · 读 research .html 当输入 · 它调 publish.py:
     projectId=<同上项目 id · 必填>
     slug=<same-slug>
     layer=project
     dri=<your-email>
     goal="<specific verifiable>"
     completionCriteria=["<signal 1>", "<signal 2>"]
     appetite="1 week"
   产出 docs/plans/plan_YYYY-MM-DD_<slug>.html(方案A · 4 必填字段)· 以**评论**形式发到计划 issue(`!file` 内联)· 加 `计划-草稿` label

Step 4 · Request review
   跑 `multica issue label add ... 计划-评审中`:
     multicaIssueId=<from step 3>
     reviewer=<senior teammate email>
   计划 issue label: 计划-草稿 → 计划-评审中
   等 reviewer 在 issue 上 comment "approved" 或 "changes-requested"

Step 5 · DRI 拍板(你自己!)
   跑 批准转换(`multica issue label/status`):
     multicaIssueId=<id>
     planPath=<path>
     reviewer=<reviewer email>
   计划 issue label: 计划-评审中 → 计划-已批准 (SOP 非妥协 #1 gate)
   (软 gate: 没 reviewer verdict 也能 approve · 但你应该等他)

Step 6 · Broadcast
   触发 `tc-1-start` skill · 它会一次性建:
     - 1 个 project
     - 2 个 issue:研究 issue(打 `研究` label)+ 计划 issue(打 `计划-草稿` label · 引用研究 issue)
     - 2 个空 stub 文件(research_YYYY-MM-DD_<slug>.html + plan_YYYY-MM-DD_<slug>.html)
   ⚠️ kickoff 只搭脚手架 —— 不跑深度 research · 不自动发广播 · 只返回 broadcastSuggestion (一段建议文案)
   你自己评估 broadcastSuggestion + 调 `notify_team` 推飞书 (含 step 1-5 全部信息)
   或手动飞书发 "Starting [project]. Plan: [link]. DRI: me. Appetite: [X]."
   24h 默认通过窗口 (无人反对就开干)
```

> **kickoff 跟 Step 2 的关系**:`tc-1-start` 是「快捷脚手架」—— 一条命令把 project + 研究 issue + 计划 issue + 空文件全建好。但它建的研究 issue 只是空壳,**深度 research 仍要另开一个 fresh session 去做**(填 research .html 那 1-3 小时的活,见 Step 2)。
> 跟 Step 2 的 `tc-2-research`+publish.py 二选一:① 要么 Step 2 单独 `tc-2-research`+publish.py 建研究 issue + Step 3 `tc-3-plan`+publish.py 建计划 issue(手动分步);② 要么直接用 `tc-1-start` 一把建齐(脚手架),再回到 fresh session 补深度 research。**别两条路都走**,否则会建出重复的研究 issue。
> ⚠️ `tc-1-start` 返回 success ≠ 做对了 —— kickoff 后按 SOP P-7 真验证产物(issue 真挂到 project?研究 issue 真在?飞书真收到 Step 1/6 广播?)。2026-05-29 实测这三处都曾静默失败。

### Implement 阶段（`tc-4-build` skill 守护）

每天遵守：
- 任务前 30s 监督 CoT（chain of thought · Claude 的"心想"）· 方向不对立刻 ESC
- 卡 30 分钟 → 触发 `tc-handoff` skill → 调 publish.py 再发新评论 (bump v1.x · label → `计划-已升级` + 重新挂 `计划-草稿` · 强制重新 review) → /clear
- 每天 ≥ 3 次 `git commit + push`
- 见 "You're absolutely right" 立即 /clear（context 浑浊信号）

### Debrief 阶段（`tc-5-review` skill + `tc-5-review`+publish.py 工具）

完工后：

```
1. 触发 `tc-5-review` skill · 它调 publish.py:
     projectId=<项目 id · 必填>
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
   产出 cases/YYYY-MM-DD-<slug>.html(方案A · 5 sections 强制)· 以**评论**形式发到 case issue(`!file` 内联)
   (tc-5-review 经 publish.py 发 case;`multica issue label add 复盘-待审`)

2. 跑 收尾(`multica issue label/status`):
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
| 周三 09:00 | `wednesday-stats` autopilot 跑 `multica skill lint` + CLAUDE.md 周变更 · 你看下 stale skill |
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
| Day 4-5 实施卡 30 分钟 | 触发 `tc-handoff` → 调 publish.py 再发新评论 → /clear · **不要 fix** |
| 同一 issue /clear 3 次 | 升级到 greenfield playbook · re-Research · re-Plan |
| 一周内 /clear 5 次 | 跟 DRI 报 · 可能 burnout 早期信号 |
| 觉得累 | 直接说 · **不等月度 burnout check** |
| 跟 DRI 意见不一致 | 触发 `tc-conflict` skill · 走 4 原则 · 写到 `decisions/` |

---

## 一句话总结

**5 天后你的可见产出：**

- ✅ `multica skill pull --all` 同步 skill + `multica login` 拿到自己的 token + tcmcp-remote /health 通 + 10 个 remote MCP 工具齐(local RPI 流走 skills/CLI,不依赖 local MCP)
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
| Day 3 | 让新人跟车看你跑一个 Debrief（5 sections + 复盘评审收尾）· 让新人完成 task-layer 任务收尾 |
| Day 4 | 给新人 1 个 project-layer mini-project · DRI 是新人自己 · 你当 reviewer 不当 DRI |
| Day 4 末 | 在 plan_request_review 后给新人 verdict · 看他 Section 1-4 写得对不对 |
| Day 5 | 让新人跑完全流程 · 你只在 plan 批准 / 复盘评审 两个 gate 时出现 |
| Day 5 末 | 跟新人 30 min 复盘第一周 · 写一条 case file（关于"接新人"这件事 · 提升候选） |

---

**本文件版本**: v0.4 · 2026-06-10 · 同步 self-login 认证 + workspace UUID `fb23cf99…` + teamctx.actionow.ai 域名 + SOP 中间产物**评论制发布**(tc-render skill 的 publish.py · 命门B 收口 · 内部 exec `comment add --inline` · `!file` 内联)+ `projectId` 必填 + **去本地 MCP**:RPI 四类文档流改走 tc-* skills + multica CLI + publish.py · 唯一保留 10 个 remote MCP 工具(`tcmcp-remote`) + 5 autopilot · 接住第一个新人后写 case 再修订
**Owner**: DRI
**Last reviewed**: 2026-06-10
