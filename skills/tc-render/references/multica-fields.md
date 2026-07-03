# multica-fields — multica 字段填写默认值单源(agent 默认自动填 · 项目重要字段显式确认)。

**适用**:所有经 CLI 建/改 project、issue 的 agent 流程(tc-kickoff / tc-research / tc-plan / tc-review 等)。
**原则**:人字段默认**当前用户**、运行时解析;状态/label **禁止手填**(走 transition 脚本,见 references/issue-label-state-rules.md)。
**例外(项目层)**:新建 project 的 **DRI / 开始时间 / 预期截止 / 优先级**属重要字段,须向用户**显式确认**(带智能默认),不得静默留空——见下方 project 表。其余预测性字段仍宁空勿假。

## 当前用户解析配方(每台机器解析到各自的人 · 禁止硬编码任何 UUID)

```bash
ME_EMAIL=$(multica auth status 2>&1 | sed -n 's/.*(\(.*\)).*/\1/p')   # auth status 输出走 stderr,2>&1 必带
ME_NAME=$(multica user list --output json | jq -r --arg e "$ME_EMAIL" '.[]|select(.email==$e)|.name')
ME_UID=$( multica user list --output json | jq -r --arg e "$ME_EMAIL" '.[]|select(.email==$e)|.user_id')   # 取 .user_id!(.id 是 workspace-member 记录 id,喂 --dri 会 FK 500)
```

> ⚠️ **ID 字段陷阱**:`multica user list` 每行有两个 UUID——
> `.id` 是 workspace-member **记录** id(**别用**,喂 `project --dri` 服务端 FK 500 拒);
> `.user_id` 才是真正的 user UUID,`project --dri` 收它,issue assignee 解析到的也是**同一个**值。
> 名字类 flag(`--assignee`/`--lead`/`--to`)模糊匹配最稳——**优先用名字,仅 `--dri` 用 `$ME_UID`(=.user_id)**。

## 字段矩阵

### issue(create / update / assign)

| 字段 | 默认 | 说明 |
|---|---|---|
| `--assignee` | **`"$ME_NAME"`,不问** | 建 issue 时即带上。例外:① plan「分工」段 EXEC 明确是别人 → 按 plan 填该人名;② assign 给 **agent/squad 会触发 multica runtime 执行**,属显式派活,绝不默认 |
| `--project` | 流程上下文已定 | 完整 UUID(短 ID 服务端报 400);**唯一保留「拿不准就问」的字段** |
| `--parent` | RPI 链决定 | plan→research、case→plan;无链则不填 |
| `--title` | 命名约定 | `计划:/研究:/复盘:<slug>`;工作项用动词前缀(Fix:/Feat:/Chore:) |
| `--status` / label | **禁止手填** | 一律走 transition 脚本 / publish 入口转换(状态机见 references/issue-label-state-rules.md) |
| `--priority` | 留空 | 优先级由 betting table 决定,不落字段;伪精确不如空白 |
| `--due-date` `--start-date` | 有明确时限则**显式问**,否则留空 | 日历日 `YYYY-MM-DD`;有 deadline 的 issue 应问一句,纯探索性可空;appetite 仍住 plan 文档 |
| `--description` | 留空或一句话指针 | 文档一律走评论内联发布(publish 脚本),描述不承载内容 |
| `--attachment` | 不用 | 内联渲染走 publish 脚本(见 references/publish-contract.md Dead ends) |

### project(create / update)

| 字段 | 默认 | 说明 |
|---|---|---|
| `--dri` | **`"$ME_UID"`(本人)· 向用户确认** | 每项目恰好一个 DRI(团队铁律);默认本人,建项目时**明确确认一次**,不静默填 · user UUID 空间(见上方警告) |
| `--start-date` | **显式询问** · 默认今天 | 重要字段 · 日历日 `YYYY-MM-DD` · 项目计划开始日 |
| `--due-date` | **显式询问** · 默认按 plan appetite 推算 | 重要字段 · 日历日 `YYYY-MM-DD` · 项目预期截止 |
| `--priority` | **显式询问** · 默认 `medium` | 重要字段 · `urgent`/`high`/`medium`/`low`/`none`(项目层用它排优先;issue 层仍走 betting table) |
| `--lead`(负责人) | **`"$ME_NAME"`,不问** | 名字 fuzzy 匹配 |
| `--title` `--description` | 来自用户意图/plan goal | title 是用户意图本身(新建 project 走确认问答);description 由 agent 从 kickoff 意图提炼,不必追问 |
| `--icon` `--status` | 留空 | 服务端默认 planned |
| `--repo` | 有明确 repo 上下文时自动附 | 当前工作 repo 的 GitHub URL;无则不填 |

> ⚠️ `--start-date` / `--due-date` / `--priority` 需较新的 multica CLI(含项目日期字段)。旧版报 `unknown flag` → 先 `multica update` 再建项目。

### plan fields.json(publish 脚本 --type plan)

| 字段 | 默认 |
|---|---|
| `dri` | **`"$ME_NAME"`,不问**(不要硬编码人名) |
| `exec` | 默认 `["Claude(编排+实现)"]` 或按实际分工 |
| `reviewer` | 默认「子 agent(staff engineer · 独立上下文)」 |

## 不要做

- ❌ 硬编码任何人员 UUID 或人名进 skill/脚本(换机器/换人即错;解析配方是唯一路径)
- ❌ 把 issue assign 给 agent/squad 当默认(那是「派 multica agent 执行」的显式动作)
- ❌ **默认**回填存量 issue 的 assignee(历史归属不明;只管增量)——**DRI 明示时例外**,可按指示一次性批量补全;增量由 create 时 `--assignee` 兜住
- ❌ 为了「填满字段」给 priority/due-date 编值
