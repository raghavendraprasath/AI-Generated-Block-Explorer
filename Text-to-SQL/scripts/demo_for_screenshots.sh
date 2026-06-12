#!/usr/bin/env bash
# Run each Homework 3 demo command in sequence — screenshot your terminal/browser at each pause.
# Usage: ./scripts/demo_for_screenshots.sh ~/hw3-data/blockchain.db
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DB="${1:-$HOME/hw3-data/blockchain.db}"

cd "$ROOT"
source .venv/bin/activate 2>/dev/null || true

pause() {
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  SCREENSHOT: $1"
  echo "  Save as:    screenshots/$2"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  read -r -p "Press Enter when done… "
  echo ""
}

echo "Homework 3 — manual screenshot demo"
echo "Database: $DB"
echo "Save PNGs to: $ROOT/screenshots/"
mkdir -p "$ROOT/screenshots"
echo ""

# --- Essential (minimum submission set) ---

python3 check_node.py
pause "bitcoind RPC — getblockcount, getblockchaininfo, getblock on tip" "01_bitcoind_rpc.png"

python3 validate.py --db "$DB"
pause "Validation passed — ingest complete & consistent" "02_validate.png"

python3 text_to_sql.py \
  --question "How many blocks are in the database?" \
  --db "$DB"
pause "Text-to-SQL — question, generated SQL, answer" "03_text_to_sql.png"

python3 run_tests.py --db "$DB" --standard-only
pause "Golden tests — 12/12 pass" "04_run_tests.png"

echo "Start the web UI in another terminal:"
echo "  ./scripts/run_web_ui.sh $DB"
echo "Then open http://localhost:8501 in your browser (not Cursor)."
read -r -p "Press Enter when the app is open… "
pause "Streamlit Home — one chat question with SQL + answer visible" "05_ui_home.png"
pause "Streamlit Insights — one rendered chart (Quick views tab)" "06_ui_insights.png"

tail -30 "$ROOT/logs/cron.log" 2>/dev/null || tail -30 "$ROOT/logs/updater.log" 2>/dev/null || echo "(no log yet — run: python3 updater.py --db $DB)"
pause "Updater/cron log — recent ingest + validate lines" "07_cron_log.png"

# --- Optional (bonus / depth) ---

read -r -p "Optional screenshots? [y/N] " opt
if [[ "${opt,,}" == "y" ]]; then
  python3 generate_schema.py examples/getblock_100000.json schema_generated.sql
  head -25 schema_generated.sql
  pause "Schema auto-generation (Approach 2)" "08_schema_generate.png"

  python3 run_tests.py --db "$DB" --live 2>&1 | tail -40
  pause "Live LLM tests (partial pass is OK — document in LIVE_LLM_RESULTS.md)" "09_run_tests_live.png"

  python3 charts.py \
    --question "Block heights and transaction counts for the first 20 blocks" \
    --db "$DB" \
    --sql "SELECT height, ntx FROM blocks ORDER BY height ASC LIMIT 20" \
    --output screenshots/chart_cli.png
  pause "CLI chart output (or use Insights page instead)" "10_chart.png"
fi

echo ""
echo "Presentation slide (open in browser, screenshot or present live):"
echo "  file://$ROOT/slides/hard_failures.html"
echo ""
echo "Done. See screenshots/README.md for the full list."
