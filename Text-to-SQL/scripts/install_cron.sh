#!/usr/bin/env bash
# Install updater cron job (§3c). Uses Linux DB path by default.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DB_PATH="${1:-$HOME/hw3-data/blockchain.db}"

mkdir -p "$ROOT/logs" "$(dirname "$DB_PATH")"
PY="$ROOT/.venv/bin/python3"
if [[ ! -x "$PY" ]]; then
  PY="/usr/bin/python3"
fi
CRON_LINE="*/5 * * * * cd $ROOT && $PY updater.py --db $DB_PATH >> $ROOT/logs/cron.log 2>&1"

( crontab -l 2>/dev/null | grep -v "Text-to-SQL/updater.py" || true
  echo "$CRON_LINE"
) | crontab -

echo "Installed cron (every 5 minutes):"
echo "  $CRON_LINE"
echo "Logs: $ROOT/logs/cron.log"
echo "After 5+ min run: tail $ROOT/logs/cron.log"
