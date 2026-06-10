# 安全设计 mini-ADR v3：真·无感自更与分发信任根（⑨ 二进制 + ⑩ skill/md）

- **状态**：DRAFT v3 — 据第二轮独立安全评审(4 lens,3 新 Blocker + B1-B5/I1-I5 逐条)**决定式收敛 7 个设计决断**,待**第三轮独立安全评审**。评审通过前不得 code(SOP 红线·plan 硬门)。
- **日期**：2026-06-10 · **取代** v2(`…-v2.md`)· 谱系 v1→v2→v3(评审 trail 见 §0)
- **目标**:用户要「真·无感自更」——CLI 自动无感更新**自己(二进制)+ skill + md 文档**,daemon 静默验证写盘,人不介入。本 ADR 把它做成**安全软件分发子系统**而非 vibe code。

## 0 · 谱系与本轮收敛

v1 被第一轮揪 5 Blocker(签名信任根循环/install.sh 空锚/落盘字节假闭合)。v2 方向性重做但第二轮(4 lens)再揪 **3 新 Blocker + 多 partial**:NB1 信任锚 repo 错位、NB2 签名机制未定且 minisign 长期裸钥、NB3 `multica update` 稳态自更在签名覆盖外;B1 gh-api 门可绕(计数版)、B5 owner 复现冲突 + §2.3 混用两套设计、I1 写路径靶子错、I5 吊销靠带外。**第二轮还揭示 ⑩ 是 greenfield**(daemon 现在不写 skill 盘)。

本 v3 **决定式**敲死 7 决断(不再「待评审定夺」):

| # | 决断 | 据评审 |
|---|---|---|
| ① | 唯一信任锚 = `feibo-ai/tc-multica`(团队部署的 fork),install.sh + update.go + attestation --repo + 分支/tag 保护全锚它;upstream 不在团队信任路径 | NB1 |
| ② | 签名 = **keyless OIDC build-provenance attestation**(无长期私钥);daemon 内置 sigstore 信任根离线验证(sigstore-go);install.sh 首跳=诚实 TOFU,二进制首启自验 provenance | NB2/B2/B3 |
| ③ | `multica update` 稳态自更纳入受保护路径,**强制验 attestation**(SHA-256 之外),无 unsigned fallback | NB3 |
| ④ | release gh-api 门升级为 **tree-sha 绑定**(tag-sha==PR.merge_commit_sha + ≥2 APPROVED@head + reviewer∉{author,bot})+ ruleset 分支/tag 保护(admin 不绕) | B1 |
| ⑤ | ⑩ 分发 = **签 git 源 blob 逐字节**,daemon byte-for-byte 写(重组=恒等);server 可变元数据(owner_user_id/last_reviewed_at)**不进分发 bundle**,留 registry DB 供 web/lint | B5/M4 |
| ⑥ | 吊销 = **稳态在线通道下发签名吊销表 + 本地持久化最高单调计数**;带外 install.sh re-bootstrap 兜底离线砖机 | I5 |
| ⑦ | 写路径靶子 = `runSkillPull` + **净新 daemon 写循环单独威胁建模**;EvalSymlinks 父链 + O_NOFOLLOW;软链「跳过」降级为**确定性拒写 + 本地告警**(非静默跳过) | I1/M3 |

---

## 1 · 信任根(决定式)

### 1.1 唯一锚 repo（解 NB1）
- **唯一签名/验证锚 = `feibo-ai/tc-multica`**(团队实际部署+安装+自更的 fork)。证据:install.sh:115 从它下载、update.go:226/252 从它拉 release。team 的信任路径**只**经它。
- upstream `multica-ai/multica` **不在团队信任路径**:团队 daemon/install.sh/attestation 一律 `--repo feibo-ai/tc-multica`,绝不接受 upstream 工件。若未来从 upstream 同步,是另一次显式信任决策(本 ADR 范围外)。
- **fork 第二条管线门控**:`feibo-ai/tc-multica` 的 release.yml 是团队唯一签名管线;§1.4 的分支/tag/Environment 保护全配在此 repo。attestation 验证断言 OIDC subject 的 repo==`feibo-ai/tc-multica`、workflow==release.yml、ref==`refs/tags/v*`——upstream 或任何其它 repo 的工件验签即失败。

### 1.2 签名机制 = keyless OIDC attestation（解 NB2/B2/B3）
- **持续工件签名(二进制 + skill bundle)= GitHub `actions/attest-build-provenance`**:OIDC 现签,**无长期私钥**(消除 minisign 私钥外泄=离线无限伪造的 Blocker)。签名身份=workflow run 的 OIDC subject。
- **daemon 离线验证**:daemon(Go)内置 **sigstore 信任根**(pin 的 TUF root.json + Fulcio CA + Rekor 公钥),用 **sigstore-go** 离线验 attestation bundle(bundle 自带 DSSE + Fulcio 证书链 + Rekor 包含证明,验链不联网 Fulcio/Rekor)。验证断言 §1.1 的 OIDC subject(repo/workflow/ref)。**self-host 离线可用**(B3 解)。
- **install.sh 首跳 = 诚实 TOFU**:install.sh 纯 bash 无 gh CLI/sigstore → 下载 + checksums.txt SHA-256(=server-trust,明文承认无密码学防护);**真 provenance 验证下沉到二进制首启**:装好的二进制(内置信任根)在 daemon 首启/首次 update 时**自验自己的 attestation**,不过即拒启 + 告警。TOFU 窗口=首装到首启,显式记入 §5。
- **统一机制**:二进制(⑨)与 skill bundle(⑩)用同一 attestation + 同一 daemon 验证栈,无双信任根。

### 1.3 `multica update` 强制验签（解 NB3）
- update.go 的 `UpdateViaDownload` 路径:下载二进制 + 其 attestation bundle → **先 sigstore-go 验 attestation**(内置信任根 + subject 断言)→ 过才 SHA-256(现有 :209-407)→ 原子替换。**无签/坏签/缺 bundle → fail-closed 拒 + 告警,无 unsigned fallback**(与 §3.0 同标准)。
- 验收:注入篡改归档 + 伪造 checksums.txt(无有效 attestation)→ 拒。

### 1.4 release gh-api 门 + GitHub 配置（解 B1）
- release.yml `verify` job 硬门(可执行断言,写进 CI):
  1. `git merge-base --is-ancestor "$GITHUB_SHA" origin/main` 通过;
  2. **tag-sha == 某 PR 的 `merge_commit_sha`**(squash 合并下用 merge_commit_sha,非 head),且该 PR 有 **≥2 条 `state==APPROVED` 且 `commit_id==PR head` 的 review**,**reviewer login ∉ {PR author, 任何 bot/Actions 身份}**;
  3. 任一不满足 → `exit 1` 不签不发。**计数式 ≥2 不够,必须绑 tree-sha + 排 self/bot**(B1)。
- **GitHub 配置依赖清单(§1.5 实测门)**:`feibo-ai/tc-multica` 上——`main` Repository **Ruleset**(非 classic):required reviews ≥2、dismiss stale、require non-author review、**bypass actors 为空(admin 不绕)**;`v*` tag **Ruleset**(create 受限、bypass 空);`.github/workflows/**` 纳入 CODEOWNERS + ruleset required review(防改 workflow 本身绕门)。
- **诚实边界**:gh-api 自检 job 跑在受保护 repo 的 CI 内,主要防**配置漂移/遗忘**,不防**主动篡改 release.yml**(攻破 workflow 者可关自检)——真完整性靠 org-ruleset 限制谁能改 `.github/`。记入 §5。

### 1.5 配置实测门
CI/脚本 `gh api repos/feibo-ai/tc-multica/rulesets`、`…/branches/main/protection` 断言 §1.4 的 ruleset 存在且 bypass 空,缺即 fail。把口头假设变可验证门(但见 §1.4 诚实边界)。

---

## 2 · ⑩ skill/md 无感分发(决定式 · 签 git 源 byte-for-byte）

### 2.1 签源字节,daemon 恒等写（解 B5/M4）
- **分发+签名对象 = git 仓库源文件原始字节**(SKILL.md 源 blob + bundle 文件 blob),CI 在 checkout 工作树对**源 blob** 打包成 bundle 并 attestation 签。git blob 字节固定=确定性可复现。
- **daemon 写 = byte-for-byte 恒等**:daemon 验 attestation → 解 bundle → 逐文件核对哈希 → **原样落盘**(无任何 server 端 buildSkillMd 重组)。`buildSkillMd`(从 DB 重组、注入 owner_user_id/last_reviewed_at)**不在无感分发路径**——它只服务 `skill pull`(手动/web)。
- **server 可变元数据出签名边界**:`owner_user_id`(sync 经 user list 解析的 UUID)、`last_reviewed_at`(touch-reviewed 改)**不进分发 bundle**;它们留在 registry DB 供 web UI / `skill lint`(lint 在 pull 后对 DB 投影跑,不依赖分发 bundle)。源 SKILL.md 里的静态 `owner: 曾振华` / `last_reviewed_at: <git值>` 是 git blob 内容,随 bundle 原样分发(静态、非 server 可变),不冲突。
- **评审对象==执行字节**(解 M4):2 人评审的是 git diff(源 blob),daemon 落盘的也是源 blob,两者同一对象。
- **manifest 绑 `(skill_name, git_commit, monotonic_version)` 进 attestation subject**(解 M2 串扰):daemon 验收到的 skill 身份==attestation 声明。

### 2.2 净新 daemon 写循环 · 单独威胁建模（解 I1/I4/M3 · 评审揭示的 greenfield）
- **现状**:daemon **不写 skill 盘**(`local_skills.go` 只读上报)。⑩ 是**净新写循环**:server 分发选择 → daemon 拉签名 bundle → 验 → 写 `~/.claude/skills`(及 md → `~/.claude` `~/.codex`)。**新引入 daemon 进程对用户 dotfile root 的自动写权,攻击面 > 手动 pull**,单独建模:
  - **写路径靶子=新写循环(非 runSkillPull 的手动路径)**:落盘前对**每一级父目录** `EvalSymlinks` 后断言真实路径仍在 `~/.claude/skills/<name>/`(及白名单 md 目标)内;写用 `O_NOFOLLOW|O_EXCL`(新建)/ 先 `lstat` 拒非常规文件。
  - **软链=确定性拒写 + 本地告警(非静默跳过)**(解 I1):目标已是 symlink/非常规文件 → **拒写该工件 + 本地告警**。理由:I4 同用户失陷模型下「软链白名单」不可信(攻击者就是能预置链的同用户);开发机的合法软链工作流(`sync-team-config.sh` 建的链)由**该机不启用 daemon 写循环**来共存——dev 机走 git 软链(本地真相),消费机才启 daemon 写循环,两类机互斥配置,不在同机并存。
  - **验签包裹写**:验 attestation + 逐字节核对 → 原子 temp+rename 落盘,无 TOCTOU。
  - **告警本地落地**(解 M3):安全告警写本地日志 + 进程退出码/状态,**不经不可信 server 回传**;daemon 后台写场景的告警可达性靠本地持久化 + `multica doctor`/状态命令暴露(人可主动查)。
- **daemon 二进制完整性 = 根 assumption**(解 I4):本地同用户写权失陷 → 验签代码可被改成 no-op,签名体系不提供保护。缓解(后续):二进制装 root-only 路径 + 非特权 daemon + OS 完整性(macOS notarize / Linux IMA)。**显式承认,记 §5。**

### 2.3 md 文档分发
md(CLAUDE.md/AGENTS.md/skills-index)同 skill:源 blob 进签名 bundle,daemon 验签后写 `~/.claude` `~/.codex`,确定性拒符号链穿越。dev 机软链不启 daemon 写(同 §2.2 互斥)。

---

## 3 · 防降级 / 防回滚 / 吊销

### 3.0 绝无 unsigned fallback（解 B4）
代码**不存在**「缺 attestation/缺 bundle/验签失败 → 退回未签安装」分支(不是默认关,是不写)。缺/坏/降级 → fail-closed 拒 + **本地**告警。验收含「删 attestation 资产/返 404 → 拒 + 告警」。

### 3.1 防回滚(永久) + 防冻结(时效)（解 I2）
- 单调版本:daemon 拒**低于已落盘**的二进制/skill bundle。永久,无时效。
- 时效:bundle 带签发时间 + 有效期(**可配**,self-host 调长,默认 90d)。**过期只 = 不再当 latest(不阻已装运行)+ 升级告警**,绝不砖。

### 3.2 吊销 = 稳态在线 + 单调计数（解 I5）
- daemon 稳态在线通道(heartbeat/poll)收**当前信任根签名的吊销表** + **本地持久化已见最高吊销计数**;拒任何计数 < 已见最高的 keyset/bundle(防回放吊销前)。
- 在线机自动收敛;离线机下次在线收;完全离线砖机靠**带外 install.sh re-bootstrap**(取新二进制+新内置信任根)。install.sh 公钥/信任根随二进制可轮换。

---

## 4 · 威胁模型 v3（含第二轮新增）

| 威胁 | 缓解 | 解 |
|---|---|---|
| upstream/fork 双管线产同名工件、锚错 | 唯一锚 feibo-ai/tc-multica;attestation 断言 repo/workflow/ref | NB1 |
| 长期签名私钥外泄=离线无限伪造 | keyless OIDC,无长期私钥 | NB2/B2 |
| self-host 离线无法验签 | sigstore-go + 内置信任根离线验 bundle | B3 |
| `multica update` 稳态拉未签二进制 | update.go 强制验 attestation,无 fallback | NB3 |
| 单成员 push tag 在未评审 commit 签 | tree-sha 绑定 + ≥2@head 排 self/bot + ruleset(admin 不绕) | B1 |
| server 重组字节/server 失陷伪造 | 签 git 源 blob,daemon 恒等写,不用 buildSkillMd | B5 |
| 净新 daemon 写循环 symlink/hardlink 逃逸 | EvalSymlinks 父链 + O_NOFOLLOW + 确定性拒写 | I1 |
| 预置软链冻结/降级 | 软链=拒写+告警(非跳过) | I1 |
| 过期致离线砖 | 过期只影响 latest 判定 | I2 |
| TOFU 首跳 + 不可复现二进制 | 二进制首启自验 attestation;诚实记 TOFU 窗口 | I3/B4 |
| daemon 二进制本地篡改 | 根 assumption,§5 诚实承认 + OS 完整性缓解 | I4 |
| 泄露旧钥冻结单机收不到吊销 | 稳态在线吊销表 + 带外 re-bootstrap | I5 |
| 跨 skill/workspace 串扰 | manifest 绑 (skill,commit,version) 进 subject | M2 |
| 告警被失陷 server 静默 | 告警本地落地 + doctor 暴露 | M3 |

## 5 · 信任边界与残留风险（诚实）
- **daemon/CLI 二进制完整性 = 所有验签的根**;本地同用户写权失陷不在保护范围(缓解:root-only 安装 + 非特权 daemon + OS 完整性)。
- **TOFU 首跳**:install.sh 首装是 TOFU,二进制首启自验收窄;窗口=首装到首启。
- **CI 失陷**:keyless 把失陷面抬到「攻破 GitHub OIDC + 过 §1.4 评审合并门」,不可完全消除(固有边界),但远高于「拿单成员 push 权」。
- **gh-api 自检**只防漂移不防主动篡改 workflow(靠 org-ruleset 限改 `.github/`)。
- **完全离线砖机**:旧钥泄露 + 控分发可冻结,靠带外 re-bootstrap 收敛。

## 6 · 验收标准 v3（评审+实现共同对照）
- [ ] 二进制(⑨):install 首跳 TOFU + 二进制首启**自验 attestation**;`multica update` 强制验 attestation,注入篡改归档/伪造 checksum/缺 bundle/降级/过期 → 拒+本地告警;合法 → 验过替换。
- [ ] skill/md(⑩):改 skill 经 2-review 合并 + CI attestation 签 git 源 bundle → daemon ≤2×ticker 无感 byte-for-byte 落盘;注入未签/伪造/降级/陈旧/**穿越**/**跨skill串扰**/**预置软链** → 全拒+本地告警。
- [ ] 签的是 git 源 blob,daemon 恒等写(touch-reviewed 改 DB 后分发仍验过——证明 buildSkillMd 不在路径);评审对象==落盘字节。
- [ ] release workflow 拒「tag 指向非 main-2review@head-merged commit / self/bot review」(B1 实测);`gh api` 断言 main+tag ruleset bypass 空(§1.5)。
- [ ] daemon 离线(断网 Fulcio/Rekor)仍能验 attestation bundle(sigstore-go + 内置信任根)。
- [ ] 净新 daemon 写循环:预置 symlink/hardlink → 确定性拒写+告警;dev 机软链工作流与消费机写循环互斥配置不互 clobber。
- [ ] 无任何 unsigned fallback 代码分支(grep + 对抗注入双证)。

## 7 · 实现工作量诚实声明(greenfield)
⑩ 是净新:(a) CI release.yml 加 attestation 签二进制 + 打包/签 git 源 skill bundle + tree-sha 评审门;(b) daemon 新写循环(拉 bundle/验 attestation/byte-for-byte 写/防穿越/告警)+ sigstore-go 离线验证栈 + 内置信任根;(c) update.go 强制验 attestation;(d) install.sh TOFU + 二进制首启自验;(e) server 分发选择端点;(f) 吊销在线通道。非「加固现有」。本 v3 过第三轮评审后,实现走 Workflow 扇出 + 对抗验证 + 独立 code review。
