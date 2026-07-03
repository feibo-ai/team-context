# Skill pack 冒烟测试（人工 / 新机验收）

每次大版本改动或新成员机器配置后跑一遍。全部通过才算分发成功。

## 1. 安装面

- [ ] `bash scripts/sync-team-config.sh --no-multica` 无报错
- [ ] `ls ~/.claude/skills/` 恰好 13 个 tc-*，全部是软链且目标存在
- [ ] `ls ~/.agents/skills/` 同上（Codex 端）
- [ ] `~/.codex/skills-index.md` 不存在（旧 hack 已清）
- [ ] 无旧名残留：`ls ~/.claude/skills | grep -E 'tc-(1-start|2-research|3-plan|4-build|5-review|monday|friday|roles|self-check|health-check)'` 为空

## 2. 发现面（Claude Code）

- [ ] 新开 session，说「我想做一个新项目」→ 应触发 tc-kickoff
- [ ] 说「接手 issue TEA-xx」/「继续任务」→ 应触发 tc-router
- [ ] 说「写个 plan」→ tc-plan；「复盘」→ tc-review；「卡住了」→ tc-router 或 tc-handoff
- [ ] 说「周五 demo」→ tc-rhythm；「自检」→ tc-health
- [ ] `/doctor` 能列出 13 个 skill 且 description 完整未截断

## 3. 发现面（Codex）

- [ ] `/skills` 列出 13 个 tc-*
- [ ] 「接手 issue」触发 tc-router（原生 description 触发，无需 index 文件）

## 4. 工具链

- [ ] `python3 evals/validate-skills.py` → 0 errors
- [ ] `python3 ~/.claude/skills/tc-render/scripts/transition.py --help` 正常输出
- [ ] `python3 -m pytest evals/render/ -q` 全绿
- [ ] `python3 ~/.claude/skills/tc-ops/scripts/monthly_health.py --help 2>/dev/null || true` 不抛语法错误

## 5. 离线韧性

- [ ] 断网后新开 session，skill 仍可触发（物理文件/软链，不依赖网络）
- [ ] 断网时跑一个调 multica CLI 的 skill → 应明确报错并停下，而不是假装成功
