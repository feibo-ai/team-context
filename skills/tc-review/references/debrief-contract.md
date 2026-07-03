复盘（case）内容契约——五个必写段的定义、门槛、评审收口协议与反模式，动笔前读完。

# 复盘的目的

记录真实发生了什么、学到了什么、什么能带到下一个项目。不是状态报告，不是"然后我们做了 X，又做了 Y"，而是关键判断的因果链。

# 五个必写段（缺一不可）

## 1. Goal（从 plan 原样粘贴）
从 plan 文档（HTML）逐字复制原始目标，不改写、不美化。

## 2. What actually happened（≤ 200 词）
压缩时间线，只留结构上重要的事件。取舍判据：这条信息若不改变下一个人的心智模型，就删。超过 200 词说明在叙事，不在压缩。

## 3. Completion criteria — met or not?
逐条核对 plan 里的完成判据并标注 met / not met，写法与门槛见同目录 completion-criteria-check.md。

## 4. Key judgments（case 存在的理由）
不是"我们做了什么"，是"我们决定了什么、为什么"。每个非显然的决策一条，结构：

- **Judgment:** 一行概括
- **Context:** 当时面对什么选择？
- **Options:** 有哪些备选？
- **Chose:** 选了什么 / 为什么
- **In hindsight:** 事后看对吗？会改什么？
- **"Ancient impossible" check:** 没有 AI Native，这个判断是否不可能成立？

目标 2–5 条。一条都找不到 = 这不是真项目，是任务——写进按周分桶的任务 case，不单开项目 case。
硬门槛（publish 脚本内建校验，违约 exit 1，发不出去）：关键判断 ≥1 条，且该段合计 ≥100 字符、非占位文本。

## 5. General rule candidates
0–3 条候选。每条一句话，须是"可能成为团队 CLAUDE.md 规则"的一般化表述（不带项目名）。DRI 逐条标 `[ ] needs DRI promotion decision`。

### 晋升规则（DRI 手动执行）
判据：这条是否适用于**所有**未来同类项目？
- YES → DRI 晋升到团队全局 CLAUDE.md（claude_md_team_global.md）：
  1. 确认拟晋升的规则文本与本 case「规则候选」段某条**匹配**（防晋升错字/臆造）；
  2. 追加到「## Claude 不能再犯的错」段末，带来源标注 `(来源:case <id> · <project>)`；
  3. 回到 case 把该候选标「已晋升」；
  4. commit。
  该红线文件仅在晋升时碰；CLAUDE.md 的其他改动走月度 review。
- NO → 留在 case 里即可。

经验值：约 10% 的候选会晋升，90% 留在本地。

# 发布与状态流转（指针，不复制契约）

case 以 HTML 作为 issue **评论**发布（append-only），只走 tc-render skill 的 scripts/publish.py；label/status 流转只走 scripts/transition.py，绝不手改。fields.json schema、exit codes、transition 子命令语义，以 tc-render skill 的 references/publish-contract.md 为准，本文件不复制。
发布成功即自动进入待审状态（加复盘待审 label、status 转 in_review）；永不改 issue 附件或描述。

# 评审与收口协议

「第二个 session」= 评审子 agent。case 发布后，当前（编排）session **立即**派评审子 agent：
- 全新上下文，role = DRI 代理 / staff engineer；
- 只给两样输入：case HTML + plan 文档路径；
- 要求重点审第 4 段（关键判断），并输出 `VERDICT: approved | changes-requested`。

**verdict 返回点 = 收口执行点**：拿到 verdict 的编排 session 当场执行，不留"等别人来收尾"的无主窗口。
- approved → 跑 tc-render 的 transition.py `case-finalize <case-issue>`（父 plan 尚有其他阶段在进行时加 `--keep-parent`）。该命令原子收口 case 与父 plan（语义以 tc-render skill 的 references/publish-contract.md 为准），执行后复核 label/status 落位。
- changes-requested → 修订 fields 后用 publish.py 再发一版（append-only），重新派审。

# 反模式

- ❌ 以"没什么值得写"为由跳过第 4 段 → 若真没有，这是任务层，写进周批
- ❌ 第 2 段超 200 词（在叙事，不在压缩）
- ❌ 第 5 段候选带项目名（如"AI hiring 用 X"）——那是 case 特有经验，不是一般规则
- ❌ 不逐条检查就把全部候选标晋升（大多数不该晋升）
- ❌ 评审通过后不当场收口，留无主窗口

# 后续去向

- 项目层 case：周五 demo 展示（真实产物，不是 slides）——见 tc-rhythm skill。
- 任务层周批 case：月度 review 统一过。
