用途:判定一件事是 project-layer(走 tc-kickoff 六步)还是 task-layer(走 tc-plan task-mode)的唯一判据。

# Project-layer vs Task-layer 判定

## 核心测试
你会把这件事称作"一个独立的大方向"吗?具体判据(三条都倾向成立才算 project-layer):

1. **体量**:预计 3 天以上的工作量。
2. **责任**:有(或应该有)一个明确的 DRI。
3. **收尾**:结束时值得写一份 debrief(复盘)。

## 判定结果
- **YES(project-layer)** → 继续 tc-kickoff 的 6 步流程(Phase 01)。
- **NO(task-layer)** → INVOKE tc-plan skill,用它的 task-mode(3 句话 mini-plan)即可,不必走 Phase 01。

## 拿不准时
- 倾向按小的做:先按 task-layer 走 tc-plan task-mode;如果做着做着发现范围膨胀到满足上面三条,再回来走 tc-kickoff 正式立项。
- 仍然模糊就直接问用户:"这是一个 3 天以上、需要 DRI、结束要复盘的独立方向吗?"
