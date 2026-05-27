# autopilots/

multica autopilot 定义的 YAML 模板。

**重要**: `multica autopilot create` 不会读取 YAML 文件 —— 它接收 CLI flags。
具体看 `scripts/apply-autopilots.sh`，它会解析这些 YAML 并翻译成
`multica autopilot create / trigger-add` 调用。

| 文件 | 时间 | 模式 | 用途 |
| --- | --- | --- | --- |
| daily-summary.yaml | 工作日 18:00 (Asia/Shanghai) | run_only | 每日总结推送到飞书 |
| monday-kickoff.yaml | 周一 09:30 (Asia/Shanghai) | create_issue | 每周计划汇总 |
| wednesday-stats.yaml | 周三 09:00 (Asia/Shanghai) | run_only | CLAUDE.md 周度统计 |
| monthly-health.yaml | 每月 1 号 10:00 (Asia/Shanghai) | run_only | 触发 monthly_health_report |

## 必需的 env vars (在每个 agent 的 custom-env 中设置)

飞书集成使用 [feishu-cli](https://github.com/riba2534/feishu-cli)。安装、
scope 配置和 setup 看 `docs/integrations/feishu-cli.md`。

- `FEISHU_TEAM_CHAT_ID` —— 主团队群 chat_id (oc_xxx)，用于每日/每周/每月推送
- `FEISHU_DEMO_CHAT_ID` —— 可选 · 周五 demo 用的独立群
- `FEISHU_TEAM_WIKI_SPACE` —— 可选 · 用于归档月度健康报告的 wiki space
- `FEISHU_HEALTH_REPORTS_NODE` —— 可选 · 健康报告归档的 wiki 父节点
- `FEISHU_CONFIG_DIR` —— 默认 `~/.feishu-cli` · workstation 共享配置

每台 EXEC workstation 必须先运行一次 `feishu-cli config create-app --save` 和
`feishu-cli doctor`，autopilot 才能正常推送。
