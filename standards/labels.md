# 团队标签字典 (multica issue labels)

**Owner**: DRI
**Last reviewed**: 2026-05-26
**Source of truth**: 本文件 · 加新 label 必须更新这里 + 开 PR

## 11 个核心 label

| Label | 颜色 | 含义 | 加 / 删时机 | 谁加 |
|---|---|---|---|---|
| `计划-草稿` | `#94A3B8` 灰 | plan markdown 已生成、未 review | `tc-3-plan`+publish.py 发布时 | skill/CLI |
| `计划-评审中` | `#F59E0B` 琥珀 | 已请 reviewer，等 verdict | `plan_request_review` 加 + `计划-草稿` 不动 | MCP 工具 |
| `计划-已批准` | `#10B981` 绿 | SOP 非妥协 #1 通过 · implement 可启动 | 批准转换 `multica issue label add` | skill/CLI |
| `计划-已升级` | `#A855F7` 紫 | plan 升级到 v1.x · 需重新 review | publish.py 再发新版 + 重新加 `计划-草稿` | skill/CLI |
| `复盘-待审` | `#3B82F6` 蓝 | case file 已生成 · 待 review section 4 | `tc-5-review`+publish.py 发布时 | skill/CLI |
| `复盘-已审` | `#059669` 深绿 | section 4 DRI 签字 · issue 可 close | `tc-5-review` 收尾 `multica issue label` | skill/CLI |
| `古法不可能` | `#EC4899` 粉 | "在传统 5 人团队不可能"的事件 · AI Native 终极指标 | 团队成员手工加 / 月度复盘加 | 任何人 |
| `投注表` | `#F97316` 橙 | 周五 betting table issue | `betting_table_capture` 加 | MCP 工具 |
| `倦怠预警` | `#DC2626` 红 | burnout check 任何 yes → 自动建 issue | `burnout_check_distribute` 加 | MCP 工具 |
| `代码评审` | `#8B5CF6` 紫罗兰 | code review 请求 issue | `code_review_request` 加 | MCP 工具 |
| `研究` | `#06B6D4` 青 | RPI Research session 产物 issue | `tc-2-research`+publish.py | skill/CLI |

## State Machine (核心 issue 路径)

```
新项目 issue
  └─> [tc-3-plan] ──> 计划-草稿
       └─> [plan_request_review] ──> 计划-评审中 (+计划-草稿)
            └─> [批准转换] ──> 计划-已批准
                 │
                 ├─> [implement work happens]
                 │
                 ├─> [plan 升级 if 卡住 30 分钟] ──> 计划-已升级 + 计划-草稿 (重新 review)
                 │
                 └─> [tc-5-review on完工] ──> 复盘-待审
                      └─> [tc-5-review 评审 by DRI] ──> 复盘-已审
                           └─> [issue close 允许]
```

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
- ❌ 给 `计划-已批准` issue 同时加 `计划-草稿` (state machine 违反)
