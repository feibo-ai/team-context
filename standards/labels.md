# 团队标签字典 (multica issue labels)

**Owner**: DRI
**Last reviewed**: 2026-05-26
**Source of truth**: 本文件 · 加新 label 必须更新这里 + 开 PR

## 11 个核心 label

| Label | 颜色 | 含义 | 加 / 删时机 | 谁加 |
|---|---|---|---|---|
| `plan-draft` | `#94A3B8` gray | plan markdown 已生成、未 review | `plan_create` 自动加 | MCP 工具 |
| `plan-under-review` | `#F59E0B` amber | 已请 reviewer，等 verdict | `plan_request_review` 加 + `plan-draft` 不动 | MCP 工具 |
| `plan-approved` | `#10B981` green | SOP 非妥协 #1 通过 · implement 可启动 | `plan_approve` 加 | MCP 工具 |
| `plan-upgraded` | `#A855F7` purple | plan 升级到 v1.x · 需重新 review | `plan_upgrade` 加 + 重新加 `plan-draft` | MCP 工具 |
| `debrief` | `#3B82F6` blue | case file 已生成 · 待 review section 4 | `case_create` 加 | MCP 工具 |
| `debrief-reviewed` | `#059669` deep-green | section 4 DRI 签字 · issue 可 close | `case_review` 加 | MCP 工具 |
| `ancient-impossible` | `#EC4899` pink | "在传统 5 人团队不可能"的事件 · AI Native 终极指标 | 团队成员手工加 / 月度复盘加 | 任何人 |
| `betting-table` | `#F97316` orange | 周五 betting table issue | `betting_table_capture` 加 | MCP 工具 |
| `burnout-alert` | `#DC2626` red | burnout check 任何 yes → 自动建 issue | `burnout_check_distribute` 加 | MCP 工具 |
| `code-review` | `#8B5CF6` violet | code review 请求 issue | `code_review_request` 加 | MCP 工具 |
| `research` | `#06B6D4` cyan | RPI Research session 产物 issue | `research_create` 加 | MCP 工具 |

## State Machine (核心 issue 路径)

```
新项目 issue
  └─> [plan_create] ──> plan-draft
       └─> [plan_request_review] ──> plan-under-review (+plan-draft)
            └─> [plan_approve] ──> plan-approved
                 │
                 ├─> [implement work happens]
                 │
                 ├─> [plan_upgrade if 卡住 30 分钟] ──> plan-upgraded + plan-draft (重新 review)
                 │
                 └─> [case_create on完工] ──> debrief
                      └─> [case_review by DRI] ──> debrief-reviewed
                           └─> [issue close 允许]
```

## 创建脚本（W1 Plan 1 EXEC 跑一次）

```bash
#!/usr/bin/env bash
# create-labels.sh — populate the 11 standard labels in multica workspace
# Uses parallel arrays instead of `declare -A` so it runs on macOS's bash 3.2.
set -euo pipefail

NAMES=(
  plan-draft
  plan-under-review
  plan-approved
  plan-upgraded
  debrief
  debrief-reviewed
  ancient-impossible
  betting-table
  burnout-alert
  code-review
  research
)
COLORS=(
  "#94A3B8"
  "#F59E0B"
  "#10B981"
  "#A855F7"
  "#3B82F6"
  "#059669"
  "#EC4899"
  "#F97316"
  "#DC2626"
  "#8B5CF6"
  "#06B6D4"
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

## 加新 label 规则

1. 写到本文件先（PR review）
2. PR merge 后跑 `multica label create --name X --color #YYY`
3. 月度健康度报告自动 diff: 当前 workspace labels vs 本文件 · 不一致告警

## 不要做

- ❌ 直接在 multica web UI 改 label 颜色 · 必须改本文件 + 重跑 create-labels.sh
- ❌ 创建本文件没列的 label · 长期下来分散语义、查询匹配不上
- ❌ 给 `plan-approved` issue 同时加 `plan-draft` (state machine 违反)
