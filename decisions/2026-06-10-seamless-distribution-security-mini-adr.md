# 安全设计 mini-ADR：无感分发与自更 provenance 信任根（⑨ + ⑩）

- **状态**：DRAFT — 待独立安全评审。**评审通过前不得 code**（SOP「绝不同 session 既写又审」、plan TEA-89 ⑩ 硬门）。
- **日期**：2026-06-10
- **作者**：feibo（DRI）+ Claude（设计）
- **关联**：TEA-89 v4 plan ⑨⑩；`decisions/2026-06-09-rpi-publish-architecture-redeliberation.md`；`decisions/2026-06-08-drop-local-mcp.md`
- **范围**：tc-multica daemon 自更（⑨ 二进制 provenance）+ 无感 skill 分发（⑩ daemon 写 `~/.claude/skills`）。两者**共享同一签名信任根**,故合并一份 mini-ADR。

---

## 1 · 背景与问题

去本地 MCP 后,团队要把「CLI 二进制更新」和「skill·md 更新」做成用户无感。但两条都是**代码执行面**:

- **⑨ 自更**:daemon 周期拉 GitHub release 换二进制。现状(`server/internal/cli/update.go`):下载二进制 + `checksums.txt` → **SHA-256 fail-closed** 校验 → 替换。缺口=**checksums.txt 无签名**:SHA-256 只验完整性(没传坏),不验真实性。能改 release 资产者(GitHub 账号失陷 / CI 失陷 / 中间人改 release)可**同时换二进制 + checksums.txt**,SHA-256 仍过 → 静默 RCE。
- **⑩ skill 分发**:要 registry→daemon 静默写可执行 skill 进 `~/.claude/skills`。skill = agent 读取并执行的指令 = **RCE 面**。现 `local_skills.go` 只读上报,无写盘;新写路径是净新攻击面。

威胁本质相同:**「谁有权决定一台机器执行什么」**。两者都必须有一条**密码学信任链**,把「可执行工件」绑定到「经评审合并的团队源」,且 daemon 在落盘前验签。

### 现有事实(grounding,勿据记忆)

| 事实 | 位置 | 含义 |
|---|---|---|
| 自更 self-host 默认关 | `daemon/config.go:381` `isOfficialCloudServer` | 仅 `api.multica.ai` 默认开;团队 `api.teamctx.actionow.ai`=self-host=关 |
| 显式启用机制已存在 | `daemon/config.go:382` `MULTICA_DAEMON_AUTO_UPDATE` env | 团队 deployment 设 `=true` 即启用,**无需改码硬编码团队 host** |
| release 源已是团队 fork | `cli/update.go:226,252` `feibo-ai/tc-multica` | fork-clobber 已防(不拉官方 multica),`config_test.go:246` 守 |
| SHA-256 fail-closed | `cli/update.go:172-207` | checksum 缺失/不符→拒换;但 checksums.txt **无签名** |
| 公钥 bootstrap 通道 | `install.sh:106-149` 走 GitHub Releases | 公钥可内置于 GitHub 分发的签名二进制(独立于 multica server) |
| daemon 写盘重组 | `cmd_skill.go:259 buildSkillMd` + `:350/369 runSkillPull` | skill pull 时 server 重组 frontmatter + 写 files[];签 commit 盖不住落盘字节 |

---

## 2 · 决策:统一签名信任根

### 2.1 信任根(共享)

- **签名身份 = release/CI**,不是任意团队成员的 commit。
  - 击破点(第三轮安全验证):「信任任一成员 commit 签名」= 单密钥失陷 = 全员 RCE。团队全员有 git push 权 → commit 签名信任根不可接受。
  - **取而代之**:签名由 **GitHub Actions release workflow** 在 **protected branch(main)+ 必需 2 人评审合并态** 上执行。签名密钥仅 CI 持有(GitHub OIDC → 短时签名,或 CI secret 持长期私钥),**任何单一成员的本地 commit 不能产生有效签名**。
- **签名对象 = 内容清单(content manifest)**,不是 commit/tag。
  - ⑨:签 `checksums.txt`(二进制的 SHA-256 清单)。
  - ⑩:签**逐文件内容哈希清单**(覆盖 `buildSkillMd:259` 服务端重组的 frontmatter + `runSkillPull:350/369` 写的 files[]) —— 因为 daemon 落盘的是**server 重组后的字节**,签 git commit 盖不住;必须签「最终落盘字节的哈希清单」。
- **验证者 = daemon,对实际落盘字节验**:
  - daemon 内置公钥 → 验清单签名 → 对**即将落盘的真实字节**逐个核对清单哈希 → 全过才落盘,任一不符即拒 + 告警。
  - registry / server 视为**不可信缓存**:它们传什么不重要,daemon 只信「公钥验过的清单 + 字节匹配」。

### 2.2 公钥 bootstrap 与吊销

- **公钥内置于 GitHub 分发的签名二进制**(`install.sh:106` 走 GitHub Releases,独立于 multica server)→ **非循环**:server 失陷不能换公钥(公钥随二进制来自 GitHub,二进制本身经下一轮签名链验证)。
- **可吊销 keyset**:二进制内置的是一组公钥(keyset),非单钥。密钥泄露→ release 一个废弃旧钥、启用新钥的新版本;吊销列表随签名清单分发(单调版本,见 2.3)。首个信任根仍靠 GitHub 二进制 bootstrap(TOFU 边界,见 §5 残留风险)。

### 2.3 防回滚 / 防冻结

- **每工件单调版本**:二进制版本(语义版本)、skill 清单带单调递增 `manifest_version`。daemon 拒绝**低于已落盘版本**的清单(防重放旧·有洞版本)。
- **签名时效界**:清单带签发时间 + 有效期(如 30d)。过期清单拒(防 server 冻结在某旧版、阻止安全修复送达)。

### 2.4 写路径安全(⑩ 专属)

- 新写路径独立校验:落盘目标必须在 `~/.claude/skills/<name>/` 内,**拒 symlink 穿越出界**(对照 `cmd_skill.go:451` 团队软链工作流——软链是开发机 git 工作流,daemon 写路径不得跟随软链写到 skills 外)。
- **验签包裹写动作**(非旁置):验签与写盘在同一不可绕过路径——先验签整个清单 + 逐字节核对 → 再原子落盘(temp + rename)→ 不存在「验了 A 写了 B」的 TOCTOU 窗口。
- **与开发机软链共存**:开发机走 git 软链(`sync-team-config.sh` step 1)= 本地真相,不触发 daemon 写路径;daemon 写路径仅用于「无 git 软链的消费机」。两者互不 clobber:daemon 写前检测目标是否为软链 → 是则**跳过**(软链=开发机已有权威源),不覆盖。

---

## 3 · ⑨ 二进制 provenance(具体)

1. **CI/release**:GoReleaser 产 `checksums.txt` 后,workflow 用 CI 签名身份产 `checksums.txt.sig`(ed25519 / minisign / cosign-blob,选型见 §6),作为 release 资产发布。
2. **daemon 自更**(`update.go` 扩):下载 `checksums.txt` + `checksums.txt.sig` → **先用内置公钥验 sig**(失败即拒,不 fall back)→ 验过才信 checksums.txt → 再 SHA-256 验二进制(现有逻辑)→ 替换。
3. **启用**:团队 deployment 设 `MULTICA_DAEMON_AUTO_UPDATE=true`(机制已存在);release 源已是 fork `feibo-ai/tc-multica`(已防 clobber)。
4. **验收(plan 硬标准)**:断言「**provenance 校验实际触发并通过**」——注入未签/错签/降级/过期的 release → 被拒 + 告警;合法签名 release → 验签通过并替换。**非仅开 enable-flag**。

---

## 4 · ⑩ 无感 skill 分发(具体)

1. **server 端分发选择**:server 决定哪些 skill 推哪些 daemon(净新逻辑);但 server **不被信任**——它只是缓存。
2. **签名清单**:release/CI 对「评审合并态的逐文件内容哈希清单」签名(覆盖 buildSkillMd 重组的 frontmatter + files[])。
3. **daemon 写路径**(净新):daemon 收到清单 + 文件字节 → 验清单签名(内置公钥)→ 逐字节核对哈希 → 单调版本 + 时效检查 → 写路径安全(防穿越)→ 原子落盘 `~/.claude/skills`。
4. **人在环**:信任经「2 人评审合并门 + CI 签名」一次性建立,之后无感达每台机(**非每机弹窗确认**——这化解了 v2 评审揪的「静默落盘 vs 可执行确认」矛盾:确认前移到评审合并门,机器侧无感)。
5. **真跑验收**:改一 skill 经评审合并 + 签名清单 → 不手动 pull,本地验签后 ≤2×ticker 落盘;注入未签 / 伪造 / 降级 / 陈旧 / 穿越工件 → 全被拒 + 告警。

---

## 5 · 威胁模型 → 缓解

| 威胁 | 缓解 |
|---|---|
| GitHub release 资产被换(账号/CI 失陷换二进制+checksum) | 公钥验 `checksums.txt.sig`;CI 签名密钥独立于 GitHub 写权,换资产无有效签名 |
| 单一成员 commit 投毒(全员 git 权) | 签名=CI 在 protected-branch+2 人评审合并态产;单成员 commit 不产有效签名 |
| server / registry 失陷推恶意 skill | server=不可信缓存;daemon 只信公钥验过的清单 + 字节匹配 |
| server 重组字节与签的 commit 不符 | 签**落盘字节哈希清单**(非 commit),daemon 验落盘字节 |
| 重放旧·有洞版本 | 单调版本,拒降级 |
| server 冻结在旧版阻止安全修复 | 签名时效界,过期拒 |
| 写路径 symlink 穿越出 skills 外 | 写路径独立校验 + 拒跟随软链写界外 + 验签包裹写(无 TOCTOU) |
| 签名密钥泄露 | 可吊销 keyset + 单调版本废旧钥;新信任根经 GitHub 二进制 bootstrap |

## 6 · 待评审定夺(选型 / 开放问题)

1. **签名算法/工具**:ed25519 裸签 vs minisign vs cosign(blob/keyless OIDC)。倾向 **cosign keyless(GitHub OIDC)**——CI 身份即签名身份,无长期私钥可泄;但需评估 daemon 侧验证依赖(Fulcio/Rekor 离线性 self-host 可用性)。备选 minisign(简单、离线、单 keyset)。**请评审给倾向**。
2. **manifest 格式**:复用 GoReleaser checksums.txt 形态扩签,还是独立 manifest(版本/时效/keyid)。
3. **keyset 内置 vs 配置**:公钥编译进二进制(改钥需发版)vs 随签名 keyset 文件分发(灵活但多一层信任)。倾向编译进(§2.2),评审确认。
4. **⑩ 落盘 ticker / server 分发选择的最小实现**:复用 register/heartbeat 通道还是净新端点。
5. **TOFU 边界**:首次 install.sh 从 GitHub 取的二进制是信任根起点(TOFU)。是否需 release 二进制本身的 GitHub Attestation(`actions/attest-build-provenance`)加固首跳。

## 7 · 验收标准(评审 + 实现共同对照)

- [ ] ⑨:注入未签/错签/降级/过期 release → daemon 拒 + 告警;合法 → 验签通过并替换(provenance 实际触发)。
- [ ] ⑩:改 skill 经评审合并+签名 → ≤2×ticker 无感落盘;注入未签/伪造/降级/陈旧/穿越 → 全拒 + 告警。
- [ ] 签名身份 = CI 在 protected-branch + 2 人评审合并态(非单成员 commit)。
- [ ] daemon 验**落盘字节**(非 commit/tag);registry/server 为不可信缓存。
- [ ] 写路径防 symlink 穿越;验签包裹写(无 TOCTOU);与开发机软链共存不互 clobber。
- [ ] 单调版本 + 时效界防回滚/冻结;可吊销 keyset。

## 8 · 残留风险

- **TOFU 首跳**:首个二进制信任靠 GitHub 分发(§6.5 可用 build-provenance attestation 加固)。
- **CI 失陷**:CI 持签名能力 → CI 失陷=可签恶意工件。缓解靠 protected-branch + 2 人评审 + OIDC 短时身份 + 审计;不可完全消除(这是任何 CI 签名体系的固有边界)。
- **公钥轮换的发版依赖**(若选编译内置):换钥需发新二进制 + 旧机经一次自更才拿到新钥;吊销列表分发缓解。
