---
name: role-assignment-protocol
description: "Use when starting a project and assigning roles. Triggers '认领角色', 'role assignment', '谁做什么', 'DRI 是谁', '认领'. Walks through SOP v0.4 P-5: 4 role types (DRI/EXEC/COLLAB/REVIEW) + 6 assignment rules. Generates the 'How to split' section of plan markdown."
---

# Role Assignment — 4 types + 6 rules

## 4 role types

### DRI · Directly Responsible Individual
- **Exactly ONE per project**. No exceptions.
- Full visibility + final decision power + ultimate responsibility.
- 实习生 can be DRI (SOP P-5). 谁拍板谁负责.

### EXEC · Direct execution
- One or more. Writes code/docs/content for specific modules.
- Accountable for module quality, not whole project.

### COLLAB · Cross-module support
- Pulled in for specific time-windows.
- Responsible for collaboration quality during window.
- Can decline if over-extended.

### REVIEW · Independent perspective
- External check: code review, plan review, risk flagging.
- Usually different Claude session, sometimes human.

Same person can hold multiple roles. Same role can be held by multiple people (except DRI which is singleton).

## 6 assignment rules

1. **自愿优先** — Ask "who wants what?" before assigning.
2. **DRI 必有** — Project without DRI is invalid. Refuse to start.
3. **认领即承诺** — Once accepted, can't ghost.
4. **可以拒绝** — Being asked != obligated. Decline politely is OK.
5. **可以交接** — Mid-project handoff allowed if proactively communicated.
6. **认领记录** — All assignments written into plan markdown's "How to split" section. Visible to all.

## Output: How to split section

```markdown
## How to split
- **DRI**: <name> (拍板 / 全权 / 收尾)
- **EXEC**: <names> (具体产出)
- **COLLAB**: <names + window> (特定时段支持)
- **REVIEW**: <name or "second Claude session"> (关键节点把关)
```

## Special situation: 实习生 DRI
- Senior members in COLLAB/REVIEW provide judgment material, NOT replace judgment.
- Express concerns, don't issue orders.
- Decisions recorded in decisions/ even if seniors disagree.
- Retrospective MUST NOT use "I told you so."

## Anti-patterns
- ❌ No DRI (most common AI Native failure — SOP ❌10)
- ❌ DRI assigned to most senior person by default without asking
- ❌ COLLAB invited but never told what's expected
- ❌ Mid-project role changes happen silently
