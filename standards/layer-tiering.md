# 项目层 / 任务层 分层判定规则

**Owner**: DRI
**Last reviewed**: 2026-06-24
**Source of truth**: 本文件 · 改判定规则或 proxy 定义必须更新这里 + 开 PR
**适用**: 所有要起 issue 的团队工作——决定一个 issue 该走【项目层】全流程,还是【任务层】轻量放行。

团队 SOP 把工作分两层:项目层走全流程(plan HTML 文档 + 评审门 + label 状态机),任务层放行轻量(3 句 mini-plan 自批)。此前没有成文判定规则,导致全队不知道什么时候该走全流程。本文件把判定收口成一条人工规则 + 一组机读度量代理。

## 判定规则(DRI 2026-06-24 拍板 · 多触发器任一)

一个 issue 满足以下**任一**触发器,即判为【项目层】,走全流程:

1. 写 / 改代码或配置,且会合进 `main`;
2. 需跨 session 或跨人交接;
3. 对外,或影响他人产出;
4. 预计耗时 > 半天。

四条触发器是**或**关系,命中任一即升项目层。**都不命中**才落【任务层】,走轻量。拿不准就当项目层处理(宁严勿松)。

## 两层各自做什么

### 项目层 = 全流程

按 RPI + SOP 三道门走完整链路,全程 label/status 状态机由 `skills/tc-render/transition.py` 驱动:

1. `tc-3-plan` 出 plan HTML 文档(4 个 SOP 必填字段:目标 / 完成标准 / 分工 / appetite);
2. **计划评审门**——派第二个 session(子 agent)评审,通过后 plan-approve;
3. **设计评审门(项目层必走)**——走 `tc-design-review`,定方案、写码前的转换边;
4. `tc-4-build` 实现;
5. `tc-5-review` 出 case HTML 收尾(5 个必填段落)。

状态机细节见 `standards/labels.md`(label 字典 + 双轨 state machine + 不变量),不在此重复。

### 任务层 = 轻量

3 句 mini-plan **自批即可**(无需第二个 session 评审门),执行**派子 agent**。编排 session 只握审 diff / 转换 / commit 的裁量权;子 agent 只产出工作产物、不碰状态、不 commit。

任务层惯例引用既有沉淀(`tc-3-plan` 的 mini-plan 分支、MEMORY「Task-layer: mini-plan + subagent exec」),此处不重复细节。任务层不强制 plan HTML、不强制评审门、可不挂流程 label(零 label 轻任务不在 issue_invariants 审计内,见 labels.md 不变量章)。

## 机读 project-ish proxy(度量代理 · ≠ 人工判定规则)

人工四触发器里有三条(②跨交接 / ③影响他人 / ④> 半天)**无法从 issue 字段机读**。所以另设一组**过近似**代理,只用于**度量与 nudge 命中**(覆盖率统计、提醒该走全流程没走的 issue),**不替代上面的人工判定**。

一个 issue 命中以下**任一**即纳入度量分母(project-ish):

- **(a) 标题前缀** `计划:` / `研究:` / `复盘:`(半角 `:` 与全角 `：` 冒号都认);
- **(b) description 长度** > 600 字;
- **(c) description 含 Markdown 标题**——正则 `^#{1,4}\s`;
- **(d) description / 字段含 GitHub PR/repo 链接**——含 `github.com`,或 `/pull/`,或 `/issues/`。

设计取向是 **recall 导向的过近似**(宁多抓不漏报):因为人工四触发器里 ②/③/④ 无法从 issue 字段机读,proxy 只能从标题、描述、链接这些可读信号近似,必然抓多。它只用于度量与 nudge 命中,**不是人工判定规则**——是否真要走全流程,仍以上面的四触发器人工判定为准。

已验 `multica issue list --output json` 返回 `description` 字段,proxy 的 (b)(c)(d) 可直接机读。

**2026-06-24 实测基线**(`issue_invariants.py` 全工作区跑出的可复现口径):proxy 命中 560 个疑似项目层 issue,已挂入口 label(流程 label ∪ `研究`)的仅 86 个 = **覆盖率 15.4%**。最大漏采用子群荣灿单人口径更低(458 命中 / 18 采用 ≈ 4%)。即绝大多数被 proxy 抓到的 issue 尚未进入流程状态机,nudge 有发力空间。

## 来源

plan TEA-1022(Multica 迭代项目)步骤3——分层判定规则落档。
