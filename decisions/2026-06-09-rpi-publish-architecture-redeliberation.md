# Decision · RPI 文档发布架构再审议 — Phase 1 轻量收敛 + Phase 2 下沉(条件触发)

**Date**: 2026-06-09
**DRI**: feibo
**Status**: decided(Phase 1 = plan-of-record · Phase 2 = deferred / 条件触发)
**Builds on**: `2026-06-08-drop-local-mcp.md`(迁移本身不推翻;本决策细化其遗留缺口的收敛路径)
**Issue**: team-iteration-sync 系列(TEA-79/84)

## Context

「去本地MCP」迁移交付并端到端验证可用后,启动一轮 **5-agent 黑/白盒评审**,揪出真问题(分数:Go 代码 7/10、publish.py 6.5/10、架构 5/10、red-team 6.5/10、UX 截断但 happy-path 通):

- 命门A 焊死服务端**私有 HTTP 契约**(无文档,会变);
- **双命门** publish.py(Python)/`--inline`(Go)两套发布逻辑,且仓里实为 **4 份命门A 实现**,权威其实是前端正则 `file-cards.ts:NEW_FILE_CARD_RE`;
- registry 分发**有损**(`buildSkillMd` pull 丢 owner → 自伤 lint)+ 双写**无 CI 同步**;
- 校验只在 publish.py,`tc-handoff/SKILL.md:59` 开了「快捷 markdown」**绕过口** → "强制"降"推荐";`<60s` 幂等门退化成 prose;
- fields **无 schema**,拼错 key 静默吞;
- 版本门槛(v0.4.11/12/13)散落 **无 preflight**;
- Codex 侧只一行 prose 指针,**两端不对称**;
- red-team 实测:**`--out`/slug 路径穿越越权写**、case「≥100字」质量闸可空格/重复占位**绕过**、`completionCriteria="字符串"` 类型混淆过 min(1)、坏 JSON/缺 config **裸 traceback 泄露路径**。
- 核心防线(XSS 实体转义、命令注入隔离、UUID 校验、CSP、发布失败不留脏评论)**全守住**。

DRI 决定:战术 bug 暂不逐个修,**全面重议架构**。派 3 个独立架构师(无原设计偏见)各持一立场:A 演进不拆库 / B Go 单核拆库 / C 第一性原理(服务端下沉)。

## 关键发现:三家独立收敛

三家先验不同(防守现状 / 拆库 / 服务端),却一致得出 ——
**现在做「不拆库轻量收敛」,把"核心下沉到哪"的重决策推迟到触发条件成熟。**

| 架构师 | 出发立场 | 终态自评 | 对"现在做什么"的结论 |
|---|---|---|---|
| A 演进派 | 不拆库 | 8.5 | 轻量收敛(其全部方案) |
| B 拆库派 | Go 单核 | 单核 6.5 → **补丁 8** | **先上补丁,单核留 Phase 2** |
| C 第一性原理 | 服务端 | server 7 → **CLI 次优 8** | 服务端 gate 在"部署丝滑",否则收口 CLI |

### 三终态对比(分歧仅在终态)

| 维度 | 客户端脚本(收敛后) | Go CLI 单核 | 服务端下沉 |
|---|---|---|---|
| 校验不可绕过 | ⚠️ 收口后较强 | ⚠️ 可绕 CLI 打裸 API | ✅ 物理不可绕 |
| 零漂移 | ⚠️ registry 需治 | ✅ 单二进制 | ✅ 客户端不持有 |
| 跨端对称 | ✅ 同调一入口 | ✅ 同子命令 | ✅ 同端点 |
| 版本无关(服务端任意版本) | ✅ | ✅ | ❌ server 版=全员耦合 |
| 改文案摩擦 | ✅ 改脚本即生效 | ⚠️ 发 CLI 版 | ⚠️ 走部署 |
| 离线自治 | ✅ | ✅ | ❌ 需在线 |
| fork-debt | ✅ 无 | ⚠️ 核心进 CLI | ❌ RPI 焊进 server |
| 5 人运维负担 | ⚠️ 脚本+sync | ✅ multica update | ❌ server 运维+部署 |

- **C 的核心洞见**:校验必须在**不可绕过的层 = API 入口**;客户端一切皆可绕。团队**掌控全栈 fork**,服务端非天堑。
- **B/C 的诚实反制**:服务端/单核把"改文案"重新绑回**发版/部署**——正是去本地MCP 要摆脱的;对 5 人低频团队摩擦真实 + **fork-debt**(违 "minimize fork debt")。

## Decision

### Phase 1(plan-of-record · 现在做)「不拆库轻量收敛」

零结构性成本,解 8 问中 5–6 条,且**不 foreclose 任何 Phase 2 终态**:

1. **收口单命门**:publish.py 内部 exec `multica issue comment add --inline`;删 `PUBLISH.md §2` 手跑兜底 + 命门A 降**契约化灾备**(写 `publish-contract-v1.yaml`,对齐前端权威正则 `file-cards.ts:NEW_FILE_CARD_RE` + CI 探针)。
2. **fields JSON Schema**(`additionalProperties:false` + `required`):消静默吞;**阈值从 schema 的 minLength/minItems 派生**(消散落魔数);计数前折叠空白(堵 red-team 的质量闸空格绕过 + 类型断言堵类型混淆)。
3. **删 `tc-handoff` 「快捷 markdown」绕过口** → 四类文档无旁路,校验回"强制"。
4. **修分发**:`buildSkillMd` 补 owner + `sync-team-config.sh` 改 create-or-**update** + 推 `files[]` + CI 加 repo→registry 对账;registry 降为**派生只读投影**,开发机走 git 软链(实测 pull 有损)。
5. **`multica doctor` preflight**:收散落版本门槛成一个发布前硬门。
6. **Codex 对称**:同一可执行入口(收口后两端都 `Bash` 调同一命令);生成 Codex skills-index。
7. **(并入 red-team 致命项)** `--out`/slug 路径白名单 + 仓内断言(堵越权写);裸 traceback → 友好 `ERROR + exit 1`;token 移出 argv;`--inline` MIME 校验。

### Phase 2(deferred · 条件触发)「核心下沉」

- **触发条件**:命门契约进入高频变更 / 团队 ≥ 15 人 / 需 authz·审计·多 workspace 并发写。
- **届时二选一**:Go CLI 单核(B · 同仓同 release)或 服务端下沉(C · 需"部署丝滑"先行)。**现在不拍**——无信息优势,Phase 1 做完会让此判断更有依据。

## Consequences

- ✅ 高频痛点(校验可绕 / 静默吞 / 分发有损 / 版本散落 / 越权写)**零结构性成本堵掉**,已交付资产(publish.py / 命门B / registry)**留用**。
- ✅ Phase 1 覆盖了 5-agent panel 战术 bug 的大半;做完为 Phase 2 决策(团队更怕"漂移/可绕"还是"重/慢/单点")提供实测依据。
- ⚠️ Phase 1 仍是**客户端校验** —— 命门A 私有契约的结构性脆弱用"契约文件 + CI 探针"**缓解,非根除**(根除需 Phase 2 下沉)。
- ⚠️ `buildSkillMd` 补 owner 需改 **CLI(Go 仓)**,是 Phase 1 唯一越过"纯 skill 侧"的改动。
- 📌 Phase 1 需走正式 **Plan(tc-3-plan)+ 第二 session 评审**后才实现(SOP 不可妥协 #1 · 不 vibe code)。

## 备选与未采纳

- **立即拆 Go 单核 / 立即服务端下沉**:B/C 均自评"现在性价比存疑",发版/部署摩擦 + fork-debt 对 5 人低频团队不划算 → 推迟为 Phase 2 条件触发。
- **维持现状不收敛**:panel 已证校验可绕 + 越权写 + 分发有损是真风险 → 否决。

## 证据来源

5-agent 评审报告 + 3 架构师方案(session 2026-06-09)。关键实测:`multica skill pull` 重建 frontmatter 丢 owner/last_reviewed_at(问题④根因);命门A 序列仓内 4 份实现,权威为前端 `packages/ui/markdown/file-cards.ts:NEW_FILE_CARD_RE`;red-team `--out ../../../x` 越权写成功 + case ≥100字空格绕过成功。
