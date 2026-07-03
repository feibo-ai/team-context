tc-ops 三个脚本的运行时机、完整命令与 exit code 契约,外加本 skill 的例行运维命令。

## 路径约定
脚本随本 skill 分发,位于 `<skills-root>/tc-ops/scripts/`(skills-root 的解析规则见团队全局规则)。下文命令按此占位符书写,勿硬编码某台机器的安装路径。

## monthly_health.py — 团队健康月报
- 何时跑:每月 review 时。
- 命令:`python3 <skills-root>/tc-ops/scripts/monthly_health.py <team-context-repo> [<project-repo> ...]`
- 输出:markdown 报告到 stdout,指标:
  - CLAUDE.md 体量:unicode 字符数(`len(text)`,与 CI lint 同口径),>4000 ⚠️;
  - 本月 claude-md 相关 commit(git log 近 30 天;为零提示 possibly under-learning);
  - skill lint:各 SKILL.md 的 name/description 必填,body >1500 字符报 ERROR(CI 同口径);owner/last_reviewed_at 读 repo 根 skill-pack.yaml 治理表(`skills: [{name, owner, last_reviewed_at}]`),缺条目/缺字段报 WARN,skill-pack.yaml 不存在则跳过治理检查并警告;
  - `wip:` 重启次数(近 30 天,>50 ⚠️ burnout 信号);
  - case 污染:人工 grep 提示(报告只给提醒,不自动扫)。
- exit:缺参数 exit 2;其余 exit 0。
- 后续:报告经 tc-render skill 发布,或直接贴月度 review。

## issue_invariants.py — issue label↔status 不变量巡检
- 何时跑:月度 review 必跑;backfill / 状态机改动后验收加 `--strict`。
- 命令:`python3 <skills-root>/tc-ops/scripts/issue_invariants.py [--strict]`
- 行为:只读、零写;经 multica CLI 全量分页拉取(`--limit/--offset` 循环至 `has_more=false` 才停——只看第一页会把样本截断)。输出 markdown 违规清单。
- exit:默认恒 exit 0(报告模式,autopilot 用);`--strict` 且有硬性违规 exit 1(backfill 验收 / CI 用)。multica CLI 不可用时 exit 1 并报错。
- 检查内容:语义以脚本 docstring 为单源;状态机见 tc-render skill 的 references/issue-label-state-rules.md。
- 后续:发现漂移一律用 tc-render skill 的 scripts/transition.py 修复,绝不手敲 label/status 命令。

## autopilot_lint.py — autopilot YAML guardrail 校验
- 何时跑:新增/修改 autopilot YAML **之前**(先 lint 再提交,有 error 就挡住)。
- 命令:`python3 <skills-root>/tc-ops/scripts/autopilot_lint.py <yaml-path> [<yaml-path> ...]`
- exit:任一文件有 ERROR exit 1;全部通过 exit 0;缺参数 exit 2。WARN 不挡,但需人工确认。
- 规则明细读 references/autopilot-guardrails.md。
- 依赖:需要 PyYAML(`import yaml`);ModuleNotFoundError 时先 `python3 -m pip install pyyaml`。

## 例行运维命令
- 改动本 skill 任何文件后,必须同步 multica registry:
  `multica skill files upsert tc-ops --path <file> --content "$(cat <file>)"`
  不同步的后果:autopilot 定期 `multica skill pull tc-ops` 会经本地 skills 软链把 registry 旧版写回仓库工作树。
- 校验规则变更必须与脚本一起改;文档不复述具体数量,以脚本 `--help` 与源码为准。
