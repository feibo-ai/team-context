# 安全设计 mini-ADR v4（APPROVED 设计）：真·无感自更与分发信任根（⑨ + ⑩）

- **状态**：**APPROVED 设计**（经三轮独立对抗安全评审收敛 · 据第三轮 8 条 RB 决定式落 MUST）。实现以本文 §0 的 10 条 implInvariants 为绑定契约;实现闭合由**第四阶段 §6 对抗验收 + 独立 code review** 裁定（非再开设计评审）。
- **日期**：2026-06-10 · **取代** v3 · 谱系 v1→v2→v3→v4（评审 trail：v1=5 Blocker、v2=3 新 Blocker、v3=0 新架构 Blocker+8 RB 精修,均独立核验真实代码）
- **目标**：CLI 自动无感更新**自己(二进制)+ skill + md**,daemon 静默验证写盘,人不介入——做成**安全软件分发子系统**。
- **2026-06-10 后续实施偏离(DRI 决定 · 记录与实现一致)**:invariant #7(原设计=「签名/发版只在 **≥2-review-merged** 态发生」)落地中经 DRI 决定**逐步放宽**至「**release tag 须经 PR 合并入 main**」——**不强制独立评审**(branch ruleset `required_approving_review_count=0`,允许自审核;provenance gate 去掉「独立 approver」检查,仅验「经 PR 合并入 main」这层来源)。速度优先(5 人团队 · DRI 常 solo)。**安全后果(显式接受)**:signing 信任根从「2 人独立评审」收敛为「PR-merged 来源证明 + gated release workflow」;**B1 单成员投毒风险被接受**。其余 invariants(#1-#6 / #8-#10:keyless attestation 离线验签、写路径安全、单调防回放、吊销、fail-closed、配置探针等)**不变,仍按本 ADR 实施**。

---

## 0 · 绑定实现契约（10 条 implInvariants · code review 逐条对照）

实现 + code review **必须**逐条满足;凡 ADR 写成散文的缓解,实现时落为 `gh api` 可查的 MUST + 验收脚本,否则视为未实现。

1. **签名/分发对象 = git tracked-blob 原始字节**（`git cat-file blob` / `git archive`),**绝不**遍历 checkout 工作树;bundle 文件集 = `git ls-files <skill-dir>` 的 tracked 文件,排未跟踪/ignored,**按路径固定排序**;repo 落 `.gitattributes` 关键路径 `-text`、CI `core.autocrlf=false`;CI 复算 blob hash 须 == git 对象 hash。【RB-4】
2. **attestation 验证三元组全等才放行**：OIDC subject `repo==feibo-ai/tc-multica` **AND** `workflow==.github/workflows/release.yml` **AND** `ref=~refs/tags/v*`;任一不符即拒——**尤其须拒 upstream `multica-ai/multica` 产的同名合法 attestation**。【RB-1】
3. **任何路径(update.go / daemon 写循环 / install 首启)缺/坏/降级 attestation → fail-closed 拒 + 本地告警,绝无 unsigned/SHA-only fallback 分支**(grep + 对抗注入双证);SHA-256 只在 attestation 验过**之后**跑,不作独立信任来源。【B4】
4. **sigstore-go 内置 TUF root 过期 = fail-closed 拒验 + 本地告警 + 提示 re-bootstrap,绝不 fail-open 退 SHA-256**。【RB-2】
5. **daemon 写循环落盘原语二分**：新建(目标不存在)走 `O_CREATE|O_EXCL|O_NOFOLLOW`;更新(目标存在)走 `lstat` 断言普通文件→同目录 temp(`O_EXCL|O_NOFOLLOW`)→`rename` 原子覆盖;两条都先对**每级父目录** `EvalSymlinks` 断言真实路径在白名单根内;目标已是软链/非常规文件 = **确定性拒写 + 本地告警,绝不静默跳过、绝不 follow**。【RB-5/I1】
6. **dev 机软链工作流 vs 消费机 daemon 写循环互斥 = 可验证配置**（`MULTICA_DAEMON_SKILL_WRITE` on/off · self-host 默认 off,同 `AutoUpdateEnabled` 逻辑):写循环启动前断言该机 `~/.claude/skills` 下无 sync 管理软链,冲突=拒启 + 告警,**不靠人约定**。【RB-6】
7. **release verify job 合并门须 ALL 满足**：`PR.state==MERGED && merged==true && base.ref=='main' && merge_commit_sha==$GITHUB_SHA && ≥2 条 APPROVED@head(commit_id==PR.head.sha)的 review,且 reviewer 两两不同且 ∉ {PR.user.login, 任何 bot/Actions slug, github.actor}`;未合并 PR / reviewer==pusher 一律 `exit 1`。【RB-8/B1】
8. **吊销表必须有真实签名来源**：做成 CI 签的工件走 §1.4 评审门(同 skill bundle 栈,吊销=一次发版),或用受 **2-reviewer Environment** 门控的显式长期钥(记为 keyless 之外第二信任材料);server heartbeat 下发带签名 `max-age`/心跳计数使 withholding 可检测;**绝不信不可信 server 下发的裸吊销表**。【RB-7】
9. **告警一律本地落地**(日志 + 进程状态/退出码 + `multica doctor` 暴露),**绝不经不可信 server 回传**或依赖 server 转达。【M3】
10. **所有安全裁决基于密码学断言或 `gh api` 可验证 GitHub 配置,不基于 honor-system/人约定**;散文缓解(org-ruleset 限改 `.github`、CODEOWNERS 覆盖 release.yml、dev/消费机互斥)实现时落 MUST + 验收脚本。【RB-1/3/6】

---

## 1 · 信任根（v3 决断 + 第三轮 RB 修正）

### 1.1 唯一锚 = feibo-ai/tc-multica · 切断靠消费端断言（RB-1 诚实化）
- 唯一签名/验证锚 = `feibo-ai/tc-multica`(团队部署/安装/自更的 fork)。install.sh:116 + update.go:226/252 实测锚它。
- **诚实表述(改 v3)**：upstream `multica-ai/multica` 的 release 管线**未被门控**(release.yml:57-87 在每个 fork 都跑、产同名 attestation 工件);**切断完全且仅靠 daemon 验签时断言 OIDC subject 三元组**(invariant #2)。这是承重脆点,记入 §5 残留 + §6 MUST 验收(构造 upstream-OIDC 合法工件→必拒)。

### 1.2 签名 = keyless OIDC attestation + sigstore-go 离线验 + TUF root 生命周期（RB-2）
- 签名 = GitHub `actions/attest-build-provenance`(OIDC,无长期私钥);daemon(Go)内置 sigstore 信任根 + `sigstore-go` 离线验 bundle(自带 DSSE+证书链+Rekor 包含证明,不联网)。
- **信任根生命周期(RB-2 新增)**：(i) root 来源——选 **Public Good TUF root**(sigstore 长期续期,daemon 在线时机会性 refresh)或自托管 root(团队自续),**第四阶段选型并写死谁续**;(ii) **内置 root 过期 = invariant #4**(fail-closed 拒 + 告警 + 提示 re-bootstrap,绝不 fail-open);(iii) 在线机会性 refresh TUF metadata(不改信任根,只续 metadata 时效),离线机靠 re-bootstrap。
- **install.sh 首跳诚实化(RB-3)**：首跳 = 纯 TOFU(install.sh 纯 bash curl→mv 无密码学校验);**二进制首启自验仅防意外损坏 + 检测降级资产,不防首跳主动 MITM/替换**(被换的恶意二进制自验=no-op);真收窄首跳需带外锚(install.sh 内联 pin 的 TUF root 指纹 / 第二信道发布 install.sh 哈希)。首跳完整性 = 根 assumption(§5)。

### 1.3 multica update 强制验签（NB3）
update.go `UpdateViaDownload`:下载二进制 + attestation bundle → sigstore-go 验(invariant #2 三元组 + #4 root 时效)→ 过才 SHA-256 → 原子替换;invariant #3 无 fallback。**前提**:self-host `AutoUpdateEnabled` 默认 false(config.go:381),团队 deployment 显式 `MULTICA_DAEMON_AUTO_UPDATE=true` 启用稳态自更载体。

### 1.4 release gh-api 合并门（RB-8 补全 = invariant #7）
release.yml `verify` job 落 invariant #7 全部谓词(现状仅 semver+go test=greenfield);§6 对抗用例:未合并 PR 的 test-merge sha 打 tag → 拒;reviewer==pusher → 拒。

### 1.5 GitHub 配置实测门（RB-1/RB-Important-3 = invariant #10）
`gh api` 断言(缺即 fail):main Ruleset(required reviews ≥2、dismiss stale、non-author、**bypass actors 空=admin 不绕**)、`v*` tag Ruleset(create 受限、bypass 空)、**`.github/workflows/**`+`.github/CODEOWNERS`+release.yml 受 CODEOWNERS 覆盖且 `require_code_owner_review==true`**(防改门本身;真实仓库现**无 CODEOWNERS**,实现须新建)。

---

## 2 · ⑩ skill/md 无感分发（v3 决断 + RB-4/5/6 修正）

### 2.1 签 git tracked-blob 字节,daemon 恒等写（RB-4 = invariant #1）
- 分发/签名对象 = `git cat-file blob`(或 `git archive`)产出的 **tracked-blob 原始字节**,非 checkout 工作树文件(`.gitattributes:5 * text=auto` 会按平台规范化 EOL 破恒等);bundle 文件集 = `git ls-files <skill-dir>` 的 tracked 文件,固定排序;CI `core.autocrlf=false` + 复算 hash == git 对象 hash。
- daemon 验 attestation → 解 bundle → 逐 blob 核对 hash → **byte-for-byte 写**(无 server buildSkillMd 重组——它注入 DB 可变 `owner_user_id`/`last_reviewed_at`,仅服务 `skill pull`,不在分发路径)。
- 可变元数据留 registry DB(web UI / lint-on-pull);源 SKILL.md 的静态 `owner: 曾振华`/`last_reviewed_at:<git值>` 是 blob 内容随 bundle 原样分发,不冲突。评审对象(git diff)== 落盘字节(invariant #1 保证)。
- manifest 绑 `(skill_name, git_commit, monotonic_version)` 进 attestation subject(M2 串扰)。

### 2.2 净新 daemon 写循环 · 写原语二分 · 互斥配置（RB-5/RB-6 = invariant #5/#6）
- daemon 现**不写盘**(local_skills.go 只读);⑩ 净新写循环单独威胁建模:server 分发选择 → daemon 拉签名 bundle → 验 → 写。
- 落盘原语**二分**(invariant #5):新建 `O_CREATE|O_EXCL|O_NOFOLLOW`;更新 `lstat` 普通文件→同目录 temp(`O_EXCL|O_NOFOLLOW`)→`rename` 原子覆盖;父链 `EvalSymlinks` 断言白名单根内;软链/非常规目标=确定性拒写+告警。
- dev/消费机**互斥落配置**(invariant #6):`MULTICA_DAEMON_SKILL_WRITE`(self-host 默认 off);写循环启动前断言无 sync 管理软链,冲突拒启+告警。
- daemon 二进制完整性=根 assumption(I4,§5)。

### 2.3 md 文档同 skill 路径
md(CLAUDE.md/AGENTS.md/skills-index)源 blob 进签名 bundle,daemon 验签 byte-for-byte 写 `~/.claude`/`~/.codex`,同 §2.2 写原语 + 互斥。

---

## 3 · 防降级/回滚/吊销

- **3.0 无 unsigned fallback**（invariant #3):缺/坏/降级 → fail-closed + 本地告警;验收含「删 attestation 资产→拒」。
- **3.1 防回滚(永久单调) + 防冻结(时效只降级不砖,可配)**（I2)。
- **3.2 吊销有真实签名来源 + 可检测 withholding**（invariant #8/RB-7):吊销表 = CI 签工件走 §1.4 门(吊销=发版),或 2-reviewer Environment 显式钥;heartbeat 带签名 max-age/计数检测扣留;本地持久化最高单调计数拒回放;**载体需启用稳态在线通道**(self-host 默认关 auto-update,须显式启用 + 吊销轮询)。

## 4 · 威胁模型 v4 = v3 表 + RB 修正
(沿用 v3 §4,叠加:upstream 同名工件→invariant #2 拒 · TUF root 过期→invariant #4 fail-closed · squash test-merge/sock-puppet→invariant #7 全谓词 · 首跳主动替换→§5 根 assumption · 吊销载体→invariant #8。)

## 5 · 信任边界与残留风险（诚实 · 第三轮强化）
- **daemon/CLI 二进制完整性 = 验签根**;本地同用户写权失陷不在保护范围。
- **install.sh 首跳 = 纯 TOFU**;首启自验不防主动替换(RB-3),真收窄需带外 install.sh 哈希锚。
- **upstream 同名 attestation 管线未门控**;切断仅靠 invariant #2 消费端断言(RB-1)。
- **CI 失陷**:keyless 把失陷面抬到「攻破 GitHub OIDC + 过 §1.4 评审门」,固有边界。
- **gh-api 自检**不防主动改 release.yml;靠 invariant #10 的 CODEOWNERS+ruleset。
- **完全离线砖机**:TUF root 过期 / 旧钥泄露冻结,靠带外 re-bootstrap 收敛。

## 6 · 验收标准 v4（第四阶段对抗验收 = 实现闭合裁定）
- [ ] 二进制⑨:install 首跳 TOFU + 首启自验;`multica update` 强制验 attestation(三元组);注入篡改归档/伪造 checksum/缺 bundle/降级/过期/**upstream-OIDC 合法工件**/**TUF root 过期** → 全 fail-closed 拒 + 本地告警;合法 → 验过替换。
- [ ] skill/md⑩:改 skill 经 2-review **合并** + CI attestation 签 **git blob** bundle → daemon ≤2×ticker 无感 byte-for-byte 落盘(touch-reviewed 改 DB 后仍验过=证 buildSkillMd 不在路径);注入未签/伪造/降级/陈旧/**穿越**/**预置软链(拒非跳过)**/**跨skill串扰** → 全拒+本地告警。
- [ ] release:未合并 PR test-merge sha 打 tag → 拒;reviewer==pusher/author/bot → 拒(invariant #7)。
- [ ] `gh api` 断言 main+tag ruleset bypass 空 + `.github` 受 CODEOWNERS required-review(invariant #10)。
- [ ] daemon 断网 Fulcio/Rekor 仍验 bundle(sigstore-go 离线);TUF root 过期 → 拒非 fail-open(invariant #4)。
- [ ] 写循环新建/更新原语二分正确;dev/消费机互斥配置生效不 clobber(invariant #5/#6)。
- [ ] grep + 对抗注入双证:无任何 unsigned/SHA-only fallback 分支(invariant #3)。

## 7 · 实现(greenfield · 第四阶段)
全栈净新:CI(attest 二进制 + 打包/签 git-blob skill bundle + invariant #7 合并门 + CODEOWNERS/ruleset)· daemon(写循环 + sigstore-go 离线验栈 + 内置 TUF root + 互斥配置 + 吊销轮询)· update.go(强制验 attestation)· install.sh(TOFU 诚实 + 首启自验)· server(分发选择端点)。实现走 Workflow 扇出 + 对抗验收(§6)+ 独立 code review(对照 §0 10 invariants)。**本 v4 = APPROVED 设计,实现期不再回开设计评审,以 §6 对抗验收裁定闭合。**
