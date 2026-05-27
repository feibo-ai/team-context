# skills/

每个子目录 = 一个 skill = 一个 SKILL.md（+ 可选的辅助文件）。
通过 `scripts/sync-to-local.sh` 同步到 `~/.claude/skills/`，通过
`scripts/sync-to-multica.sh` 同步到 multica workspace。

## Format
```
skills/<skill-name>/
├── SKILL.md            (required: YAML frontmatter + body)
└── *.md                (optional supporting reference docs)
```

## Body budget
目标 ≤ 1500 字（约 2000 tokens）。CI lint 强制执行硬上限。
