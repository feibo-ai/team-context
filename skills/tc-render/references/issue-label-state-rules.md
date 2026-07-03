# issue-label-state-rules — 团队 label 字典 + issue 状态机 + 谁写什么(单源;加新 label 必须先改本文件 + 开 PR)。

**转换执行者收口**:label/status 流转一律走 tc-render 的 `scripts/transition.py`(或 publish 脚本发布时自动),**禁止手敲 `multica issue label/status` 散文命令**——CLI 的 `issue label add` 只收 label UUID,按名称的手敲命令本就跑不通;transition 脚本内置 name→UUID 运行时解析 + 后置复核(写后重读断言)。

## 13 个核心 label

| Label | 颜色 | 含义 | 加 / 删时机 | 谁执行 |
|---|---|---|---|---|
| `计划-草稿` | `#9ca3af` 灰 | plan 已发布、未请审 | publish 发布 plan 时自动加(仅当 issue 无任何 计划-* label;重发 v2 不重打) | publish→transition |
| `计划-评审中` | `#f59e0b` 琥珀 | 已派评审子 agent,等 verdict | `plan-request-review` 加(+status `in_review`);批准/取消时摘 | transition |
| `计划-已批准` | `#10b981` 绿 | plan 评审门通过 · **待启动**(开工另有动作) | `plan-approve` 加,同时摘 草稿/评审中/**已升级**,status `todo` | transition |
| `计划-已升级` | `#8b5cf6` 紫 | plan 升级 · 需重新 review | `plan-upgrade` 加(摘已批准 · 加已升级+草稿 · status `todo`);re-approve 时被 plan-approve 摘除(防与已批准并存) | transition |
| `设计-待审` | `#eab308` 黄 | 设计评审中(批准后·开工前)· 等 verdict | `design-request-review` 加(+status `in_review` · 摘在场 设计-已审=复审作废旧批准);approve/cancel 时摘 | transition |
| `设计-已审` | `#0ea5e9` 天蓝 | 设计评审通过 · 可开工(与 计划-已批准 共存,历史事实) | `design-approve` 加(摘待审 · status `todo` 回待启动) | transition |
| `复盘-待审` | `#f97316` 橙 | case 已发布 · 待 review 关键判断段 | publish 发布 case 时自动加(+status `in_review`;仅当无 复盘-已审) | publish→transition |
| `复盘-已审` | `#14b8a6` 青绿 | 关键判断段评审通过 · issue 已关 | `case-finalize` 加(摘待审 · status `done` · 父链连带) | transition |
| `古法不可能` | `#ef4444` 红 | 「在传统 5 人团队不可能」的事件 · AI Native 终极指标 | 团队成员手工加 / 月度复盘加 | 任何人 |
| `投注表` | `#ec4899` 粉 | 周五 betting table issue | `betting_table_capture` 加 | remote MCP |
| `倦怠预警` | `#dc2626` 深红 | burnout check 任何 yes → 自动建 issue | `burnout_check_distribute` 加 | remote MCP |
| `代码评审` | `#6366f1` 靛 | code review 请求 issue | `code_review_request` 加 | remote MCP |
| `研究` | `#3b82f6` 蓝 | RPI Research session 产物 issue | publish 发布 research 时自动加(findings 非空 → status `done`) | publish→transition |

> 谁写什么:流程 label(计划-*/设计-*/复盘-*/研究)只由 transition 脚本写;remote MCP 只负责飞书侧通知与 投注表/倦怠预警/代码评审 三个 label(`plan_request_review` 的 label 写路径已废弃,请审统一走 `plan-request-review` 子命令,避免双写者打架)。
> 颜色以本文件为准;改色须先改本文件再重跑 create-labels.sh(见下)。

## State Machine(label 轨 + status 轨 · 双轨同图)

```
issue create(status 默认 todo)
  └─> [publish --type plan]           label: +计划-草稿              status: todo
       └─> [plan-request-review]      label: +计划-评审中            status: in_review   ← 派评审子 agent
            ├─ approved ─> [plan-approve]
            │                         label: +已批准 −草稿−评审中−已升级  status: todo(待启动 · 不碰 设计-*)
            │    ├─> [design-request-review(设计评审门 · 项目层必走/任务层可跳)]
            │    │                    label: +设计-待审 −设计-已审    status: in_review   ← 派设计评审子 agent
            │    │    └─ approved ─> [design-approve]
            │    │                    label: +设计-已审 −设计-待审    status: todo(回待启动)
            │    └─> [build-start]    label: 不变                    status: in_progress  ← 首个 build session(开工卡同时机;
            │         │                                                设计-待审 在场时告警「评审未完成就开工」)
            │         ├─> [plan-upgrade(卡住30分钟/实质改方案)]
            │         │              label: +已升级+草稿 −已批准      status: todo → 重走 request-review
            │         └─ 完工 ─> [publish --type case(case issue)]
            │                         label: +复盘-待审              status: in_review   ← 派评审子 agent
            │              └─ approved ─> [case-finalize]
            │                         case:  +复盘-已审 −复盘-待审    status: done
            │                         父plan: −未决流程label(草稿/评审中/已升级/设计-待审 · 保留已批准+设计-已审) status: done
            │                         祖父research: 尽力 done(legacy 兜底;--keep-parent 跳过父链)
            └─ kill ─> [cancel]       label: −全部流程label(含设计对)  status: cancelled

research issue: [publish --type research] → +研究;findings 非空即 status done(不挂账)
```

**in_review 的三语义**(查询一律 label 驱动,status 只是粗轨,勿用裸 `--status in_review` 查询):
- plan issue + `计划-评审中` = plan 评审中
- work issue + `设计-待审` = 设计评审中(此时 `计划-已批准` 共存合法 → 不变量 #4 的 carve-out)
- case issue + `复盘-待审` = case 待审

**执行者绑定原则**:评审/测试/任务层执行由**子 agent**承担(全新上下文的独立 session);
verdict/交付返回到编排 session 的那一刻 = 动作执行点(plan-approve / case-finalize / commit 当场做)。
子 agent 只产出 verdict 或工作产物、**不碰状态、不 commit**;转换权与 commit 权始终归编排 session。

## 不变量(tc-ops skill 的 issue 巡检脚本核查 · 已编入 monthly-health autopilot,report-only 随月度健康卡推飞书;--strict 留给验收/CI)

硬性不变量(违规即漂移,适用于**带流程 label** 的 issue;零 label 轻任务不在审计内):

| # | 不变量 | 抓的漂移型 |
|---|---|---|
| 1 | `复盘-已审` ⇒ status `done` | 收尾块漏跑 |
| 2 | `复盘-待审` ⇒ status `in_review` | 乱序 / 滞留 todo |
| 3 | `计划-评审中` ⇒ status `in_review` | 请审不置 status |
| 4 | `计划-已批准` ⇒ status ∈ {`todo`,`in_progress`,`done`};**`设计-待审` 在场时另允许 `in_review`**(carve-out:设计评审中=已批准+in_review 合法) | 批准后被错误回退 |
| 5 | status `cancelled` ⇒ 无任何流程 label | 取消不清场 |
| 6 | `计划-已升级` ⊕ `计划-已批准` 互斥 | approve 不摘已升级 |
| 7 | `设计-待审` ⇒ status `in_review` | 设计评审挂起/乱序 |
| 8 | `设计-待审` ⊕ `设计-已审` 互斥 | 复审不作废旧批准(由 design-request-review 摘除保证) |

警告档(不算违规,提示人看):
- **staleness**:`计划-评审中` / `设计-待审` / `复盘-待审` 挂超 48h——编排 session 在 verdict 后死亡的残留态
- **盲区**:标题前缀 `计划:`/`研究:`/`复盘:` 却无任何入口 label(流程 label ∪ `研究`)——入口转换缺失(调研中的空 research issue 命中属预期:没发布就是没交付)
- **研究未关**:带 `研究` label 但 status≠done——研究发布即 done 语义,legacy 滞留

巡检必须**分页拉全**(`--limit/--offset` 循环至 `has_more=false`)——默认一页 50 条,只看第一页会把 91 个 issue 看成 50 个。

## 创建脚本 create-labels.sh(workspace 缺标准 label 时重建;transition 脚本解析失败会指向这里)

```bash
#!/usr/bin/env bash
# create-labels.sh — populate the 13 standard labels in multica workspace
# Uses parallel arrays instead of `declare -A` so it runs on macOS's bash 3.2.
set -euo pipefail

NAMES=(
  计划-草稿
  计划-评审中
  计划-已批准
  计划-已升级
  设计-待审
  设计-已审
  复盘-待审
  复盘-已审
  古法不可能
  投注表
  倦怠预警
  代码评审
  研究
)
COLORS=(
  "#9ca3af"
  "#f59e0b"
  "#10b981"
  "#8b5cf6"
  "#eab308"
  "#0ea5e9"
  "#f97316"
  "#14b8a6"
  "#ef4444"
  "#ec4899"
  "#dc2626"
  "#6366f1"
  "#3b82f6"
)

for i in "${!NAMES[@]}"; do
  name="${NAMES[$i]}"
  color="${COLORS[$i]}"
  existing=$(multica label list --output json | jq -r ".[] | select(.name==\"${name}\") | .id" || echo "")
  if [[ -z "${existing}" ]]; then
    echo "Creating: ${name} (${color})"
    multica label create --name "${name}" --color "${color}" >/dev/null
  else
    echo "Exists:   ${name} (${existing})"
  fi
done

echo ""
echo "Done. Verify: multica label list"
```

月度健康度报告检查这 13 个 label 是否仍全部存在(没人手贱删了)。
**transition 脚本依赖这 13 个 label 存在**(name→UUID 运行时解析,缺失即 exit 1 并指向本脚本)。

## 加新 label 规则

1. 写到本文件先(PR review)
2. PR merge 后跑 `multica label create --name X --color #YYY`
3. 月度健康度报告自动 diff:当前 workspace labels vs 本文件 · 不一致告警

## 不要做

- ❌ 直接在 multica web UI 改 label 颜色 · 必须改本文件 + 重跑 create-labels.sh
- ❌ 创建本文件没列的 label · 长期下来分散语义、查询匹配不上
- ❌ 给 `计划-已批准` issue 同时加 `计划-草稿` 或 `计划-已升级`(不变量 #6 · state machine 违反)
- ❌ 给 `设计-待审` issue 同时加 `设计-已审`(不变量 #8 · 复审先走 design-request-review 作废旧批准)
- ❌ 手敲 `multica issue label add <issue> <名称>`——只收 UUID,跑不通;走 transition 脚本
- ❌ 用裸 `--status` 做流程查询(in_review 三语义)· 查询一律 label 驱动
