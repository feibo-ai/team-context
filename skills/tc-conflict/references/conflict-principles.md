四原则完整判据：tc-conflict 裁决团队分歧时逐条执行的原则、判断标准与反模式。

# Conflict Adjudication — 四原则

## 1. 对事不对人
- Frame the disagreement as "two options" or "two interpretations," not "X vs Y people."
- If you can't restate the other side's argument fairly, you don't understand it yet — back up and listen first.

## 2. 依据优先于偏好
What does EVIDENCE say?
- Performance data? Test results? Prior cases? Industry references? Cite them.
- "I feel" or "in my experience" without specifics doesn't count.
- If there is no evidence either way, label it explicitly: "this is a judgment call between X and Y."

## 3. DRI 最终决定权
After principles 1 + 2:
- If consensus → great, document it.
- If still split → the DRI decides. Even if the DRI is more junior. Even if the DRI is wrong — the team still executes and observes the outcome.

## 4. 决策必须记录
Every adjudicated decision gets a dated record `YYYY-MM-DD-<topic>.md` written into the `decisions` directory at the team-context repo root (locate the repo explicitly; never assume the current working directory is the repo). The record must contain:
- Context (what was the choice?)
- Options considered
- Evidence cited for each
- DRI's decision
- Dissenter's flag if any
- Date + signatures

Non-negotiable. Without the file, the decision didn't happen.

## Anti-patterns
- ❌ "Let's vote on it" — the DRI model means the DRI decides, not the majority
- ❌ Skipping the file because "the decision was obvious in the meeting"
- ❌ "I told you so" later when dissent turns out right — the dissent is already on record; that is the point of recording it
- ❌ A senior member overriding an intern DRI without documenting it
