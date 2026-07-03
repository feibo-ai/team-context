# design-review-flow

设计评审门的完整流程：时点与层级判据、设计载体、三步转换、changes-requested 循环、补审场景与机制盲区。

## 时点与层级
- 时点：plan 批准（plan-approve）之后、build 开工（build-start）之前；挂**同一个 work issue**，不建新 issue、不新增 doc 类型。
- **项目层：必走**（与「计划评审项目层必走」对齐）。tc-build skill 的 pre-flight 会检查 `设计-已审` 在场。
- **任务层：可跳**——plan-approve 后直接 build-start 合法，巡检不报。

## 机制盲区（如实声明）
「从未请审就开工」只能靠 pre-flight 纪律拦截——issue 数据无 layer 字段，巡检无法区分项目/任务层，做成硬性不变量会对任务层的合法跳过持续误报。巡检能抓的是：

- 评审中开工：build-start 时 `设计-待审` 在场 → 告警；
- 评审挂起：staleness > 48h。

## 设计载体（纯流转，不新增 doc 类型）
- 方案写在 **plan 的 approach 段**；批准后实质改方案 → 先走 plan-upgrade 重走计划评审（INVOKE tc-plan skill）。
- 或一条 **issue 评论**（增补型设计细化，append-only）。
- 若将来需要独立设计稿（publish.py 的 `--type design`），另开一期——本门只管评审与 label/status 流转。

## 三步流程（编排 session 执行）

### 1 · 请审转换
```bash
python3 <skills-root>/tc-render/scripts/transition.py design-request-review <work-issue>
```
原子完成请审：加 `设计-待审`、**摘除在场的 `设计-已审`（复审作废旧批准）**、status 进 `in_review`；与 `计划-已批准` 共存是被承认的例外。精确的 label/status 状态机语义以 tc-render skill 的 references/issue-label-state-rules.md 为准，本文件不复制。

### 2 · 派设计评审子 agent（「第二个 session」）
全新上下文 = 天然独立；role = staff engineer。只给：设计载体（plan HTML / 评论 URL）+ 相关 research。**不带实现方对话记忆**。输出契约见本 skill 的 references/review-verdict-template.md。

子 agent 只产出 verdict、**不碰状态**；转换权始终归编排 session。

### 3 · verdict 返回点 = 转换执行点（当场跑，不留无主窗口）
- **approved** →
  ```bash
  python3 <skills-root>/tc-render/scripts/transition.py design-approve <work-issue>
  ```
  （加 `设计-已审`、摘 `设计-待审`、status 回 `todo` 待启动）→ 接 tc-build skill 的 build-start。
- **changes-requested** → 修订设计：plan approach 段实质变更走 plan-upgrade 重审计划（INVOKE tc-plan skill）；评论级细化直接补评论 → 回第 2 步重审。

## 补审场景（issue 已在建，两连勿断）
对已 `in_progress` 的 issue 补走设计评审：design-request-review 会把 status 拉到 `in_review`，design-approve 回 `todo`——**verdict 后必须 `design-approve` → `build-start` 两连**，把 status 送回 `in_progress`，否则 issue 滞留 `todo` 呈「待启动」假象。

## Anti-patterns
- ❌ 子 agent 直接跑 design-approve（转换权归编排 session）。
- ❌ 设计评审中（`设计-待审` 在场）硬开工——build-start 会被巡检告警；项目层属违纪。
- ❌ 给带 `设计-已审` 的 issue 手动再贴 `设计-待审`——走 design-request-review，它会原子换签。
- ❌ 为设计稿新建 issue 或改写 issue 描述（载体 = plan approach 段 / 评论，append-only）。
