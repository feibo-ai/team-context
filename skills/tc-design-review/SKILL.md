---
name: tc-design-review
description: "Use between plan approval and build start — 设计评审门(SOP 三道评审门之②,①计划批准 ③代码评审)。Triggers: '设计评审', 'design review', plan 刚被 plan-approve 且为项目层, '方案过一下', tc-3-plan 批准后/tc-4-build 开工前的交叉引用指到这里。把『方案定下、写码前』的设计评审收口成与 plan/case 同构的转换边:transition.py design-request-review(+设计-待审 · in_review)→ 设计评审子 agent 出 verdict → 编排 session 当场 design-approve(+设计-已审 · todo)。项目层必走、任务层可跳。MVP 设计载体 = plan approach 段或 issue 评论,不新增 doc 类型。"
owner: 曾振华
last_reviewed_at: 2026-06-10
---

# 设计评审门 — plan-approve 之后 · build-start 之前

## 何时走这道门
- **项目层:必走**(与「计划评审项目层必走」对齐)。tc-4-build pre-flight 会查 `设计-已审`。
- **任务层:可跳**——plan-approve 后直接 build-start 合法,巡检不报。
- 时点:`plan-approve`(计划-已批准 · todo)之后、`build-start`(in_progress)之前;
  挂**同一个 work issue**,不建新 issue、不新增 doc 类型。

> ⚠️ 机制盲区(如实声明):「从未请审就开工」只能靠本 pre-flight 纪律拦截——
> issue 数据无 layer 字段,巡检无法区分项目/任务层,做成不变量会对任务层合法跳过持续误报。
> 巡检能抓的是:评审中开工(build-start 对 `设计-待审` 在场告警)、评审挂起(staleness >48h)。

## 设计载体(MVP · 纯流转)
方案写在 **plan 的 approach 段**(批准后实质改方案 → 先 `plan-upgrade` 重走计划评审),
或一条 **issue 评论**(增补型设计细化)。若将来需要独立设计稿(publish.py `--type design`),
另开一期——本门只管 label/status 流转。

## 三步(编排 session 执行)

### 1 · 请审转换
```bash
python3 ~/.claude/skills/tc-render/transition.py design-request-review <work-issue>
```
原子做完:+`设计-待审` · **摘在场 `设计-已审`(复审作废旧批准,堵不变量 #8)** · status `in_review`。
与 `计划-已批准` 共存(不变量 #4 的 carve-out 由巡检承认)。

### 2 · 派设计评审子 agent(「第二个 session」)
全新上下文 = 天然独立;role = staff engineer。只给:设计载体(plan HTML / 评论 URL)+
相关 research。**不带实现方对话记忆**。要求输出:
- `VERDICT: approved | changes-requested`
- BLOCKING / NON-BLOCKING 清单(架构取舍、与现有系统的兼容、风险盲区)
- 事实核查清单(声称 vs 它实际验证)

子 agent 只产出 verdict、**不碰状态**;转换权始终归编排 session。

### 3 · verdict 返回点 = 转换执行点(当场跑,不留无主窗口)
- approved →
  ```bash
  python3 ~/.claude/skills/tc-render/transition.py design-approve <work-issue>
  ```
  (+`设计-已审` · −`设计-待审` · status `todo` 回待启动)→ 接 tc-4-build `build-start`。
- changes-requested → 修订设计(plan approach 实质变更走 `plan-upgrade` 重审计划;
  评论级细化直接补评论)→ 回第 2 步重审。

## 补审场景(issue 已在建,两连勿断)
对已 `in_progress` 的 issue 补走设计评审:request-review 会把 status 拉到 `in_review`,
approve 回 `todo`——**verdict 后必须 `design-approve` → `build-start` 两连**,
把 status 送回 `in_progress`,否则 issue 滞留 `todo` 呈「待启动」假象。

## Anti-patterns
- ❌ 子 agent 直接跑 design-approve(转换权归编排 session)
- ❌ 设计评审中(`设计-待审` 在场)硬开工(build-start 会告警;项目层这是违纪)
- ❌ 给带 `设计-已审` 的 issue 手动再贴 `设计-待审`(走 design-request-review,它会原子换签)
- ❌ 为设计稿新建 issue 或塞 issue 描述(载体=plan approach 段/评论,append-only)
