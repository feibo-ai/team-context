#!/usr/bin/env bash
# install-skill-pull-cron.sh — 成员机 skill 自动同步:每小时从 multica registry
# 拉全部 skill 到双目录(~/.claude/skills 给 Claude 系 · ~/.agents/skills 给 Codex)。
#
# 这是「三条真相不同步」的成员端解:registry 更新后至多 1 小时全员机器就位,
# 不再依赖每个人记得 git pull / 手动 pull。过期检测另有 `multica skill pull --check`
# (已接进 `multica doctor` 软检查)。
#
# macOS: LaunchAgent(每小时 + 登录时跑一次;日志 ~/Library/Logs/multica-skill-pull.log)
# Linux: crontab 条目(标记注释幂等)
#
# 用法:
#   bash scripts/install-skill-pull-cron.sh              # 安装/更新
#   bash scripts/install-skill-pull-cron.sh --uninstall  # 卸载
#
# 注意:DRI 开发机走 git 软链模式(sync-team-config.sh),不要装本 cron——
# pull 会拒绝覆盖软链(--force 才会),但没必要让它每小时报错。
set -euo pipefail

LABEL="ai.feibo.multica-skill-pull"
PULL_CMD='multica skill pull --all && multica skill pull --all --dir "$HOME/.agents/skills"'
UNINSTALL=0
[ "${1:-}" = "--uninstall" ] && UNINSTALL=1

command -v multica >/dev/null 2>&1 || { echo "ERROR: multica CLI 不在 PATH,先装 CLI" >&2; exit 1; }

# DRI 软链布局检测:~/.claude/skills 下有指向 git 仓的软链 → 这台是开发机
if [ "$UNINSTALL" = 0 ] && [ -d "$HOME/.claude/skills" ]; then
  for link in "$HOME/.claude/skills"/tc-*; do
    [ -L "$link" ] || continue
    echo "WARN: 检测到软链 $(basename "$link")(git-dev 布局)。开发机不建议装 pull cron。" >&2
    printf '继续安装? [y/N] ' >&2
    read -r ans
    [ "$ans" = y ] || [ "$ans" = Y ] || { echo "已取消"; exit 0; }
    break
  done
fi

case "$(uname -s)" in
  Darwin)
    PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
    if [ "$UNINSTALL" = 1 ]; then
      launchctl bootout "gui/$(id -u)/${LABEL}" 2>/dev/null || true
      rm -f "$PLIST"
      echo "已卸载 LaunchAgent ${LABEL}"
      exit 0
    fi
    mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
    # -l 登录 shell:multica 可能装在 /opt/homebrew/bin 等非默认 PATH
    cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>${LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>-lc</string>
    <string>${PULL_CMD}</string>
  </array>
  <key>StartInterval</key><integer>3600</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>${HOME}/Library/Logs/multica-skill-pull.log</string>
  <key>StandardErrorPath</key><string>${HOME}/Library/Logs/multica-skill-pull.log</string>
</dict>
</plist>
PLIST
    launchctl bootout "gui/$(id -u)/${LABEL}" 2>/dev/null || true
    launchctl bootstrap "gui/$(id -u)" "$PLIST"
    echo "已安装 LaunchAgent ${LABEL}(每小时 + 登录时;日志 ~/Library/Logs/multica-skill-pull.log)"
    echo "立即验证: launchctl kickstart gui/$(id -u)/${LABEL} && tail -f ~/Library/Logs/multica-skill-pull.log"
    ;;
  Linux)
    MARK="# ${LABEL}"
    if [ "$UNINSTALL" = 1 ]; then
      (crontab -l 2>/dev/null | grep -v "$MARK") | crontab - || true
      echo "已移除 crontab 条目 ${LABEL}"
      exit 0
    fi
    LINE="0 * * * * /bin/bash -lc '${PULL_CMD}' >> \$HOME/.multica-skill-pull.log 2>&1 ${MARK}"
    (crontab -l 2>/dev/null | grep -v "$MARK"; echo "$LINE") | crontab -
    echo "已安装 crontab 条目(每小时;日志 ~/.multica-skill-pull.log)"
    ;;
  *)
    echo "ERROR: 未支持的平台 $(uname -s)" >&2; exit 1 ;;
esac
