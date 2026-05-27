# skills/

Each subdirectory = one skill = one SKILL.md (+ optional supporting files).
Synced to `~/.claude/skills/` via `scripts/sync-to-local.sh` and to multica
workspace via `scripts/sync-to-multica.sh`.

## Format
```
skills/<skill-name>/
├── SKILL.md            (required: YAML frontmatter + body)
└── *.md                (optional supporting reference docs)
```

## Body budget
Target ≤ 1500 words (≈ 2000 tokens). CI lint enforces hard ceiling.
