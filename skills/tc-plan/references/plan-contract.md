用途：plan 的 4 个必填字段、发布与状态转换的调用点（契约真相在 tc-render），以及「评审通过前不许写码」的评审门。

# Plan 契约

## 4 个必填字段

### 1. Goal（目标）
Specific, verifiable. Not "do better".
- ✅ "Reduce p99 latency on /api/feed from 800ms to <400ms"
- ❌ "Make the feed faster"

### 2. Completion criteria（完成标准）
Observable signals, not "done when good".
- ✅ "Three consecutive prod runs show p99 <400ms for 24h"
- ❌ "Performance is acceptable"

### 3. How to split（谁做什么）
- 项目层：DRI + EXEC 名单 + COLLAB 邀请 + REVIEW 指派（角色定义与分配规则见 references/role-assignment.md）
- 任务层：就是你自己（默认 DRI）

### 4. Time box（appetite — Shape Up 式）
- 项目层：days / week / month（投入上限，不是工期估算）
- 任务层：小时数

## 发布（唯一路径 = tc-render publish 脚本）
- 发布只走 `python3 <skills-root>/tc-render/scripts/publish.py --type plan --data fields.json --issue <完整UUID> …`。fields.json schema、硬校验阈值、exit code 语义与补救、入口状态转换：唯一真相见 tc-render skill 的 references/publish-contract.md，本文件不复述。
- 选项目：projectId 用完整 UUID（8 位短 ID 报 400）；没有合适项目 → 问用户是否 `multica project create` 新建；绝不建无项目的孤儿 issue。
- 字段默认值配方见 tc-render skill 的 references/multica-fields.md（`dri` 与 assignee 一样填当前用户，运行时解析，绝不硬编码人名/UUID）；label/status 状态机见 tc-render skill 的 references/issue-label-state-rules.md。

## 评审门（non-negotiable）
写任何代码之前，plan 必须由第二个 session（role = staff engineer）评审。绝不允许写 plan 的 session 自己执行这个 plan。

「第二个 session」= 评审子 agent（团队成员人手大量 agent，这是默认形态）：
1. **请审转换**（plan 写完、派评审之前）：
   `python3 <skills-root>/tc-render/scripts/transition.py plan-request-review <plan-issue>`
   （任务层 plan 同样适用；label/status 变化见 tc-render skill 的 references/publish-contract.md）
2. **派评审子 agent**（全新上下文 = 天然满足独立性）：role = staff engineer，只给 plan HTML 路径 + research 输入，不带实现方对话记忆；要求输出 `VERDICT: approved | changes-requested` + blocking/non-blocking 清单 + 事实核查。
3. **verdict 返回点 = 转换执行点**（编排 session 立即执行，不留无主窗口）：
   - approved → 走下方「批准状态转换」；
   - changes-requested → 修订后用 publish.py 再发一版（append-only），回到第 2 步。
   子 agent 只产出 verdict、不碰状态；转换权始终归编排 session。

- 项目层 plan：REVIEW agent 的明确批准写进 plan 的 "## Review" 段。
- 任务层 plan：3 句 mini-plan 可自批，但写码前必须明说（执行方式见 references/task-vs-project-plan.md）。

## 批准状态转换
approved verdict 返回后立即执行：
```bash
python3 <skills-root>/tc-render/scripts/transition.py plan-approve <plan-issue>
```
label/status 语义、幂等与后置复核见 tc-render skill 的 references/publish-contract.md，本文件不复述。

**批准 ≠ 开工**：`in_progress` 由 build session 开工时经 `transition.py build-start` 设置（见 tc-build skill）——每日 kickoff 的「待启动」桶（`计划-已批准`+`todo`）依赖此语义。

Reviewer / Verdict 写进 plan 的 approach/评审字段，用 publish.py `--type plan` 再发一版（append-only）。

## 已批准后的实质修改
先 `python3 <skills-root>/tc-render/scripts/transition.py plan-upgrade <plan-issue>`（语义见 tc-render skill 的 references/publish-contract.md），再重走评审门。

## 三道评审门
①计划批准（本 skill）→ ②设计评审（INVOKE tc-design-review skill：`design-request-review` → 设计评审子 agent → `design-approve`；项目层必走、任务层可跳）→ ③代码评审（build 阶段）。通过设计评审后才到 tc-build `build-start`。

## Hand-off to Implement
plan 已评审批准（项目层再过设计评审）→ INVOKE tc-handoff skill → `/clear` → 开 Implement session，以 plan HTML 为主要输入。
