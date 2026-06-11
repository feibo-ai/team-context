# multica 字段填写默认值(agent 不问自动填 · 单源)

**Owner**: DRI
**Last reviewed**: 2026-06-11
**适用**: 所有经 CLI 建/改 project、issue 的 agent 流程(tc-1-start / tc-2-research / tc-3-plan / tc-5-review 等)。
**原则**: 人字段默认**当前用户**、运行时解析、绝不询问;预测性字段宁空勿假;状态/label **禁止手填**(走 transition.py)。

## 当前用户解析配方(每台机器解析到各自的人 · 禁止硬编码任何 UUID)

```bash
ME_EMAIL=$(multica auth status 2>&1 | sed -n 's/.*(\(.*\)).*/\1/p')   # auth status 输出走 stderr,2>&1 必带
ME_NAME=$(multica user list --output json | jq -r --arg e "$ME_EMAIL" '.[]|select(.email==$e)|.name')
ME_UID=$( multica user list --output json | jq -r --arg e "$ME_EMAIL" '.[]|select(.email==$e)|.id')
```

> ⚠️ **两套人员 ID 空间**:`project --dri` 收 **user UUID**(`multica user list` 的 id);
> issue 的 assignee 解析到 **member UUID**(另一空间)。名字类 flag(`--assignee`/`--lead`/`--to`)
> 走模糊匹配可绕开这个坑——**优先用名字,只有 `--dri` 用 `$ME_UID`**。

## 字段矩阵

### issue(create / update / assign)

| 字段 | 默认 | 说明 |
|---|---|---|
| `--assignee` | **`"$ME_NAME"`,不问** | 建 issue 时即带上。例外:① plan「分工」段 EXEC 明确是别人 → 按 plan 填该人名;② assign 给 **agent/squad 会触发 multica runtime 执行**,属显式派活,绝不默认 |
| `--project` | 流程上下文已定 | rule #6:完整 UUID;**唯一保留「拿不准就问」的字段** |
| `--parent` | RPI 链决定 | plan→research、case→plan;无链则不填 |
| `--title` | 命名约定 | `计划:/研究:/复盘:<slug>`;工作项用动词前缀(Fix:/Feat:/Chore:) |
| `--status` / label | **禁止手填** | 一律走 `transition.py` / publish.py 入口转换(labels.md 状态机) |
| `--priority` | 留空 | 优先级由 betting table 决定,不落字段;伪精确不如空白 |
| `--due-date` `--start-date` | 留空 | 预测性字段;appetite 住在 plan 文档里 |
| `--description` | 留空或一句话指针 | 文档一律走评论内联(命门B),描述不承载内容 |
| `--attachment` | 不用 | 内联渲染走 publish.py(PUBLISH.md Dead ends) |

### project(create / update)

| 字段 | 默认 | 说明 |
|---|---|---|
| `--dri` | **`"$ME_UID"`,不问** | user UUID 空间(见上方警告) |
| `--lead`(负责人) | **`"$ME_NAME"`,不问** | 名字 fuzzy 匹配 |
| `--title` `--description` | 来自用户意图/plan goal | title 是用户意图本身(新建 project 本就走 rule #6 问答);description 由 agent 从 kickoff 意图提炼,不必追问 |
| `--icon` `--status` | 留空 | 服务端默认 planned |
| `--repo` | 有明确 repo 上下文时自动附 | 当前工作 repo 的 GitHub URL;无则不填 |

### plan fields.json(publish.py --type plan)

| 字段 | 默认 |
|---|---|
| `dri` | **`"$ME_NAME"`,不问**(不要硬编码人名) |
| `exec` | 默认 `["Claude(编排+实现)"]` 或按实际分工 |
| `reviewer` | 默认「子 agent(staff engineer · 独立上下文)」 |

## 不要做

- ❌ 硬编码任何人员 UUID 或人名进 skill/脚本(换机器/换人即错;解析配方是唯一路径)
- ❌ 把 issue assign 给 agent/squad 当默认(那是「派 multica agent 执行」的显式动作)
- ❌ 回填存量 issue 的 assignee(历史归属不明,批量填当前用户=制造假数据;只管增量)
- ❌ 为了「填满字段」给 priority/due-date 编值
