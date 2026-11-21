#!/bin/bash
# Устанавливает launchd-агент macOS, который каждый день выбирает «Ежедневный вызов».
#
# Usage:
#   ./scripts/install_daily_challenge_agent.sh            # установить
#   ./scripts/install_daily_challenge_agent.sh --uninstall
#
# Агент запускает scripts/daily_challenge.sh ежедневно в 00:05 и при загрузке.
set -euo pipefail

LABEL="com.kernify.dailychallenge"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT="$PROJECT_DIR/scripts/daily_challenge.sh"
PLIST_DIR="$HOME/Library/LaunchAgents"
PLIST="$PLIST_DIR/$LABEL.plist"

if [ "${1:-}" = "--uninstall" ]; then
    launchctl unload "$PLIST" 2>/dev/null || true
    rm -f "$PLIST"
    echo "Агент удалён: $PLIST"
    exit 0
fi

mkdir -p "$PLIST_DIR" "$PROJECT_DIR/logs"

cat > "$PLIST" <<PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$SCRIPT</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>0</integer>
        <key>Minute</key>
        <integer>5</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>$PROJECT_DIR/logs/daily_challenge_agent.log</string>
    <key>StandardErrorPath</key>
    <string>$PROJECT_DIR/logs/daily_challenge_agent.err.log</string>
</dict>
</plist>
PLIST_EOF

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
echo "Агент установлен: $PLIST"
echo "Он будет выбирать задачу ежедневно в 00:05 (и сразу сейчас)."
echo "Проверка: launchctl list | grep $LABEL"
