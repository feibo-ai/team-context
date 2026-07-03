WIP/未提交改动在 handoff 时的处置政策:先看清、按路径操作,绝不整树扫入。

## 原则

- 工作树常混有其他项目/其他人的未提交文件。任何 add/stash/discard 之前都必须先 `git status --short` 看清全貌并报告用户,再按具体路径操作。
- 绝不 `git add -A`:会把无关文件一并裹挟提交。
- 绝不裸 `git checkout .`:会连带其他改动一起丢弃。

## 三种去向(不明显时问用户)

1. **commit** — 默认选项,适用于任何有意义的工作:
   - `git add <具体路径>` 显式暂存本次相关文件;
   - `git commit -m "wip: <one-line state>"`。
2. **stash** — 不确定是否值得保留、但可能想找回:
   - `git stash push -m "wip: <one-line>" -- <具体路径>`。
3. **discard** — 仅限用户显式确认,绝非默认(confirmDiscard 门:丢弃前必须得到用户明确点头):
   - `git checkout -- <具体路径>`。
