Current State 交接块模板:每次 handoff 照此填写,发布前逐项自检。

## 模板

```markdown
## Current State (handoff @ <YYYY-MM-DD HH:MM>)

**Last commit**: <hash> <subject>
**Worktree**: <branch>, <N> file(s) changed since last commit

**What's done**:
- <1-3 specific bullets>

**Next action** (concrete enough for a fresh session to start cold):
- <1-3 sentences, naming files/functions if applicable>

**Dead ends — do NOT retry**:
- <approach tried + why it failed>
- ...

**Context pollution signal** (why we are clearing):
- <one sentence>
```

## 填写要点

- **Next action** 必须具体到能让新 session 冷启动:点名文件/函数,禁止 "continue the work" 这类空话。
- **Dead ends** 一条都别省:漏写会让新 session 重蹈死胡同,代价约 2 倍时间。
- **Context pollution signal** 一句话说清这次为什么要 clear。
- 发布用的 fields.json 字段契约与渲染语义,以 tc-render skill 的 references/publish-contract.md 为准,本文件只管内容质量。
