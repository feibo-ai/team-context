# 安全设计 mini-ADR v2：无感分发与自更 provenance 信任根（⑨ + ⑩）

- **状态**：DRAFT v2 — 据第一轮独立安全评审(5 Blocker)方向性重做,待**第二轮独立安全评审**。**评审通过前不得 code**。
- **日期**：2026-06-10 · **取代** `2026-06-10-seamless-distribution-security-mini-adr.md`(v1)
- **关联**：TEA-89 v4 plan ⑨⑩;v1 + 其评审记录(本文件 §0 摘要)。

## 0 · v1 → v2:第一轮评审击破的三个承重假设

第一轮独立安全评审对照真实代码证伪了 v1 的核心:

| Blocker | v1 假设 | 真实代码证伪 | v2 解法 |
|---|---|---|---|
| **B1** | 签名由 CI 在「protected-branch + 2 人评审合并态」产 | `release.yml` 是 `push: tags v*` 触发,无 CODEOWNERS / 无 required-review enforcement / 无 tag protection → 任意成员可在**任意 commit** push tag 触发签名 | §2.1:release workflow 加**可验证硬门**(tag 必须指向 main 上 2 人评审的合并 commit)+ GitHub 配置清单(§2.5)+ 验收实测 |
| **B4** | install.sh 公钥 bootstrap「已存在」 | install.sh **零校验**(curl→mv),无内置公钥 → 信任链第 0 跳是空的 | §2.2 + §3.0:install.sh **实装** attestation 验证首跳 + 内置 keyset;**代码里无 unsigned fallback 分支** |
| **B5** | ⑩ 签「落盘字节哈希清单」 | `buildSkillMd` 落盘字节含 server 可变状态(`last_reviewed_at` 被 `touch-reviewed` 改)→ CI 离线算不出 daemon 落盘字节 = 假闭合 | §2.3:签**git 源字节**,daemon **确定性重组**(可变元数据排除在签名外),分发传源 bundle 不传 server 重组响应 |

外加 B2(签名身份须 OIDC/无长期裸 secret)、B3(self-host 离线验证)、I1–I5、M1–M4。本 v2 逐条解。

---

## 1 · 不变的方向（评审确认正确,保留）

- 签**内容**(清单/源字节),不签 commit/tag。
- registry/server = **不可信缓存**;daemon 只信「内置信任根验过的签名 + 字节匹配」。
- 单调版本(防回滚)+ 时效(防冻结)。
- 验签**包裹**写动作(无 TOCTOU)、原子 temp+rename。

---

## 2 · v2 信任根（重做）

### 2.1 签名只在「2 人评审 + 合并 main」态发生（解 B1）

三道硬门,缺一不可:

1. **release workflow 硬门(可验证 · 写进 CI)**:`release.yml` 的 `verify` job 增加——
   - `git merge-base --is-ancestor "$GITHUB_SHA" origin/main` 必须通过(tag 指向的 commit 必须在 main 上);
   - 用 `gh api` 断言该 commit 对应一个 **已合并 PR** 且 `reviewDecision==APPROVED`、**approved review 数 ≥2 且 reviewer ≠ author**;
   - 任一不满足 → workflow `exit 1`,**不签、不发**。
2. **GitHub 服务端配置(§2.5 清单 · 验收实测)**:`main` branch protection(required reviews ≥2、dismiss stale、require review from non-author)+ **`v*` tag protection rule**(否则 push-tag 本身是后门,绕开 #1)。
3. **签名能力受 2-reviewer Environment 门控(解 B2)**:签名步骤在 GitHub Actions **`release` Environment** 内执行,该 Environment 配 **required reviewers ≥2**;即任何一次签名都需 2 人在 release 时点头。单个失陷成员既过不了 #1(2 人评审合并)也过不了 #3(2 人 Environment 批准)。

### 2.2 签名机制:minisign(离线)+ GitHub attestation(首跳)（解 B2/B3）

- **持续工件签名 = minisign**(ed25519,纯离线、单文件验证、零外部在线依赖)——契合 self-host/离线消费机(B3)。私钥**不裸放普通 Secrets**:存 §2.1#3 的 2-reviewer `release` Environment secret,仅受批准的 release run 可读。
- **install.sh 首跳 = GitHub build-provenance attestation**(`actions/attest-build-provenance`,OIDC、无私钥)。install.sh 用 `gh attestation verify --repo feibo-ai/tc-multica`(或内置离线 bundle 验证)验首个二进制 provenance 绑定到本 repo + release workflow → 把 TOFU 从「信任任意字节」收窄到「信任本 repo release workflow 产物」(解 B4/I3,attestation 升为 **MUST**)。
- **公钥 keyset 编译内置二进制**(多公钥 + 吊销,§2.4)。换钥经发版 + install.sh 带外 re-bootstrap(§2.4)。
- **§6 选型**:minisign vs 统一 attestation 二选一仍留第二轮评审定夺;v2 倾向 minisign(离线简单)+ attestation 仅护首跳。

### 2.3 ⑩ 签源字节,daemon 确定性重组（解 B5）

- **签名对象 = git 仓库源 skill 文件原始字节**(SKILL.md 源 blob + bundle 文件 blob),CI 在 checkout 工作树上对**源 blob** 算哈希清单并 minisign 签 —— git blob 字节固定 = **确定性可复现**,CI 与 daemon 算同一哈希。
- **server 派生的可变元数据**(`last_reviewed_at`、`owner_user_id`)**绝不进签名覆盖字节**:daemon 落盘时本地附加(或经独立可信路径),不参与哈希。frontmatter 重组逻辑做成 CI/daemon **共享纯函数**(字段固定顺序、可变字段排除),对固定源输入确定性输出。
- **分发数据流(必须画清,否则回退到信 server)**:净新分发通道传「CI 签好的源 bundle + minisign 签名 + manifest(身份/版本/时效)」;daemon **不走** `GET /api/skills/<id>`(server 重组响应)。daemon:验 manifest 签名 → 逐源字节核对哈希 → 确定性重组 → 验落盘字节 == 重组结果 → 原子落盘。server 只透传签好的 bundle,改不了签名也改不了 daemon 重组结果。
- **manifest 绑定 `(workspace_id, skill_name, monotonic_version)` 进签名覆盖**(解 M2 串扰):daemon 验「收到的 skill 身份 == manifest 声明」。

### 2.4 防回滚/时效/吊销（解 I2/I5）

- **防回滚(永久)**:每 skill / 二进制单调版本;daemon 拒**低于已落盘**版本的清单。永久有效,无时效。
- **防冻结(时效,仅影响『是否当 latest』)**:manifest 带签发时间 + 有效期(**可配**,self-host 可调长,默认如 90d)。**过期清单只 = 不再当作 latest(不阻止寻找更新),绝不 = 拒绝运行已落盘版本**。过期 → 升级告警,已装版本继续可用(解 I2「过期即砖」)。
- **吊销单调**:keyset 带吊销计数;daemon 见过吊销 N 后拒任何吊销计数 <N 的清单(防回放吊销前状态,解 I5)。带外 re-bootstrap:重跑 install.sh 从 GitHub 取新二进制(新 keyset);install.sh 公钥经 attestation 验(§2.2),可轮换。

### 2.5 信任根的 GitHub 配置依赖清单（B1#2 · 验收实测）

ADR 显式声明这些**仓库外但必须存在**的 GitHub 配置(以前 v1 当口头假设):
- [ ] `main` branch protection:required approving reviews ≥2、dismiss stale approvals、require review from someone other than author、require status checks(ci.yml)。
- [ ] `v*` tag protection rule(仅 maintainer/CI 可创建 release tag)。
- [ ] `release` Environment:required reviewers ≥2,minisign 私钥 secret 仅此 Environment。
- **验收实测**:CI/脚本用 `gh api repos/feibo-ai/tc-multica/branches/main/protection` 等断言以上存在,缺即 fail(把口头假设变成可验证门)。

---

## 3 · 写路径与降级（解 B4/I1/I4）

### 3.0 绝无 unsigned fallback（解 B4）

- **代码里根本不存在「缺签名/缺验证物料 → 退回未签安装」的分支**(不是「默认关」,是不写这条路)。缺 .sig / 缺 attestation / 验证物料 404 → **fail-closed 拒 + 本地告警**。
- 验收含「**删除签名资产 / 返回缺失 → daemon 拒 + 告警**」(降级变体,v1 只测了未签/错签)。

### 3.1 写路径防穿越（解 I1）

- 落盘前对**每一级父目录** `EvalSymlinks` 后断言仍在 `~/.claude/skills/<name>/` 真实路径内;写文件用 `O_NOFOLLOW|O_EXCL`(新建)或先 `lstat` 拒非常规文件 —— 防 symlink/hardlink 跟随写到 skills 外(现 `runSkillPull` 只查 `..`/绝对,不够)。
- **「目标是软链则跳过」改为积极判据**:仅当软链指向 git 工作树内**白名单**权威源(`sync-team-config.sh` 建的链)才跳过;**未知软链 = 攻击信号 → 告警 + 拒写,不静默跳过**(否则攻击者预置软链 = 冻结/降级武器,解 I1)。
- daemon 写权限:以用户态写 `~/.claude/skills` → 有权写用户全部 dotfile,symlink 逃逸影响面=整个家目录,§5 显式建模。

### 3.2 告警可靠性（解 M3）

- 安全告警**本地落地**(本地日志文件 + 非零退出码),**不依赖 server 回传**(server 是不可信缓存,失陷 server 会吞告警)。

---

## 4 · 威胁模型 v2（补 v1 漏项）

| 威胁 | 缓解 | 解 |
|---|---|---|
| 单成员 push tag 在未评审 commit 上触发签名 | release workflow 验 main-merged + ≥2 review + tag protection + Environment 2-reviewer | B1 |
| 长期签名私钥泄露/被任意 run 读取 | 私钥仅 2-reviewer Environment;首跳用无私钥 attestation | B2 |
| self-host 离线无法验签 | minisign 纯离线 + attestation 离线 bundle | B3 |
| 缺签名→降级未签安装 | 代码无 fallback 分支,fail-closed | B4 |
| server 重组字节与签的源不符 / server 失陷重算清单 | 签源 blob,daemon 确定性重组,分发传源 bundle 不传 server 响应 | B5 |
| symlink/hardlink 写出 skills 外 / 预置软链冻结 | EvalSymlinks 父链校验 + O_NOFOLLOW + 软链积极白名单判据 | I1 |
| 过期清单致 self-host 砖 | 过期只影响 latest 判定,不阻已装运行;有效期可配 | I2 |
| TOFU 首跳信任空 / 二进制不可复现 | attestation MUST 验首跳 | I3 |
| daemon 二进制本地被篡改 → 验签形同虚设 | **信任边界**:daemon 二进制完整性是验签根 assumption;本地同用户写权失陷不在保护范围 | I4(§5) |
| 泄露旧钥+控分发冻结单机收不到吊销 | 单调吊销计数 + 带外 install.sh re-bootstrap | I5 |
| A workspace 签名 skill 被串给 B workspace | manifest 绑 (workspace_id, skill, version) 进签名 | M2 |
| 多机告警被失陷 server 静默 | 告警本地落地 | M3 |
| 评审者审 git diff ≠ 机器执行字节 | 签源字节 + daemon 确定性重组(评审对象=执行对象) | M4/B5 |

## 5 · 信任边界与残留风险（诚实）

- **daemon 二进制完整性 = 所有验签的根**:本地 root / 同用户写权失陷 → 签名体系不提供保护。缓解(可后续):二进制装 root-only 路径 + 非特权 daemon + OS 完整性(macOS notarize / Linux IMA)。**显式承认,不假装验签在本地失陷下有效**(I4)。
- **CI 失陷**:CI 持签名能力。缓解=B1 三门 + OIDC 短时 + 审计;不可完全消除(任何 CI 签名体系固有边界,但已从「单成员 push 权」抬到「攻破 2-reviewer Environment + 评审合并门」)。
- **TOFU 首跳**:install.sh 首个二进制经 attestation 收窄,但仍是信任起点。
- **旧钥泄露冻结单机**:接受为残留,带外 re-bootstrap 收敛。

## 6 · 待第二轮评审定夺

1. minisign(离线简单 · 私钥 Environment 门控)vs 统一 attestation(无私钥 · 离线验证复杂度)—— v2 倾向前者,请评审拍。
2. daemon/CI 共享的「确定性 frontmatter 重组纯函数」边界:哪些字段进签名、哪些 daemon 本地附加(`last_reviewed_at`/`owner_user_id` 排除已定;还有别的吗)。
3. ⑩ 分发通道:净新端点 vs 复用 register/heartbeat 传签名 bundle。

## 7 · 验收标准 v2

- [ ] ⑨:注入未签/错签/降级/**缺签名物料**/过期 release → 拒 + **本地**告警;合法 → provenance 实际触发并替换。
- [ ] ⑩:改 skill 经 2-review 合并 + 签源 bundle → ≤2×ticker 无感落盘;注入未签/伪造/降级/陈旧/**穿越**/**跨 workspace 串扰** → 全拒 + 本地告警。
- [ ] release workflow 拒「tag 指向非 main-2review-merged commit」(B1 实测)。
- [ ] `gh api` 断言 main branch protection + v* tag protection + release Environment 2-reviewer 存在(§2.5 实测)。
- [ ] install.sh 验首个二进制 attestation,缺/坏即拒(B4 实测)。
- [ ] daemon 验**源 blob 哈希 + 确定性重组后落盘字节**(非 server 响应);可变元数据不在签名内(B5 实测:touch-reviewed 后分发仍验过)。
- [ ] 写路径:预置 symlink/hardlink 逃逸 → 拒 + 告警;未知软链不静默跳过(I1 实测)。
- [ ] 过期清单 → 不阻已装运行 + 升级告警(I2 实测);有效期可配。
