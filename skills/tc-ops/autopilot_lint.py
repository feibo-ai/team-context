#!/usr/bin/env python3
"""autopilot lint — 校验 autopilot YAML 是否满足 SOP PB-04 guardrails。

取代本地 MCP 的 autopilot_lint(无需 MCP 服务器)。有 error 则 exit 1。
用法:  autopilot_lint.py <yaml-path> [<yaml-path> ...]
"""
import sys
import yaml

REQUIRED_FORBIDDEN_COMMANDS = ["git push", "npm publish"]
MAX_BUDGET_USD_HARD_CAP = 150
MIN_FORBIDDEN_COMMANDS = 5


def lint(path):
    errors, warnings = [], []
    try:
        p = yaml.safe_load(open(path)) or {}
    except Exception as e:
        return [f"YAML parse error: {e}"], []

    if not p.get("name"):
        errors.append("missing required field: name")
    if not p.get("description"):
        errors.append("missing required field: description")
    if p.get("mode") not in ("run_only", "create_issue"):
        errors.append(f"invalid mode: {p.get('mode')} (must be run_only or create_issue)")
    if not (p.get("agent") or {}).get("name"):
        errors.append("missing required field: agent.name")
    if not p.get("prompt"):
        errors.append("missing required field: prompt")
    trig = p.get("trigger") or {}
    if not trig.get("cron"):
        errors.append("missing required field: trigger.cron")
    if not trig.get("timezone"):
        errors.append("missing required field: trigger.timezone")

    g = p.get("guardrails")
    if not g:
        errors.append("missing required section: guardrails (SOP PB-04 violation)")
        return errors, warnings  # can't check further

    fc = g.get("forbidden_commands")
    if not isinstance(fc, list) or len(fc) < MIN_FORBIDDEN_COMMANDS:
        errors.append(
            f"guardrails.forbidden_commands must have ≥ {MIN_FORBIDDEN_COMMANDS} entries "
            f"(got {len(fc) if isinstance(fc, list) else 0})"
        )
    else:
        for required in REQUIRED_FORBIDDEN_COMMANDS:
            if not any(required.lower() in str(cmd).lower() for cmd in fc):
                errors.append(f'guardrails.forbidden_commands must include "{required}"')

    fp = g.get("forbidden_paths")
    if not isinstance(fp, list) or len(fp) == 0:
        errors.append("guardrails.forbidden_paths must have at least 1 entry")

    mb = g.get("max_budget_usd")
    if not isinstance(mb, (int, float)) or isinstance(mb, bool):
        errors.append("guardrails.max_budget_usd must be a number")
    elif mb > MAX_BUDGET_USD_HARD_CAP:
        errors.append(f"guardrails.max_budget_usd {mb} > {MAX_BUDGET_USD_HARD_CAP} hard cap (SOP PB-04)")
    elif mb > 80:
        warnings.append(f"guardrails.max_budget_usd {mb} 在 SOP PB-04 大批量 range — DRI 应明示批准")

    mr = g.get("max_runtime_minutes")
    if not isinstance(mr, (int, float)) or isinstance(mr, bool) or mr <= 0:
        errors.append("guardrails.max_runtime_minutes must be a positive number")

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("usage: autopilot_lint.py <yaml-path> [...]", file=sys.stderr)
        sys.exit(2)
    any_error = False
    for path in sys.argv[1:]:
        errors, warnings = lint(path)
        mark = "OK" if not errors else "FAIL"
        print(f"[{mark}] {path}")
        for e in errors:
            print(f"  ERROR: {e}")
        for w in warnings:
            print(f"  WARN: {w}")
        if errors:
            any_error = True
    sys.exit(1 if any_error else 0)


if __name__ == "__main__":
    main()
