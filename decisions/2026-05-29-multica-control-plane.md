# Decision · multica 升级成 SOP 平台的 control plane

**Date**: 2026-05-29
**DRI**: <你的名字>
**Status**: decided
**Supersedes**: parts of 2026-05-26-v0.2-launch.md (specifically the per-EXEC feishu-cli + .env model)

## Context

W1 设计假设：
- 每个团队成员本地装 feishu-cli + 各自扫码 + 各自开 scope
- secret 散在每人 `~/.feishu-cli/config.yaml`
- MCP server 是个人 stdio 实例 · 每人本地 build + 跑

W2-W3 真实使用后暴露 3 个问题：
1. **Secret 漂移**: 5 个成员的 scope 配置不一致 (有人没开 wiki:wiki · monthly-health 推不上 wiki)
2. **离职吊销难**: 没办法批量吊销个人 feishu app secret
3. **per-user daily summary 阻塞**: 需要 team_members 列表的唯一权威源 · 找不到该放哪
4. **配置改一次要找 5 人**: chat_id / wiki_space_id 等变更要每人改 `.env`

## Decision

Multica 升级成 **control plane**:
- 新 3 类对象: Integration (config) · Secret (encrypted) · Deployment (runtime tracker)
- WebSocket `integration.config-changed` 事件广播
- DRI 在 multica web UI / CLI 集中管理

team-context-mcp 重构成 **HTTP/SSE 远程 + 本地 stdio split**:
- Remote (9 工具 · 含 4 新飞书工具) · 容器化 · DRI mac 跑
- Local (12 工具 · git+file) · 团队成员各自跑
- ConfigSource 抽象 · 启动时拉 multica · WS 订阅 hot-reload
- 用 `@larksuiteoapi/node-sdk` 替代 `feishu-cli` shell-out

team-context (本仓库) · 角色转变成 **spec source**:
- standards/integration-schemas/ · schema 定义 (DRI PR review)
- autopilots/*.yaml · 通过 integration_ref 引用 multica integration · 不再含 secret
- scripts/multica-secrets-bootstrap.sh · 一次性脚本 · env-file → multica secret

## Options considered

- **A. 保持现状 + 加 1Password 同步**: 集中 secret 但不解决配置漂移 · 弃
- **B. 全远程 (Codespaces 模型)**: 解决一切但要求团队完全切远程开发 · 12 个月路线
- **C. Control plane + 拆 MCP**: 这个决定 · 中等改动 · 立即可用
- **D. 不改 · 累积 1 个月再说**: workspace 已经有 5 人 · 越拖越难改

## Trade-offs accepted

- multica fork 改动 ~5 天 (Plan 4)
- team-context-mcp 重构 ~7 天 (Plan 5)
- team-context 整合 ~1.5 天 (本 plan)
- 短期 +13.5 工时 · 中期 ops 体验 / 离职安全 / 配置一致性显著提升

## Trade-offs rejected

- 不做加密 KMS / Vault · 只用 env-file master key (Decision D-G) · v0 简化 · v1 后再说
- 不做 k8s · DRI mac 跑 docker compose (Decision D-H) · 5 人团队不需要 k8s
- 不回推 multica-ai 上游 (Decision D-J) · 内部专属 · 上游接不接受不知道

## Operational notes

- autopilot-bot user token rotated every 90d (`multica auth issue-token --user-email autopilot-bot@aimiq --name "autopilot-bot-<YYYY>-q<N>"`)
  + re-run `apply-autopilots.sh` to re-inject. Calendar reminder lives in monthly-health autopilot output.

## Review trigger

- W12 月度健康度报告中检查:
  - secret rotation 真在用 (audit_logs 含 secret.set/rotated)
  - per-user daily summary 接收率 (5 人各收 1 条 P2P · 收满)
  - 接入新成员时间 · 应 ≤ 5 min (替换原 30 min)
- 如果 audit_logs 显示 W6-W12 没人 rotate 过任何 secret · 说明 control plane 设计过度 · 简化
