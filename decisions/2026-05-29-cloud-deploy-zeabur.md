# Decision · multica 控制面从 DRI mac 迁到 Zeabur 云

**Date**: 2026-05-29 (记录日 · 实际迁移在 2026-05-28 W5 cloud bootstrap)
**DRI**: feibo
**Status**: decided
**Supersedes**: Decision D-H of `2026-05-29-multica-control-plane.md`（"不做 k8s · DRI mac 跑 docker compose"）+ 该文 Remote "容器化 · DRI mac 跑" 的部署假设

> ⚠️ 本 ADR 的 **Context（为什么迁）由 DRI 确认 / 补充** —— 下面动机是从现状
> （`docs/ONBOARDING-DRI.md` 拓扑表 + `multica/docs/superpowers/specs/2026-05-28-personal-autopilot-script-spec.md` §2.1）
> 反推的,可能不完整。拓扑事实部分（Decision 段）已上线验证。

## Context

W5 之前（`2026-05-29-multica-control-plane.md` · Decision D-H）的部署假设:
- `multica-backend` / `multica-web` / `tcmcp-remote` 以 docker compose 跑在 **DRI 的 mac**（`localhost:8443` · LAN `10.0.5.51:8443`）
- "5 人团队不需要 k8s",DRI mac 即部署环境

这个模型暴露的问题（**推断 · 待 DRI 确认**）:
1. **单点 / 可用性** — 服务绑在 DRI 一台 mac 上 · mac 关机 / 睡眠 / 重启 → 全队 multica backend + web + 飞书推送中断
2. **LAN 依赖** — `tcmcp-remote` 走 `10.0.5.51` LAN IP · 远程 / 异地成员够不着
3. **没有独立 always-on 环境** — 不只是 autopilot · backend/web 也依赖 DRI 在场

## Decision

把 **multica 后端 + web + tcmcp-remote** 迁到 **Zeabur 云**（BYOC · Aliyun SG · server `AI-Gateway` · `43.106.62.232`）:

- Zeabur project `teamctx` · 4 个 service: `postgresql(pgvector) / multica-backend / multica-web / tcmcp-remote`
- 3 个公网域名（Cloudflare actionow.ai 区）: `api.teamctx.actionow.ai`（REST+WS）· `teamctx.actionow.ai`（web）· `mcp.teamctx.actionow.ai`（MCP）
- **不变**: `multica daemon` + codex/claude/hermes runtime + `tcmcp-local`（12 个 git+file 工具）**仍在各成员 / DRI 的 mac** —— daemon 离线 → 该人 autopilot 当天静默 skip（见 spec §1.3）
- integration / secret / config 仍由 multica 控制面管理（v2 其余设计不变）

## Options considered

- **A. 保持 DRI mac docker compose**（D-H 现状）: 零迁移成本 · 但单点 + LAN 依赖不解决 · 弃
- **B. 迁 Zeabur BYOC**: 本决定 · 中等迁移成本 · always-on + 公网可达
- **C. 上 k8s**: 5 人团队过重（D-H 已拒 · 本决定继承）· 弃

## Trade-offs accepted

- 引入云依赖 + 月度成本（Zeabur Resource Usage · 见 ONBOARDING-DRI §5）
- BYOC 在 Aliyun SG · 数据出 DRI mac
- daemon / runtime 仍在 mac（没全云化）→ autopilot 离线 skip 语义保留

## Trade-offs rejected

- 不全云化 daemon / runtime: agent 执行 + `tcmcp-local` 的 git/file 操作天然要在成员本地 working tree · 留 mac
- 不上 k8s（同 D-H）

## Rollback

上线后 **< 7 天** 可临时拉回 `10.0.5.51` 本地 multica（`multica config set server_url` + `docker compose -f docker-compose.selfhost.yml up`）· 前提 `10.0.5.51` 的 `pgdata` volume 还在（承诺 7 天才删）· 详见 ONBOARDING-DRI §7。
**过 7 天（约 2026-06-04）此回退失效。**

## Review trigger

- **2026-06-04**: 确认云端稳定后 · 清理 `10.0.5.51` docker volume + 删 ONBOARDING-DRI §7 回退段
- 月度健康度: Zeabur 成本 vs DRI mac 自托管 · 是否仍值得
