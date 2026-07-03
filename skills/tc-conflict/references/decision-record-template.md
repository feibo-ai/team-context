决策记录输出模板：tc-conflict 落档决策时按此模板生成文件，无论裁决结果如何都必须写。

File name: `YYYY-MM-DD-<topic>.md`. Location: the `decisions` directory at the team-context repo root — locate the repo first; never assume the current working directory is the repo.

```markdown
# Decision: <topic>

**Date**: YYYY-MM-DD
**DRI**: <name>
**Status**: decided

## Context
<what was the choice?>

## Options
- A: <description>
- B: <description>

## Evidence per option
- For A: <citation>
- For B: <citation>

## DRI decision
Chose: <A or B>
Reason: <1-2 sentences>

## Dissent
<name> disagreed with <reason>, but agreed to execute.

## Review trigger
If <observable signal> happens, revisit.
```
