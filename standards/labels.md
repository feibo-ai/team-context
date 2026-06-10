# 团队标签字典 (multica issue labels)

**Owner**: DRI
**Last reviewed**: 2026-06-10
**Source of truth**: 本文件 · 加新 label 必须更新这里 + 开 PR
**转换执行者收口**: label/status 流转一律走 `skills/tc-render/transition.py`(或 publish.py 发布时自动),**不再手敲 `multica issue label/status` 散文命令**——CLI 的 `issue label add` 只收 label UUID,按名称的手敲命令本就跑不通;transition.py 内置 name→UUID 运行时解析 + 后置复核(P-7)。

## 11 个核心 label

| Label | 颜色(=线上实际 · 2026-06-10 核对) | 含义 | 加 / 删时机 | 谁执行 |
|---|---|---|---|---|
| `计划-草稿` | `#9ca3af` 灰 | plan 已发布、未请审 | publish.py 发布 plan 时自动加(仅当 issue 无任何 计划-* label;重发 v2 不重打) | publish.py→transition.py |
| `计划-评审中` | `#f59e0b` 琥珀 | 已派评审子 agent,等 verdict | `transition.py plan-request-review` 加(+status `in_review`);批准/取消时摘 | transition.py |
| `计划-已批准` | `#10b981` 绿 | SOP 非妥协 #1 通过 · **待启动**(开工另有动作) | `transition.py plan-approve` 加,同时摘 草稿/评审中/**已升级**,status `todo` | transition.py |
| `计划-已升级` | `#8b5cf6` 紫 | plan 升级 · 需重新 review | `transition.py plan-upgrade` 加(摘已批准 · 加已升级+草稿 · status `todo`);re-approve 时被 plan-approve 摘除(防与已批准并存) | transition.py |
| `复盘-待审` | `#f97316` 橙 | case 已发布 · 待 review section 4 | publish.py 发布 case 时自动加(+status `in_review`;仅当无 复盘-已审) | publish.py→transition.py |
| `复盘-已审` | `#14b8a6` 青绿 | section 4 评审通过 · issue 已关 | `transition.py case-finalize` 加(摘待审 · status `done` · 父链连带) | transition.py |
| `古法不可能` | `#ef4444` 红 | "在传统 5 人团队不可能"的事件 · AI Native 终极指标 | 团队成员手工加 / 月度复盘加 | 任何人 |
| `投注表` | `#ec4899` 粉 | 周五 betting table issue | `betting_table_capture` 加 | remote MCP |
| `倦怠预警` | `#dc2626` 深红 | burnout check 任何 yes → 自动建 issue | `burnout_check_distribute` 加 | remote MCP |
| `代码评审` | `#6366f1` 靛 | code review 请求 issue | `code_review_request` 加 | remote MCP |
| `研究` | `#3b82f6` 蓝 | RPI Research session 产物 issue | publish.py 发布 research 时自动加(findings 非空 → status `done`) | publish.py→transition.py |

> 注:`plan_request_review`(remote MCP)的 **label 写路径已废弃**——请审统一走 `transition.py plan-request-review`,避免双写者打架。remote MCP 仍负责飞书侧通知与 投注表/倦怠预警/代码评审 三个 label。
> 颜色列 2026-06-10 与线上一次性对齐(此前 8/11 漂移);改色仍须先改本文件再重跑 create-labels.sh。

## State Machine(label 轨 + status 轨 · 双轨同图)

```
issue create(status 默认 todo)
  └─> [publish.py --type plan]        label: +计划-草稿              status: todo
       └─> [plan-request-review]      label: +计划-评审中            status: in_review   ← 派评审子 agent
            ├─ approved ─> [plan-approve]
            │                         label: +已批准 −草稿−评审中−已升级  status: todo(待启动)
            │    └─> [build-start]    label: 不变                    status: in_progress  ← 首个 build session(开工卡同时机)
            │         ├─> [plan-upgrade(卡住30分钟/实质改方案)]
            │         │              label: +已升级+草稿 −已批准      status: todo → 重走 request-review
            │         └─ 完工 ─> [publish.py --type case(case issue)]
            │                         label: +复盘-待审              status: in_review   ← 派评审子 agent
            │              └─ approved ─> [case-finalize]
            │                         case:  +复盘-已审 −复盘-待审    status: done
            │                         父plan: −未决流程label(保留已批准) status: done
            │                         祖父research: 尽力 done(legacy 兜底;--keep-parent 跳过父链)
            └─ kill ─> [cancel]       label: −全部流程label           status: cancelled

research issue: [publish.py --type research] → +研究;findings 非空即 status done(不挂账)
```

**in_review 的双语义**(查询一律 label 驱动,status 只是粗轨,勿用裸 `--status in_review` 查询):
- plan issue + `计划-评审中` = plan 评审中
- case issue + `复盘-待审` = case 待审

**执行者绑定原则**:评审/测试由**子 agent**承担(全新上下文 = SOP「第二个 session」);
verdict 返回到编排 session 的那一刻 = 转换执行点(plan-approve / case-finalize 当场跑)。
子 agent 只产出 verdict、不碰状态;转换权始终归编排 session。

## 不变量(issue_invariants.py 巡检 · skills/tc-ops/)

硬性不变量(违规即漂移,适用于**带流程 label** 的 issue;零 label 轻任务不在审计内):

| # | 不变量 | 抓的漂移型 |
|---|---|---|
| 1 | `复盘-已审` ⇒ status `done` | TEA-95/70 型(收尾块漏跑) |
| 2 | `复盘-待审` ⇒ status `in_review` | TEA-62/33 型(乱序)+ TEA-94/54 型(滞留 todo) |
| 3 | `计划-评审中` ⇒ status `in_review` | TEA-66 型 |
| 4 | `计划-已批准` ⇒ status ∈ {`todo`,`in_progress`,`done`} | 批准后被错误回退 |
| 5 | status `cancelled` ⇒ 无任何流程 label | TEA-75/69 型(取消不清场) |
| 6 | `计划-已升级` ⊕ `计划-已批准` 互斥 | TEA-79/28/22/14 型(approve 不摘已升级) |

警告档(不算违规,提示人看):
- **staleness**:`计划-评审中` 或 `复盘-待审` 挂超 48h——编排 session 在 verdict 后死亡的残留态
- **盲区**:标题前缀 `计划:`/`研究:`/`复盘:` 却无任何入口 label(流程 label ∪ `研究`)——入口转换缺失(TEA-90/82 型;调研中的空 research issue 命中属预期:没发布就是没交付)
- **研究未关**:带 `研究` label 但 status≠done——研究发布即 done 语义,legacy 滞留

巡检必须**分页拉全**(`--limit/--offset` 循环至 `has_more=false`)——默认一页 50 条,只看第一页曾把 91 个 issue 看成 50 个。

## 创建脚本（W1 Plan 1 EXEC 跑一次）

```bash
#!/usr/bin/env bash
# create-labels.sh — populate the 11 standard labels in multica workspace
# Uses parallel arrays instead of `declare -A` so it runs on macOS's bash 3.2.
set -euo pipefail

NAMES=(
  计划-草稿
  计划-评审中
  计划-已批准
  计划-已升级
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

保存到 `~/team-context/scripts/create-labels.sh` · 跑一次 · 月度健康度报告检查这 11 个 label 是否仍全部存在 (没人手贱删了)。
**transition.py 依赖这 11 个 label 存在**(name→UUID 运行时解析,缺失即 exit 1 并指向本脚本)。

## 加新 label 规则

1. 写到本文件先（PR review）
2. PR merge 后跑 `multica label create --name X --color #YYY`
3. 月度健康度报告自动 diff: 当前 workspace labels vs 本文件 · 不一致告警

## 不要做

- ❌ 直接在 multica web UI 改 label 颜色 · 必须改本文件 + 重跑 create-labels.sh
- ❌ 创建本文件没列的 label · 长期下来分散语义、查询匹配不上
- ❌ 给 `计划-已批准` issue 同时加 `计划-草稿` 或 `计划-已升级`(不变量 #6 · state machine 违反)
- ❌ 手敲 `multica issue label add <issue> <名称>`——只收 UUID,跑不通;走 transition.py
- ❌ 用裸 `--status` 做流程查询(in_review 双语义)· 查询一律 label 驱动
